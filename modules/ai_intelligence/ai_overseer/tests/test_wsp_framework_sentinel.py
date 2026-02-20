#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for AI Overseer WSP framework sentinel."""

from __future__ import annotations

import os
import asyncio
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
from modules.ai_intelligence.ai_overseer.src.wsp_framework_sentinel import WSPFrameworkSentinel


class TestWSPFrameworkSentinel(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)
        self.framework_src = self.repo_root / "WSP_framework" / "src"
        self.knowledge_src = self.repo_root / "WSP_knowledge" / "src"
        self.framework_src.mkdir(parents=True, exist_ok=True)
        self.knowledge_src.mkdir(parents=True, exist_ok=True)

        (self.framework_src / "WSP_15_Module_Prioritization_Scoring_System.md").write_text(
            "WSP 15 framework version\n",
            encoding="utf-8",
        )
        (self.framework_src / "WSP_96_MCP_Governance_and_Consensus_Protocol.md").write_text(
            "WSP 96 framework version\n",
            encoding="utf-8",
        )
        (self.knowledge_src / "WSP_15_Module_Prioritization_Scoring_System.md").write_text(
            "WSP 15 framework version\n",
            encoding="utf-8",
        )
        (self.knowledge_src / "WSP_96_MCP_Governance_and_Consensus_Protocol.md").write_text(
            "WSP 96 old backup version\n",
            encoding="utf-8",
        )
        (self.knowledge_src / "WSP_97_System_Execution_Prompting_Protocol.md").write_text(
            "WSP 97 knowledge only\n",
            encoding="utf-8",
        )

        (self.framework_src / "WSP_MASTER_INDEX.md").write_text(
            "\n".join(
                [
                    "| WSP | Title |",
                    "|-----|-------|",
                    "| WSP 15 | MPS |",
                    "| WSP 96 | MCP Governance |",
                    "| WSP 97 | System Prompting |",
                    "- **Next Available Number**: WSP 99",
                ]
            ),
            encoding="utf-8",
        )

        self.sentinel = WSPFrameworkSentinel(self.repo_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detects_drift_and_framework_knowledge_diff(self) -> None:
        status = self.sentinel.check(force=True)
        self.assertTrue(status["available"])
        self.assertEqual(status["framework_count"], 2)
        self.assertEqual(status["knowledge_count"], 3)
        self.assertEqual(status["common_count"], 2)
        self.assertEqual(status["drift_count"], 1)
        self.assertIn("WSP_96_MCP_Governance_and_Consensus_Protocol", status["drift_files"])
        self.assertEqual(status["framework_only"], [])
        self.assertIn("WSP_97_System_Execution_Prompting_Protocol", status["knowledge_only"])
        self.assertEqual(status["index_issues"], [])
        self.assertEqual(status["severity"], "warning")
        self.assertIn("report_path", status)

    def test_uses_cache_within_ttl(self) -> None:
        with unittest.mock.patch.dict(os.environ, {"WSP_FRAMEWORK_AUDIT_TTL_SEC": "3600"}, clear=False):
            first = self.sentinel.check(force=True)
            second = self.sentinel.check(force=False)
        self.assertFalse(first["cached"])
        self.assertTrue(second["cached"])
        self.assertEqual(first["drift_count"], second["drift_count"])

    def test_backup_only_knowledge_files_are_non_blocking_by_default(self) -> None:
        (self.knowledge_src / "WSP_96_MCP_Governance_and_Consensus_Protocol.md").write_text(
            "WSP 96 framework version\n",
            encoding="utf-8",
        )

        status = self.sentinel.check(force=True)
        self.assertEqual(status["drift_count"], 0)
        self.assertEqual(status["framework_only"], [])
        self.assertIn("WSP_97_System_Execution_Prompting_Protocol", status["knowledge_only"])
        self.assertEqual(status["severity"], "ok")

    def test_backup_only_can_be_promoted_to_warning_via_env(self) -> None:
        (self.knowledge_src / "WSP_96_MCP_Governance_and_Consensus_Protocol.md").write_text(
            "WSP 96 framework version\n",
            encoding="utf-8",
        )

        with unittest.mock.patch.dict(
            os.environ,
            {"WSP_FRAMEWORK_ALLOW_KNOWLEDGE_ONLY": "0"},
            clear=False,
        ):
            status = self.sentinel.check(force=True)
        self.assertEqual(status["drift_count"], 0)
        self.assertEqual(status["severity"], "warning")


class TestAIOverseerWSPAuditApi(unittest.TestCase):
    def test_monitor_wsp_framework_updates_last_status(self) -> None:
        overseer = object.__new__(AIIntelligenceOverseer)
        expected = {
            "available": True,
            "severity": "warning",
            "drift_count": 2,
            "framework_only": ["WSP_95_WRE_SKILLz_Wardrobe_Protocol"],
            "knowledge_only": ["WSP_95_MCP_Governance_and_Consensus_Protocol"],
            "index_issues": [],
        }
        sentinel = MagicMock()
        sentinel.check.return_value = expected

        overseer.wsp_framework_sentinel = sentinel
        overseer.wsp_framework_last_status = None

        with unittest.mock.patch.dict(os.environ, {"WSP_FRAMEWORK_ALERT_TO_STDOUT": "0"}, clear=False):
            result = AIIntelligenceOverseer.monitor_wsp_framework(
                overseer,
                force=True,
                emit_alert=True,
            )

        sentinel.check.assert_called_once_with(force=True)
        self.assertEqual(result, expected)
        self.assertEqual(overseer.wsp_framework_last_status, expected)

    def test_monitor_wsp_framework_handles_unavailable_sentinel(self) -> None:
        overseer = object.__new__(AIIntelligenceOverseer)
        overseer.wsp_framework_sentinel = None
        overseer.wsp_framework_last_status = None

        result = AIIntelligenceOverseer.monitor_wsp_framework(overseer, force=False)
        self.assertFalse(result["available"])
        self.assertEqual(result["severity"], "critical")

    def test_telemetry_event_routes_wsp_framework_audit_request(self) -> None:
        overseer = object.__new__(AIIntelligenceOverseer)
        overseer.monitor_wsp_framework = MagicMock(
            return_value={"severity": "warning", "drift_count": 3}
        )

        async def _run() -> None:
            await AIIntelligenceOverseer._handle_telemetry_event(
                overseer,
                {"event": "wsp_framework_audit_request", "force": True},
            )

        asyncio.run(_run())
        overseer.monitor_wsp_framework.assert_called_once_with(force=True, emit_alert=True)


if __name__ == "__main__":
    unittest.main()
