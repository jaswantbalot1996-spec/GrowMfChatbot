import sys, os
sys.path.insert(0, os.getcwd())
from phase_3_llm_integration.phase3_service import Phase3QueryService

svc = Phase3QueryService()
resp = svc.query('What is NAV?')
print('Response:', resp)
