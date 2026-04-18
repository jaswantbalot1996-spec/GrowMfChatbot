# Phase 3: Chroma Cloud + Gemini LLM Integration

**Status**: ✅ Production Ready  
**Vector DB**: Chroma Cloud (Hybrid Search)  
**LLM**: Gemini (Google Generative AI)  
**Embedding Models**: Chroma Cloud Qwen (dense) + Splade (sparse)  
**Corpus**: 15 Groww AMC URLs (Daily 9 AM IST Refresh via GitHub Actions)

---

## What This Does

End-to-end facts-only FAQ assistant for Groww mutual funds:

```
Query: "What is the expense ratio of ELSS?"
  ↓
[Hybrid Search on Chroma Cloud]
  ├─ Dense: 768D semantic vectors (Qwen)
  ├─ Sparse: Keyword matching (Splade)
  └─ RRF: Reciprocal Rank Fusion
  ↓
[Gemini LLM Response]
  ├─ Context: Top 5 results from 15 AMC corpus
  ├─ Validation: PII blocking, advice refusal
  └─ Output: Factual answer with 1 source, ≤3 sentences
  ↓
[Citation + Timestamp]
  ├─ Answer: "ELSS expense ratios typically..."
  ├─ Source: https://groww.in/mutual-funds/amc/...
  └─ Last updated: 2026-04-18
```

---

## Quick Start (5 minutes)

### 1. Setup

```bash
cd phase_3_llm_integration

# Copy template
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Configuration

```bash
python -m phase_3_llm_integration.config
```

Expected output:
```
✅ Configuration validated successfully!
   • Chroma Cloud: api.trychroma.com
   • LLM Model: text-bison-001 (Gemini)
   • Hybrid Search: Enabled (Dense 60% + Sparse 40%)
```

### 3. Start API Server

```bash
python -m phase_3_llm_integration.api_server 8000
```

### 4. Test Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the expense ratio?"}'
```

Response:
```json
{
  "query": "What is the expense ratio?",
  "response": "The expense ratio is the annual cost...",
  "sources": [
    {
      "chunk_id": "hdfc_001",
      "amc_name": "HDFC",
      "source_url": "https://...",
      "score": 0.95
    }
  ],
  "confidence": 0.95,
  "latency_ms": 342.5,
  "status": "success"
}
```

---

## Architecture

### System Diagram

```
Phase 2 Output (Chunks + Embeddings)
         ↓
┌─────────────────────────────────────┐
│ Chroma Cloud (Hybrid Search)        │
├─────────────────────────────────────┤
│ Collections (sharded by AMC):       │
│  • groww_faq (default)              │
│  • groww_faq_hdfc                   │
│  • groww_faq_icici                  │
│                                     │
│ Dense Embeddings (768D):            │
│  • Model: Chroma Cloud Qwen         │
│  • Distance: Cosine similarity      │
│  • Search: Top-20 results           │
│                                     │
│ Sparse Embeddings:                  │
│  • Model: Chroma Cloud Splade       │
│  • Match: Keyword/BM25-like         │
│  • Search: Top-20 results           │
│                                     │
│ RRF Fusion:                         │
│  • K=60, 60% dense + 40% sparse    │
│  • Final results: Top-5             │
│                                     │
│ GroupBy Dedup:                      │
│  • Max 3 results per source         │
└────────────┬──────────────────────┘
             ↓
┌──────────────────────────┐
│ Gemini LLM (Google)      │
├──────────────────────────┤
│ • Response generation    │
│ • Facts-only mode        │
│ • Citation tracking      │
│ • Multi-language support │
└────────────┬─────────────┘
             ↓
         Answer ✓
```

---

## API Endpoints

### GET /health
Health check endpoint.

```bash
curl http://localhost:8000/health
```

### GET /info
API information.

```bash
curl http://localhost:8000/info
```

### GET /stats
Service statistics.

```bash
curl http://localhost:8000/stats
```

Response:
```json
{
  "status": "healthy",
  "chroma_cloud": {
    "collection": "groww_faq",
    "total_documents": 245,
    "dense_embedding_model": "chroma-cloud-qwen",
    "sparse_embedding_model": "chroma-cloud-splade"
  },
  "gemini_llm": {
    "model": "text-bison-001",
    "max_tokens": 2048,
    "temperature": 0.1
  }
}
```

### POST /query
Single query (main endpoint).

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is mutual fund?",
    "top_k": 5
  }'
```

**Parameters:**
- `query` (required): User question
- `top_k` (optional): Number of results (default: 5)

### POST /batch
Batch queries.

```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "What is mutual fund?",
      "Which funds have lowest exit load?"
    ]
  }'
```

---

## Usage Examples

### Python Direct

```python
from phase_3_llm_integration import create_phase3_service

# Create service
service = create_phase3_service()

# Single query
response = service.query("What is expense ratio?")
print(response['response'])
print(f"Confidence: {response['confidence']:.2%}")

# Batch
responses = service.batch_query([
    "Query 1",
    "Query 2",
])

# Stats
stats = service.get_statistics()
print(f"Total documents: {stats['chroma_cloud']['total_documents']}")
```

### REST API (Python Requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What is expense ratio?"}
)
result = response.json()
print(result['response'])
```

### REST API (JavaScript)

```javascript
fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'What is expense ratio?' })
})
.then(r => r.json())
.then(data => console.log(data.response))
```

---

## Configuration

All settings in `.env` (copy from `.env.example`):

```bash
# Chroma Cloud (required)
CHROMA_API_KEY=ck-7t4YnqoWntZg3RyM91HeRtNRPZa4w5Ct8HirMhqYWTsR

# Gemini LLM (required for responses)
GEMINI_API_KEY=your-gemini-api-key

# Hybrid search tuning (optional)
DENSE_WEIGHT=0.6        # 60% semantic search
SPARSE_WEIGHT=0.4       # 40% keyword search
TOP_K_FINAL=5           # Return top 5 results
RRF_K_PARAMETER=60      # RRF tuning constant
```

---

## Performance

Expected latencies:

| Component | Time |
|-----------|------|
| Dense search (20 results) | 50-100ms |
| Sparse search (20 results) | 30-80ms |
| RRF fusion | <5ms |
| GroupBy dedup | <10ms |
| Gemini LLM response | 300-1000ms |
| **Total** | **400-1200ms** |

Target: <800ms p95

---

## Troubleshooting

### Connection Issues

```bash
# Verify Chroma Cloud connection
python << 'EOF'
from phase_3_llm_integration.chroma_cloud_client import create_chroma_client
try:
    client = create_chroma_client()
    print("✓ Connected to Chroma Cloud")
except Exception as e:
    print(f"✗ Connection failed: {e}")
EOF
```

**Fix:** Check `CHROMA_API_KEY` in `.env`

### No Search Results

```bash
# Check collection stats
python << 'EOF'
from phase_3_llm_integration import create_phase3_service
service = create_phase3_service()
stats = service.get_statistics()
print(f"Documents: {stats['chroma_cloud']['total_documents']}")
EOF
```

**Fix:** Ensure Phase 2 data was imported to Chroma Cloud

### Slow Responses

**Fix:** Reduce `TOP_K_DENSE` and `TOP_K_SPARSE` in `.env`

---

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "phase_3_llm_integration.api_server", "8000"]
```

Build and run:
```bash
docker build -t groww-phase3 .
docker run -p 8000:8000 \
  -e CHROMA_API_KEY=your-key \
  -e GEMINI_API_KEY=your-key \
  groww-phase3
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phase3-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: phase3-api
  template:
    metadata:
      labels:
        app: phase3-api
    spec:
      containers:
      - name: phase3-api
        image: groww-phase3:latest
        ports:
        - containerPort: 8000
        env:
        - name: CHROMA_API_KEY
          valueFrom:
            secretKeyRef:
              name: phase3-secrets
              key: chroma-api-key
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: phase3-secrets
              key: gemini-api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## Files

| File | Purpose |
|------|---------|
| `config.py` | Configuration management |
| `chroma_cloud_client.py` | Hybrid search implementation |
| `gemini_client.py` | LLM response generation |
| `phase3_service.py` | Query orchestration service |
| `api_server.py` | Flask REST API |
| `data_import.py` | Data import utilities |
| `requirements.txt` | Dependencies |
| `.env.example` | Configuration template |

---

## Next Steps

1. ✅ Copy `.env.example` to `.env`
2. ✅ Install: `pip install -r requirements.txt`
3. ✅ Validate: `python -m phase_3_llm_integration.config`
4. ✅ Start API: `python -m phase_3_llm_integration.api_server 8000`
5. ✅ Test query: `curl http://localhost:8000/query ...`

---

## Support

- **Config issues**: Check `.env` variables
- **Connection issues**: Verify API keys
- **Performance issues**: Adjust TOP_K or RRF weights
- **Logs**: Check `logs/phase_3.log`

---

**Version**: 3.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-04-17
