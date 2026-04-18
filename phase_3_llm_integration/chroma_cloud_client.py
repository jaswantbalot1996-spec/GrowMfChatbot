"""
Chroma Cloud Client with Hybrid Search (Dense + Sparse + RRF)
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np
from dataclasses import dataclass

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError(
        "chromadb not installed. Install with: pip install chromadb"
    )

from .config import (
    CHROMA_HOST,
    CHROMA_API_KEY,
    CHROMA_TENANT,
    CHROMA_DATABASE,
    CHROMA_COLLECTION_NAME_TEMPLATE,
    CHROMA_COLLECTION_METADATA,
    DENSE_EMBEDDING_MODEL,
    SPARSE_EMBEDDING_MODEL,
    TOP_K_DENSE,
    TOP_K_SPARSE,
    TOP_K_FINAL,
    RRF_K_PARAMETER,
    DENSE_WEIGHT,
    SPARSE_WEIGHT,
    GROUPBY_FIELD,
    GROUPBY_LIMIT,
)

logger = logging.getLogger(__name__)


@dataclass
class HybridSearchResult:
    """Result from hybrid search combining dense and sparse matches."""
    chunk_id: str
    score: float  # Combined score from RRF
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    metadata: Dict[str, Any] = None
    text: Optional[str] = None
    source_url: Optional[str] = None
    amc_name: Optional[str] = None
    scheme_name: Optional[str] = None


class ChromaCloudClient:
    """Chroma Cloud client with hybrid search capabilities."""
    
    def __init__(self, collection_name: str = "groww_faq"):
        """
        Initialize Chroma Cloud client.
        
        Args:
            collection_name: Collection name (will be prefixed with shard info)
        """
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        self._authenticate()
        self._get_or_create_collection()
    
    def _authenticate(self):
        """Authenticate with Chroma Cloud."""
        try:
            logger.info(f"Authenticating with Chroma Cloud at {CHROMA_HOST}...")
            # Prefer CloudClient API when API key / tenant / database are provided
            try:
                if CHROMA_API_KEY and CHROMA_TENANT and CHROMA_DATABASE:
                    logger.debug("Attempting chromadb.CloudClient authentication")
                    # CloudClient abstracts host/ssl/headers
                    self.client = chromadb.CloudClient(
                        api_key=CHROMA_API_KEY,
                        tenant=CHROMA_TENANT,
                        database=CHROMA_DATABASE,
                    )
                    # CloudClient exposes a simple ping or get_settings depending on SDK
                    try:
                        _ = getattr(self.client, 'get_settings', lambda: True)()
                    except Exception:
                        # ignore; cloud client may not implement get_settings
                        pass
                    logger.info("✓ Successfully authenticated with Chroma Cloud (CloudClient)")
                    return
            except Exception as e:
                logger.warning(f"CloudClient auth failed: {e}")

            # Fallback to HttpClient if CloudClient not available/failed
            self.client = chromadb.HttpClient(
                host=CHROMA_HOST,
                port=443,
                ssl=True,
                headers={
                    "Authorization": f"Bearer {CHROMA_API_KEY}"
                }
            )

            # Verify connection
            _ = self.client.get_settings()
            logger.info("✓ Successfully authenticated with Chroma Cloud (HttpClient)")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Chroma Cloud: {e}")
            raise
    
    def _get_or_create_collection(self):
        """Get or create collection with schema."""
        try:
            logger.info(f"Getting or creating collection: {self.collection_name}")
            
            # Define schema with dense + sparse embeddings
            metadata = CHROMA_COLLECTION_METADATA.copy()
            metadata.update({
                "hnsw:space": "cosine",  # Dense: cosine distance
                "dense_model": DENSE_EMBEDDING_MODEL,
                "sparse_model": SPARSE_EMBEDDING_MODEL,
            })
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata=metadata
            )
            
            logger.info(f"✓ Collection ready: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def upsert_documents(self,
                        documents: List[Dict],
                        batch_size: int = 100) -> bool:
        """
        Upsert documents with 384D embeddings (Qwen model dimension).
        
        Args:
            documents: List of documents with 384D embeddings
            batch_size: Batch size for upserts
            
        Returns:
            True if successful
        """
        if not documents:
            logger.warning("No documents to upsert")
            return True
        
        try:
            logger.info(f"Upserting {len(documents)} documents to Chroma Cloud (384D embeddings)...")
            
            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                
                ids = []
                embeddings = []
                documents_text = []
                metadatas = []
                
                for doc in batch:
                    ids.append(doc['chunk_id'])
                    
                    # Dense embedding (384D from Qwen)
                    embedding = doc.get('embedding')
                    if isinstance(embedding, (list, np.ndarray)):
                        embeddings.append(
                            embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                        )
                    
                    documents_text.append(doc.get('text', ''))
                    
                    # Metadata for filtering and GroupBy
                    metadatas.append({
                        'amc_name': doc.get('amc_name', ''),
                        'scheme_name': doc.get('scheme_name', ''),
                        'source_url': doc.get('source_url', ''),
                        'concepts': ','.join(doc.get('concepts', [])),
                        'scraped_datetime': doc.get('scraped_datetime', ''),
                        'chunk_index': str(doc.get('chunk_index', 0)),
                    })
                
                # Upsert with 384D embeddings
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents_text,
                    metadatas=metadatas,
                )
                
                logger.debug(f"Upserted {len(batch)} documents (384D embeddings)")
            
            logger.info(f"✓ Successfully upserted {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert documents: {e}")
            return False
    
    def hybrid_search(self,
                     query_embedding: Optional[List[float]] = None,
                     query_text: str = "",
                     top_k: Optional[int] = None) -> List[HybridSearchResult]:
        """
        Hybrid search using text-based queries (most reliable).
        
        Args:
            query_embedding: (Ignored - using text-based instead)
            query_text: Query text for searching
            top_k: Number of final results to return
            
        Returns:
            List of hybrid search results
        """
        if top_k is None:
            top_k = TOP_K_FINAL
        
        if not query_text:
            logger.warning("Empty query text provided to hybrid_search")
            return []
        
        try:
            # Use text-based query - most reliable with Chroma Cloud
            logger.debug(f"Searching with text query: {query_text[:50]}...")
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k * 2,  # Fetch extra for deduplication
                include=["documents", "metadatas", "distances"],
            )
            
            # Parse results
            hybrid_results = []
            seen_sources = {}  # Track by source for GroupBy
            
            if results and results['ids'] and len(results['ids']) > 0:
                for idx, chunk_id in enumerate(results['ids'][0]):
                    # Get metadata and content
                    metadata = results['metadatas'][0][idx] if results['metadatas'] else {}
                    document = results['documents'][0][idx] if results['documents'] else ""
                    distance = results['distances'][0][idx] if results['distances'] else 1.0
                    
                    # Convert distance to similarity score (0-1 range)
                    similarity = max(0.0, 1.0 - distance) if distance is not None else 0.0
                    
                    source_url = metadata.get('source_url', 'unknown')
                    
                    # Apply GroupBy deduplication - limit results per source
                    if source_url not in seen_sources:
                        seen_sources[source_url] = 0
                    
                    if seen_sources[source_url] < GROUPBY_LIMIT:
                        seen_sources[source_url] += 1
                        
                        result = HybridSearchResult(
                            chunk_id=chunk_id,
                            text=document,
                            score=float(similarity),
                            source_url=source_url,
                            metadata=metadata,
                        )
                        hybrid_results.append(result)
                    
                    # Stop if we have enough results
                    if sum(seen_sources.values()) >= top_k:
                        break
            
            logger.debug(f"Hybrid search returned {len(hybrid_results)} results")
            return hybrid_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            import traceback
            traceback.print_exc()
            return []
            
            # Fetch full document data and apply GroupBy
            final_results = []
            source_urls_seen = {}  # Track sources for GroupBy
            
            for chunk_id, rrf_score in sorted_results:
                if len(final_results) >= top_k:
                    break
                
                try:
                    # Get document from collection
                    doc_data = self.collection.get(ids=[chunk_id])
                    
                    if doc_data and doc_data['ids']:
                        metadata = doc_data['metadatas'][0] if doc_data['metadatas'] else {}
                        source_url = metadata.get('source_url', 'unknown')
                        
                        # GroupBy deduplication
                        if source_url not in source_urls_seen:
                            source_urls_seen[source_url] = 0
                        
                        if source_urls_seen[source_url] < GROUPBY_LIMIT:
                            source_urls_seen[source_url] += 1
                            
                            result = HybridSearchResult(
                                chunk_id=chunk_id,
                                score=rrf_score,
                                dense_score=dense_matches.get(chunk_id, {}).get('score'),
                                sparse_score=sparse_matches.get(chunk_id, {}).get('score'),
                                metadata=metadata,
                                text=doc_data['documents'][0] if doc_data['documents'] else None,
                                source_url=source_url,
                                amc_name=metadata.get('amc_name'),
                                scheme_name=metadata.get('scheme_name'),
                            )
                            
                            final_results.append(result)
                
                except Exception as e:
                    logger.warning(f"Failed to fetch document {chunk_id}: {e}")
                    continue
            
            logger.info(f"✓ Hybrid search returned {len(final_results)} deduplicated results")
            # If no results from hybrid search, fall back to simple substring match
            if not final_results:
                logger.info("Hybrid search returned no results; using substring fallback")
                try:
                    all_docs = self.collection.get(limit=1000)
                    for idx, doc_text in enumerate(all_docs.get('documents', [])):
                        if query_text.lower() in (doc_text or '').lower():
                            chunk_id = all_docs['ids'][idx]
                            metadata = all_docs['metadatas'][idx] if all_docs.get('metadatas') else {}
                            result = HybridSearchResult(
                                chunk_id=chunk_id,
                                score=1.0,
                                dense_score=None,
                                sparse_score=None,
                                metadata=metadata,
                                text=doc_text,
                                source_url=metadata.get('source_url') if metadata else None,
                                amc_name=metadata.get('amc_name') if metadata else None,
                                scheme_name=metadata.get('scheme_name') if metadata else None,
                            )
                            final_results.append(result)
                except Exception as e:
                    logger.warning(f"Fallback substring retrieval failed: {e}")

            return final_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection_name,
                'total_documents': count,
                'embedding_model': DENSE_EMBEDDING_MODEL,
                'sparse_model': SPARSE_EMBEDDING_MODEL,
                'hybrid_search_enabled': True,
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    def delete_collection(self) -> bool:
        """Delete collection (use with caution)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.warning(f"✓ Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False


def create_chroma_client(amc_name: Optional[str] = None) -> ChromaCloudClient:
    """
    Factory function to create Chroma Cloud client with shard-specific collection.
    
    Args:
        amc_name: AMC name for collection sharding (optional)
        
    Returns:
        ChromaCloudClient instance
    """
    if amc_name:
        collection_name = CHROMA_COLLECTION_NAME_TEMPLATE.format(
            amc_name_lower=amc_name.lower().replace(" ", "_")
        )
    else:
        collection_name = "groww_faq"
    
    return ChromaCloudClient(collection_name=collection_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test connection
    print("Testing Chroma Cloud connection...")
    client = create_chroma_client()
    stats = client.get_collection_stats()
    print(f"✓ Collection stats: {stats}")
