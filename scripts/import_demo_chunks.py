import sys, os, json, time
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv

# Load environment variables from phase_3_llm_integration/.env so chroma client picks up keys
load_dotenv(os.path.join(os.getcwd(), 'phase_3_llm_integration', '.env'))

from phase_3_llm_integration.data_import import import_chunks_to_chroma_cloud
import numpy as np
from datetime import datetime

# Demo FAQ entries
faq_entries = [
    {
        'text': 'ELSS (Equity Linked Savings Scheme) is a mutual fund category that offers tax deduction under Section 80C. It has a mandatory lock-in period of 3 years.',
        'amc_name': 'Groww',
        'scheme_name': 'ELSS Demo Fund',
        'source_url': 'https://groww.in/faq/elss',
        'concepts': ['elss','tax','lock-in'],
    },
    {
        'text': 'NAV stands for Net Asset Value and is calculated as (Total Assets - Total Liabilities) / Number of Units. NAV is calculated daily.',
        'amc_name': 'Groww',
        'scheme_name': 'NAV Demo Fund',
        'source_url': 'https://groww.in/faq/nav',
        'concepts': ['nav','definition'],
    },
    {
        'text': 'Expense ratio is the annual fee charged by a mutual fund as a percentage of assets under management. Lower expense ratios are better for investors.',
        'amc_name': 'Groww',
        'scheme_name': 'Expense Demo Fund',
        'source_url': 'https://groww.in/faq/expense-ratio',
        'concepts': ['expense','fees'],
    },
]

# Build chunks with normalized random embeddings
chunks = []
for i, entry in enumerate(faq_entries, start=1):
    emb = np.random.rand(768).astype('float32')
    # L2-normalize
    emb = emb / np.linalg.norm(emb)
    chunk = {
        'chunk_id': f'demo_{i:03}',
        'embedding': emb.tolist(),
        'text': entry['text'],
        'amc_name': entry['amc_name'],
        'scheme_name': entry['scheme_name'],
        'source_url': entry['source_url'],
        'concepts': entry['concepts'],
        'scraped_datetime': datetime.utcnow().isoformat(),
        'chunk_index': 0,
    }
    chunks.append(chunk)

print(f"Prepared {len(chunks)} demo chunks for import")

# Import into Chroma Cloud
success = import_chunks_to_chroma_cloud(chunks, collection_name='groww_faq', batch_size=50)
print('Import success:', success)

# Wait a bit for collection to stabilize
time.sleep(2)
# Validate by checking collection stats via the chroma client
from phase_3_llm_integration.chroma_cloud_client import create_chroma_client
try:
    client = create_chroma_client()
    stats = client.get_collection_stats()
    print('Collection stats:', stats)
except Exception as e:
    print('Failed to fetch collection stats:', repr(e))
