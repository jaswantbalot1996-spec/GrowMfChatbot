"""
Advanced Latency Breakdown - Identifies exact bottlenecks in API chain
"""
import time
import requests
import sys
from datetime import datetime

def test_chroma_cloud_latency():
    """Test Chroma Cloud retrieval speed."""
    print("\n" + "="*60)
    print("📦 CHROMA CLOUD LATENCY TEST")
    print("="*60)
    
    try:
        # Test connection to Chroma Cloud
        start = time.time()
        resp = requests.get(
            "https://api.trychroma.com/api/info",
            timeout=10
        )
        latency = (time.time() - start) * 1000
        
        print(f"Chroma Cloud API response: {latency:.0f}ms")
        
        if latency > 2000:
            print("⚠️  SLOW! Network to Chroma Cloud is high latency")
            print("   Try local Chroma instead (faster)")
    except Exception as e:
        print(f"❌ Error: {e}")


def trace_api_request():
    """Trace API request with detailed timing."""
    print("\n" + "="*60)
    print("🔬 API REQUEST TRACING")
    print("="*60)
    print("Sending instrumented query...")
    
    start_total = time.time()
    
    try:
        resp = requests.post(
            "http://localhost:8000/query",
            json={"query": "What is ELSS?", "language": "en"},
            timeout=180
        )
        
        if resp.status_code == 200:
            data = resp.json()
            total_ms = (time.time() - start_total) * 1000
            
            print(f"\n✅ Total time: {total_ms:.0f}ms")
            
            # Extract latency details
            print(f"\nResponse structure:")
            for key in data.keys():
                value = data[key]
                if isinstance(value, (int, float)):
                    print(f"  • {key}: {value}")
                elif isinstance(value, str) and len(value) < 100:
                    print(f"  • {key}: {value[:50]}...")
                elif isinstance(value, list):
                    print(f"  • {key}: [{len(value)} items]")
            
            # Try to get latency breakdown
            if 'latency_ms' in data:
                print(f"\nLatency breakdown:")
                latency_data = data['latency_ms']
                
                if isinstance(latency_data, dict):
                    for stage, ms in latency_data.items():
                        print(f"  {stage}: {ms:.0f}ms")
                else:
                    print(f"  {latency_data}")
            
            # Analyze
            print(f"\n📊 Analysis:")
            if total_ms > 30000:
                print(f"  ❌ Query is SLOW: {total_ms/1000:.1f}s")
                print(f"     Expected: 5-10s (retrieval 1-2s + generation 5s)")
                print(f"     Overhead: {total_ms - 6000:.0f}ms unaccounted for")
                
                print(f"\n  Likely bottleneck:")
                print(f"     1. Chroma Cloud retrieval (network latency)")
                print(f"     2. Post-processing overhead")
                print(f"     3. Python GIL/startup overhead")
        else:
            print(f"❌ Error: {resp.status_code}")
            print(f"   {resp.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def check_api_code_overhead():
    """Check for unnecessary overhead in API code."""
    print("\n" + "="*60)
    print("🔧 API CODE ANALYSIS")
    print("="*60)
    
    print("""
Potential bottlenecks in api_server_phase4.py:
  
  1. PII Detection (QueryValidator.check_pii)
     • Runs regex on entire query multiple times
     • Impact: ~10-50ms
     
  2. Retrieval Phase (Chroma Cloud search)
     • Dense search (50-400ms depending on network)
     • Sparse search (30-200ms)
     • Fusion & ranking (10-50ms)
     • Expected total: 200-500ms baseline
     • ⚠️ Can be 3-5s if network is slow
     
  3. LLM Generation (Ollama)
     • First request: Load model ~2-5s
     • Subsequent: ~6s for 150 tokens @ 39ms/token
     • Expected: 6-7s per request
     
  4. Post-processing
     • Citation verification
     • Response formatting
     • Translation (if enabled)
     • Expected: 100-500ms
     
  5. Python Overhead
     • Imports (first time)
     • Model initialization
     • Connection pooling warmup
     • Expected: 1-2s (first request only)

MOST LIKELY CULPRIT: Chroma Cloud network latency!
     Check with: curl -w '@curl-format.txt' https://api.trychroma.com/api/info
    """)


def check_network_dns():
    """Check DNS resolution time."""
    print("\n" + "="*60)
    print("🌐 NETWORK & DNS CHECK")
    print("="*60)
    
    import socket
    
    # Test DNS resolution
    print("DNS resolution times:")
    hosts = [
        "localhost:11434",
        "api.trychroma.com",
        "localhost:8000"
    ]
    
    for host in hosts:
        hostname = host.split(':')[0]
        try:
            start = time.time()
            ip = socket.gethostbyname(hostname)
            latency = (time.time() - start) * 1000
            print(f"  {hostname} ({ip}): {latency:.1f}ms")
        except Exception as e:
            print(f"  {hostname}: ERROR - {e}")


def main():
    print("\n" + "="*70)
    print(" 🔬 DETAILED LATENCY ANALYSIS")
    print("="*70)
    
    check_network_dns()
    test_chroma_cloud_latency()
    trace_api_request()
    check_api_code_overhead()
    
    print("\n" + "="*70)
    print(" 💡 QUICK FIXES (in order of impact)")
    print("="*70)
    
    print("""
1️⃣  FASTEST: Switch Chroma to LOCAL (5X faster)
    • Docker run local Chroma Cloud locally
    • Or use Milvus/Qdrant (faster for queries)
    • Expected improvement: 27s → 8-10s
    
2️⃣  NEXT: Reduce max tokens 150 → 100
    • Change in config.py
    • Expected improvement: 33s → 28s (15% gain)
    
3️⃣  CACHE enabled
    • Already in api_server_phase4.py
    • Repeated queries bypass LLM entirely
    • Expected improvement: 33s → 0.5s for cache hits
    
4️⃣  Use smaller model
    • Try: OLLAMA_MODEL=gemma:2b
    • Expected improvement: 33s → 20-25s (more tokens/sec)
    
5️⃣  Flask async/threading
    • Current: Synchronous (blocks on each step)
    • Could implement: Parallel retrieval + generation
    • Expected improvement: 33s → 15-20s
    """)
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
