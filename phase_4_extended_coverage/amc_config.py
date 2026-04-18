"""
Phase 4: Extended Coverage & Multi-Language Support
AMC Configuration (25-50 URLs)
All major Indian mutual fund houses
"""

# Extended AMC URL Configuration
AMC_CONFIG = {
    # TIER 1: All URLs (complete coverage)
    "tier1_large_amc": [
        {
            "name": "HDFC Mutual Funds",
            "amc_code": "hdfc",
            "url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 35,
            "active": True,
        },
        {
            "name": "ICICI Mutual Funds",
            "amc_code": "icici",
            "url": "https://groww.in/mutual-funds/amc/icici-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 30,
            "active": True,
        },
        {
            "name": "SBI Mutual Funds",
            "amc_code": "sbi",
            "url": "https://groww.in/mutual-funds/amc/sbi-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 32,
            "active": True,
        },
        {
            "name": "Axis Mutual Funds",
            "amc_code": "axis",
            "url": "https://groww.in/mutual-funds/amc/axis-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 28,
            "active": True,
        },
        {
            "name": "Kotak Mahindra Mutual Funds",
            "amc_code": "kotak",
            "url": "https://groww.in/mutual-funds/amc/kotak-mahindra-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 30,
            "active": True,
        },
    ],
    
    # TIER 2: Mid-cap AMCs
    "tier2_mid_amc": [
        {
            "name": "Motilal Oswal Mutual Funds",
            "amc_code": "motilal",
            "url": "https://groww.in/mutual-funds/amc/motilal-oswal-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 22,
            "active": True,
        },
        {
            "name": "UTI Mutual Funds",
            "amc_code": "uti",
            "url": "https://groww.in/mutual-funds/amc/uti-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 25,
            "active": True,
        },
        {
            "name": "Nippon India Mutual Funds",
            "amc_code": "nippon",
            "url": "https://groww.in/mutual-funds/amc/nippon-india-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 28,
            "active": True,
        },
        {
            "name": "Aditya Birla Sun Life",
            "amc_code": "aditya",
            "url": "https://groww.in/mutual-funds/amc/aditya-birla-sun-life-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 26,
            "active": True,
        },
        {
            "name": "Invesco Mutual Funds",
            "amc_code": "invesco",
            "url": "https://groww.in/mutual-funds/amc/invesco-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 20,
            "active": True,
        },
        {
            "name": "ICICI Prudent Mutual Funds",
            "amc_code": "icici_pru",
            "url": "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 24,
            "active": True,
        },
        {
            "name": "Canara Robeco Mutual Funds",
            "amc_code": "canara",
            "url": "https://groww.in/mutual-funds/amc/canara-robeco-mutual-funds",
            "region": "south",
            "fund_count_estimate": 18,
            "active": True,
        },
    ],
    
    # TIER 3: Emerging & Niche AMCs
    "tier3_emerging_amc": [
        {
            "name": "Quantum Mutual Funds",
            "amc_code": "quantum",
            "url": "https://groww.in/mutual-funds/amc/quantum-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 12,
            "active": True,
        },
        {
            "name": "DSP Mutual Funds",
            "amc_code": "dsp",
            "url": "https://groww.in/mutual-funds/amc/dsp-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 20,
            "active": True,
        },
        {
            "name": "Tata Mutual Funds",
            "amc_code": "tata",
            "url": "https://groww.in/mutual-funds/amc/tata-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 18,
            "active": True,
        },
        {
            "name": "Franklin Templeton Mutual Funds",
            "amc_code": "franklin",
            "url": "https://groww.in/mutual-funds/amc/franklin-templeton-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 25,
            "active": True,
        },
        {
            "name": "PGIM India Mutual Funds",
            "amc_code": "pgim",
            "url": "https://groww.in/mutual-funds/amc/pgim-india-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 15,
            "active": True,
        },
        {
            "name": "Bandhan Mutual Funds",
            "amc_code": "bandhan",
            "url": "https://groww.in/mutual-funds/amc/bandhan-mutual-funds",
            "region": "east",
            "fund_count_estimate": 14,
            "active": True,
        },
        {
            "name": "Vanguard India Mutual Funds",
            "amc_code": "vanguard",
            "url": "https://groww.in/mutual-funds/amc/vanguard-india-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 8,
            "active": True,
        },
        {
            "name": "Principal Mutual Funds",
            "amc_code": "principal",
            "url": "https://groww.in/mutual-funds/amc/principal-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 16,
            "active": True,
        },
        {
            "name": "Bajaj Finserv Mutual Funds",
            "amc_code": "bajaj",
            "url": "https://groww.in/mutual-funds/amc/bajaj-finserv-mutual-funds",
            "region": "west",
            "fund_count_estimate": 12,
            "active": True,
        },
        {
            "name": "BOI AXA Mutual Funds",
            "amc_code": "boi_axa",
            "url": "https://groww.in/mutual-funds/amc/boi-axa-mutual-funds",
            "region": "pan-india",
            "fund_count_estimate": 11,
            "active": True,
        },
        {
            "name": "Mahindra Mutual Funds",
            "amc_code": "mahindra",
            "url": "https://groww.in/mutual-funds/amc/mahindra-manulife-mutual-funds",
            "region": "west",
            "fund_count_estimate": 18,
            "active": True,
        },
    ],
    
    # TIER 4: Sector/Thematic Focus
    "tier4_sector_amc": [
        {
            "name": "ICICI Value Discover Fund",
            "amc_code": "value_discover",
            "url": "https://groww.in/mutual-funds/category/value-and-index-funds",
            "region": "pan-india",
            "fund_count_estimate": 5,
            "category": "value_index",
            "active": True,
        },
        {
            "name": "Groww Money Markets",
            "amc_code": "groww_mm",
            "url": "https://groww.in/mutual-funds/category/money-market-funds",
            "region": "pan-india",
            "fund_count_estimate": 8,
            "category": "money_market",
            "active": True,
        },
        {
            "name": "International Fund Pages",
            "amc_code": "intl_funds",
            "url": "https://groww.in/mutual-funds/category/international-funds",
            "region": "global",
            "fund_count_estimate": 12,
            "category": "international",
            "active": True,
        },
    ],
}

# Configuration for language support
LANGUAGE_CONFIG = {
    "default_language": "en",
    "supported_languages": ["en", "hi"],
    "language_names": {
        "en": "English",
        "hi": "हिंदी (Hindi)",
    },
    "translation_service": "google_translate",  # google_translate or azure_translator
    "auto_translate_chunks": True,  # Translate chunks on ingestion
    "cache_translations": True,  # Cache translations in DB
    "translation_cache_ttl": 86400 * 30,  # 30 days (seconds)
}

# Advanced filtering configuration
FILTER_CONFIG = {
    "risk_levels": {
        "low": ["Liquid", "Ultra Short Duration", "Short Duration", "Overnight"],
        "low_moderate": ["Medium Duration", "Conservative Allocation"],
        "moderate": ["Dynamic Bond", "Aggressive Allocation"],
        "moderate_high": ["Large Cap", "Multi Cap", "Dividend Yield"],
        "high": ["Mid Cap", "Small Cap", "Sector Specific", "Thematic"],
        "very_high": ["International", "Emerging Market"],
    },
    "categories": {
        "debt": ["Liquid", "Ultra Short", "Short Duration", "Medium Duration", "Long Duration", "Dynamic Bond"],
        "equity": ["Large Cap", "Mid Cap", "Small Cap", "Multi Cap", "ELSS", "Focused", "Value"],
        "hybrid": ["Conservative Allocation", "Balanced Allocation", "Aggressive Allocation"],
        "international": ["International", "Emerging Market", "Global"],
        "alternative": ["Gold", "Money Market"],
    },
    "aum_ranges": {
        "micro": {"min": 0, "max": 100, "label": "< ₹100 Cr"},
        "small": {"min": 100, "max": 500, "label": "₹100 Cr - ₹500 Cr"},
        "medium": {"min": 500, "max": 2000, "label": "₹500 Cr - ₹2000 Cr"},
        "large": {"min": 2000, "max": 10000, "label": "₹2000 Cr - ₹10000 Cr"},
        "mega": {"min": 10000, "max": float("inf"), "label": "> ₹10000 Cr"},
    },
    "performance_periods": ["1y", "3y", "5y", "10y", "since_launch"],
}

# Mobile optimization
MOBILE_CONFIG = {
    "enabled": True,
    "response_compression": True,
    "chunk_compression": "gzip",
    "cache_ttl": 3600,  # 1 hour
    "max_search_results": 5,  # Smaller on mobile
    "timeout_ms": 2000,  # Tight mobile timeout
    "offline_mode": True,  # Cache responses for offline access
}

def get_all_urls_flat():
    """Get all AMC URLs as flat list"""
    urls = []
    for tier in ["tier1_large_amc", "tier2_mid_amc", "tier3_emerging_amc", "tier4_sector_amc"]:
        urls.extend(AMC_CONFIG.get(tier, []))
    return urls

def get_url_count():
    """Get total URL count"""
    all_urls = get_all_urls_flat()
    return len(all_urls)

def get_urls_by_tier(tier_name):
    """Get URLs for specific tier"""
    return AMC_CONFIG.get(tier_name, [])

def get_urls_by_region(region):
    """Filter URLs by region"""
    all_urls = get_all_urls_flat()
    return [u for u in all_urls if u.get("region") == region or u.get("region") == "pan-india"]

def get_enabled_urls():
    """Get only active/enabled URLs"""
    all_urls = get_all_urls_flat()
    return [u for u in all_urls if u.get("active", True)]

# Example usage
if __name__ == "__main__":
    print(f"Total AMC URLs: {get_url_count()}")
    print(f"Enabled URLs: {len(get_enabled_urls())}")
    print(f"Supported Languages: {LANGUAGE_CONFIG['supported_languages']}")
    print(f"Risk Levels: {list(FILTER_CONFIG['risk_levels'].keys())}")
    print(f"Categories: {list(FILTER_CONFIG['categories'].keys())}")
