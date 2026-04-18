import requests
import json
import time

print("Testing Ollama + Chroma integration...")
print(f"Time: {time.strftime('%H:%M:%S')}\n")

try:
    # Send query with longer timeout for Ollama
    print("Sending query to /query endpoint...")
    print("⏳ Waiting for Ollama to process (this may take 30-60 seconds on first use)...\n")
    
    start = time.time()
    r = requests.post(
        'http://localhost:8000/query',
        json={
            'query': 'What is the minimum SIP for Groww Money Market Fund?',
            'language': 'en'
        },
        timeout=180  # Give Ollama 3 minutes
    )
    elapsed = time.time() - start
    
    print(f"✓ Response received in {elapsed:.1f}s\n")
    print(f"Status: {r.status_code}\n")
    
    data = r.json()
    
    print(f"📋 Query: {data.get('query_original', 'N/A')}")
    print(f"🤖 Model: {data.get('model', 'Unknown')}")
    print(f"⏱️  Latency: {data.get('latency_ms', 0):.0f}ms\n")
    
    print(f"📝 Answer (first 400 chars):")
    print(f"   {data.get('answer', 'N/A')[:400]}\n")
    
    print(f"📚 Sources: {len(data.get('sources', []))} found")
    for i, source in enumerate(data.get('sources', [])[:3], 1):
        print(f"   {i}. {source.get('source', 'Unknown')} (relevance: {source.get('relevance', 0):.2f})")
    
except requests.exceptions.Timeout:
    print("❌ Request timed out - Ollama might still be loading the model")
except Exception as e:
    print(f"❌ Error: {e}")
