"""
Fetch URLs Module - Scrape 15 Groww AMC pages
"""

import logging
import requests
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

# 15 Groww AMC URLs (per RAG_ARCHITECTURE.md)
CORPUS_URLS = [
    "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
    "https://groww.in/mutual-funds/amc/icici-mutual-funds",
    "https://groww.in/mutual-funds/amc/sbi-mutual-funds",
    "https://groww.in/mutual-funds/amc/axis-mutual-funds",
    "https://groww.in/mutual-funds/amc/kotak-mutual-funds",
    "https://groww.in/mutual-funds/amc/aditya-birla-sun-life-mutual-funds",
    "https://groww.in/mutual-funds/amc/dsp-mutual-funds",
    "https://groww.in/mutual-funds/amc/idfc-mutual-funds",
    "https://groww.in/mutual-funds/amc/nippon-india-mutual-funds",
    "https://groww.in/mutual-funds/amc/hdfc-bank-mutual-funds",
    "https://groww.in/mutual-funds/amc/induslind-mutual-funds",
    "https://groww.in/mutual-funds/amc/mahindra-mutual-funds",
    "https://groww.in/mutual-funds/amc/mirae-asset-mutual-funds",
    "https://groww.in/mutual-funds/amc/motilal-oswal-mutual-funds",
    "https://groww.in/mutual-funds/amc/trust-mutual-funds",
]

# Browser-like headers to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

def fetch_url(url: str, timeout: int = 30, retries: int = 3) -> Optional[str]:
    """
    Fetch content from a single URL with retry logic.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        retries: Number of retries on failure
        
    Returns:
        HTML content or None on failure
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            logger.info(f"✅ Fetched {url} (attempt {attempt + 1})")
            return response.text
        except requests.RequestException as e:
            logger.warning(f"⚠️  Fetch failed for {url} (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching {url}: {e}")
            return None
    
    logger.error(f"❌ Failed to fetch {url} after {retries} retries")
    return None


def fetch_all_urls(urls: Optional[List[str]] = None) -> Dict[str, Optional[str]]:
    """
    Fetch content from all 15 Groww AMC URLs.
    
    Args:
        urls: Optional custom URL list (defaults to CORPUS_URLS)
        
    Returns:
        Dict mapping URL -> HTML content (or None if failed)
    """
    if urls is None:
        urls = CORPUS_URLS
    
    logger.info(f"📥 Starting fetch of {len(urls)} URLs...")
    
    results = {}
    success_count = 0
    
    for url in urls:
        content = fetch_url(url)
        results[url] = content
        if content:
            success_count += 1
        # Rate limit: 1 request per second
        time.sleep(1)
    
    logger.info(f"✅ Fetch complete: {success_count}/{len(urls)} URLs succeeded")
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = fetch_all_urls()
    
    for url, content in results.items():
        status = "✅" if content else "❌"
        size = len(content) if content else 0
        print(f"{status} {url}: {size} bytes")
