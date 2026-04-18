# 📅 Scheduler Overview - Daily Corpus Refresh

## 📍 Scheduler Location

**File**: `.github/workflows/daily-scrape.yml`

**Type**: GitHub Actions Workflow  
**Status**: ✅ Configured & Ready  
**Trigger**: Automatic schedule + Manual trigger option

---

## ⏰ Schedule Details

### When Does It Run?

```
EVERY DAY AT: 9:00 AM IST (Indian Standard Time)
              3:30 AM UTC (Coordinated Universal Time)

Cron Expression: 30 3 * * *
                  │ │ │ │ └─ Day of Week: * (every day)
                  │ │ │ └─── Month: * (every month)
                  │ │ └───── Day of Month: * (every day)
                  │ └─────── Hour: 3 UTC = 8:30 AM IST + offset
                  └───────── Minute: 30 (30 past the hour)
```

**Equivalent Times Worldwide**:
- 🇮🇳 India: **9:00 AM IST**
- 🌍 UTC: **3:30 AM UTC**
- 🇬🇧 UK: 4:30 AM BST (summer) / 3:30 AM GMT (winter)
- 🇺🇸 US East: 11:30 PM EDT (summer) / 10:30 PM EST (winter)
- 🇺🇸 US West: 8:30 PM PDT (summer) / 7:30 PM PST (winter)

---

## 🔄 What The Scheduler Does?

### Step 1️⃣: Checkout Repository
- **Time**: ~5 seconds
- **Action**: Pulls latest code from GitHub
- **Purpose**: Ensures latest version of scraper runs

### Step 2️⃣: Setup Python 3.10
- **Time**: ~10 seconds
- **Action**: Installs Python 3.10 environment
- **Purpose**: Provides runtime for scripts

### Step 3️⃣: Install Dependencies
- **Time**: ~30-60 seconds
- **Action**: Installs required Python packages:
  - `phase_3_llm_integration/requirements.txt`
  - `beautifulsoup4` (HTML parsing)
  - `requests` (HTTP client)
  - `lxml` (XML/HTML processing)
- **Purpose**: Prepares all tools needed for scraping

### Step 4️⃣: Fetch & Ingest 15 Groww AMC URLs ⭐
- **Time**: ~3-5 minutes
- **Action**: Runs `python scripts/ingest_corpus.py`
- **What it does**:
  ```
  For each of 15 Groww AMC URLs:
  ├─ FETCH (fetch_urls.py)
  │  └─ Download HTML from URL
  │     - Rate limit: 1 request/sec
  │     - Retry: 3 attempts with exponential backoff
  │     - Timeout: 30 seconds per URL
  │
  ├─ PARSE & CHUNK (parse_chunks.py)
  │  └─ Extract text from HTML
  │     - Split into semantic chunks (300±50 tokens)
  │     - Deduplicates short chunks (<50 chars)
  │     - Extracts metadata (AMC name, scheme, timestamp)
  │
  ├─ EMBED (generate_embeddings.py)
  │  └─ Create 768D embeddings
  │     - Batch processing (100 chunks/batch)
  │     - Normalized vectors (unit length)
  │
  └─ INDEX (update_indexes.py)
     └─ Import to Chroma Cloud
        - Upsert chunks to collection
        - Preserve metadata
        - Update searchable index
  ```

**15 URLs Scraped Daily**:
1. https://groww.in/mutual-funds/amc/hdfc-mutual-funds
2. https://groww.in/mutual-funds/amc/icici-mutual-funds
3. https://groww.in/mutual-funds/amc/sbi-mutual-funds
4. https://groww.in/mutual-funds/amc/axis-mutual-funds
5. https://groww.in/mutual-funds/amc/kotak-mutual-funds
6. https://groww.in/mutual-funds/amc/aditya-birla-sun-life-mutual-funds
7. https://groww.in/mutual-funds/amc/dsp-mutual-funds
8. https://groww.in/mutual-funds/amc/idfc-mutual-funds
9. https://groww.in/mutual-funds/amc/nippon-india-mutual-funds
10. https://groww.in/mutual-funds/amc/hdfc-bank-mutual-funds
11. https://groww.in/mutual-funds/amc/induslind-mutual-funds
12. https://groww.in/mutual-funds/amc/mahindra-mutual-funds
13. https://groww.in/mutual-funds/amc/mirae-asset-mutual-funds
14. https://groww.in/mutual-funds/amc/motilal-oswal-mutual-funds
15. https://groww.in/mutual-funds/amc/trust-mutual-funds

### Step 5️⃣: Validate Corpus Indexing ✅
- **Time**: ~10-20 seconds
- **Action**: Runs validation check on Chroma Cloud
- **What it checks**:
  ```
  ✅ Total documents indexed ≥ 10
  ✅ Collection statistics valid
  ✅ No errors during import
  ```
- **Purpose**: Ensures corpus was successfully indexed

### Step 6️⃣: Log Completion 📝
- **Time**: ~2 seconds
- **Action**: Prints completion summary
- **Logs**:
  ```
  ✅ Daily corpus refresh completed successfully
  Scheduled: 9:00 AM IST (3:30 AM UTC daily)
  Source: 15 Groww AMC pages (official public data)
  Timestamp: [UTC timestamp]
  ```

### Step 7️⃣: Report Failure (if any) ⚠️
- **Time**: ~2 seconds
- **Action**: If any step fails, reports error
- **Logs**:
  ```
  ❌ Corpus refresh failed
  Time: [UTC timestamp]
  Manual intervention may be needed
  ```

---

## 📊 Total Runtime

| Phase | Time | Status |
|---|---|---|
| Checkout + Setup | ~15 sec | ✅ Quick |
| Install Dependencies | ~45 sec | ✅ Cached |
| Fetch 15 URLs | ~2 min | ✅ Rate limited |
| Parse & Chunk | ~1 min | ✅ Batch processed |
| Generate Embeddings | ~1 min | ✅ Vectorized |
| Update Chroma Index | ~30 sec | ✅ Upserted |
| Validate + Report | ~30 sec | ✅ Verified |
| **TOTAL** | **~5-6 min** | ✅ **Within 20-min timeout** |

---

## 🎮 Manual Trigger Option

You can also **manually trigger** the workflow anytime:

1. Go to GitHub: `.github/workflows/daily-scrape.yml`
2. Click **"Actions"** tab
3. Select **"Daily Corpus Refresh (9 AM IST)"**
4. Click **"Run workflow"** button
5. Workflow runs immediately

**Useful for**:
- Testing before automatic run
- Emergency corpus refresh
- Debugging issues
- Manual data updates

---

## 🔐 GitHub Secrets Required

The workflow uses these GitHub secrets (must be configured):

```
CHROMA_API_KEY        → API key for Chroma Cloud access
CHROMA_TENANT         → Chroma tenant ID
CHROMA_DATABASE       → Chroma database name
GEMINI_API_KEY        → Google Generative AI API key (not used in scheduler, but good to have)
```

**How to set them**:
1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add each secret with value
4. Save

---

## 📈 What Gets Updated Daily

After scheduler runs, your Chroma Cloud collection gets:

```
Monthly Growth Example:
├─ Day 1:  15 URLs → ~30-40 chunks indexed
├─ Day 2:  15 URLs → ~40-50 chunks indexed (new content)
├─ Day 3:  15 URLs → ~45-55 chunks indexed (updated)
├─ ...
└─ Month 1: ~150-200+ chunks indexed

Content Updated:
✅ Expense ratios
✅ Scheme details
✅ Factsheets
✅ Fund categories
✅ Riskometer data
✅ Benchmark info
✅ Exit load changes
✅ NAV updates
```

---

## 🚨 Error Handling

### Retry Strategy
```
URL Fetch Failure:
├─ Attempt 1: Fails (timeout)
├─ Wait 1 second
├─ Attempt 2: Fails (connection error)
├─ Wait 2 seconds  
├─ Attempt 3: Succeeds ✅
└─ Continue to next URL
```

### Failure Notifications
- ❌ If corpus has <10 documents → Exit with error
- ❌ If all URLs fail → Workflow fails
- ⚠️ If some URLs fail → Continue with successful ones

---

## 📋 Monitoring Scheduler

### Check Run History
**GitHub UI**:
1. Go to repo → **Actions** tab
2. Select **"Daily Corpus Refresh"** workflow
3. See all past runs with status ✅ or ❌
4. Click any run to see detailed logs

### Example Run Log
```
Log Entry Timeline:

3:30:00 AM UTC (9:00 AM IST)
├─ [Checkout] Pulling repository... ✅
├─ [Setup] Installing Python 3.10... ✅
├─ [Install] Installing dependencies... ✅
├─ [Fetch] Fetching 15 URLs...
│  ├─ hdfc-mutual-funds: 45 KB ✅
│  ├─ icici-mutual-funds: 52 KB ✅
│  ├─ sbi-mutual-funds: 38 KB ✅
│  └─ ... (12 more)
├─ [Parse] Creating chunks... ✅ (245 chunks)
├─ [Embed] Generating embeddings... ✅ (768D)
├─ [Index] Pushing to Chroma... ✅
├─ [Validate] Checking corpus... ✅ (250 docs)
└─ 3:36:00 AM UTC - COMPLETED ✅ (6 min runtime)
```

---

## 🎯 Next Steps to Activate Scheduler

1. **Configure GitHub Secrets** (if not already done):
   - Push to repo first, then set secrets in GitHub Settings
   
2. **Trigger Manual Test**:
   - Go to Actions → "Daily Corpus Refresh" → "Run workflow"
   
3. **Monitor First Run**:
   - Check logs in GitHub Actions
   - Verify Chroma Cloud gets documents
   
4. **Automatic Runs Start**:
   - Tomorrow at 9:00 AM IST, scheduler runs automatically
   - Every day after that at same time

---

## 📞 Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Workflow not running | Secrets not configured | Set CHROMA_* secrets in GitHub |
| "Corpus has <10 docs" | Fetch failed | Check URL accessibility, API keys |
| Slow runtime | Rate limiting | Already set to 1 req/sec (optimal) |
| Auth errors | Invalid API keys | Verify CHROMA_API_KEY, GEMINI_API_KEY |
| No new data | Content unchanged | Normal - updates pushed anyway |

---

**Status**: ✅ **SCHEDULER CONFIGURED & READY**  
**Schedule**: 🕘 Daily at **9:00 AM IST (3:30 AM UTC)**  
**Action**: Fetch 15 Groww URLs → Parse → Embed → Index to Chroma Cloud  
**Next Run**: Tomorrow at 9:00 AM IST
