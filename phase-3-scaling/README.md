# Phase 3: Scaling - Extended Coverage & LLM Integration (Week 5-6)

## Overview
Phase 3 expands the system scope and integrates GPT-4/Claude for intelligent fact-checking and response generation.

## Phase 3 Objectives

✅ **Extended URL Coverage**
- Scale from 15 to 25-50 Groww AMC URLs
- Add regional/niche fund house pages
- Implement parallel GitHub Actions jobs

✅ **LLM Integration**
- Integrate GPT-4 or Claude 3.5 API
- Fact-checking layer (semantic similarity > 0.85)
- Response quality guardrails (no advice, no hallucinations)
- Prompt engineering & fine-tuning

✅ **Fine-grained Monitoring**
- Advanced Slack dashboards (daily metrics)
- Grafana/DataDog dashboards
- Quality metrics tracking (citation accuracy, factuality)
- User feedback loop

✅ **Advanced Features**
- Multi-language support (English + Hindi)
- FAQ caching (Redis 1-hour TTL, invalidated daily)
- Featured questions rotation
- Performance optimization

✅ **Load Testing & Optimization**
- Query latency optimization (<500ms p99)
- Throughput scaling (100+ QPS capacity)
- Database query optimization
- Cache hit rate > 70%

## Folder Structure

```
phase-3-scaling/
├── llm_integration/
│   ├── gpt4_client.py
│   ├── claude_client.py
│   ├── prompt_templates.py
│   └── fine_tuning/
│
├── monitoring/
│   ├── metrics.py
│   ├── dashboards/
│   │   ├── slack_dashboard.py
│   │   └── grafana_config.json
│   └── alerts.py
│
├── multilingual/
│   ├── translator.py
│   ├── hindi_models/
│   └── translation_cache.py
│
├── optimization/
│   ├── query_optimization.py
│   ├── cache_strategy.py
│   └── load_testing/
│
├── README.md
└── DEPLOYMENT_CHECKLIST.md
```

## Extended URL List (25-50 URLs)

### Tier 1: Large AMCs (15 existing)
- HDFC, ICICI, SBI, Axis, Kotak, Wipro, Sundaram, Tata, Motilal Oswal, 
- Mirae Asset, Franklin Templeton, Reliance, JM Financial, IDFC, Aditya Birla

### Tier 2: Medium AMCs (10-15 additional)
- L&T, DSP, Invesco, Quantum, Canara Robeco, Bandhan, HSBC, UTI, 
- BOI AXA, SBI Magnum, etc.

### Tier 3: Niche/Boutique (10-20 additional)
- Baroda Pioneer, Post Office, Bajaj, Coffee, Nippon India, etc.

## LLM Integration Strategy

### Prompt Engineering
```
System Prompt:
- Role: Factual FAQ assistant for mutual funds
- Constraints: No advice, facts only, citation mandatory
- Output format: 1-3 sentences + 1 source URL

Few-shot Examples:
Q: "What is ELSS?" → A: "ELSS (Equity-Linked Savings Scheme) 
   is a type of tax-saving mutual fund with a 3-year lock-in period."
   (Source: SEBI guidelines)
```

### Fine-tuning (Optional)
- Collect 100+ Q&A pairs from Fund House FAQs
- Fine-tune GPT-4 or Claude on mutual fund terminology
- Reduce hallucinations, improve factuality score

## Monitoring Dashboard

### Slack Daily Summary
```
✅ Daily Corpus Refresh
📊 Metrics:
   - URLs Processed: 25/25 ✓
   - Chunks Created: 342
   - Avg Chunk Quality: 96%
📈 Query Analytics:
   - Queries/hour: 145
   - Avg Latency: 680ms
   - Cache Hit Rate: 74%
❌ Alerts:
   - 1 URL had 2 consecutive timeouts (HDFC - degraded)
```

## Performance Targets (Phase 3)

| Metric | Target | Status |
|---|---|---|
| **Query Latency** | p99 < 500ms | In Progress |
| **Citation Accuracy** | 99%+ | In Progress |
| **Factuality Score** | > 95% | In Progress |
| **Cache Hit Rate** | > 70% | In Progress |
| **Uptime** | 99.9% | In Progress |
| **URL Coverage** | 25-50 URLs | In Progress |
| **Multi-language** | EN + HI | In Progress |
| **Load Capacity** | 100+ QPS | In Progress |

## Implementation Timeline

- **Week 5**: LLM integration + prompt engineering, extended URL setup
- **Week 6**: Monitoring dashboards, multi-language support, performance optimization

## Success Criteria (Phase 3)

- [ ] 25-50 URLs indexed and monitored
- [ ] LLM integration working (GPT-4 or Claude)
- [ ] Citation accuracy > 99%
- [ ] Response factuality > 95%
- [ ] Query latency p99 < 500ms
- [ ] Cache hit rate > 70%
- [ ] Slack dashboards showing daily metrics
- [ ] Multi-language support (EN + HI)
- [ ] Load testing confirms 100+ QPS capacity
- [ ] User satisfaction > 4.2/5 (CSAT survey)

---

**Status**: Planning  
**Target Completion**: Week 5-6  
**Dependency**: Phase 2 must be complete  
**Investment**: Medium (LLM API costs, optimization effort)
