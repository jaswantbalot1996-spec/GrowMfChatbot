import requests
import json

# Quick test with very short timeout
url = 'http://localhost:8000/query'
payload = {
    'query': 'ELSS',  # Simple keyword
    'language': 'en'
}

try:
    print("Sending request...")
    r = requests.post(url, json=payload, timeout=10)
    print(f'Status: {r.status_code}')
    print(json.dumps(r.json(), indent=2))
except requests.Timeout:
    print('Request timed out - API is hanging on query processing')
except Exception as e:
    print(f'Error: {e}')
