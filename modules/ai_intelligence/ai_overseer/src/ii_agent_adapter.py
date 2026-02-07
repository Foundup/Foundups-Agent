#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
II-Agent Adapter for AI_overseer

Purpose:
- Provide optional external-agent execution behind a feature flag.
- Keep AI_overseer orchestration stable while enabling pilot use.
"""

from __future__ import annotations

import json
import logging
import os
import shlex
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class IIAgentAdapter:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.enabled = os.getenv("II_AGENT_ENABLED", "false").lower() in ("1", "true", "yes")
        self.mode = os.getenv("II_AGENT_MODE", "cli").lower()
        self.timeout_sec = int(os.getenv("II_AGENT_TIMEOUT_SEC", "300"))
        self.cli_path = os.getenv("II_AGENT_CLI", "").strip()
        self.command_template = os.getenv("II_AGENT_COMMAND", "").strip()
        self.endpoint = os.getenv("II_AGENT_ENDPOINT", "").strip()
        self.llm_base_url = os.getenv("II_AGENT_LLM_BASE_URL", "").strip()
        self.llm_auto_start = os.getenv("II_AGENT_LLM_AUTO_START", "false").lower() in ("1", "true", "yes")
        self.llm_start_script = os.getenv("II_AGENT_LLM_START_SCRIPT", "").strip()
        self.llm_start_timeout = int(os.getenv("II_AGENT_LLM_START_TIMEOUT_SEC", "60"))

    def run_mission(self, mission_description: str, mission_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "success": False,
                "skipped": True,
                "reason": "II_AGENT_ENABLED not set",
            }

        payload = {
            "mission": mission_description,
            "mission_type": mission_type,
            "context": context or {},
        }

        if self.mode == "http":
            return self._run_http(payload)

        return self._run_cli(payload)

    def _run_cli(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.llm_auto_start and self.llm_base_url:
            ready = self._ensure_llm_ready()
            if not ready:
                return {"success": False, "error": "Local LLM not ready (auto-start failed)"}

        if self.command_template:
            command = self.command_template.format(task=payload["mission"])
            args = shlex.split(command)
        elif self.cli_path:
            args = [self.cli_path, "--task", payload["mission"]]
        else:
            return {"success": False, "error": "II_AGENT_CLI or II_AGENT_COMMAND not configured"}

        try:
            proc = subprocess.run(
                args,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                check=False,
            )
            return {
                "success": proc.returncode == 0,
                "method": "cli",
                "command": " ".join(args),
                "stdout": proc.stdout[-8000:],
                "stderr": proc.stderr[-8000:],
                "return_code": proc.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"II-Agent CLI timed out after {self.timeout_sec}s"}
        except Exception as exc:
            return {"success": False, "error": f"II-Agent CLI error: {exc}"}

    def _ensure_llm_ready(self) -> bool:
        health_urls = []
        base = self.llm_base_url.rstrip("/")
        if base.endswith("/v1"):
            health_urls.append(f"{base}/models")
        else:
            health_urls.append(f"{base}/v1/models")

        if self._check_urls(health_urls):
            return True

        if self.llm_start_script:
            try:
                subprocess.Popen(
                    [
                        "powershell",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        self.llm_start_script,
                    ],
                    cwd=str(self.repo_root),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as exc:
                logger.error("Failed to start LLM server: %s", exc)
                return False

        # Wait for the server to come up
        deadline = self.timeout_sec if self.llm_start_timeout <= 0 else self.llm_start_timeout
        for _ in range(deadline):
            if self._check_urls(health_urls):
                return True
            time.sleep(1)
        return False

    def _check_urls(self, urls: list[str]) -> bool:
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                continue
        return False

    def _run_http(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.endpoint:
            return {"success": False, "error": "II_AGENT_ENDPOINT not configured"}

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.endpoint, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            return {"success": True, "method": "http", "response": body}
        except Exception as exc:
            return {"success": False, "error": f"II-Agent HTTP error: {exc}"}
