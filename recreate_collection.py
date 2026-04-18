#!/usr/bin/env python3
"""
Delete and recreate Chroma Cloud collection with correct 384D embeddings
"""
import sys
sys.path.insert(0, 'c:/GrowMfChatbot')

from phase_3_llm_integration.chroma_cloud_client import create_chroma_client

try:
    print("Connecting to Chroma Cloud...")
    client = create_chroma_client()
    
    collection_name = "groww_faq"
    
    print(f"Deleting old collection: {collection_name}")
    try:
        client.client.delete_collection(name=collection_name)
        print(f"✓ Collection {collection_name} deleted")
    except Exception as e:
        print(f"Note: Collection deletion returned: {e}")
    
    print(f"\nCreating new collection: {collection_name}")
    collection = client.client.get_or_create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": "cosine",
            "dense_embedding_model": "chroma-cloud-qwen",
            "sparse_embedding_model": "chroma-cloud-splade",
            "hybrid_search": True,
        }
    )
    print(f"✓ New collection created: {collection_name}")
    print(f"  - Metadata: {collection.metadata}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
