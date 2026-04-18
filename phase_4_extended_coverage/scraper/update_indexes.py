"""
Update Indexes Module - Push chunks to Chroma Cloud
"""

import logging
import sys
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from phase_3_llm_integration.chroma_cloud_client import create_chroma_client
    from phase_3_llm_integration.data_import import import_chunks_to_chroma_cloud
except ImportError as e:
    logger.warning(f"Could not import Chroma clients: {e}")


def update_chroma_cloud_index(
    chunks: List[Dict[str, Any]],
    collection_name: str = "groww_faq",
    batch_size: int = 100
) -> bool:
    """
    Update Chroma Cloud index with chunks.
    
    Args:
        chunks: List of chunks with embeddings (from generate_embeddings.py)
        collection_name: Chroma collection name
        batch_size: Upsert batch size
        
    Returns:
        True if successful, False otherwise
    """
    if not chunks:
        logger.warning("No chunks to index")
        return False
    
    logger.info(f"📋 Preparing to index {len(chunks)} chunks to Chroma Cloud...")
    
    try:
        # Import chunks using existing utility
        success = import_chunks_to_chroma_cloud(
            chunks=chunks,
            collection_name=collection_name,
            batch_size=batch_size
        )
        
        if success:
            logger.info(f"✅ Successfully indexed {len(chunks)} chunks to Chroma Cloud")
            return True
        else:
            logger.error("❌ Failed to import chunks to Chroma Cloud")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error updating Chroma Cloud index: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_index_update(collection_name: str = "groww_faq") -> Dict[str, Any]:
    """
    Verify that chunks were successfully indexed.
    
    Args:
        collection_name: Chroma collection name
        
    Returns:
        Collection statistics dict
    """
    try:
        client = create_chroma_client()
        stats = client.get_collection_stats()
        
        logger.info(f"💾 Chroma Cloud collection stats:")
        logger.info(f"   • Total documents: {stats.get('total_documents', 0)}")
        logger.info(f"   • Collection: {collection_name}")
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ Error verifying index: {e}")
        return {}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test index verification
    logger.info("Testing Chroma Cloud index verification...")
    stats = verify_index_update()
    print(f"Stats: {stats}")
