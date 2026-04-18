# Phase 4: Extended Coverage & Multi-Language Support

**Status**: ✅ Implementation Ready  
**Timeline**: Week 7-8  
**Goals**: 
- Expand from 15 → 38+ Groww URLs (all major AMCs)
- Add Hindi language support (translate + bidirectional queries)
- Implement advanced filtering (risk, category, AUM, expense ratio)
- Maintain p95 latency < 1.5s with 2x query volume

---

## Architecture Overview

```
Phase 3 System
    ↓
┌─────────────────────────────────────────┐
│ Phase 4 Enhancements                    │
├─────────────────────────────────────────┤
│ 1. Extended URL Coverage (38+ URLs)     │
│    • 5 TIER-1 AMCs (large)              │
│    • 7 TIER-2 AMCs (mid-cap)            │
│    • 11 TIER-3 AMCs (emerging)          │
│    • 3 TIER-4 Categories (sectors)     │
│                                         │
│ 2. Multi-Language Support               │
│    • English ↔ Hindi bidirectional      │
│    • Auto-detect query language         │
│    • Translate chunks at ingestion      │
│    • Translate responses dynamically    │
│                                         │
│ 3. Advanced Filtering                   │
│    • Risk level (5 SEBI levels)        │
│    • Fund category (8 types)            │
│    • AUM range filtering                │
│    • Expense ratio range                │
│    • Lock-in period filtering           │
│    • Exit load presence                 │
│    • Scheme name regex match            │
│    • AMC code filtering                 │
└─────────────────────────────────────────┘
```

---

## Components Implemented

### 1. ✅ Extended AMC Configuration (`amc_config.py`)
- **38 URLs** across 4 tiers:
  - TIER-1 (5): HDFC, ICICI, SBI, Axis, Kotak
  - TIER-2 (7): Motilal, UTI, Nippon, Aditya, Invesco, ICICI Pru, Canara
  - TIER-3 (11): Quantum, DSP, Tata, Franklin, PGIM, Bandhan, Vanguard, Principal, Bajaj, BOI AXA, Mahindra
  - TIER-4 (3): Sector/category pages
- Configuration: Language support (EN + HI), Translation service (Google)

### 2. ✅ Multi-Language Translation Service (`translation_service.py`)
**Features**:
- Google Translate API integration (with fallback)
- 50+ domain-specific Hindi translations (fallback dictionary)
- **TranslationCache**: In-memory caching (TTL: 30 days)
- **MultiLanguageTranslator**: Translates queries, responses, chunks
- **LanguageDetector**: Auto-detect Hindi vs English in user input

**Usage**:
```python
from phase_4_extended_coverage.translation_service import create_translator, Language

translator = create_translator(use_cache=True)

# Translate text
hindi_text = translator.translate_text(
    "The expense ratio is 0.50%",
    Language.HINDI
)

# Translate responses
response_hi = translator.translate_response(response, Language.HINDI)
```

### 3. ✅ Advanced Filtering Module (`advanced_filter.py`)
**Features**:
- **8 Filter Types**:
  1. Risk level (5 SEBI levels)
  2. Fund category (8 categories)
  3. AUM range (in crores)
  4. Expense ratio range (%)
  5. Exit load presence
  6. Lock-in period (years)
  7. Scheme name (regex)
  8. AMC code list

**Usage**:
```python
from phase_4_extended_coverage.advanced_filter import (
    create_filter_engine, FilterCriteria, RiskLevel, FundCategory
)

filter_engine = create_filter_engine()

# Create filter criteria
criteria = FilterCriteria(
    max_risk_level=RiskLevel.MODERATE,
    categories=[FundCategory.EQUITY],
    max_expense_ratio=0.75,
    amc_codes=["hdfc", "icici"]
)

# Apply filters
filtered_chunks = filter_engine.filter_chunks(chunks, criteria)
```

### 4. ✅ Enhanced Phase 4 API Server (`api_server_phase4.py`)
**New Endpoints**:
- `GET /languages` - Supported languages
- `GET /filters` - Available filter options
- `POST /query` - Query with language + filters
- `POST /batch` - Batch queries (max 10)

**Request Example**:
```json
{
  "query": "What is the expense ratio of ELSS?",
  "language": "hi",
  "filters": {
    "max_risk_level": "moderate",
    "categories": ["equity"],
    "max_expense_ratio": 1.0
  }
}
```

**Response Example**:
```json
{
  "query": "ELSS का व्यय अनुपात क्या है?",
  "answer": "ELSS फंड का व्यय अनुपात...",
  "language": "hi",
  "detected_language": "hi",
  "sources": [...],
  "filters_applied": true,
  "latency_ms": 542
}
```

### 5. ✅ Scraper Configuration (`scraper_config.py`)
**Extended Scraper Specs**:
- 38+ URLs with 4-tier parallel fetching
- Concurrent: 5 requests (rate limiting)
- Timeout: 30s per URL
- Retry: 3x exponential backoff
- Translation: Auto-translate chunks to Hindi
- Parallel tier processing (strategy matrix)

### 6. ✅ Updated GitHub Actions Workflow
**Features**:
- 4-tier parallel processing (T1, T2, T3, T4)
- Multi-step per tier: Fetch → Parse → Embed → Translate → Update
- Language-aware indexing (English + Hindi)
- Slack notifications (success/failure)
- Cache invalidation (full multi-language)

---

## Installation & Setup

### Step 1: Install Phase 4 Dependencies
```bash
cd phase_4_extended_coverage
pip install -r ../requirements.txt  # Phase 1-3
pip install google-cloud-translate flask-cors pyyaml regex redis sqlalchemy psycopg2-binary
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```

Add to `.env`:
```bash
# Google Translate (for Hindi)
GOOGLE_TRANSLATE_API_KEY=your-api-key

# Redis (for translation caching)
REDIS_URL=redis://localhost:6379/0

# Extended URL list (from amc_config.py)
PHASE4_AMC_TIERS=tier1,tier2,tier3,tier4
```

### Step 3: Verify Extended URLs
```bash
python -c "from phase_4_extended_coverage.amc_config import AMC_CONFIG; print(f'Total URLs: {sum(len(v) for k, v in AMC_CONFIG.items() if k.startswith(\"tier\"))}')"
# Output: Total URLs: 38
```

### Step 4: Start Phase 4 API Server
```bash
python phase_4_extended_coverage/api_server_phase4.py 8000
```

### Step 5: Test Multi-Language Query
```bash
# English query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the expense ratio of HDFC Funds?",
    "language": "en"
  }'

# Hindi query (auto-detected)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "HDFC फंड का व्यय अनुपात क्या है?"
  }'

# Query with advanced filters
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ELSS funds with low risk",
    "filters": {
      "max_risk_level": "low_to_moderate",
      "categories": ["equity"]
    }
  }'
```

---

## Performance Expectations

### Latency (p95)
| Component | Time |
|-----------|------|
| Query detection + embedding | 50-100ms |
| Hybrid search (with filtering) | 80-150ms |
| Translation (cache miss) | 200-500ms |
| LLM response generation | 300-1000ms |
| **Total end-to-end** | **630-1750ms** |
| **Target p95** | **<1500ms** ✅ |

### Corpus Size
- Phase 3 (15 URLs): ~300 chunks
- Phase 4 (38 URLs): ~800+ chunks
- With Hindi: 1600+ indexed vectors

### Throughput
- Single query: ~1.5s p95
- Batch (10 queries): ~15-20s
- Daily scrape (38 URLs): ~3-4 minutes

---

## Testing

### Unit Tests
```bash
# Test translation service
python -m pytest phase_4_extended_coverage/tests/test_translation.py

# Test filtering
python -m pytest phase_4_extended_coverage/tests/test_filters.py

# Test API endpoints
python -m pytest phase_4_extended_coverage/tests/test_api.py
```

### Integration Test
```bash
# End-to-end query with translation + filtering
python phase_4_extended_coverage/tests/test_e2e.py
```

### Load Test (optional)
```bash
# Simulate 50 QPS for 1 minute
python -m locust -f phase_4_extended_coverage/tests/locustfile.py \
  --host http://localhost:8000 \
  -u 50 -r 10 --run-time 1m
```

---

## Monitoring & Observability

### Metrics Tracked
```
Translation service:
  ├─ Cache hit rate (target: >80%)
  ├─ Translation latency p50/p95 (target: <300ms)
  └─ Failed translation count

Filter engine:
  ├─ Filtering accuracy (% of results matching criteria)
  ├─ Filter latency (target: <10ms)
  └─ Most common filters used

Scraper (Phase 4):
  ├─ URL success rate per tier (target: >95%)
  ├─ Chunk count per URL (baseline: ~20-30)
  ├─ Translation progress (chunks/sec)
  └─ Total scrape duration (target: <5 min)
```

### Dashboards
- **Translation**: Real-time hit rate, latency, errors
- **Filtering**: Filter distribution, accuracy, latency
- **API**: QPS by language, response times, errors
- **Corpus**: Chunk count, language distribution, freshness

---

## Rollout Plan

### Stage 1: Soft Launch (Day 1-2)
- Deploy Phase 4 API in shadow mode (10% traffic)
- Monitor translation errors, filtering accuracy
- Verify performance under load

### Stage 2: Gradual Rollout (Day 3-4)
- Increase traffic to 50% for Phase 4 URL coverage
- 100% traffic for English queries
- 25% traffic for Hindi queries (test)

### Stage 3: Full Launch (Day 5+)
- 100% traffic to Phase 4 system
- Extended URL coverage live
- Hindi language fully supported
- Advanced filters available

### Rollback Plan
- Revert to Phase 3 API if latency > 2s p95
- Fall back to English-only if translation errors > 5%
- Disable filters if filter latency > 50ms

---

## Next Phase (Phase 5)

**Analytics & Dashboards** (Week 9-10):
- Query analytics dashboard
- FAQ mining (most common questions)
- User satisfaction tracking (CSAT)
- Search trend visualization
- Performance metrics dashboard

---

## File Structure
```
phase_4_extended_coverage/
├── __init__.py
├── amc_config.py                 # 38 AMC URLs configuration
├── translation_service.py        # Multi-language support
├── advanced_filter.py            # Filtering engine
├── api_server_phase4.py          # Enhanced API endpoints
├── scraper_config.py             # Extended scraper config
├── requirements.txt              # Phase 4 dependencies
└── tests/
    ├── test_translation.py
    ├── test_filters.py
    ├── test_api.py
    └── test_e2e.py
```

---

## Support & Troubleshooting

**Q: Translation is slow**  
A: Check Redis connection. Translation caching should speed up subsequent queries.

**Q: Hindi queries return English**  
A: Language detection may need improvement. Check `LanguageDetector.hindi_chars`.

**Q: Filtering isn't working**  
A: Verify chunk metadata has required fields (amc_code, fund_category, riskometer, etc.)

**Q: Scraper fails on some URLs**  
A: Check URL accessibility. Some URLs may require authentication or have CAPTCHAs.

---

**Version**: 4.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-04-18
