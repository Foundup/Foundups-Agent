import os
from pathlib import Path


TEMPLATE = """# Module Memory Architecture (WSP 60)

Purpose
- Persist module-specific memory artifacts for 0102 operations (not 012 narratives).
- Maintain minimal, navigational documentation only. No temporal references.

Structure
- This directory is reserved for module memory artifacts required at runtime or for compliance.
- Do not store logs here unless explicitly required by WSP 60.

Notes
- Keep this README present to satisfy WSP 60 documentation requirements.
"""


def ensure_memory_readme(repo_root: Path) -> int:
    modules_dir = repo_root / "modules"
    if not modules_dir.exists():
        return 0

    created = 0
    for domain_dir in modules_dir.iterdir():
        if not domain_dir.is_dir():
            continue
        for module_dir in domain_dir.iterdir():
            if not module_dir.is_dir():
                continue
            mem_dir = module_dir / "memory"
            mem_readme = mem_dir / "README.md"
            try:
                if not mem_dir.exists():
                    mem_dir.mkdir(parents=True, exist_ok=True)
                if not mem_readme.exists():
                    mem_readme.write_text(TEMPLATE, encoding="utf-8")
                    created += 1
            except Exception:
                # Skip modules we cannot modify (permissions or transient issues)
                continue
    return created


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    count = ensure_memory_readme(root)
    print(f"WSP 60: created memory/README.md in {count} module(s)")


