import requests
import json
import time

time.sleep(1)

# Test with NAV query
url = 'http://localhost:8000/query'
payload = {
    'query': 'what is current NAV of Quant small Cap fund direct plan growth',
    'language': 'en'
}

try:
    r = requests.post(url, json=payload, timeout=5)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'\n✅ Query successful!')
        print(f'Mode: {data.get("mode", "unknown")}')
        print(f'\nAnswer:\n{data.get("answer")}')
        print(f'\nSources: {len(data.get("sources", []))} found')
    else:
        print(f'Error: {r.json()}')
except Exception as e:
    print(f'Error: {e}')
