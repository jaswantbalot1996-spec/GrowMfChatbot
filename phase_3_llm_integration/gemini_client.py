"""
Gemini (Google Generative) LLM client - Facts-only FAQ assistant
"""
import logging
from typing import List, Optional, Dict, Any
import os
import requests
from .config import (
    GEMINI_MAX_TOKENS,
    GEMINI_TEMPERATURE,
    SYSTEM_PROMPT,
    QUERY_TEMPLATE,
)

logger = logging.getLogger(__name__)


class GeminiLLMClient:
    """Simple Gemini/Text-Bison client wrapper."""

    # Base endpoint for Google Generative API (using v1 stable API)
    BASE_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # Get Gemini API key from environment or parameter
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        # Get model from parameter, environment, or default
        # Use current Gemini model names: gemini-1.5-flash or gemini-pro
        self.model = model or os.getenv('GEMINI_MODEL') or "gemini-1.5-flash"
        # Get parameters from config (Gemini-specific, low temperature for factual accuracy)
        self.max_tokens = GEMINI_MAX_TOKENS
        self.temperature = GEMINI_TEMPERATURE

        if not self.api_key:
            raise ValueError("GEMINI API key not provided (set GEMINI_API_KEY env var)")

        logger.info(f"Gemini client initialized: model={self.model}, temperature={self.temperature} (facts-only)")

    def generate_response(self, query: str, search_results: List[Any], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        try:
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

            endpoint = f"{self.BASE_ENDPOINT}/{self.model}:generateContent"
            params = { 'key': self.api_key }

            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\n{user_message}"
                    }]
                }],
                "generationConfig": {
                    "temperature": float(self.temperature),
                    "maxOutputTokens": int(self.max_tokens),
                }
            }

            logger.debug(f"Calling Gemini endpoint: {endpoint}")
            resp = requests.post(endpoint, params=params, json=payload, timeout=60)
            if resp.status_code != 200:
                logger.error(f"Gemini API error: {resp.status_code} - {resp.text}")
                return {'response': '', 'sources': valid_sources, 'confidence': 0.0}

            data = resp.json()
            # Parse response from new Gemini API format
            answer = ""
            if 'candidates' in data and data['candidates']:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    if candidate['content']['parts']:
                        answer = candidate['content']['parts'][0].get('text', '')
            
            if not answer:
                logger.warning(f"Empty response from Gemini: {data}")
                return {'response': '', 'sources': valid_sources, 'confidence': 0.0}

            return {
                'response': answer,
                'sources': valid_sources,
                'confidence': float(sum(s['score'] for s in valid_sources) / len(valid_sources)) if valid_sources else 0.0,
                'model': self.model,
            }

        except Exception as e:
            logger.error(f"Gemini client error: {e}")
            return {'response': f'LLM error: {e}', 'sources': [], 'confidence': 0.0}
