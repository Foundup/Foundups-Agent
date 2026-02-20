import os
import tempfile
from pathlib import Path

from modules.ai_intelligence.video_indexer.src import studio_ask_indexer
from modules.ai_intelligence.video_indexer.src.studio_ask_indexer import StudioAskIndexer


def test_index_exists_and_counts():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "undaodu").mkdir(parents=True, exist_ok=True)
        (root / "undaodu" / "vid1.json").write_text("{}", encoding="utf-8")
        (root / "move2japan").mkdir(parents=True, exist_ok=True)

        assert StudioAskIndexer._index_exists(root, "undaodu", "vid1") is True
        assert StudioAskIndexer._index_exists(root, "undaodu", "missing") is False

        counts = studio_ask_indexer._count_indexed_by_channel(root)
        assert counts.get("undaodu") == 1
        assert counts.get("move2japan") == 0


def test_force_reindex_env():
    os.environ["VIDEO_INDEXER_FORCE_REINDEX"] = "true"
    try:
        assert studio_ask_indexer._consume_reindex_signal() is True
    finally:
        os.environ.pop("VIDEO_INDEXER_FORCE_REINDEX", None)
