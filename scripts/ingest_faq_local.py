#!/usr/bin/env python
"""
Create and ingest sample FAQ data into Chroma Cloud
This loads pre-made FAQ content directly without fetching from URLs
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment
env_path = os.path.join(os.path.dirname(__file__), '..', 'phase_3_llm_integration', '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Import Chroma
try:
    import chromadb
    from chromadb.config import Settings
    logger.info("✓ Chromadb imported")
except Exception as e:
    logger.error(f"Failed to import chromadb: {e}")
    sys.exit(1)

# Sample FAQ data about mutual funds
SAMPLE_FAQ_DATA = [
    {
        "id": "faq_001",
        "content": "NAV stands for Net Asset Value. It is the per-unit value of a mutual fund calculated as: (Total Assets - Total Liabilities) / Number of Units. NAV is calculated at the end of each trading day. You buy/sell mutual fund units at the NAV of that day. Higher past NAV doesn't mean better performance - focus on returns and expense ratio instead.",
        "amc_name": "General",
        "scheme_name": "NAV Definition",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_002",
        "content": "An expense ratio is the annual cost charged by a mutual fund as a percentage of your investment. It includes management fees, administrative costs, and operational expenses. Lower expense ratios mean more of your money goes toward investments. Direct plans have lower expense ratios compared to regular plans because they save on commission costs.",
        "amc_name": "General",
        "scheme_name": "Expense Ratio",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_003",
        "content": "ELSS (Equity Linked Savings Scheme) is a mutual fund category that offers tax deduction under Section 80C of the Income Tax Act. You can invest up to ₹1.5 lakhs in a financial year. ELSS funds have a mandatory lock-in period of 3 years. They invest mostly in equity, providing potential for long-term growth. Popular ELSS funds: HDFC ELSS Tax Saver, Axis ELSS Tax Saver, Aditya Birla Sun Life ELSS Tax Saver.",
        "amc_name": "General",
        "scheme_name": "ELSS Tax Saver",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_004",
        "content": "Exit load is a charge levied when you sell/redeem mutual fund units before a specified period. It is typically 1-2% of the redemption amount. Some funds have no exit load. ELSS funds don't have exit load after 3-year lock-in period. Direct plans have lower or no exit load compared to regular plans.",
        "amc_name": "General",
        "scheme_name": "Exit Load",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_005",
        "content": "SIP (Systematic Investment Plan) is an investment method where you invest a fixed amount regularly (daily/weekly/monthly). SIP advantages: 1) Rupee cost averaging - you buy more units when price is low and fewer when price is high, 2) Disciplined investing, 3) Lower lump sum requirement, 4) Power of compounding. Minimum SIP: ₹100-500 depending on fund.",
        "amc_name": "General",
        "scheme_name": "Systematic Investment Plan",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_006",
        "content": "Mutual funds are categorized into: 1) Equity Funds - for growth, suitable for long-term investment with high risk appetite. Returns depend on stock market performance. 2) Debt Funds - provide stable income with lower risk. 3) Hybrid Funds - balanced mix of equity and debt. 4) Liquid Funds - very low risk, suitable for short-term parking of money. 5) Money Market Funds - ultra-safe with instant liquidity.",
        "amc_name": "General",
        "scheme_name": "Fund Categories",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_007",
        "content": "A systematic withdrawal plan (SWP) is a method to withdraw a fixed amount from your mutual fund investment at regular intervals (monthly, quarterly, or yearly). SWP is useful for retirees who need regular income. Unlike committing to SIP, with SWP you can pause or adjust withdrawals as per your needs. The withdrawn amount is the NAV at the time of withdrawal.",
        "amc_name": "General",
        "scheme_name": "Systematic Withdrawal Plan",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_008",
        "content": "The difference between direct and regular plans: Direct plans have no middleman (distributor), so expense ratio is lower, typically by 0.5-1% per year. Regular plans are sold through distributors who charge commission. Both invest in the same portfolio, but direct plans give you better returns due to lower costs. Groww recommends direct plans for cost-conscious investors.",
        "amc_name": "General",
        "scheme_name": "Direct vs Regular Plans",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_009",
        "content": "Asset Under Management (AUM) refers to the total value of assets managed by a mutual fund. A higher AUM indicates the fund is managing more money from investors. However, AUM alone is not a measure of fund quality. A newer fund with lower AUM can sometimes outperform an older fund with high AUM. Focus on fund performance, management quality, and expense ratio rather than AUM alone.",
        "amc_name": "General",
        "scheme_name": "Asset Under Management",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_010",
        "content": "Tax-Saving Funds (ELSS) are mutual funds that provide tax benefits under Section 80C of the Income Tax Act. The key features: 1) Invest up to ₹1.5 lakhs per financial year to get full tax benefit. 2) 3-year mandatory lock-in period. 3) No exit load after lock-in expires. 4) Mostly invested in equities for growth. 5) Can file ITR income tax returns with ELSS investment.",
        "amc_name": "General",
        "scheme_name": "Tax Saving Funds",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_011",
        "content": "Dividend yield funds aim to provide regular income through dividends from stocks that pay dividends regularly. These are suitable for income-seeking investors. The dividend is distributed to investors at regular intervals (monthly, quarterly). A dividend fund's NAV may fluctuate based on stock market changes, but dividends provide regular cash flow. Tax treatment: Dividend Distribution Tax (DDT) is now paid by fund houses, not investors.",
        "amc_name": "General",
        "scheme_name": "Dividend Yield Funds",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_012",
        "content": "A lump sum investment is a one-time investment of a larger amount instead of regular small investments through SIP. Lump sum is suitable if you have a bulk amount to invest and market conditions are favorable. It can provide higher returns if invested at market bottoms. However, timing the market is difficult. SIP is often preferred for its disciplined approach and lower market timing risk.",
        "amc_name": "General",
        "scheme_name": "Lump Sum Investment",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_013",
        "content": "Mid-cap funds invest primarily in mid-capitalization stocks (companies with market cap typically between ₹500 crore and ₹15,000 crore). Mid-cap stocks offer growth potential higher than large-cap but with more volatility. Mid-cap funds are suitable for investors with moderate-to-high risk appetite and longer investment horizon (5+ years). They can provide returns higher than large-cap funds during bull markets.",
        "amc_name": "General",
        "scheme_name": "Mid-Cap Funds",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_014",
        "content": "Small-cap funds invest in small-capitalization stocks (typically market cap below ₹500 crore). Small-cap stocks have high growth potential but also higher volatility and risk. Small-cap funds are suitable for risk-appetite investors with 7-10 year investment horizon. They can deliver exceptional returns during favorable market periods but may underperform during market downturns.",
        "amc_name": "General",
        "scheme_name": "Small-Cap Funds",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_015",
        "content": "Liquid funds invest in debt instruments with very short maturity (upto 91 days). They offer high liquidity with capital preservation as the primary goal. Liquid funds are ideal for: 1) Parking emergency funds. 2) Temporary cash during market downturns. 3) Keeping money while waiting to invest in equity funds. Liquid funds are safer than savings accounts but provide better returns than bank savings rates.",
        "amc_name": "General",
        "scheme_name": "Liquid Funds",
        "source": "https://www.groww.in/learn"
    },
    {
        "id": "faq_016",
        "content": "Hybrid funds allocate investments across both equity and debt instruments. Asset allocation varies by fund - some may be 60% equity 40% debt, others 70% equity 30% debt. Hybrid funds offer a balanced approach suitable for investors seeking growth with some downside protection. They are less volatile than pure equity funds but provide better growth potential than pure debt funds.",
        "amc_name": "General",
        "scheme_name": "Hybrid Funds",
        "source": "https://www.groww.in/learn"
    },
]

def create_chroma_client():
    """Create connection to Chroma Cloud"""
    try:
        chroma_api_key = os.environ.get("CHROMA_API_KEY")
        chroma_tenant = os.environ.get("CHROMA_TENANT")
        chroma_database = os.environ.get("CHROMA_DATABASE")
        
        if not all([chroma_api_key, chroma_tenant, chroma_database]):
            raise ValueError("Missing Chroma Cloud configuration in .env")
        
        client = chromadb.HttpClient(
            host="api.trychroma.com",
            port=8000,
            headers={"x-chroma-token": chroma_api_key},
            tenant_name=chroma_tenant,
            database_name=chroma_database,
            ssl=True
        )
        logger.info("✓ Connected to Chroma Cloud")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Chroma Cloud: {e}")
        raise

def ingest_faq_data():
    """Ingest sample FAQ data into Chroma"""
    try:
        client = create_chroma_client()
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name="groww_faq",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"✓ Using collection: groww_faq")
        
        # Prepare data for ingest
        ids = []
        documents = []
        metadatas = []
        
        for faq in SAMPLE_FAQ_DATA:
            ids.append(faq["id"])
            documents.append(faq["content"])
            metadatas.append({
                "amc_name": faq.get("amc_name", "General"),
                "scheme_name": faq.get("scheme_name", "General"),
                "source": faq.get("source", "https://www.groww.in/learn"),
                "content_hash": str(hash(faq["content"])),
                "chunk_index": 0
            })
        
        # Ingest to Chroma
        logger.info(f"Ingesting {len(ids)} FAQ documents...")
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"✓ Successfully ingested {len(ids)} documents")
        
        # Get collection count
        count = collection.count()
        logger.info(f"✓ Collection now has {count} total documents")
        
        return True
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Loading Sample FAQ Data into Chroma Cloud")
    logger.info("=" * 70)
    
    success = ingest_faq_data()
    
    if success:
        logger.info("=" * 70)
        logger.info("✓ FAQ database population complete!")
        logger.info("=" * 70)
        sys.exit(0)
    else:
        logger.error("Failed to populate FAQ database")
        sys.exit(1)
