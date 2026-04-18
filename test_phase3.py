#!/usr/bin/env python
"""Test Phase 3 LLM service connectivity"""

import sys, os
sys.path.insert(0, 'phase_3_llm_integration')

# Load env
env_path = 'phase_3_llm_integration/.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

print('Environment variables loaded:')
print(f'  CHROMA_API_KEY: {"*" * 10 if os.environ.get("CHROMA_API_KEY") else "NOT SET"}')
print(f'  CHROMA_TENANT: {os.environ.get("CHROMA_TENANT", "NOT SET")}')
print(f'  CHROMA_DATABASE: {os.environ.get("CHROMA_DATABASE", "NOT SET")}')
print(f'  GEMINI_API_KEY: {"*" * 10 if os.environ.get("GEMINI_API_KEY") else "NOT SET"}')
print()

try:
    from phase3_service import Phase3QueryService
    print('✅ Phase3QueryService imported successfully')
    service = Phase3QueryService()
    print('✅ Phase3QueryService initialized')
    
    # Test query
    print('\n🔍 Testing query: "What is NAV?"')
    result = service.query('What is NAV?')
    print()
    print('✅ Query executed successfully')
    print(f'Response: {result.get("response", "N/A")[:200]}...')
    print(f'Sources: {len(result.get("sources", []))} found')
    if result.get("sources"):
        print(f'  Source 1: {result["sources"][0].get("source", "N/A")}')
except Exception as e:
    print(f'❌ Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
