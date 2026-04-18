# Main Scraping Service Entry Point

import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Tuple

from .config import GROWW_AMC_URLS, HTTP_CONFIG, RUN_CONFIG
from .database import DatabaseManager
from .fetcher import ScrapeClient
from .parser import HTMLParser
from .validator import Validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScraperService:
    """Main scraping service orchestrator"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.client = ScrapeClient()
        self.parser = HTMLParser()
        self.validator = Validator()
        self.run_id = self._generate_run_id()
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID with timestamp"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{RUN_CONFIG['run_id_prefix']}{timestamp}"
    
    async def run_daily_scrape(self) -> Dict:
        """Main orchestrator for daily scrape job"""
        logger.info(f"[{self.run_id}] Starting daily scrape at {datetime.utcnow()}")
        
        try:
            # Initialize run in database
            self.db.initialize_run(self.run_id)
            
            # Fetch all URLs
            fetch_results = await self._fetch_phase()
            
            # Parse and extract metadata
            parse_results = self._parse_phase(fetch_results)
            
            # Validation
            validation_results = self._validate_phase(parse_results)
            
            # Store raw HTML in staging
            storage_results = self._storage_phase(fetch_results)
            
            # Update run status
            self.db.finalize_run(self.run_id, "success", {
                "urls_processed": len(fetch_results),
                "chunks_created": len(parse_results),
                "validation_status": validation_results,
            })
            
            logger.info(f"[{self.run_id}] Scrape completed successfully")
            return {
                "run_id": self.run_id,
                "status": "success",
                "summary": {
                    "urls_total": len(GROWW_AMC_URLS),
                    "urls_processed": len(fetch_results),
                    "parse_results": len(parse_results),
                    "validation_passed": validation_results["overall"],
                }
            }
        
        except Exception as e:
            logger.error(f"[{self.run_id}] Scrape failed: {str(e)}", exc_info=True)
            self.db.finalize_run(self.run_id, "failed", {"error": str(e)})
            return {
                "run_id": self.run_id,
                "status": "failed",
                "error": str(e),
            }
    
    async def _fetch_phase(self) -> List[Tuple[str, str, int]]:
        """Fetch all URLs with retry logic"""
        logger.info(f"[{self.run_id}] Starting fetch phase for {len(GROWW_AMC_URLS)} URLs")
        
        results = []
        for url in GROWW_AMC_URLS:
            try:
                # Check Last-Modified header (conditional fetch)
                last_modified = self.db.get_last_modified_date(url)
                
                # Fetch URL
                response_text, status_code = await self.client.fetch_url(url)
                
                if status_code == 200:
                    results.append((url, response_text, status_code))
                    logger.info(f"[{self.run_id}] ✓ Fetched: {url}")
                    
                    # Update URL health
                    content_hash = self.parser.calculate_content_hash(response_text)
                    self.db.update_url_health(url, status_code, content_hash)
                
                else:
                    logger.warning(f"[{self.run_id}] ✗ Failed: {url} (Status: {status_code})")
                    self.db.update_url_health(url, status_code, None)
            
            except Exception as e:
                logger.error(f"[{self.run_id}] Error fetching {url}: {str(e)}")
                self.db.update_url_health(url, None, None, error=str(e))
        
        logger.info(f"[{self.run_id}] Fetch phase complete: {len(results)}/{len(GROWW_AMC_URLS)} URLs succeeded")
        return results
    
    def _parse_phase(self, fetch_results: List[Tuple[str, str, int]]) -> List[Dict]:
        """Parse HTML and extract metadata"""
        logger.info(f"[{self.run_id}] Starting parse phase")
        
        parse_results = []
        for url, html_content, status_code in fetch_results:
            try:
                # Parse HTML
                parsed_data = self.parser.parse_amc_page(html_content, url)
                parse_results.append(parsed_data)
                logger.info(f"[{self.run_id}] Parsed: {url} → {len(parsed_data.get('schemes', []))} schemes found")
            
            except Exception as e:
                logger.error(f"[{self.run_id}] Error parsing {url}: {str(e)}")
        
        logger.info(f"[{self.run_id}] Parse phase complete: {len(parse_results)} documents parsed")
        return parse_results
    
    def _validate_phase(self, parse_results: List[Dict]) -> Dict:
        """Validate parsed results"""
        logger.info(f"[{self.run_id}] Starting validation phase")
        
        validation_results = self.validator.validate_scrape(parse_results)
        logger.info(f"[{self.run_id}] Validation complete: {validation_results}")
        
        return validation_results
    
    def _storage_phase(self, fetch_results: List[Tuple[str, str, int]]) -> Dict:
        """Store raw HTML in staging table"""
        logger.info(f"[{self.run_id}] Starting storage phase")
        
        stored_count = 0
        for url, html_content, status_code in fetch_results:
            try:
                content_hash = self.parser.calculate_content_hash(html_content)
                self.db.store_raw_html(self.run_id, url, html_content, status_code, content_hash)
                stored_count += 1
            
            except Exception as e:
                logger.error(f"[{self.run_id}] Error storing {url}: {str(e)}")
        
        logger.info(f"[{self.run_id}] Storage phase complete: {stored_count} documents stored")
        return {"stored": stored_count}


async def run_daily_scrape():
    """Entry point for daily scrape (CLI)"""
    service = ScraperService()
    result = await service.run_daily_scrape()
    
    # Print summary
    if result["status"] == "success":
        summary = result["summary"]
        print(f"\n✅ Scrape Successful")
        print(f"   URLs Total: {summary['urls_total']}")
        print(f"   URLs Processed: {summary['urls_processed']}")
        print(f"   Documents Parsed: {summary['parse_results']}")
        print(f"   Validation: {'PASSED' if summary['validation_passed'] else 'FAILED'}")
    else:
        print(f"\n❌ Scrape Failed: {result['error']}")
    
    return result


if __name__ == "__main__":
    # Run scraper
    result = asyncio.run(run_daily_scrape())
    sys.exit(0 if result["status"] == "success" else 1)
