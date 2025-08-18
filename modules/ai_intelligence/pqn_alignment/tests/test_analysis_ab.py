import os
import tempfile
from modules.ai_intelligence.pqn_alignment.src.analysis_ab import compare_events


def test_compare_events_deltas_and_cost():
	# Create two temporary event logs
	with tempfile.TemporaryDirectory() as d:
		base = os.path.join(d, 'base.jsonl')
		var = os.path.join(d, 'var.jsonl')
		# Baseline: more paradox, slightly higher PQN
		with open(base, 'w', encoding='utf-8') as f:
			f.write('{"flags":["PQN_DETECTED"]}\n')
			f.write('{"flags":["PQN_DETECTED","PARADOX_RISK"]}\n')
			f.write('{"flags":["PARADOX_RISK"]}\n')
		# Variant: fewer paradox, slightly fewer PQN
		with open(var, 'w', encoding='utf-8') as f:
			f.write('{"flags":["PQN_DETECTED"]}\n')
			f.write('{"flags":["RESONANCE_HIT"]}\n')

		res = compare_events(base, steps_a=1000, events_b=var, steps_b=1000)
		# Baseline: pqn=2, par=2 => rates per 1k
		# Variant: pqn=1, par=0
		assert res['paradox_rate_a'] == 2.0
		assert res['paradox_rate_b'] == 0.0
		assert res['pqn_rate_a'] == 2.0
		assert res['pqn_rate_b'] == 1.0
		assert res['delta_paradox_rate'] == -2.0
		assert res['delta_pqn_rate'] == -1.0
		# cost_of_stability = pqn loss per paradox avoided = 1 / 2
		assert abs(res['cost_of_stability'] - 0.5) < 1e-9
