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
                first = self.sentinel.check(force=False)
                second = self.sentinel.check(force=True)

        self.assertFalse(first["cached"])
        self.assertFalse(second["cached"])
        self.assertEqual(mock_scan.call_count, 2)


if __name__ == "__main__":
    unittest.main()
