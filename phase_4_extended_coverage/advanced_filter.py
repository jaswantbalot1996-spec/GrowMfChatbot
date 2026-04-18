"""
Phase 4: Advanced Filtering Module
Filters search results by risk level, category, AUM range, etc.
"""

import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """SEBI-mandated risk classifications"""
    LOW = "low"
    LOW_TO_MODERATE = "low_to_moderate"
    MODERATE = "moderate"
    MODERATE_TO_HIGH = "moderate_to_high"
    HIGH = "high"


class FundCategory(Enum):
    """Mutual fund categories"""
    EQUITY = "equity"
    DEBT = "debt"
    HYBRID = "hybrid"
    LIQUID = "liquid"
    MONEY_MARKET = "money_market"
    INTERNATIONAL = "international"
    COMMODITY = "commodity"
    GOVERNMENT_SECURITIES = "government_securities"


@dataclass
class FilterCriteria:
    """Filter criteria for search results"""
    # Risk filtering
    min_risk_level: Optional[RiskLevel] = None
    max_risk_level: Optional[RiskLevel] = None
    
    # Category filtering
    categories: Optional[List[FundCategory]] = None
    
    # AUM filtering (in crores)
    min_aum: Optional[float] = None
    max_aum: Optional[float] = None
    
    # Expense ratio filtering (in percentage)
    min_expense_ratio: Optional[float] = None
    max_expense_ratio: Optional[float] = None
    
    # Exit load filtering
    has_exit_load: Optional[bool] = None
    
    # Lock-in period filtering
    min_lockin_years: Optional[int] = None
    max_lockin_years: Optional[int] = None
    
    # Scheme name filter (regex)
    scheme_name_filter: Optional[str] = None
    
    # AMC code filter
    amc_codes: Optional[List[str]] = None


class AdvancedFilterEngine:
    """Filters chunks and results based on criteria"""
    
    # Risk level mapping for sorting
    RISK_ORDER = {
        RiskLevel.LOW: 1,
        RiskLevel.LOW_TO_MODERATE: 2,
        RiskLevel.MODERATE: 3,
        RiskLevel.MODERATE_TO_HIGH: 4,
        RiskLevel.HIGH: 5,
    }
    
    def __init__(self):
        """Initialize filter engine"""
        logger.info("Advanced Filter Engine initialized")
    
    def filter_chunks(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """
        Filter chunks based on criteria
        
        Args:
            chunks: List of chunks with metadata
            criteria: Filter criteria
        
        Returns:
            Filtered list of chunks
        """
        if not criteria:
            return chunks
        
        filtered = chunks
        
        # Apply each filter sequentially
        if criteria.min_risk_level or criteria.max_risk_level:
            filtered = self._filter_by_risk(filtered, criteria)
        
        if criteria.categories:
            filtered = self._filter_by_category(filtered, criteria)
        
        if criteria.min_aum is not None or criteria.max_aum is not None:
            filtered = self._filter_by_aum(filtered, criteria)
        
        if criteria.min_expense_ratio is not None or criteria.max_expense_ratio is not None:
            filtered = self._filter_by_expense_ratio(filtered, criteria)
        
        if criteria.has_exit_load is not None:
            filtered = self._filter_by_exit_load(filtered, criteria)
        
        if criteria.min_lockin_years is not None or criteria.max_lockin_years is not None:
            filtered = self._filter_by_lockin(filtered, criteria)
        
        if criteria.scheme_name_filter:
            filtered = self._filter_by_name(filtered, criteria)
        
        if criteria.amc_codes:
            filtered = self._filter_by_amc(filtered, criteria)
        
        logger.debug(f"Filtering: {len(chunks)} → {len(filtered)} chunks")
        return filtered
    
    def _filter_by_risk(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by risk level"""
        min_risk = self.RISK_ORDER.get(criteria.min_risk_level, 1)
        max_risk = self.RISK_ORDER.get(criteria.max_risk_level, 5)
        
        filtered = []
        for chunk in chunks:
            risk = chunk.get('metadata', {}).get('riskometer')
            if risk:
                risk_order = self.RISK_ORDER.get(risk, 3)
                if min_risk <= risk_order <= max_risk:
                    filtered.append(chunk)
            else:
                filtered.append(chunk)  # Include if risk not specified
        
        return filtered
    
    def _filter_by_category(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by fund category"""
        allowed_categories = {cat.value for cat in criteria.categories}
        
        filtered = []
        for chunk in chunks:
            category = chunk.get('metadata', {}).get('fund_category')
            if category in allowed_categories:
                filtered.append(chunk)
            elif not category:
                filtered.append(chunk)  # Include if category not specified
        
        return filtered
    
    def _filter_by_aum(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by Assets Under Management (in crores)"""
        filtered = []
        for chunk in chunks:
            aum_str = chunk.get('metadata', {}).get('aum')
            if aum_str:
                try:
                    # Parse AUM string (e.g., "₹5,000 Cr" → 5000)
                    aum_value = self._parse_aum(aum_str)
                    
                    if criteria.min_aum and aum_value < criteria.min_aum:
                        continue
                    if criteria.max_aum and aum_value > criteria.max_aum:
                        continue
                    
                    filtered.append(chunk)
                except Exception as e:
                    logger.warning(f"Failed to parse AUM: {aum_str} - {e}")
                    filtered.append(chunk)  # Include on parse error
            else:
                filtered.append(chunk)  # Include if AUM not specified
        
        return filtered
    
    def _filter_by_expense_ratio(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by expense ratio (in percentage)"""
        filtered = []
        for chunk in chunks:
            exp_ratio_str = chunk.get('metadata', {}).get('expense_ratio')
            if exp_ratio_str:
                try:
                    # Parse expense ratio (e.g., "0.50%" → 0.50)
                    exp_ratio = self._parse_percentage(exp_ratio_str)
                    
                    if criteria.min_expense_ratio and exp_ratio < criteria.min_expense_ratio:
                        continue
                    if criteria.max_expense_ratio and exp_ratio > criteria.max_expense_ratio:
                        continue
                    
                    filtered.append(chunk)
                except Exception as e:
                    logger.warning(f"Failed to parse expense ratio: {exp_ratio_str} - {e}")
                    filtered.append(chunk)
            else:
                filtered.append(chunk)
        
        return filtered
    
    def _filter_by_exit_load(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by exit load presence"""
        filtered = []
        for chunk in chunks:
            exit_load = chunk.get('metadata', {}).get('exit_load')
            has_exit_load = bool(exit_load and exit_load.lower() != 'nil')
            
            if criteria.has_exit_load == has_exit_load:
                filtered.append(chunk)
            elif criteria.has_exit_load is None:
                filtered.append(chunk)  # Include if no preference
        
        return filtered
    
    def _filter_by_lockin(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by lock-in period (in years)"""
        filtered = []
        for chunk in chunks:
            lockin_str = chunk.get('metadata', {}).get('lockin_period')
            if lockin_str:
                try:
                    # Parse lock-in (e.g., "3 years" → 3, "No lock-in" → 0)
                    lockin_years = self._parse_lockin(lockin_str)
                    
                    if criteria.min_lockin_years and lockin_years < criteria.min_lockin_years:
                        continue
                    if criteria.max_lockin_years and lockin_years > criteria.max_lockin_years:
                        continue
                    
                    filtered.append(chunk)
                except Exception as e:
                    logger.warning(f"Failed to parse lock-in: {lockin_str} - {e}")
                    filtered.append(chunk)
            else:
                filtered.append(chunk)
        
        return filtered
    
    def _filter_by_name(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by scheme name (regex)"""
        filtered = []
        try:
            pattern = re.compile(criteria.scheme_name_filter, re.IGNORECASE)
            for chunk in chunks:
                scheme_name = chunk.get('metadata', {}).get('scheme_name', '')
                if pattern.search(scheme_name):
                    filtered.append(chunk)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {criteria.scheme_name_filter} - {e}")
            filtered = chunks  # No filtering on error
        
        return filtered
    
    def _filter_by_amc(
        self,
        chunks: List[Dict],
        criteria: FilterCriteria
    ) -> List[Dict]:
        """Filter by AMC code"""
        if not criteria.amc_codes:
            return chunks
        
        allowed_amcs = {code.lower() for code in criteria.amc_codes}
        
        filtered = []
        for chunk in chunks:
            amc_code = chunk.get('metadata', {}).get('amc_code', '').lower()
            if amc_code in allowed_amcs:
                filtered.append(chunk)
        
        return filtered
    
    @staticmethod
    def _parse_aum(aum_str: str) -> float:
        """Parse AUM string to numeric value (in crores)"""
        # Extract numbers and multiplier (Cr, Lac, etc.)
        match = re.search(r'([\d,]+\.?\d*)\s*(Cr|Crore|Lac|Lakh)?', aum_str, re.IGNORECASE)
        if match:
            value = float(match.group(1).replace(',', ''))
            multiplier = match.group(2).lower() if match.group(2) else 'cr'
            
            if multiplier in ['cr', 'crore']:
                return value
            elif multiplier in ['lac', 'lakh']:
                return value / 100
            else:
                return value
        
        raise ValueError(f"Cannot parse AUM: {aum_str}")
    
    @staticmethod
    def _parse_percentage(pct_str: str) -> float:
        """Parse percentage string to numeric value"""
        match = re.search(r'([\d.]+)\s*%', pct_str)
        if match:
            return float(match.group(1))
        raise ValueError(f"Cannot parse percentage: {pct_str}")
    
    @staticmethod
    def _parse_lockin(lockin_str: str) -> int:
        """Parse lock-in period string to years"""
        if 'no lock' in lockin_str.lower() or 'none' in lockin_str.lower():
            return 0
        
        match = re.search(r'(\d+)\s*(?:year|yr)', lockin_str, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        raise ValueError(f"Cannot parse lock-in: {lockin_str}")


def create_filter_engine() -> AdvancedFilterEngine:
    """Factory function to create filter engine"""
    return AdvancedFilterEngine()


# Example usage
if __name__ == "__main__":
    filter_engine = create_filter_engine()
    
    # Test chunk
    test_chunks = [
        {
            "text": "HDFC Large-Cap has 0.50% expense ratio",
            "metadata": {
                "scheme_name": "HDFC Large-Cap Fund",
                "amc_code": "hdfc",
                "fund_category": "equity",
                "riskometer": RiskLevel.MODERATE,
                "expense_ratio": "0.50%",
                "aum": "₹50,000 Cr",
                "exit_load": "0.5% within 1 year",
                "lockin_period": "No lock-in",
            }
        }
    ]
    
    # Create filter criteria
    criteria = FilterCriteria(
        max_risk_level=RiskLevel.MODERATE,
        categories=[FundCategory.EQUITY],
        max_expense_ratio=1.0
    )
    
    # Apply filters
    filtered = filter_engine.filter_chunks(test_chunks, criteria)
    print(f"Filtered: {len(filtered)} chunks")
    print(f"Result: {filtered[0]['metadata']['scheme_name']}")
