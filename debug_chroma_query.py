#!/usr/bin/env python3
"""
Debug: Test Chroma query directly
"""
import sys
sys.path.insert(0, 'c:/GrowMfChatbot')

from phase_3_llm_integration.chroma_cloud_client import create_chroma_client

try:
    print("Testing Chroma Cloud direct query...")
    client = create_chroma_client()
    
    # Test with text query
    print("\n1. Testing text-based query...")
    results = client.collection.query(
        query_texts=["What is the minimum SIP for Groww Money Market Fund?"],
        n_results=5
    )
    
    print(f"   Results: {len(results['ids'][0]) if results['ids'] else 0} found")
    if results['ids'] and len(results['ids'][0]) > 0:
        for i, chunk_id in enumerate(results['ids'][0]):
            print(f"   {i+1}. {chunk_id}: {results['documents'][0][i][:60]}...")
    else:
        print("   No results!")
    
    # Test with query_embeddings parameter
    print("\n2. Testing with 384D embedding vector...")
    import numpy as np
    emb = np.random.rand(384).astype('float32').tolist()
    
    try:
        results = client.collection.query(
            query_embeddings=[emb],
            n_results=5
        )
        print(f"   Results: {len(results['ids'][0]) if results['ids'] else 0} found")
    except Exception as e:
        print(f"   Error: {e}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
