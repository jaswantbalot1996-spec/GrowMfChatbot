# Phase 1 Scraping Service - URLs Configuration

# 15 Groww AMC URLs for scraping (MVP Scope)
GROWW_AMC_URLS = {
    "HDFC": {
        "url": "https://groww.in/mutual-funds/amc/hdfc-mutual-funds",
        "name": "HDFC Mutual Funds",
        "schemes_expected": 20,  # Approximate
    },
    "ICICI": {
        "url": "https://groww.in/mutual-funds/amc/icici-mutual-funds",
        "name": "ICICI Mutual Funds",
        "schemes_expected": 18,
    },
    "SBI": {
        "url": "https://groww.in/mutual-funds/amc/sbi-mutual-funds",
        "name": "SBI Mutual Funds",
        "schemes_expected": 25,
    },
    "Axis": {
        "url": "https://groww.in/mutual-funds/amc/axis-mutual-funds",
        "name": "Axis Mutual Funds",
        "schemes_expected": 15,
    },
    "Kotak": {
        "url": "https://groww.in/mutual-funds/amc/kotak-mutual-funds",
        "name": "Kotak Mutual Funds",
        "schemes_expected": 12,
    },
    "Wipro": {
        "url": "https://groww.in/mutual-funds/amc/wipro-mutual-funds",
        "name": "Wipro Mutual Funds",
        "schemes_expected": 8,
    },
    "Sundaram": {
        "url": "https://groww.in/mutual-funds/amc/sundaram-mutual-funds",
        "name": "Sundaram Mutual Funds",
        "schemes_expected": 10,
    },
    "Tata": {
        "url": "https://groww.in/mutual-funds/amc/tata-mutual-funds",
        "name": "Tata Mutual Funds",
        "schemes_expected": 14,
    },
    "Motilal Oswal": {
        "url": "https://groww.in/mutual-funds/amc/motilal-oswal-mutual-funds",
        "name": "Motilal Oswal Mutual Funds",
        "schemes_expected": 11,
    },
    "Mirae Asset": {
        "url": "https://groww.in/mutual-funds/amc/mirae-asset-mutual-funds",
        "name": "Mirae Asset Mutual Funds",
        "schemes_expected": 10,
    },
    "Franklin Templeton": {
        "url": "https://groww.in/mutual-funds/amc/franklin-templeton-mutual-funds",
        "name": "Franklin Templeton Mutual Funds",
        "schemes_expected": 9,
    },
    "Reliance": {
        "url": "https://groww.in/mutual-funds/amc/reliance-mutual-funds",
        "name": "Reliance Mutual Funds",
        "schemes_expected": 16,
    },
    "JM Financial": {
        "url": "https://groww.in/mutual-funds/amc/jm-financial-mutual-funds",
        "name": "JM Financial Mutual Funds",
        "schemes_expected": 7,
    },
    "IDFC": {
        "url": "https://groww.in/mutual-funds/amc/idfc-mutual-funds",
        "name": "IDFC Mutual Funds",
        "schemes_expected": 9,
    },
    "Aditya Birla": {
        "url": "https://groww.in/mutual-funds/amc/aditya-birla-mutual-funds",
        "name": "Aditya Birla Mutual Funds",
        "schemes_expected": 13,
    },
}

# Extended list for Phase 3 (not used in MVP)
EXTENDED_AMC_URLS = {
    "L&T": {
        "url": "https://groww.in/mutual-funds/amc/l-and-t-mutual-funds",
        "name": "L&T Mutual Funds",
    },
    "DSP": {
        "url": "https://groww.in/mutual-funds/amc/dsp-mutual-funds",
        "name": "DSP Mutual Funds",
    },
    "Invesco": {
        "url": "https://groww.in/mutual-funds/amc/invesco-mutual-funds",
        "name": "Invesco Mutual Funds",
    },
    "Quantum": {
        "url": "https://groww.in/mutual-funds/amc/quantum-mutual-funds",
        "name": "Quantum Mutual Funds",
    },
    "Canara Robeco": {
        "url": "https://groww.in/mutual-funds/amc/canara-robeco-mutual-funds",
        "name": "Canara Robeco Mutual Funds",
    },
}


def get_amc_urls_for_phase(phase: str = "phase-1") -> Dict[str, str]:
    """Get URLs for specific phase"""
    if phase == "phase-1":
        return {k: v["url"] for k, v in GROWW_AMC_URLS.items()}
    elif phase == "phase-3":
        return {
            **{k: v["url"] for k, v in GROWW_AMC_URLS.items()},
            **{k: v["url"] for k, v in EXTENDED_AMC_URLS.items()},
        }
    else:
        return {k: v["url"] for k, v in GROWW_AMC_URLS.items()}
