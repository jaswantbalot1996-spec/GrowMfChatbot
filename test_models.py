#!/usr/bin/env python3
import requests

api_key = 'AIzaSyAdWtCEYibH2U7SdpseRCnVS8FXHhm21Uc'
url = f'https://generativelanguage.googleapis.com/v1/models?key={api_key}'

try:
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        import json
        data = r.json()
        models = data.get('models', [])
        print(f"Available models ({len(models)} total):")
        for m in models:
            name = m.get('name', 'unknown')
            display_name = m.get('displayName', '')
            print(f"  {name}")
            if display_name:
                print(f"    -> {display_name}")
    else:
        print(f'Error: {r.status_code}')
        print(r.text[:500])
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()
