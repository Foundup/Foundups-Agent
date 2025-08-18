import os, json, argparse, subprocess, sys, itertools, math
from collections import Counter

PY = sys.executable
ROOT = os.path.dirname(__file__)
DETECTOR_V2 = os.path.join(ROOT, "cmst_pqn_detector_v2.py")


def jaccard_script(a: str, b: str) -> float:
	if not a and not b:
		return 1.0
	set_a = Counter(a)
	set_b = Counter(b)
	keys = set(set_a.keys()) | set(set_b.keys())
	inter = sum(min(set_a[k], set_b[k]) for k in keys)
	union = sum(max(set_a[k], set_b[k]) for k in keys)
	return float(inter / union) if union > 0 else 0.0


def mutate_single_edit(script: str, alphabet="^&#."):
	if not script:
		return ["^&#"]
	variants = set()
	for i in range(len(script)):
		for ch in alphabet:
			if ch != script[i]:
				variants.add(script[:i] + ch + script[i+1:])
	return list(variants)


def run_v2(script: str, steps: int, steps_per_sym: int, dt: float, out_dir: str, seed: int):
	log_csv = os.path.join(out_dir, f"{script.replace('.', 'dot')}_s{seed}_log.csv")
	events = os.path.join(out_dir, f"{script.replace('.', 'dot')}_s{seed}_events.txt")
	os.makedirs(out_dir, exist_ok=True)
	cmd = [
		PY, DETECTOR_V2,
		"--script", script,
		"--steps", str(steps),
		"--steps_per_sym", str(steps_per_sym),
		"--dt", str(dt),
		"--out_dir", out_dir,
		"--log_csv", os.path.basename(log_csv),
		"--events", os.path.basename(events),
		"--seed", str(seed),
	]
	res = subprocess.run(cmd, capture_output=True, text=True)
	return events, res.returncode, res.stderr


def summarize_events(events_path: str, steps: int):
	pqn = 0
	par = 0
	res = 0
	with open(events_path, "r") as f:
		for line in f:
			try:
				obj = json.loads(line)
			except Exception:
				continue
			flags = obj.get("flags", [])
			if "PQN_DETECTED" in flags:
				pqn += 1
			if "PARADOX_RISK" in flags:
				par += 1
			if "RESONANCE_HIT" in flags:
				res += 1
	return {
		"pqn": pqn,
		"paradox": par,
		"res_hits": res,
		"pqn_per_1k": (1000.0 * pqn / steps) if steps > 0 else 0.0,
		"paradox_per_1k": (1000.0 * par / steps) if steps > 0 else 0.0,
	}


def robustness_bonus(values):
	# Reward lower variability across seeds
	if not values:
		return 0.0
	mu = sum(values) / len(values)
	var = sum((v - mu) ** 2 for v in values) / max(1, (len(values) - 1))
	std = math.sqrt(var)
	return float(max(0.0, mu) / (1.0 + std))


def novelty_bonus(script: str, prior: list):
	if not prior:
		return 0.5
	scores = [jaccard_script(script, s) for s in prior]
	return float(1.0 - max(scores))  # farther from prior tops is better


def score_aggregate(avg_pqn_1k: float, avg_par_1k: float, avg_res: float, r_robust: float, r_novel: float):
	return 3.0 * avg_pqn_1k - 2.0 * avg_par_1k + 1.5 * avg_res + r_robust + r_novel


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--proposals", type=str, nargs="*", default=[])
	ap.add_argument("--seeds", type=int, nargs="*", default=[0,1,2])
	ap.add_argument("--steps", type=int, default=2000)
	ap.add_argument("--steps_per_sym", type=int, default=120)
	ap.add_argument("--dt", type=float, default=0.5/7.05)
	ap.add_argument("--out_dir", type=str, default=os.path.join(ROOT, "council_runs"))
	ap.add_argument("--topN", type=int, default=5)
	ap.add_argument("--archive", type=str, default=os.path.join(ROOT, "council", "archive.json"))
	ap.add_argument("--emit_summary", type=str, default=os.path.join(ROOT, "council", "summary.json"))
	args = ap.parse_args()

	os.makedirs(os.path.dirname(args.emit_summary), exist_ok=True)

	# Load prior archive of top scripts for novelty calc
	prior = []
	if os.path.exists(args.archive):
		try:
			with open(args.archive, "r") as f:
				j = json.load(f)
				prior = j.get("top_scripts", [])
		except Exception:
			prior = []

	# Collect proposals
	proposals = []
	for p in args.proposals:
		if os.path.isdir(p):
			for fn in os.listdir(p):
				if fn.endswith(".json"):
					with open(os.path.join(p, fn), "r") as f:
						proposals.append(json.load(f))
		elif os.path.isfile(p):
			with open(p, "r") as f:
				proposals.append(json.load(f))

	# Fallback: simple built-in proposal if none provided
	if not proposals:
		proposals = [{
			"author": "builtin",
			"type": "experiment",
			"scripts": ["^^^", "^&#", "&&#", "#^.", "&.^"],
			"sweep": {"dt_scale": [1.0]},
			"hypotheses": ["baseline council run"],
		}]

	all_results = []
	for idx, prop in enumerate(proposals):
		scripts = prop.get("scripts", [])
		dt_scales = prop.get("sweep", {}).get("dt_scale", [1.0])
		for script, dts in itertools.product(scripts, dt_scales):
			seed_summaries = []
			for sd in args.seeds:
				out_dir = os.path.join(args.out_dir, f"prop{idx}")
				events_path, rc, err = run_v2(
					script=script,
					steps=args.steps,
					steps_per_sym=args.steps_per_sym,
					dt=args.dt * float(dts),
					out_dir=out_dir,
					seed=sd,
				)
				if rc != 0 or not os.path.exists(events_path):
					continue
				seed_summaries.append(summarize_events(events_path, steps=args.steps))
			if not seed_summaries:
				continue
			avg_pqn_1k = sum(s["pqn_per_1k"] for s in seed_summaries) / len(seed_summaries)
			avg_par_1k = sum(s["paradox_per_1k"] for s in seed_summaries) / len(seed_summaries)
			avg_res = sum(s["res_hits"] for s in seed_summaries) / len(seed_summaries)
			r_robust = robustness_bonus([s["pqn_per_1k"] for s in seed_summaries])
			r_novel = novelty_bonus(script, prior)
			score = score_aggregate(avg_pqn_1k, avg_par_1k, avg_res, r_robust, r_novel)
			all_results.append({
				"proposal_idx": idx,
				"author": prop.get("author", "unknown"),
				"script": script,
				"dt_scale": float(dts),
				"avg_pqn_per_1k": avg_pqn_1k,
				"avg_paradox_per_1k": avg_par_1k,
				"avg_res_hits": avg_res,
				"robust_bonus": r_robust,
				"novel_bonus": r_novel,
				"score": score,
			})

	all_results.sort(key=lambda r: r["score"], reverse=True)
	top = all_results[: args.topN]

	# Update archive
	archive_obj = {"top_scripts": [r["script"] for r in top]}
	with open(args.archive, "w") as fa:
		json.dump(archive_obj, fa, indent=2)

	with open(args.emit_summary, "w") as fs:
		json.dump({"results": all_results, "top": top}, fs, indent=2)

	print(json.dumps({"top": top, "saved": args.emit_summary}, indent=2))


if __name__ == "__main__":
	main()


