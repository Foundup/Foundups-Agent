from __future__ import annotations

import json
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Generator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from modules.ai_intelligence.pqn_alignment.src.detector.api import run_detector  # type: ignore
from modules.ai_intelligence.pqn_alignment.src.results_db import query_runs  # type: ignore
from .docs import get_docs_index


app = FastAPI(title="PQN Portal FoundUp (PoC)")

# Minimal CORS for Prototype web pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


_RUNS: Dict[str, Dict[str, Any]] = {}
_OUTPUT_ROOT = Path("campaign_results")


def _start_demo_run(run_id: str) -> None:
	"""Execute a short, safe PQN demo run and write artifacts under campaign_results."""
	run_dir = _OUTPUT_ROOT / f"PortalDemo_{run_id}"
	run_dir.mkdir(parents=True, exist_ok=True)
	try:
		config = {
			"script": "^^^&&&^^^",
			"steps": 400,
			"steps_per_sym": 60,
			"dt": 0.5/7.05,
			"seed": 0,
			"out_dir": str(run_dir)
		}
		events_path, metrics_csv = run_detector(config)
		_RUNS[run_id].update({
			"status": "finished",
			"events": str(events_path),
			"metrics": str(metrics_csv),
			"dir": str(run_dir),
		})
	except Exception as e:
		_RUNS[run_id].update({"status": "error", "error": str(e)})


@app.get("/docs")
def docs_index() -> JSONResponse:
	return JSONResponse(get_docs_index())


@app.get("/docs/index.json")
def docs_index_json() -> JSONResponse:
	return JSONResponse(get_docs_index())


@app.post("/runs/demo")
def start_demo() -> JSONResponse:
	run_id = uuid.uuid4().hex[:12]
	_RUNS[run_id] = {"status": "running", "started": time.time()}
	threading.Thread(target=_start_demo_run, args=(run_id,), daemon=True).start()
	return JSONResponse({"run_id": run_id, "status": "running"})


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> JSONResponse:
	info = _RUNS.get(run_id)
	if not info:
		raise HTTPException(status_code=404, detail="run not found")
	return JSONResponse(info)


def _sse_lines(path: Path, timeout_s: float = 25.0) -> Generator[bytes, None, None]:
	"""Yield SSE lines from a JSONL file as it grows."""
	start = time.time()
	while not path.exists() and time.time() - start < timeout_s:
		time.sleep(0.1)
	
	if not path.exists():
		yield b"event: done\ndata: {\"status\":\"timeout\"}\n\n"
		return

	with open(path, "r", encoding="utf-8") as f:
		pos = 0
		while time.time() - start < timeout_s:
			f.seek(pos)
			line = f.readline()
			if not line:
				time.sleep(0.2)
				continue
			pos = f.tell()
			try:
				obj = json.loads(line)
				payload = json.dumps({
					"t": obj.get("t"),
					"coherence": obj.get("coherence"),
					"paradox_flag": bool("PARADOX_RISK" in (obj.get("flags") or [])),
					"spectrum": obj.get("spectrum"),
				})
			except Exception:
				payload = json.dumps({"raw": line.strip()})
			yield f"event: metric\ndata: {payload}\n\n".encode("utf-8")
		yield b"event: done\ndata: {\"status\":\"complete\"}\n\n"


@app.get("/runs/{run_id}/stream")
def stream_run(run_id: str) -> StreamingResponse:
	info = _RUNS.get(run_id)
	if not info:
		raise HTTPException(status_code=404, detail="run not found")
	path = Path(info.get("events") or "")
	return StreamingResponse(_sse_lines(path), media_type="text/event-stream")


@app.get("/gallery")
def gallery() -> JSONResponse:
	rows = query_runs({})
	# Reduce payload size for PoC
	min_rows = [
		{
			"model": r.get("model"),
			"status": r.get("overall_status"),
			"resonance_peak": r.get("resonance_peak"),
			"coherence_avg": r.get("coherence_avg"),
			"collapse_critical": r.get("collapse_critical"),
			"log": r.get("log_path"),
		}
		for r in rows
	]
	return JSONResponse({"runs": min_rows})


# Run via: uvicorn modules.foundups.pqn_portal.src.api:app --reload --port 8080

