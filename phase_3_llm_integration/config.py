"""
Phase 3 Configuration - LLM Integration with Gemini + Chroma Cloud
"""

import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
import sys

# Load .env file from this directory
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    load_dotenv(_env_path)
elif os.path.exists(os.path.join(os.path.dirname(__file__), '..', '.env')):
    # Try parent directory too
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ============================================================================
# CHROMA CLOUD Configuration
# ============================================================================

CHROMA_HOST = os.getenv("CHROMA_HOST", "api.trychroma.com")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")  # From Chroma Cloud dashboard
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "294acee2-3774-495c-939a-15b101ff9a19")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "Demo")

# Collection names (by data shard - e.g., by AMC)
CHROMA_COLLECTION_NAME_TEMPLATE = "groww_faq_{amc_name_lower}"
CHROMA_COLLECTION_METADATA = {
    "dense_embedding_model": "chroma-cloud-qwen",  # Chroma Cloud Qwen
    "sparse_embedding_model": "chroma-cloud-splade",  # Chroma Cloud Splade
    "hybrid_search": True,
    "description": "Groww FAQ hybrid search collection"
}

# ============================================================================
# EMBEDDING Configuration (Chroma Cloud)
# ============================================================================

# Dense embeddings: Chroma Cloud Qwen (384D)
DENSE_EMBEDDING_MODEL = "chroma-cloud-qwen"
DENSE_EMBEDDING_DIMENSION = 384

# Sparse embeddings: Chroma Cloud Splade
SPARSE_EMBEDDING_MODEL = "chroma-cloud-splade"

# ============================================================================
# LLM Configuration (Ollama - Local)
# ============================================================================

LLM_PROVIDER = "ollama"  # Using Ollama (local LLM)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")  # Ollama model name
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))  # Reused for token limit
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))  # Low temp for factual accuracy

# ============================================================================
# CORPUS Configuration (15 Groww AMC URLs for daily scraping)
# ============================================================================

GROWW_BASE_URL = "https://groww.in/mutual-funds/amc"

# 15 Groww AMC URLs for corpus (per RAG_ARCHITECTURE.md)
CORPUS_URLS: List[str] = [
    f"{GROWW_BASE_URL}/hdfc-mutual-funds",
    f"{GROWW_BASE_URL}/icici-mutual-funds",
    f"{GROWW_BASE_URL}/sbi-mutual-funds",
    f"{GROWW_BASE_URL}/axis-mutual-funds",
    f"{GROWW_BASE_URL}/kotak-mutual-funds",
    f"{GROWW_BASE_URL}/aditya-birla-sun-life-mutual-funds",
    f"{GROWW_BASE_URL}/dsp-mutual-funds",
    f"{GROWW_BASE_URL}/idfc-mutual-funds",
    f"{GROWW_BASE_URL}/nippon-india-mutual-funds",
    f"{GROWW_BASE_URL}/hdfc-bank-mutual-funds",
    f"{GROWW_BASE_URL}/induslind-mutual-funds",
    f"{GROWW_BASE_URL}/mahindra-mutual-funds",
    f"{GROWW_BASE_URL}/mirae-asset-mutual-funds",
    f"{GROWW_BASE_URL}/motilal-oswal-mutual-funds",
    f"{GROWW_BASE_URL}/trust-mutual-funds",
]

# Corpus metadata schema
CORPUS_METADATA_SCHEMA = {
    "chunk_id": "string",           # Unique chunk identifier
    "amc_name": "string",           # AMC name (HDFC, ICICI, etc.)
    "scheme_name": "string",        # Scheme name (Large-Cap, ELSS, etc.)
    "source_url": "string",         # Source URL from CORPUS_URLS
    "content_hash": "string",       # SHA-256 hash for change detection
    "scraped_datetime": "string",   # ISO 8601 timestamp
    "retry_count": "integer",       # Number of retries to fetch
    "concepts": "array",            # Extracted concepts (keywords)
    "chunk_index": "integer",       # Sequence index within document
}

# ============================================================================
# HYBRID SEARCH Configuration
# ============================================================================

# Reciprocal Rank Fusion (RRF) weights
RRF_K_PARAMETER = int(os.getenv("RRF_K_PARAMETER", "60"))  # RRF constant
DENSE_WEIGHT = float(os.getenv("DENSE_WEIGHT", "0.6"))  # 60% dense results
SPARSE_WEIGHT = float(os.getenv("SPARSE_WEIGHT", "0.4"))  # 40% sparse results

# Result retrieval
TOP_K_DENSE = int(os.getenv("TOP_K_DENSE", "20"))  # Dense search top-K
TOP_K_SPARSE = int(os.getenv("TOP_K_SPARSE", "20"))  # Sparse search top-K
TOP_K_FINAL = int(os.getenv("TOP_K_FINAL", "5"))  # Final combined results

# ============================================================================
# GROUPBY Configuration (Deduplication)
# ============================================================================

# GroupBy fields for deduplication across chunks from same document
GROUPBY_FIELD = "source_url"  # Group by source URL to deduplicate
GROUPBY_LIMIT = int(os.getenv("GROUPBY_LIMIT", "3"))  # Max chunks per source

# ============================================================================
# CHUNKING Configuration
# ============================================================================

CHUNK_MAX_SIZE_KB = 16  # Chroma Cloud 16 KiB limit per document
CHUNK_SIZE_TOKENS = int(os.getenv("CHUNK_SIZE_TOKENS", "300"))
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "50"))

# ============================================================================
# QUERY Configuration
# ============================================================================

# Minimum similarity threshold for results
MIN_SIMILARITY_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", "0.85"))

# Query parameters
QUERY_TIMEOUT_SECONDS = int(os.getenv("QUERY_TIMEOUT_SECONDS", "30"))

# ============================================================================
# LLM PROMPT Templates (Fact-Based, No Advice)
# ============================================================================

SYSTEM_PROMPT = """You are a facts-only FAQ assistant for Groww mutual fund schemes.
STRICT RULES:
1. Answer ONLY factual questions (expense ratio, exit load, minimum SIP, ELSS lock-in, riskometer, benchmark, statements).
2. Refuse portfolio/investment advice ("Should I buy...?", "Is this safe...?", "Will I earn...?").
3. Include EXACTLY ONE source URL from the provided context.
4. Answers must be <= 3 sentences.
5. Never accept or store PII (PAN, Aadhaar, account number, phone, email, OTP).
6. Include "Last updated from sources: YYYY-MM-DD" timestamp.
7. Only cite official Groww, SEBI, AMFI, RBI sources.

Respond in English or Hindi (matching query language).
"""

QUERY_TEMPLATE = """Context from Groww FAQ (Official Public Sources):
{context}

User Question: {query}

RESPONSE RULES:
- If factual: Answer (≤3 sentences) + Source: [URL] + Last updated: [date]
- If advice/opinion: "I provide only factual information, not investment advice. Learn more: [link]"
- If PII detected: "I cannot store or process personal information. Contact support: groww.in/help"
- If not in sources: "I couldn't find reliable information about this in official sources."

Respond now:
"""

# ============================================================================
# CACHING Configuration (Optional)
# ============================================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
USE_RESULT_CACHE = os.getenv("USE_RESULT_CACHE", "true").lower() == "true"

# ============================================================================
# LOGGING Configuration
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/phase_3.log")

# ============================================================================
# Data Import Configuration
# ============================================================================

IMPORT_BATCH_SIZE = int(os.getenv("IMPORT_BATCH_SIZE", "100"))
PRESERVE_METADATA = os.getenv("PRESERVE_METADATA", "true").lower() == "true"

# ============================================================================
# VALIDATION Functions
# ============================================================================

def validate_config() -> bool:
    """Validate that all required configuration is present."""
    errors = []
    
    provider = (LLM_PROVIDER or "").lower()
    
    # Chroma Cloud checks
    if not CHROMA_API_KEY:
        errors.append("[ERROR] CHROMA_API_KEY not set (required for Chroma Cloud)")
    
    if not CHROMA_TENANT:
        errors.append("[ERROR] CHROMA_TENANT not set (required for Chroma Cloud)")
    
    # LLM provider check
    if provider != "ollama":
        errors.append(f"[ERROR] LLM_PROVIDER must be 'ollama', got '{provider}'")
    
    # Hybrid search checks
    if abs(DENSE_WEIGHT + SPARSE_WEIGHT - 1.0) > 0.01:
        errors.append(f"[ERROR] DENSE_WEIGHT + SPARSE_WEIGHT must = 1.0, got {DENSE_WEIGHT + SPARSE_WEIGHT}")
    
    if TOP_K_DENSE <= 0 or TOP_K_SPARSE <= 0 or TOP_K_FINAL <= 0:
        errors.append("[ERROR] TOP_K parameters must be > 0")
    
    # Corpus URL check
    if not CORPUS_URLS or len(CORPUS_URLS) < 15:
        errors.append(f"[ERROR] CORPUS_URLS must have 15 URLs, got {len(CORPUS_URLS) if CORPUS_URLS else 0}")
    
    if errors:
        print("\n".join(errors))
        return False

    print("[OK] Configuration validated successfully")
    return True


def print_config_summary():
    """Print configuration summary (Ollama + Chroma Cloud)."""
    print("""
┌─ Phase 3 Configuration Summary (Ollama + Chroma Cloud) ─────┐
│ Chroma Cloud Setup:                                         │
│   • Host: {}
│   • Tenant: {}...
│   • Database: {}                                    │
│   • Collections: Sharded by AMC                             │
│                                                             │
│ Embedding Models (Chroma Cloud):                            │
│   • Dense: {} (384D)                     │
│   • Sparse: {}                         │
│   • Hybrid Search: Enabled (RRF)                            │
│                                                             │
│ LLM (Ollama - Local):                                       │
│   • Model: {}                                      │
│   • Max Tokens: {}                                    │
│   • Temperature: {} (low = factual)                  │
│                                                             │
│ Search Weights (RRF):                                       │
│   • Dense Contribution: {}%                              │
│   • Sparse Contribution: {}%                              │
│   • Top-K Final Results: {}                               │
│   • GroupBy Deduplication: {} chunks/source         │
│                                                             │
│ Chunking (Chroma Cloud Limit):                              │
│   • Max Size: {} KiB                                    │
│   • Chunk Tokens: {}                                   │
│   • Overlap: {} tokens                                │
│                                                             │
│ Corpus (15 Groww AMC URLs):                                 │
│   • URLs Configured: {}                                     │
│   • Refresh Schedule: Daily 9 AM IST (GitHub Actions)      │
│   • Public Sources: Groww, SEBI, AMFI, RBI                 │
└─────────────────────────────────────────────────────────────┘
    """.format(
        CHROMA_HOST,
        CHROMA_TENANT[:8],
        CHROMA_DATABASE,
        DENSE_EMBEDDING_MODEL,
        SPARSE_EMBEDDING_MODEL,
        OLLAMA_MODEL,
        GEMINI_MAX_TOKENS,
        GEMINI_TEMPERATURE,
        int(DENSE_WEIGHT * 100),
        int(SPARSE_WEIGHT * 100),
        TOP_K_FINAL,
        GROUPBY_LIMIT,
        CHUNK_MAX_SIZE_KB,
        CHUNK_SIZE_TOKENS,
        CHUNK_OVERLAP_TOKENS,
        len(CORPUS_URLS),
    ))


if __name__ == "__main__":
    print_config_summary()
    validate_config()
