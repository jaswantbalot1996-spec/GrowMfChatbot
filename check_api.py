#!/usr/bin/env python3
import requests
import json
import time

time.sleep(8)

try:
    r = requests.get('http://localhost:8000/health', timeout=5)
    print(f'API Server Status: {r.status_code}')
    data = r.json()
    print(f'Mode: {data.get("mode", "unknown")}')
    print(f'Phase 3 Available: {data.get("phase3_available", False)}')
    print('API is ready!')
except Exception as e:
    print(f'API Server Error: {e}')
    exit(1)
