#!/usr/bin/env python
"""Synchronize WSP backup mirror from framework canonical sources.

Canonical source: WSP_framework/src
Backup mirror:     WSP_knowledge/src

This tool enforces the policy:
- Edit protocol files in framework only.
- Mirror those files into knowledge for backup/recovery.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List


WSP_PATTERN = "WSP_*.md"


@dataclass
class SyncReport:
    """Comparison and sync summary."""

    missing_in_knowledge: List[str] = field(default_factory=list)
    drifted_in_knowledge: List[str] = field(default_factory=list)
    extra_in_knowledge: List[str] = field(default_factory=list)
    copied_to_knowledge: List[str] = field(default_factory=list)
    updated_in_knowledge: List[str] = field(default_factory=list)
    deleted_from_knowledge: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.missing_in_knowledge or self.drifted_in_knowledge)

    def as_lines(self) -> List[str]:
        lines: List[str] = []
        if self.missing_in_knowledge:
            lines.append(f"missing_in_knowledge={len(self.missing_in_knowledge)}")
            lines.extend(f"  MISSING {name}" for name in self.missing_in_knowledge)
        if self.drifted_in_knowledge:
            lines.append(f"drifted_in_knowledge={len(self.drifted_in_knowledge)}")
            lines.extend(f"  DRIFT {name}" for name in self.drifted_in_knowledge)
        if self.extra_in_knowledge:
            lines.append(f"extra_in_knowledge={len(self.extra_in_knowledge)}")
            lines.extend(f"  EXTRA {name}" for name in self.extra_in_knowledge)
        if self.copied_to_knowledge:
            lines.append(f"copied_to_knowledge={len(self.copied_to_knowledge)}")
            lines.extend(f"  COPIED {name}" for name in self.copied_to_knowledge)
        if self.updated_in_knowledge:
            lines.append(f"updated_in_knowledge={len(self.updated_in_knowledge)}")
            lines.extend(f"  UPDATED {name}" for name in self.updated_in_knowledge)
        if self.deleted_from_knowledge:
            lines.append(f"deleted_from_knowledge={len(self.deleted_from_knowledge)}")
            lines.extend(f"  DELETED {name}" for name in self.deleted_from_knowledge)
        if not lines:
            lines.append("no_changes_detected")
        return lines


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _collect_wsp_files(directory: Path, pattern: str = WSP_PATTERN) -> Dict[str, Path]:
    if not directory.exists():
        return {}
    files = {
        path.name: path
        for path in directory.glob(pattern)
        if path.is_file()
    }
    return dict(sorted(files.items()))


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compare_framework_to_knowledge(
    framework_dir: Path,
    knowledge_dir: Path,
    pattern: str = WSP_PATTERN,
) -> SyncReport:
    """Compare canonical framework files to knowledge backup mirror."""
    report = SyncReport()

    framework_files = _collect_wsp_files(framework_dir, pattern)
    knowledge_files = _collect_wsp_files(knowledge_dir, pattern)

    for name, framework_path in framework_files.items():
        knowledge_path = knowledge_files.get(name)
        if knowledge_path is None:
            report.missing_in_knowledge.append(name)
            continue
        if _sha256(framework_path) != _sha256(knowledge_path):
            report.drifted_in_knowledge.append(name)

    framework_names = set(framework_files.keys())
    for name in knowledge_files:
        if name not in framework_names:
            report.extra_in_knowledge.append(name)

    return report


def sync_framework_to_knowledge(
    framework_dir: Path,
    knowledge_dir: Path,
    *,
    prune: bool = False,
    pattern: str = WSP_PATTERN,
) -> SyncReport:
    """Apply one-way sync from framework to knowledge."""
    report = compare_framework_to_knowledge(framework_dir, knowledge_dir, pattern=pattern)
    framework_files = _collect_wsp_files(framework_dir, pattern)
    knowledge_files = _collect_wsp_files(knowledge_dir, pattern)

    knowledge_dir.mkdir(parents=True, exist_ok=True)

    for name in report.missing_in_knowledge:
        src = framework_files[name]
        dst = knowledge_dir / name
        shutil.copy2(src, dst)
        report.copied_to_knowledge.append(name)

    for name in report.drifted_in_knowledge:
        src = framework_files[name]
        dst = knowledge_dir / name
        shutil.copy2(src, dst)
        report.updated_in_knowledge.append(name)

    if prune:
        framework_names = set(framework_files.keys())
        for name, path in knowledge_files.items():
            if name not in framework_names:
                path.unlink()
                report.deleted_from_knowledge.append(name)

    return report


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize WSP framework canonical files into WSP knowledge backup mirror.",
    )
    parser.add_argument(
        "--framework-dir",
        default=str(_repo_root() / "WSP_framework" / "src"),
        help="Canonical WSP directory (default: WSP_framework/src)",
    )
    parser.add_argument(
        "--knowledge-dir",
        default=str(_repo_root() / "WSP_knowledge" / "src"),
        help="Backup mirror directory (default: WSP_knowledge/src)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mirror drift only (non-zero exit on missing/drifted files).",
    )
    parser.add_argument(
        "--sync-to-knowledge",
        action="store_true",
        help="Apply one-way sync from framework -> knowledge.",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Delete backup files that do not exist in framework (destructive).",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    framework_dir = Path(args.framework_dir)
    knowledge_dir = Path(args.knowledge_dir)

    if not args.check and not args.sync_to_knowledge:
        args.check = True

    if args.prune and not args.sync_to_knowledge:
        print("error: --prune requires --sync-to-knowledge", file=sys.stderr)
        return 2

    if args.check:
        report = compare_framework_to_knowledge(framework_dir, knowledge_dir)
        for line in report.as_lines():
            print(line)
        if report.has_drift:
            return 1
        return 0

    report = sync_framework_to_knowledge(
        framework_dir,
        knowledge_dir,
        prune=args.prune,
    )
    for line in report.as_lines():
        print(line)
    post = compare_framework_to_knowledge(framework_dir, knowledge_dir)
    return 0 if not post.has_drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
