import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from phase_3_llm_integration.gemini_client import GeminiLLMClient

try:
    client = GeminiLLMClient()
    resp = client.generate_response('What is ELSS?', [])
    print('OK', resp)
except Exception as e:
    print('ERROR', e)
