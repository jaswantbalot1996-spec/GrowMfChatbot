# Scraping Configuration

import os
from datetime import datetime

# URLs Configuration
GROWW_AMC_URLS = [
    "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
    "https://groww.in/mutual-funds/amc/icici-mutual-funds",
    "https://groww.in/mutual-funds/amc/sbi-mutual-funds",
    "https://groww.in/mutual-funds/amc/axis-mutual-funds",
    "https://groww.in/mutual-funds/amc/kotak-mutual-funds",
    "https://groww.in/mutual-funds/amc/wipro-mutual-funds",
    "https://groww.in/mutual-funds/amc/sundaram-mutual-funds",
    "https://groww.in/mutual-funds/amc/tata-mutual-funds",
    "https://groww.in/mutual-funds/amc/motilal-oswal-mutual-funds",
    "https://groww.in/mutual-funds/amc/mirae-asset-mutual-funds",
    "https://groww.in/mutual-funds/amc/franklin-templeton-mutual-funds",
    "https://groww.in/mutual-funds/amc/reliance-mutual-funds",
    "https://groww.in/mutual-funds/amc/jm-financial-mutual-funds",
    "https://groww.in/mutual-funds/amc/idfc-mutual-funds",
    "https://groww.in/mutual-funds/amc/aditya-birla-mutual-funds",
]

# HTTP Configuration
HTTP_CONFIG = {
    "timeout_per_url": 30,  # seconds
    "max_retries": 3,
    "retry_backoff": [5, 15, 45],  # exponential backoff in seconds
    "concurrent_requests": 3,  # max parallel requests
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Scraper Configuration
SCRAPER_CONFIG = {
    "batch_size": 100,  # for batch processing
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "check_last_modified": True,  # conditional fetch based on HTTP headers
}

# Chunking Configuration (Phase 2)
CHUNK_CONFIG = {
    "min_tokens": 300,
    "max_tokens": 500,
    "overlap_tokens": 50,
}

# Database Configuration
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/groww_db"),
    "pool_size": 5,
    "max_overflow": 10,
    "echo": False,  # Set to True for SQL logging
}

# Run Configuration
RUN_CONFIG = {
    "run_id_prefix": "scrape_",
    "timestamp_format": "%Y-%m-%dT%H:%M:%SZ",
}

# Alert Configuration
ALERT_CONFIG = {
    "failure_threshold": 2,  # alert after 2+ URL failures
    "consecutive_failure_limit": 3,  # mark URL as 'down' after 3 failures
}
