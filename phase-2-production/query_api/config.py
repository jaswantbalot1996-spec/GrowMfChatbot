"""
Query API Configuration
Settings for the FastAPI query service
"""

import os
from typing import Dict, Any

class QueryAPIConfig:
    """Configuration for query API"""
    
    # API settings
    HOST = os.getenv('QUERY_API_HOST', '127.0.0.1')
    PORT = int(os.getenv('QUERY_API_PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Query processing
    MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', 500))
    QUERY_TIMEOUT_SECONDS = int(os.getenv('QUERY_TIMEOUT', 30))
    
    # Retrieval
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', 5))
    MIN_SIMILARITY_SCORE = float(os.getenv('MIN_SIMILARITY_SCORE', 0.5))
    
    # LLM
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')  # or claude-3-5, llama-2-13b
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', 150))
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0.3))
    
    # Redis cache
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL', 3600))  # 1 hour
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'debug': cls.DEBUG,
            'top_k_results': cls.TOP_K_RESULTS,
            'min_similarity_score': cls.MIN_SIMILARITY_SCORE,
        }
