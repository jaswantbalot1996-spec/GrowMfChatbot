import requests
import json

# Test 1: PII detection (PAN)
print("=" * 70)
print("TEST 1: PII Detection - PAN Number")
print("=" * 70)
r = requests.post('http://127.0.0.1:8000/query', 
                  json={'query': 'My PAN is ABCDE1234F, what funds can I invest in?', 'language': 'en'},
                  timeout=10)
print('Status:', r.status_code)
print(json.dumps(r.json(), indent=2))

# Test 2: Advice query detection
print("\n" + "=" * 70)
print("TEST 2: Advice Query Refusal - Should I...")
print("=" * 70)
r = requests.post('http://127.0.0.1:8000/query', 
                  json={'query': 'Should I buy ELSS funds now for tax savings?', 'language': 'en'},
                  timeout=10)
print('Status:', r.status_code)
print(json.dumps(r.json(), indent=2))

# Test 3: Normal factual query
print("\n" + "=" * 70)
print("TEST 3: Factual Query - NAV")
print("=" * 70)
r = requests.post('http://127.0.0.1:8000/query', 
                  json={'query': 'What is NAV in mutual funds?', 'language': 'en'},
                  timeout=10)
print('Status:', r.status_code)
resp = r.json()
print('Mode:', resp.get('mode'))
print('Answer:', resp.get('answer'))
print('Has source link:', 'https://' in resp.get('answer', ''))
print('Last updated:', 'Last updated from sources:' in resp.get('answer', ''))
