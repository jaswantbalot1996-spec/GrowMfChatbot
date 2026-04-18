# Phase 2: Production - Chunking, Embedding & Indexing (Week 3-4)

## Overview
Phase 2 extends Phase 1 by implementing the core RAG pipeline components:
- **Chunking**: Convert raw HTML into semantic chunks (300-500 tokens)
- **Embedding**: Generate 768D vectors for semantic search
- **Indexing**: Update Vector DB (Pinecone) + BM25 index
- **Query API**: Serve FAQ queries with context retrieval

## Phase 2 Objectives

✅ **Chunking Service**
- Parse raw HTML from Phase 1 staging table
- Split into semantic chunks (300-500 tokens, 50-token overlap)
- Extract metadata (scheme name, ISIN, concepts/tags)
- Output schema per CHUNKING_STRATEGY.md

✅ **Embedding Service**
- Batch encode chunks using sentence-transformers
- 768D embeddings with L2 normalization
- Incremental updates via content hash detection
- Batch size: 100 chunks for efficiency

✅ **Vector DB Integration**
- Upload embeddings to Pinecone
- Store metadata (source_url, amc_name, scheme_name, concepts)
- Support semantic similarity search

✅ **BM25 Indexing**
- Rebuild keyword index from chunks
- Support exact term matching (expense ratio, ELSS, etc.)
- Fusion with vector search (0.7 semantic + 0.3 keyword)

✅ **Query API**
- FastAPI endpoints for chat queries
- PII detection + query validation
- Hybrid retrieval (vector + BM25)
- Citation verification
- Response generation (basic template, Phase 3 adds LLM)

## Folder Structure

```
phase-2-production/
├── chunking/
│   ├── config.py
│   ├── main.py
│   ├── service.py
│   ├── tokenizer.py
│   └── tests/
│
├── embedding/
│   ├── config.py
│   ├── main.py
│   ├── service.py
│   └── tests/
│
├── indexing/
│   ├── config.py
│   ├── vector_db.py
│   ├── bm25_index.py
│   └── tests/
│
├── query_api/
│   ├── main.py
│   ├── routes.py
│   ├── validators.py
│   └── retrievers.py
│
├── README.md
└── DEPLOYMENT_CHECKLIST.md
```

## Architecture

```
Phase 1 Output (Raw HTML)
         │
         ▼
┌─ Chunking Service
│   ├─ Fetch from scrape_html_staging
│   ├─ Parse + split into chunks (300-500 tokens)
│   ├─ Extract schemes/concepts
│   └─ Output to chunks table
│
├─ Embedding Service
│   ├─ Batch encode chunks (100 chunks/batch)
│   ├─ 768D vectors, L2-normalized
│   └─ Store in PostgreSQL + vector DB
│
├─ Indexing
│   ├─ Upsert to Pinecone (vector DB)
│   ├─ Build BM25 index from text
│   └─ Update metadata indexes
│
└─ Query API (FastAPI)
    ├─ Receive chat query
    ├─ Validate (PII check, intent classification)
    ├─ Retrieve (vector + BM25, hybrid fusion)
    ├─ Generate (LLM in Phase 3)
    └─ Return response + source
```

## Key Deliverables

1. **CHUNKING_STRATEGY.md** - Already created ✅
   - Chunking algorithms (greedy algorithm, overlap)
   - Concept extraction (8 concept types)
   - Output schema (18-field JSON per chunk)
   - ~245 chunks from 15 URLs

2. **EMBEDDING_STRATEGY.md** - Already created ✅
   - Model: sentence-transformers/all-mpnet-base-v2 (768D)
   - Batch processing (100 chunks/batch, <3 min total)
   - Incremental updates via content hash
   - Pinecone integration

3. **GITHUB_ACTIONS_SCHEDULER.md** - Already created ✅
   - GitHub Actions workflow with 9 job steps
   - Daily 9 AM IST (03:30 AM UTC) cron trigger
   - Slack notifications

4. **Query API** (New)
   - FastAPI for serving FAQ queries
   - Hybrid search (vector + keyword)
   - Citation verification
   - Response formatting

## Implementation Timeline

- **Week 3**: Chunking + Embedding services
- **Week 4**: Vector DB + BM25 indexing, Query API, e2e testing

## Transition from Phase 1

Phase 1 outputs (raw HTML + metadata) will be consumed by Phase 2:

```
Phase 1: scrape_runs, scrape_html_staging, url_health
    │
    └─→ Phase 2: chunks table
           │
           └─→ vector embeddings + BM25 index
              │
              └─→ Query API (responds to user questions)
```

---

**Status**: Planning  
**Target Completion**: Week 3-4  
**Dependency**: Phase 1 must be complete
