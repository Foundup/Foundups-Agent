#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Tests for the CodeIndex circulation + architect mode building blocks.
"""

import tempfile
import unittest
from pathlib import Path

from holo_index.qwen_advisor.qwen_health_monitor import CodeIndexCirculationEngine
from holo_index.qwen_advisor.architect_mode import ArchitectDecisionEngine
from holo_index.qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator
from holo_index.intent_classifier import IntentClassification, IntentType


class TestCodeIndexMonitor(unittest.TestCase):
    """Validate new CodeIndex health monitor primitives."""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.module_root = Path(self._temp_dir.name) / "modules" / "demo" / "module"
        src_dir = self.module_root / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        # Compose synthetic module with one high complexity function
        source = [
            "def helper():\n",
            "    return 1\n",
            "\n",
            "def massive_function():\n",
            "    accumulator = 0\n",
        ]
        for idx in range(210):
            source.append(f"    accumulator += {idx}\n")
        source.extend(
            [
                "    # TODO: extract logic into dedicated services\n",
                '    config_path = "C:/path/to/hardcoded/config/for/tests"\n',
                "    return accumulator\n",
            ]
        )

        self.module_path = src_dir / "heavy.py"
        self.module_path.write_text("".join(source), encoding="utf-8")

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_circulation_engine_reports_surgical_fixes(self) -> None:
        engine = CodeIndexCirculationEngine()
        report = engine.evaluate_module(self.module_root)
        self.assertIsNotNone(report)
        assert report is not None

        self.assertEqual(report.module_name, "module")
        self.assertGreaterEqual(len(report.surgical_fixes), 1)
        top_fix = report.surgical_fixes[0]
        self.assertIn("massive_function", top_fix.function)
        self.assertGreaterEqual(top_fix.estimated_effort, 45)
        self.assertIn("[CIRCULATION]", report.circulation_summary)
        self.assertIn("Hardcoded", report.assumption_alerts)

    def test_architect_engine_generates_decisions(self) -> None:
        engine = CodeIndexCirculationEngine()
        report = engine.evaluate_module(self.module_root)
        assert report is not None

        decision_engine = ArchitectDecisionEngine()
        decisions = decision_engine.build_decisions(report)
        self.assertEqual(len(decisions), 3)
        labels = {decision.label for decision in decisions}
        self.assertSetEqual(labels, {"A", "B", "C"})
        summary_text = decision_engine.summarize(report)
        self.assertIn("[ARCHITECT] Module", summary_text)
        self.assertIn("Surgical:", summary_text)

    def test_orchestrator_codeindex_trigger_heuristic(self) -> None:
        orchestrator = QwenOrchestrator()
        classification = IntentClassification(
            intent=IntentType.CODE_LOCATION,
            confidence=0.8,
            patterns_matched=[],
            raw_query="refactor module",
        )
        snapshot = {
            "module": "modules/demo/module",
            "path": self.module_root,
            "exists": True,
            "missing_docs": [],
            "test_count": 0,
            "py_file_count": 1,
            "script_orphans": [],
            "large_python_files": [(self.module_path, 500, 15)],
        }
        should_trigger, reason = orchestrator._should_trigger_codeindex(
            query="refactor module",
            intent_classification=classification,
            module_snapshots={"modules/demo/module": snapshot},
        )
        self.assertTrue(should_trigger)
        self.assertIn("refactor", reason.lower())

    def test_orchestrator_generates_codeindex_section(self) -> None:
        orchestrator = QwenOrchestrator()
        snapshot = {
            "module": "modules/demo/module",
            "path": self.module_root,
            "exists": True,
            "missing_docs": [],
            "test_count": 0,
            "py_file_count": 1,
            "script_orphans": [],
            "large_python_files": [(self.module_path, 500, 15)],
        }
        section = orchestrator._generate_codeindex_section({"modules/demo/module": snapshot})
        self.assertIn("[CODEINDEX]", section)
        self.assertIn("[ARCHITECT]", section)


if __name__ == "__main__":
    unittest.main()
