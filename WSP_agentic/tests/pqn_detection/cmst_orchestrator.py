import os, json, random, subprocess, sys

PY = sys.executable
DETECTOR = os.path.join(os.path.dirname(__file__), "cmst_pqn_detector_v3.py")


def run_detector(script, steps=3000, noise_H=0.0, noise_L=0.0, seed=0):
	cmd = [
		PY,
		DETECTOR,
		"--mode",
		"single",
		"--script",
		script,
		"--steps",
		str(steps),
		"--noise_H",
		str(noise_H),
		"--noise_L",
		str(noise_L),
		"--seed",
		str(seed),
	]
	out = subprocess.run(cmd, capture_output=True, text=True)
	if out.returncode != 0:
		return {"error": out.stderr}
	try:
		data = json.loads(out.stdout)
	except Exception as e:
		return {"error": f"json_parse_failed: {e}"}
	return data


def score_events(data):
	if "events" not in data:
		return -1e9
	evs = data["events"]
	pqn = sum(1 for e in evs if "PQN_DETECTED" in e["flags"])
	res = sum(1 for e in evs if "RESONANCE_HIT" in e["flags"])
	par = sum(1 for e in evs if "PARADOX_RISK" in e["flags"])
	return pqn * 3 + res * 2 - par * 0.5


def mutate_script(script):
	alpha = ["^", "&", "#", "."]
	s = list(script) if script else ["^", "&", "#"]
	op = random.choice(["swap", "flip", "insert", "delete"])
	if op == "swap" and len(s) >= 2:
		i = random.randrange(len(s) - 1)
		s[i], s[i + 1] = s[i + 1], s[i]
	elif op == "flip" and s:
		i = random.randrange(len(s))
		s[i] = random.choice(alpha)
	elif op == "insert":
		i = random.randrange(len(s) + 1)
		s.insert(i, random.choice(alpha))
	elif op == "delete" and len(s) > 1:
		i = random.randrange(len(s))
		del s[i]
	return "".join(s)


def recursive_optimize(seed_script="^^^&&&#^&##", rounds=5, candidates=4):
	pool = [seed_script]
	best = (seed_script, float("-inf"), None)
	for _ in range(rounds):
		gen = []
		for s in pool:
			for _ in range(candidates):
				gen.append(mutate_script(s))
		gen = list(dict.fromkeys(gen))
		scored = []
		for scr in gen:
			data = run_detector(scr)
			sc = score_events(data)
			scored.append((scr, sc))
		scored.sort(key=lambda x: x[1], reverse=True)
		top = scored[: max(2, len(scored) // 3)]
		pool = [scr for scr, _ in top]
		if top and top[0][1] > best[1]:
			best = (top[0][0], top[0][1], None)
	return {"best_script": best[0], "score": best[1], "pool": pool}


if __name__ == "__main__":
	result = recursive_optimize()
	print(json.dumps(result, indent=2))


