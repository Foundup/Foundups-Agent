#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw security sentinel driven by AI Overseer.

Runs the OpenClaw skill safety scan and persists a TTL-bounded cache so
startup/runtime checks remain deterministic and auditable.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

from typing import Any, Dict, List, Optional, Set, Tuple
import subprocess
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class OpenClawSecurityStatus:
    available: bool
    passed: bool
    required: bool
    enforced: bool
    cached: bool
    checked_at: float
    ttl_sec: int
    max_severity: str
    message: str
    skills_dir: str
    report_path: Optional[str]
    exit_code: int
    open_ports: Optional[List[int]] = None
    risky_bindings: Optional[List[str]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "passed": self.passed,
            "required": self.required,
            "enforced": self.enforced,
            "cached": self.cached,
            "checked_at": self.checked_at,
            "ttl_sec": self.ttl_sec,
            "max_severity": self.max_severity,
            "message": self.message,
            "skills_dir": self.skills_dir,
            "report_path": self.report_path,

            "exit_code": self.exit_code,
            "open_ports": self.open_ports or [],
            "risky_bindings": self.risky_bindings or [],
        }


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() not in {"0", "false", "no", "off"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


class OpenClawSecuritySentinel:
    """AI Overseer-managed OpenClaw security sentinel."""

    def __init__(
        self,
        repo_root: Path,
        *,
        skills_dir: Optional[Path] = None,
        cache_path: Optional[Path] = None,
    ):
        self.repo_root = Path(repo_root)
        self.skills_dir = (
            Path(skills_dir)
            if skills_dir
            else self.repo_root / "modules/communication/moltbot_bridge/workspace/skills"
        )
        default_cache = (
            self.repo_root
            / "modules/ai_intelligence/ai_overseer/memory/openclaw_security_sentinel.json"
        )
        self.cache_path = Path(os.getenv("OPENCLAW_SENTINEL_CACHE_PATH", str(cache_path or default_cache)))
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def check(self, *, force: bool = False) -> Dict[str, Any]:
        """Run (or reuse) OpenClaw security check."""
        ttl_sec = _env_int("OPENCLAW_SKILL_SCAN_TTL_SEC", 900)
        required = _env_bool("OPENCLAW_SKILL_SCAN_REQUIRED", True)
        enforced = _env_bool("OPENCLAW_SKILL_SCAN_ENFORCED", True)
        max_severity = os.getenv("OPENCLAW_SKILL_SCAN_MAX_SEVERITY", "medium")
        now = time.time()

        cached = self._load_cache()
        if cached and not force:
            checked_at = float(cached.get("checked_at", 0))
            if checked_at > 0 and (now - checked_at) < max(ttl_sec, 0):
                cached["cached"] = True
                return cached

        try:
            from modules.communication.moltbot_bridge.src.skill_safety_guard import run_skill_scan
        except Exception as exc:
            status = OpenClawSecurityStatus(
                available=False,
                passed=not required,
                required=required,
                enforced=enforced,
                cached=False,
                checked_at=now,
                ttl_sec=ttl_sec,
                max_severity=max_severity,
                message=f"skill safety guard unavailable: {exc}",
                skills_dir=str(self.skills_dir),
                report_path=None,
                exit_code=127,
            ).as_dict()
            self._save_cache(status)
            return status

        try:
            result = run_skill_scan(
                skills_dir=self.skills_dir,
                max_severity=max_severity,
            )
        except Exception as exc:
            status = OpenClawSecurityStatus(
                available=False,
                passed=not required,
                required=required,
                enforced=enforced,
                cached=False,
                checked_at=now,
                ttl_sec=ttl_sec,
                max_severity=max_severity,
                message=f"skill scan execution failed: {exc}",
                skills_dir=str(self.skills_dir),
                report_path=None,
                exit_code=70,
            ).as_dict()
            self._save_cache(status)
            return status


        # --- Phase 11: Runtime Port Scan ---
        try:
            open_ports, risky_bindings = self._scan_ports()
        except Exception as exc:
            logger.warning(f"Port scan failed: {exc}")
            open_ports, risky_bindings = [], []

        # Fail if risky bindings found
        if risky_bindings and enforced:
            result.available = True  # We ran the check
            result.passed = False
            result.message = f"CRITICAL: Risky network bindings detected: {', '.join(risky_bindings)}"
            result.exit_code = 1  # Security failure
        # -----------------------------------

        if not result.available:
            passed = not required
        else:
            passed = result.passed or (not enforced)

        status = OpenClawSecurityStatus(
            available=result.available,
            passed=passed,
            required=required,
            enforced=enforced,
            cached=False,
            checked_at=now,
            ttl_sec=ttl_sec,
            max_severity=max_severity,
            message=result.message,
            skills_dir=result.skills_dir,
            report_path=result.report_path,
            exit_code=result.exit_code,
            open_ports=open_ports,
            risky_bindings=risky_bindings,
        ).as_dict()
        self._save_cache(status)
        return status

    def _scan_ports(self) -> tuple[List[int], List[str]]:
        """Scan active listening ports and flag wildcard bindings with sane defaults.

        This check focuses on likely application exposure and avoids failing on:
        - Core Windows system listeners (PID 0/4)
        - Ephemeral high ports (default >= 49152)
        - Operator-configured ignore lists
        """
        open_ports: Set[int] = set()
        risky_bindings: Set[str] = set()

        ignore_ports = self._parse_port_set(
            os.getenv("OPENCLAW_PORT_SCAN_IGNORE_PORTS", "135,445,1900,5353,5355,5357,5358,5040")
        )
        default_monitored_ports = (
            os.getenv("OPENCLAW_BRIDGE_PORT")
            or os.getenv("MOLTBOT_BRIDGE_PORT")
            or "18800"
        )
        monitored_ports = self._parse_port_set(
            os.getenv("OPENCLAW_PORT_SCAN_MONITORED_PORTS", default_monitored_ports)
        )
        ignore_ephemeral = _env_bool("OPENCLAW_PORT_SCAN_IGNORE_EPHEMERAL", True)
        ignore_system_pids = _env_bool("OPENCLAW_PORT_SCAN_IGNORE_SYSTEM_PIDS", True)
        
        try:
            # Cross-platform netstat (mostly Windows/Linux compatible for this flag verify)
            # -a: all, -n: numeric
            cmd = ["netstat", "-an"]
            # Windows specific: -o for PID but we just need IP:Port
            if os.name == 'nt':
                cmd = ["netstat", "-ano"]
                
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
            
            for raw_line in output.splitlines():
                line = raw_line.strip()
                if "LISTEN" not in line and "LISTENING" not in line:
                    continue

                host, port, pid = self._extract_binding(line)
                if host is None or port is None:
                    continue

                open_ports.add(port)
                if not self._is_wildcard_host(host):
                    continue

                if ignore_system_pids and pid in {0, 4}:
                    continue
                if ignore_ephemeral and port >= 49152:
                    continue
                if port in ignore_ports:
                    continue
                if monitored_ports and port not in monitored_ports:
                    continue

                host_display = "[::]" if host == "::" else host
                risky_bindings.add(f"{host_display}:{port}")
                            
        except Exception as e:
            logger.error(f"Failed to scan ports: {e}")
            
        return sorted(open_ports), sorted(risky_bindings)

    @staticmethod
    def _is_wildcard_host(host: str) -> bool:
        normalized = host.strip().lower().strip("[]")
        return normalized in {"0.0.0.0", "::", "*", ":::*"}

    @staticmethod
    def _parse_port_set(raw: str) -> Set[int]:
        ports: Set[int] = set()
        for token in (raw or "").split(","):
            value = token.strip()
            if not value:
                continue
            if "-" in value:
                start_s, end_s = value.split("-", 1)
                try:
                    start = int(start_s.strip())
                    end = int(end_s.strip())
                except ValueError:
                    continue
                if end < start:
                    start, end = end, start
                for port in range(max(start, 1), min(end, 65535) + 1):
                    ports.add(port)
                continue
            try:
                port = int(value)
            except ValueError:
                continue
            if 1 <= port <= 65535:
                ports.add(port)
        return ports

    def _extract_binding(self, line: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        parts = re.split(r"\s+", line.strip())
        if len(parts) < 2:
            return None, None, None

        local_addr: Optional[str] = None
        pid: Optional[int] = None

        # Windows netstat -ano format:
        # TCP  0.0.0.0:135  0.0.0.0:0  LISTENING  916
        if os.name == "nt" and len(parts) >= 4:
            local_addr = parts[1]
            if parts[-1].isdigit():
                pid = int(parts[-1])
        else:
            # Linux-ish fallback:
            # tcp  0  0 0.0.0.0:22  0.0.0.0:*  LISTEN  123/sshd
            try:
                state_idx = next(
                    i for i, token in enumerate(parts)
                    if token.upper() in {"LISTEN", "LISTENING"}
                )
            except StopIteration:
                state_idx = -1
            if state_idx >= 2:
                candidate = parts[state_idx - 2]
                if ":" in candidate:
                    local_addr = candidate
            tail = parts[-1]
            if tail.isdigit():
                pid = int(tail)
            elif "/" in tail:
                maybe_pid = tail.split("/", 1)[0]
                if maybe_pid.isdigit():
                    pid = int(maybe_pid)

        if not local_addr:
            return None, None, pid

        host, port = self._split_host_port(local_addr)
        return host, port, pid

    @staticmethod
    def _split_host_port(local_addr: str) -> Tuple[Optional[str], Optional[int]]:
        addr = (local_addr or "").strip()
        if not addr or ":" not in addr:
            return None, None

        if addr.startswith("[") and "]:" in addr:
            host, _, port_part = addr[1:].partition("]:")
        else:
            host, _, port_part = addr.rpartition(":")

        if not port_part.isdigit():
            return None, None
        try:
            port = int(port_part)
        except ValueError:
            return None, None
        if not (1 <= port <= 65535):
            return None, None

        normalized_host = (host or "*").strip().strip("[]")
        if normalized_host == ":::":
            normalized_host = "::"
        return normalized_host, port

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        if not self.cache_path.exists():
            return None
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _save_cache(self, payload: Dict[str, Any]) -> None:
        try:
            self.cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            # Non-fatal: cache write should never block security decision.
            pass
