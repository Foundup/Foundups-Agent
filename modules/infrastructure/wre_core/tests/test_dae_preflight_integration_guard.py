#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression guard: required DAE entrypoints must wire WRE preflight.

This fails fast if someone adds/removes launch logic and forgets to keep
`run_dae_preflight(...)` or `@preflight_guard(...)` integration.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


REQUIRED_ENTRYPOINTS = [
    # Root entrypoint
    "main.py",
    # Already integrated DAEs
    "modules/ai_intelligence/holo_dae/scripts/launch.py",
    "modules/platform_integration/social_media_orchestrator/scripts/launch.py",
    "modules/platform_integration/youtube_shorts_scheduler/scripts/launch.py",
    # Remaining DAEs integrated in this rollout
    "modules/ai_intelligence/pqn/scripts/launch.py",
    "modules/communication/auto_meeting_orchestrator/scripts/launch.py",
    "modules/communication/liberty_alert/scripts/launch.py",
    "modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/launch.py",
    "modules/infrastructure/evade_net/scripts/launch.py",
    "modules/infrastructure/git_push_dae/scripts/launch.py",
    "modules/ai_intelligence/training_system/scripts/launch.py",
]


def _has_launch_preflight_integration(source_text: str) -> bool:
    """True if file uses shared preflight module via decorator or direct call."""
    has_shared_import = "modules.infrastructure.wre_core.src.dae_preflight" in source_text
    has_guard = "@preflight_guard(" in source_text
    has_direct_call = "run_dae_preflight(" in source_text
    return has_shared_import and (has_guard or has_direct_call)


def _has_main_startup_preflight(source_text: str) -> bool:
    """True if main.py has explicit dashboard preflight wiring."""
    return (
        "modules.infrastructure.wre_core.src.dashboard_alerts" in source_text
        and "check_dashboard_health(" in source_text
        and "[WRE-DASHBOARD] preflight=" in source_text
    )


def _has_shared_security_preflight(source_text: str) -> bool:
    """True if shared DAE preflight includes OpenClaw security sentinel gate."""
    return (
        "OpenClawSecuritySentinel" in source_text
        and "OPENCLAW_SECURITY_PREFLIGHT" in source_text
        and "SECURITY preflight=" in source_text
    )


def test_required_dae_entrypoints_have_wre_preflight():
    missing_files = []
    missing_integration = []

    for rel_path in REQUIRED_ENTRYPOINTS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            missing_files.append(rel_path)
            continue

        source = path.read_text(encoding="utf-8", errors="replace")
        if rel_path == "main.py":
            if not _has_main_startup_preflight(source):
                missing_integration.append(rel_path)
        elif not _has_launch_preflight_integration(source):
            missing_integration.append(rel_path)

    assert not missing_files, (
        "Required DAE entrypoint files missing:\n- " + "\n- ".join(missing_files)
    )
    assert not missing_integration, (
        "Required DAE entrypoints missing WRE preflight integration "
        "(need `run_dae_preflight(...)` or `@preflight_guard(...)`):\n- "
        + "\n- ".join(missing_integration)
    )


def test_shared_dae_preflight_has_openclaw_security_gate():
    path = REPO_ROOT / "modules/infrastructure/wre_core/src/dae_preflight.py"
    assert path.exists(), "Shared DAE preflight module missing"
    source = path.read_text(encoding="utf-8", errors="replace")
    assert _has_shared_security_preflight(source), (
        "Shared DAE preflight must include OpenClaw security sentinel gate "
        "(OPENCLAW_SECURITY_PREFLIGHT + OpenClawSecuritySentinel)."
    )
