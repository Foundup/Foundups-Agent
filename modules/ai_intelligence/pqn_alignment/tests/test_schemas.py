import json


def validate_event(obj: dict) -> bool:
	required = {"t","sym","C","E","rnorm","purity","S","detg","det_thr","flags"}
	return required.issubset(set(obj.keys()))


def test_event_schema_example():
	# Example object following INTERFACE
	obj = {
		"t": 10.142,
		"sym": "^",
		"C": 0.188,
		"E": 0.362,
		"rnorm": 0.5,
		"purity": 0.79,
		"S": 0.41,
		"detg": 3.34e-08,
		"det_thr": 1e-08,
		"flags": ["PQN_DETECTED","RESONANCE_HIT"],
	}
	assert validate_event(obj)
