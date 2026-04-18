# HTML Parser and Metadata Extraction

import hashlib
import logging
import json
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class HTMLParser:
    """Parse HTML from Groww AMC pages and extract metadata"""
    
    def __init__(self):
        self.required_fields = [
            "scheme_name",
            "scheme_isin",
            "amc_name",
            "expense_ratio",
        ]
    
    def parse_amc_page(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse AMC page HTML and extract schemes/metadata"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract AMC name from URL
            amc_name = self._extract_amc_name(url)
            
            # Extract scheme data (placeholder - customize based on actual HTML structure)
            schemes = self._extract_schemes(soup, url, amc_name)
            
            # Extract general page metadata
            page_metadata = {
                "url": url,
                "amc_name": amc_name,
                "page_title": soup.title.string if soup.title else "Unknown",
                "scraped_datetime": self._get_iso_timestamp(),
                "content_hash": self.calculate_content_hash(html_content),
                "schemes": schemes,
            }
            
            logger.info(f"Parsed {len(schemes)} schemes from {amc_name}")
            return page_metadata
        
        except Exception as e:
            logger.error(f"Error parsing HTML for {url}: {str(e)}")
            return {"error": str(e), "url": url}
    
    def _extract_amc_name(self, url: str) -> str:
        """Extract AMC name from URL"""
        try:
            # URL pattern: https://groww.in/mutual-funds/amc/{amc-name}
            match = re.search(r'/amc/([^/]+)', url)
            if match:
                amc_name = match.group(1).replace('-mutual-funds', '').replace('-', ' ').title()
                return amc_name
        except Exception as e:
            logger.error(f"Error extracting AMC name from {url}: {str(e)}")
        
        return "Unknown"
    
    def _extract_schemes(self, soup: BeautifulSoup, url: str, amc_name: str) -> List[Dict]:
        """Extract scheme information from parsed HTML"""
        schemes = []
        
        try:
            # Placeholder: Customize based on actual Groww HTML structure
            # This is a generic pattern that should be updated with actual selectors
            
            # Look for scheme tables or cards
            scheme_elements = soup.find_all('div', class_=re.compile('scheme|fund', re.I))
            
            for element in scheme_elements:
                try:
                    scheme_data = {
                        "scheme_name": self._extract_text(element, ['h2', 'h3', 'a']),
                        "scheme_isin": self._extract_isin(element),
                        "expense_ratio": self._extract_expense_ratio(element),
                        "amc_name": amc_name,
                        "source_url": url,
                        "category": self._extract_category(element),
                    }
                    
                    # Only add if has required fields
                    if scheme_data.get("scheme_name"):
                        schemes.append(scheme_data)
                
                except Exception as e:
                    logger.debug(f"Error extracting scheme: {str(e)}")
                    continue
        
        except Exception as e:
            logger.warning(f"Error extracting schemes from {url}: {str(e)}")
        
        return schemes
    
    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text from element using selectors"""
        for selector in selectors:
            found = element.find(selector)
            if found and found.string:
                return found.string.strip()
        return ""
    
    def _extract_isin(self, element) -> str:
        """Extract ISIN from element"""
        text = element.get_text()
        isin_match = re.search(r'INF[A-Z0-9]{9}', text)
        return isin_match.group(0) if isin_match else ""
    
    def _extract_expense_ratio(self, element) -> str:
        """Extract expense ratio"""
        text = element.get_text()
        ratio_match = re.search(r'(\d+\.?\d*)\s*%\s*(?:p\.a|pa)', text, re.I)
        return ratio_match.group(1) if ratio_match else ""
    
    def _extract_category(self, element) -> str:
        """Extract fund category"""
        text = element.get_text()
        categories = [
            'Large Cap', 'Mid Cap', 'Small Cap', 'Multi Cap', 'ELSS',
            'Liquid', 'Overnight', 'Short Duration', 'Debt', 'Money Market',
            'Gilt', 'Index', 'Sectoral'
        ]
        for category in categories:
            if category.lower() in text.lower():
                return category
        return ""
    
    def _get_iso_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format"""
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Fix common encoding issues
        text = text.encode('utf-8', 'ignore').decode('utf-8')
        return text
