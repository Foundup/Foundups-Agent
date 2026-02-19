#!/usr/bin/env python3
"""Contract tests for HoloIndex machine-language governance."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_JSON = REPO_ROOT / "holo_index" / "docs" / "HOLO_INDEX_MACHINE_LANGUAGE_SPEC_0102.json"
INTERFACE_MD = REPO_ROOT / "holo_index" / "INTERFACE.md"
CLI_REFERENCE_MD = REPO_ROOT / "holo_index" / "CLI_REFERENCE.md"


def test_machine_spec_json_is_valid_and_authoritative() -> None:
    assert SPEC_JSON.exists(), f"missing spec file: {SPEC_JSON}"
    payload = json.loads(SPEC_JSON.read_text(encoding="utf-8"))

    assert payload.get("spec_id") == "holo_index.machine_language.v1"
    assert payload.get("source_of_truth_policy"), "missing source_of_truth_policy section"

    policy = payload["source_of_truth_policy"]
    assert policy.get("authoritative_machine_contract") == "holo_index/docs/HOLO_INDEX_MACHINE_LANGUAGE_SPEC_0102.json"
    assert policy.get("human_interface_contract") == "holo_index/INTERFACE.md"
    assert policy.get("operator_menu_atlas_non_normative") == "holo_index/CLI_REFERENCE.md"


def test_interface_declares_source_of_truth_policy() -> None:
    assert INTERFACE_MD.exists(), f"missing interface file: {INTERFACE_MD}"
    text = INTERFACE_MD.read_text(encoding="utf-8")

    assert "Source-of-truth policy:" in text
    assert "Authoritative machine contract" in text
    assert "non-normative" in text


def test_cli_reference_declares_non_normative_status() -> None:
    assert CLI_REFERENCE_MD.exists(), f"missing cli reference: {CLI_REFERENCE_MD}"
    text = CLI_REFERENCE_MD.read_text(encoding="utf-8")

    assert "not an exhaustive CLI flag list" in text
    assert "Canonical machine schema lives in `holo_index/docs/HOLO_INDEX_MACHINE_LANGUAGE_SPEC_0102.json`." in text

