# Validation Framework

import logging
from typing import Dict, List, Any
from .config import ALERT_CONFIG

logger = logging.getLogger(__name__)


class Validator:
    """Validate scraping results"""
    
    def validate_scrape(self, parse_results: List[Dict]) -> Dict[str, Any]:
        """Validate overall scrape results"""
        validation_results = {
            "overall": True,
            "checks": {},
            "warnings": [],
            "errors": [],
        }
        
        # Check 1: Document count
        if len(parse_results) == 0:
            validation_results["errors"].append("No documents parsed")
            validation_results["overall"] = False
        else:
            validation_results["checks"]["document_count"] = len(parse_results)
        
        # Check 2: Required fields presence
        for idx, doc in enumerate(parse_results):
            if "error" in doc:
                validation_results["warnings"].append(f"Document {idx} has error: {doc['error']}")
            else:
                # Verify required fields
                schemes_count = len(doc.get("schemes", []))
                validation_results["checks"][f"doc_{idx}_schemes"] = schemes_count
                
                if schemes_count == 0:
                    validation_results["warnings"].append(
                        f"Document {idx} ({doc.get('url')}) has no schemes"
                    )
        
        # Check 3: Overall validation
        if len(validation_results["errors"]) > 0:
            validation_results["overall"] = False
        
        logger.info(f"Validation results: {validation_results}")
        return validation_results
    
    def validate_chunk_count(self, current_count: int, baseline_count: int, 
                           tolerance: float = 0.1) -> bool:
        """Validate chunk count hasn't deviated significantly from baseline"""
        if baseline_count == 0:
            return True  # No baseline to compare
        
        deviation = abs(current_count - baseline_count) / baseline_count
        
        if deviation > tolerance:
            logger.warning(f"Chunk count deviation: {deviation:.1%} (current: {current_count}, baseline: {baseline_count})")
            return False
        
        return True
    
    def validate_required_fields(self, data: Dict) -> bool:
        """Validate document has required fields"""
        required_fields = ["scheme_name", "amc_name", "source_url"]
        
        for field in required_fields:
            if field not in data or not data[field]:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True


class HealthChecker:
    """Health check functions"""
    
    @staticmethod
    def check_url_reachability(url: str) -> bool:
        """Check if URL is reachable"""
        try:
            import requests
            response = requests.head(url, timeout=5)
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.warning(f"URL {url} not reachable: {str(e)}")
            return False
    
    @staticmethod
    def check_content_quality(html_content: str, required_patterns: List[str]) -> bool:
        """Check if HTML contains expected patterns"""
        for pattern in required_patterns:
            if pattern.lower() not in html_content.lower():
                logger.warning(f"Content doesn't contain expected pattern: {pattern}")
                return False
        
        return True
