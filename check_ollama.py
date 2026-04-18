import requests
import sys

try:
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    r.raise_for_status()
    models = r.json().get('models', [])
    if models:
        print("Available Ollama models:")
        for m in models:
            print(f"  • {m['name']}")
    else:
        print("No models found in Ollama")
except Exception as e:
    print(f"Error connecting to Ollama: {e}")
    sys.exit(1)
