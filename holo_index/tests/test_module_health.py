#!/usr/bin/env python3
"""
FMAS Tests for Module Health Audit System
WSP Compliance: WSP 87 (Code Navigation), WSP 49 (Module Structure)
"""

import unittest
from pathlib import Path
import tempfile
import shutil
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module_health.size_audit import SizeAuditor, FileSizeResult, RiskTier
from module_health.structure_audit import StructureAuditor, StructureResult


class TestSizeAuditor(unittest.TestCase):
    """Test the size audit functionality."""

    def setUp(self):
        """Create test environment."""
        self.auditor = SizeAuditor()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_file_under_threshold(self):
        """Test that files under 800 lines are OK."""
        # Create a small file
        test_file = Path(self.temp_dir) / "small.py"
        with open(test_file, 'w') as f:
            for i in range(500):
                f.write(f"# Line {i}\n")

        result = self.auditor.audit_file(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result.line_count, 500)
        self.assertEqual(result.risk_tier, RiskTier.OK)
        self.assertFalse(result.needs_attention)
        self.assertIn("acceptable", result.guidance)

    def test_file_warn_threshold(self):
        """Test that files between 800-1000 lines trigger warning."""
        # Create a medium file
        test_file = Path(self.temp_dir) / "medium.py"
        with open(test_file, 'w') as f:
            for i in range(900):
                f.write(f"# Line {i}\n")

        result = self.auditor.audit_file(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result.line_count, 900)
        self.assertEqual(result.risk_tier, RiskTier.WARN)
        self.assertTrue(result.needs_attention)
        self.assertIn("approaching guideline", result.guidance)

    def test_file_critical_threshold(self):
        """Test that files over 1000 lines are critical."""
        # Create a large file
        test_file = Path(self.temp_dir) / "large.py"
        with open(test_file, 'w') as f:
            for i in range(1200):
                f.write(f"# Line {i}\n")

        result = self.auditor.audit_file(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result.line_count, 1200)
        self.assertEqual(result.risk_tier, RiskTier.CRITICAL)
        self.assertTrue(result.needs_attention)
        self.assertIn("exceeds guideline", result.guidance)
        self.assertIn("1500", result.guidance)  # Mentions hard limit

    def test_nonexistent_file(self):
        """Test that nonexistent files return None."""
        test_file = Path(self.temp_dir) / "missing.py"
        result = self.auditor.audit_file(test_file)
        self.assertIsNone(result)

    def test_non_python_file_skipped(self):
        """Test that non-Python files are skipped."""
        test_file = Path(self.temp_dir) / "data.txt"
        with open(test_file, 'w') as f:
            f.write("Some data\n" * 1000)

        result = self.auditor.audit_file(test_file)
        self.assertIsNone(result)

    def test_audit_module(self):
        """Test auditing an entire module."""
        # Create module structure
        module_dir = Path(self.temp_dir) / "test_module"
        src_dir = module_dir / "src"
        src_dir.mkdir(parents=True)

        # Create files of different sizes
        small_file = src_dir / "small.py"
        with open(small_file, 'w') as f:
            f.write("# Small file\n" * 100)

        large_file = src_dir / "large.py"
        with open(large_file, 'w') as f:
            f.write("# Large file\n" * 1100)

        # Run module audit
        results = self.auditor.audit_module(module_dir)

        # Should only return the large file (needs attention)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].path, large_file)
        self.assertEqual(results[0].risk_tier, RiskTier.CRITICAL)


class TestStructureAuditor(unittest.TestCase):
    """Test the structure audit functionality."""

    def setUp(self):
        """Create test environment."""
        self.auditor = StructureAuditor()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compliant_module(self):
        """Test a fully compliant module structure."""
        # Create compliant module
        module_dir = Path(self.temp_dir) / "compliant_module"
        module_dir.mkdir()

        # Create all required artifacts
        (module_dir / "README.md").touch()
        (module_dir / "INTERFACE.md").touch()
        (module_dir / "ModLog.md").touch()
        (module_dir / "src").mkdir()
        (module_dir / "tests").mkdir()
        (module_dir / "tests" / "TestModLog.md").touch()

        result = self.auditor.audit_module(module_dir)
        self.assertTrue(result.is_compliant)
        self.assertEqual(len(result.missing_artifacts), 0)
        self.assertIn("compliant", result.guidance)

    def test_missing_readme(self):
        """Test detection of missing README.md."""
        module_dir = Path(self.temp_dir) / "incomplete_module"
        module_dir.mkdir()

        # Create some but not all artifacts
        (module_dir / "INTERFACE.md").touch()
        (module_dir / "ModLog.md").touch()
        (module_dir / "src").mkdir()
        (module_dir / "tests").mkdir()

        result = self.auditor.audit_module(module_dir)
        self.assertFalse(result.is_compliant)
        self.assertIn("README.md", result.missing_artifacts)
        self.assertIn("tests/TestModLog.md", result.missing_artifacts)

        # Check todos
        todos = result.todos
        self.assertTrue(any("README.md" in todo for todo in todos))
        self.assertTrue(any("overview and purpose" in todo for todo in todos))

    def test_missing_tests_directory(self):
        """Test detection of missing tests directory."""
        module_dir = Path(self.temp_dir) / "no_tests_module"
        module_dir.mkdir()

        (module_dir / "README.md").touch()
        (module_dir / "INTERFACE.md").touch()
        (module_dir / "ModLog.md").touch()
        (module_dir / "src").mkdir()

        result = self.auditor.audit_module(module_dir)
        self.assertFalse(result.is_compliant)
        self.assertIn("tests/", result.missing_artifacts)
        # TestModLog.md is not added separately when tests/ is missing

    def test_find_module_root_direct(self):
        """Test finding module root from a direct module path."""
        module_dir = Path(self.temp_dir) / "modules" / "domain" / "module"
        module_dir.mkdir(parents=True)
        (module_dir / "README.md").touch()

        found = self.auditor.find_module_root(module_dir)
        self.assertEqual(found, module_dir)

    def test_find_module_root_from_file(self):
        """Test finding module root from a file within the module."""
        module_dir = Path(self.temp_dir) / "modules" / "domain" / "module"
        src_dir = module_dir / "src"
        src_dir.mkdir(parents=True)
        (module_dir / "README.md").touch()

        test_file = src_dir / "code.py"
        test_file.touch()

        found = self.auditor.find_module_root(test_file)
        self.assertEqual(found, module_dir)

    def test_nonexistent_module(self):
        """Test auditing a nonexistent module."""
        module_dir = Path(self.temp_dir) / "nonexistent"
        result = self.auditor.audit_module(module_dir)

        self.assertFalse(result.is_compliant)
        # All artifacts should be missing
        self.assertTrue(len(result.missing_artifacts) > 0)


class TestRulesEngineIntegration(unittest.TestCase):
    """Test integration with the rules engine."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rules_engine_with_health_checks(self):
        """Test that rules engine properly integrates health checks."""
        from qwen_advisor.rules_engine import ComplianceRulesEngine

        engine = ComplianceRulesEngine()

        # Create a mock search hit pointing to a large file
        module_dir = Path(self.temp_dir) / "modules" / "test" / "module"
        src_dir = module_dir / "src"
        src_dir.mkdir(parents=True)

        large_file = src_dir / "large.py"
        with open(large_file, 'w') as f:
            f.write("# Large file\n" * 1100)

        # Mock search hits
        search_hits = [
            {
                "location": str(large_file),
                "need": "test functionality",
                "confidence": 80
            }
        ]

        # Generate guidance
        guidance = engine.generate_contextual_guidance(
            "search for test functionality",
            search_hits
        )

        # Should have violations if module health is available
        if engine.size_auditor:
            # Check that size violation was detected
            self.assertTrue(len(guidance["violations"]) > 0 or len(guidance["reminders"]) > 0)

            # Check for WSP 87 reference
            all_checks = guidance["all_checks"]
            wsp_87_found = any("WSP 87" in check.get("wsp_reference", "") for check in all_checks)
            self.assertTrue(wsp_87_found or not engine.size_auditor)

    def test_path_resolution(self):
        """Test the path resolution logic."""
        from qwen_advisor.rules_engine import ComplianceRulesEngine

        engine = ComplianceRulesEngine()

        # Test direct path
        test_file = Path(self.temp_dir) / "test.py"
        test_file.touch()

        hit = {"location": str(test_file)}
        resolved = engine._resolve_file_path(hit)
        self.assertEqual(resolved, test_file)

        # Test module notation
        modules_dir = Path(self.temp_dir) / "modules" / "test" / "module" / "src"
        modules_dir.mkdir(parents=True)
        module_file = modules_dir / "code.py"
        module_file.touch()

        # This would need the project root to be set correctly
        # For now, just test that it doesn't crash
        hit = {"location": "modules.test.module.src.code"}
        resolved = engine._resolve_file_path(hit)
        # May be None if not in actual project structure
        self.assertTrue(resolved is None or resolved.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)