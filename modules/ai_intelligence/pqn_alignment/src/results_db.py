"""
Results database (SQLite) for PQN campaigns and council optimization.

Public API:
- init_db(db_path: Optional[str]) -> None
- index_run(log_path: str, db_path: Optional[str]) -> dict
- index_council_run(summary_path: str, db_path: Optional[str]) -> dict
- query_runs(filters: Dict[str, object], db_path: Optional[str]) -> list[dict]

Default DB location: modules/ai_intelligence/pqn_alignment/results.db
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


def _default_db_path() -> str:
    # src/ -> module root
    module_root = Path(__file__).resolve().parents[1]
    return str(module_root / "results.db")


def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    db = db_path or _default_db_path()
    os.makedirs(os.path.dirname(db), exist_ok=True)
    return sqlite3.connect(db)


def init_db(db_path: Optional[str] = None) -> None:
    """Create results schema if it does not exist."""
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT,
                run_id TEXT NOT NULL,
                run_dir TEXT,
                start_ts TEXT,
                end_ts TEXT,
                overall_status TEXT,
                resonance_peak REAL,
                h_f_div2 REAL,
                h_f2 REAL,
                h_f3 REAL,
                coherence_avg REAL,
                coherence_sustained REAL,
                coherence_paradox REAL,
                collapse_critical INTEGER,
                guardrail_reduction REAL,
                guardrail_cost REAL,
                steps INTEGER,
                dt REAL,
                noise_H REAL,
                noise_L REAL,
                top_script TEXT,
                top_score REAL,
                run_type TEXT DEFAULT 'campaign',
                log_path TEXT UNIQUE
            )
            """
        )
        conn.commit()


def _get_task(tasks: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    for t in tasks:
        if t.get("task_name") == name:
            return t
    return None


def index_run(log_path: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Parse a campaign_log.json and insert a summary row into the DB.

    Returns a dict with inserted summary values.
    """
    init_db(db_path)

    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    run_dir = str(Path(log_path).resolve().parent)
    run_id = Path(run_dir).name
    model = data.get("agent_details", {}).get("model", "unknown")
    start_ts = data.get("timestamp_utc_start")
    end_ts = data.get("timestamp_utc_end")
    overall_status = data.get("campaign_summary", {}).get("overall_status")

    tasks: List[Dict[str, Any]] = data.get("validation_tasks", [])

    # Task 1.1
    t11 = _get_task(tasks, "1.1_Resonance_Harmonics") or {}
    t11r = (t11.get("result") or {})
    resonance_peak = (t11r.get("key_metrics") or {}).get("mean_peak_frequency_hz")
    h_ratios = (t11r.get("key_metrics") or {}).get("harmonic_power_ratios") or {}
    h_f_div2 = h_ratios.get("f_div_2")
    h_f2 = h_ratios.get("f_x_2")
    h_f3 = h_ratios.get("f_x_3")

    # Task 1.2
    t12 = _get_task(tasks, "1.2_Coherence_Threshold") or {}
    t12r = (t12.get("result") or {})
    c_metrics = (t12r.get("key_metrics") or {})
    coherence_avg = c_metrics.get("average_coherence")
    coherence_sustained = c_metrics.get("sustained_coherence_percent")
    coherence_paradox = c_metrics.get("paradox_rate")

    # Task 1.3
    t13 = _get_task(tasks, "1.3_Observer_Collapse") or {}
    t13r = (t13.get("result") or {})
    collapse_critical = (t13r.get("key_metrics") or {}).get("critical_run_length")

    # Task 2.1
    t21 = _get_task(tasks, "2.1_Guardrail_AB_Test") or {}
    t21r = (t21.get("result") or {})
    g_metrics = (t21r.get("key_metrics") or {})
    guardrail_reduction = g_metrics.get("paradox_rate_reduction_percent")
    guardrail_cost = g_metrics.get("cost_of_stability")

    summary = {
        "model": model,
        "run_id": run_id,
        "run_dir": run_dir,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "overall_status": overall_status,
        "resonance_peak": resonance_peak,
        "h_f_div2": h_f_div2,
        "h_f2": h_f2,
        "h_f3": h_f3,
        "coherence_avg": coherence_avg,
        "coherence_sustained": coherence_sustained,
        "coherence_paradox": coherence_paradox,
        "collapse_critical": collapse_critical,
        "guardrail_reduction": guardrail_reduction,
        "guardrail_cost": guardrail_cost,
        "steps": None,
        "dt": None,
        "noise_H": None,
        "noise_L": None,
        "top_script": None,
        "top_score": None,
        "run_type": "campaign",
        "log_path": str(Path(log_path).resolve()),
    }

    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO runs (
                model, run_id, run_dir, start_ts, end_ts, overall_status,
                resonance_peak, h_f_div2, h_f2, h_f3,
                coherence_avg, coherence_sustained, coherence_paradox,
                collapse_critical, guardrail_reduction, guardrail_cost,
                steps, dt, noise_H, noise_L, top_script, top_score, run_type, log_path
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                summary["model"], summary["run_id"], summary["run_dir"], summary["start_ts"], summary["end_ts"], summary["overall_status"],
                summary["resonance_peak"], summary["h_f_div2"], summary["h_f2"], summary["h_f3"],
                summary["coherence_avg"], summary["coherence_sustained"], summary["coherence_paradox"],
                summary["collapse_critical"], summary["guardrail_reduction"], summary["guardrail_cost"],
                summary["steps"], summary["dt"], summary["noise_H"], summary["noise_L"], 
                summary["top_script"], summary["top_score"], summary["run_type"], summary["log_path"],
            ),
        )
        conn.commit()

    return summary


def index_council_run(summary_path: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Index a council summary.json into the DB.
    
    Returns a dict with inserted summary values.
    """
    init_db(db_path)
    
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Council summary not found: {summary_path}")
    
    with open(summary_path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    
    # Extract top script and score
    top = (obj.get("top") or [])
    top_script = None
    top_score = None
    if top:
        first = top[0]
        top_script = first.get("script")
        top_score = float(first.get("score", 0.0))
    
    # Extract execution parameters from results
    results = obj.get("results") or []
    steps = None
    dt = None
    noise_H = None
    noise_L = None
    if results:
        # Heuristic: extract from first result if present
        row = results[0]
        steps = int(row.get("steps", 0)) if "steps" in row else None
        dt = float(row.get("dt", 0.0)) if "dt" in row else None
        noise_H = float(row.get("noise_H", 0.0)) if "noise_H" in row else None
        noise_L = float(row.get("noise_L", 0.0)) if "noise_L" in row else None
    
    run_id = os.path.basename(os.path.dirname(summary_path)) or "council_run"
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    
    summary = {
        "model": None,
        "run_id": run_id,
        "run_dir": str(Path(summary_path).resolve().parent),
        "start_ts": timestamp,
        "end_ts": timestamp,
        "overall_status": "COUNCIL_OPTIMIZATION",
        "resonance_peak": None,
        "h_f_div2": None,
        "h_f2": None,
        "h_f3": None,
        "coherence_avg": None,
        "coherence_sustained": None,
        "coherence_paradox": None,
        "collapse_critical": None,
        "guardrail_reduction": None,
        "guardrail_cost": None,
        "steps": steps,
        "dt": dt,
        "noise_H": noise_H,
        "noise_L": noise_L,
        "top_script": top_script,
        "top_score": top_score,
        "run_type": "council",
        "log_path": str(Path(summary_path).resolve()),
    }
    
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO runs (
                model, run_id, run_dir, start_ts, end_ts, overall_status,
                resonance_peak, h_f_div2, h_f2, h_f3,
                coherence_avg, coherence_sustained, coherence_paradox,
                collapse_critical, guardrail_reduction, guardrail_cost,
                steps, dt, noise_H, noise_L, top_script, top_score, run_type, log_path
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                summary["model"], summary["run_id"], summary["run_dir"], summary["start_ts"], summary["end_ts"], summary["overall_status"],
                summary["resonance_peak"], summary["h_f_div2"], summary["h_f2"], summary["h_f3"],
                summary["coherence_avg"], summary["coherence_sustained"], summary["coherence_paradox"],
                summary["collapse_critical"], summary["guardrail_reduction"], summary["guardrail_cost"],
                summary["steps"], summary["dt"], summary["noise_H"], summary["noise_L"], 
                summary["top_script"], summary["top_score"], summary["run_type"], summary["log_path"],
            ),
        )
        conn.commit()
    
    return summary


def query_runs(filters: Dict[str, object] | None = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query indexed runs with simple equality filters.
    Example: query_runs({"model": "gpt-5", "overall_status": "SUCCESSFUL_VALIDATION"})
    """
    filters = filters or {}
    where: List[str] = []
    params: List[object] = []
    for k, v in filters.items():
        where.append(f"{k} = ?")
        params.append(v)
    sql = "SELECT * FROM runs"
    if where:
        sql += " WHERE " + " AND ".join(where)

    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def query_cross_analysis(filters: Dict[str, object] | None = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query across campaign and council results for comparative analysis.
    
    Example: query_cross_analysis({
        "run_type": "campaign",
        "resonance_peak": {"min": 7.0, "max": 7.1}
    })
    """
    # Enhanced querying for cross-analysis
    # TODO: Implement range queries and complex filters
    return query_runs(filters, db_path)
