#!/usr/bin/env python3
"""
Test Chroma Cloud collection directly to debug search issues
"""
import sys
sys.path.insert(0, 'c:\GrowMfChatbot')

from phase_3_llm_integration.chroma_cloud_client import ChromaCloudClient
from phase_3_llm_integration.config import CHROMA_COLLECTION_NAME_TEMPLATE

# Initialize Chroma client
client = ChromaCloudClient()

print("=" * 60)
print("Testing Chroma Cloud Collection Access")
print("=" * 60)

# Try to get collection stats
try:
    collection_name = CHROMA_COLLECTION_NAME_TEMPLATE.format(amc_name_lower="groww")
    print(f"\nCollection Name: {collection_name}")
    
    stats = client.get_collection_stats(collection_name)
    print(f"\n✓ Collection Stats:")
    print(f"  - Total Documents: {stats.get('total_documents', 0)}")
    print(f"  - Embedding Model: {stats.get('embedding_model', 'unknown')}")
    print(f"  - Sparse Model: {stats.get('sparse_model', 'unknown')}")
    print(f"  - Hybrid Search: {stats.get('hybrid_search', False)}")
    
except Exception as e:
    print(f"\n✗ Error getting collection stats: {e}")
    import traceback
    traceback.print_exc()

# Test a simple query
print("\n" + "=" * 60)
print("Testing Query")
print("=" * 60)

try:
    results = client.hybrid_search(
        query_embedding=None,  # Will use text-based
        query_text="What is the minimum SIP for Groww Money Market Fund?",
        top_k=5
    )
    
    print(f"\n✓ Query returned {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    - Text: {result.text[:100]}...")
        print(f"    - Score: {result.score}")
        print(f"    - Source: {result.source_url}")
        
except Exception as e:
    print(f"\n✗ Query error: {e}")
    import traceback
    traceback.print_exc()
