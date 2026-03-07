"""Executable entry point for `python -m modules.infrastructure.cli`."""

from __future__ import annotations


def main() -> int:
    """Delegate to the repository's canonical CLI router."""
    from main import main as root_main

    root_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
