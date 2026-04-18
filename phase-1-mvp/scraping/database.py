# Database Operations for Scraping

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

import psycopg2
from psycopg2 import sql

from .config import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self):
        self.db_url = DATABASE_CONFIG["url"]
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            logger.info("✓ Database connected")
        except Exception as e:
            logger.error(f"✗ Database connection failed: {str(e)}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("✓ Database disconnected")
    
    def initialize_run(self, run_id: str) -> None:
        """Initialize new scrape run record"""
        try:
            if not self.conn:
                self.connect()
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO scrape_runs (run_id, run_datetime, urls_total, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (run_id) DO NOTHING
                """, (run_id, datetime.utcnow(), 15, 'in_progress'))
                self.conn.commit()
                logger.info(f"Initialized run: {run_id}")
        except Exception as e:
            logger.error(f"Error initializing run: {str(e)}")
            raise
    
    def finalize_run(self, run_id: str, status: str, summary: Dict[str, Any]) -> None:
        """Finalize scrape run record"""
        try:
            if not self.conn:
                self.connect()
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE scrape_runs
                    SET status = %s, 
                        urls_success = %s,
                        duration_seconds = EXTRACT(EPOCH FROM (NOW() - run_datetime))::INTEGER,
                        error_message = %s
                    WHERE run_id = %s
                """, (
                    status,
                    summary.get('urls_processed', 0),
                    summary.get('error') if status == 'failed' else None,
                    run_id
                ))
                self.conn.commit()
                logger.info(f"Finalized run: {run_id} with status: {status}")
        except Exception as e:
            logger.error(f"Error finalizing run: {str(e)}")
            raise
    
    def get_last_modified_date(self, url: str) -> Optional[str]:
        """Get last modified date for URL"""
        try:
            if not self.conn:
                self.connect()
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT last_modified_date FROM url_health WHERE url = %s
                """, (url,))
                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.debug(f"Error fetching last modified date: {str(e)}")
            return None
    
    def update_url_health(self, url: str, status_code: Optional[int], 
                          content_hash: Optional[str], error: Optional[str] = None) -> None:
        """Update URL health status"""
        try:
            if not self.conn:
                self.connect()
            
            consecutive_failures = 0
            health_status = 'healthy'
            
            if status_code and 200 <= status_code < 300:
                # Success
                consecutive_failures = 0
                health_status = 'healthy'
            elif status_code:
                # Failure
                health_status = 'degraded' if status_code in [429, 502, 503] else 'down'
                consecutive_failures = (self._get_consecutive_failures(url) or 0) + 1
            else:
                # Network error
                health_status = 'down'
                consecutive_failures = (self._get_consecutive_failures(url) or 0) + 1
            
            with self.conn.cursor() as cur:
                amc_name = self._extract_amc_from_url(url)
                
                cur.execute("""
                    INSERT INTO url_health 
                    (url, amc_name, last_fetch_datetime, last_fetch_status, 
                     content_hash, consecutive_failures, health_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        last_fetch_datetime = EXCLUDED.last_fetch_datetime,
                        last_fetch_status = EXCLUDED.last_fetch_status,
                        content_hash = COALESCE(EXCLUDED.content_hash, url_health.content_hash),
                        consecutive_failures = EXCLUDED.consecutive_failures,
                        health_status = EXCLUDED.health_status,
                        updated_at = NOW()
                """, (url, amc_name, datetime.utcnow(), status_code, 
                      content_hash, consecutive_failures, health_status))
                self.conn.commit()
                logger.debug(f"Updated health for {url}: {health_status}")
        except Exception as e:
            logger.error(f"Error updating URL health: {str(e)}")
    
    def store_raw_html(self, run_id: str, url: str, html_content: str, 
                      status_code: int, content_hash: str) -> None:
        """Store raw HTML in staging table"""
        try:
            if not self.conn:
                self.connect()
            
            # Truncate HTML content if too large (max 16MB for LONGTEXT)
            if len(html_content) > 16_000_000:
                logger.warning(f"HTML content for {url} exceeds limit, truncating...")
                html_content = html_content[:16_000_000]
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO scrape_html_staging 
                    (run_id, url, raw_html, fetch_status, content_hash)
                    VALUES (%s, %s, %s, %s, %s)
                """, (run_id, url, html_content, status_code, content_hash))
                self.conn.commit()
                logger.debug(f"Stored raw HTML for {url} ({len(html_content)} bytes)")
        except Exception as e:
            logger.error(f"Error storing raw HTML: {str(e)}")
            raise
    
    def _get_consecutive_failures(self, url: str) -> Optional[int]:
        """Get consecutive failures count for URL"""
        try:
            if not self.conn:
                self.connect()
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT consecutive_failures FROM url_health WHERE url = %s
                """, (url,))
                result = cur.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.debug(f"Error fetching consecutive failures: {str(e)}")
            return 0
    
    def _extract_amc_from_url(self, url: str) -> str:
        """Extract AMC name from URL"""
        import re
        try:
            match = re.search(r'/amc/([^/]+)', url)
            if match:
                return match.group(1).replace('-mutual-funds', '').replace('-', ' ').title()
        except:
            pass
        return "Unknown"
