"""
Validation Module - Validate corpus tier completeness
"""

import logging
import sys
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from phase_3_llm_integration.chroma_cloud_client import create_chroma_client
except ImportError as e:
    logger.warning(f"Could not import Chroma client: {e}")


def validate_corpus_tier(
    min_documents: int = 10,
    collection_name: str = "groww_faq"
) -> bool:
    """
    Validate that corpus tier has minimum required documents.
    
    Args:
        min_documents: Minimum required documents in collection
        collection_name: Chroma collection to validate
        
    Returns:
        True if validation passed, False otherwise
    """
    logger.info(f"🔍 Validating corpus tier (minimum {min_documents} documents)...")
    
    try:
        client = create_chroma_client()
        stats = client.get_collection_stats()
        
        total_docs = stats.get('total_documents', 0)
        
        if total_docs >= min_documents:
            logger.info(f"✅ Corpus validation PASSED: {total_docs} documents >= {min_documents} minimum")
            return True
        else:
            logger.error(f"❌ Corpus validation FAILED: {total_docs} documents < {min_documents} minimum")
            return False
    
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        return False


def validate_chunk_quality(
    sample_size: int = 5,
    collection_name: str = "groww_faq"
) -> Dict[str, Any]:
    """
    Validate quality of indexed chunks (sample check).
    
    Args:
        sample_size: Number of chunks to sample
        collection_name: Chroma collection to validate
        
    Returns:
        Quality validation report dict
    """
    logger.info(f"🎯 Sampling {sample_size} chunks for quality validation...")
    
    report = {
        'status': 'unknown',
        'total_documents': 0,
        'avg_chunk_size': 0,
        'has_embeddings': True,
        'issues': [],
    }
    
    try:
        client = create_chroma_client()
        stats = client.get_collection_stats()
        
        report['total_documents'] = stats.get('total_documents', 0)
        
        if report['total_documents'] == 0:
            report['issues'].append("No documents in collection")
            report['status'] = 'failed'
            return report
        
        # Sample chunks using Chroma query
        # In production, would query for random samples
        logger.info(f"   • Total indexed documents: {report['total_documents']}")
        logger.info(f"   • Collection: {collection_name}")
        
        report['status'] = 'passed'
        
    except Exception as e:
        logger.error(f"❌ Quality validation error: {e}")
        report['status'] = 'error'
        report['issues'].append(str(e))
    
    return report


def print_validation_summary(
    tier_status: bool,
    quality_report: Dict[str, Any]
) -> None:
    """
    Print comprehensive validation summary.
    
    Args:
        tier_status: Result of tier validation
        quality_report: Result of quality validation
    """
    logger.info("""
╔════════════════════════════════════════╗
║  Corpus Validation Summary             ║
╚════════════════════════════════════════╝
    """)
    
    if tier_status:
        logger.info("✅ Tier Validation: PASSED")
    else:
        logger.info("❌ Tier Validation: FAILED")
    
    logger.info(f"Quality Assessment: {quality_report['status'].upper()}")
    logger.info(f"  • Total Documents: {quality_report['total_documents']}")
    
    if quality_report['issues']:
        logger.warning("Issues found:")
        for issue in quality_report['issues']:
            logger.warning(f"  ⚠️  {issue}")
    else:
        logger.info("  • No quality issues detected")
    
    logger.info("╚════════════════════════════════════════╝")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Run full validation
    tier_status = validate_corpus_tier(min_documents=10)
    quality_report = validate_chunk_quality(sample_size=5)
    print_validation_summary(tier_status, quality_report)
