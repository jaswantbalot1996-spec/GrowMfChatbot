"""
Chunking Service Configuration
Semantic chunking parameters for breaking down Groww AMC pages into retrievable chunks
"""

import os
from typing import Dict, Any

class ChunkingConfig:
    """Configuration for semantic chunking"""
    
    # Token budget for chunks
    MIN_TOKENS = int(os.getenv('CHUNK_MIN_TOKENS', 300))
    MAX_TOKENS = int(os.getenv('CHUNK_MAX_TOKENS', 500))
    OVERLAP_TOKENS = int(os.getenv('CHUNK_OVERLAP_TOKENS', 50))
    
    # Tokenizer config
    TOKENIZER_MODEL = 'sentence-transformers/all-mpnet-base-v2'
    
    # Concept extraction patterns
    CONCEPT_PATTERNS = {
        'expense_ratio': r'expense ratio|ER|annual fees?|management fee',
        'exit_load': r'exit load|exit charge|redemption charge',
        'lock_in': r'lock.?in|lock period|ELSS|3.?years?',
        'minimum_sip': r'minimum SIP|min.*SIP|SIP amount',
        'statement': r'statement|download|annual report',
        'riskometer': r'riskometer|risk level|risk classification',
        'benchmark': r'benchmark|NSE Nifty|Sensex|BSE',
        'fund_details': r'fund type|category|launch date|ISIN',
        'aum': r'assets under management|AUM',
        'dividend': r'dividend|distribution|payout',
    }
    
    # Chunk quality thresholds
    MIN_CHUNK_LENGTH_CHARS = 50  # Minimum characters to avoid empty chunks
    MIN_SENTENCE_LENGTH_WORDS = 3  # Filter out single-word "sentences"
    
    # Sentence segmentation
    SENTENCE_TOKENIZER = 'punkt'  # NLTK tokenizer
    
    # Batch processing
    BATCH_SIZE = 100  # Chunks per batch during processing
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary for serialization"""
        return {
            'min_tokens': cls.MIN_TOKENS,
            'max_tokens': cls.MAX_TOKENS,
            'overlap_tokens': cls.OVERLAP_TOKENS,
            'tokenizer_model': cls.TOKENIZER_MODEL,
            'batch_size': cls.BATCH_SIZE,
        }
