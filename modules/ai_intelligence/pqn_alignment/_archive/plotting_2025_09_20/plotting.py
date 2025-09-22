"""
Plotting utilities
- plot_phase_diagram(df, output_path)
- plot_run_timeseries(log_df, output_path)

Optional deps: matplotlib, seaborn.
"""
from typing import Optional

try:
	import matplotlib.pyplot as plt  # type: ignore
	has_mpl = True
except Exception:
	has_mpl = False

try:
	import seaborn as sns  # type: ignore
	has_sns = True
except Exception:
	has_sns = False


def plot_phase_diagram(df, output_path: str) -> Optional[str]:
	if not has_mpl:
		raise RuntimeError("matplotlib is required for plotting")
	x = 'pqn_per_1k' if 'pqn_per_1k' in df.columns else 'pqn_rate'
	y = 'paradox_per_1k' if 'paradox_per_1k' in df.columns else 'paradox_rate'
	plt.figure(figsize=(8, 6))
	if has_sns:
		sns.scatterplot(data=df, x=x, y=y, alpha=0.8)
	else:
		plt.scatter(df[x], df[y], s=20, alpha=0.8)
	plt.xlabel('PQN detections per 1k steps')
	plt.ylabel('Paradox-risk flags per 1k steps')
	plt.title('PQN vs Paradox Phase Diagram')
	plt.grid(True, linestyle='--', alpha=0.4)
	plt.tight_layout()
	plt.savefig(output_path, dpi=140)
	return output_path


def plot_run_timeseries(log_df, output_path: str) -> Optional[str]:
	if not has_mpl:
		raise RuntimeError("matplotlib is required for plotting")
	needed = {'t','C','E','detg','S'}
	if not needed.issubset(set(log_df.columns)):
		raise ValueError("log_df missing required columns for time-series plot")
	plt.figure(figsize=(10, 7))
	plt.subplot(4,1,1); plt.plot(log_df['t'], log_df['C']); plt.ylabel('C'); plt.grid(True, alpha=0.3)
	plt.subplot(4,1,2); plt.plot(log_df['t'], log_df['E']); plt.ylabel('E'); plt.grid(True, alpha=0.3)
	plt.subplot(4,1,3); plt.plot(log_df['t'], log_df['detg']); plt.ylabel('det(g)'); plt.grid(True, alpha=0.3)
	plt.subplot(4,1,4); plt.plot(log_df['t'], log_df['S']); plt.ylabel('S'); plt.xlabel('t'); plt.grid(True, alpha=0.3)
	plt.tight_layout()
	plt.savefig(output_path, dpi=140)
	return output_path
