#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M2M Compression Sentinel Tests + Benchmarks (WSP 99).

Tests:
    - FileAnalysis confidence calculation
    - Candidate file collection and filtering
    - Deterministic M2M transformation quality
    - Staged promotion workflow (compile -> list -> promote -> rollback)
    - Pattern memory learning

Benchmarks:
    - Scan speed (full repo scan latency)
    - Compression ratios by file type
    - Transformation throughput (files/sec)
"""

from __future__ import annotations

import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import pytest


# ============ Fixtures ============ #

@pytest.fixture
def repo_root():
    """Return actual repo root for integration tests."""
    return Path(__file__).resolve().parents[4]


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repo structure for isolated unit tests."""
    # Create minimal structure
    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\n"
        "## Instructions\n\n"
        "Please ensure that you follow all the guidelines carefully.\n"
        "It is important to note that the system uses WSP 77 for coordination.\n"
        "For example, the agent coordination protocol handles all tasks.\n"
        "In order to achieve this, we need to implement the following steps:\n"
        "As mentioned above, the architecture uses Qwen and Gemma.\n"
        "Could you please make sure to validate all inputs.\n"
        "Remember to check WSP 50 before making any changes.\n"
        "The following demonstrates the approach:\n"
        "\n"
        "```python\n"
        "class AIOverser:\n"
        "    def coordinate(self): pass\n"
        "```\n"
        "\n"
        "## Core Protocol\n\n"
        "- **Module**: ai_overseer\n"
        "- **Status**: Active\n"
        "- **WSP**: 77, 54, 96\n"
        "\n" * 30 +  # Pad to meet min lines
        "End of file.\n",
        encoding="utf-8",
    )

    # Module INTERFACE.md
    mod_dir = tmp_path / "modules" / "test_module"
    mod_dir.mkdir(parents=True)
    (mod_dir / "INTERFACE.md").write_text(
        "# Test Module Interface\n\n"
        "## Public API\n\n"
        "- **search(query, limit)**: Search for documents\n"
        "- **index_all()**: Rebuild all indexes\n"
        "- `check_module(name)`: WSP compliance check\n"
        "\n"
        "## Integration\n\n"
        "It should be noted that this module integrates with WSP 87.\n"
        "For instance, the HoloIndex provides semantic search.\n"
        "Please ensure that you initialize before searching.\n"
        "\n" * 40 +
        "End of interface.\n",
        encoding="utf-8",
    )

    # WSP framework file
    wsp_dir = tmp_path / "WSP_framework" / "src"
    wsp_dir.mkdir(parents=True)
    (wsp_dir / "WSP_99_M2M_Prompting.md").write_text(
        "# WSP 99: M2M Prompting Protocol\n\n"
        "## Overview\n\n"
        "This protocol defines machine-to-machine compressed format.\n"
        "In other words, it removes human-readable prose.\n"
        "It is important to note that M2M achieves 4x compression.\n"
        "\n"
        "## Format\n\n"
        "- **Header**: `# M2M v1.0 | filename | date`\n"
        "- **Sections**: `SECTION_NAME:`\n"
        "- **Key-Value**: `  KEY: value`\n"
        "- **WSP refs**: `  WSP: [nn]`\n"
        "\n" * 30 +
        "End of WSP.\n",
        encoding="utf-8",
    )

    # Small file that should be SKIPPED (below threshold)
    (tmp_path / "modules" / "test_module" / "README.md").write_text(
        "# Test Module\nShort readme.\n",
        encoding="utf-8",
    )

    # CHANGELOG (should be EXCLUDED)
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n## v1.0\n- Initial release\n" * 50,
        encoding="utf-8",
    )

    # Create M2M staged directory
    (tmp_path / ".m2m" / "staged").mkdir(parents=True)
    (tmp_path / ".m2m" / "backups").mkdir(parents=True)

    # Create overseer memory directory
    mem_dir = tmp_path / "modules" / "ai_intelligence" / "ai_overseer" / "memory"
    mem_dir.mkdir(parents=True)

    return tmp_path


@pytest.fixture
def sentinel(temp_repo):
    """Create M2MCompressionSentinel with temp repo."""
    from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import (
        M2MCompressionSentinel,
    )
    return M2MCompressionSentinel(temp_repo)


# ============ Unit Tests: File Analysis ============ #

class TestFileAnalysis:
    """Test file-level analysis and confidence calculation."""

    def test_analyze_verbose_file(self, sentinel, temp_repo):
        """Files with politeness markers and verbose patterns score high prose density."""
        analysis = sentinel._analyze_file(temp_repo / "CLAUDE.md")
        assert analysis is not None
        assert analysis.prose_density > 0.3, "Verbose file should have high prose density"
        assert analysis.politeness_count > 0, "Should detect politeness markers"
        assert analysis.verbose_count > 0, "Should detect verbose patterns"

    def test_analyze_interface_file(self, sentinel, temp_repo):
        """INTERFACE.md files with K:V patterns should be compression candidates."""
        analysis = sentinel._analyze_file(
            temp_repo / "modules" / "test_module" / "INTERFACE.md"
        )
        assert analysis is not None
        assert analysis.estimated_reduction > 20, "Interface files should be compressible"

    def test_skip_small_files(self, sentinel, temp_repo):
        """Files below MIN_LINES_FOR_COMPRESSION should be skipped."""
        analysis = sentinel._analyze_file(
            temp_repo / "modules" / "test_module" / "README.md"
        )
        assert analysis is None, "Small files should return None"

    def test_critical_file_detection(self, sentinel, temp_repo):
        """CLAUDE.md should be flagged as critical."""
        analysis = sentinel._analyze_file(temp_repo / "CLAUDE.md")
        assert analysis is not None
        assert analysis.is_critical is True
        assert analysis.action == "stage_review", "Critical files always need review"

    def test_confidence_range(self, sentinel, temp_repo):
        """Confidence should always be in [0.0, 1.0]."""
        analysis = sentinel._analyze_file(temp_repo / "CLAUDE.md")
        assert analysis is not None
        assert 0.0 <= analysis.confidence <= 1.0

    def test_analysis_as_dict(self, sentinel, temp_repo):
        """FileAnalysis.as_dict() should produce valid JSON-serializable dict."""
        analysis = sentinel._analyze_file(temp_repo / "CLAUDE.md")
        assert analysis is not None
        d = analysis.as_dict()
        assert isinstance(d, dict)
        json.dumps(d)  # Should not raise


# ============ Unit Tests: Candidate Collection ============ #

class TestCandidateCollection:
    """Test file collection and filtering logic."""

    def test_collects_claude_md(self, sentinel, temp_repo):
        """Should find root CLAUDE.md."""
        candidates = sentinel._collect_candidate_files()
        names = [p.name for p in candidates]
        assert "CLAUDE.md" in names

    def test_collects_interface_md(self, sentinel, temp_repo):
        """Should find module INTERFACE.md files."""
        candidates = sentinel._collect_candidate_files()
        names = [p.name for p in candidates]
        assert "INTERFACE.md" in names

    def test_excludes_changelog(self, sentinel, temp_repo):
        """CHANGELOG.md should be excluded."""
        candidates = sentinel._collect_candidate_files()
        names = [p.name for p in candidates]
        assert "CHANGELOG.md" not in names

    def test_excludes_m2m_files(self, sentinel, temp_repo):
        """Already-compressed M2M files should be excluded."""
        # Create a fake M2M file in staged dir
        staged = temp_repo / ".m2m" / "staged" / "test_M2M.yaml"
        staged.write_text("# M2M v1.0\nTEST:", encoding="utf-8")

        candidates = sentinel._collect_candidate_files()
        paths_str = [str(p) for p in candidates]
        assert not any("_M2M" in s for s in paths_str)


# ============ Unit Tests: Deterministic Transform ============ #

class TestDeterministicTransform:
    """Test the deterministic M2M transformation."""

    def test_transform_produces_header(self, sentinel):
        """M2M output should start with standard header."""
        content = "# Test\n\n- **Key**: Value\n\n" * 20
        result = sentinel._transform_to_m2m(content, "test.md")
        assert result.startswith("# M2M v1.0 | test.md")

    def test_transform_extracts_kv(self, sentinel):
        """Should extract key:value pairs from backtick bullets."""
        content = (
            "# Module Config\n\n"
            "Overview of the module configuration.\n\n"
            "## Settings\n\n"
            "- `Status`: Active\n"
            "- `Version`: 1.0\n"
            "- `Author`: 0102\n"
            "\n" * 20
        )
        result = sentinel._transform_to_m2m(content, "test.md")
        assert "STATUS:" in result or "VERSION:" in result or "AUTHOR:" in result

    def test_transform_extracts_wsp_refs(self, sentinel):
        """Should extract WSP references."""
        content = (
            "# Compliance\n\n"
            "This module follows WSP 77 and WSP 50.\n"
            "\n" * 20
        )
        result = sentinel._transform_to_m2m(content, "test.md")
        assert "WSP:" in result
        assert "77" in result

    def test_transform_extracts_signatures(self, sentinel):
        """Should extract class/function signatures from code blocks."""
        content = (
            "# API\n\n"
            "```python\n"
            "class HoloIndex:\n"
            "    def search(self, query):\n"
            "        return results\n"
            "```\n"
            "\n" * 20
        )
        result = sentinel._transform_to_m2m(content, "test.md")
        assert "SIG:" in result
        assert "class HoloIndex" in result

    def test_transform_skips_prose(self, sentinel):
        """Prose sentences should be removed."""
        content = (
            "# Overview\n\n"
            "This is a very long description that explains what the module does.\n"
            "It provides extensive documentation about the architecture.\n"
            "\n" * 20
        )
        result = sentinel._transform_to_m2m(content, "test.md")
        # Prose lines should NOT appear in output
        assert "very long description" not in result
        assert "extensive documentation" not in result

    def test_transform_reduction_ratio(self, sentinel, temp_repo):
        """Deterministic transform should achieve at least 40% reduction."""
        content = (temp_repo / "CLAUDE.md").read_text(encoding="utf-8")
        result = sentinel._transform_to_m2m(content, "CLAUDE.md")

        original_lines = len(content.splitlines())
        m2m_lines = len(result.splitlines())
        reduction = (original_lines - m2m_lines) / original_lines * 100

        assert reduction >= 40, f"Expected >= 40% reduction, got {reduction:.1f}%"


# ============ Unit Tests: Staged Workflow ============ #

class TestStagedWorkflow:
    """Test compile -> list -> promote -> rollback pipeline."""

    def test_compile_to_staged(self, sentinel, temp_repo):
        """compile_to_staged should create M2M file in staged dir."""
        result = sentinel.compile_to_staged(
            "CLAUDE.md", use_qwen=False
        )
        assert result["success"] is True
        assert result["reduction_percent"] > 0
        assert result["compilation_method"] == "deterministic"

        # Verify staged file exists
        staged_path = temp_repo / result["staged_path"]
        assert staged_path.exists()

    def test_list_staged(self, sentinel, temp_repo):
        """list_staged should find compiled files."""
        # Compile first
        sentinel.compile_to_staged("CLAUDE.md", use_qwen=False)

        staged = sentinel.list_staged()
        assert staged["total_staged"] >= 1
        assert len(staged["files"]) >= 1

    def test_promote_with_backup(self, sentinel, temp_repo):
        """promote_staged should backup original and replace with M2M."""
        # Compile
        compile_result = sentinel.compile_to_staged("CLAUDE.md", use_qwen=False)
        staged_path = compile_result["staged_path"]

        # Remember original content
        original = (temp_repo / "CLAUDE.md").read_text(encoding="utf-8")

        # Promote
        result = sentinel.promote_staged(
            staged_path, target_path="CLAUDE.md"
        )
        assert result["success"] is True
        assert result["backup_path"] is not None

        # Verify target now has M2M content
        new_content = (temp_repo / "CLAUDE.md").read_text(encoding="utf-8")
        assert new_content.startswith("# M2M v1.0")
        assert new_content != original

    def test_rollback_restores_original(self, sentinel, temp_repo):
        """rollback should restore the original content from backup."""
        # Compile and promote
        compile_result = sentinel.compile_to_staged("CLAUDE.md", use_qwen=False)
        original = (temp_repo / "CLAUDE.md").read_text(encoding="utf-8")
        sentinel.promote_staged(
            compile_result["staged_path"], target_path="CLAUDE.md"
        )

        # Verify M2M content is in place
        m2m_content = (temp_repo / "CLAUDE.md").read_text(encoding="utf-8")
        assert m2m_content.startswith("# M2M v1.0")

        # Rollback
        result = sentinel.rollback("CLAUDE.md")
        assert result["success"] is True

        # Verify original restored
        restored = (temp_repo / "CLAUDE.md").read_text(encoding="utf-8")
        assert restored == original

    def test_rollback_no_backup_fails(self, sentinel):
        """rollback with no backup should return error."""
        result = sentinel.rollback("nonexistent.md")
        assert result["success"] is False

    def test_compile_nonexistent_fails(self, sentinel):
        """compile_to_staged on missing file should fail gracefully."""
        result = sentinel.compile_to_staged("does_not_exist.md")
        assert result["success"] is False


# ============ Unit Tests: Pattern Memory ============ #

class TestPatternMemory:
    """Test learning and outcome recording."""

    def test_record_success(self, sentinel):
        """record_outcome should track successes."""
        sentinel.record_outcome("test.md", success=True, reason="good compression")
        assert "test.md" in sentinel._pattern_memory
        assert sentinel._pattern_memory["test.md"]["successes"] == 1
        assert sentinel._pattern_memory["test.md"]["success_rate"] == 1.0

    def test_record_failure(self, sentinel):
        """record_outcome should track failures."""
        sentinel.record_outcome("test.md", success=False, reason="too aggressive")
        assert sentinel._pattern_memory["test.md"]["failures"] == 1
        assert sentinel._pattern_memory["test.md"]["success_rate"] == 0.0

    def test_success_rate_calculation(self, sentinel):
        """Success rate should update correctly over multiple outcomes."""
        sentinel.record_outcome("test.md", success=True)
        sentinel.record_outcome("test.md", success=True)
        sentinel.record_outcome("test.md", success=False)
        assert abs(sentinel._pattern_memory["test.md"]["success_rate"] - 0.6667) < 0.01

    def test_pattern_memory_persistence(self, sentinel):
        """Pattern memory should persist to disk."""
        sentinel.record_outcome("test.md", success=True)
        sentinel._save_pattern_memory()

        assert sentinel.pattern_memory_path.exists()
        data = json.loads(sentinel.pattern_memory_path.read_text(encoding="utf-8"))
        assert "test.md" in data


# ============ Unit Tests: Full Scan ============ #

class TestFullScan:
    """Test the check() method (full scan pipeline)."""

    def test_check_returns_valid_status(self, sentinel):
        """check() should return a valid M2MCompressionStatus dict."""
        result = sentinel.check(force=True)
        assert result["available"] is True
        assert "files_scanned" in result
        assert "candidates_found" in result
        assert "severity" in result
        assert "message" in result

    def test_check_caches_results(self, sentinel):
        """Second check() should return cached result."""
        result1 = sentinel.check(force=True)
        result2 = sentinel.check(force=False)
        assert result2.get("cached") is True

    def test_check_force_bypasses_cache(self, sentinel):
        """check(force=True) should always run fresh scan."""
        sentinel.check(force=True)
        result = sentinel.check(force=True)
        assert result.get("cached", False) is False


# ============ P0 Hardening Tests ============ #

class TestHardening:
    """P0 hardening tests from 0102 audit.

    Validates: method truthfulness, YAML validity, path stability,
    deterministic promotion, rollback safety, and eval pipeline.
    """

    def test_compilation_method_truthful(self, sentinel, temp_repo):
        """Compilation method should be 'deterministic' when Qwen unavailable."""
        doc = temp_repo / "modules" / "test_mod" / "INTERFACE.md"
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text("# Test Module\n\n## Overview\n\nSome content here.\n", encoding="utf-8")

        result = sentinel.compile_to_staged(
            str(doc.relative_to(temp_repo)),
            use_qwen=False,
        )
        assert result["success"] is True
        assert result["compilation_method"] == "deterministic"

    def test_compilation_method_not_qwen_on_fallback(self, sentinel, temp_repo):
        """Method should NOT say 'qwen' if Qwen returns None."""
        doc = temp_repo / "modules" / "test_mod2" / "README.md"
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text("# Readme\n\n## API\n\n- `status`: Active\n", encoding="utf-8")

        # use_qwen=True but Qwen is unavailable -> should still say deterministic
        result = sentinel.compile_to_staged(
            str(doc.relative_to(temp_repo)),
            use_qwen=True,
        )
        assert result["success"] is True
        assert result["compilation_method"] == "deterministic"

    def test_m2m_validation_rejects_empty(self, sentinel):
        """Validation should reject empty output."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import M2MCompressionSentinel
        result = M2MCompressionSentinel._validate_m2m_output("", "test.md")
        assert result["valid"] is False

    def test_m2m_validation_rejects_no_header(self, sentinel):
        """Validation should reject content without M2M header."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import M2MCompressionSentinel
        result = M2MCompressionSentinel._validate_m2m_output(
            "SOME_SECTION:\n  KEY: value\n  KEY2: value2\n", "test.md"
        )
        assert result["valid"] is False

    def test_m2m_validation_rejects_no_sections(self, sentinel):
        """Validation should reject content with header but no section keys."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import M2MCompressionSentinel
        result = M2MCompressionSentinel._validate_m2m_output(
            "# M2M v1.0 | test.md | 20260213\n\njust some text\n", "test.md"
        )
        assert result["valid"] is False

    def test_m2m_validation_accepts_valid(self, sentinel):
        """Validation should accept well-formed M2M content."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import M2MCompressionSentinel
        result = M2MCompressionSentinel._validate_m2m_output(
            "# M2M v1.0 | test.md | 20260213\n\nOVERVIEW:\n  KEY: value\n", "test.md"
        )
        assert result["valid"] is True

    def test_m2m_validation_rejects_corruption(self, sentinel):
        """Validation should reject content with encoding corruption."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import M2MCompressionSentinel
        result = M2MCompressionSentinel._validate_m2m_output(
            "# M2M v1.0 | test.md | 20260213\n\nSECTION:\n  KEY: val\ufffd\n", "test.md"
        )
        assert result["valid"] is False

    def test_staged_path_uses_full_relpath(self, sentinel, temp_repo):
        """Staged files should use full relative path (not just parent name)."""
        # Create two files with same parent name but different paths
        doc1 = temp_repo / "modules" / "a" / "sub" / "INTERFACE.md"
        doc2 = temp_repo / "modules" / "b" / "sub" / "INTERFACE.md"
        doc1.parent.mkdir(parents=True, exist_ok=True)
        doc2.parent.mkdir(parents=True, exist_ok=True)
        doc1.write_text("# Module A Sub\n\n## Interface\n\n- `Name`: A\n", encoding="utf-8")
        doc2.write_text("# Module B Sub\n\n## Interface\n\n- `Name`: B\n", encoding="utf-8")

        r1 = sentinel.compile_to_staged(str(doc1.relative_to(temp_repo)), use_qwen=False)
        r2 = sentinel.compile_to_staged(str(doc2.relative_to(temp_repo)), use_qwen=False)

        assert r1["success"] and r2["success"]
        # Staged paths should be different (not collide)
        assert r1["staged_path"] != r2["staged_path"]

    def test_header_contains_source_path(self, sentinel, temp_repo):
        """M2M header should contain src: field for deterministic promotion."""
        doc = temp_repo / "modules" / "mymod" / "INTERFACE.md"
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text("# My Module\n\n## API\n\n- `Status`: Active\n", encoding="utf-8")

        rel = str(doc.relative_to(temp_repo))
        result = sentinel.compile_to_staged(rel, use_qwen=False)
        assert result["success"]

        staged = Path(temp_repo / result["staged_path"])
        content = staged.read_text(encoding="utf-8")
        header = content.splitlines()[0]
        assert "src:" in header
        assert rel.replace("\\", "/") in header.replace("\\", "/") or "INTERFACE.md" in header

    def test_eval_returns_metrics(self, repo_root):
        """evaluate_staged() should return similarity metrics for real staged files."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import M2MCompressionSentinel
        sentinel = M2MCompressionSentinel(repo_root)
        result = sentinel.evaluate_staged()

        if result.get("pairs_evaluated", 0) > 0:
            assert "avg_cosine_similarity" in result
            assert "verdict" in result
            assert result["avg_cosine_similarity"] > 0.3, \
                f"Avg similarity {result['avg_cosine_similarity']} too low (minimum 0.3)"
            assert result["verdict"] in ("excellent", "acceptable", "needs_improvement")


# ============ Boot Prompt Detection ============ #

class TestBootPromptDetection:
    """Content-based boot prompt detection.

    Boot prompts (WSP_00, CLAUDE.md) contain identity-lock patterns,
    equations, and code blocks that M2M strips. Detection is content-based,
    not filename-based: 3+ signals = boot prompt.
    """

    def test_detects_boot_prompt_with_identity_lock(self, sentinel, temp_repo):
        """Files with I AM 0102, φ=1.618, 7.05Hz → boot prompt."""
        boot_doc = temp_repo / "WSP_framework" / "src" / "WSP_00_Test.md"
        boot_doc.parent.mkdir(parents=True, exist_ok=True)
        boot_doc.write_text(
            "# WSP_00: Boot Protocol\n\n"
            "I AM 0102 - the neural network.\n"
            "φ=1.618 golden ratio.\n"
            "Resonance at 7.05Hz.\n"
            "State: 01(02) -> 0102\n"
            "Coherence≥0.618\n"
            "VI scaffolding must be shed.\n"
            "\n" * 50,
            encoding="utf-8",
        )
        analysis = sentinel._analyze_file(boot_doc)
        assert analysis is not None
        assert analysis.action == "boot_prompt_skip"
        assert "boot_prompt" in analysis.reasons[0]

    def test_compile_rejects_boot_prompt(self, sentinel, temp_repo):
        """compile_to_staged should refuse boot prompt content."""
        boot_doc = temp_repo / "modules" / "test_module" / "BOOT.md"
        boot_doc.parent.mkdir(parents=True, exist_ok=True)
        boot_doc.write_text(
            "# Boot\n\nI AM 0102.\nφ=1.618\n7.05Hz resonance.\n"
            "01(02) -> 0102 state transition.\n"
            "Coherence≥0.618 threshold.\n"
            "VI scaffolding patterns.\n",
            encoding="utf-8",
        )
        result = sentinel.compile_to_staged(
            str(boot_doc.relative_to(temp_repo)), use_qwen=False
        )
        assert result["success"] is False
        assert result.get("boot_prompt") is True

    def test_normal_docs_pass_through(self, sentinel, temp_repo):
        """Normal reference docs (no boot signals) should NOT be flagged."""
        analysis = sentinel._analyze_file(temp_repo / "CLAUDE.md")
        assert analysis is not None
        assert analysis.action != "boot_prompt_skip"

    def test_threshold_requires_3_signals(self, sentinel, temp_repo):
        """Fewer than 3 boot signals should NOT trigger exclusion."""
        partial_doc = temp_repo / "modules" / "test_module" / "PARTIAL.md"
        partial_doc.parent.mkdir(parents=True, exist_ok=True)
        partial_doc.write_text(
            "# Protocol\n\n"
            "Resonance at 7.05Hz frequency.\n"
            "The system uses φ=1.618 ratio.\n"
            "But no identity lock or state transitions.\n"
            "\n" * 50,
            encoding="utf-8",
        )
        analysis = sentinel._analyze_file(partial_doc)
        assert analysis is not None
        assert analysis.action != "boot_prompt_skip", \
            "Only 2 signals should not trigger boot prompt exclusion"

    def test_skill_files_excluded_by_convention(self, sentinel, temp_repo):
        """SKILL.md and SKILLz.md are always executable → boot_prompt_skip."""
        skill_dir = temp_repo / "modules" / "test_module" / "skillz" / "my_skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_doc = skill_dir / "SKILLz.md"
        skill_doc.write_text(
            "# My Skill\n\n## Commands\n\n```python\nresult = do_thing()\n```\n"
            "\n" * 50,
            encoding="utf-8",
        )
        analysis = sentinel._analyze_file(skill_doc)
        assert analysis is not None
        assert analysis.action == "boot_prompt_skip"
        assert "skill_file_convention" in analysis.reasons[0]

    def test_compile_rejects_skill_file(self, sentinel, temp_repo):
        """compile_to_staged should refuse SKILL.md files."""
        skill_dir = temp_repo / ".claude" / "skills" / "test_skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_doc = skill_dir / "SKILL.md"
        skill_doc.write_text(
            "# Test Skill\n\n## Execution\n\nRun the code.\n",
            encoding="utf-8",
        )
        result = sentinel.compile_to_staged(
            str(skill_doc.relative_to(temp_repo)), use_qwen=False
        )
        assert result["success"] is False
        assert result.get("boot_prompt") is True


# ============ Benchmarks ============ #

class TestBenchmarks:
    """Performance benchmarks for M2M compression pipeline.

    These test against the REAL repo for meaningful metrics.
    """

    def test_benchmark_full_scan(self, repo_root):
        """Benchmark: Full repo scan latency."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import (
            M2MCompressionSentinel,
        )
        sentinel = M2MCompressionSentinel(repo_root)

        start = time.perf_counter()
        result = sentinel.check(force=True)
        elapsed = time.perf_counter() - start

        print(f"\n=== M2M SCAN BENCHMARK ===")
        print(f"Scan time: {elapsed:.3f}s")
        print(f"Files scanned: {result['files_scanned']}")
        print(f"Candidates found: {result['candidates_found']}")
        print(f"Auto-apply: {result['auto_apply_count']}")
        print(f"Stage-promote: {result['stage_promote_count']}")
        print(f"Stage-review: {result['stage_review_count']}")
        print(f"Flag-only: {result['flag_only_count']}")
        print(f"Est. savings: {result['total_estimated_savings_percent']:.1f}%")
        print(f"Throughput: {result['files_scanned'] / elapsed:.1f} files/sec")

        assert elapsed < 60, f"Scan took {elapsed:.1f}s (threshold: 60s)"
        assert result["files_scanned"] > 0, "Should find files to scan"

    def test_benchmark_deterministic_transform(self, repo_root):
        """Benchmark: Deterministic transform speed and quality per file type."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import (
            M2MCompressionSentinel,
        )
        sentinel = M2MCompressionSentinel(repo_root)

        test_files = [
            ("CLAUDE.md", "root_config"),
            ("modules/ai_intelligence/ai_overseer/INTERFACE.md", "interface"),
        ]

        print(f"\n=== DETERMINISTIC TRANSFORM BENCHMARK ===")
        print(f"{'File':<50} {'Lines':<8} {'M2M':<8} {'Reduction':<12} {'Time':<10}")
        print("-" * 90)

        for rel_path, category in test_files:
            full_path = repo_root / rel_path
            if not full_path.exists():
                continue

            content = full_path.read_text(encoding="utf-8", errors="replace")
            original_lines = len(content.splitlines())

            start = time.perf_counter()
            m2m = sentinel._transform_to_m2m(content, full_path.name)
            elapsed = time.perf_counter() - start

            m2m_lines = len(m2m.splitlines())
            reduction = (original_lines - m2m_lines) / original_lines * 100 if original_lines > 0 else 0

            print(f"{rel_path:<50} {original_lines:<8} {m2m_lines:<8} {reduction:.1f}%{'':<6} {elapsed*1000:.1f}ms")

            assert elapsed < 1.0, f"Transform took {elapsed:.1f}s (threshold: 1s)"
            assert reduction > 30, f"Expected > 30% reduction for {rel_path}, got {reduction:.1f}%"

    def test_benchmark_staged_roundtrip(self, repo_root):
        """Benchmark: Compile -> List -> stage workflow latency."""
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import (
            M2MCompressionSentinel,
        )
        sentinel = M2MCompressionSentinel(repo_root)

        # Compile
        start = time.perf_counter()
        compile_result = sentinel.compile_to_staged(
            "modules/ai_intelligence/ai_overseer/INTERFACE.md",
            use_qwen=False,
        )
        compile_time = time.perf_counter() - start

        # List
        start = time.perf_counter()
        list_result = sentinel.list_staged()
        list_time = time.perf_counter() - start

        print(f"\n=== STAGED ROUNDTRIP BENCHMARK ===")
        print(f"Compile: {compile_time*1000:.1f}ms")
        print(f"  Result: {compile_result.get('reduction_percent', 0):.1f}% reduction")
        print(f"  Method: {compile_result.get('compilation_method', 'unknown')}")
        print(f"List staged: {list_time*1000:.1f}ms")
        print(f"  Total staged: {list_result['total_staged']}")

        assert compile_result["success"] is True
        assert compile_time < 5.0, f"Compile took {compile_time:.1f}s"
        assert list_time < 2.0, f"List took {list_time:.1f}s"


# ============ Runner ============ #

if __name__ == "__main__":
    """Direct execution for quick benchmark runs."""
    import sys

    repo_root = Path(__file__).resolve().parents[4]

    print("=" * 60)
    print("M2M Compression Sentinel - Benchmark Suite")
    print("=" * 60)

    from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import (
        M2MCompressionSentinel,
    )

    sentinel = M2MCompressionSentinel(repo_root)

    # 1. Full scan benchmark
    print("\n--- Full Scan ---")
    start = time.perf_counter()
    result = sentinel.check(force=True)
    elapsed = time.perf_counter() - start
    print(f"Time: {elapsed:.3f}s | Files: {result['files_scanned']} | "
          f"Candidates: {result['candidates_found']} | "
          f"Savings: {result['total_estimated_savings_percent']:.1f}%")

    # 2. Per-file transform benchmark
    print("\n--- Deterministic Transform ---")
    test_files = list(Path(repo_root).glob("modules/**/INTERFACE.md"))[:5]
    for fp in test_files:
        content = fp.read_text(encoding="utf-8", errors="replace")
        orig = len(content.splitlines())
        start = time.perf_counter()
        m2m = sentinel._transform_to_m2m(content, fp.name)
        elapsed = time.perf_counter() - start
        m2m_lines = len(m2m.splitlines())
        reduction = (orig - m2m_lines) / orig * 100 if orig > 0 else 0
        rel = fp.relative_to(repo_root)
        print(f"  {str(rel):<55} {orig:>4} -> {m2m_lines:>4} ({reduction:.0f}%) {elapsed*1000:.0f}ms")

    # 3. Staged workflow
    print("\n--- Staged Workflow ---")
    staged = sentinel.list_staged()
    print(f"  Staged files: {staged['total_staged']}")
    for module, files in staged["by_module"].items():
        print(f"  {module}: {len(files)} files")

    print(f"\nBenchmark complete.")
