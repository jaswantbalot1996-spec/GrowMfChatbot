"""
Ollama LLM client - Local facts-only FAQ assistant
Uses locally installed Ollama with models like llama3.2 or gemma3
"""
import logging
from typing import List, Optional, Dict, Any
import requests
from .config import (
    GEMINI_MAX_TOKENS,
    GEMINI_TEMPERATURE,
    SYSTEM_PROMPT,
    QUERY_TEMPLATE,
)

logger = logging.getLogger(__name__)


class OllamaLLMClient:
    """Ollama local LLM client wrapper."""

    # Ollama API endpoint (default local)
    BASE_ENDPOINT = "http://localhost:11434/api/generate"

    def __init__(self, model: Optional[str] = None):
        """
        Initialize Ollama client.
        
        Args:
            model: Model name (e.g., 'llama3.2', 'gemma3:4b'). Defaults to 'llama3.2:latest'
        """
        self.model = model or "llama3.2:latest"
        self.max_tokens = GEMINI_MAX_TOKENS  # Reuse config max tokens
        self.temperature = GEMINI_TEMPERATURE  # Reuse config temperature
        self.endpoint = self.BASE_ENDPOINT

        logger.info(f"Ollama client initialized: model={self.model}, temperature={self.temperature} (local)")

    def _check_connection(self) -> bool:
        """Verify Ollama is running and responding."""
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=2)
            return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama connection check failed: {e}")
            return False

    def generate_response(self, query: str, search_results: List[Any], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate response using Ollama.
        
        Args:
            query: User query
            search_results: List of search results from Chroma
            system_prompt: Optional system prompt override
            
        Returns:
            Dict with 'response', 'sources', 'confidence', 'model' keys
        """
        try:
            # Check connection
            if not self._check_connection():
                logger.error("Ollama service not responding")
                return {'response': '', 'sources': [], 'confidence': 0.0}

            # Build context
            context_pieces = []
            valid_sources = []
            for result in search_results:
                # result expected to have .text and metadata
                text = getattr(result, 'text', str(result))
                context_pieces.append(text)
                valid_sources.append({
                    'chunk_id': getattr(result, 'chunk_id', None),
                    'score': float(getattr(result, 'score', 0.0)),
                })

            if not system_prompt:
                system_prompt = SYSTEM_PROMPT

            context = "\n".join(context_pieces)
            user_message = QUERY_TEMPLATE.format(context=context, query=query)
            
            # Combine system prompt and user message
            full_prompt = f"{system_prompt}\n\n{user_message}"

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "temperature": float(self.temperature),
                "num_predict": int(self.max_tokens),
                "stream": False,
            }

            logger.debug(f"Calling Ollama endpoint: {self.endpoint} with model={self.model}")
            resp = requests.post(self.endpoint, json=payload, timeout=120)
            
            if resp.status_code != 200:
                logger.error(f"Ollama API error: {resp.status_code} - {resp.text}")
                return {'response': '', 'sources': valid_sources, 'confidence': 0.0}

            data = resp.json()
            answer = data.get('response', '').strip()
            
            if not answer:
                logger.warning(f"Empty response from Ollama: {data}")
                return {'response': '', 'sources': valid_sources, 'confidence': 0.0}

            return {
                'response': answer,
                'sources': valid_sources,
                'confidence': float(sum(s['score'] for s in valid_sources) / len(valid_sources)) if valid_sources else 0.0,
                'model': self.model,
            }

        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out (model may be generating)")
            return {'response': '', 'sources': [], 'confidence': 0.0}
        except Exception as e:
            logger.error(f"Ollama client error: {e}")
            return {'response': '', 'sources': [], 'confidence': 0.0}
