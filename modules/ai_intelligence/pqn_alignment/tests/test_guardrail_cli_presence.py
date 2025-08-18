import os

def test_v3_guardrail_cli_flags_present():
	path = os.path.join('WSP_agentic','tests','pqn_detection','cmst_pqn_detector_v3.py')
	assert os.path.exists(path), 'v3 detector file missing'
	with open(path, 'r', encoding='utf-8') as f:
		src = f.read()
	for flag in ['--guardrail_on','--guardrail_window','--paradox_purity','--paradox_entropy']:
		assert flag in src, f'missing CLI flag {flag}'
