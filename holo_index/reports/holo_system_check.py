# -*- coding: utf-8 -*-
"""Holo System Check - lightweight wiring audit for CLI subroutines."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import glob


IN_DEV_FLAGS = {
    "--mcp-log": "Placeholder until MCP log backend is wired.",
}

DEFAULT_MENU_CHECKS: List[Dict[str, str]] = [
    {"flag": "--index-all", "arg": "index_all", "label": "Manual Index Refresh"},
    {"flag": "--start-holodae", "arg": "start_holodae", "label": "Launch HoloDAE"},
    {"flag": "--search", "arg": "search", "label": "Semantic Search"},
    {"flag": "--check-module", "arg": "check_module", "label": "WSP Compliance Check"},
    {"flag": "--pattern-coach", "arg": "pattern_coach", "label": "Pattern Coach"},
    {"flag": "--module-analysis", "arg": "module_analysis", "label": "Module Analysis"},
    {"flag": "--health-check", "arg": "health_check", "label": "Health Analysis"},
    {"flag": "--wsp88", "arg": "wsp88", "label": "Orphan Analysis"},
    {"flag": "--performance-metrics", "arg": "performance_metrics", "label": "Performance Metrics"},
    {"flag": "--llm-advisor", "arg": "llm_advisor", "label": "LLM Advisor"},
    {"flag": "--stop-holodae", "arg": "stop_holodae", "label": "Stop Monitoring"},
    {"flag": "--holodae-status", "arg": "holodae_status", "label": "HoloDAE Status"},
    {"flag": "--thought-log", "arg": "thought_log", "label": "Chain-of-Thought Log"},
    {"flag": "--slow-mode", "arg": "slow_mode", "label": "Slow Mode"},
    {"flag": "--pattern-memory", "arg": "pattern_memory", "label": "Pattern Memory"},
    {"flag": "--memory-feedback", "arg": "memory_feedback", "label": "Memory Feedback"},
    {"flag": "--mcp-hooks", "arg": "mcp_hooks", "label": "MCP Hook Map"},
    {"flag": "--mcp-log", "arg": "mcp_log", "label": "MCP Action Log"},
    {"flag": "--monitor-work", "arg": "monitor_work", "label": "Work Publisher"},
    {"flag": "--system-check", "arg": "system_check", "label": "System Check"},
]


def run_system_check(
    repo_root: Path,
    checks: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    repo_root = Path(repo_root)
    cli_path = repo_root / "holo_index" / "cli.py"
    cli_text = ""
    if cli_path.exists():
        cli_text = cli_path.read_text(encoding="utf-8", errors="ignore")

    results = []
    for check in checks or DEFAULT_MENU_CHECKS:
        flag = check.get("flag", "")
        arg = check.get("arg", "")
        label = check.get("label", "")
        note = check.get("note", "")

        flag_found = _has_flag(cli_text, flag)
        handler_found = _has_handler(cli_text, arg) if arg else False

        status = "ok"
        if not flag_found:
            status = "missing"
        elif arg and not handler_found:
            status = "unwired"
        elif flag in IN_DEV_FLAGS:
            status = "in_dev"
            if not note:
                note = IN_DEV_FLAGS[flag]

        results.append({
            "flag": flag,
            "label": label,
            "status": status,
            "flag_found": flag_found,
            "handler_found": handler_found,
            "note": note,
        })

    summary = _summarize(results)
    skillz_inventory = _collect_skillz_inventory(repo_root)
    wsp_framework_health = _collect_wsp_framework_health(repo_root)
    m2m_compression_health = _collect_m2m_compression_health(repo_root)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "wiring",
        "cli_path": str(cli_path),
        "summary": summary,
        "skillz_inventory": skillz_inventory,
        "wsp_framework_health": wsp_framework_health,
        "m2m_compression_health": m2m_compression_health,
        "checks": results,
    }


def write_system_check_report(report: Dict[str, Any], output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _stamp(report.get("timestamp"))
    out_path = output_dir / f"Holo_System_Check_{timestamp}.md"

    summary = report.get("summary") or {}
    ok = summary.get("ok", 0)
    in_dev = summary.get("in_dev", 0)
    missing = summary.get("missing", 0)
    unwired = summary.get("unwired", 0)
    skillz_inventory = report.get("skillz_inventory") or {}
    skillz_total = skillz_inventory.get("total", 0)
    skillz_breakdown = skillz_inventory.get("by_root") or {}
    skillz_samples = skillz_inventory.get("samples") or []
    wsp_framework_health = report.get("wsp_framework_health") or {}

    lines = [
        "# Holo System Check Report",
        "",
        f"Date: {report.get('timestamp', '')}",
        f"Mode: {report.get('mode', 'wiring')}",
        "",
        f"Summary: ok {ok}, in_dev {in_dev}, missing {missing}, unwired {unwired}",
        f"Skillz Inventory: total {skillz_total}",
        "",
        "| Flag | Status | Parser | Handler | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]

    for check in report.get("checks", []):
        flag = check.get("flag", "")
        status = check.get("status", "")
        parser = "yes" if check.get("flag_found") else "no"
        handler = "yes" if check.get("handler_found") else "no"
        note = check.get("note", "")
        lines.append(f"| `{flag}` | {status} | {parser} | {handler} | {note} |")

    if wsp_framework_health:
        lines.extend([
            "",
            "## WSP Framework Health",
            "",
            f"- Available: {wsp_framework_health.get('available', False)}",
            f"- Severity: {wsp_framework_health.get('severity', 'unknown')}",
            f"- Message: {wsp_framework_health.get('message', 'n/a')}",
            f"- Drift Count: {wsp_framework_health.get('drift_count', 0)}",
            f"- Framework Count: {wsp_framework_health.get('framework_count', 0)}",
            f"- Knowledge Count: {wsp_framework_health.get('knowledge_count', 0)}",
        ])

        report_path = wsp_framework_health.get("report_path")
        if report_path:
            lines.append(f"- Sentinel Report: `{report_path}`")

    if skillz_breakdown:
        lines.extend([
            "",
            "## Skillz Breakdown",
            "",
        ])
        for root_key, count in sorted(skillz_breakdown.items()):
            lines.append(f"- {root_key}: {count}")

    if skillz_samples:
        lines.extend([
            "",
            "## Skillz Sample Paths",
            "",
        ])
        for path in skillz_samples:
            lines.append(f"- `{path}`")

    # M2M Compression Health (WSP 99)
    m2m_health = report.get("m2m_compression_health") or {}
    if m2m_health.get("available"):
        lines.extend([
            "",
            "## M2M Compression Opportunities (WSP 99)",
            "",
            f"- Severity: {m2m_health.get('severity', 'unknown')}",
            f"- Message: {m2m_health.get('message', 'n/a')}",
            f"- Files Scanned: {m2m_health.get('files_scanned', 0)}",
            f"- Candidates Found: {m2m_health.get('candidates_found', 0)}",
            f"- Auto-Apply Ready: {m2m_health.get('auto_apply_count', 0)}",
            f"- Stage + Promote: {m2m_health.get('stage_promote_count', 0)}",
            f"- Stage + Review: {m2m_health.get('stage_review_count', 0)}",
            f"- Flag Only: {m2m_health.get('flag_only_count', 0)}",
            f"- Est. Savings: {m2m_health.get('total_estimated_savings_percent', 0):.1f}%",
        ])

        m2m_report = m2m_health.get("report_path")
        if m2m_report:
            lines.append(f"- Full Report: `{m2m_report}`")

        top_candidates = m2m_health.get("top_candidates") or []
        if top_candidates:
            lines.extend([
                "",
                "### Top Compression Candidates",
                "",
                "| File | Lines | Reduction | Confidence | Action |",
                "| --- | --- | --- | --- | --- |",
            ])
            for candidate in top_candidates:
                filename = candidate.get("filename", "?")
                line_count = candidate.get("line_count", 0)
                reduction = candidate.get("estimated_reduction", 0)
                confidence = candidate.get("confidence", 0)
                action = candidate.get("action", "?")
                lines.append(f"| `{filename}` | {line_count} | {reduction:.0f}% | {confidence:.2f} | {action} |")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def _has_flag(cli_text: str, flag: str) -> bool:
    if not cli_text or not flag:
        return False
    return flag in cli_text


def _has_handler(cli_text: str, arg: str) -> bool:
    if not cli_text or not arg:
        return False
    if f"args.{arg}" in cli_text:
        return True
    if f"getattr(args, '{arg}'" in cli_text:
        return True
    if f'getattr(args, "{arg}"' in cli_text:
        return True
    return False


def _summarize(results: List[Dict[str, Any]]) -> Dict[str, int]:
    summary = {"ok": 0, "in_dev": 0, "missing": 0, "unwired": 0}
    for result in results:
        status = result.get("status", "ok")
        if status not in summary:
            summary[status] = 0
        summary[status] += 1
    return summary


def _collect_skillz_inventory(repo_root: Path) -> Dict[str, Any]:
    roots = {
        "holo_index": repo_root / "holo_index" / "skillz",
        "modules": repo_root / "modules",
        ".claude": repo_root / ".claude",
    }
    patterns = [
        repo_root / "holo_index" / "skillz" / "*" / "SKILLz.md",
        repo_root / "modules" / "**" / "skills" / "*" / "SKILLz.md",
        repo_root / "modules" / "**" / "skillz" / "*" / "SKILLz.md",
        repo_root / ".claude" / "skills" / "*" / "SKILLz.md",
        repo_root / ".claude" / "skillz" / "*" / "SKILLz.md",
    ]

    files: List[Path] = []
    for pattern in patterns:
        matches = glob.glob(str(pattern), recursive=True)
        files.extend(Path(match) for match in matches)

    unique_files = []
    seen = set()
    for path in files:
        resolved = str(path)
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_files.append(path)

    by_root: Dict[str, int] = {"holo_index": 0, "modules": 0, ".claude": 0}
    for path in unique_files:
        key = "modules"
        if roots["holo_index"] in path.parents:
            key = "holo_index"
        elif roots[".claude"] in path.parents:
            key = ".claude"
        by_root[key] = by_root.get(key, 0) + 1

    samples = []
    for path in unique_files[:5]:
        try:
            samples.append(str(path.relative_to(repo_root)).replace("\\", "/"))
        except ValueError:
            samples.append(str(path).replace("\\", "/"))

    return {
        "total": len(unique_files),
        "by_root": by_root,
        "samples": samples,
    }


def _collect_wsp_framework_health(repo_root: Path) -> Dict[str, Any]:
    """Collect WSP framework-vs-knowledge drift status via AI Overseer sentinel."""
    try:
        from modules.ai_intelligence.ai_overseer.src.wsp_framework_sentinel import WSPFrameworkSentinel
    except Exception as exc:
        return {
            "available": False,
            "severity": "unknown",
            "message": f"wsp framework sentinel import failed: {exc}",
            "drift_count": 0,
            "framework_count": 0,
            "knowledge_count": 0,
            "report_path": None,
        }

    try:
        sentinel = WSPFrameworkSentinel(Path(repo_root))
        status = sentinel.check(force=False)
        return {
            "available": bool(status.get("available", False)),
            "severity": status.get("severity", "unknown"),
            "message": status.get("message", ""),
            "drift_count": int(status.get("drift_count", 0)),
            "framework_count": int(status.get("framework_count", 0)),
            "knowledge_count": int(status.get("knowledge_count", 0)),
            "report_path": status.get("report_path"),
        }
    except Exception as exc:
        return {
            "available": False,
            "severity": "critical",
            "message": f"wsp framework sentinel execution failed: {exc}",
            "drift_count": 0,
            "framework_count": 0,
            "knowledge_count": 0,
            "report_path": None,
        }


def _collect_m2m_compression_health(repo_root: Path) -> Dict[str, Any]:
    """Collect M2M compression opportunities via AI Overseer sentinel (WSP 99).

    Uses batched scanning with confidence-based scaled response:
    - Gemma: Pattern detection (prose density, politeness markers)
    - Qwen: Actual M2M compilation (if approved)
    - 0102: Oversight for low-confidence/critical files

    Returns compressed status for health report integration.
    """
    try:
        from modules.ai_intelligence.ai_overseer.src.m2m_compression_sentinel import M2MCompressionSentinel
    except Exception as exc:
        return {
            "available": False,
            "severity": "unknown",
            "message": f"m2m compression sentinel import failed: {exc}",
            "files_scanned": 0,
            "candidates_found": 0,
            "auto_apply_count": 0,
            "stage_review_count": 0,
            "total_estimated_savings_percent": 0.0,
            "report_path": None,
        }

    try:
        sentinel = M2MCompressionSentinel(Path(repo_root))
        status = sentinel.check(force=False)
        return {
            "available": bool(status.get("available", False)),
            "severity": status.get("severity", "info"),
            "message": status.get("message", ""),
            "files_scanned": int(status.get("files_scanned", 0)),
            "candidates_found": int(status.get("candidates_found", 0)),
            "auto_apply_count": int(status.get("auto_apply_count", 0)),
            "stage_promote_count": int(status.get("stage_promote_count", 0)),
            "stage_review_count": int(status.get("stage_review_count", 0)),
            "flag_only_count": int(status.get("flag_only_count", 0)),
            "total_estimated_savings_percent": float(status.get("total_estimated_savings_percent", 0.0)),
            "top_candidates": status.get("candidates", [])[:5],  # Top 5 for summary
            "report_path": status.get("report_path"),
        }
    except Exception as exc:
        return {
            "available": False,
            "severity": "unknown",
            "message": f"m2m compression sentinel execution failed: {exc}",
            "files_scanned": 0,
            "candidates_found": 0,
            "auto_apply_count": 0,
            "stage_review_count": 0,
            "total_estimated_savings_percent": 0.0,
            "report_path": None,
        }


def _stamp(raw: Optional[str]) -> str:
    if not raw:
        return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    cleaned = raw.replace(":", "").replace("-", "")
    cleaned = cleaned.replace("T", "-").split(".")[0]
    return cleaned
