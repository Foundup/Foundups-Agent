"""
A/B analysis helper (guardrail OFF vs ON or baseline vs variant).
- compare_events(events_a, steps_a, events_b, steps_b) -> dict with deltas
"""
from typing import Dict


def _summarize_events(events_path: str) -> Dict[str, int]:
	pqn = 0
	par = 0
	res = 0
	try:
		with open(events_path, 'r', encoding='utf-8') as f:
			for line in f:
				if 'PQN_DETECTED' in line:
					pqn += 1
				if 'PARADOX_RISK' in line:
					par += 1
				if 'RESONANCE_HIT' in line:
					res += 1
	except FileNotFoundError:
		pass
	return {"pqn": pqn, "par": par, "res": res}


def compare_events(events_a: str, steps_a: int, events_b: str, steps_b: int) -> Dict[str, float]:
	"""
	Return deltas: Δparadox_rate, Δpqn_rate, cost_of_stability (pqn loss per paradox avoided).
	Rates are per 1k steps.
	"""
	sum_a = _summarize_events(events_a)
	sum_b = _summarize_events(events_b)
	k_a = max(1.0, steps_a / 1000.0)
	k_b = max(1.0, steps_b / 1000.0)
	par_a = sum_a["par"] / k_a
	par_b = sum_b["par"] / k_b
	pqn_a = sum_a["pqn"] / k_a
	pqn_b = sum_b["pqn"] / k_b
	d_par = par_b - par_a
	d_pqn = pqn_b - pqn_a
	cost_of_stability = 0.0
	if d_par < 0:  # paradox reduced in B
		cost_of_stability = -d_pqn / (-d_par) if (-d_par) > 0 else 0.0
	return {
		"paradox_rate_a": par_a,
		"paradox_rate_b": par_b,
		"pqn_rate_a": pqn_a,
		"pqn_rate_b": pqn_b,
		"delta_paradox_rate": d_par,
		"delta_pqn_rate": d_pqn,
		"cost_of_stability": cost_of_stability,
	}
