"""
Phase 4: Multi-Language Translation Service
Handles Hindi & English translations for all query responses
"""

import logging
import hashlib
import json
import os
from typing import Dict, List, Optional, Tuple
from enum import Enum
from functools import lru_cache
import time

try:
    from google.cloud import translate_v2 as translate
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    HINDI = "hi"


class TranslationCache:
    """In-memory cache for translations with TTL"""
    
    def __init__(self, ttl_seconds: int = 86400 * 30):
        self.ttl = ttl_seconds
        self.cache: Dict[str, Tuple[str, float]] = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get cached translation"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: str):
        """Store translation in cache"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
    
    def generate_key(self, text: str, target_language: str) -> str:
        """Generate cache key from text and language"""
        combined = f"{text}:{target_language}"
        return hashlib.md5(combined.encode()).hexdigest()


class MultiLanguageTranslator:
    """Translates queries, responses, and metadata to Hindi/English"""
    
    def __init__(self, use_cache: bool = True, cache_ttl: int = 86400 * 30):
        """
        Initialize translator
        
        Args:
            use_cache: Whether to cache translations
            cache_ttl: Cache TTL in seconds
        """
        self.cache = TranslationCache(ttl_seconds=cache_ttl) if use_cache else None
        self.use_cache = use_cache
        self.google_client = None
        self.fallback_translations = self._load_fallback_dictionary()
        
        # Initialize Google Translate client if available
        if GOOGLE_TRANSLATE_AVAILABLE:
            try:
                self.google_client = translate.Client()
                logger.info("✓ Google Translate API initialized")
            except Exception as e:
                logger.warning(f"Google Translate initialization failed: {e}. Using fallback.")
                self.google_client = None
    
    def _load_fallback_dictionary(self) -> Dict[str, str]:
        """Load domain-specific Hindi translations (fallback)"""
        return {
            # Common financial terms
            "expense ratio": "व्यय अनुपात",
            "mutual fund": "म्यूचुअल फंड",
            "exit load": "निकास भार",
            "lock-in period": "लॉक-इन अवधि",
            "scheme": "योजना",
            "ISIN": "ISIN",
            "NAV": "NAV (शुद्ध संपत्ति मूल्य)",
            "AUM": "AUM (प्रबंधित संपत्ति)",
            "ELSS": "ELSS (इक्विटी लिंक्ड सेविंग्स स्कीम)",
            "SIP": "SIP (व्यवस्थित निवेश योजना)",
            "benchmark": "बेंचमार्क",
            "riskometer": "जोखिम मीटर",
            "equity": "इक्विटी",
            "debt": "ऋण",
            "hybrid": "हाइब्रिड",
            "minimum SIP": "न्यूनतम SIP",
            "risk level": "जोखिम स्तर",
            "performance": "कार्यक्षमता",
            "holdings": "होल्डिंग्स",
            "sector": "क्षेत्र",
            "dividend": "लाभांश",
            "return": "रिटर्न",
            "low": "कम",
            "medium": "मध्यम",
            "high": "अधिक",
            "source": "स्रोत",
            "I can only provide factual information": "मैं केवल तथ्यात्मक जानकारी प्रदान कर सकता हूँ",
            "investment advice": "निवेश सलाह",
            "Learn more at": "यहाँ अधिक जानें",
            "Last updated": "अंतिम अपडेट",
        }
    
    def translate_text(
        self, 
        text: str, 
        target_language: Language = Language.HINDI
    ) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language (default: Hindi)
        
        Returns:
            Translated text
        """
        if target_language == Language.ENGLISH:
            return text  # Already in English
        
        # Generate cache key
        if self.use_cache and self.cache:
            cache_key = self.cache.generate_key(text, target_language.value)
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for translation: {text[:50]}...")
                return cached
        
        # Try Google Translate
        if self.google_client:
            try:
                result = self.google_client.translate_text(
                    text,
                    target_language=target_language.value
                )
                translated = result['translatedText']
                
                # Cache the result
                if self.use_cache and self.cache:
                    self.cache.set(cache_key, translated)
                
                return translated
            except Exception as e:
                logger.warning(f"Google Translate failed: {e}. Using fallback.")
        
        # Fallback: Use dictionary + simple rules
        return self._fallback_translate(text, target_language)
    
    def _fallback_translate(
        self, 
        text: str, 
        target_language: Language
    ) -> str:
        """
        Fallback translation using dictionary
        
        Args:
            text: Text to translate
            target_language: Target language
        
        Returns:
            Best-effort translation
        """
        if target_language == Language.ENGLISH:
            return text
        
        result = text
        # Replace known terms (case-insensitive)
        for english, hindi in self.fallback_translations.items():
            result = result.replace(english, hindi)
            result = result.replace(english.capitalize(), hindi)
            result = result.replace(english.upper(), hindi)
        
        logger.debug(f"Fallback translation applied: {text[:50]}...")
        return result
    
    def translate_response(
        self,
        response: Dict,
        target_language: Language = Language.ENGLISH
    ) -> Dict:
        """
        Translate entire response object
        
        Args:
            response: Response dict with 'answer' and other fields
            target_language: Target language
        
        Returns:
            Response with translated fields
        """
        if target_language == Language.ENGLISH:
            return response  # No translation needed
        
        translated_response = response.copy()
        
        # Translate main answer
        if 'answer' in translated_response:
            translated_response['answer'] = self.translate_text(
                translated_response['answer'],
                target_language
            )
        
        # Translate sources (keep URLs as-is, translate text)
        if 'sources' in translated_response:
            for source in translated_response['sources']:
                if 'text' in source:
                    source['text'] = self.translate_text(
                        source['text'],
                        target_language
                    )
        
        # Add language field
        translated_response['language'] = target_language.value
        
        return translated_response
    
    def translate_chunk_metadata(
        self,
        chunk: Dict,
        target_language: Language = Language.ENGLISH
    ) -> Dict:
        """
        Translate chunk text for multi-language indexing
        
        Args:
            chunk: Chunk dict with 'text' field
            target_language: Target language
        
        Returns:
            Chunk with additional translated field
        """
        if target_language == Language.ENGLISH:
            return chunk
        
        translated_chunk = chunk.copy()
        
        # Store translation in separate field
        field_name = f"text_{target_language.value}"
        translated_chunk[field_name] = self.translate_text(
            chunk.get('text', ''),
            target_language
        )
        
        return translated_chunk


class LanguageDetector:
    """Detects user's query language"""
    
    def __init__(self):
        """Initialize language detector"""
        self.hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह़ंः़ँ')
        self.english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    def detect_language(self, query: str) -> Language:
        """
        Detect language of input query
        
        Args:
            query: User query string
        
        Returns:
            Detected language (English or Hindi)
        """
        hindi_count = sum(1 for char in query if char in self.hindi_chars)
        english_count = sum(1 for char in query if char in self.english_chars)
        
        if hindi_count > english_count:
            return Language.HINDI
        else:
            return Language.ENGLISH


def create_translator(use_cache: bool = True) -> MultiLanguageTranslator:
    """Factory function to create translator instance"""
    return MultiLanguageTranslator(use_cache=use_cache)


# Example usage
if __name__ == "__main__":
    translator = create_translator()
    
    # Test translation
    test_text = "The expense ratio of ELSS Fund is 0.50% per annum"
    translated = translator.translate_text(test_text, Language.HINDI)
    print(f"Original: {test_text}")
    print(f"Translated: {translated}")
    
    # Test response translation
    test_response = {
        "answer": "The minimum SIP is ₹500",
        "source_url": "https://groww.in/...",
        "confidence": 0.95
    }
    translated_response = translator.translate_response(test_response, Language.HINDI)
    print(f"\nResponse: {json.dumps(translated_response, ensure_ascii=False, indent=2)}")
