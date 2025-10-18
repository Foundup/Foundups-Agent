#!/usr/bin/env python
"""
PQN Results Analyzer
- Generates cross-model performance and campaign-council correlation reports
- Writes JSON outputs to analysis_reports/
- Prints concise summary to stdout

Per WSP 50: safely resolve imports without relying on package context
Per WSP 84: reuse existing results_db functions, no vibecoding
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is on sys.path (src/ -> module root -> project root)
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[5]
sys.path.insert(0, str(PROJECT_ROOT))

from modules.ai_intelligence.pqn_alignment.src import results_db  # type: ignore


def main() -> int:
	# Run analyses
	analysis = results_db.analyze_cross_model_performance()
	correlation = results_db.correlate_campaign_council_results()

	# Prepare output dir
	out_dir = Path(__file__).resolve().parent / "analysis_reports"
	out_dir.mkdir(parents=True, exist_ok=True)
	stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

	# Write files
	perf_path = out_dir / f"cross_model_performance_{stamp}.json"
	corr_path = out_dir / f"campaign_council_correlation_{stamp}.json"
	with open(perf_path, "w", encoding="utf-8") as f:
		json.dump(analysis, f, indent=2)
	with open(corr_path, "w", encoding="utf-8") as f:
		json.dump(correlation, f, indent=2)

	# Print concise summary
	best = analysis.get("best_model", {})
	print("PQN Results Analysis Summary")
	print("=" * 32)
	print(f"Models analyzed: {len(analysis.get('model_performance', []))}")
	print(f"Council runs: {analysis.get('total_council_runs', 0)}")
	print(f"Best model: {best.get('model')} (success={best.get('success_rate'):.2f})")
	print(f"Outputs:\n - {perf_path}\n - {corr_path}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
