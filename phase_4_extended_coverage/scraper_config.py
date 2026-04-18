"""
Phase 4: Updated Scraper Configuration for Extended URLs
Extends Phase 1 scraper to handle 38+ Groww AMC URLs
"""

import yaml
from typing import Dict, List, Any

# Updated GitHub Actions workflow configuration for Phase 4
GITHUB_ACTIONS_CONFIG = """
name: Phase 4 - Daily Corpus Refresh (Extended Coverage)

on:
  schedule:
    # 9:00 AM IST = 3:30 AM UTC
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  scrape-extended-coverage:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    strategy:
      matrix:
        amc_tier: [tier1, tier2, tier3, tier4]
    
    env:
      PYTHON_VERSION: '3.10'
      AWS_REGION: 'us-east-1'
      LOG_LEVEL: 'INFO'
      PHASE: '4'
    
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
          pip install google-cloud-translate
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActionsRole
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Fetch ${{ matrix.amc_tier }} AMCs
        run: |
          python -m phase_4_extended_coverage.scraper.fetch_urls \\
            --tier ${{ matrix.amc_tier }} \\
            --batch-size 5 \\
            --timeout 30
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
      
      - name: Parse & Chunk (${{ matrix.amc_tier }})
        run: |
          python -m phase_4_extended_coverage.scraper.parse_chunks \\
            --tier ${{ matrix.amc_tier }} \\
            --chunk-size-min 300 \\
            --chunk-size-max 500
      
      - name: Generate Embeddings (${{ matrix.amc_tier }})
        run: |
          python -m phase_4_extended_coverage.scraper.generate_embeddings \\
            --tier ${{ matrix.amc_tier }} \\
            --batch-size 100
      
      - name: Translate Chunks to Hindi (${{ matrix.amc_tier }})
        if: matrix.amc_tier != 'tier4'
        run: |
          python -m phase_4_extended_coverage.scraper.translate_chunks \\
            --tier ${{ matrix.amc_tier }} \\
            --target-language hi
        env:
          GOOGLE_TRANSLATE_API_KEY: ${{ secrets.GOOGLE_TRANSLATE_API_KEY }}
      
      - name: Update Indexes (${{ matrix.amc_tier }})
        run: |
          python -m phase_4_extended_coverage.scraper.update_indexes \\
            --tier ${{ matrix.amc_tier }} \\
            --vector-db chroma
        env:
          VECTOR_DB_API_KEY: ${{ secrets.VECTOR_DB_API_KEY }}
      
      - name: Validate Tier (${{ matrix.amc_tier }})
        run: |
          python -m phase_4_extended_coverage.scraper.validate_tier \\
            --tier ${{ matrix.amc_tier }}
      
      - name: Invalidate Cache (all tiers after final)
        if: matrix.amc_tier == 'tier4'
        run: |
          python -m phase_4_extended_coverage.cache.invalidate_all
        env:
          REDIS_URL: ${{ secrets.REDIS_URL }}
      
      - name: Upload logs to S3
        if: always()
        run: |
          aws s3 cp logs/ s3://${{ secrets.AWS_BUCKET }}/phase-4-logs/$(date +%Y-%m-%d)/ --recursive
      
      - name: Notify Slack (success)
        if: success() && matrix.amc_tier == 'tier4'
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Phase 4 Daily Corpus Refresh Completed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Phase 4: Extended Coverage (38+ URLs)*\\n
                    Time: $(date -u)\\n
                    Status: SUCCESS\\n
                    AMC Tiers: 4 (T1: 5 + T2: 7 + T3: 11 + T4: 3 = 26+ AMCs + categories)\\n
                    Languages: English + Hindi"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Notify Slack (failure)
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "❌ Phase 4 Daily Corpus Refresh FAILED",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Phase 4: Extended Coverage*\\n
                    Time: $(date -u)\\n
                    Status: FAILED\\n
                    Tier: ${{ matrix.amc_tier }}\\n
                    Logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
"""

# Scraper configuration for extended URLs
SCRAPER_CONFIG_PHASE4 = {
    "phase": 4,
    "name": "Extended Coverage Scraper",
    "description": "Scrapes 38+ Groww AMC URLs with multi-language support",
    
    "urls_config": {
        "total_urls": 38,
        "tier1": 5,      # Large AMCs (HDFC, ICICI, SBI, Axis, Kotak)
        "tier2": 7,      # Mid-cap (Motilal, UTI, Nippon, Aditya, Invesco, ICICI Pru, Canara)
        "tier3": 11,     # Emerging (Quantum, DSP, Tata, Franklin, PGIM, Bandhan, Vanguard, Principal, Bajaj, BOI AXA, Mahindra)
        "tier4": 3,      # Sector/category (Value, Money Market, International)
    },
    
    "scraping": {
        "concurrent_requests": 5,
        "timeout_per_url": 30,
        "max_retries": 3,
        "retry_backoff": [5, 15, 45],
        "request_delay": 0.5,  # Seconds between requests (rate limiting)
        "check_last_modified": True,
        "batch_processing": 5,  # Process 5 URLs at a time
    },
    
    "chunking": {
        "min_tokens": 300,
        "max_tokens": 500,
        "overlap_tokens": 50,
    },
    
    "embedding": {
        "model": "sentence-transformers/all-mpnet-base-v2",
        "dimension": 768,
        "batch_size": 100,
        "languages": ["en", "hi"],  # Generate embeddings for both
    },
    
    "translation": {
        "enabled": True,
        "service": "google_translate",
        "target_languages": ["hi"],  # Translate English chunks to Hindi
        "cache_ttl": 86400 * 30,  # 30 days
    },
    
    "index_update": {
        "vector_db": "chroma",
        "rebuild_bm25": True,
        "update_metadata": True,
        "invalidate_cache": True,
    },
    
    "monitoring": {
        "log_level": "INFO",
        "metrics_enabled": True,
        "alert_on_failure": True,
        "slack_notifications": True,
    },
    
    "validation": {
        "verify_chunk_count": True,
        "verify_embeddings": True,
        "verify_translations": True,
        "min_chunks_expected": 300,
        "max_chunks_expected": 500,
    },
}


# Requirements for Phase 4
REQUIREMENTS_PHASE4 = """
# Phase 4: Extended Coverage & Multi-Language Support

# From Phase 3
chromadb>=0.5.0
requests>=2.31.0
flask>=3.0.0
numpy>=1.24.0
pandas>=1.5.0
pytest>=7.0.0

# Phase 4 additions
google-cloud-translate>=3.10.0  # For Hindi translation
flask-cors>=4.0.0               # CORS support for multi-language UI
pyyaml>=6.0                     # Configuration management
regex>=2023.0                   # Advanced regex for filtering

# Caching
redis>=4.5.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0

# Monitoring
python-dotenv>=1.0.0
