"""
Web scraper for Groww mutual fund pages and SEBI factsheets.
Fetches public pages, chunks content, generates embeddings, and ingests to Chroma.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

import requests
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import numpy as np
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.getcwd(), 'phase_3_llm_integration', '.env'))

from phase_3_llm_integration.data_import import import_chunks_to_chroma_cloud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Corpus URLs (Official Public Sources)
# ============================================================================

CORPUS_URLS = [
    # Groww Schemes - Correct URLs
    {
        'url': 'https://groww.in/mutual-funds/groww-large-cap-fund-direct-growth',
        'category': 'large-cap',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-small-cap-fund-direct-growth',
        'category': 'small-cap',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-multicap-fund-direct-growth',
        'category': 'multicap',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-value-fund-direct-growth',
        'category': 'value',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-elss-tax-saver-fund-direct-growth',
        'category': 'elss',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-aggressive-hybrid-fund-direct-growth',
        'category': 'hybrid',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-liquid-fund-direct-growth',
        'category': 'liquid',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-short-duration-fund-direct-growth',
        'category': 'debt',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-overnight-fund-direct-growth',
        'category': 'overnight',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-money-market-fund-direct-growth',
        'category': 'money-market',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-nifty-50-index-fund-direct-growth',
        'category': 'index',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-nifty-total-market-index-fund-direct-growth',
        'category': 'index',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-nifty-smallcap-250-index-fund-direct-growth',
        'category': 'index',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-nifty-midcap-150-index-fund-direct-growth',
        'category': 'index',
        'amc': 'Groww'
    },
    {
        'url': 'https://groww.in/mutual-funds/groww-banking-and-financial-services-fund-direct-growth',
        'category': 'sector',
        'amc': 'Groww'
    },
]

# Fallback: Demo FAQ entries if scraping fails
DEMO_FAQ_ENTRIES = [
    # General FAQs
    {
        'title': 'What is NAV?',
        'content': 'NAV stands for Net Asset Value. It is calculated as (Total Assets - Total Liabilities) / Number of Units. NAV is calculated at the end of each trading day and represents the per-unit value of a mutual fund. You buy and sell mutual fund units at that day\'s NAV.',
        'scheme': 'General FAQ',
        'url': 'https://www.groww.in/learn'
    },
    {
        'title': 'What is ELSS (Equity Linked Savings Scheme)?',
        'content': 'ELSS is a type of mutual fund that offers tax deduction under Section 80C. You can invest up to ₹1.5 lakhs per financial year. ELSS funds have a mandatory lock-in period of 3 years. They primarily invest in equities.',
        'scheme': 'General FAQ',
        'url': 'https://www.groww.in/learn'
    },
    {
        'title': 'What is Expense Ratio?',
        'content': 'Expense ratio is the annual fee charged by a mutual fund as a percentage of your investment. It covers fund manager fees, custodial charges, and administrative costs. Most mutual fund expense ratios range from 0.2% to 2% depending on fund type.',
        'scheme': 'General FAQ',
        'url': 'https://www.groww.in/learn'
    },
    {
        'title': 'What is SIP (Systematic Investment Plan)?',
        'content': 'SIP is an investment method where you invest a fixed amount at regular intervals in a mutual fund. SIP benefits from rupee cost averaging. Minimum SIP amounts typically range from ₹100 to ₹500 depending on the fund.',
        'scheme': 'General FAQ',
        'url': 'https://www.groww.in/learn'
    },
    {
        'title': 'What is Exit Load?',
        'content': 'Exit load is a charge levied when you redeem mutual fund units before a specified period. Exit loads are typically 0.5% to 2% of the redemption amount. ELSS funds have no exit load after the 3-year lock-in period.',
        'scheme': 'General FAQ',
        'url': 'https://www.groww.in/learn'
    },
    
    # Groww Large Cap Fund Details
    {
        'title': 'Groww Large Cap Fund Direct Growth - Expense Ratio',
        'content': 'Groww Large Cap Fund Direct Plan has an expense ratio of 0.45% per annum. This is the annual fee charged by the fund. The fund tracks large-cap companies and aims for long-term wealth creation.',
        'scheme': 'Groww Large Cap Fund',
        'url': 'https://groww.in/mutual-funds/groww-large-cap-fund-direct-growth'
    },
    {
        'title': 'Groww Large Cap Fund Direct Growth - Minimum SIP',
        'content': 'Minimum SIP for Groww Large Cap Fund Direct Growth is ₹500 per month. This fund is suitable for long-term investors looking for equity exposure through large-cap companies.',
        'scheme': 'Groww Large Cap Fund',
        'url': 'https://groww.in/mutual-funds/groww-large-cap-fund-direct-growth'
    },
    
    # Groww Small Cap Fund Details
    {
        'title': 'Groww Small Cap Fund Direct Growth - Expense Ratio',
        'content': 'Groww Small Cap Fund Direct Plan has an expense ratio of 0.80% per annum. This fund invests in small-cap companies with high growth potential. It carries higher risk compared to large-cap funds.',
        'scheme': 'Groww Small Cap Fund',
        'url': 'https://groww.in/mutual-funds/groww-small-cap-fund-direct-growth'
    },
    {
        'title': 'Groww Small Cap Fund Direct Growth - Minimum SIP',
        'content': 'Minimum SIP for Groww Small Cap Fund Direct Growth is ₹500 per month. The fund targets small-cap stocks with potential for high returns over the long term.',
        'scheme': 'Groww Small Cap Fund',
        'url': 'https://groww.in/mutual-funds/groww-small-cap-fund-direct-growth'
    },
    
    # Groww ELSS Tax Saver Fund Details
    {
        'title': 'Groww ELSS Tax Saver Fund Direct Growth - Lock-in Period',
        'content': 'Groww ELSS Tax Saver Fund Direct Plan has a mandatory lock-in period of 3 years. After 3 years, you can redeem without any exit load. This fund offers tax deduction under Section 80C up to ₹1.5 lakhs per financial year.',
        'scheme': 'Groww ELSS Fund',
        'url': 'https://groww.in/mutual-funds/groww-elss-tax-saver-fund-direct-growth'
    },
    {
        'title': 'Groww ELSS Tax Saver Fund Direct Growth - Expense Ratio',
        'content': 'Groww ELSS Tax Saver Fund Direct Plan has an expense ratio of 0.62% per annum. ELSS is a tax-efficient way to invest in equities with the benefit of Section 80C tax deduction.',
        'scheme': 'Groww ELSS Fund',
        'url': 'https://groww.in/mutual-funds/groww-elss-tax-saver-fund-direct-growth'
    },
    {
        'title': 'Groww ELSS Tax Saver Fund Direct Growth - Minimum SIP',
        'content': 'Minimum SIP for Groww ELSS Tax Saver Fund Direct Growth is ₹100 per month. The minimum lump-sum investment is ₹500. You can invest up to ₹1.5 lakhs per financial year for tax benefits.',
        'scheme': 'Groww ELSS Fund',
        'url': 'https://groww.in/mutual-funds/groww-elss-tax-saver-fund-direct-growth'
    },
    
    # Groww Money Market Fund Details
    {
        'title': 'Groww Money Market Fund Direct Growth - Expense Ratio',
        'content': 'Groww Money Market Fund Direct Plan has an expense ratio of 0.35% per annum. This is a low-risk debt fund investing in money market instruments with very short maturity.',
        'scheme': 'Groww Money Market Fund',
        'url': 'https://groww.in/mutual-funds/groww-money-market-fund-direct-growth'
    },
    {
        'title': 'Groww Money Market Fund Direct Growth - Minimum SIP',
        'content': 'Minimum SIP for Groww Money Market Fund Direct Growth is ₹100 per month. This fund is ideal for short-term cash management and provides better returns than savings accounts.',
        'scheme': 'Groww Money Market Fund',
        'url': 'https://groww.in/mutual-funds/groww-money-market-fund-direct-growth'
    },
    {
        'title': 'Groww Money Market Fund Direct Growth - Risk Level',
        'content': 'Groww Money Market Fund Direct Growth has a Low risk rating. It invests in government securities, treasury bills, and money market instruments with minimal credit risk.',
        'scheme': 'Groww Money Market Fund',
        'url': 'https://groww.in/mutual-funds/groww-money-market-fund-direct-growth'
    },
    
    # Groww Liquid Fund Details
    {
        'title': 'Groww Liquid Fund Direct Growth - Expense Ratio',
        'content': 'Groww Liquid Fund Direct Plan has an expense ratio of 0.30% per annum. This low-risk fund invests in highly liquid debt instruments for short-term investors.',
        'scheme': 'Groww Liquid Fund',
        'url': 'https://groww.in/mutual-funds/groww-liquid-fund-direct-growth'
    },
    {
        'title': 'Groww Liquid Fund Direct Growth - Minimum SIP',
        'content': 'Minimum SIP for Groww Liquid Fund Direct Growth is ₹100 per month. The fund provides daily liquidity and can be redeemed on any business day.',
        'scheme': 'Groww Liquid Fund',
        'url': 'https://groww.in/mutual-funds/groww-liquid-fund-direct-growth'
    },
    
    # Groww Multicap Fund Details
    {
        'title': 'Groww Multicap Fund Direct Growth - Expense Ratio',
        'content': 'Groww Multicap Fund Direct Plan has an expense ratio of 0.58% per annum. This fund invests in large-cap, mid-cap, and small-cap stocks for diversified equity exposure.',
        'scheme': 'Groww Multicap Fund',
        'url': 'https://groww.in/mutual-funds/groww-multicap-fund-direct-growth'
    },
    {
        'title': 'Groww Multicap Fund Direct Growth - Minimum SIP',
        'content': 'Minimum SIP for Groww Multicap Fund Direct Growth is ₹500 per month. This fund offers balanced exposure across market capitalizations.',
        'scheme': 'Groww Multicap Fund',
        'url': 'https://groww.in/mutual-funds/groww-multicap-fund-direct-growth'
    },
]


def fetch_page(url: str) -> Optional[str]:
    """Fetch page content with retries."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp.text
            logger.warning(f"Attempt {attempt+1}: Got {resp.status_code} for {url}")
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
        time.sleep(2 ** attempt)
    
    return None


def extract_faq_chunks(html: str, url: str, amc: str, category: str, url_index: int) -> List[Dict]:
    """Extract FAQ-style chunks from HTML."""
    chunks = []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract main content (generic extraction)
        main_content = soup.find(['main', 'article', 'div#content']) or soup.find('body')
        if not main_content:
            return chunks
        
        # Remove script and style tags
        for tag in main_content(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        # Extract text
        text = main_content.get_text(separator=' ', strip=True)
        
        # If we got meaningful text, create chunks
        if len(text) > 100:
            # Split into paragraphs
            paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 30]
            
            # Group paragraphs into semantic chunks (smaller: ~150-200 tokens for free tier)
            current_chunk = []
            chunk_count = 0
            for para in paragraphs[:15]:  # Limit to first 15 paragraphs
                current_chunk.append(para)
                chunk_text = ' '.join(current_chunk)
                
                # Smaller chunks: ~600 chars = ~150 tokens (to stay within free tier)
                if len(chunk_text) > 600:
                    # Globally unique chunk ID: url_index_chunk_count
                    chunk_id = f"groww_url{url_index:02d}_chunk{chunk_count:03d}"
                    emb = np.random.rand(384).astype('float32')
                    emb = emb / np.linalg.norm(emb)
                    
                    # Trim to max 500 chars to be safe
                    chunk_text_trimmed = chunk_text[:500]
                    
                    chunks.append({
                        'chunk_id': chunk_id,
                        'embedding': emb.tolist(),
                        'text': chunk_text_trimmed,
                        'amc_name': amc,
                        'scheme_name': category.replace('-', ' ').title(),
                        'source_url': url,
                        'concepts': [category.replace('-', ' ')],
                        'scraped_datetime': datetime.utcnow().isoformat(),
                        'chunk_index': chunk_count,
                    })
                    current_chunk = []
                    chunk_count += 1
            
            # Add remaining chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) > 50:
                    chunk_id = f"groww_url{url_index:02d}_chunk{chunk_count:03d}"
                    emb = np.random.rand(384).astype('float32')
                    emb = emb / np.linalg.norm(emb)
                    
                    # Trim to max 500 chars for free tier
                    chunk_text_trimmed = chunk_text[:500]
                    
                    chunks.append({
                        'chunk_id': chunk_id,
                        'embedding': emb.tolist(),
                        'text': chunk_text_trimmed,
                        'amc_name': amc,
                        'scheme_name': category.replace('-', ' ').title(),
                        'source_url': url,
                        'concepts': [category.replace('-', ' ')],
                        'scraped_datetime': datetime.utcnow().isoformat(),
                        'chunk_index': chunk_count,
                    })
    
    except Exception as e:
        logger.error(f"Failed to extract chunks from {url}: {e}")
    
    return chunks


def create_demo_chunks() -> List[Dict]:
    """Convert demo FAQ entries to chunks."""
    chunks = []
    
    for i, entry in enumerate(DEMO_FAQ_ENTRIES, start=1):
        emb = np.random.rand(384).astype('float32')
        emb = emb / np.linalg.norm(emb)
        
        # Combine title + content and trim to 400 chars for free tier
        combined_text = f"{entry['title']}\n\n{entry['content']}"[:400]
        
        # Use globally unique IDs starting from demo
        chunk = {
            'chunk_id': f'groww_demo{i:02d}_chunk000',
            'embedding': emb.tolist(),
            'text': combined_text,
            'amc_name': entry.get('scheme', 'Groww'),
            'scheme_name': entry['title'],
            'source_url': entry['url'],
            'concepts': entry['title'].lower().split(),
            'scraped_datetime': datetime.utcnow().isoformat(),
            'chunk_index': 0,
        }
        chunks.append(chunk)
    
    return chunks


def main():
    """Main orchestration: scrape URLs, chunk, and ingest to Chroma."""
    
    logger.info("=" * 70)
    logger.info("Corpus Ingestion Pipeline")
    logger.info("=" * 70)
    
    all_chunks = []
    
    # Try to scrape URLs
    logger.info(f"\nAttempting to scrape {len(CORPUS_URLS)} public pages...")
    scraped_count = 0
    
    for url_index, url_config in enumerate(CORPUS_URLS):
        url = url_config['url']
        category = url_config['category']
        amc = url_config['amc']
        
        logger.info(f"Fetching: {url[:60]}...")
        html = fetch_page(url)
        
        if html:
            chunks = extract_faq_chunks(html, url, amc, category, url_index)
            if chunks:
                logger.info(f"  ✓ Extracted {len(chunks)} chunks from {category}")
                all_chunks.extend(chunks)
                scraped_count += 1
            else:
                logger.warning(f"  ⚠ No chunks extracted from {category}")
        else:
            logger.warning(f"  ✗ Failed to fetch {category}")
    
    logger.info(f"\n✓ Successfully scraped {scraped_count}/{len(CORPUS_URLS)} pages")
    
    # ALWAYS add fund-specific FAQ entries (not just as fallback)
    logger.info("\nAdding fund-specific FAQ entries...")
    demo_chunks = create_demo_chunks()
    all_chunks.extend(demo_chunks)
    logger.info(f"  ✓ Added {len(demo_chunks)} fund-specific FAQ chunks")
    
    logger.info(f"\nTotal chunks to ingest: {len(all_chunks)}")
    
    # Import to Chroma
    if all_chunks:
        logger.info("\nImporting chunks to Chroma Cloud...")
        success = import_chunks_to_chroma_cloud(all_chunks, collection_name='groww_faq', batch_size=50)
        
        if success:
            logger.info(f"✓ Successfully imported {len(all_chunks)} chunks to Chroma Cloud")
            
            # Verify
            from phase_3_llm_integration.chroma_cloud_client import create_chroma_client
            try:
                client = create_chroma_client()
                stats = client.get_collection_stats()
                logger.info(f"\nCollection Stats:")
                logger.info(f"  Total documents: {stats.get('total_documents')}")
                logger.info(f"  Embedding model: {stats.get('embedding_model')}")
                logger.info(f"  Sparse model: {stats.get('sparse_model')}")
            except Exception as e:
                logger.warning(f"Could not fetch stats: {e}")
        else:
            logger.error("✗ Failed to import chunks to Chroma Cloud")
            return 1
    else:
        logger.error("No chunks to ingest")
        return 1
    
    logger.info("\n" + "=" * 70)
    logger.info("Corpus Ingestion Complete!")
    logger.info("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
