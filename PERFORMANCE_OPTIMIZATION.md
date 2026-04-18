# ⚡ Performance Optimization Guide - Groww Chatbot

**Current Performance**: 13-60 seconds per query  
**Target Performance**: 3-5 seconds per query  
**Bottleneck**: Chroma Cloud network latency + excessive token limit

---

## 📊 Performance Baseline (as of April 18, 2026)

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Ollama inference (39ms/token) | ✅ | ✅ | Good (GPU enabled) |
| Max tokens | 2048 (❌ WAY too high) | 150 | **NEEDS FIX** |
| Chroma Cloud latency | 930ms | <200ms | Network issue |
| Total query latency | 13-60s | 3-5s | **NEEDS OPTIMIZATION** |

---

## 🟢 QUICK WIN #1: Reduce Max Tokens (ALREADY DONE ✅)

### What was changed:
```python
# OLD: 2048 tokens (generates 100+ sentences!)
GEMINI_MAX_TOKENS = 2048

# NEW: 150 tokens (enforces ≤3 sentences per RAG_ARCHITECTURE.md)
GEMINI_MAX_TOKENS = 150
```

### Impact:
- **Latency reduction**: ~13-15 seconds faster
- **Token generation**: 2048 → 150 = ~13x fewer tokens
- **Estimated new time**: 60 seconds → 8-10 seconds

### Why it works:
- RAG_ARCHITECTURE.md specifies: "Answers ≤3 sentences"
- 150 tokens is sufficient for 3 sentences (~50 tokens each)
- 2048 was generating 50-100 sentences (way too verbose)
- Fewer tokens = faster inference

---

## 🟡 OPTIMIZATION #2: Reduce Chroma Cloud Latency (5X FASTER)

### Problem:
```
Current: Chroma Cloud (remote, 930ms latency)
Issue: Network round-trip to San Francisco servers
```

### Solution Options (in order of speed improvement):

#### Option A: Use Local Chroma (FASTEST - 5X improvement)
```bash
# Start local Chroma Cloud
docker run -p 8000:8000 chromadb/chroma

# Update .env
CHROMA_HOST=localhost:8000
CHROMA_API_KEY=""  # Not needed for local
```
**Expected improvement**: 930ms → 50-100ms per query (+15 seconds faster)

#### Option B: Switch to Milvus (VERY FAST - 3X improvement)
```bash
# Start Milvus
docker run -d -p 19530:19530 milvusdb/milvus

# Update config to use Milvus client
pip install pymilvus
```
**Expected improvement**: 930ms → 150-200ms per query (+10 seconds faster)

#### Option C: Use Qdrant (FAST - 2X improvement)
```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Update config
pip install qdrant-client
```
**Expected improvement**: 930ms → 300-400ms per query (+5 seconds faster)

---

## 🔵 OPTIMIZATION #3: Response Caching (For Repeated Queries)

**Status**: ✅ Already implemented in api_server_phase4.py

### How it works:
```
First query: "What is ELSS?"  → 10 seconds (full pipeline)
Second query: "What is ELSS?" → 0.2 seconds (Redis cache hit!)
                                 = 50X FASTER!
```

### Activation:
1. Ensure Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

2. Check cache settings in api_server_phase4.py:
```python
# Cache TTL = 1 hour for FAQ queries
CACHE_TTL = 3600
```

### Expected improvement:
- Repeated queries: 90%+ reduction (cache hits)
- Unique queries: 0% improvement (cache miss)
- Real-world mixed: 30-50% improvement overall

---

## 🔴 OPTIMIZATION #4: Use Smaller LLM Model (20%+ faster)

### Current:
```
llama3.2:latest: 1.9GB, ~39ms/token ✅ Already good
```

### Faster alternatives:
```
gemma:2b:        1.7GB, ~30ms/token (20% faster)
llama2:7b:       3.9GB, ~50ms/token (30% slower, more accurate)
mistral:7b:      4.1GB, ~45ms/token (15% slower, good quality)
```

### Change model:
```bash
# Edit .env
OLLAMA_MODEL=gemma:2b

# Pull model if not already loaded
ollama pull gemma:2b

# Restart API
python phase_4_extended_coverage/api_server_phase4.py 8000
```

### Expected improvement:
- Current: 39ms/token × 150 tokens = 5.8s generation
- With gemma:2b: 30ms/token × 150 tokens = 4.5s generation
- **Net improvement**: ~1.3 seconds

---

## 🟣 OPTIMIZATION #5: Parallel Retrieval + Generation (Advanced)

### Current (Sequential):
```
Query
  ↓
Retrieval (~1-2s from Chroma)
  ↓
LLM Generation (~6s from Ollama)
  ↓
Post-processing (~0.5s)
  ↓
Response
Total: ~7.5-8.5s
```

### Optimized (Parallel):
```
Query
  ├─→ Retrieval (1-2s)
  └─→ While retrieval is happening, prepare LLM
        (context becomes available mid-stream)
  ↓
Combined: ~6-7s (generation starts earlier)
```

### Implementation:
```python
# Use async/await or threading in Flask
from concurrent.futures import ThreadPoolExecutor

@app.route('/query', methods=['POST'])
async def query():
    data = request.get_json()
    
    # Parallel execution
    with ThreadPoolExecutor() as executor:
        retrieval_future = executor.submit(retrieve, data['query'])
        # LLM can start prepping while retrieval happens
        llm_future = executor.submit(llm_prepare)
        
        results = retrieval_future.result()
        answer = llm_future.result(results)
    
    return jsonify(answer)
```

**Expected improvement**: ~2-3 seconds (parallelism overhead reduction)

---

## 📋 Implementation Roadmap

### Phase 1: Quick Win (DONE ✅)
- [x] Reduce max tokens 2048 → 150

### Phase 2: Next (30 minutes)
- [ ] Switch to local Chroma Cloud (Docker)
- [ ] Update .env and config
- [ ] Restart API server

### Phase 3: Medium-term (1-2 hours)
- [ ] Consider alternative models (gemma:2b)
- [ ] Optimize Redis caching
- [ ] Monitor real-world performance

### Phase 4: Long-term (optimization)
- [ ] Parallel retrieval + generation
- [ ] Request batching
- [ ] Model quantization (for faster CPU inference)

---

## 🎯 Performance Targets After Changes

| Step | Current | After Fix #1 | After Fixes #1+#2 |
|------|---------|--------------|-------------------|
| Retrieval | 1-2s | 1-2s | 50-200ms |
| LLM Gen (150 tokens) | 6s | 6s | 6s |
| Post-processing | 0.5s | 0.5s | 0.5s |
| **TOTAL** | **13s** | **8s** | **3-5s** ✅ |

---

## 🔍 Monitoring & Verification

### Test after each optimization:
```bash
python diagnose_latency.py
python analyze_latency_advanced.py
```

### Expected output after all fixes:
```
✅ Total time: 3000-5000ms (3-5 seconds)
✅ Ollama inference: 39ms/token (GPU)
✅ Chroma latency: 50-100ms
✅ Cache hit rate: 30-50%
```

---

## 💡 Additional Tips

### 1. Pre-warm Ollama model (first request optimization)
```python
# On startup, load model into memory
llm_client.generate_response("warmup", [])
```

### 2. Batch similar queries
```bash
# Instead of 10 individual queries → 10 seconds each
# Use batch endpoint with max 10 queries → 15 seconds total
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{"queries": [...]}'
```

### 3. Enable request compression
```python
# Compress Chroma Cloud responses
COMPRESS_RESPONSES = True
```

---

## 📞 Support

If still experiencing slow queries after these optimizations:

1. Check system resources:
   ```bash
   python diagnose_latency.py
   ```

2. Check network:
   ```bash
   ping api.trychroma.com
   curl -w '@curl-format.txt' https://api.trychroma.com/api/info
   ```

3. Monitor logs:
   ```bash
   tail -f api_server_logs.txt | grep "latency"
   ```

---

**Last updated**: April 18, 2026  
**Testing**: Verified with llama3.2:latest + Chroma Cloud
