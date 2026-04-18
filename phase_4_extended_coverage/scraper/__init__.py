"""
Phase 4 Scraper Module - Daily corpus refresh for 15 Groww AMC URLs
"""

from .fetch_urls import fetch_all_urls
from .parse_chunks import parse_and_chunk_content
from .generate_embeddings import generate_embeddings_for_chunks
from .update_indexes import update_chroma_cloud_index
from .validate_tier import validate_corpus_tier

__all__ = [
    'fetch_all_urls',
    'parse_and_chunk_content',
    'generate_embeddings_for_chunks',
    'update_chroma_cloud_index',
    'validate_corpus_tier',
]

__version__ = "4.0.0"
