"""
Results database (minimal)
- init_db(db_path): create tables if missing
- index_summary(db_path, summary_json_path): insert a top-row summary

Schema (initial):
- runs(id INTEGER PK, run_id TEXT, timestamp TEXT, steps INT, dt REAL, noise_H REAL, noise_L REAL,
       top_script TEXT, top_score REAL, summary_json_path TEXT)
"""
from typing import Optional
import json
import os
import sqlite3
from datetime import datetime


def init_db(db_path: str) -> None:
	if not db_path:
		raise ValueError("db_path is required")
	dirname = os.path.dirname(db_path)
	if dirname:
		os.makedirs(dirname, exist_ok=True)
	with sqlite3.connect(db_path) as con:
		cur = con.cursor()
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS runs (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				run_id TEXT,
				timestamp TEXT,
				steps INTEGER,
				dt REAL,
				noise_H REAL,
				noise_L REAL,
				top_script TEXT,
				top_score REAL,
				summary_json_path TEXT
			)
			"""
		)
		con.commit()


def index_summary(db_path: str, summary_json_path: str) -> Optional[int]:
	"""
	Index a council summary.json into the DB. Returns inserted row id or None.
	Minimal extraction: uses the first top entry as representative.
	"""
	if not os.path.exists(summary_json_path):
		return None
	with open(summary_json_path, "r", encoding="utf-8") as f:
		obj = json.load(f)
	top = (obj.get("top") or [])
	top_script = None
	top_score = None
	if top:
		first = top[0]
		top_script = first.get("script")
		top_score = float(first.get("score", 0.0))
	# Attempt to extract minimal context (if present)
	results = obj.get("results") or []
	steps = None
	dt = None
	nH = None
	nL = None
	if results:
		# Heuristic: not all summaries include these fields; keep None if absent
		row = results[0]
		steps = int(row.get("steps", 0)) if "steps" in row else None
		dt = float(row.get("dt", 0.0)) if "dt" in row else None
		nH = float(row.get("noise_H", 0.0)) if "noise_H" in row else None
		nL = float(row.get("noise_L", 0.0)) if "noise_L" in row else None
	with sqlite3.connect(db_path) as con:
		cur = con.cursor()
		cur.execute(
			"""
			INSERT INTO runs(run_id, timestamp, steps, dt, noise_H, noise_L, top_script, top_score, summary_json_path)
			VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
			""",
			(
				os.path.basename(os.path.dirname(summary_json_path)) or "",
				datetime.utcnow().isoformat(timespec="seconds"),
				steps,
				dt,
				nH,
				nL,
				top_script,
				top_score,
				summary_json_path,
			),
		)
		con.commit()
		return cur.lastrowid
