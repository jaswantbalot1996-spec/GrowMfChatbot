"""
Phase 3 Main Service - Orchestrates Hybrid Search + LLM Response Generation
Ollama LLM (Local) + Chroma Cloud Hybrid Search
"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from .chroma_cloud_client import create_chroma_client, ChromaCloudClient
from .config import validate_config, print_config_summary, LLM_PROVIDER
from .ollama_client import OllamaLLMClient

logger = logging.getLogger(__name__)


class Phase3QueryService:
    """Phase 3 Query Service - Hybrid Search + LLM."""
    
    def __init__(self):
        """Initialize Phase 3 service."""
        
        # Validate configuration
        if not validate_config():
            raise ValueError("Configuration validation failed")
        
        try:
            print_config_summary()
        except Exception as e:
            logger.warning(f"print_config_summary failed: {e}")
        
        # Initialize clients
        logger.info("Initializing Phase 3 service components...")

        try:
            self.chroma_client = create_chroma_client()
        except Exception as e:
            logger.warning(f"Failed to initialize Chroma client: {e}")
            self.chroma_client = None

        # Initialize Ollama LLM client (local)
        try:
            self.llm_client = OllamaLLMClient()
            logger.info("Ollama LLM client initialized successfully for Phase 3")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM client: {e}")
            raise ValueError(f"Ollama LLM initialization failed: {e}")

        logger.info("Phase 3 service initialized successfully")
    
    def query(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a query end-to-end:
        1. Encode query with dense embedding
        2. Perform hybrid search (dense + sparse with RRF)
        3. Generate response with Gemini LLM
        
        Args:
            query: User query (in English or Hindi)
            top_k: Number of final results to return
            
        Returns:
            Response dict with answer, sources, metadata
        """
        
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Step 1: No need to pre-generate embeddings - Chroma handles it
            logger.debug("Step 1: Preparing to search Chroma Cloud...")
            
            # Step 2: Hybrid search (text-based, most reliable)
            search_results = []
            if self.chroma_client:
                logger.debug("Step 2: Performing hybrid search...")
                search_results = self.chroma_client.hybrid_search(
                    query_text=query,
                    top_k=top_k,
                )
            else:
                logger.warning("Chroma client unavailable — proceeding with LLM-only generation")
            
            # Log search result count (may be zero — LLM-only generation will proceed)
            logger.debug(f"Found {len(search_results)} search results")
            
            # Step 3: Generate response with chosen LLM
            logger.debug("Step 3: Generating response with LLM...")
            if hasattr(self, '_generate_func') and self._generate_func:
                response_data = self._generate_func(query, search_results, self.llm_client)
            else:
                # Gemini style client has generate_response method
                response_data = self.llm_client.generate_response(query, search_results)
            # If LLM returned empty or no useful answer, fallback to local FAQ generator
            if not response_data or not response_data.get('response'):
                logger.warning("LLM returned empty response — using local fallback generator")
                response_data = self._local_fallback_generate(query)
            
            # Add metadata
            response_data['query'] = query
            response_data['num_sources'] = len(search_results)
            response_data['latency_ms'] = (time.time() - start_time) * 1000
            response_data['status'] = 'success'
            
            logger.info(f"[OK] Query processed in {response_data['latency_ms']:.1f}ms")
            
            return response_data
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                'query': query,
                'response': f"An error occurred: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'latency_ms': (time.time() - start_time) * 1000,
                'error': str(e),
                'status': 'error',
            }
    
    def batch_query(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple queries.
        
        Args:
            queries: List of queries
            
        Returns:
            List of response dicts
        """
        
        logger.info(f"Processing batch of {len(queries)} queries...")
        
        responses = []
        for i, query in enumerate(queries, 1):
            logger.debug(f"[{i}/{len(queries)}] Processing query...")
            response = self.query(query)
            responses.append(response)
        
        logger.info(f"✓ Batch processing complete ({len(responses)} queries)")
        return responses
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        
        try:
            chroma_stats = self.chroma_client.get_collection_stats()
            
            return {
                'status': 'healthy',
                'chroma_cloud': {
                    'collection': chroma_stats.get('collection_name'),
                    'total_documents': chroma_stats.get('total_documents'),
                    'dense_embedding_model': chroma_stats.get('embedding_model'),
                    'sparse_embedding_model': chroma_stats.get('sparse_model'),
                    'hybrid_search_enabled': chroma_stats.get('hybrid_search_enabled'),
                },
                'grok_llm': {
                    'model': self.grok_client.model,
                    'max_tokens': self.grok_client.max_tokens,
                    'temperature': self.grok_client.temperature,
                },
                'timestamp': str(time.time()),
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'status': 'error', 'error': str(e)}

    def _local_fallback_generate(self, query: str) -> Dict[str, Any]:
        """Simple local generator to provide helpful answers when external LLM fails.

        This is a lightweight fallback for demo purposes; it matches keywords to
        canned responses to keep the UI functional.
        """
        q = query.lower()
        faq_map = {
            'elss': "ELSS (Equity Linked Savings Scheme) is a mutual fund category that offers tax deduction under Section 80C. It has a 3-year lock-in period.",
            'nav': "NAV (Net Asset Value) is the per-unit value of a mutual fund: (Total Assets - Total Liabilities) / Number of Units.",
            'expense': "Expense ratio is the annual fee charged by a mutual fund as a percentage of assets under management.",
            'sip': "SIP (Systematic Investment Plan) lets you invest fixed amounts regularly and benefits from rupee cost averaging.",
        }

        for k, v in faq_map.items():
            if k in q:
                return {'response': v, 'sources': [{'source': 'Local_Fallback_FAQ', 'relevance': 0.9}], 'confidence': 0.6}

        # Default fallback
        return {'response': "I don't have enough information to answer that precisely. Please try a more specific question or use the demo FAQ.", 'sources': [{'source': 'Local_Fallback_FAQ', 'relevance': 0.5}], 'confidence': 0.2}


def create_phase3_service() -> Phase3QueryService:
    """Factory function to create Phase 3 service."""
    return Phase3QueryService()


# API Server Integration (Flask example)
if __name__ == "__main__":
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test service
    print("\n" + "=" * 70)
    print("Phase 3 Query Service - Interactive Testing")
    print("=" * 70 + "\n")
    
    try:
        service = create_phase3_service()
        
        # Show statistics
        stats = service.get_statistics()
        print(f"Service Statistics:\n{stats}\n")
        
        # Test queries
        test_queries = [
            "What is the expense ratio of HDFC Large-Cap Fund?",
            "Which funds have the lowest exit load?",
            "What is the difference between Large Cap and Mid Cap funds?",
        ]
        
        print("Running test queries...\n")
        for query in test_queries:
            print(f"Q: {query}")
            response = service.query(query)
            print(f"A: {response['response'][:200]}...")
            print(f"Confidence: {response['confidence']:.2%}, Latency: {response['latency_ms']:.1f}ms")
            print(f"Sources: {response['num_sources']}\n")
        
        print("[OK] Phase 3 service is operational!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        exit(1)
