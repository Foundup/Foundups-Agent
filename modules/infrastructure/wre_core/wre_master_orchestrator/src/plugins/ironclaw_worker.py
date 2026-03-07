#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IronClaw worker plugin for WRE master orchestrator.

Provides a thin execution worker that sends structured tasks to IronClaw's
OpenAI-compatible gateway and returns normalized WRE-friendly results.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator import (
    OrchestratorPlugin,
)


class IronClawWorkerPlugin(OrchestratorPlugin):
    """WRE plugin adapter for IronClaw worker tasks."""

    SUPPORTED_WORK_TYPES = {"builder", "twin", "sim", "custom"}

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__("ironclaw_worker")
        self.repo_root = Path(repo_root).resolve() if repo_root else Path.cwd()
        self._last_status: Dict[str, Any] = {
            "success": False,
            "available": False,
            "message": "No IronClaw worker task has run in this session",
        }

    @staticmethod
    def _normalize_work_type(raw: Any) -> str:
        work_type = str(raw or "custom").strip().lower()
        if work_type not in IronClawWorkerPlugin.SUPPORTED_WORK_TYPES:
            return "custom"
        return work_type

    @staticmethod
    def _build_system_prompt(work_type: str) -> str:
        prompts = {
            "builder": (
                "You are an IronClaw builder worker for FoundUps. "
                "Return concise, deterministic implementation guidance."
            ),
            "twin": (
                "You are an IronClaw digital-twin worker for FoundUps. "
                "Respect policy boundaries and output actionable next steps."
            ),
            "sim": (
                "You are an IronClaw simulator worker for FoundUps. "
                "Optimize for reproducibility, consistency, and measurable KPIs."
            ),
            "custom": (
                "You are an IronClaw worker for FoundUps. "
                "Respond with concise structured output."
            ),
        }
        return prompts.get(work_type, prompts["custom"])

    @staticmethod
    def _serialize_payload(payload: Any) -> str:
        if isinstance(payload, str):
            return payload.strip()
        if payload is None:
            return ""
        try:
            return json.dumps(payload, ensure_ascii=True, sort_keys=True)
        except Exception:
            return str(payload).strip()

    @staticmethod
    def _safe_int(raw: Any, default: int) -> int:
        try:
            return int(raw)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_float(raw: Any, default: float) -> float:
        try:
            return float(raw)
        except (TypeError, ValueError):
            return default

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a worker task through IronClaw gateway."""
        started_at = time.time()
        work_type = self._normalize_work_type(task.get("work_type") or task.get("type"))
        payload = task.get("input_payload", task.get("payload", task.get("task")))
        user_message = task.get("user_message") or self._serialize_payload(payload)
        user_message = str(user_message or "").strip()
        if not user_message:
            result = {
                "success": False,
                "available": False,
                "plugin": self.name,
                "work_type": work_type,
                "error": "Missing user_message/input_payload for IronClaw worker task",
                "duration_ms": int((time.time() - started_at) * 1000),
            }
            self._last_status = result
            return result

        max_tokens = max(32, min(self._safe_int(task.get("max_tokens", 300), 300), 2048))
        temperature = max(0.0, min(self._safe_float(task.get("temperature", 0.2), 0.2), 2.0))
        system_prompt = str(task.get("system_prompt") or self._build_system_prompt(work_type))
        require_healthy = bool(task.get("require_healthy", False))

        try:
            from modules.communication.moltbot_bridge.src.ironclaw_gateway_client import (
                IronClawGatewayClient,
            )

            client = IronClawGatewayClient()
            healthy, health_detail = client.health()
            models = client.list_models()

            if require_healthy and not healthy:
                result = {
                    "success": False,
                    "available": True,
                    "plugin": self.name,
                    "work_type": work_type,
                    "error": f"IronClaw unhealthy: {health_detail}",
                    "health_detail": health_detail,
                    "base_url": client.config.base_url,
                    "model": client.config.model,
                    "duration_ms": int((time.time() - started_at) * 1000),
                }
                self._last_status = result
                return result

            response = client.chat_completion(
                user_message=user_message,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            success = bool(response and response.strip())
            result = {
                "success": success,
                "available": True,
                "plugin": self.name,
                "work_type": work_type,
                "response": (response or "").strip(),
                "base_url": client.config.base_url,
                "model": client.config.model,
                "models": models,
                "models_count": len(models),
                "healthy": healthy,
                "health_detail": health_detail,
                "key_isolation": bool(client.config.no_api_keys),
                "duration_ms": int((time.time() - started_at) * 1000),
            }
            if not success:
                result["error"] = "Empty response from IronClaw gateway"
            self._last_status = result
            return result

        except Exception as exc:
            result = {
                "success": False,
                "available": False,
                "plugin": self.name,
                "work_type": work_type,
                "error": f"IronClaw worker execution failed: {exc}",
                "duration_ms": int((time.time() - started_at) * 1000),
            }
            self._last_status = result
            return result

    def get_runtime_status(self) -> Dict[str, Any]:
        """Return last execution/runtime status snapshot."""
        return dict(self._last_status)
