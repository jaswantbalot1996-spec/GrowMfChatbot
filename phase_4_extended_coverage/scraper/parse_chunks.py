"""
Parse and Chunk Module - Extract semantic chunks from HTML content
"""

import logging
import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

logger = logging.getLogger(__name__)

def extract_amc_name(url: str) -> str:
    """Extract AMC name from URL."""
    # URL format: https://groww.in/mutual-funds/amc/{amc-name}
    parts = url.rstrip('/').split('/')
    amc_slug = parts[-1] if parts else "unknown"
    return amc_slug.replace('-mutual-funds', '').replace('-', '_').upper()


def clean_text(text: str) -> str:
    """Clean and normalize HTML text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove non-ASCII characters (if needed)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text


def parse_html(html: str, url: str) -> Dict[str, Any]:
    """
    Parse HTML content and extract structured data.
    
    Args:
        html: Raw HTML content
        url: Source URL
        
    Returns:
        Parsed content dict with title, body text, metadata
    """
    try:
        if not BeautifulSoup:
            logger.warning("BeautifulSoup not available, using regex fallback")
            return parse_html_fallback(html, url)
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('h1')
        if title_tag:
            title = clean_text(title_tag.get_text())
        
        # Extract main body text
        text_parts = []
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract paragraphs and lists
        for element in soup.find_all(['p', 'li', 'h2', 'h3', 'span']):
            text = clean_text(element.get_text())
            if text and len(text) > 10:  # Skip very short text
                text_parts.append(text)
        
        body_text = ' '.join(text_parts)
        
        # Calculate content hash for change detection
        content_hash = hashlib.sha256(body_text.encode()).hexdigest()
        
        return {
            'title': title,
            'body': body_text,
            'content_hash': content_hash,
            'source_url': url,
            'amc_name': extract_amc_name(url),
            'scraped_datetime': datetime.utcnow().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to parse HTML from {url}: {e}")
        return parse_html_fallback(html, url)


def parse_html_fallback(html: str, url: str) -> Dict[str, Any]:
    """Fallback parser using regex when BeautifulSoup unavailable."""
    # Extract text between tags
    text = re.sub(r'<[^>]+>', ' ', html)
    text = clean_text(text)
    
    # Calculate hash
    content_hash = hashlib.sha256(text.encode()).hexdigest()
    
    return {
        'title': "Groww AMC Page",
        'body': text[:5000],  # Limit to first 5000 chars
        'content_hash': content_hash,
        'source_url': url,
        'amc_name': extract_amc_name(url),
        'scraped_datetime': datetime.utcnow().isoformat(),
    }


def chunk_text(text: str, chunk_size_tokens: int = 300, overlap_tokens: int = 50) -> List[str]:
    """
    Split text into overlapping chunks (token-based).
    
    Args:
        text: Text to chunk
        chunk_size_tokens: Target tokens per chunk
        overlap_tokens: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Simple token approximation: ~4 chars per token  
    chars_per_token = 4
    chunk_size_chars = chunk_size_tokens * chars_per_token
    overlap_chars = overlap_tokens * chars_per_token
    
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size_chars:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Create overlap
            overlap_start = max(0, len(current_chunk) - overlap_chars)
            current_chunk = current_chunk[overlap_start:] + " " + sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return [c for c in chunks if len(c) > 50]  # Filter out very short chunks


def parse_and_chunk_content(
    html_data: Dict[str, Optional[str]],
    chunk_size_tokens: int = 300,
    overlap_tokens: int = 50
) -> List[Dict[str, Any]]:
    """
    Parse HTML and create chunks from all URLs.
    
    Args:
        html_data: Dict mapping URL -> HTML content
        chunk_size_tokens: Tokens per chunk
        overlap_tokens: Overlap between chunks
        
    Returns:
        List of chunk dicts with metadata
    """
    logger.info(f"📄 Parsing and chunking {len(html_data)} documents...")
    
    chunks = []
    chunk_id_counter = {}
    
    for url, html in html_data.items():
        if not html:
            logger.warning(f"⚠️  Skipping empty HTML from {url}")
            continue
        
        # Parse HTML
        parsed = parse_html(html, url)
        amc_name = parsed['amc_name']
        
        # Chunk the body text
        text_chunks = chunk_text(parsed['body'], chunk_size_tokens, overlap_tokens)
        
        # Initialize counter for this AMC
        if amc_name not in chunk_id_counter:
            chunk_id_counter[amc_name] = 0
        
        for idx, chunk_text_content in enumerate(text_chunks):
            chunk_id_counter[amc_name] += 1
            
            chunk_dict = {
                'chunk_id': f"{amc_name.lower()}_{chunk_id_counter[amc_name]:03d}",
                'amc_name': amc_name,
                'scheme_name': "",  # Extract from chunk text if possible
                'source_url': url,
                'content': chunk_text_content,
                'content_hash': parsed['content_hash'],
                'scraped_datetime': parsed['scraped_datetime'],
                'chunk_index': idx,
                'concepts': [],  # Will be filled by NLP later if needed
                'retry_count': 0,
            }
            chunks.append(chunk_dict)
    
    logger.info(f"✅ Created {len(chunks)} chunks from {sum(1 for h in html_data.values() if h)} documents")
    
    return chunks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test  with sample HTML
    sample_html = "<html><body><h1>Test</h1><p>This is test content about expense ratios.</p></body></html>"
    parsed = parse_html(sample_html, "https://example.com")
    print(f"Parsed: {parsed}")
    
    chunks = chunk_text(parsed['body'], chunk_size_tokens=50)
    print(f"Chunks: {chunks}")
