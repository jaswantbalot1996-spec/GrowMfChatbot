"""
Embedding Service
Converts text chunks into 768D dense vector representations for semantic search.
Supports batch processing, L2 normalization, and incremental updates.

Reference: EMBEDDING_STRATEGY.md
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import EmbeddingConfig

logger = logging.getLogger(__name__)
logger.setLevel(EmbeddingConfig.LOG_LEVEL)


class EmbeddingService:
    """Service for generating sentence embeddings (768D)"""
    
    def __init__(self,
                 model_name: Optional[str] = None,
                 batch_size: Optional[int] = None,
                 device: Optional[str] = None):
        """
        Initialize embedding service.
        
        Args:
            model_name: HuggingFace model ID (defaults to config)
            batch_size: Batch size for encoding (defaults to config)
            device: 'cuda', 'cpu', or 'auto' (defaults to config)
        """
        self.model_name = model_name or EmbeddingConfig.MODEL_NAME
        self.batch_size = batch_size or EmbeddingConfig.BATCH_SIZE
        
        # Auto-detect device
        if device == 'auto' or device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = device
        
        logger.info(f"Loading embedding model: {self.model_name}")
        logger.info(f"Device: {self.device}")
        
        # Load model
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Dimension: {self.embedding_dim}D")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def embed_batch(self,
                   texts: List[str],
                   normalize: bool = True) -> np.ndarray:
        """
        Embed a batch of texts.
        
        Args:
            texts: List of strings to embed
            normalize: Whether to L2-normalize embeddings
            
        Returns:
            Numpy array of shape (len(texts), embedding_dim)
        """
        logger.debug(f"Embedding batch of {len(texts)} texts (normalize={normalize})")
        
        start_time = time.time()
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=EmbeddingConfig.SHOW_PROGRESS_BAR,
        )
        
        elapsed = time.time() - start_time
        throughput = len(texts) / elapsed
        logger.debug(f"Encoded {len(texts)} texts in {elapsed:.2f}s ({throughput:.1f} texts/sec)")
        
        assert embeddings.shape == (len(texts), self.embedding_dim), \
            f"Unexpected embedding shape: {embeddings.shape}"
        
        return embeddings
    
    def embed_chunks(self,
                    chunks: List[Dict],
                    batch_size: Optional[int] = None) -> List[Dict]:
        """
        Embed a list of chunk objects, attaching embeddings to each.
        
        Args:
            chunks: List of chunk dicts with 'text' key
            batch_size: Override instance batch_size
            
        Returns:
            Same chunks with 'embedding' field populated (list of floats)
        """
        batch_size = batch_size or self.batch_size
        texts = [c['text'] for c in chunks]
        
        logger.info(f"Embedding {len(chunks)} chunks with batch_size={batch_size}")
        
        # Process in sub-batches
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embed_batch(batch_texts)
            all_embeddings.append(batch_embeddings)
        
        # Concatenate batches
        embeddings = np.vstack(all_embeddings) if all_embeddings else np.array([])
        
        # Attach embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist()  # Convert to list for JSON serialization
        
        logger.info(f"Successfully embedded {len(chunks)} chunks")
        return chunks
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.
        
        Args:
            query: Query text
            
        Returns:
            768D normalized embedding vector
        """
        query_clean = query.strip()
        embedding = self.model.encode(
            query_clean,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding
    
    @staticmethod
    def compute_similarity(query_embedding: np.ndarray,
                          chunk_embeddings: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between query and chunks.
        Works via dot product on L2-normalized vectors.
        
        Args:
            query_embedding: 1D array of shape (embedding_dim,)
            chunk_embeddings: 2D array of shape (N, embedding_dim)
            
        Returns:
            1D array of shape (N,) with similarity scores
        """
        # Cosine similarity = dot product for L2-normalized vectors
        similarities = np.dot(chunk_embeddings, query_embedding)
        return similarities


class IncrementalEmbeddingUpdater:
    """Handle incremental embedding updates based on content hash"""
    
    def __init__(self, embedding_service: EmbeddingService):
        """
        Initialize updater.
        
        Args:
            embedding_service: EmbeddingService instance
        """
        self.service = embedding_service
        logger.info("IncrementalEmbeddingUpdater initialized")
    
    def update_embeddings(self,
                        old_chunks: List[Dict],
                        new_chunks: List[Dict]) -> List[Dict]:
        """
        Update embeddings for new chunks, reusing old embeddings where content unchanged.
        
        Args:
            old_chunks: Previously embedded chunks
            new_chunks: New chunks (no embeddings yet)
            
        Returns:
            new_chunks with embeddings (reused or newly computed)
        """
        logger.info(f"Incremental update: {len(old_chunks)} old, {len(new_chunks)} new")
        
        # Create indexes for fast lookup
        old_hash_to_chunk = {c.get('content_hash'): c for c in old_chunks if c.get('content_hash')}
        old_id_to_chunk = {c.get('chunk_id'): c for c in old_chunks if c.get('chunk_id')}
        
        chunks_to_embed = []
        chunks_to_reuse = []
        reuse_map = {}  # Map: new_chunk_id -> old_embedding
        
        for new_chunk in new_chunks:
            content_hash = new_chunk.get('content_hash')
            chunk_id = new_chunk.get('chunk_id')
            
            # Look up by chunk ID first
            old_chunk = old_id_to_chunk.get(chunk_id)
            
            if old_chunk and old_chunk.get('embedding'):
                # Check if content hash matches (content unchanged)
                if old_chunk.get('content_hash') == content_hash:
                    # Content identical: reuse embedding
                    reuse_map[chunk_id] = old_chunk['embedding']
                    chunks_to_reuse.append(new_chunk)
                else:
                    # Content changed: re-embed
                    chunks_to_embed.append(new_chunk)
            else:
                # New chunk: embed
                chunks_to_embed.append(new_chunk)
        
        logger.info(f"Reusing {len(chunks_to_reuse)} embeddings, re-embedding {len(chunks_to_embed)}")
        
        # Embed only changed/new chunks
        if chunks_to_embed:
            self.service.embed_chunks(chunks_to_embed)
        
        # Restore reused embeddings
        for chunk in chunks_to_reuse:
            chunk['embedding'] = reuse_map[chunk['chunk_id']]
        
        # Combine
        all_chunks = chunks_to_reuse + chunks_to_embed
        return all_chunks


@retry(
    stop=stop_after_attempt(EmbeddingConfig.MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def embed_with_retry(service: EmbeddingService, texts: List[str]) -> np.ndarray:
    """
    Embed texts with automatic retry on failure.
    
    Args:
        service: EmbeddingService instance
        texts: List of texts to embed
        
    Returns:
        Embedding array
    """
    return service.embed_batch(texts)


def validate_embeddings(chunks: List[Dict]) -> bool:
    """
    Validate embedding quality and format.
    
    Args:
        chunks: List of chunks with embeddings
        
    Returns:
        True if all valid, False otherwise
    """
    if not chunks:
        logger.warning("No chunks to validate")
        return True
    
    issues = []
    
    for chunk in chunks:
        if 'embedding' not in chunk:
            issues.append(f"Chunk {chunk.get('chunk_id')} missing embedding")
            continue
        
        emb = chunk['embedding']
        
        # Check if it's a list (serialized form)
        if isinstance(emb, list):
            emb = np.array(emb)
        
        # Validate L2 norm (should be ~1.0)
        if isinstance(emb, np.ndarray):
            norm = np.linalg.norm(emb)
            if not (0.99 < norm < 1.01):
                issues.append(f"Chunk {chunk.get('chunk_id')} not L2-normalized (norm={norm:.4f})")
    
    if issues:
        logger.warning(f"Embedding validation issues:\n" + "\n".join(issues[:5]))
        return False
    
    logger.info(f"✓ All {len(chunks)} embeddings validated")
    return True
