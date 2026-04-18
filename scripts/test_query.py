import requests
url='http://127.0.0.1:8000/query'
payload={'query':'What is NAV?'}
try:
    r=requests.post(url,json=payload,timeout=10)
    print('Status:',r.status_code)
    print(r.text)
except Exception as e:
    print('Request failed:',e)
