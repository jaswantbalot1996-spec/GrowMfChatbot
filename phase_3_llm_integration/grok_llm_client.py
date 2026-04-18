"""
Grok LLM Integration - Response Generation with Context Awareness
"""

import logging
from typing import List, Optional, Dict, Any
import json

try:
    import requests
except ImportError:
    raise ImportError("requests not installed. Install with: pip install requests")

from .config import (
    GROK_API_KEY,
    GROK_MODEL,
    GROK_MAX_TOKENS,
    GROK_TEMPERATURE,
    SYSTEM_PROMPT,
    QUERY_TEMPLATE,
    MIN_SIMILARITY_SCORE,
)
from .chroma_cloud_client import HybridSearchResult

logger = logging.getLogger(__name__)


class GrokLLMClient:
    """Grok LLM client for response generation."""
    
    # Grok API endpoint (xAI's API)
    API_ENDPOINT = "https://api.x.ai/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Grok LLM client.
        
        Args:
            api_key: xAI API key (defaults to GROK_API_KEY from env)
        """
        self.api_key = api_key or GROK_API_KEY
        
        if not self.api_key:
            raise ValueError(
                "GROK_API_KEY not set. "
                "Get key from https://console.x.ai/ and set GROK_API_KEY env var"
            )
        
        self.model = GROK_MODEL
        self.max_tokens = GROK_MAX_TOKENS
        self.temperature = GROK_TEMPERATURE
        
        logger.info(f"Grok LLM initialized: model={self.model}")
    
    def generate_response(self,
                         query: str,
                         search_results: List[HybridSearchResult],
                         system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate response using Grok LLM with search context.
        
        Args:
            query: User query
            search_results: List of HybridSearchResult from hybrid search
            system_prompt: Custom system prompt (optional)
            
        Returns:
            Dict with response, sources, confidence, etc.
        """
        
        try:
            # Build context from search results (filter by similarity)
            context_pieces = []
            valid_sources = []
            
            for result in search_results:
                # Filter by minimum similarity score
                if result.score < MIN_SIMILARITY_SCORE:
                    logger.debug(f"Skipping result due to low score: {result.score}")
                    continue
                
                piece = f"""
Source: {result.amc_name} - {result.scheme_name}
URL: {result.source_url}
Score: {result.score:.3f} (Dense: {result.dense_score:.3f}, Sparse: {result.sparse_score:.3f})
---
{result.text}
"""
                context_pieces.append(piece)
                valid_sources.append({
                    'chunk_id': result.chunk_id,
                    'amc_name': result.amc_name,
                    'scheme_name': result.scheme_name,
                    'source_url': result.source_url,
                    'score': float(result.score),
                })
            
            if not context_pieces:
                logger.warning(f"No context found for query: {query}")
                return {
                    'response': "I couldn't find relevant information to answer your question.",
                    'sources': [],
                    'confidence': 0.0,
                    'error': 'No relevant context found',
                }
            
            # Prepare context string
            context = "\n".join(context_pieces)
            
            # Build prompt
            if not system_prompt:
                system_prompt = SYSTEM_PROMPT
            
            user_message = QUERY_TEMPLATE.format(
                context=context,
                query=query,
            )
            
            logger.debug(f"Generating response with Grok...")
            logger.debug(f"Context length: {len(context)} chars, Sources: {len(valid_sources)}")
            
            # Call Grok API
            response = self._call_grok_api(system_prompt, user_message)
            
            if not response:
                return {
                    'response': "An error occurred while generating the response.",
                    'sources': valid_sources,
                    'confidence': 0.0,
                    'error': 'LLM API error',
                }
            
            # Extract response text
            answer = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Calculate confidence (average of top sources)
            avg_source_confidence = (
                sum(s['score'] for s in valid_sources) / len(valid_sources)
                if valid_sources else 0.0
            )
            
            logger.info(f"✓ Generated response using {len(valid_sources)} sources")
            
            return {
                'response': answer,
                'sources': valid_sources,
                'confidence': float(avg_source_confidence),
                'model': self.model,
                'input_tokens': response.get('usage', {}).get('prompt_tokens', 0),
                'output_tokens': response.get('usage', {}).get('completion_tokens', 0),
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                'response': f"An error occurred: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'error': str(e),
            }
    
    def _call_grok_api(self, system_prompt: str, user_message: str) -> Optional[Dict]:
        """
        Call Grok API.
        
        Args:
            system_prompt: System prompt for Grok
            user_message: User message
            
        Returns:
            Response dict from Grok API
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
            
            logger.debug(f"Calling Grok API: {self.API_ENDPOINT}")
            
            response = requests.post(
                self.API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=60,
            )
            
            # Check for errors
            if response.status_code != 200:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                return None
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Request to Grok API failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Grok API: {e}")
            return None


def generate_answer(query: str,
                   search_results: List[HybridSearchResult],
                   grok_client: Optional[GrokLLMClient] = None) -> Dict[str, Any]:
    """
    Generate answer from query and search results using Grok.
    
    Args:
        query: User query
        search_results: List of HybridSearchResult
        grok_client: GrokLLMClient instance (creates new if not provided)
        
    Returns:
        Response dict with answer, sources, confidence
    """
    if not grok_client:
        grok_client = GrokLLMClient()
    
    return grok_client.generate_response(query, search_results)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Grok connection
    print("Testing Grok LLM connection...")
    try:
        client = GrokLLMClient()
        print(f"✓ Grok LLM initialized: {client.model}")
        
        # Test with mock search result
        mock_result = HybridSearchResult(
            chunk_id="test_001",
            score=0.95,
            dense_score=0.95,
            sparse_score=0.90,
            text="The expense ratio of HDFC Large-Cap Fund is 0.50% per annum.",
            source_url="https://groww.in/mutual-funds/hdfc-large-cap-fund",
            amc_name="HDFC",
            scheme_name="Large-Cap Fund",
        )
        
        response = client.generate_response(
            query="What is the expense ratio of HDFC Large-Cap Fund?",
            search_results=[mock_result],
        )
        
        print(f"\nTest Response:")
        print(f"Answer: {response['response']}")
        print(f"Confidence: {response['confidence']:.2%}")
        print(f"Sources: {len(response['sources'])}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
