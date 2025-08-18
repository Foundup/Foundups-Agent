import os, json, argparse
from modules.ai_intelligence.pqn_alignment.src.sweep.api import run_sweep


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--length", type=int, default=3)
	ap.add_argument("--steps", type=int, default=800)
	ap.add_argument("--steps_per_sym", type=int, default=120)
	ap.add_argument("--dt", type=float, default=0.5/7.05)
	ap.add_argument("--plot", action="store_true")
	args = ap.parse_args()

	# Delegate to library
	results_csv, plot_png = run_sweep({
		"length": args.length,
		"steps": args.steps,
		"steps_per_sym": args.steps_per_sym,
		"dt": args.dt,
		"plot": bool(args.plot),
	})
	out_dir = os.path.dirname(results_csv)
	print(json.dumps({
		"results_csv": results_csv,
		"out_dir": out_dir,
		"plotted": bool(plot_png and os.path.exists(plot_png)),
	}, indent=2))


if __name__ == "__main__":
	main()


