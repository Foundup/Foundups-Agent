#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw / IronClaw capability + drift audit.

Purpose:
- Audit which top-level CLI options are accessible via OpenClaw routes.
- Detect model-switch drift against AI Gateway/model registry choices.
- Probe IronClaw runtime health and model visibility.
- Persist a daily report for operator review.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MAIN_MENU_OPTION_HINTS: Dict[str, Dict[str, str]] = {
    "0": {
        "status": "partial",
        "via": "command/wre_orchestrator",
        "note": "Git menu has no dedicated OpenClaw adapter contract.",
    },
    "1": {
        "status": "partial",
        "via": "automation/schedule -> youtube_automation_adapter",
        "note": "Comments/indexing/scheduling are exposed; full YouTube submenu parity is not guaranteed.",
    },
    "2": {
        "status": "partial",
        "via": "query -> holo_index",
        "note": "Search path is exposed; HoloDAE operational submenu controls are not directly mapped.",
    },
    "3": {
        "status": "partial",
        "via": "automation -> auto_moderator_bridge",
        "note": "Intent route exists but not full AMO menu parity.",
    },
    "4": {
        "status": "direct",
        "via": "social adapters",
        "note": "LinkedIn/X/social campaign commands are directly handled.",
    },
    "5": {
        "status": "unmapped",
        "via": "none",
        "note": "No dedicated Liberty Alert DAE route in OpenClaw intents.",
    },
    "6": {
        "status": "direct",
        "via": "research -> pqn_research_adapter",
        "note": "PQN research/teaching/demo/publish paths are routed.",
    },
    "7": {
        "status": "unmapped",
        "via": "none",
        "note": "Liberty mesh alert option is not represented in OpenClaw routes.",
    },
    "8": {
        "status": "unmapped",
        "via": "none",
        "note": "Vision DAE launch path is not exposed as a dedicated OpenClaw route.",
    },
    "9": {
        "status": "unmapped",
        "via": "none",
        "note": "No single 'all DAEs' orchestration route in OpenClaw.",
    },
    "10": {
        "status": "n_a",
        "via": "n_a",
        "note": "Interactive exit option (not a DAE capability).",
    },
    "00": {
        "status": "partial",
        "via": "monitor intent",
        "note": "OpenClaw monitor reports health, but not full main-menu status pipeline.",
    },
    "11": {
        "status": "unmapped",
        "via": "none",
        "note": "Training system menu path has no dedicated OpenClaw route.",
    },
    "12": {
        "status": "unmapped",
        "via": "none",
        "note": "MCP services menu is not directly mapped through OpenClaw intents.",
    },
    "13": {
        "status": "unmapped",
        "via": "none",
        "note": "Dependency launcher is not exposed as a dedicated OpenClaw route.",
    },
    "14": {
        "status": "partial",
        "via": "foundup -> fam_adapter",
        "note": "FoundUp launch paths are routed; full ecosystem menu parity is broader.",
    },
    "15": {
        "status": "partial",
        "via": "command/wre_orchestrator",
        "note": "Follow-WSP contract is available in CLI; OpenClaw uses generic command routing.",
    },
    "16": {
        "status": "direct",
        "via": "openclaw_menu/openclaw_dae",
        "note": "Native OpenClaw/IronClaw menu and chat/voice paths.",
    },
    "17": {
        "status": "partial",
        "via": "monitor intent",
        "note": "Dashboard-like health snapshots are exposed, not full dashboard UX.",
    },
    "18": {
        "status": "partial",
        "via": "query intent",
        "note": "Explainer content can be queried, but no dedicated explainer route.",
    },
    "19": {
        "status": "direct",
        "via": "connect_wre deterministic conversation contract",
        "note": "OpenClaw includes explicit Connect-WRE command handling.",
    },
    "20": {
        "status": "unmapped",
        "via": "none",
        "note": "antifaFM broadcaster has no dedicated OpenClaw route.",
    },
}


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _extract_main_menu_options(main_menu_path: Path) -> Dict[str, str]:
    """
    Parse top-level CLI options from main_menu.py print lines.

    Keeps the first occurrence for each option id; this aligns with the top-level
    main menu block in the current file layout.
    """
    text = _safe_read_text(main_menu_path)
    if not text:
        return {}

    options: Dict[str, str] = {}
    pattern = re.compile(r'print\("(?P<opt>00|\d{1,2})\.\s*(?P<label>[^"]+)"\)')
    for match in pattern.finditer(text):
        opt = match.group("opt")
        label = match.group("label").strip()
        if opt not in options:
            options[opt] = label
    return options


def _extract_openclaw_menu_options(openclaw_menu_path: Path) -> Dict[str, str]:
    text = _safe_read_text(openclaw_menu_path)
    if not text:
        return {}

    options: Dict[str, str] = {}
    pattern = re.compile(r'print\("\s*(?P<opt>0|\d)\.\s*(?P<label>[^"]+)"\)')
    for match in pattern.finditer(text):
        opt = match.group("opt")
        label = match.group("label").strip()
        if opt not in options:
            options[opt] = label
    return options


def _ensure_repo_on_path(root: Path) -> None:
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _audit_cli_coverage(main_menu_options: Dict[str, str]) -> Dict[str, Any]:
    entries: List[Dict[str, str]] = []
    counts = {"direct": 0, "partial": 0, "unmapped": 0, "n_a": 0}
    unknown = []

    for option_id in sorted(main_menu_options.keys(), key=lambda x: (len(x), x)):
        hint = MAIN_MENU_OPTION_HINTS.get(option_id)
        if hint is None:
            unknown.append(option_id)
            hint = {
                "status": "unmapped",
                "via": "none",
                "note": "No capability hint configured.",
            }
        status = hint["status"]
        counts[status] = counts.get(status, 0) + 1
        entries.append(
            {
                "option": option_id,
                "label": main_menu_options[option_id],
                "status": status,
                "via": hint["via"],
                "note": hint["note"],
            }
        )

    tracked_total = counts["direct"] + counts["partial"] + counts["unmapped"]
    coverage_ratio = round(
        ((counts["direct"] + counts["partial"]) / tracked_total) if tracked_total else 0.0,
        4,
    )
    return {
        "entries": entries,
        "counts": counts,
        "tracked_total": tracked_total,
        "coverage_ratio": coverage_ratio,
        "unknown_options": unknown,
    }


def _audit_switch_model_drift() -> Dict[str, Any]:
    root = Path(__file__).resolve().parents[4]
    _ensure_repo_on_path(root)
    try:
        from modules.ai_intelligence.ai_gateway.src.ai_gateway import AIGateway
        from modules.ai_intelligence.ai_gateway.src.model_registry import (
            RECOMMENDED_MODELS,
            get_current_models,
        )
        from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    except Exception as exc:
        return {
            "ok": False,
            "error": f"import_failed:{type(exc).__name__}",
            "switchable_external_models": [],
            "recommended_primary_not_switchable": [],
            "provider_quick_models_not_switchable": {},
        }

    current = get_current_models()
    external_models = {
        model_id: info
        for model_id, info in current.items()
        if info.provider in {"openai", "anthropic", "google", "xai"}
    }

    switchable = sorted(
        model_id
        for model_id in external_models
        if OpenClawDAE._resolve_external_target(model_id) is not None
    )
    unswitchable = sorted(set(external_models) - set(switchable))

    primary_tasks = ("coding", "social", "research", "analysis", "reasoning", "quick")
    recommended_primary = {}
    recommended_primary_not_switchable = []
    for task in primary_tasks:
        top = (RECOMMENDED_MODELS.get(task) or [None])[0]
        if not top:
            continue
        recommended_primary[task] = top
        if top in external_models and OpenClawDAE._resolve_external_target(top) is None:
            recommended_primary_not_switchable.append({"task": task, "model": top})

    gateway = AIGateway()
    quick_models = {
        name: cfg.models.get("quick", "")
        for name, cfg in gateway.providers.items()
    }
    quick_models_not_switchable = {
        provider: model
        for provider, model in quick_models.items()
        if model and OpenClawDAE._resolve_external_target(model) is None
    }

    return {
        "ok": True,
        "external_current_models_count": len(external_models),
        "switchable_external_models": switchable,
        "unswitchable_external_models": unswitchable,
        "recommended_primary_top_model": recommended_primary,
        "recommended_primary_not_switchable": recommended_primary_not_switchable,
        "provider_quick_model": quick_models,
        "provider_quick_models_not_switchable": quick_models_not_switchable,
    }


def _audit_ironclaw_runtime() -> Dict[str, Any]:
    root = Path(__file__).resolve().parents[4]
    _ensure_repo_on_path(root)
    try:
        from modules.communication.moltbot_bridge.src.ironclaw_gateway_client import (
            IronClawGatewayClient,
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": f"import_failed:{type(exc).__name__}",
            "healthy": False,
            "detail": "client_import_failed",
            "configured_model": "unknown",
            "visible_models": [],
            "configured_model_visible": None,
        }

    try:
        client = IronClawGatewayClient()
        healthy, detail = client.health()
        models = client.list_models()
        configured = client.config.model
        visible = configured in models if models else None
        return {
            "ok": True,
            "healthy": bool(healthy),
            "detail": detail,
            "base_url": client.config.base_url,
            "configured_model": configured,
            "visible_models": models,
            "visible_models_count": len(models),
            "configured_model_visible": visible,
            "key_isolation": bool(client.config.no_api_keys),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"probe_failed:{type(exc).__name__}",
            "healthy": False,
            "detail": "probe_failed",
            "configured_model": "unknown",
            "visible_models": [],
            "configured_model_visible": None,
        }


def _build_recommendations(report: Dict[str, Any]) -> List[str]:
    recs: List[str] = []

    coverage = report.get("cli_coverage", {})
    counts = coverage.get("counts", {})
    unmapped = int(counts.get("unmapped", 0))
    if unmapped > 0:
        recs.append(
            "Add explicit OpenClaw routes/adapters for unmapped main-menu capabilities "
            f"(currently {unmapped} top-level options)."
        )

    unknown = coverage.get("unknown_options", []) or []
    if unknown:
        recs.append(
            "Update MAIN_MENU_OPTION_HINTS for new/changed menu options: "
            + ", ".join(sorted(unknown))
        )

    switch_audit = report.get("switch_model_drift", {})
    quick_not_switchable = switch_audit.get("provider_quick_models_not_switchable", {}) or {}
    if quick_not_switchable:
        pairs = ", ".join(f"{p}:{m}" for p, m in sorted(quick_not_switchable.items()))
        recs.append(
            "Extend OpenClaw model-switch mapping to include AI Gateway quick models "
            f"({pairs}) for alignment with runtime routing."
        )

    primary_not_switchable = switch_audit.get("recommended_primary_not_switchable", []) or []
    if primary_not_switchable:
        items = ", ".join(
            f"{entry['task']}->{entry['model']}" for entry in primary_not_switchable
        )
        recs.append(
            "Add aliases for primary recommended models not currently switchable "
            f"({items})."
        )

    runtime = report.get("ironclaw_runtime", {})
    if not runtime.get("healthy", False):
        recs.append(
            "IronClaw runtime health is failing; verify gateway process, auth token, and base URL."
        )
    if runtime.get("configured_model_visible") is False:
        recs.append(
            "Configured IronClaw model is not visible in /v1/models; sync IRONCLAW_MODEL with loaded runtime models."
        )

    if not recs:
        recs.append("No critical drift detected in this audit snapshot.")
    return recs


def run_daily_audit(repo_root: Optional[Path] = None, write_files: bool = True) -> Dict[str, Any]:
    """
    Run OpenClaw/IronClaw daily audit and optionally persist report artifacts.
    """
    root = (repo_root or Path(__file__).resolve().parents[4]).resolve()
    generated_at = datetime.now(timezone.utc).isoformat()

    main_menu_path = root / "modules" / "infrastructure" / "cli" / "src" / "main_menu.py"
    openclaw_menu_path = root / "modules" / "infrastructure" / "cli" / "src" / "openclaw_menu.py"

    main_menu_options = _extract_main_menu_options(main_menu_path)
    openclaw_menu_options = _extract_openclaw_menu_options(openclaw_menu_path)

    report: Dict[str, Any] = {
        "generated_at_utc": generated_at,
        "repo_root": str(root),
        "sources": {
            "main_menu": str(main_menu_path),
            "openclaw_menu": str(openclaw_menu_path),
        },
        "main_menu_option_count": len(main_menu_options),
        "openclaw_menu_option_count": len(openclaw_menu_options),
        "cli_coverage": _audit_cli_coverage(main_menu_options),
        "main_menu_options": main_menu_options,
        "openclaw_menu_options": openclaw_menu_options,
        "switch_model_drift": _audit_switch_model_drift(),
        "ironclaw_runtime": _audit_ironclaw_runtime(),
    }
    report["recommendations"] = _build_recommendations(report)

    if write_files:
        report_dir = root / "modules" / "communication" / "moltbot_bridge" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        latest_path = report_dir / "openclaw_ironclaw_daily_audit_latest.json"
        history_path = report_dir / "openclaw_ironclaw_daily_audit_history.jsonl"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        dated_path = report_dir / f"openclaw_ironclaw_daily_audit_{stamp}.json"

        payload = json.dumps(report, indent=2, ensure_ascii=False)
        latest_path.write_text(payload + "\n", encoding="utf-8")
        dated_path.write_text(payload + "\n", encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(report, ensure_ascii=False) + "\n")

        report["artifacts"] = {
            "latest": str(latest_path),
            "dated": str(dated_path),
            "history": str(history_path),
        }
    else:
        report["artifacts"] = {}

    return report


def _print_summary(report: Dict[str, Any]) -> None:
    coverage = report.get("cli_coverage", {})
    counts = coverage.get("counts", {})
    ratio = coverage.get("coverage_ratio", 0.0)
    switch_audit = report.get("switch_model_drift", {})
    runtime = report.get("ironclaw_runtime", {})

    print("OpenClaw / IronClaw Daily Audit")
    print("--------------------------------")
    print(
        "CLI coverage: "
        f"direct={counts.get('direct', 0)} "
        f"partial={counts.get('partial', 0)} "
        f"unmapped={counts.get('unmapped', 0)} "
        f"(ratio={ratio:.2f})"
    )
    print(
        "Switchable external models: "
        f"{len(switch_audit.get('switchable_external_models', []))}"
    )
    print(
        "Quick models not switchable: "
        f"{len((switch_audit.get('provider_quick_models_not_switchable') or {}))}"
    )
    print(
        "IronClaw runtime: "
        f"healthy={runtime.get('healthy', False)} "
        f"detail={runtime.get('detail', 'unknown')}"
    )

    recs = report.get("recommendations", []) or []
    print("\nRecommendations:")
    for idx, rec in enumerate(recs, start=1):
        print(f"{idx}. {rec}")

    artifacts = report.get("artifacts", {}) or {}
    if artifacts:
        print("\nArtifacts:")
        for key in ("latest", "dated", "history"):
            value = artifacts.get(key)
            if value:
                print(f"- {key}: {value}")


if __name__ == "__main__":
    result = run_daily_audit()
    _print_summary(result)
