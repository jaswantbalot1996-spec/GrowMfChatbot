import requests
import json
import time

time.sleep(1)

url = 'http://localhost:8000/query'
payload = {
    'query': 'What is ELSS?',
    'language': 'en'
}

try:
    r = requests.post(url, json=payload, timeout=5)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'✅ Query successful!')
        print(f'Answer: {data.get("answer")[:100]}...')
    else:
        print(f'Error: {r.json()}')
except Exception as e:
    print(f'Connection Error: {e}')
