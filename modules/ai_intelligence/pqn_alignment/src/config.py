"""
Canonical config loader (YAML only per WSP 12/22 policy).
- load_config(path) -> dict
"""
from typing import Dict, Any


def load_config(path: str) -> Dict[str, Any]:
	"""
	Load a YAML config file and return as dict.
	JSON fallback is removed to enforce a single canonical format.
	"""
	if not path:
		raise ValueError("path is required")
	with open(path, "r", encoding="utf-8") as f:
		data = f.read()
	try:
		import yaml  # type: ignore
	except Exception as exc:
		raise ImportError("pyyaml is required for configuration loading. Install pyyaml.") from exc
	obj = yaml.safe_load(data)
	if isinstance(obj, dict):
		return obj
	raise ValueError("YAML config must define a mapping/dict at the root")
