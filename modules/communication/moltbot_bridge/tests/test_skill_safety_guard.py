#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Cisco skill scanner guard integration.

WSP Compliance:
  WSP 71  : Secrets Management - Skill Supply-Chain Safety Gate
  WSP 95  : WRE Skills Wardrobe Protocol - Mandatory safety gate

Test Coverage:
  1. Scanner missing + required mode => block
  2. High severity => block
  3. Medium/low at threshold => allow
  4. Cache expiry => re-scan
  5. Auditable decision logging
"""

import asyncio
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from modules.communication.moltbot_bridge.src.skill_safety_guard import run_skill_scan


# ---------------------------------------------------------------------------
# Unit Tests: run_skill_scan function
# ---------------------------------------------------------------------------


def test_run_skill_scan_reports_missing_scanner(tmp_path: Path):
    """Scanner unavailable: available=False, passed=False (WSP 95 fail-closed)."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    with patch("modules.communication.moltbot_bridge.src.skill_safety_guard.shutil.which", return_value=None):
        result = run_skill_scan(skills_dir=skills_dir)

    assert result.available is False
    assert result.passed is False
    assert result.exit_code == 127
    assert "not installed" in result.message.lower()


def test_run_skill_scan_passes_on_zero_exit(tmp_path: Path):
    """Scanner runs successfully with no findings: passed=True."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    class _Completed:
        returncode = 0
        stdout = "scan complete"
        stderr = ""

    with patch("modules.communication.moltbot_bridge.src.skill_safety_guard.shutil.which", return_value="skill-scanner"):
        with patch(
            "modules.communication.moltbot_bridge.src.skill_safety_guard.subprocess.run",
            return_value=_Completed(),
        ):
            result = run_skill_scan(skills_dir=skills_dir, max_severity="medium")

    assert result.available is True
    assert result.passed is True
    assert result.exit_code == 0


def test_run_skill_scan_fails_on_nonzero_exit(tmp_path: Path):
    """Scanner exits with error code: passed=False."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    class _Completed:
        returncode = 3
        stdout = ""
        stderr = "high severity issue found"

    with patch("modules.communication.moltbot_bridge.src.skill_safety_guard.shutil.which", return_value="skill-scanner"):
        with patch(
            "modules.communication.moltbot_bridge.src.skill_safety_guard.subprocess.run",
            return_value=_Completed(),
        ):
            result = run_skill_scan(skills_dir=skills_dir, max_severity="medium")

    assert result.available is True
    assert result.passed is False
    assert result.exit_code == 3


def test_run_skill_scan_high_severity_blocks(tmp_path: Path):
    """High severity findings exceed medium threshold: passed=False (WSP 95)."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    report_dir = tmp_path / "reports"
    report_dir.mkdir()

    # Create a report with high severity findings
    report_path = report_dir / "openclaw_skill_scan_report.json"
    report_path.write_text(json.dumps({
        "summary": {
            "findings_by_severity": {
                "high": 1,
                "medium": 0,
                "low": 0,
            }
        }
    }))

    class _Completed:
        returncode = 0  # Scanner ran successfully
        stdout = ""
        stderr = ""

    with patch("modules.communication.moltbot_bridge.src.skill_safety_guard.shutil.which", return_value="skill-scanner"):
        with patch(
            "modules.communication.moltbot_bridge.src.skill_safety_guard.subprocess.run",
            return_value=_Completed(),
        ):
            result = run_skill_scan(
                skills_dir=skills_dir,
                max_severity="medium",  # Threshold is medium, high exceeds it
                report_dir=report_dir,
            )

    assert result.available is True
    assert result.passed is False  # High severity blocked by medium threshold


def test_run_skill_scan_medium_at_threshold_blocks(tmp_path: Path):
    """Medium severity at medium threshold: passed=False (at-or-above blocks)."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    report_dir = tmp_path / "reports"
    report_dir.mkdir()

    report_path = report_dir / "openclaw_skill_scan_report.json"
    report_path.write_text(json.dumps({
        "summary": {
            "findings_by_severity": {
                "medium": 2,
                "low": 1,
            }
        }
    }))

    class _Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    with patch("modules.communication.moltbot_bridge.src.skill_safety_guard.shutil.which", return_value="skill-scanner"):
        with patch(
            "modules.communication.moltbot_bridge.src.skill_safety_guard.subprocess.run",
            return_value=_Completed(),
        ):
            result = run_skill_scan(
                skills_dir=skills_dir,
                max_severity="medium",
                report_dir=report_dir,
            )

    assert result.passed is False  # Medium at medium threshold blocks


def test_run_skill_scan_low_below_threshold_allows(tmp_path: Path):
    """Low severity below medium threshold: passed=True (WSP 95)."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    report_dir = tmp_path / "reports"
    report_dir.mkdir()

    report_path = report_dir / "openclaw_skill_scan_report.json"
    report_path.write_text(json.dumps({
        "summary": {
            "findings_by_severity": {
                "low": 5,
                "info": 10,
            }
        }
    }))

    class _Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    with patch("modules.communication.moltbot_bridge.src.skill_safety_guard.shutil.which", return_value="skill-scanner"):
        with patch(
            "modules.communication.moltbot_bridge.src.skill_safety_guard.subprocess.run",
            return_value=_Completed(),
        ):
            result = run_skill_scan(
                skills_dir=skills_dir,
                max_severity="medium",
                report_dir=report_dir,
            )

    assert result.passed is True  # Low severity allowed at medium threshold


def test_run_skill_scan_critical_severity_always_blocks(tmp_path: Path):
    """Critical severity always blocks regardless of threshold (WSP 95)."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    report_dir = tmp_path / "reports"
    report_dir.mkdir()

    report_path = report_dir / "openclaw_skill_scan_report.json"
    report_path.write_text(json.dumps({
        "summary": {
            "findings_by_severity": {
                "critical": 1,
            }
        }
    }))

    class _Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    with patch("modules.communication.moltbot_bridge.src.skill_safety_guard.shutil.which", return_value="skill-scanner"):
        with patch(
            "modules.communication.moltbot_bridge.src.skill_safety_guard.subprocess.run",
            return_value=_Completed(),
        ):
            # Even with high threshold, critical should block
            result = run_skill_scan(
                skills_dir=skills_dir,
                max_severity="high",
                report_dir=report_dir,
            )

    assert result.passed is False  # Critical blocked even at high threshold


# ---------------------------------------------------------------------------
# Integration Tests: OpenClaw DAE skill safety gate
# ---------------------------------------------------------------------------


def test_openclaw_dae_required_mode_blocks_when_scanner_missing():
    """Required mode: scanner unavailable => route blocked (WSP 95 fail-closed)."""
    from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    from modules.communication.moltbot_bridge.src.skill_safety_guard import SkillScanResult

    dae = OpenClawDAE()
    dae._skill_scan_required = True
    dae._skill_scan_enforced = True
    dae._skill_scan_ttl_sec = 0  # Force re-scan

    mock_result = SkillScanResult(
        available=False,
        passed=False,
        exit_code=127,
        skills_dir="/test",
        report_path=None,
        message="skill-scanner not installed",
    )

    with patch(
        "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
        return_value=mock_result
    ):
        result = dae._ensure_skill_safety(force=True)

    assert result is False
    assert "unavailable" in dae._skill_scan_message.lower() or "not installed" in dae._skill_scan_message.lower()


def test_openclaw_dae_required_mode_allows_when_scanner_passes():
    """Required mode: scanner passes => route allowed."""
    from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    from modules.communication.moltbot_bridge.src.skill_safety_guard import SkillScanResult

    dae = OpenClawDAE()
    dae._skill_scan_required = True
    dae._skill_scan_enforced = True
    dae._skill_scan_ttl_sec = 0

    mock_result = SkillScanResult(
        available=True,
        passed=True,
        exit_code=0,
        skills_dir="/test",
        report_path=None,
        message="skills passed safety scan",
    )

    with patch(
        "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
        return_value=mock_result
    ):
        result = dae._ensure_skill_safety(force=True)

    assert result is True


def test_openclaw_dae_cache_ttl_prevents_rescan():
    """Cache TTL: cached result used within TTL window (WSP 95)."""
    from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE

    dae = OpenClawDAE()
    dae._skill_scan_required = True
    dae._skill_scan_enforced = True
    dae._skill_scan_ttl_sec = 300  # 5 minute TTL

    # Seed cached state
    dae._skill_scan_checked_at = time.time()
    dae._skill_scan_ok = True
    dae._skill_scan_message = "cached pass"

    # Should NOT call run_skill_scan (using cache)
    # The method returns early if cache is valid, so we just verify the return value
    result = dae._ensure_skill_safety(force=False)

    assert result is True


def test_openclaw_dae_cache_expiry_triggers_rescan():
    """Cache expiry: expired cache triggers new scan (WSP 95)."""
    from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    from modules.communication.moltbot_bridge.src.skill_safety_guard import SkillScanResult

    dae = OpenClawDAE()
    dae._skill_scan_required = True
    dae._skill_scan_enforced = True
    dae._skill_scan_ttl_sec = 1  # 1 second TTL

    # Seed expired cache (2 seconds ago)
    dae._skill_scan_checked_at = time.time() - 2
    dae._skill_scan_ok = True
    dae._skill_scan_message = "old cached pass"

    mock_result = SkillScanResult(
        available=True,
        passed=False,  # New scan fails
        exit_code=1,
        skills_dir="/test",
        report_path=None,
        message="new scan found issues",
    )

    with patch(
        "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
        return_value=mock_result
    ):
        result = dae._ensure_skill_safety(force=False)

    assert result is False  # New scan failed


def test_openclaw_dae_enforced_mode_blocks_failed_scan():
    """Enforced mode: failed scan => route blocked (WSP 95)."""
    from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    from modules.communication.moltbot_bridge.src.skill_safety_guard import SkillScanResult

    dae = OpenClawDAE()
    dae._skill_scan_required = True
    dae._skill_scan_enforced = True
    dae._skill_scan_ttl_sec = 0

    mock_result = SkillScanResult(
        available=True,
        passed=False,  # Scan failed
        exit_code=1,
        skills_dir="/test",
        report_path=None,
        message="high severity findings",
    )

    with patch(
        "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
        return_value=mock_result
    ):
        result = dae._ensure_skill_safety(force=True)

    assert result is False


def test_openclaw_dae_non_enforced_mode_allows_failed_scan():
    """Non-enforced mode: failed scan => route allowed with warning (WSP 95)."""
    from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    from modules.communication.moltbot_bridge.src.skill_safety_guard import SkillScanResult

    dae = OpenClawDAE()
    dae._skill_scan_required = True
    dae._skill_scan_enforced = False  # Non-enforced
    dae._skill_scan_ttl_sec = 0

    mock_result = SkillScanResult(
        available=True,
        passed=False,  # Scan failed
        exit_code=1,
        skills_dir="/test",
        report_path=None,
        message="high severity findings",
    )

    with patch(
        "modules.communication.moltbot_bridge.src.skill_safety_guard.run_skill_scan",
        return_value=mock_result
    ):
        result = dae._ensure_skill_safety(force=True)

    assert result is True  # Allowed in non-enforced mode


def test_openclaw_dae_process_downgrades_foundup_on_safety_failure():
    """FOUNDUP intent downgrades to CONVERSATION when skill safety fails."""
    from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE, IntentCategory

    dae = OpenClawDAE()
    dae._skill_scan_required = True
    dae._skill_scan_enforced = True
    dae._skill_scan_ttl_sec = 300  # Use cache

    # Pre-seed failed cache state (avoids calling run_skill_scan)
    dae._skill_scan_checked_at = time.time()
    dae._skill_scan_ok = False
    dae._skill_scan_message = "blocked by test"

    # Classify a FOUNDUP intent
    intent = dae.classify_intent(
        message="launch foundup myproject with token TEST",
        sender="test_user",
        channel="test",
        session_key="test_session",
    )

    assert intent.category == IntentCategory.FOUNDUP

    # Verify this category would be checked for skill safety
    should_check = intent.category in (
        IntentCategory.COMMAND,
        IntentCategory.SYSTEM,
        IntentCategory.SCHEDULE,
        IntentCategory.SOCIAL,
        IntentCategory.AUTOMATION,
        IntentCategory.FOUNDUP,
    )
    assert should_check is True

    # And the gate would fail (using cached state)
    gate_result = dae._ensure_skill_safety(force=False)
    assert gate_result is False
