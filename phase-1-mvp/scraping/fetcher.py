# HTTP Fetcher with Retry Logic

import asyncio
import hashlib
import logging
from typing import Tuple
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import HTTP_CONFIG

logger = logging.getLogger(__name__)


class ScrapeClient:
    """HTTP client for fetching URLs with retry logic and rate limiting"""
    
    def __init__(self):
        self.timeout = HTTP_CONFIG["timeout_per_url"]
        self.max_retries = HTTP_CONFIG["max_retries"]
        self.retry_backoff = HTTP_CONFIG["retry_backoff"]
        self.concurrent_requests = HTTP_CONFIG["concurrent_requests"]
        self.semaphore = asyncio.Semaphore(self.concurrent_requests)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
            backoff_factor=1,  # Will be overridden with custom backoff
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            "User-Agent": HTTP_CONFIG["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        
        return session
    
    async def fetch_url(self, url: str) -> Tuple[str, int]:
        """
        Fetch URL with retry logic and exponential backoff
        
        Returns:
            Tuple[str, int]: (response_text, status_code)
        """
        async with self.semaphore:
            return await self._fetch_with_retry(url)
    
    async def _fetch_with_retry(self, url: str) -> Tuple[str, int]:
        """Fetch with exponential backoff retries"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Check Last-Modified header first
                try:
                    head_response = self.session.head(url, timeout=10)
                    if head_response.status_code != 200:
                        return "", head_response.status_code
                except Exception as e:
                    logger.debug(f"HEAD request failed for {url}: {str(e)}")
                
                # Fetch full content
                response = self.session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.text, response.status_code
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
                    # Retry on 5xx errors
                    if 500 <= response.status_code < 600:
                        if attempt < self.max_retries:
                            backoff_time = self.retry_backoff[attempt]
                            logger.info(f"Retrying {url} after {backoff_time}s (attempt {attempt + 1}/{self.max_retries})")
                            await asyncio.sleep(backoff_time)
                            continue
                    
                    return "", response.status_code
            
            except requests.Timeout:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                last_exception = f"Timeout after {self.timeout}s"
                
                if attempt < self.max_retries:
                    backoff_time = self.retry_backoff[attempt]
                    logger.info(f"Retrying {url} after {backoff_time}s")
                    await asyncio.sleep(backoff_time)
            
            except requests.ConnectionError as e:
                logger.warning(f"Connection error for {url}: {str(e)}")
                last_exception = f"Connection error: {str(e)}"
                
                if attempt < self.max_retries:
                    backoff_time = self.retry_backoff[attempt]
                    logger.info(f"Retrying {url} after {backoff_time}s")
                    await asyncio.sleep(backoff_time)
            
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {str(e)}")
                last_exception = str(e)
                return "", 0
        
        # All retries exhausted
        logger.error(f"Failed to fetch {url} after {self.max_retries} retries: {last_exception}")
        return "", 0
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for change detection"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def close(self):
        """Close session"""
        self.session.close()
