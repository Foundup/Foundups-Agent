def test_config_loader_exists():
	import importlib
	mod = importlib.import_module('modules.ai_intelligence.pqn_alignment.src.config')
	assert hasattr(mod, 'load_config')
