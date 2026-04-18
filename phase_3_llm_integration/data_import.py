"""
Chroma Cloud Data Import - Import chunks directly from Phase 2

This is NOT a migration (we never used Pinecone).
This is for importing freshly chunked data from Phase 2 into Chroma Cloud.
"""

import logging
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from .chroma_cloud_client import create_chroma_client
from .config import IMPORT_BATCH_SIZE, PRESERVE_METADATA

logger = logging.getLogger(__name__)


def import_chunks_to_chroma_cloud(chunks: List[Dict[str, Any]],
                                  collection_name: str = "groww_faq",
                                  batch_size: int = IMPORT_BATCH_SIZE) -> bool:
    """
    Import chunks directly into Chroma Cloud.
    Uses 384D embeddings (Qwen model dimension).
    
    Args:
        chunks: List of chunks from Phase 2 (with embeddings)
        collection_name: Target collection name
        batch_size: Batch size for upserts
        
    Returns:
        True if successful
    """
    
    try:
        logger.info(f"Initializing Chroma Cloud client for collection: {collection_name}")
        chroma_client = create_chroma_client()
        
        if not chunks:
            logger.warning("No chunks to import")
            return True
        
        logger.info(f"Importing {len(chunks)} chunks to Chroma Cloud (384D embeddings)...")
        
        # Prepare chunks for upsert
        prepared_chunks = []
        for chunk in chunks:
            prepared_chunk = {
                'chunk_id': chunk.get('chunk_id'),
                'embedding': chunk.get('embedding'),  # Keep embeddings - they're 384D
                'text': chunk.get('text', ''),
                'amc_name': chunk.get('amc_name', ''),
                'scheme_name': chunk.get('scheme_name', ''),
                'source_url': chunk.get('source_url', ''),
                'concepts': chunk.get('concepts', []),
                'scraped_datetime': chunk.get('scraped_datetime', ''),
                'chunk_index': chunk.get('chunk_index', 0),
            }
            prepared_chunks.append(prepared_chunk)
        
        # Upsert to Chroma Cloud
        success = chroma_client.upsert_documents(
            documents=prepared_chunks,
            batch_size=batch_size
        )
        
        if success:
            logger.info(f"✓ Successfully imported {len(chunks)} chunks to Chroma Cloud")
            stats = chroma_client.get_collection_stats()
            logger.info(f"Collection stats: {stats}")
            return True
        else:
            logger.error("Failed to import chunks to Chroma Cloud")
            return False
            
    except Exception as e:
        logger.error(f"Failed to import to Chroma Cloud: {e}")
        raise


def validate_import(chroma_collection: str = "groww_faq") -> bool:
    """
    Validate that chunks were successfully imported to Chroma Cloud.
    
    Args:
        chroma_collection: Collection to validate
        
    Returns:
        True if validation successful
    """
    
    try:
        logger.info(f"Validating import to {chroma_collection}...")
        
        chroma_client = create_chroma_client()
        
        stats = chroma_client.get_collection_stats()
        total_docs = stats.get('total_documents', 0)
        
        if total_docs == 0:
            logger.error("No documents in Chroma Cloud collection")
            return False
        
        logger.info(f"✓ Import validation passed!")
        logger.info(f"  - Total documents: {total_docs}")
        logger.info(f"  - Dense embedding model: {stats.get('embedding_model')}")
        logger.info(f"  - Sparse embedding model: {stats.get('sparse_model')}")
        logger.info(f"  - Hybrid search enabled: {stats.get('hybrid_search_enabled')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Import validation failed: {e}")
        return False


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    print("""
    Chroma Cloud Data Import Tool
    (For importing chunks from Phase 2)
    
    Usage:
        from phase_3_llm_integration.data_import import import_chunks_to_chroma_cloud
        
        chunks = [...]  # From Phase 2
        import_chunks_to_chroma_cloud(chunks)
    """)
