#!/usr/bin/env python3
"""Module usage audit to identify orphaned vibecoded modules."""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set

MODULE_ROOT = Path('modules')
ENTRY_ALLOWLIST = {
    'main.py',
}

@dataclass
class ModuleRecord:
    module: str
    path: str
    lines: int
    imports: Set[str]
    incoming: Set[str]
    has_main_guard: bool
    recommendation: str
    notes: List[str]

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['imports'] = sorted(self.imports)
        data['incoming'] = sorted(self.incoming)
        return data

class ImportCollector(ast.NodeVisitor):
    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.imports: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None and node.level == 0:
            return
        base = self._resolve_from(node)
        if base:
            self.imports.add(base)
            for alias in node.names:
                self.imports.add(f"{base}.{alias.name}")

    def _resolve_from(self, node: ast.ImportFrom) -> str | None:
        module = self.module_name
        package_parts = module.split('.')[:-1]
        if module.endswith('__init__'):
            package_parts = module.split('.')
        level = node.level
        if level:
            if level > len(package_parts):
                return None
            base_parts = package_parts[:-level]
            if node.module:
                base_parts += node.module.split('.')
            return '.'.join(base_parts)
        return node.module


def discover_modules() -> Dict[str, Path]:
    module_map: Dict[str, Path] = {}
    for path in MODULE_ROOT.rglob('*.py'):
        rel = path.relative_to(MODULE_ROOT)
        dotted = 'modules.' + '.'.join(rel.with_suffix('').parts)
        module_map[dotted] = path
    return module_map


def analyze_module(module: str, path: Path) -> ModuleRecord:
    text = path.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    collector = ImportCollector(module)
    try:
        tree = ast.parse(text)
        collector.visit(tree)
    except SyntaxError:
        tree = None
    has_main_guard = '__main__' in text
    return ModuleRecord(
        module=module,
        path=str(path),
        lines=len(lines),
        imports={imp for imp in collector.imports if imp},
        incoming=set(),
        has_main_guard=has_main_guard,
        recommendation='unknown',
        notes=[],
    )


def build_graph(records: Dict[str, ModuleRecord]) -> None:
    modules = set(records.keys())
    for record in records.values():
        for imp in record.imports:
            if imp in records:
                records[imp].incoming.add(record.module)


def classify(record: ModuleRecord) -> None:
    if record.has_main_guard or record.module.endswith('__init__'):
        record.recommendation = 'keep'
        record.notes.append('Entry point or package initialiser.')
        return
    incoming = len(record.incoming)
    if incoming == 0:
        record.recommendation = 'archive'
        record.notes.append('No inbound references detected.')
    elif incoming == 1:
        record.recommendation = 'review'
        record.notes.append('Single inbound reference; verify necessity.')
    else:
        record.recommendation = 'keep'
        record.notes.append(f'{incoming} inbound references.')


def main() -> None:
    module_map = discover_modules()
    records = {name: analyze_module(name, path) for name, path in module_map.items()}
    build_graph(records)

    for record in records.values():
        classify(record)

    out_dir = Path('tools/audits')
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / 'module_usage_audit.json'
    md_path = out_dir / 'module_usage_audit.md'

    json_path.write_text(json.dumps({k: v.to_dict() for k, v in records.items()}, indent=2), encoding='utf-8')

    with md_path.open('w', encoding='utf-8') as md:
        md.write('# Module Usage Audit\n\n')
        md.write('| Module | Recommendation | Lines | Incoming | Notes |\n')
        md.write('|---|---|---|---|---|\n')
        for record in sorted(records.values(), key=lambda r: (r.recommendation, r.module)):
            notes = '<br>'.join(record.notes) if record.notes else '—'
            md.write(
                f"| {record.module} | {record.recommendation} | {record.lines} | {len(record.incoming)} | {notes} |\n"
            )

    print(f"Module usage audit written to {json_path} and {md_path}")

if __name__ == '__main__':
    main()
