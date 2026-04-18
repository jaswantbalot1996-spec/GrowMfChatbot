import sys, os
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), 'phase_3_llm_integration', '.env'))
from phase_3_llm_integration.chroma_cloud_client import create_chroma_client

client = create_chroma_client()
col = client.collection
print('Collection name:', client.collection_name)

try:
    # As a fallback, list all documents and do a local substring match
    all_docs = col.get(limit=100)
    print('Total docs fetched:', len(all_docs.get('ids', [])))
    for idx, doc in enumerate(all_docs.get('documents', [])):
        if 'nav' in (doc or '').lower():
            print('Match doc id:', all_docs['ids'][idx])
            print('Text:', doc)
            print('Metadata:', all_docs['metadatas'][idx])
            print('---')
except Exception as e:
    print('Query failed:', e)
