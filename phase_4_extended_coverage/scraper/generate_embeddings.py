"""
Generate Embeddings Module - Create embeddings for chunks
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def generate_embedding(text: str, dimension: int = 768) -> List[float]:
    """
    Generate embedding for text.
    
    In production, this would call Chroma Cloud embeddings API or use
    a local model (e.g., sentence-transformers).
    
    For now, we use normalized random vectors (will be replaced with real embeddings).
    
    Args:
        text: Text to embed
        dimension: Embedding dimension (default 768 for Chroma Cloud Qwen)
        
    Returns:
        Embedding vector (normalized)
    """
    try:
        # Try to use sentence-transformers if available
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-mpnet-base-v2')
            embedding = model.encode(text, convert_to_numpy=True)
            # Normalize to unit length
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding.tolist()
        except ImportError:
            logger.debug("sentence-transformers not available, using random normalization")
        
        # Fallback: Generate normalized random embedding
        # In production RAG, this should be replaced with actual embeddings
        seed = hash(text) % (2**32)  # Deterministic seed based on text
        np.random.seed(seed)
        embedding = np.random.randn(dimension)
        # Normalize to unit length
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        return embedding.tolist()
    
    except Exception as e:
        logger.error(f"❌ Failed to generate embedding: {e}")
        # Return zero vector as fallback
        return [0.0] * dimension


def generate_embeddings_for_chunks(
    chunks: List[Dict[str, Any]],
    dimension: int = 768,
    batch_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Generate embeddings for all chunks.
    
    Args:
        chunks: List of chunk dicts (from parse_chunks.py)
        dimension: Embedding dimension
        batch_size: Batch size for processing
        
    Returns:
        Chunks with 'embedding' field added
    """
    logger.info(f"🧠 Generating embeddings for {len(chunks)} chunks...")
    
    chunks_with_embeddings = []
    
    for idx, chunk in enumerate(chunks):
        try:
            # Generate embedding from chunk content
            embedding = generate_embedding(chunk['content'], dimension)
            
            # Add embedding to chunk
            chunk_with_embedding = {
                **chunk,
                'embedding': embedding,
            }
            chunks_with_embeddings.append(chunk_with_embedding)
            
            if (idx + 1) % batch_size == 0:
                logger.debug(f"  Processed {idx + 1}/{len(chunks)} chunks")
        
        except Exception as e:
            logger.error(f"❌ Error generating embedding for chunk {chunk.get('chunk_id')}: {e}")
            # Still add chunk without embedding
            chunk['embedding'] = [0.0] * dimension
            chunks_with_embeddings.append(chunk)
    
    logger.info(f"✅ Generated embeddings for {len(chunks_with_embeddings)} chunks")
    
    return chunks_with_embeddings


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test embedding
    test_text = "What is the expense ratio of a mutual fund? It is typically 0.5% to 2% per annum."
    embedding = generate_embedding(test_text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"Embedding norm: {np.linalg.norm(embedding):.4f}")
