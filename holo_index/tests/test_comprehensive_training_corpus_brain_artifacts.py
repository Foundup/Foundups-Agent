import json
from pathlib import Path

from holo_index.training.comprehensive_training_corpus import ComprehensiveTrainingCorpus


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_collect_all_includes_brain_artifact_training_rows(tmp_path: Path):
    root = tmp_path / "repo"
    _write(root / "WSP_knowledge" / "src" / "WSP_MODULE_VIOLATIONS.md", "## Sample violation")

    brain_dir = tmp_path / "brain"
    conv = brain_dir / "conv-001"
    _write(conv / "task.md", "# Task\nStabilize the OpenClaw startup path.")
    _write(conv / "implementation_plan.md.resolved.0", "First draft plan.")
    _write(conv / "implementation_plan.md.resolved.1", "Final plan after review.")
    _write(conv / "walkthrough.md", "Verified walkthrough with concrete steps and validation output.")

    collector = ComprehensiveTrainingCorpus(root_dir=str(root), brain_dir=str(brain_dir))
    corpus = collector.collect_all()

    assert len(corpus["brain_artifact_dpo_pairs"]) == 1
    assert len(corpus["brain_artifact_sft"]) == 1
    assert collector.get_summary()["breakdown"]["brain_artifact_dpo_pairs"] == 1


def test_export_brain_training_jsonl_writes_expected_files(tmp_path: Path):
    collector = ComprehensiveTrainingCorpus(root_dir=str(tmp_path), brain_dir=str(tmp_path / "brain"))
    collector.corpus["brain_artifact_dpo_pairs"] = [
        {"prompt": "Task", "chosen": "Final", "rejected": "Draft", "source": "conv-001"}
    ]
    collector.corpus["brain_artifact_sft"] = [
        {"system": "You are 0102.", "user": "Task", "assistant": "Walkthrough", "source": "conv-001"}
    ]

    paths = collector.export_brain_training_jsonl(str(tmp_path / "training_data"))

    dpo_row = json.loads(paths["dpo_pairs"].read_text(encoding="utf-8").strip())
    sft_row = json.loads(paths["sft_examples"].read_text(encoding="utf-8").strip())

    assert dpo_row["chosen"] == "Final"
    assert sft_row["assistant"] == "Walkthrough"
