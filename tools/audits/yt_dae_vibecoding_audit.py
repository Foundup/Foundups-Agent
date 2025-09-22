#!/usr/bin/env python3
"""YT DAE Vibecoding Audit Tool (Phase 0)."""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

BASE = Path('modules/communication/livechat/src')
TARGET_MODULES = [
    'auto_moderator_dae.py',
    'livechat_core.py',
    'message_processor.py',
    'chat_poller.py',
    'chat_sender.py',
    'session_manager.py',
    'command_handler.py',
    'event_handler.py',
    'consciousness_handler.py',
    'agentic_chat_engine.py',
    'chat_memory_manager.py',
    'greeting_generator.py',
    'llm_bypass_engine.py',
    'llm_integration.py',
    'moderation_stats.py',
    'quota_aware_poller.py',
    'simple_fact_checker.py',
    'stream_trigger.py',
    'intelligent_throttle_manager.py',
    'mcp_youtube_integration.py',
]

WSP_HINTS = {
    'WSP 87-small': 'Module under 500 lines; WSP 87 prefers larger cohesive files.',
    'WSP 87-large': 'Module above 1,200 lines; consider splitting before hitting 1,500 hard limit.',
    'WSP 84': 'Avoid duplicate/enhanced module definitions; evolve existing code.',
    'WSP 50': 'TODO/bare pass indicates unfinished work; log pre-action plan.',
}

MIN_LINES = 500
LARGE_LINES = 1200
HARD_LIMIT = 1500

@dataclass
class ModuleAudit:
    module: str
    path: str
    lines: int
    nav_present: bool
    docstring_present: bool
    todo_count: int
    class_enhanced: bool
    warnings: List[str]
    recommendation: str
    mtime: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['warnings'] = list(self.warnings)
        return data

def analyse_module(file_path: Path) -> ModuleAudit:
    text = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    line_count = len(lines)

    nav_present = 'NAVIGATION:' in text
    try:
        docstring_present = bool(ast.get_docstring(ast.parse(text)))
    except SyntaxError:
        docstring_present = False

    todo_count = text.count('TODO') + text.count('FIXME')
    class_enhanced = 'Enhanced' in text or 'enhanced_' in text

    warnings: List[str] = []

    if line_count < MIN_LINES:
        warnings.append('WSP 87-small')
    if line_count > LARGE_LINES:
        warnings.append('WSP 87-large')
    if line_count > HARD_LIMIT:
        warnings.append('WSP 87-large (exceeds hard limit)')
    if class_enhanced:
        warnings.append('WSP 84')
    if todo_count:
        warnings.append('WSP 50')

    recommendation = 'retain'
    if line_count > HARD_LIMIT or 'WSP 84' in warnings:
        recommendation = 'refactor'
    elif 'WSP 87-small' in warnings or 'WSP 87-large' in warnings or 'WSP 50' in warnings:
        recommendation = 'enhance'

    mtime = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

    expanded_warnings: List[str] = []
    for warn in warnings:
        hint = WSP_HINTS.get(warn)
        if hint:
            expanded_warnings.append(hint)
        else:
            expanded_warnings.append(warn)

    return ModuleAudit(
        module=file_path.name,
        path=str(file_path),
        lines=line_count,
        nav_present=nav_present,
        docstring_present=docstring_present,
        todo_count=todo_count,
        class_enhanced=class_enhanced,
        warnings=expanded_warnings,
        recommendation=recommendation,
        mtime=mtime,
    )

def run_audit() -> Dict[str, ModuleAudit]:
    report: Dict[str, ModuleAudit] = {}
    for module in TARGET_MODULES:
        fp = BASE / module
        if not fp.exists():
            continue
        report[module] = analyse_module(fp)
    return report

def render_markdown(report: Dict[str, ModuleAudit], path: Path) -> None:
    with path.open('w', encoding='utf-8') as md:
        md.write('# YT DAE Vibecoding Audit\n\n')
        md.write('| Module | Lines | NAV | Docstring | TODOs | Recommendation | Notes |\n')
        md.write('|---|---|---|---|---|---|---|\n')
        for audit in report.values():
            notes = '<br>'.join(audit.warnings) if audit.warnings else '—'
            md.write(
                f"| {audit.module} | {audit.lines} | {'Yes' if audit.nav_present else 'No'} | "
                f"{'Yes' if audit.docstring_present else 'No'} | {audit.todo_count} | {audit.recommendation} | {notes} |\n"
            )

def main() -> None:
    report = run_audit()
    if not report:
        print('No modules analysed.')
        return

    out_dir = Path('tools/audits')
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / 'yt_dae_audit.json'
    md_path = out_dir / 'yt_dae_audit.md'

    json_path.write_text(json.dumps({k: v.to_dict() for k, v in report.items()}, indent=2), encoding='utf-8')
    render_markdown(report, md_path)

    print(f"Audit written to {json_path} and {md_path}")

if __name__ == '__main__':
    main()
