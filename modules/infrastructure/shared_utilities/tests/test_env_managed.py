from pathlib import Path
from unittest.mock import patch

from modules.infrastructure.shared_utilities.env_managed import (
    build_managed_env,
    load_managed_env,
)


def test_build_managed_env_resolves_duplicates_and_keeps_orphans(tmp_path: Path):
    src = tmp_path / ".env"
    dst = tmp_path / ".env.managed"
    src.write_text(
        "\n".join(
            [
                "# test env",
                "A=1",
                "B=2",
                "A=3",
                "BAD LINE WITHOUT EQUALS",
                "export C=4",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    stats = build_managed_env(src, dst)
    content = dst.read_text(encoding="utf-8")

    assert stats["total_keys"] == 3
    assert stats["duplicate_keys"] == 1
    assert stats["duplicate_overwrites"] == 1
    assert stats["orphan_lines"] == 1
    assert "A=3" in content
    assert "B=2" in content
    assert "C=4" in content
    assert "# ORPHAN" in content


def test_load_managed_env_in_memory_purges_stale_copy(tmp_path: Path):
    src = tmp_path / ".env"
    stale = tmp_path / ".env.managed"
    src.write_text("A=1\nA=2\nB=3\n", encoding="utf-8")
    stale.write_text("STALE=1\n", encoding="utf-8")

    with patch.dict(
        "os.environ",
        {
            "FOUNDUPS_ENV_MANAGED_DISK_COPY": "0",
            "FOUNDUPS_ENV_MANAGED_PURGE_COPY": "1",
        },
        clear=False,
    ):
        stats = load_managed_env(tmp_path, override=False, regenerate=True)

    assert stats["mode"] == "in_memory"
    assert stats["duplicate_keys"] == 1
    assert stats["duplicate_overwrites"] == 1
    assert stats["managed_copy_written"] is False
    assert stats["managed_copy_deleted"] is True
    assert stale.exists() is False
