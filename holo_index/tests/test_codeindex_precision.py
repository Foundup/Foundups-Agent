#!/usr/bin/env python3
"""
CodeIndex surgical intelligence regression tests.

Validates that QwenAdvisor delivers the surgical insights promised in WSP 93:
  * exact fix coordinates with complexity scoring
  * LEGO block visualisation for refactor planning
  * continuous circulation health signals
  * architect-grade choice framing and assumption detection
"""

import tempfile
import unittest
from pathlib import Path

from holo_index.qwen_advisor.advisor import AdvisorContext, QwenAdvisor


class TestCodeIndexPrecision(unittest.TestCase):
    """Ensure CodeIndex behaviours stay aligned with WSP 93 guarantees."""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        base_path = Path(self._temp_dir.name)
        module_dir = base_path / "modules" / "demo_domain" / "demo_module" / "src"
        module_dir.mkdir(parents=True, exist_ok=True)

        self.module_path = module_dir / "heavy_module.py"
        self.module_path.write_text(self._build_demo_module(), encoding="utf-8")

        # Track total lines for circulation heuristics
        with self.module_path.open("r", encoding="utf-8") as handle:
            self.total_lines = sum(1 for _ in handle)

        self.context = AdvisorContext(
            query="optimize heavy_module using first principles",
            code_hits=[
                {
                    "file_path": self.module_path.as_posix(),
                    "lines": self.total_lines,
                }
            ],
            wsp_hits=[],
        )
        self.advisor = QwenAdvisor()

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def _build_demo_module(self) -> str:
        """Create a synthetic module with deliberate complexity + assumptions."""
        lines = [
            "def tiny_helper():\n",
            "    return len('helper')\n",
            "\n",
            "def mega_function():\n",
            "    processed_data = []\n",
        ]

        # 210 comment lines to push complexity & estimated effort to 90 minutes
        for _ in range(210):
            lines.append("    # maintain structural load for complexity detection\n")

        lines.extend(
            [
                "    # TODO: revisit for maintainability and split responsibilities\n",
                '    config_path = "C:/very/long/hardcoded/config/path/for/testing/purposes"\n',
                "    return processed_data\n",
            ]
        )
        return "".join(lines)

    def test_surgical_code_index_flags_high_complexity(self) -> None:
        """Surgical analysis must identify high complexity fix coordinates."""
        results = self.advisor.surgical_code_index(self.context)
        self.assertIn(self.module_path.as_posix(), results["modules_analyzed"])

        fixes = {fix["function"]: fix for fix in results["exact_fixes"]}
        self.assertIn("mega_function", fixes)

        mega_fix = fixes["mega_function"]
        self.assertGreaterEqual(mega_fix["complexity"], 3)
        self.assertEqual(mega_fix["estimated_effort"], 90)
        self.assertRegex(mega_fix["line_range"], r"\d+-\d+")

    def test_lego_visualization_marks_break_candidates(self) -> None:
        """LEGO diagram should highlight break-apart opportunities."""
        diagram = self.advisor.lego_visualization(self.context)
        self.assertIn("[LEGO]", diagram)
        self.assertIn("mega_function", diagram)
        self.assertIn("[BREAK]", diagram)

    def test_present_choice_offers_surgical_option(self) -> None:
        """Architect choice framing must surface surgical path when needed."""
        choice_text = self.advisor.present_choice(self.context)
        self.assertIn("[SURGICAL]", choice_text)
        self.assertIn("mega_function", choice_text)
        self.assertIn("Target: mega_function", choice_text)

    def test_continuous_circulation_reports_complexity_alert(self) -> None:
        """Continuous circulation should surface complexity alerts."""
        health_report = self.advisor.continuous_circulation(self.context)
        self.assertIn("[WARNING] HIGH COMPLEXITY", health_report)
        self.assertIn("Functions analyzed", health_report)

    def test_challenge_assumptions_detects_todo_and_hardcoded(self) -> None:
        """Hidden assumption detector must flag TODO + hardcoded config path."""
        assumptions = self.advisor.challenge_assumptions(self.context)
        self.assertIn("[FILE]", assumptions)
        self.assertIn("TODO", assumptions)
        self.assertIn("Long hardcoded string", assumptions)


if __name__ == "__main__":
    unittest.main()
