import json
from pathlib import Path

import pytest

from holo_index.exporters.graphrag_exporter import GraphRAGExporter


class DummyHoloIndex:
    """Minimal stand-in that mimics the search signature."""

    def __init__(self, files):
        self.files = files

    def search(self, query, limit=10, doc_type_filter="all"):
        hits = []
        for path, metadata in self.files.items():
            if query.lower() in metadata.get("query_match", "").lower():
                hits.append(
                    {
                        "need": metadata.get("title"),
                        "path": str(path),
                        "type": metadata.get("type", "code"),
                    }
                )
        return {"code": hits, "wsps": []}


@pytest.fixture()
def sample_files(tmp_path):
    file_a = tmp_path / "module_a.md"
    file_a.write_text("# Module A\nSome documentation.", encoding="utf-8")
    file_b = tmp_path / "module_b.py"
    file_b.write_text("def foo():\n    return 42\n", encoding="utf-8")
    return {
        file_a: {"title": "Module A Doc", "query_match": "module architecture", "type": "documentation"},
        file_b: {"title": "Module B Code", "query_match": "semantic search", "type": "code"},
    }


def test_exporter_writes_documents(tmp_path, sample_files):
    holo = DummyHoloIndex(sample_files)
    exporter = GraphRAGExporter(holo)

    output_dir = tmp_path / "bundle"
    exporter.export(output_dir, limit=5)

    input_dir = output_dir / "input"
    assert input_dir.exists()

    docs = sorted(input_dir.glob("doc_*.txt"))
    assert len(docs) == 2  # both documents exported

    metadata = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
    assert len(metadata) == 2
    titles = {item["title"] for item in metadata}
    assert "Module A Doc" in titles
    assert "Module B Code" in titles


def test_exporter_skips_unsupported_suffix(tmp_path, sample_files):
    # add unsupported file type
    unsupported = tmp_path / "diagram.png"
    unsupported.write_bytes(b"\x89PNG\r\n")
    sample_files[unsupported] = {"title": "PNG", "query_match": "module architecture", "type": "asset"}

    holo = DummyHoloIndex(sample_files)
    exporter = GraphRAGExporter(holo)
    output_dir = tmp_path / "bundle2"
    exporter.export(output_dir, limit=5)

    docs = sorted((output_dir / "input").glob("doc_*.txt"))
    assert len(docs) == 2  # PNG skipped
