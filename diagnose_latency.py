"""
Latency Diagnosis Tool for Groww Chatbot
Identifies bottlenecks in query processing
"""
import time
import requests
import json
import sys

def check_ollama_status():
    """Check Ollama service health and model status."""
    print("\n" + "="*60)
    print("🔍 OLLAMA SERVICE CHECK")
    print("="*60)
    
    try:
        # Check if Ollama is running
        start = time.time()
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        latency = (time.time() - start) * 1000
        
        if resp.status_code == 200:
            data = resp.json()
            models = data.get('models', [])
            print(f"✅ Ollama is RUNNING (latency: {latency:.0f}ms)")
            print(f"📦 Loaded models: {len(models)}")
            for model in models:
                name = model.get('name', 'unknown')
                print(f"   • {name}")
                if 'size' in model:
                    size_gb = model['size'] / (1024**3)
                    print(f"     Size: {size_gb:.1f}GB")
        else:
            print(f"❌ Ollama error: {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ OLLAMA NOT RUNNING!")
        print("   Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def test_ollama_inference():
    """Test Ollama inference speed."""
    print("\n" + "="*60)
    print("⚡ OLLAMA INFERENCE SPEED TEST")
    print("="*60)
    
    payload = {
        "model": "llama3.2:latest",
        "prompt": "What is ELSS? Answer in one sentence.",
        "temperature": 0.1,
        "num_predict": 50,  # Limit to 50 tokens for quick test
        "stream": False,
    }
    
    print("Testing model inference (50 tokens)...")
    start = time.time()
    
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=180
        )
        latency = (time.time() - start) * 1000
        
        if resp.status_code == 200:
            data = resp.json()
            tokens = data.get('eval_count', 0)
            eval_time = data.get('eval_duration', 0)
            
            print(f"✅ Response received in {latency:.0f}ms")
            print(f"   Tokens generated: {tokens}")
            print(f"   Eval time: {eval_time/1e9:.2f}s")
            
            if tokens > 0:
                time_per_token = eval_time / tokens / 1e9
                print(f"   Per-token latency: {time_per_token*1000:.0f}ms")
                print(f"   Estimated for 150 tokens: {time_per_token*150*1000:.0f}ms")
                
                if time_per_token > 0.1:  # > 100ms per token = CPU
                    print("   ⚠️  SLOW! Likely running on CPU. Consider:")
                    print("      • Check if GPU is available")
                    print("      • Reduce model size (try llama2:7b or gemma:2b)")
                    print("      • Check CUDA installation")
                else:
                    print("   ✅ Good speed (GPU likely being used)")
            
            print(f"\n   Sample response: {data.get('response', '')[:100]}...")
        else:
            print(f"❌ Error: {resp.status_code} - {resp.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT! Model took > 180 seconds - definitely CPU-bound")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_api_endpoint():
    """Test full API query latency."""
    print("\n" + "="*60)
    print("📊 API ENDPOINT LATENCY TEST")
    print("="*60)
    
    payload = {
        "query": "What is ELSS?",
        "language": "en"
    }
    
    print("Sending test query to API...")
    start = time.time()
    
    try:
        resp = requests.post(
            "http://localhost:8000/query",
            json=payload,
            timeout=180
        )
        total_latency = (time.time() - start) * 1000
        
        if resp.status_code == 200:
            data = resp.json()
            latency_breakdown = data.get('latency_ms', {})
            
            print(f"✅ Query completed in {total_latency:.0f}ms ({total_latency/1000:.1f}s)")
            print(f"\nLatency Breakdown:")
            print(f"   • Retrieval: {latency_breakdown.get('retrieval_ms', 'N/A')}ms")
            print(f"   • Generation: {latency_breakdown.get('generation_ms', 'N/A')}ms")
            print(f"   • Post-processing: {latency_breakdown.get('post_processing_ms', 'N/A')}ms")
            
            if total_latency > 30000:
                print(f"\n⚠️  SLOW QUERY ({total_latency/1000:.1f}s)!")
                if latency_breakdown.get('generation_ms', 0) > 20000:
                    print("   🔴 Generation is the bottleneck (60%+)")
                    print("   → This is Ollama on CPU. Recommendations:")
                    print("     1. Enable GPU in Ollama: CUDA/Metal support")
                    print("     2. Use smaller model: llama2:7b, gemma:2b")
                    print("     3. Reduce max tokens (currently 150)")
                elif latency_breakdown.get('retrieval_ms', 0) > 5000:
                    print("   🟡 Retrieval is slow")
                    print("   → Check Chroma Cloud connection")
            
            print(f"\n   Answer preview: {data.get('answer', '')[:100]}...")
        else:
            print(f"❌ Error: {resp.status_code}")
            print(f"   Response: {resp.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT! API took > 180 seconds")
    except requests.exceptions.ConnectionError:
        print(f"❌ API not running! Start with: python phase_4_extended_coverage/api_server_phase4.py 8000")
    except Exception as e:
        print(f"❌ Error: {e}")


def check_system_info():
    """Check system resources."""
    print("\n" + "="*60)
    print("💻 SYSTEM INFORMATION")
    print("="*60)
    
    try:
        import psutil
        import torch
        
        # CPU info
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"CPU: {cpu_count} cores @ {cpu_percent}% usage")
        
        # Memory info
        memory = psutil.virtual_memory()
        print(f"RAM: {memory.used/1024**3:.1f}GB / {memory.total/1024**3:.1f}GB ({memory.percent}%)")
        
        # GPU info
        if torch.cuda.is_available():
            print(f"✅ GPU AVAILABLE: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA: {torch.version.cuda}")
        else:
            print(f"❌ NO GPU DETECTED - Ollama will use CPU (SLOW!)")
        
    except ImportError:
        print("⚠️  psutil/torch not installed. Run: pip install psutil torch")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all diagnostics."""
    print("\n" + "="*70)
    print(" 🔧 GROWW CHATBOT LATENCY DIAGNOSIS TOOL")
    print("="*70)
    
    # Run checks
    ollama_ok = check_ollama_status()
    
    if ollama_ok:
        test_ollama_inference()
    
    check_system_info()
    test_api_endpoint()
    
    # Recommendations
    print("\n" + "="*60)
    print("💡 OPTIMIZATION RECOMMENDATIONS")
    print("="*60)
    
    print("""
If latency is > 30 seconds:

1️⃣  ENABLE GPU ACCELERATION (FASTEST - target: 2-5s per query)
   ├─ On Windows (NVIDIA):
   │  ├─ Install NVIDIA GPU drivers
   │  ├─ Install CUDA Toolkit 12.x
   │  ├─ Ollama will auto-detect GPU
   │  └─ Restart Ollama: ollama serve
   │
   ├─ On Mac (Apple Silicon):
   │  ├─ Metal GPU is auto-enabled
   │  └─ Already optimized
   │
   └─ On Linux (NVIDIA):
      ├─ Install nvidia-docker
      ├─ Run: docker run --gpus all -d -p 11434:11434 ollama/ollama
      └─ Pull model: docker exec <container> ollama pull llama2:7b

2️⃣  USE SMALLER MODEL (Fast alternative - target: 5-10s)
   ├─ Current: llama3.2:latest (5.2GB)
   ├─ Recommended: gemma:2b (1.7GB) or llama2:7b (3.9GB)
   └─ Change in .env: OLLAMA_MODEL=gemma:2b

3️⃣  REDUCE MAX TOKENS (Quick fix - 10-20% improvement)
   ├─ Current: max_tokens=150
   ├─ Better: max_tokens=100
   └─ Change in config.py: GEMINI_MAX_TOKENS = 100

4️⃣  ENABLE RESPONSE CACHING (For repeated queries)
   ├─ Already implemented in api_server_phase4.py
   ├─ Check Redis is running
   └─ Benefits cached queries by 90%+

5️⃣  CHECK NETWORK
   ├─ Chroma Cloud latency should be < 200ms
   ├─ Use: curl https://api.trychroma.com/api/info
   └─ If slow, switch to local Chroma
    """)
    
    print("="*70)


if __name__ == "__main__":
    main()
