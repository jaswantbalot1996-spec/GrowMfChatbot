import requests
import json

url = 'http://localhost:8000/query'
payload = {
    'query': 'what is current NAV of Quant small Cap fund direct plan growth',
    'language': 'en'
}

r = requests.post(url, json=payload, timeout=10)
print(f'Status: {r.status_code}\n')
data = r.json()
print(f'Mode: {data.get("mode")}')
print(f'\nAnswer:\n{data.get("answer")}\n')
print(f'Source: {data.get("sources")[0].get("source") if data.get("sources") else "N/A"}')
