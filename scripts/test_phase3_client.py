import sys, os
sys.path.insert(0, os.getcwd())
from phase_3_llm_integration.phase3_service import Phase3QueryService

try:
    svc = Phase3QueryService()
    print('LLM client:', type(svc.llm_client).__name__)
except Exception as e:
    print('ERROR', e)
