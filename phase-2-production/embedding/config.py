"""
Embedding Service Configuration
Embedding model and batch processing parameters
"""

import os
from typing import Dict, Any

class EmbeddingConfig:
    """Configuration for embedding generation"""
    
    # Model configuration
    MODEL_NAME = os.getenv(
        'EMBEDDING_MODEL', 
        'sentence-transformers/all-mpnet-base-v2'
    )
    EMBEDDING_DIM = 768  # all-mpnet-base-v2 dimension
    
    # Device selection
    DEVICE = os.getenv('EMBEDDING_DEVICE', 'auto')  # auto, cuda, cpu
    
    # Batch processing
    BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', 100))
    MAX_SEQ_LENGTH = 512  # Model max sequence length
    
    # Normalization
    NORMALIZE_EMBEDDINGS = True  # L2 normalization for cosine similarity
    
    # Performance
    SHOW_PROGRESS_BAR = os.getenv('SHOW_PROGRESS', 'false').lower() == 'true'
    
    # For retry logic
    MAX_RETRIES = int(os.getenv('EMBEDDING_MAX_RETRIES', 3))
    RETRY_BACKOFF_FACTOR = float(os.getenv('EMBEDDING_RETRY_BACKOFF', 1.5))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'model_name': cls.MODEL_NAME,
            'embedding_dim': cls.EMBEDDING_DIM,
            'batch_size': cls.BATCH_SIZE,
            'normalize': cls.NORMALIZE_EMBEDDINGS,
            'device': cls.DEVICE,
        }
