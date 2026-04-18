"""
Phase 3 LLM Integration Module
Hybrid Search (Dense + Sparse + RRF) + Ollama LLM (Local)
Powered by Chroma Cloud
"""

from .phase3_service import Phase3QueryService, create_phase3_service
from .chroma_cloud_client import ChromaCloudClient, HybridSearchResult, create_chroma_client
from .ollama_client import OllamaLLMClient
from .data_import import import_chunks_to_chroma_cloud, validate_import
from .config import validate_config

__all__ = [
    'Phase3QueryService',
    'create_phase3_service',
    'ChromaCloudClient',
    'HybridSearchResult',
    'create_chroma_client',
    'OllamaLLMClient',
    'import_chunks_to_chroma_cloud',
    'validate_import',
    'validate_config',
]

__version__ = "3.0.0"
