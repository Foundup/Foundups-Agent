import subprocess
from pathlib import Path
from typing import Iterable


DB_PATTERNS: Iterable[str] = (
    "data/foundups.db*",
    "*.db",
    "*.db-shm",
    "*.db-wal",
)


def _ensure_gitignore_patterns(logger) -> None:
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        return
    content = gitignore.read_text(encoding="utf-8", errors="ignore").splitlines()
    existing = set(line.strip() for line in content if line.strip())
    changed = False
    for pattern in DB_PATTERNS:
        if pattern not in existing:
            content.append(pattern)
            changed = True
    if changed:
        gitignore.write_text("\n".join(content) + "\n", encoding="utf-8")
        logger.info("[DB-GUARD] Updated .gitignore with DB patterns")


def _untrack_db_artifacts(logger) -> None:
    for pattern in DB_PATTERNS:
        try:
            subprocess.run(
                ["git", "rm", "--cached", "--ignore-unmatch", pattern],
                capture_output=True,
            )
        except Exception as exc:
            logger.debug(f"[DB-GUARD] Untrack failed for {pattern}: {exc}")


def apply_db_guard(logger) -> bool:
    """
    Ensure DB artifacts are ignored and untracked.
    Returns True when guard completed (even if no changes were needed).
    """
    try:
        _ensure_gitignore_patterns(logger)
        _untrack_db_artifacts(logger)
        return True
    except Exception as exc:
        logger.warning(f"[DB-GUARD] Guard failed: {exc}")
        return False
