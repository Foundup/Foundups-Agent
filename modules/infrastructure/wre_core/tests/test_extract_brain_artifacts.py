import json
from pathlib import Path

from modules.infrastructure.wre_core.scripts.extract_brain_artifacts import (
    build_training_examples,
    refresh_artifacts_if_needed,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_training_examples_extracts_dpo_and_sft(tmp_path: Path):
    conv = tmp_path / "conv-001"
    _write(conv / "task.md", "# Task\nImplement startup brain memory indexing.")
    _write(conv / "implementation_plan.md.resolved.0", "Draft plan with missing validation.")
    _write(conv / "implementation_plan.md.resolved.1", "Final approved plan with validation and rollback.")
    _write(conv / "walkthrough.md", "Verified walkthrough with executed steps and validation results.")

    result = build_training_examples(tmp_path)

    assert result["summary"]["dpo_pairs"] == 1
    assert result["summary"]["sft_examples"] == 1
    assert result["dpo_pairs"][0]["prompt"].startswith("# Task")
    assert result["dpo_pairs"][0]["rejected"] == "Draft plan with missing validation."
    assert result["dpo_pairs"][0]["chosen"] == "Final approved plan with validation and rollback."
    assert result["sft_examples"][0]["assistant"] == "Verified walkthrough with executed steps and validation results."


def test_refresh_artifacts_if_needed_skips_when_signature_is_unchanged(tmp_path: Path):
    brain_dir = tmp_path / "brain"
    conv = brain_dir / "conv-001"
    _write(conv / "task.md", "# Task\nImplement startup brain memory indexing.")
    _write(conv / "implementation_plan.md.resolved.0", "Draft plan.")
    _write(conv / "implementation_plan.md.resolved.1", "Final plan.")
    _write(conv / "walkthrough.md", "Verified walkthrough with enough detail to persist.")

    output_dir = tmp_path / "out"
    first = refresh_artifacts_if_needed(brain_dir=brain_dir, output_dir=output_dir)
    second = refresh_artifacts_if_needed(brain_dir=brain_dir, output_dir=output_dir)

    assert first["ran"] is True
    assert second["ran"] is False

    state = json.loads((output_dir / "brain_artifact_state.json").read_text(encoding="utf-8"))
    assert state["signature"]["conversation_count"] == 1
