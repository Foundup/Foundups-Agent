import importlib

def test_public_api_symbols_exist():
	mod = importlib.import_module('modules.ai_intelligence.pqn_alignment')
	assert hasattr(mod, 'run_detector')
	assert hasattr(mod, 'phase_sweep')
	assert hasattr(mod, 'rerun_targeted')
	assert hasattr(mod, 'council_run')
	assert hasattr(mod, 'promote')
