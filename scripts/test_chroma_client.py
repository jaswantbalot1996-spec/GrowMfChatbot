import sys, os
sys.path.insert(0, os.getcwd())
from phase_3_llm_integration.chroma_cloud_client import create_chroma_client

try:
    client = create_chroma_client()
    stats = client.get_collection_stats()
    print('OK', stats)
except Exception as e:
    print('ERROR', e)
