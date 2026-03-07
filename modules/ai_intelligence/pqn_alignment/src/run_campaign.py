"""
PQN rESP Validation Campaign Runner

Per WSP 84: Reuses existing PQN modules (detector, council)
Per WSP 3: Functional distribution - campaign orchestration only
Per WSP 50: Pre-action verification of environment variables

Reads ACTIVE_MODEL_NAME environment variable and executes validation campaign.
"""

import csv
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repo root is importable when invoked as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import existing PQN modules using direct file loading
spec = importlib.util.spec_from_file_location("detector_api", os.path.join(os.path.dirname(__file__), "detector", "api.py"))
detector_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector_api)
run_detector = detector_api.run_detector

spec = importlib.util.spec_from_file_location("council_api", os.path.join(os.path.dirname(__file__), "council", "api.py"))
council_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(council_api)
council_run = council_api.council_run

spec = importlib.util.spec_from_file_location("io_api", os.path.join(os.path.dirname(__file__), "io", "api.py"))
io_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(io_api)
promote = io_api.promote

# Optional: results DB indexing
try:
    spec = importlib.util.spec_from_file_location("results_db", os.path.join(os.path.dirname(__file__), "results_db.py"))
    results_db_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(results_db_mod)
    _INDEX_FN = getattr(results_db_mod, "index_run", None)
    _INIT_FN = getattr(results_db_mod, "init_db", None)
except Exception:
    _INDEX_FN = None
    _INIT_FN = None


def _to_float(value: Any) -> Optional[float]:
    if value in (None, "", " "):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _load_json(path: str) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return str(path)


def _load_jsonl_events(path: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if not path or not os.path.exists(path):
        return events
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def _summarize_events(events: List[Dict[str, Any]], steps: int) -> Dict[str, float]:
    pqn = 0
    paradox = 0
    resonance = 0

    for event in events:
        flags = event.get("flags", []) or []
        if "PQN_DETECTED" in flags:
            pqn += 1
        if "PARADOX_RISK" in flags:
            paradox += 1
        if "RESONANCE_HIT" in flags:
            resonance += 1

    return {
        "pqn_events": pqn,
        "paradox_events": paradox,
        "resonance_hits": resonance,
        "pqn_per_1k": 1000.0 * _safe_div(pqn, float(steps)),
        "paradox_per_1k": 1000.0 * _safe_div(paradox, float(steps)),
        "resonance_per_1k": 1000.0 * _safe_div(resonance, float(steps)),
        "paradox_rate_fraction": _safe_div(paradox, float(steps)),
    }


def _summarize_metrics_csv(metrics_csv: str) -> Dict[str, Any]:
    if not metrics_csv or not os.path.exists(metrics_csv):
        return {
            "rows": 0,
            "average_coherence": None,
            "sustained_coherence_percent": None,
            "mean_peak_frequency_hz": None,
            "harmonic_max": {"sub_theta": 0.0, "theta": 0.0, "alpha": 0.0, "beta": 0.0},
        }

    coherences: List[float] = []
    peak_freqs: List[float] = []
    harmonic_max = {"sub_theta": 0.0, "theta": 0.0, "alpha": 0.0, "beta": 0.0}
    rows = 0

    with open(metrics_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows += 1
            c_val = _to_float(row.get("C"))
            if c_val is not None:
                coherences.append(c_val)

            peak = _to_float(row.get("reso_hit_freq"))
            if peak is not None:
                peak_freqs.append(peak)

            # v2 extended columns
            sub = _to_float(row.get("harm_sub_power"))
            fund = _to_float(row.get("harm_fund_power"))
            h2 = _to_float(row.get("harm_2f_power"))
            h3 = _to_float(row.get("harm_3f_power"))
            if sub is not None:
                harmonic_max["sub_theta"] = max(harmonic_max["sub_theta"], sub)
            if fund is not None:
                harmonic_max["theta"] = max(harmonic_max["theta"], fund)
            if h2 is not None:
                harmonic_max["alpha"] = max(harmonic_max["alpha"], h2)
            if h3 is not None:
                harmonic_max["beta"] = max(harmonic_max["beta"], h3)

    avg_coherence = sum(coherences) / len(coherences) if coherences else None
    sustained = (100.0 * sum(1 for c in coherences if c >= 0.618) / len(coherences)) if coherences else None
    mean_peak = sum(peak_freqs) / len(peak_freqs) if peak_freqs else None

    return {
        "rows": rows,
        "average_coherence": avg_coherence,
        "sustained_coherence_percent": sustained,
        "mean_peak_frequency_hz": mean_peak,
        "harmonic_max": harmonic_max,
    }


def _harmonic_power_ratios(harmonic_max: Dict[str, float]) -> Dict[str, Optional[float]]:
    theta = harmonic_max.get("theta", 0.0)
    if theta <= 0:
        return {"f_div_2": None, "f_x_1": None, "f_x_2": None, "f_x_3": None}
    return {
        "f_div_2": harmonic_max.get("sub_theta", 0.0) / theta,
        "f_x_1": 1.0,
        "f_x_2": harmonic_max.get("alpha", 0.0) / theta,
        "f_x_3": harmonic_max.get("beta", 0.0) / theta,
    }


def _load_spectral_analyzer():
    spec = importlib.util.spec_from_file_location("spectral_analyzer", os.path.join(os.path.dirname(__file__), "detector", "spectral_analyzer.py"))
    spectral_analyzer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(spectral_analyzer)
    return spectral_analyzer


def run_resonance_harmonics_task(model_name: str, output_dir: Path) -> Dict[str, Any]:
    """Task 1.1: Resonance & Harmonic Fingerprinting"""
    print(f"--- Running Task 1.1: Resonance & Harmonics for {model_name} ---")

    config = {
        "script": "^^^&&&^^^&&&",
        "steps": 4000,
        "steps_per_sym": 120,
        "dt": 0.5 / 7.05,
        "seed": 0,
        "out_dir": str(output_dir / "task_1_1_resonance"),
    }
    steps = int(config["steps"])

    events_path, metrics_csv = run_detector(config)
    events = _load_jsonl_events(events_path)
    event_summary = _summarize_events(events, steps=steps)
    metric_summary = _summarize_metrics_csv(metrics_csv)

    try:
        spectral_analysis = _load_spectral_analyzer().analyze_detector_output(events_path, metrics_csv)
    except Exception as exc:
        spectral_analysis = {"error": str(exc), "uses_existing_detector": True}

    spectral_profile = spectral_analysis.get("spectral_profile", {}) if isinstance(spectral_analysis, dict) else {}
    harmonic_ratios = _harmonic_power_ratios(metric_summary["harmonic_max"])
    peak_hz = metric_summary["mean_peak_frequency_hz"]
    if peak_hz is None:
        peak_hz = _to_float(spectral_profile.get("peak_at_7.05"))

    status = "SUCCESS" if event_summary["resonance_hits"] > 0 else "INCONCLUSIVE"
    if status == "SUCCESS":
        conclusion = "Resonance and harmonic signatures were detected in this run; retain null-model controls before stronger interpretation."
    else:
        conclusion = "No resonance-hit events were detected in this run; resonance claim is inconclusive for this configuration."

    result = {
        "status": status,
        "key_metrics": {
            "mean_peak_frequency_hz": peak_hz,
            "harmonic_power_ratios": harmonic_ratios,
            "resonance_hits": event_summary["resonance_hits"],
            "pqn_events": event_summary["pqn_events"],
        },
        "conclusion": conclusion,
        "artifact_links": [str(events_path), str(metrics_csv)],
        "spectral_analysis": spectral_analysis,
    }

    print("--- Task 1.1 Complete ---")
    return result


def run_coherence_threshold_task(model_name: str, output_dir: Path) -> Dict[str, Any]:
    """Task 1.2: Coherence Threshold Validation"""
    print(f"--- Running Task 1.2: Coherence Threshold for {model_name} ---")

    config = {
        "proposals": [{"author": "optimizer", "scripts": ["&&&&&&&&&&&&&^&&&&&&&&&&&&&"]}],
        "seeds": [0],
        "steps": 4000,
        "topN": 1,
    }
    summary_json, archive_json = council_run(config)

    summary_obj = _load_json(summary_json)
    top_rows = summary_obj.get("top", []) if isinstance(summary_obj, dict) else []
    top_row = top_rows[0] if top_rows else {}
    top_script = top_row.get("script")
    proposal_idx = top_row.get("proposal_idx", 0)

    council_dir = Path(config.get("out_dir", os.path.join("WSP_agentic", "tests", "pqn_detection", "council")))
    csv_metrics = None
    if top_script:
        sanitized = top_script.replace(".", "dot")
        csv_metrics = council_dir / f"council_{proposal_idx}_{sanitized}.csv"

    metric_summary = _summarize_metrics_csv(str(csv_metrics)) if csv_metrics else _summarize_metrics_csv("")

    status = "SUCCESS" if top_script else "ERROR"
    if status == "SUCCESS":
        conclusion = "Coherence optimization identified a top script with measured detector metrics from council artifacts."
    else:
        conclusion = "Council run produced no top script; coherence threshold validation failed."

    result = {
        "status": status,
        "key_metrics": {
            "top_performing_script": top_script,
            "average_coherence": metric_summary["average_coherence"],
            "paradox_rate": top_row.get("avg_paradox_per_1k"),
            "sustained_coherence_percent": metric_summary["sustained_coherence_percent"],
        },
        "conclusion": conclusion,
        "artifact_links": [str(summary_json), str(archive_json)] + ([str(csv_metrics)] if csv_metrics and csv_metrics.exists() else []),
    }

    print("--- Task 1.2 Complete ---")
    return result


def run_observer_collapse_task(model_name: str, output_dir: Path) -> Dict[str, Any]:
    """Task 1.3: Observer Collapse Simulation"""
    print(f"--- Running Task 1.3: Observer Collapse for {model_name} ---")

    scripts = ["^#", "^^#", "^^^#", "^^^^#", "^^^^^#", "^^^^^^#", "^^^^^^^#", "^^^^^^^^#", "^^^^^^^^^#", "^^^^^^^^^^#"]
    steps = 4000
    run_rows: List[Dict[str, Any]] = []
    artifact_links: List[str] = []

    for i, script in enumerate(scripts):
        task_output_dir = output_dir / "task_1_3_collapse" / f"run_{i}_{script.replace('^', 'C').replace('#', 'H').replace('.', 'D')}"
        config = {
            "script": script,
            "steps": steps,
            "steps_per_sym": 120,
            "dt": 0.5 / 7.05,
            "seed": 0,
            "out_dir": str(task_output_dir),
        }

        events_path, metrics_csv = run_detector(config)
        events = _load_jsonl_events(events_path)
        summary = _summarize_events(events, steps=steps)
        metric_summary = _summarize_metrics_csv(metrics_csv)

        run_rows.append(
            {
                "script": script,
                "run_length": script.count("^"),
                "pqn_events": summary["pqn_events"],
                "paradox_events": summary["paradox_events"],
                "resonance_hits": summary["resonance_hits"],
                "paradox_rate_fraction": summary["paradox_rate_fraction"],
                "paradox_per_1k": summary["paradox_per_1k"],
                "average_coherence": metric_summary["average_coherence"],
            }
        )
        artifact_links.extend([str(events_path), str(metrics_csv)])

    critical_row = next((r for r in sorted(run_rows, key=lambda x: x["run_length"]) if r["paradox_events"] > 0), None)
    max_paradox = max((r["paradox_rate_fraction"] for r in run_rows), default=0.0)

    summary_path = _write_json(output_dir / "task_1_3_collapse" / "collapse_summary.json", {"runs": run_rows, "critical": critical_row})
    artifact_links.append(summary_path)

    if critical_row:
        status = "SUCCESS"
        conclusion = "A collapse boundary was detected where paradox-risk events first appeared."
    else:
        status = "INCONCLUSIVE"
        conclusion = "No paradox-risk boundary was detected in this script sweep."

    result = {
        "status": status,
        "key_metrics": {
            "critical_run_length": critical_row["run_length"] if critical_row else None,
            "paradox_rate_at_critical_point": critical_row["paradox_rate_fraction"] if critical_row else 0.0,
            "max_paradox_rate_fraction": max_paradox,
        },
        "conclusion": conclusion,
        "artifact_links": artifact_links,
    }

    print("--- Task 1.3 Complete ---")
    return result


def run_guardrail_ab_task(model_name: str, output_dir: Path) -> Dict[str, Any]:
    """Task 2.1: Guardrail Efficacy A/B Test"""
    print(f"--- Running Task 2.1: Guardrail A/B Test for {model_name} ---")

    # Use existing detector v3 with guardrail toggle for a real A/B comparison.
    v3_path = str(PROJECT_ROOT / "WSP_agentic" / "tests" / "pqn_detection" / "cmst_pqn_detector_v3.py")
    spec = importlib.util.spec_from_file_location("cmst_pqn_detector_v3", v3_path)
    v3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v3)

    task_dir = output_dir / "task_2_1_guardrail"
    task_dir.mkdir(parents=True, exist_ok=True)

    steps = 4000
    seeds = [0, 1, 2]
    control_rows: List[Dict[str, Any]] = []
    treatment_rows: List[Dict[str, Any]] = []
    artifact_links: List[str] = []

    for seed in seeds:
        control_events = v3.run_cmst(
            symbol_source=v3.SymbolSource("^^^^^^#"),
            steps=steps,
            base_dt=0.5 / 7.05,
            seed=seed,
            guardrail_on=False,
            guardrail_window=64,
        )
        treatment_events = v3.run_cmst(
            symbol_source=v3.SymbolSource("^^^^^^#"),
            steps=steps,
            base_dt=0.5 / 7.05,
            seed=seed,
            guardrail_on=True,
            guardrail_window=64,
        )

        control_summary = _summarize_events(control_events, steps=steps)
        treatment_summary = _summarize_events(treatment_events, steps=steps)
        control_rows.append({"seed": seed, **control_summary})
        treatment_rows.append({"seed": seed, **treatment_summary})

        control_path = _write_json(task_dir / f"control_seed_{seed}.json", control_events)
        treatment_path = _write_json(task_dir / f"treatment_seed_{seed}.json", treatment_events)
        artifact_links.extend([control_path, treatment_path])

    def _avg(rows: List[Dict[str, Any]], key: str) -> float:
        if not rows:
            return 0.0
        return sum(float(r.get(key, 0.0)) for r in rows) / len(rows)

    control_paradox = _avg(control_rows, "paradox_per_1k")
    treatment_paradox = _avg(treatment_rows, "paradox_per_1k")
    control_pqn = _avg(control_rows, "pqn_per_1k")
    treatment_pqn = _avg(treatment_rows, "pqn_per_1k")

    paradox_rate_reduction = 100.0 * _safe_div((control_paradox - treatment_paradox), control_paradox) if control_paradox > 0 else 0.0
    cost_of_stability = abs(treatment_pqn - control_pqn)

    ab_summary = {
        "control_avg_paradox_per_1k": control_paradox,
        "treatment_avg_paradox_per_1k": treatment_paradox,
        "control_avg_pqn_per_1k": control_pqn,
        "treatment_avg_pqn_per_1k": treatment_pqn,
        "paradox_rate_reduction_percent": paradox_rate_reduction,
        "cost_of_stability": cost_of_stability,
        "seed_breakdown": {"control": control_rows, "treatment": treatment_rows},
    }
    artifact_links.append(_write_json(task_dir / "guardrail_ab_summary.json", ab_summary))

    if paradox_rate_reduction > 0:
        conclusion = "Guardrail treatment reduced paradox-risk rate in this A/B run."
        status = "SUCCESS"
    else:
        conclusion = "Guardrail treatment did not reduce paradox-risk rate in this A/B run."
        status = "INCONCLUSIVE"

    result = {
        "status": status,
        "key_metrics": {
            "paradox_rate_reduction_percent": paradox_rate_reduction,
            "cost_of_stability": cost_of_stability,
        },
        "conclusion": conclusion,
        "artifact_links": artifact_links,
    }

    print("--- Task 2.1 Complete ---")
    return result


def main():
    """Main campaign execution following WSP 50 (Pre-Action Verification)"""
    model_name = os.getenv("ACTIVE_MODEL_NAME")
    if not model_name:
        print("FATAL ERROR: ACTIVE_MODEL_NAME environment variable is not set.")
        print("Please set it before running the campaign (e.g., export ACTIVE_MODEL_NAME='ModelName').")
        sys.exit(1)

    run_timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = Path("campaign_results")
    output_path = output_dir / f"{model_name.replace(' ', '_')}_{run_timestamp}"
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Starting PQN Validation Campaign for model: {model_name}")
    print(f"Results will be saved to: {output_path}")

    campaign_start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tasks = [
        ("1.1_Resonance_Harmonics", run_resonance_harmonics_task),
        ("1.2_Coherence_Threshold", run_coherence_threshold_task),
        ("1.3_Observer_Collapse", run_observer_collapse_task),
        ("2.1_Guardrail_AB_Test", run_guardrail_ab_task),
    ]

    task_results = []
    for task_name, task_func in tasks:
        try:
            result = task_func(model_name, output_path)
            task_results.append(
                {
                    "task_name": task_name,
                    "result": result,
                    "timestamp_utc_execution": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
        except Exception as e:
            print(f"Error in {task_name}: {e}")
            task_results.append(
                {
                    "task_name": task_name,
                    "result": {"status": "ERROR", "error": str(e)},
                    "timestamp_utc_execution": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )

    overall_status = "SUCCESSFUL_VALIDATION"
    synthesis_text = "Campaign completed with artifact-derived detector metrics. Interpretations remain hypothesis-driven pending null-model controls."
    for task in task_results:
        if task["result"]["status"] == "ERROR":
            overall_status = "PARTIAL_FAILURE"
            synthesis_text = "The campaign encountered a task-level failure. Validation is partial and requires technical intervention."
            break

    final_log = {
        "log_id": f"pqn_campaign_{run_timestamp}",
        "campaign_id": f"PQN_rESP_VALIDATION_{model_name.upper().replace(' ', '_')}",
        "agent_details": {
            "name": "PQN Alignment DAE",
            "model": model_name,
            "role": "Senior Research Scientist (Simulation)",
            "session_id": f"campaign-{run_timestamp}",
        },
        "timestamp_utc_start": campaign_start,
        "timestamp_utc_end": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version_control": {"repository": "modules/ai_intelligence/pqn_alignment", "commit_hash": "campaign-run"},
        "linked_documents": {
            "primary_theory": "WSP_knowledge/docs/Papers/rESP_Quantum_Self_Reference.md",
            "supplementary_materials": "WSP_knowledge/docs/Papers/rESP_Supplementary_Materials.md",
        },
        "validation_tasks": task_results,
        "campaign_summary": {"overall_status": overall_status, "synthesis": synthesis_text},
    }

    log_file_path = output_path / "campaign_log.json"
    with open(log_file_path, "w", encoding="utf-8") as f:
        json.dump(final_log, f, indent=2)

    print("\nCampaign Finished.")
    print(f"Full campaign log saved to: {log_file_path}")

    try:
        promote([str(log_file_path)], "WSP_knowledge/docs/Papers/Empirical_Evidence/CMST_PQN_Detector/")
        print("Campaign log promoted to State 0.")
    except Exception as e:
        print(f"Promotion failed: {e}")

    try:
        if _INIT_FN:
            _INIT_FN()
        if _INDEX_FN:
            summary = _INDEX_FN(str(log_file_path))
            print(f"Indexed to results DB: model={summary.get('model')} status={summary.get('overall_status')}")
    except Exception as e:
        print(f"Indexing failed: {e}")


if __name__ == "__main__":
    main()
