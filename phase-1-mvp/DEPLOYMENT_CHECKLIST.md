# Phase 1 Deployment Checklist

Complete this checklist to deploy Phase 1 (Scheduler + Scraping).

## Pre-Deployment (Week 1)

### Infrastructure Setup
- [ ] PostgreSQL database provisioned (AWS RDS / local)
- [ ] Redis instance provisioned (Phase 2, but prepare now)
- [ ] GitHub repository created and configured
- [ ] AWS account setup (if using OIDC authentication)

### Development Environment
- [ ] Python 3.10+ installed
- [ ] `pip` dependencies installed: `pip install -r requirements.txt`
- [ ] Environment variables configured locally
- [ ] Database connection tested locally

### GitHub Repository
- [ ] Repository initialized with git
- [ ] `.github/workflows/` directory created
- [ ] `daily-scrape.yml` workflow file committed

## GitHub Actions Secrets Configuration

### Add 6 Secrets to Repository
1. [ ] `AWS_ACCOUNT_ID` - Your AWS account ID (12-digit number)
2. [ ] `DATABASE_URL` - PostgreSQL connection string
   ```
   Example: postgresql://user:password@host:5432/groww_db
   ```
3. [ ] `VECTOR_DB_API_KEY` - Pinecone API key (will use Phase 2)
4. [ ] `VECTOR_DB_HOST` - Pinecone host URL (will use Phase 2)
5. [ ] `REDIS_URL` - Redis connection string (will use Phase 2)
6. [ ] `SLACK_WEBHOOK_URL` - Incoming webhook URL from Slack
   ```
   Example: https://hooks.slack.com/services/TXXX/BXXX/XXXX
   ```

**Steps to Add Secrets:**
```bash
# Via GitHub CLI (fastest)
gh secret set AWS_ACCOUNT_ID --body "123456789012"
gh secret set DATABASE_URL --body "postgresql://user:password@host:5432/groww_db"
gh secret set VECTOR_DB_API_KEY --body "xxx-api-key"
gh secret set VECTOR_DB_HOST --body "xxx.pinecone.io"
gh secret set REDIS_URL --body "redis://localhost:6379"
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/..."

# Or via GitHub UI:
# 1. Settings → Secrets and variables → Actions
# 2. Click "New repository secret"
# 3. Add each secret above
```

## Database Setup (Week 1)

### Create Tables
- [ ] Create `scrape_runs` table
- [ ] Create `url_health` table
- [ ] Create `scrape_html_staging` table
- [ ] Verify all tables created: `\dt` (PostgreSQL)

### Test Database Connection
```bash
# From GitHub Actions environment
python -c "import psycopg2; conn = psycopg2.connect(os.environ['DATABASE_URL']); print('Connected!')"
```

## Code Deployment (Week 1)

### Phase 1 Scraping Service
- [ ] Implement `phase_1_mvp/scraping/main.py` (entry point)
- [ ] Implement `phase_1_mvp/scraping/fetcher.py` (HTTP client)
- [ ] Implement `phase_1_mvp/scraping/parser.py` (HTML parsing)
- [ ] Implement `phase_1_mvp/scraping/database.py` (DB operations)
- [ ] Implement `phase_1_mvp/scraping/validator.py` (validation)
- [ ] Implement `phase_1_mvp/scraping/urls_config.py` (15 URLs)

### Configuration Files
- [ ] Create `phase_1_mvp/scraping/config.py` (global settings)
- [ ] Create `phase_1_mvp/scheduler/config.py` (scheduler settings)
- [ ] Update `requirements.txt` with Phase 1 dependencies

### Testing
- [ ] Run unit tests: `pytest phase_1_mvp/scraping/tests/`
- [ ] Manual test scraper: `python -m phase_1_mvp.scraping.main run_daily_scrape`
- [ ] Verify PostgreSQL has staging data after test run
- [ ] Check health_status table updated

## GitHub Actions Workflow Deployment (Week 1-2)

### Workflow Configuration
- [ ] Copy `daily-scrape.yml` to `.github/workflows/`
- [ ] Verify cron timing: `30 3 * * *` (UTC) = 9:00 AM IST
- [ ] Test manual trigger: `gh workflow run daily-scrape.yml`
- [ ] Monitor first test run in GitHub Actions UI

### Workflow Testing
- [ ] Manual trigger succeeds without errors
- [ ] All 15 URLs processed in test run
- [ ] Slack notification received on success
- [ ] Database tables populated with scrape data
- [ ] Check logs for any warnings/errors

## Slack Integration (Week 2)

### Setup Slack Channel
- [ ] Create Slack channel: `#groww-bot-alerts` (or similar)
- [ ] Create incoming webhook in Slack
- [ ] Test webhook: Send sample message
- [ ] Store webhook URL in GitHub secret `SLACK_WEBHOOK_URL`

### Notification Testing
- [ ] Trigger manual workflow: `gh workflow run daily-scrape.yml`
- [ ] Verify Slack notification arrives within 2 minutes
- [ ] Check notification format and content
- [ ] Test failure notification (optional: force a failure)

## Monitoring & Alerting (Week 2)

### GitHub Actions Monitoring
- [ ] Set up GitHub Actions notifications (email/browser)
- [ ] Monitor workflow logs for errors
- [ ] Track execution time (target: < 30 seconds for Phase 1)

### Database Monitoring
- [ ] Query latest scrape_run record: 
  ```sql
  SELECT * FROM scrape_runs ORDER BY created_at DESC LIMIT 1;
  ```
- [ ] Check url_health table for all 15 URLs
- [ ] Verify consecutive_failures = 0 for all URLs

### Health Checks
- [ ] All 15 URLs have status = 'healthy'
- [ ] No failed URLs logged in error_message
- [ ] Content hash varies across different scrape_runs (content changes)

## Production Readiness (Week 2)

### Final Validation
- [ ] Scraper runs successfully at scheduled 9 AM IST
- [ ] All 15 URLs fetched without errors
- [ ] Raw HTML stored in staging table
- [ ] Content hashes calculate correctly
- [ ] URL health statuses updated
- [ ] Slack notifications working

### Documentation
- [ ] Update `README.md` with actual deployment details
- [ ] Document any custom configuration
- [ ] Create runbook for troubleshooting
- [ ] Document backup & recovery procedures

### Performance Baseline
- [ ] Record baseline scrape runtime (target: < 30s in Phase 1)
- [ ] Record baseline chunk count (from staging HTML)
- [ ] Document baseline URL health status

## Go-Live Checklist

- [ ] All tests pass ✅
- [ ] GitHub Actions workflow deployed ✅
- [ ] Database fully populated ✅
- [ ] Slack notifications working ✅
- [ ] Manual trigger successful ✅
- [ ] Scheduled trigger ready (9 AM IST) ✅
- [ ] Monitoring & alerting in place ✅
- [ ] Documentation complete ✅

## Phase 1 Sign-Off

- [ ] Dev Team Lead: ___________________ (Date: ___)
- [ ] DevOps Lead: ___________________ (Date: ___)
- [ ] Project Manager: ___________________ (Date: ___)

---

**Phase 1 Status**: `[ ] Not Started  [ ] In Progress  [X] Ready for Deployment`

**Next Phase**: Phase 2 - Chunking & Embedding (Week 3-4)
