"""
Vector Database Integration (Pinecone)
Manages semantic search via KNN lookup in vector DB.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class PineconeVectorDB:
    """Integration with Pinecone vector database"""
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 environment: Optional[str] = None,
                 index_name: str = 'groww-faq'):
        """
        Initialize Pinecone connection.
        
        Args:
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env)
            environment: Pinecone environment (defaults to PINECONE_ENV env)
            index_name: Index name to use
        """
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment or os.getenv('PINECONE_ENV')
        self.index_name = index_name
        
        if not self.api_key or not self.environment:
            logger.warning("Pinecone credentials not provided. Vector DB operations will fail.")
            self.index = None
            return
        
        try:
            import pinecone
            pinecone.init(api_key=self.api_key, environment=self.environment)
            self.index = pinecone.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
        except ImportError:
            logger.error("Pinecone not installed. Install with: pip install pinecone-client")
            self.index = None
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.index = None
    
    def upsert_embeddings(self,
                         chunks: List[Dict],
                         batch_size: int = 100) -> bool:
        """
        Upsert chunks with embeddings to vector DB.
        
        Args:
            chunks: List of chunks with 'chunk_id' and 'embedding'
            batch_size: Batch size for upserts
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("Pinecone not initialized")
            return False
        
        if not chunks:
            logger.warning("No chunks to upsert")
            return True
        
        try:
            vectors_to_upsert = []
            
            for chunk in chunks:
                chunk_id = chunk.get('chunk_id')
                embedding = chunk.get('embedding')
                
                if not chunk_id or not embedding:
                    logger.warning(f"Skipping chunk without id or embedding: {chunk.get('chunk_id')}")
                    continue
                
                # Convert to list if numpy array
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                # Metadata for filtering
                metadata = {
                    'amc_name': chunk.get('amc_name', ''),
                    'scheme_name': chunk.get('scheme_name', ''),
                    'source_url': chunk.get('source_url', ''),
                    'concepts': ','.join(chunk.get('concepts', [])),
                    'scraped_datetime': chunk.get('scraped_datetime', ''),
                }
                
                vectors_to_upsert.append((chunk_id, embedding, metadata))
                
                # Batch upsert
                if len(vectors_to_upsert) >= batch_size:
                    self.index.upsert(vectors=vectors_to_upsert)
                    logger.debug(f"Upserted {len(vectors_to_upsert)} vectors")
                    vectors_to_upsert = []
            
            # Upsert remaining
            if vectors_to_upsert:
                self.index.upsert(vectors=vectors_to_upsert)
                logger.debug(f"Upserted {len(vectors_to_upsert)} vectors")
            
            logger.info(f"Successfully upserted {len(chunks)} embeddings to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert embeddings: {e}")
            return False
    
    def search(self,
              query_embedding: np.ndarray,
              top_k: int = 5,
              filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            filters: Metadata filters (e.g., {'amc_name': 'HDFC'})
            
        Returns:
            List of top-K similar chunks with scores
        """
        if not self.index:
            logger.error("Pinecone not initialized")
            return []
        
        try:
            # Convert to list if numpy
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Query
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filters
            )
            
            # Format results
            matches = []
            for match in results.get('matches', []):
                matches.append({
                    'chunk_id': match['id'],
                    'score': match.get('score', 0.0),
                    'metadata': match.get('metadata', {}),
                })
            
            logger.debug(f"Found {len(matches)} matches in Pinecone")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to search Pinecone: {e}")
            return []
    
    def delete_index_content(self) -> bool:
        """Clear all vectors from index"""
        if not self.index:
            return False
        
        try:
            self.index.delete(delete_all=True)
            logger.info(f"Cleared all vectors from index {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get index statistics"""
        if not self.index:
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.get('total_vector_count', 0),
                'namespaces': stats.get('namespaces', {}),
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}


class LocalVectorIndex:
    """Fallback in-memory vector index (for testing/development)"""
    
    def __init__(self):
        """Initialize local index"""
        self.vectors = {}  # chunk_id -> embedding
        self.metadata = {}  # chunk_id -> metadata
        logger.info("Using local in-memory vector index (not suitable for production)")
    
    def upsert_embeddings(self, chunks: List[Dict], batch_size: int = 100) -> bool:
        """Store embeddings locally"""
        for chunk in chunks:
            chunk_id = chunk.get('chunk_id')
            embedding = chunk.get('embedding')
            
            if chunk_id and embedding:
                if isinstance(embedding, list):
                    embedding = np.array(embedding)
                self.vectors[chunk_id] = embedding
                self.metadata[chunk_id] = {
                    'amc_name': chunk.get('amc_name'),
                    'scheme_name': chunk.get('scheme_name'),
                    'source_url': chunk.get('source_url'),
                }
        
        logger.info(f"Stored {len(chunks)} embeddings locally")
        return True
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Find top-K similar vectors"""
        if not isinstance(query_embedding, np.ndarray):
            query_embedding = np.array(query_embedding)
        
        # Compute similarities
        similarities = {}
        for chunk_id, vector in self.vectors.items():
            if isinstance(vector, list):
                vector = np.array(vector)
            sim = np.dot(query_embedding, vector)  # Cosine similarity (L2-normalized vectors)
            similarities[chunk_id] = sim
        
        # Get top-K
        top_ids = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = [
            {
                'chunk_id': chunk_id,
                'score': float(score),
                'metadata': self.metadata.get(chunk_id, {}),
            }
            for chunk_id, score in top_ids
        ]
        
        return results


def get_vector_db(use_local: bool = False) -> object:
    """
    Factory function to get vector DB instance.
    
    Args:
        use_local: If True, use local in-memory index. Otherwise try Pinecone.
        
    Returns:
        Vector DB instance (Pinecone or Local)
    """
    if use_local:
        return LocalVectorIndex()
    else:
        return PineconeVectorDB()
