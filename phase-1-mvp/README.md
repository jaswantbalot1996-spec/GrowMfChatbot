# Phase 1: MVP - Scheduler & Scraping (Week 1-2)

## Overview
Phase 1 focuses on building the core infrastructure for **automated daily data collection** via a scheduler and scraping service. This phase establishes the foundation for the entire RAG system.

## Phase 1 Objectives

✅ **Scheduler Setup**
- GitHub Actions workflow for daily 9 AM IST execution
- Manual trigger support for testing
- Slack notifications for success/failure

✅ **Scraping Service**
- Fetch 15 official Groww AMC URLs
- Error handling with exponential backoff retries
- Content change detection (Last-Modified header + content hash)
- Rate limiting (3 concurrent requests max)

✅ **Data Staging**
- PostgreSQL staging table for raw HTML
- Metadata logging (fetch status, timestamps, content hashes)
- Audit trail for compliance

✅ **Validation Framework**
- Basic health checks (URL reachability, content presence)
- Logging for monitoring and debugging
- Error alerting mechanism

## Folder Structure

```
phase-1-mvp/
├── scheduler/
│   ├── config.py              # Scheduler configuration (cron timing, retries)
│   ├── github_actions_setup.md # GitHub Actions deployment guide
│   └── secrets_template.txt   # Required GitHub secrets checklist
│
├── scraping/
│   ├── config.py              # Scraping parameters (URLs, timeouts, concurrency)
│   ├── main.py                # Scraper service entry point
│   ├── fetcher.py             # HTTP client with retry logic
│   ├── parser.py              # HTML parsing & extraction
│   ├── database.py            # Database operations (staging)
│   ├── validator.py           # Validation checks
│   ├── urls_config.py         # List of 15 Groww AMC URLs
│   └── tests/
│       ├── test_fetcher.py
│       ├── test_parser.py
│       └── test_validator.py
│
├── README.md                   # This file
└── DEPLOYMENT_CHECKLIST.md    # Step-by-step deployment guide

```

## Key Features

### 🔄 Scheduler (GitHub Actions)
- **Trigger**: Daily at 9:00 AM IST (03:30 AM UTC)
- **Cron**: `30 3 * * *` (UTC)
- **Manual Testing**: Trigger via `gh workflow run daily-scrape.yml`
- **Notifications**: Slack webhook on success/failure
- **Timeout**: 15 minutes per run
- **Retry**: GitHub Actions native retry (3 attempts)

### 🕷️ Scraper Service
- **Scope**: 15 official Groww AMC URLs only
- **HTTP Client**: `requests` library with timeout (30s per URL)
- **Concurrency**: 3 parallel requests (rate limiting)
- **Retry Logic**: Exponential backoff (5s, 15s, 45s)
- **Change Detection**:
  - HTTP Last-Modified header check
  - SHA-256 content hash for verification
  - Skip unchanged pages (optimization)
- **Error Handling**: Log all failures, alert on > 2 failures per run

### 💾 Data Storage
- **Staging Table**: Raw HTML + metadata
- **Tracking Table**: Successful/failed URL runs
- **Health Table**: URL status & consecutive failures

### ✅ Validation
- URL reachability (HTTP HEAD check)
- Content presence (required fields verification)
- Chunk count anomaly detection (vs. baseline)
- Error logging & alerting

## Architecture

```
┌─ GitHub Actions Scheduler (9 AM IST)
│
├─→ Checkout Repository
│
├─→ Setup Python 3.10
│
├─→ Install Dependencies (requirements.txt)
│
├─→ Run Daily Scraper
│   ├─ Fetch 15 URLs (3 parallel)
│   ├─ Check Last-Modified (skip if unchanged)
│   ├─ Store raw HTML + metadata in PostgreSQL
│   ├─ Retry failed URLs (exponential backoff)
│   └─ Log success/failure metrics
│
├─→ Logging & Validation
│   ├─ Count processed URLs
│   ├─ Verify all URLs indexed
│   └─ Alert on failures
│
└─→ Slack Notification
    ├─ Success: All 15 URLs processed, X chunks ready
    └─ Failure: Error message + GitHub Actions run link
```

## Setup Instructions

### 1. Configure GitHub Actions Secrets

Add these 6 secrets to your GitHub repository settings:

```
AWS_ACCOUNT_ID          # AWS account ID (if using OIDC)
DATABASE_URL            # PostgreSQL connection string
VECTOR_DB_API_KEY       # Pinecone API key (Phase 2)
VECTOR_DB_HOST          # Pinecone host (Phase 2)
REDIS_URL               # Redis connection (Phase 2)
SLACK_WEBHOOK_URL       # Slack incoming webhook
```

**Steps:**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret name + value

### 2. Deploy Workflow File

The workflow file is located at: `.github/workflows/daily-scrape.yml`

**Manual trigger for testing:**
```bash
gh workflow run daily-scrape.yml
```

### 3. Database Setup

Create PostgreSQL tables:

```sql
-- Scrape runs tracking
CREATE TABLE scrape_runs (
    run_id VARCHAR(50) PRIMARY KEY,
    run_datetime TIMESTAMP NOT NULL,
    urls_total INT DEFAULT 15,
    urls_success INT DEFAULT 0,
    urls_failed INT DEFAULT 0,
    retry_count INT DEFAULT 0,
    chunks_created INT DEFAULT 0,
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
    last_fetch_status INT,
    last_modified_date DATE,
    content_hash VARCHAR(64),
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

## Deliverables

By end of Phase 1, you will have:

1. ✅ **GitHub Actions Workflow** (`.github/workflows/daily-scrape.yml`)
   - Scheduled daily at 9 AM IST
   - Manual trigger support
   - Slack notifications

2. ✅ **Scraping Service** (`scraping/main.py`)
   - Fetches 15 Groww AMC URLs
   - Handles retries with exponential backoff
   - Stores raw HTML in PostgreSQL

3. ✅ **Validation Framework** (`scraping/validator.py`)
   - URL health checks
   - Chunk count verification
   - Anomaly detection

4. ✅ **Database Schema**
   - Scrape runs tracking
   - URL health monitoring
   - Raw HTML staging

5. ✅ **Monitoring & Alerts**
   - Slack notifications (success/failure)
   - GitHub Actions logs
   - Database audit trails

## Testing Checklist

- [ ] GitHub Actions workflow deploys successfully
- [ ] Manual trigger works: `gh workflow run daily-scrape.yml`
- [ ] All 15 URLs fetch successfully
- [ ] Retry logic works on failed URLs
- [ ] Raw HTML stored in PostgreSQL staging table
- [ ] Content hash calculates correctly
- [ ] Last-Modified header detection works
- [ ] Slack notifications sent on completion
- [ ] Health status updated for all URLs
- [ ] Logs show proper error handling

## Next Steps (Phase 2)

Once Phase 1 is complete:
- Parse & chunk HTML content (see `CHUNKING_STRATEGY.md`)
- Generate embeddings (see `EMBEDDING_STRATEGY.md`)
- Index in Vector DB + BM25
- Invalidate cache
- Deploy query API

---

**Status**: Ready for Development  
**Target Completion**: Week 1-2  
**Owner**: DevOps / Backend Team
