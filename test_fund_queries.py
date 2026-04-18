#!/usr/bin/env python
"""Test fund-specific queries"""
import requests
import json

queries = [
    'What is the minimum SIP for Groww Money Market Fund Direct Growth?',
    'What is the expense ratio of Groww ELSS Tax Saver Fund?',
    'What is the lock-in period for Groww ELSS fund?',
    'What is the expense ratio for Groww Large Cap Fund?',
    'What is the minimum SIP for Groww Liquid Fund?',
]

for query in queries:
    print('\n' + '='*70)
    print(f'Query: {query}')
    print('='*70)
    try:
        r = requests.post('http://localhost:8000/query', 
            json={'query': query, 'language': 'en'}, 
            timeout=60)
        response = r.json()
        print(f'Answer: {response.get("answer", "No answer found")}')
        sources = response.get('sources', [])
        if sources:
            print(f'Source: {sources[0].get("source", "Unknown")}')
            print(f'Relevance: {sources[0].get("relevance", "N/A")}')
    except Exception as e:
        print(f'Error: {e}')
