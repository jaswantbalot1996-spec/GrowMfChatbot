import requests
import json

# Test with ELSS query to match demo FAQ
r = requests.post('http://127.0.0.1:8000/query', 
                  json={'query': 'What is ELSS and what is the lock-in period?', 'language': 'en'},
                  timeout=10)
print('Status:', r.status_code)
resp = r.json()
print('\n=== FULL RESPONSE ===')
print(json.dumps(resp, indent=2))
print('\n=== CHECKS ===')
print(f"✓ Has answer: {bool(resp.get('answer'))}")
print(f"✓ Has exactly 1 source: {len(resp.get('sources', [])) == 1}")
print(f"✓ Answer <= 3 sentences: {resp.get('answer', '').count('.') <= 3}")
print(f"✓ Has 'Last updated from sources:': {'Last updated from sources:' in resp.get('answer', '')}")
print(f"✓ Source is whitelisted: {'groww.in' in resp.get('answer', '') or 'sebi.gov.in' in resp.get('answer', '')}")
