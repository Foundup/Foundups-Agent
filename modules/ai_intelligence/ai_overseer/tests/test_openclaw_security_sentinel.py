#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for OpenClaw security sentinel."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel import (
    OpenClawSecuritySentinel,
)
from modules.communication.moltbot_bridge.src.skill_safety_guard import SkillScanResult


class TestOpenClawSecuritySentinel(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)
        self.skills_dir = self.repo_root / "modules/communication/moltbot_bridge/workspace/skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = (
            self.repo_root / "modules/ai_intelligence/ai_overseer/memory/openclaw_security_sentinel.json"
        )
        self.sentinel = OpenClawSecuritySentinel(
            self.repo_root,
            skills_dir=self.skills_dir,
            cache_path=self.cache_path,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _scan_result(self, *, available: bool, passed: bool, message: str = "ok", exit_code: int = 0):
        return SkillScanResult(
            available=available,
            passed=passed,
            exit_code=exit_code,
            skills_dir=str(self.skills_dir),
            report_path=str(self.repo_root / "report.json"),
            message=message,
        )

    def test_fail_closed_when_scanner_unavailable_and_required(self):
        with patch.dict(
            os.environ,
            {
                "OPENCLAW_SKILL_SCAN_REQUIRED": "1",
                "OPENCLAW_SKILL_SCAN_ENFORCED": "1",
                "OPENCLAW_SKILL_SCAN_TTL_SEC": "900",
            },
            clear=False,
        ):
            with patch(
                "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
                return_value=self._scan_result(available=False, passed=False, message="scanner missing", exit_code=127),
            ):
                with patch.object(self.sentinel, "_scan_ports", return_value=([], [])):
                    status = self.sentinel.check(force=True)
        self.assertFalse(status["passed"])
        self.assertFalse(status["available"])
        self.assertTrue(status["required"])

    def test_fail_open_when_scanner_unavailable_and_not_required(self):
        with patch.dict(
            os.environ,
            {
                "OPENCLAW_SKILL_SCAN_REQUIRED": "0",
                "OPENCLAW_SKILL_SCAN_ENFORCED": "1",
                "OPENCLAW_SKILL_SCAN_TTL_SEC": "900",
            },
            clear=False,
        ):
            with patch(
                "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
                return_value=self._scan_result(available=False, passed=False, message="scanner missing", exit_code=127),
            ):
                with patch.object(self.sentinel, "_scan_ports", return_value=([], [])):
                    status = self.sentinel.check(force=True)
        self.assertTrue(status["passed"])
        self.assertFalse(status["available"])
        self.assertFalse(status["required"])

    def test_non_enforced_mode_allows_failed_scan(self):
        with patch.dict(
            os.environ,
            {
                "OPENCLAW_SKILL_SCAN_REQUIRED": "1",
                "OPENCLAW_SKILL_SCAN_ENFORCED": "0",
                "OPENCLAW_SKILL_SCAN_TTL_SEC": "900",
            },
            clear=False,
        ):
            with patch(
                "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
                return_value=self._scan_result(available=True, passed=False, message="threshold exceeded", exit_code=1),
            ):
                with patch.object(self.sentinel, "_scan_ports", return_value=([], [])):
                    status = self.sentinel.check(force=True)
        self.assertTrue(status["passed"])
        self.assertTrue(status["available"])
        self.assertFalse(status["enforced"])

    def test_cache_prevents_rescan_within_ttl(self):
        with patch.dict(
            os.environ,
            {
                "OPENCLAW_SKILL_SCAN_REQUIRED": "1",
                "OPENCLAW_SKILL_SCAN_ENFORCED": "1",
                "OPENCLAW_SKILL_SCAN_TTL_SEC": "3600",
            },
            clear=False,
        ):
            with patch(
                "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
                return_value=self._scan_result(available=True, passed=True),
            ) as mock_scan:
                with patch.object(self.sentinel, "_scan_ports", return_value=([], [])):
                    first = self.sentinel.check(force=False)
                    second = self.sentinel.check(force=False)

        self.assertTrue(first["passed"])
        self.assertTrue(second["passed"])
        self.assertFalse(first["cached"])
        self.assertTrue(second["cached"])
        self.assertEqual(mock_scan.call_count, 1)

    def test_force_bypasses_cache(self):
        with patch.dict(
            os.environ,
            {
                "OPENCLAW_SKILL_SCAN_REQUIRED": "1",
                "OPENCLAW_SKILL_SCAN_ENFORCED": "1",
                "OPENCLAW_SKILL_SCAN_TTL_SEC": "3600",
            },
            clear=False,
        ):
            with patch(
                "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
                side_effect=[
                    self._scan_result(available=True, passed=True, message="first"),
                    self._scan_result(available=True, passed=True, message="second"),
                ],
            ) as mock_scan:
                with patch.object(self.sentinel, "_scan_ports", return_value=([], [])):
                    first = self.sentinel.check(force=False)
                    second = self.sentinel.check(force=True)

        self.assertFalse(first["cached"])
        self.assertFalse(second["cached"])
        self.assertEqual(mock_scan.call_count, 2)

    def test_scan_ports_ignores_system_and_ephemeral_listeners(self):
        netstat_output = "\n".join(
            [
                "TCP    0.0.0.0:135    0.0.0.0:0    LISTENING    4",
                "TCP    0.0.0.0:3000   0.0.0.0:0    LISTENING    4321",
                "TCP    0.0.0.0:56238  0.0.0.0:0    LISTENING    9876",
                "TCP    127.0.0.1:18800 0.0.0.0:0   LISTENING    2222",
                "TCP    [::]:445       [::]:0       LISTENING    4",
            ]
        ).encode("utf-8")

        with patch.dict(
            os.environ,
            {"OPENCLAW_PORT_SCAN_MONITORED_PORTS": ""},
            clear=False,
        ):
            with patch(
                "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.subprocess.check_output",
                return_value=netstat_output,
            ):
                with patch(
                    "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.os.name",
                    "nt",
                ):
                    open_ports, risky = self.sentinel._scan_ports()

        self.assertIn(3000, open_ports)
        self.assertIn(56238, open_ports)
        self.assertEqual(risky, ["0.0.0.0:3000"])

    def test_scan_ports_defaults_to_openclaw_bridge_port(self):
        netstat_output = "\n".join(
            [
                "TCP    0.0.0.0:3000   0.0.0.0:0    LISTENING    4321",
                "TCP    0.0.0.0:18800  0.0.0.0:0    LISTENING    2222",
            ]
        ).encode("utf-8")

        with patch.dict(
            os.environ,
            {"OPENCLAW_BRIDGE_PORT": "18800"},
            clear=False,
        ):
            with patch(
                "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.subprocess.check_output",
                return_value=netstat_output,
            ):
                with patch(
                    "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.os.name",
                    "nt",
                ):
                    _, risky = self.sentinel._scan_ports()

        self.assertEqual(risky, ["0.0.0.0:18800"])

    def test_scan_ports_can_limit_to_monitored_ports(self):
        netstat_output = "\n".join(
            [
                "TCP    0.0.0.0:3000   0.0.0.0:0    LISTENING    4321",
                "TCP    0.0.0.0:18800  0.0.0.0:0    LISTENING    2222",
            ]
        ).encode("utf-8")

        with patch.dict(
            os.environ,
            {"OPENCLAW_PORT_SCAN_MONITORED_PORTS": "18800"},
            clear=False,
        ):
            with patch(
                "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.subprocess.check_output",
                return_value=netstat_output,
            ):
                with patch(
                    "modules.ai_intelligence.ai_overseer.src.openclaw_security_sentinel.os.name",
                    "nt",
                ):
                    _, risky = self.sentinel._scan_ports()

        self.assertEqual(risky, ["0.0.0.0:18800"])


if __name__ == "__main__":
    unittest.main()
