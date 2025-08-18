import os
import sys
import json
import argparse
import subprocess
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
TESTS_DIR = os.path.join(ROOT, "WSP_agentic", "tests", "pqn_detection")
KNOW_DIR = os.path.join(ROOT, "WSP_knowledge", "docs", "Papers", "Empirical_Evidence", "CMST_PQN_Detector")


def try_load_plan(path: str) -> dict:
    # Supports JSON; attempts YAML if PyYAML is available
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    try:
        import yaml  # type: ignore
        return yaml.safe_load(data)
    except Exception:
        return json.loads(data)


def run(cmd: list[str]) -> int:
    res = subprocess.run(cmd, cwd=ROOT)
    return res.returncode


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def promote(src_paths: list[str], dst_dir: str) -> None:
    ensure_dir(dst_dir)
    for sp in src_paths:
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(dst_dir, os.path.basename(sp)))


def phase_sweep(length: int, steps: int, sps: int, dt: float, plot: bool) -> dict:
    # Library-first sweep execution
    from modules.ai_intelligence.pqn_alignment.src.sweep.api import run_sweep
    res_csv, plot_png = run_sweep({
        "length": int(length),
        "steps": int(steps),
        "steps_per_sym": int(sps),
        "dt": float(dt),
        "plot": bool(plot),
    })
    return {"rc": 0, "out_dir": os.path.dirname(res_csv)}


def promote_phase(length: int) -> None:
    src_dir = os.path.join(TESTS_DIR, "logs", f"phase_len{length}")
    promote([
        os.path.join(src_dir, f"phase_diagram_results_len{length}.csv"),
        os.path.join(src_dir, f"phase_diagram_scatter_len{length}.png"),
    ], os.path.join(KNOW_DIR, f"phase_len{length}"))


def top_risky_from_csv(csv_path: str, k: int = 8) -> list[str]:
    import csv  # local to avoid global import cost
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            try:
                rows.append((r["script"], float(r["paradox_per_1k"])) )
            except Exception:
                continue
    rows.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in rows[:k]]


def rerun_targeted(scripts: list[str], steps: int, sps: int, dt_values: list[float], noise_pairs: list[tuple[float, float]]) -> str:
    out_dir = os.path.join(TESTS_DIR, "logs", "targeted")
    ensure_dir(out_dir)
    v2 = os.path.join(TESTS_DIR, "cmst_pqn_detector_v2.py")
    for scr in scripts:
        for dt in dt_values:
            for (nH, nL) in noise_pairs:
                cmd = [
                    sys.executable, v2,
                    "--script", scr,
                    "--steps", str(steps),
                    "--steps_per_sym", str(sps),
                    "--dt", str(dt),
                    "--out_dir", out_dir,
                    "--log_csv", f"{scr.replace('.', 'dot')}_dt{dt:.3f}_nH{nH:.3f}_nL{nL:.3f}.csv",
                    "--events",  f"{scr.replace('.', 'dot')}_dt{dt:.3f}_nH{nH:.3f}_nL{nL:.3f}.txt",
                ]
                run(cmd)
    return out_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=str, required=False, default="tools/auto/pqn_autorun.json")
    args = ap.parse_args()

    plan = {}
    if os.path.exists(os.path.join(ROOT, args.plan)):
        plan = try_load_plan(os.path.join(ROOT, args.plan)) or {}

    # Defaults
    seeds = plan.get("seeds", [0])
    dt = float(plan.get("dt", 0.5/7.05))
    steps_per_sym = int(plan.get("steps_per_sym", 120))

    # S2: phase sweeps (len 2/3/4)
    for L in plan.get("phase_lengths", [3]):
        phase_sweep(length=int(L), steps=int(plan.get("phase_steps", 800)), sps=steps_per_sym, dt=dt, plot=True)
        promote_phase(int(L))

    # S3: targeted re-runs from len-3
    try:
        len3_csv = os.path.join(TESTS_DIR, "logs", "phase_len3", "phase_diagram_results_len3.csv")
        if os.path.exists(len3_csv):
            top_scripts = top_risky_from_csv(len3_csv, k=int(plan.get("target_top_k", 6)))
            targeted_dir = rerun_targeted(
                scripts=top_scripts,
                steps=int(plan.get("target_steps", 2400)),
                sps=steps_per_sym,
                dt_values=[dt*0.5, dt, dt*2.0],
                noise_pairs=[(0.005,0.002),(0.01,0.005)],
            )
            promote([
                *[os.path.join(targeted_dir, fn) for fn in os.listdir(targeted_dir) if fn.endswith((".csv",".txt"))]
            ], os.path.join(KNOW_DIR, "targeted_runs"))
    except Exception:
        pass

    # S6: council cycle (small)
    council = os.path.join(TESTS_DIR, "council_orchestrator.py")
    ensure_dir(os.path.join(TESTS_DIR, "council"))
    run([sys.executable, council, "--steps", str(int(plan.get("council_steps", 1200))), "--seeds", *[str(s) for s in seeds]])

    print(json.dumps({"status": "ok", "note": "autorun completed"}))


if __name__ == "__main__":
    main()


