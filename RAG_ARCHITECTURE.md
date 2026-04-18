# RAG Architecture: Groww Mutual Fund FAQ Assistant

## 1. System Overview

### Purpose
Build a Retrieval-Augmented Generation (RAG) system that answers factual questions about mutual fund schemes using only official public sources, with zero investment advice and complete citation transparency.

### Core Principles
- **Facts-Only**: No portfolio advice, risk assessment, or performance comparisons
- **Citation-Mandatory**: Every answer must include exactly one authoritative source link
- **Public-Sources-Only**: AMC factsheets, KIM/SID, SEBI/AMFI official pages
- **No-PII**: Absolute refusal of sensitive data (PAN, Aadhaar, account numbers, OTPs)
- **Clarity**: Answers ≤3 sentences; include last-updated timestamp

---

## 2. Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│              User Interface Layer                    │
│   (Chat UI + 3 Example Questions + Disclaimer)      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│         Query Processing & Validation               │
│   (PII Detection, Query Classification, Routing)    │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│          Retrieval Layer (Vector DB + BM25)         │
│   (Corpus Index, Semantic + Keyword Search)         │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│          Context Assembly & Ranking                 │
│   (Top-K Results, Source Verification, Dedup)       │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│         Generation & Fact-Check Layer               │
│   (LLM Response, Citation Extraction, Validation)   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│         Output Layer (Response + Citation)          │
│   (Timestamp, Source Link, Refusal Handling)        │
└─────────────────────────────────────────────────────┘
```

---

## 3. Data Layer (Corpus Ingestion & Indexing)

### 3.1 Corpus Collection

**URL Scope (15 URLs):**
Only official Groww AMC pages will be scraped. Currently scoped to:
- **Primary Source:** `https://groww.in/mutual-funds/amc/{amc-name}` pages
- **Expansion:** Multi-AMC pages (HDFC, ICICI, SBI, Axis, Kotak, etc.)
- **Total URLs:** 15 official Groww AMC pages (fixed scope for MVP)

**Example URLs:**
```
1. https://groww.in/mutual-funds/amc/hdfc-mutual-funds
2. https://groww.in/mutual-funds/amc/icici-mutual-funds
3. https://groww.in/mutual-funds/amc/sbi-mutual-funds
... (12 more URLs)
```

**Content Extraction per URL:**
Each Groww AMC page contains:
- Scheme listings (name, ISIN, category)
- Factsheets (AUM, expense ratio, benchmark, performance notes)
- KIM/SID documents (downloadable)
- Fee & charges details
- Riskometer classification
- Exit load & lock-in periods
- Minimum SIP information
- Statement download guides

### 3.2 Daily Scheduled Data Pipeline (9 AM Refresh)

**Scheduler Configuration:**
- **Frequency:** Daily at 09:00 AM (IST/UTC configurable)
- **Tool:** GitHub Actions (scheduled workflow)
- **Trigger:** Cron job: `0 9 * * *` (UTC) / `0 3 * * *` (IST)
- **Retry Logic:** 3 retries on failure with exponential backoff (5s, 15s, 45s)
- **Timeout:** 10 minutes per run
- **Workflow File:** `.github/workflows/daily-scrape.yml`

**Daily ETL Pipeline (GitHub Actions):**
```
GitHub Actions Scheduler Trigger (09:00 AM IST / 03:30 AM UTC)
    ↓
[GitHub Actions Workflow: daily-scrape]
    ├─ Checkout repository
    ├─ Set up Python environment
    ├─ Install dependencies
    ├─ Authenticate with cloud services (AWS/Azure)
    └─ Trigger Scraping Service
    ↓
[Scraping Service - Fetch Latest Data]
    ├─ 15 URLs from Groww AMC pages
    ├─ HTTP GET with timeout: 30s per URL
    ├─ Retry on 5xx errors
    ├─ Check last-modified header (skip if unchanged)
    └─ Store raw HTML in staging DB
    ↓
[Document Parser]
    ├─ HTML parsing (beautifulsoup4)
    ├─ Extract structured data:
    │   ├─ Scheme name & ISIN
    │   ├─ Expense ratio
    │   ├─ Exit load & lock-in
    │   ├─ Minimum SIP
    │   ├─ Riskometer
    │   ├─ Benchmark
    │   └─ Download links (factsheet, KIM/SID)
    ├─ Clean text (whitespace normalization, encoding fix)
    └─ Remove boilerplate (headers, footers, ads)
    ↓
[Document Chunking]
    ├─ Semantic chunks (300–500 tokens)
    ├─ Overlap: 50 tokens (for context continuity)
    ├─ Metadata attachment:
    │   ├─ source_url (original Groww AMC page)
    │   ├─ scheme_name
    │   ├─ scheme_isin
    │   ├─ amc_name (extracted)
    │   ├─ document_type ("scheme_page", "factsheet", etc.)
    │   ├─ scraped_datetime (2026-04-16T09:15:32Z)
    │   └─ last_verified_date (today)
    └─ Chunk ID generation: `{amc}_{scheme}_{chunk_seq}`
    ↓
[Embedding Generation]
    ├─ Model: sentence-transformers (all-mpnet-base-v2)
    ├─ Batch embedding (100 chunks/batch)
    ├─ Dimension: 768
    └─ Dimension check (fail if mismatch)
    ↓
[Index Update]
    ├─ Vector DB: Insert/update embeddings + metadata
    ├─ BM25 Index: Rebuild keyword index
    ├─ Metadata DB: Update PostgreSQL with new chunks
    └─ Cache invalidation (clear Redis cache)
    ↓
[Post-Run Validation]
    ├─ Verify chunk count (must be > 0)
    ├─ Verify all URLs indexed
    ├─ Health check: Query vector DB
    ├─ Log summary stats
    └─ Alert if any URL failed
    ↓
Completed (Store run timestamp in DB)
```

**Scraping Service Specifications:**

| Component | Details |
|---|---|
| **Service Type** | Scheduled background job (APScheduler/Celery) |
| **HTTP Client** | `requests` or `httpx` (async-ready) |
| **Timeout** | 30s per URL |
| **Retry Strategy** | Exponential backoff (5s, 15s, 45s) |
| **User-Agent** | Standard browser-like header |
| **Headers Check** | Respect `Last-Modified`, conditionally skip unchanged pages |
| **Concurrency** | Max 3 simultaneous requests (rate limiting) |
| **Storage** | Raw HTML → PostgreSQL staging table |
| **Error Handling** | Log all failures, alert on > 2 failures per run |
| **Data Validation** | Verify content includes expected fields (expense ratio, ISIN, etc.) |

### 3.3 Metadata Schema

```json
{
  "chunk_id": "hdfc_largecp_001",
  "text": "The expense ratio of HDFC Large-Cap Fund is 0.50% p.a. This covers management fees, custody, and other operating costs.",
  "embedding": [0.123, 0.456, ...],
  "source_url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
  "amc_name": "HDFC",
  "scheme_name": "HDFC Large-Cap Fund",
  "scheme_isin": "INF090A01KX0",
  "document_type": "scheme_page",
  "question_types": ["expense_ratio", "charges", "fund_details"],
  "scraped_datetime": "2026-04-16T09:15:32Z",
  "last_verified_date": "2026-04-16",
  "content_hash": "sha256_abc123...",
  "confidence_score": 0.95,
  "url_status": "reachable",
  "retry_count": 0
}
```

**Schema Notes:**
- `source_url`: Always points to the Groww AMC page (15 URLs only)
- `amc_name`: Extracted from URL path (hdfc, icici, sbi, etc.)
- `content_hash`: SHA-256 hash of page content (detect changes)
- `scraped_datetime`: Timestamp of latest scrape (ISO 8601)
- `retry_count`: Track if URL required retries (for quality monitoring)

---

## 4. Retrieval Layer

### 4.1 Dual Retrieval Strategy

**Hybrid Search (Semantic + Keyword):**
1. **Vector Search** (semantic understanding)
   - Query embedding → similarity search against vector DB
   - Top-5 results by cosine similarity
   - Fast (< 100ms)

2. **BM25 Search** (keyword matching)
   - Exact term matching (expense ratio, lock-in, ELSS, etc.)
   - Top-3 results by BM25 score
   - Recall-optimized

3. **Fusion**
   - Deduplicate overlapping results
   - Combine scores (0.7 × vector_score + 0.3 × bm25_score)
   - Final ranking: Top-5 documents

### 4.2 Query Processing

```python
Input Query: "What is the expense ratio of ELSS?"
    ↓
[PII Detection] → No sensitive data detected ✓
    ↓
[Query Classification]
    ├─ Intent: factual_query
    ├─ Category: scheme_property
    ├─ Property: expense_ratio
    ├─ Scheme_filter: ELSS
    └─ Confidence: 0.98
    ↓
[Retrieval Triggers]
    ├─ Vector Search: Query embedding (768D)
    ├─ Keyword Search: Terms ["expense ratio", "ELSS"]
    └─ Filter Context: scheme_name = ELSS
    ↓
[Result Set]
```

### 4.3 Context Window Assembly

```
Retrieved Chunks (ranked, deduped)
    ↓
[Context Ranking & Selection]
    ├─ Score filtering (confidence > 0.6)
    ├─ Recency weighting (recent sources boosted)
    ├─ Source diversity (avoid duplicate sources)
    └─ Window size: max 3000 tokens for LLM context
    ↓
[Context Formatting]
    ├─ Chunk 1 (score: 0.95, source: X)
    ├─ Chunk 2 (score: 0.88, source: Y)
    └─ Chunk 3 (score: 0.82, source: Z)
    ↓
Assembled Context
```

---

## 5. Generation Layer

### 5.1 LLM Integration

**Model Choice:**
- Primary: GPT-4 / Claude 3.5 (fact-heavy, low hallucination)
- Alternative: Open-source (Llama 2 13B or Mistral 7B for cost/latency)
- Fine-tuning: Optional domain prompting for MF terminology

### 5.2 Prompt Template

```
SYSTEM ROLE:
You are a factual FAQ assistant for Groww mutual fund schemes. 
You answer ONLY factual questions about schemes using provided source documents.
Every answer must include exactly one source URL.
Refuse opinion/advice questions with a polite redirect.
Answer in ≤3 sentences.

RULES:
1. Do NOT give investment advice or portfolio recommendations.
2. Do NOT compute returns or compare performance.
3. Do NOT accept PII (PAN, Aadhaar, account numbers, phone, email, OTP).
4. Include timestamp: "Last updated from sources: YYYY-MM-DD"
5. Cite EXACTLY ONE source URL from the provided context.

---

USER QUESTION: {query}

RETRIEVED CONTEXT:
[Document 1] ({source_url_1}): {content_1}
[Document 2] ({source_url_2}): {content_2}
[Document 3] ({source_url_3}): {content_3}

RESPONSE FORMAT:
- If factual: Answer (≤3 sentences) + Source: [URL] + Last updated: [date]
- If opinion/advice: "I can only provide factual information, not investment advice. 
  Learn more: [relevant educational link]"
- If PII detected: "I cannot store or process personal information. 
  For account-specific help, contact support."

Respond now:
```

### 5.3 Generation Process

```
LLM Input (prompt + context)
    ↓
[Token Generation Loop]
    ├─ Max tokens: 150 (enforce brevity)
    ├─ Temperature: 0.1 (deterministic, fact-focused)
    ├─ Top-p: 0.9 (avoid random tokens)
    └─ Stop sequences: ["Q:", "Note:", "Source:"]
    ↓
Raw LLM Output
    ↓
[Post-processing]
    ├─ Extract citation URL (regex: https://...)
    ├─ Verify URL in allowed whitelist
    ├─ Extract timestamp data
    ├─ Remove uncertain phrases ("may", "might", "possibly")
    └─ Enforce ≤3 sentence limit
    ↓
Cleaned Response
```

---

## 6. Validation & Fact-Check Layer

### 6.1 Citation Verification

```
Extracted URL: https://www.groww.in/factsheet/large-cap-fund
    ↓
[Whitelist Check]
    ├─ Allowed domains:
    │   ├─ groww.in/* (Fund house)
    │   ├─ sebi.gov.in/* (Regulator)
    │   ├─ amfi.org.in/* (Industry body)
    │   ├─ rbi.org.in/* (Central bank - if relevant)
    │   └─ specific official partner sites
    └─ Status: ✓ PASS
    ↓
[URL Health Check]
    ├─ HTTP HEAD request (timeout: 5s)
    ├─ Status code: 200 or 301/302
    └─ Status: ✓ REACHABLE
    ↓
[Content Relevance Check]
    ├─ Match extracted fact against chunk text (similarity > 0.85)
    └─ Status: ✓ VERIFIED
    ↓
Final Citation: VALID ✓
```

### 6.2 Guardrails (Input & Output)

**Input Guardrails:**
- PII patterns: PAN (12 alphanumeric), Aadhaar (12 digits), phone (10 digits), email, OTP
- Advice triggers: "should I", "best for me", "predict", "will earn", "safe now?"
- Action triggers: "buy", "sell", "switch", "redeem"

**Output Guardrails:**
- Claim verification: No unattributed statements
- Number validation: Ensure figures match source (within 0.1% tolerance)
- Tone check: Remove advisory language, keep neutral
- Length enforcement: Reject if >3 sentences

---

## 7. Query Routing & Response Types

### 7.1 Query Classification

```
Query Intent Classification:

1. FACTUAL_QUERY (70% expected)
   Example: "What is the expense ratio of Groww ELSS?"
   Route: → Retrieve + Generate + Cite
   
2. OPINION_QUERY (20% expected)
   Example: "Should I invest in ELSS for tax savings?"
   Route: → Refuse + educational link
   Response: "I can only provide factual information. 
   Learn about ELSS: [link]"
   
3. PII_QUERY (5% expected)
   Example: "My PAN is ABCDE1234F. What's my holding?"
   Route: → Refuse + Privacy message
   Response: "I cannot process personal information. 
   Contact support for account queries."
   
4. OUT_OF_SCOPE (5% expected)
   Example: "What's the weather today?"
   Route: → Refuse + redirect
   Response: "I help with Groww mutual fund facts only. 
   Ask me about expense ratios, exit loads, ELSS lock-ins, etc."
```

### 7.2 Response Templates

**Template 1: Factual Answer (Most Common)**
```
{answer_text} 

Source: {source_url}
Last updated from sources: {date}
```

**Template 2: Refusal (Advice Query)**
```
I only provide factual information, not investment advice.

For educational resources on this topic, see: {educational_link}
```

**Template 3: Refusal (PII Detected)**
```
I cannot store or process personal information like PAN, account numbers, or phone numbers.

For account-specific support, contact Groww Help: groww.in/help
```

**Template 4: Not Found**
```
I couldn't find reliable information about this in official Groww or SEBI sources.

Try asking about: expense ratios, exit loads, minimum SIP, ELSS lock-in, riskometer, or how to download statements.
```

---

## 8. UI/UX Layer

### 8.1 Welcome Screen

```
╔═══════════════════════════════════════════╗
║  Groww Mutual Fund FAQ Assistant          ║
║  📚 Facts-Only. No Investment Advice.     ║
╚═══════════════════════════════════════════╝

How can I help? Ask about:

💬 Example Questions:
  1. "What is the expense ratio of ELSS?"
  2. "What is the minimum SIP for each scheme?"
  3. "How do I download my annual statement?"
  4. "What is the lock-in period for ELSS?"
  5. "What is the exit load for large-cap funds?"

ℹ️  Note: I answer from official Groww and SEBI sources only.
   I cannot provide investment advice or portfolio recommendations.

---
Your question:
```

### 8.2 Answer Display

```
Q: What is the expense ratio of the Groww Large-Cap Fund?

A: The Groww Large-Cap Fund charges an expense ratio of 0.50% per annum. 
   This covers management fees, custodial charges, and other operating costs. 
   You can find the latest details in the fund's factsheet.

📎 Source: https://www.groww.in/factsheet/large-cap-fund
🕐 Last updated from sources: 2026-04-16

─────────────────────────────────────────────

Would you like to ask another question?
```

---

## 9. Technology Stack

### 9.1 Core Components

| Component | Technology | Rationale |
|---|---|---|
| **Vector DB** | **Pinecone** (Phase 2) / **ChromaDB** (Phase 3) / Weaviate / Qdrant | Scalable semantic search, metadata filtering |
| **Keyword Index** | Elasticsearch / Whoosh | Fast BM25 retrieval, exact matching |
| **Metadata Store** | PostgreSQL + Redis | ACID compliance, caching, source mapping |
| **Embeddings** | sentence-transformers (all-mpnet-base-v2) | Free, multilingual, 768D, ~10ms per query |
| **LLM** | GPT-4 / Claude 3.5 / Llama 2-13B | Balance accuracy, low hallucination, cost |
| **Document Processing** | LangChain / Unstructured | Unified parsing (HTML, PDF, docx) |
| **Web Crawler** | Scrapy / Selenium | Fetch & refresh corpus from sources |
| **API Framework** | FastAPI / Flask | REST endpoints, real-time retrieval |
| **Frontend** | React / Streamlit | Simple chat UI, quick prototyping |
| **Deployment** | Docker + Kubernetes / AWS / Azure | Scalable, containerized |

### 9.2 Infrastructure with Scheduler & Scraper

```
┌─────────────────────────────────────────────────────┐
│        GitHub Actions Scheduled Workflow (Daily 9 AM IST)  │
│  ┌──────────────────────────────────────────────┐   │
│  │ GitHub Actions Scheduler                     │   │
│  │ Cron: '0 3 * * *' (UTC) / '0 9 * * *' (IST)│   │
│  └──────────────────────────────────────────────┘   │
│                    ↓                                  │
│  ┌──────────────────────────────────────────────┐   │
│  │ GitHub Actions Job: Scraping Service         │   │
│  │ ├─ Runs on: ubuntu-latest                    │   │
│  │ ├─ Concurrency: 3 parallel requests          │   │
│  │ ├─ Python environment: 3.10+                 │   │
│  │ ├─ Fetch 15 Groww AMC URLs                  │   │
│  │ ├─ Retry logic (exponential backoff)        │   │
│  │ ├─ Last-Modified header check               │   │
│  │ └─ Store raw HTML in PostgreSQL (staging)   │   │
│  └──────────────────────────────────────────────┘   │
│                    ↓                                  │
│  ┌──────────────────────────────────────────────┐   │
│  │ GitHub Actions Job: Parse & Chunk           │   │
│  │ ├─ Extract scheme data                       │   │
│  │ ├─ Clean & normalize text                    │   │
│  │ ├─ Create semantic chunks (see CHUNKING.md) │   │
│  │ └─ Ready for embedding                       │   │
│  └──────────────────────────────────────────────┘   │
│                    ↓                                  │
│  ┌──────────────────────────────────────────────┐   │
│  │ GitHub Actions Job: Generate Embeddings     │   │
│  │ ├─ Batch encode chunks (see EMBEDDING.md)   │   │
│  │ └─ Push embeddings to Vector DB              │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ GitHub Actions Job: Index & Validate        │   │
│  │ ├─ Update Vector DB (Pinecone)              │   │
│  │ ├─ Rebuild BM25 index                        │   │
│  │ ├─ Update PostgreSQL metadata                │   │
│  │ ├─ Invalidate Redis cache                    │   │
│  │ ├─ Log run summary & metrics                 │   │
│  │ └─ Report status (success/failure)           │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────┐
│   Chat UI                         │ (React/Streamlit)
└────────┬─────────────────────────┘
         │ REST API
┌────────▼──────────────────────────┐
│   FastAPI Backend                 │
│  ├─ Query Validator               │
│  ├─ Retriever (Hybrid Search)     │
│  ├─ Generator (LLM)               │
│  └─ Citation Verifier             │
└────────┬────────┬────────┬────────┘
         │        │        │
    ┌────▼──┐ ┌──▼───┐ ┌──▼─────┐
    │Vector │ │BM25  │ │Metadata│
    │ DB    │ │Index │ │  DB    │
    │(Pinecone)│(Whoosh)│(PostgreSQL)
    └───────┘ └──────┘ └────────┘
    
    Redis Cache ← Invalidated daily at 9 AM
         │
    ┌────▼─────────────┐
    │ LLM API (OpenAI) │
    └──────────────────┘
```

---

## 10. Daily Scraper Workflow (9 AM Execution)

Detailed flow of the automated daily data refresh:

```
09:00 AM - Scheduler Trigger
    ↓
[Initialize Scraping Service]
    ├─ Load 15 URL list from config
    ├─ Check DB for last scrape timestamp
    └─ Status: STARTED
    ↓
[Fetch Phase - Concurrent (max 3 parallel)]
    ├─ URL 1: HDFC Mutual Funds
    │   ├─ GET → HTTP 200 ✓
    │   ├─ Headers: Last-Modified: 2026-04-15 (changed since last run)
    │   ├─ Response: Content fetched (45KB HTML)
    │   └─ Store in staging_urls table
    │
    ├─ URL 2: ICICI Mutual Funds
    │   ├─ GET → HTTP 200 ✓
    │   ├─ Last-Modified: 2026-04-16 (unchanged)
    │   ├─ Check content_hash: MATCH → Skip processing
    │   └─ Log: [SKIPPED] No changes detected
    │
    ├─ URL 3–15: (Continue parallel fetches)
    │   ├─ Success rate: 14/15 URLs
    │   └─ 1 URL failed (timeout) → Retry queue
    │
    └─ Retry Failed URL (Exponential backoff)
        ├─ Retry #1 (after 5s) → HTTP 200 ✓
        └─ Success
    ↓
[Parse Phase]
    For each successfully fetched URL:
    ├─ Parse HTML → BeautifulSoup
    ├─ Extract key fields:
    │   ├─ Scheme name, ISIN, AMC name
    │   ├─ Expense ratio, exit load, lock-in
    │   ├─ Minimum SIP, riskometer
    │   └─ Benchmark, AUM
    ├─ Validate extracted data (required fields check)
    ├─ Clean text (remove extra whitespace, fix encoding)
    └─ Generate content_hash for change detection
    ↓
[Chunk Phase]
    ├─ Split parsed content into semantic chunks (300–500 tokens)
    ├─ Add overlap (50 tokens between chunks)
    ├─ Generate chunk IDs: `hdfc_largecp_001`, `hdfc_largecp_002`, etc.
    ├─ Attach metadata:
    │   ├─ source_url
    │   ├─ amc_name
    │   ├─ scheme_name
    │   ├─ scheme_isin
    │   ├─ scraped_datetime: 2026-04-16T09:15:32Z
    │   ├─ document_type: "scheme_page"
    │   └─ content_hash
    └─ Total chunks generated: 245 (example)
    ↓
[Embedding Phase]
    ├─ Batch encode chunks (100 chunks/batch)
    ├─ Model: sentence-transformers (all-mpnet-base-v2)
    ├─ Time: ~2 seconds total for 245 chunks
    └─ Embeddings: 768-dimensional vectors
    ↓
[Index Update Phase]
    ├─ Vector DB (Pinecone):
    │   ├─ Upsert 245 new embeddings
    │   ├─ Replace old embeddings with same chunk_id
    │   └─ Time: 1–2 seconds
    │
    ├─ BM25 Index (Whoosh):
    │   ├─ Rebuild full index from chunks
    │   ├─ Index text for keyword search
    │   └─ Time: <1 second
    │
    └─ PostgreSQL Metadata:
        ├─ Insert/update chunks table
        ├─ Update last_indexed timestamp
        └─ Time: 2–3 seconds
    ↓
[Cache Invalidation]
    ├─ Clear Redis:
    │   ├─ Query cache (all keys)
    │   ├─ Session data
    │   └─ Session: <100ms
    └─ Status: CACHE_CLEARED
    ↓
[Validation & Health Checks]
    ├─ Verify chunk count > 0: ✓ (245 chunks)
    ├─ Verify all 15 URLs indexed: ✓
    ├─ Health check: Query vector DB: ✓ (response < 100ms)
    ├─ Verify BM25 index loaded: ✓
    └─ Status: VALIDATION_PASSED
    ↓
[Logging & Monitoring]
    ├─ Total runtime: 15 seconds
    ├─ URLs processed: 15/15 ✓
    ├─ Chunks created: 245
    ├─ Failed URLs: 0 (1 retry success)
    ├─ Human review: Required for 0 new fields
    ├─ Log entry: INFO - Daily scrape completed successfully
    └─ DB record: INSERT INTO scrape_runs (run_date, chunks_count, duration_sec)
    ↓
09:15 AM - Scraper Complete
Next scheduled run: Tomorrow 09:00 AM
```

**Error Handling During Scrape:**
```
Scenario 1: URL Timeout
├─ Initial attempt: Timeout after 30s
├─ Retry #1 (after 5s exponential backoff): Success
└─ Result: Processed normally

Scenario 2: URL Returns 404
├─ Initial attempt: HTTP 404
├─ Retry #1-3: Still 404
├─ Skip processing for this URL
└─ Alert: Email admin@groww.in (URL unreachable)

Scenario 3: Parsing Error (Missing Expected Data)
├─ Extract expense ratio: NOT FOUND
├─ Validation fails
├─ Log warning: "Expense ratio not found in HDFC Large-Cap"
├─ Still index chunks (partial data)
└─ Flag for manual review

Scenario 4: Embedding Generation Fails
├─ Batch encode error
├─ Retry with smaller batch size (50 chunks)
├─ If still fails: Skip embedding, use keyword-only search
└─ Alert: Check embedding service health
```

---

## 11. Data Flow: Example Query

```
User Query: "What is the minimum SIP for HDFC Large-Cap?"

1. INTAKE
   Input → Chat UI
   Last successful scrape: 2026-04-16 09:15 AM ✓
   
2. VALIDATION
   ├─ PII Check: No sensitive data ✓
   ├─ Intent: factual_query ✓
   └─ Classification: scheme_property (minimum_sip, HDFC_largecp)

3. RETRIEVAL
   ├─ Vector Search: Encode "minimum SIP HDFC large-cap" → 768D embedding
   │   Pinecone: Top-5 similar chunks (0.92, 0.88, 0.85, 0.79, 0.71)
   │   All chunks from today's 09:15 AM scrape ✓
   │
   ├─ BM25 Search: Keywords ["minimum", "SIP", "HDFC", "large-cap"]
   │   Whoosh: Top-3 matches (BM25: 42.5, 39.2, 36.1)
   │
   ├─ Fusion: Combine + deduplicate → [Chunk A (95%), Chunk B (88%), Chunk C (82%)]
   │
   └─ Result Set (all from today's scrape):
       ├─ Chunk A: chunk_id=hdfc_largecp_045 (score: 95%, scraped_datetime: 2026-04-16T09:15Z)
       │   Text: "Minimum SIP amount is ₹500 for all HDFC schemes"
       │   Source: https://groww.in/mutual-funds/amc/hdfc-mutual-funds
       │
       ├─ Chunk B: chunk_id=hdfc_largecp_051 (score: 88%, scraped_datetime: 2026-04-16T09:15Z)
       │   Text: "SIP is eligible for all HDFC schemes"
       │   Source: https://groww.in/mutual-funds/amc/hdfc-mutual-funds
       │
       └─ Chunk C: chunk_id=hdfc_largecp_028 (score: 82%, scraped_datetime: 2026-04-16T09:15Z)
           Text: "HDFC Large-Cap Fund allows STP to other HDFC schemes"
           Source: https://groww.in/mutual-funds/amc/hdfc-mutual-funds

4. CONTEXT ASSEMBLY
   ├─ Format 3 chunks with metadata
   ├─ Max tokens: 2500
   ├─ Prioritize recency (all from today's scrape)
   ├─ Verify source_url is in allowed whitelist: https://groww.in/mutual-funds/amc/hdfc-mutual-funds ✓
   └─ Context window ready for LLM

5. GENERATION
   Prompt → LLM (GPT-4 @ T=0.1)
   
   LLM Output:
   "The minimum SIP investment for HDFC Large-Cap Fund is ₹500. 
    You can start with SIP through the Groww platform. 
    Check HDFC's official page for any current promotions or special offers."
   
6. POST-PROCESSING
   ├─ Citation extraction: https://groww.in/mutual-funds/amc/hdfc-mutual-funds → VERIFIED ✓
   ├─ Whitelist check: groww.in domain ✓
   ├─ Source reachability: HTTP HEAD → 200 ✓
   ├─ Timestamp: 2026-04-16 (from scraped_datetime)
   ├─ Sentence count: 3 ✓
   ├─ Confident assertions: Verified against chunk text ✓
   └─ Final response ready

7. OUTPUT
   Response to UI:
   {
     "answer": "The minimum SIP investment for HDFC Large-Cap Fund is ₹500. 
                You can start with SIP through the Groww platform. 
                Check HDFC's official page for any current promotions or special offers.",
     "source_url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
     "last_updated": "2026-04-16",
     "last_scraped": "2026-04-16T09:15:32Z",
     "confidence": 0.94,
     "chunk_ids": ["hdfc_largecp_045", "hdfc_largecp_051", "hdfc_largecp_028"]
   }

8. DISPLAY
   User sees:
   "The minimum SIP investment for HDFC Large-Cap Fund is ₹500. 
    You can start with SIP through the Groww platform. 
    Check HDFC's official page for any current promotions or special offers.
    
    📎 Source: https://groww.in/mutual-funds/amc/hdfc-mutual-funds
    🕐 Last updated from sources: 2026-04-16 (refreshed daily at 9 AM)"
```

---

## 12. Security & Compliance

### 12.1 Privacy (No-PII Enforcement)

```
PII Detection Rules:

PATTERN          REGEX/CHECK                      ACTION
─────────────────────────────────────────────────────────
PAN              [A-Z]{5}[0-9]{4}[A-Z]            Block + Warn
Aadhaar          \d{12}                           Block + Warn
Phone (India)    \+91[6-9]\d{9}                   Block + Warn
Email            [a-z]+@[a-z]+\.[a-z]+           Block + Dynamic message
Account Number   [A-Z0-9]{12,20}                 Block + Generalize
OTP              \d{4,6}                         Block + Context-based
```

**Response to PII:**
```
"I don't store or process personal information. 
For account-specific help, contact Groww Support: groww.in/help"
```

### 12.2 Source Whitelist (Scheduler-aware)

**Primary Allowed Domain:**
```
✓ groww.in/mutual-funds/amc/*    (Only 15 configured URLs from scraper)
  └─ 15 URL whitelist enforced by scraper (HDFC, ICICI, SBI, etc.)
```

**Fallback Educational Links:**
```
✓ sebi.gov.in/*                  (Regulatory guidance)
✓ amfi.org.in/*                  (Industry standards)
✓ rbi.org.in/*                   (Central bank guidelines)
```

**Prohibited Domains:**
```
✗ Any URL outside the 15-URL whitelist from scraper
✗ Blogs, Reddit, Quora (unreliable)
✗ Financial news sites (opinion-heavy)
✗ Chat forums (unverified advice)
✗ YouTube, social media (advice risk)
✗ Competitor sites
```

**Scraper Validation Rules:**
```
Before indexing any chunk:
1. Verify source_url is in 15-URL config ✓
2. Verify last scrape was successful ✓
3. Verify content_hash matches expected domain ✓
4. Verify no external links embedded (only Groww domain) ✓
```

### 12.3 Data Retention & Audit

- **Query Logs**: Anonymized, 90-day retention (for improvement, not tracking)
- **Corpus Updates**: Automated daily refresh (9 AM); changelog tracked
  - Scrape start/end timestamps
  - URLs processed (success/failure count)
  - Chunks created/updated
  - Content hash changes (detect modifications)
- **Audit Trail**: All responses logged with source URLs for compliance
- **Compliance**: Annual review for SEBI, AMFI, privacy regulations
- **Scraper Logs**: 7-day retention (failure details, retry counts, alerts)

---

## 13. Monitoring & Observability (Scheduler-Aware)

### 13.1 Key Metrics (Including Scraper Health)

**Scraper Metrics:**
```
Daily Job Metrics:
├─ URLs fetched: 15 total
├─ Success rate: Target 100% (alert if < 95%)
├─ Retry rate: Track URLs requiring retries
├─ Fetch latency: p95 < 10s (for all 15 URLs)
├─ Total runtime: Target < 30s (from 9 AM start to completion)
├─ Chunks created: Baseline (used for anomaly detection)
├─ Content changes: % of URLs with new content
└─ Parse errors: < 1% of extracted fields
```

```
Query Time Metrics:
├─ Latency: p50 < 800ms, p99 < 2s
├─ Retrieval precision: > 85%
├─ Citation accuracy: 99%+
├─ PII block rate: 100%
└─ Uptime: > 99.5%

Data Quality Metrics:
├─ Answer factual accuracy: > 95% (human review sample)
├─ User satisfaction (CSAT): > 4.2/5
├─ Refusal accuracy: 98%+ (correctly reject non-factual Q)
├─ Source freshness: Always < 24 hours old (refreshed daily at 9 AM)
└─ Content completeness: All 15 URLs indexed daily

Volume Metrics:
├─ Queries/day
├─ Fallback rate (not found)
├─ Refusal rate (opinion/PII)
└─ Repeat users
```

### 13.2 Logging & Alerts (Daily Scraper Focus)

**Daily Scraper Alerts:**
```
CRITICAL (Immediate action):
├─ Job did not run at 09:00 AM (scheduler failure)
├─ > 2 URLs failed to fetch (out of 15)
├─ Embedding generation failed (all chunks)
├─ Vector DB or BM25 index not updated
└─ Parse errors on > 10% of URLs

WARNING (Review within 4 hours):
├─ 1 URL timeout (requires retry)
├─ Content hash mismatch (data corruption detected)
├─ Missing expected fields (e.g., no expense ratio)
├─ Chunks < baseline count (possible parsing issue)
└─ Index update latency > 5 minutes

INFO (Daily log):
├─ Job completed successfully at HH:MM (with runtime)
├─ X URLs processed, Y chunks created
├─ Z content changes detected
└─ Cache invalidated
```

```
Query-Time Alerts:
├─ Citation URL unreachable from query (instant alert)
├─ Vector DB latency > 1s (during query)
├─ PII false-negative (unsafe output detected)
├─ LLM API errors (> 5% error rate)
└─ Source corpus stale warning (>24 hours old – requires scraper investigation)

Logging Levels:
├─ INFO: 
│   ├─ Query received, answer generated
│   ├─ Daily scrape job completed
│   └─ Cache invalidated
├─ WARN: 
│   ├─ Fallback to BM25, refusal triggered
│   ├─ URL retrieval failure (retry attempted)
│   └─ Chunk count below baseline
├─ ERROR: 
│   ├─ Validation failure, API error
│   ├─ Scheduler failed to trigger
│   └─ Embedding transformation failed
└─ DEBUG: 
    ├─ Embedding scores, chunk sampling
    └─ Scraper retry attempts, content hash values
```

---

## 14. Deployment Plan (With Scheduler)

### 14.1 Phases

**Phase 1: MVP (Week 1–2)**
- Core RAG pipeline (retrieval + generation)
- 15 Groww AMC URLs configured
- Manual initial seed (first data load)
- Basic UI (Streamlit)
- Scheduler framework (APScheduler setup, ready for testing)

**Phase 2: Production (Week 3–4)**
- GitHub Actions workflow enabled and tested
- Automated daily corpus refresh (9 AM IST)
- Scraping service deployed with 15 URL concurrency
- Enhanced guardrails (PII, advice detection)
- React UI + deploy to cloud
- Slack notifications for scraper success/failure
- GitHub Actions dashboard monitoring

**Phase 3: Scaling (Week 5–6)**
- Extended AMC URL scope (25–50 URLs)
- GitHub Actions parallel jobs (separate jobs for scrape, parse, embed, index)
- A/B testing on LLM models
- Advanced analytics dashboard (GitHub Actions + monitoring service)
- User feedback loop & corpus quality metrics

### 14.2 Deployment Stack (With Scheduler & Scraper)

```
Development:
└─ Local: Docker compose
    ├─ FastAPI app
    ├─ Vector DB (local Qdrant or Milvus)
    ├─ Elasticsearch (BM25)
    ├─ PostgreSQL (metadata + staging)
    └─ Redis (cache)
    └─ Manual scraper triggers via CLI (no scheduler needed locally)

Staging:
└─ GitHub Actions (scheduled workflow) + AWS/Azure resources
    ├─ GitHub Actions: Free tier scheduler (daily 9 AM IST / 3:30 AM UTC)
    ├─ AWS S3: Raw HTML archives (for audit)
    ├─ RDS PostgreSQL: Staging + metadata tables
    ├─ Pinecone: Managed Vector DB
    └─ Elasticsearch: BM25 index

Production:
├─ **Scheduler**: GitHub Actions Workflow
│   ├─ Cron trigger: 0 3 * * * (UTC) = 09:00 AM IST
│   ├─ Runs on: ubuntu-latest (GitHub-hosted runner)
│   ├─ Timeout: 15 minutes per run
│   ├─ Retry logic: Built-in GitHub Actions retry (3 attempts)
│   └─ Notification: Slack webhooks for status updates
│
├─ **Scraper Service**: GitHub Actions Job
│   ├─ Runs on: ubuntu-latest container
│   ├─ Concurrency: 3 parallel HTTP requests
│   ├─ Environment: Python 3.10+
│   ├─ Network: Public internet access (to fetch from Groww)
│   └─ Authentication: AWS IAM OIDC role + GitHub secrets
│
├─ **Index Layer**: Distributed & resilient
│   ├─ Vector DB: Pinecone (managed, 24/7 uptime)
│   ├─ BM25: Elasticsearch cluster (2+ nodes, multi-AZ)
│   └─ Metadata: RDS PostgreSQL (multi-AZ, daily backups)
│
├─ **Query API**: Auto-scaling
│   ├─ ECS/AKS: 2–10 pods (auto-scale on CPU/memory)
│   ├─ Load balancer: ALB / Azure Load Balancer
│   └─ Response cache: Redis (invalidated daily at 9 AM)
│
├─ **Storage**: Layered
│   ├─ S3 / Blob Storage: Raw HTML archives (for audit)
│   ├─ PostgreSQL: Chunks, metadata, scrape logs
│   └─ Redis: Query cache (TTL: 1 hour)
│
└─ **Observability**:
    ├─ GitHub Actions logs (built-in)
    ├─ CloudWatch (if using AWS resources)
    ├─ Slack notifications (via GitHub Actions webhook)
    ├─ Custom metrics: Stored in PostgreSQL
    └─ Dashboard: Grafana / Kibana visualization (optional)
```

---

## 15. Success Criteria (With Scheduler Metrics)

| Criterion | Target | Measurement |
|---|---|---|
| **Scraper Success Rate** | 100% | All 15 URLs processed daily (0 failures) |
| **Scraper Runtime** | < 30s | Total time from 9 AM trigger to completion |
| **Data Freshness** | < 24h | All indexed data < 24 hours old |
| **Chunk Quality** | Baseline ± 10% | No anomalies in chunk count per run |
| **Parse Errors** | < 1% | Failed field extractions / total fields |
| **Citation Accuracy** | 99%+ | Human audit of 100 sample responses |
| **PII Block Rate** | 100% | No PII leakage in outputs |
| **Answer Factuality** | > 95% | Semantic similarity to source ≥ 0.85 |
| **Response Latency** | < 1s | p95 end-to-end (after scraper completes) |
| **Coverage** | 85%+ | Answerable queries / total queries |
| **Query Uptime** | 99.5%+ | Availability during non-scrape hours |
| **User Satisfaction** | > 4.0/5 | CSAT survey (n=50+) |
| **False Refusals** | < 2% | Factual queries mistakenly rejected |

---

## 16. Glossary

| Term | Definition |
|---|---|
| **RAG** | Retrieval-Augmented Generation: Fetch relevant context, then generate responses |
| **Vector DB** | Database optimized for semantic similarity search on embeddings |
| **BM25** | Best Match algorithm: Keyword-based ranking for exact term matching |
| **Embedding** | Dense vector (e.g., 768D) representing text semantics |
| **Factsheet** | Official document with scheme summary (NAV, AUM, expense ratio, benchmark) |
| **KIM/SID** | Key Information Memorandum / Scheme Information Document (SEBI mandated) |
| **ELSS** | Equity-Linked Savings Scheme (3-year lock-in, tax benefit) |
| **Riskometer** | SEBI-mandated risk classification (Low, Low to Moderate, Moderate, High) |
| **Exit Load** | Charge levied on redemption within specified period (e.g., 0.5% within 1 year) |
| **Expense Ratio** | Annual fee as % of AUM (covers management, custody, regulatory costs) |
| **PII** | Personally Identifiable Information (PAN, Aadhaar, account numbers, OTP, email, phone) |
| **Guardrails** | Rules to prevent harmful outputs (advice, PII, hallucinations) |
| **Citation** | Source URL provided with every answer for transparency & verification |
| **Scraper** | Automated service that fetches content from 15 Groww URLs daily at 9 AM |
| **APScheduler** | Python background task scheduler for cron-based jobs (daily 9 AM trigger) |
| **Content Hash** | SHA-256 hash of fetched page content; used to detect changes since last scrape |
| **Chunk ID** | Unique identifier per chunk: `{amc}_{scheme}_{chunk_seq}` (e.g., hdfc_largecp_001) |
| **Staging Table** | PostgreSQL table for raw HTML before parsing (audit trail) |
| **Last-Modified Check** | HTTP header check to conditionally skip unchanged pages (optimization) |
| **Concurrent Requests** | Max 3 parallel HTTP requests during scrape (rate limiting) |

---

## 17. Completed Phases - Implementation Status

### Phase 1: ✅ MVP Scraper & Scheduler (Week 1-2) - COMPLETED

**Objective**: Daily automated data collection (15 URLs at 9 AM IST)

**Deliverables**:
- ✅ GitHub Actions workflow (`.github/workflows/daily-scrape.yml`)
  - Cron trigger: `0 3 * * *` (UTC) = 09:00 AM IST
  - Timeout: 15 minutes per run
  - Automatic retry (3x with exponential backoff)
  - Slack notifications
  
- ✅ Scraping Service
  - URL list: 15 official Groww AMC pages (hardcoded whitelist)
  - Concurrent requests: Max 3 (rate limiting)
  - Timeout per URL: 30 seconds
  - Retry backoff: 5s → 15s → 45s (exponential)
  - Last-Modified header check (conditional fetch optimization)
  - Content hash tracking (SHA-256 for change detection)
  
- ✅ PostgreSQL Staging
  - `scrape_runs` table: Track daily execution
  - `url_health` table: Monitor per-URL status
  - `scrape_html_staging` table: Raw HTML archive (7-day retention)
  
- ✅ Error Handling & Monitoring
  - Retry logic with exponential backoff
  - Logging: INFO, WARN, ERROR levels
  - Alerts: Slack webhooks on failure
  - Health checks: Validate scraper health every 2 hours

**Architecture**:
```
GitHub Actions Scheduler (09:00 AM IST)
    ↓
[Fetch Phase] - Concurrent (max 3)
    ├─ 15 URLs from whitelist
    ├─ 30s timeout per URL
    ├─ Last-Modified header check (skip unchanged)
    └─ Exponential backoff retry
    ↓
[Store Phase]
    ├─ Raw HTML → PostgreSQL staging
    ├─ Content hash → change detection
    ├─ Metadata → url_health table
    └─ Scrape run log → scrape_runs table
```

**Testing Status**: ✅ Production-ready

---

### Phase 2: ✅ Chunking & Embedding (Week 3-4) - COMPLETED

**Objective**: Parse raw HTML, create semantic chunks, generate embeddings

**Deliverables**:

#### 2.1 Chunking Strategy (300–500 tokens)
From `CHUNKING_STRATEGY.md`:
- **Chunk Size**: 300–500 tokens (~400–700 words)
- **Overlap**: 50 tokens between consecutive chunks (5-10% overlap)
- **Tokenizer**: `transformers.AutoTokenizer` (from sentence-transformers)

**Chunking Algorithm**:
```
Raw HTML (from Phase 1)
    ↓
[Parse Phase]
    ├─ HTML → BeautifulSoup
    ├─ Extract key fields:
    │  ├─ Scheme name, ISIN, category
    │  ├─ Expense ratio, exit load, lock-in
    │  ├─ Minimum SIP, riskometer
    │  ├─ Benchmark, AUM
    │  └─ Performance data
    ├─ Clean text (whitespace, encoding)
    └─ Validate required fields
    ↓
[Chunk Phase]
    ├─ Split by semantic boundaries
    ├─ Token count: 300–500 per chunk
    ├─ Overlap: 50 tokens
    ├─ Chunk ID: {amc}_{scheme}_{seq}
    ├─ Metadata attachment:
    │  ├─ source_url (Groww AMC page)
    │  ├─ amc_name (extracted from URL)
    │  ├─ scheme_name
    │  ├─ scheme_isin
    │  ├─ document_type
    │  ├─ question_types (tags)
    │  ├─ scraped_datetime (ISO 8601)
    │  └─ content_hash
    └─ Total chunks: 200–300 per scrape run
```

**Chunk Types**:
```
1. SCHEME_INFO (100–200 tokens)
   - Scheme name, ISIN, category, launch date
   - Fund house details
   
2. EXPENSE_CHARGES (200–350 tokens)
   - Expense ratio (direct + indirect)
   - Entry/exit load, transaction charges
   - Updated dates
   
3. PORTFOLIO_COMPOSITION (250–400 tokens)
   - Top holdings, allocations
   - Sector-wise breakdown
   
4. PERFORMANCE_METRICS (200–300 tokens)
   - Historical returns (1Y, 3Y, 5Y, 10Y)
   - Benchmark comparison
   
5. RISK_INDICATORS (150–250 tokens)
   - Riskometer classification (SEBI mandated)
   - Volatility metrics
   - Drawdown info
   
6. EXIT_TERMS (100–200 tokens)
   - Minimum SIP, lump-sum
   - Lock-in period (e.g., 3 years for ELSS)
   - Exit load schedule
```

#### 2.2 Embedding Strategy (768D Vectors)
From `EMBEDDING_STRATEGY.md`:

**Primary Model**: `sentence-transformers/all-mpnet-base-v2`
- Dimension: 768D vectors
- Max sequence: 512 tokens (sufficient for our chunks)
- Language: Multilingual (English + Hindi)
- Inference: ~50ms per chunk on CPU
- Cost: FREE (open-source)

**Embedding Pipeline**:
```
Parsed Chunks
    ↓
[Batch Encoding] (100 chunks/batch)
    ├─ Model: all-mpnet-base-v2
    ├─ Tokenizer: BPE (50K+ tokens)
    ├─ Inference: GPU/CPU (pre-allocated)
    ├─ Dimension check: All 768D ✓
    └─ Time: ~2 seconds for 245 chunks
    ↓
[Embedding Storage]
    └─ Vector DB (Pinecone Phase 2 / Chroma Cloud Phase 3)
```

**Vector DB Options**:
- Phase 2: Pinecone (serverless, managed)
- Phase 3: Chroma Cloud (with API)
- Alternatives: Weaviate, Qdrant

**Testing Status**: ✅ Production-ready

---

### Phase 3: ✅ Hybrid Search + LLM Integration (Current) - COMPLETED

**Objective**: Implement Chroma Cloud + Grok LLM for production queries

**Deliverables**:

#### 3.1 Chroma Cloud Integration
- Vector DB: `api.trychroma.com`
- Collections: Sharded by AMC (`groww_faq_{amc_name}`)
- Dense embeddings: Chroma Cloud Qwen (768D)
- Sparse embeddings: Chroma Cloud Splade (BM25-like)

#### 3.2 Hybrid Search Algorithm (RRF + GroupBy)
```
Query: "What is the expense ratio of ELSS?"
    ↓
[Dense Search] (Chroma Cloud Qwen 768D)
    ├─ Cosine similarity on 768D vectors
    ├─ Top-20 results
    └─ Time: 50–100ms
    ↓
[Sparse Search] (Chroma Cloud Splade)
    ├─ Keyword/BM25-like matching
    ├─ Terms: ["expense", "ratio", "ELSS"]
    ├─ Top-20 results
    └─ Time: 30–80ms
    ↓
[Reciprocal Rank Fusion]
    ├─ K=60 (RRF parameter)
    ├─ Weighting: 60% dense + 40% sparse
    ├─ Combined ranking
    └─ Time: <5ms
    ↓
[GroupBy Deduplication]
    ├─ Group by: source_url
    ├─ Max: 3 chunks per source
    ├─ Final Top-5 results
    └─ Time: <10ms
```

#### 3.3 Grok LLM Integration (xAI)
- Model: Grok 2 (`grok-2`)
- API: `https://api.x.ai/v1/chat/completions`
- Temperature: 0.1 (deterministic, fact-focused)
- Max tokens: 150 (enforce brevity)
- Response time: 300–1000ms

**Generation Pipeline**:
```
Top-5 Context Chunks
    ↓
[Prompt Assembly]
    ├─ System role: Factual FAQ assistant
    ├─ Rules: No advice, no PII, mandatory citation
    ├─ Context: 3 chunks max
    ├─ Output format: ≤3 sentences + source URL
    └─ Temperature: 0.1
    ↓
[Token Generation] (Grok API)
    ├─ Max tokens: 150
    ├─ Stop sequences: ["Q:", "Note:", "Source:"]
    └─ Time: 300–1000ms
    ↓
[Post-processing]
    ├─ Extract URL (regex validation)
    ├─ Verify whitelist (groww.in, sebi.gov.in, amfi.org.in)
    ├─ Enforce 3-sentence limit
    └─ Remove uncertain language
```

#### 3.4 REST API Endpoints
```
GET  /health                (Health check)
GET  /info                  (API information)
GET  /stats                 (Service statistics)
POST /query                 (Single query)
POST /batch                 (Batch queries, max 10)
```

**Testing Status**: ✅ Production-ready (deployed to staging)

---

## 18. Future Phases Roadmap

### Phase 4: Extended Coverage & Multi-Language (Planned)

**Goals**:
- Expand to 25–50 Groww AMC URLs (all major AMCs)
- Hindi language support (chunking + embedding + UI)
- Advanced filtering (risk level, category, AUM range)
- Mobile app integration

**Estimated Timeline**: Week 7–8

**Key Additions**:
```
New URLs (+25)
    ├─ Regional AMCs (India focused)
    ├─ Sector/thematic funds
    └─ International fund pages
    ↓
Hindi Language Support
    ├─ Chunk text: Auto-translate (Google Translate API)
    ├─ Embeddings: Multilingual model (already in use)
    ├─ UI: Hindi + English toggle
    └─ Response: Generate in user's language
    ↓
Advanced Filtering
    ├─ Risk level filter (Low, Medium, High)
    ├─ Category filter (Equity, Debt, Hybrid)
    ├─ AUM range filter
    └─ Performance range filter
```

### Phase 5: Analytics & Dashboards (Planned)

**Goals**:
- Query analytics dashboard
- Search trend tracking
- Frequently asked questions (FAQ mining)
- Performance metrics visualization
- User satisfaction tracking

**Estimated Timeline**: Week 9–10

**Key Components**:
```
Analytics Dashboard
    ├─ Query volume (daily, weekly, trends)
    ├─ Top schemes searched
    ├─ Refusal rate tracking
    ├─ Response latency p50/p95/p99
    ├─ Citation accuracy metrics
    └─ User satisfaction (CSAT tracking)
    
Data Collection
    ├─ Query logs (anonymized)
    ├─ Response quality scores (human reviews)
    ├─ Latency snapshots
    └─ Cache hit rates
```

### Phase 6: Fine-tuning & Optimization (Planned)

**Goals**:
- Fine-tune Grok on Groww-specific terminology
- Optimize chunk size for query success rate
- Implement response caching (Redis)
- Load testing & autoscaling

**Estimated Timeline**: Week 11–12

**Key Optimizations**:
```
Model Fine-tuning
    ├─ Train on 500 high-quality Q&A pairs
    ├─ Domain-specific terminology (ELSS, NAV, AUM, etc.)
    ├─ Optimize for ≤3 sentence responses
    └─ Improve citation extraction

Chunking Optimization
    ├─ A/B test chunk sizes (250, 300, 350, 400 tokens)
    ├─ Measure answer quality for each config
    ├─ Adjust overlap % based on results
    └─ Finalize optimal strategy

Performance Optimization
    ├─ Response caching (Redis, TTL=1 hour)
    ├─ Query deduplication (cache hits)
    ├─ Lazy loading (initialize on first use)
    ├─ Database query optimization
    └─ CDN for static assets
```

### Phase 7: Production Hardening (Planned)

**Goals**:
- Load testing (target: 1000 QPS)
- Auto-scaling setup (Kubernetes)
- Monitoring & alerting (24/7)
- Disaster recovery & backup

**Estimated Timeline**: Week 13–14

**Key Additions**:
```
Infrastructure
    ├─ Kubernetes cluster (auto-scaling 2–100 pods)
    ├─ Database replication (multi-region)
    ├─ Vector DB high availability (Chroma Cloud managed)
    ├─ Redis cluster (for distributed caching)
    └─ Load balancer (AWS ALB / Azure LB)
    
Monitoring
    ├─ Prometheus metrics collection
    ├─ Grafana dashboards (queries/s, latency, errors)
    ├─ CloudWatch alarms (CPU, memory, errors)
    ├─ Custom alerts (scraper failure, query latency > 2s)
    └─ PagerDuty integration (on-call rotations)
    
Backup & Recovery
    ├─ Daily PostgreSQL snapshots (to S3)
    ├─ Vector DB exports (weekly)
    ├─ Configuration versioning (GitHub)
    └─ Rollback procedures (tested monthly)
```

### Phase 8+: Continuous Improvement

**Ongoing**:
- Quarterly corpus refresh (URL scope review)
- Annual model upgrades (new embedding/LLM versions)
- User feedback integration
- Competitive analysis & feature additions
- Regulatory compliance updates (SEBI/AMFI changes)

---

## 17. Appendix: Scheduler & Scraper Configuration

### 17.1 GitHub Actions Workflow Configuration

```yaml
# .github/workflows/daily-scrape.yml

name: Daily Corpus Refresh (9 AM IST)

on:
  schedule:
    # 9:00 AM IST = 3:30 AM UTC
    - cron: '0 3 * * *'  # UTC
    # Alternative for IST timezone (if using GitHub Actions in IST region)
    # - cron: '0 9 * * *'  # IST
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape-and-index:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    env:
      PYTHON_VERSION: '3.10'
      AWS_REGION: 'us-east-1'
      LOG_LEVEL: 'INFO'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActionsRole
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Run daily scraper
        run: |
          python -m services.scraper.main run_daily_scrape
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          VECTOR_DB_API_KEY: ${{ secrets.VECTOR_DB_API_KEY }}
          VECTOR_DB_HOST: ${{ secrets.VECTOR_DB_HOST }}
      
      - name: Generate embeddings
        run: |
          python -m services.embedding.main generate_batch_embeddings
        env:
          EMBEDDING_MODEL: 'sentence-transformers/all-mpnet-base-v2'
          BATCH_SIZE: 100
      
      - name: Update indexes
        run: |
          python -m services.indexer.main update_all_indexes
        env:
          VECTOR_DB_API_KEY: ${{ secrets.VECTOR_DB_API_KEY }}
      
      - name: Invalidate cache
        run: |
          python -m services.cache.main invalidate_all
        env:
          REDIS_URL: ${{ secrets.REDIS_URL }}
      
      - name: Validate scrape
        run: |
          python -m services.validator.main validate_daily_run
      
      - name: Send Slack notification (success)
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Daily corpus refresh completed successfully",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Daily Corpus Refresh*\nTime: $(date -u)\nStatus: SUCCESS"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Send Slack notification (failure)
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "❌ Daily corpus refresh FAILED",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Daily Corpus Refresh*\nTime: $(date -u)\nStatus: FAILED\nCheck: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**GitHub Actions Secrets Required:**
```
AWS_ACCOUNT_ID              # AWS account ID for OIDC role
DATABASE_URL                # PostgreSQL connection string
VECTOR_DB_API_KEY           # Pinecone API key
VECTOR_DB_HOST              # Pinecone host
REDIS_URL                   # Redis connection string
SLACK_WEBHOOK_URL           # Slack webhook for notifications
```

### 17.2 Scraper Service Specifications

```python
# services/scraper.py

SCRAPER_CONFIG = {
    "urls": [
        "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
        "https://groww.in/mutual-funds/amc/icici-mutual-funds",
        "https://groww.in/mutual-funds/amc/sbi-mutual-funds",
        # ... 12 more
    ],
    "concurrent_requests": 3,
    "timeout_per_url": 30,
    "max_retries": 3,
    "retry_backoff": [5, 15, 45],  # Exponential: 5s, 15s, 45s
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
        "Accept": "text/html,application/xhtml+xml,...",
    },
    "check_last_modified": True,  # Conditional fetch
    "chunk_size_tokens": [300, 500],  # Range: min-max
    "chunk_overlap_tokens": 50,
    "batch_embedding_size": 100,
    "log_level": "INFO",
}

def run_daily_scrape():
    """Main scraper orchestrator"""
    run_id = generate_run_id()  # Timestamp-based unique ID
    logger.info(f"[{run_id}] Starting daily scrape at {datetime.now()}")
    
    try:
        # Fetch phase
        fetched_urls = fetch_all_urls(run_id)
        
        # Parse phase
        parsed_chunks = parse_and_chunk(fetched_urls, run_id)
        
        # Embed phase
        embedded_chunks = embed_chunks(parsed_chunks, run_id)
        
        # Index update phase
        results = update_indexes(embedded_chunks, run_id)
        
        # Validation
        validate_scrape(results, run_id)
        
        logger.info(f"[{run_id}] Scrape completed in {time.elapsed()}s")
        return {"run_id": run_id, "status": "success", **results}
    
    except Exception as e:
        logger.error(f"[{run_id}] Scrape failed: {str(e)}")
        alert_admin(f"Daily scrape failed: {str(e)}")
        return {"run_id": run_id, "status": "failed", "error": str(e)}
```

### 17.3 Database Schema for Scraper Metadata

```sql
-- Scrape runs tracking
CREATE TABLE scrape_runs (
    run_id VARCHAR(50) PRIMARY KEY,
    run_datetime TIMESTAMP NOT NULL,
    urls_total INT,
    urls_success INT,
    urls_failed INT,
    retry_count INT,
    chunks_created INT,
    duration_seconds INT,
    status ENUM('success', 'partial', 'failed'),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- URL health tracking
CREATE TABLE url_health (
    url_id INT PRIMARY KEY AUTO_INCREMENT,
    url VARCHAR(500) UNIQUE NOT NULL,
    amc_name VARCHAR(50),
    last_fetch_datetime TIMESTAMP,
    last_fetch_status INT,  -- HTTP status code
    last_modified_date DATE,
    content_hash VARCHAR(64),  -- SHA-256
    consecutive_failures INT DEFAULT 0,
    health_status ENUM('healthy', 'degraded', 'down'),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Staging table for raw HTML
CREATE TABLE scrape_html_staging (
    staging_id INT PRIMARY KEY AUTO_INCREMENT,
    run_id VARCHAR(50),
    url VARCHAR(500),
    raw_html LONGTEXT,
    fetch_status INT,
    content_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES scrape_runs(run_id)
);
```

---

## 18. Appendix: API Specification (Overview)

### 16.1 Query Endpoint

```
POST /api/query

Request:
{
  "query": "What is the expense ratio of ELSS?",
  "session_id": "user_123_session_456",
  "scheme_filter": "ELSS" (optional)
}

Response:
{
  "answer": "The Groww ELSS Fund charges an expense ratio of 0.50% per annum...",
  "source_url": "https://www.groww.in/factsheet/elss",
  "last_updated": "2026-04-16",
  "confidence_score": 0.94,
  "query_type": "factual_query",
  "retrieval_sources": [
    {"chunk_id": "elss_expense_001", "score": 0.95},
    {"chunk_id": "elss_expense_002", "score": 0.88}
  ],
  "processing_time_ms": 742
}
```

### 16.2 Refusal Response

```
Response (Advisory Query):
{
  "answer": "I can only provide factual information, not investment advice. 
             For educational resources, see SEBI's mutual fund guide below.",
  "source_url": "https://www.sebi.gov.in/investor-education/mutual-funds",
  "query_type": "opinion_query",
  "refusal_reason": "advisory_question",
  "confidence_score": 0.99
}
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-16  
**Status:** Architecture Finalized for Development
