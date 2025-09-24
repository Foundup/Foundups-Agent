from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def record_advisor_event(telemetry_path: Path, payload: Dict[str, Any]) -> None:
    """Append an advisor event to the JSONL telemetry file (best-effort)."""

    try:
        telemetry_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {**payload, "timestamp": datetime.now(UTC).isoformat()}
        with telemetry_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as exc:  # pragma: no cover - safety log
        logger.debug("Failed to record advisor telemetry: %s", exc)
