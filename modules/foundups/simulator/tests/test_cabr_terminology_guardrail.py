"""CABR terminology guardrail tests.

Prevents definition drift across core WSP + simulator/FAM documents.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]

CORE_CABR_FILES = [
    "WSP_framework/src/WSP_29_CABR_Engine.md",
    "WSP_knowledge/src/WSP_29_CABR_Engine.md",
    "modules/foundups/simulator/README.md",
    "modules/foundups/simulator/INTERFACE.md",
    "modules/foundups/agent_market/README.md",
    "modules/foundups/agent_market/INTERFACE.md",
    "modules/foundups/simulator/ai/cabr_estimator.py",
    "modules/foundups/simulator/mesa_model.py",
    "modules/foundups/agent_market/src/cabr_hooks.py",
    "modules/communication/moltbot_bridge/src/fam_adapter.py",
    "modules/infrastructure/foundups_tokenization/README.md",
    "modules/infrastructure/foundups_tokenization/docs/CABR_INTEGRATION.md",
    "modules/infrastructure/wre_core/README.md",
]

CANONICAL_TERMS = (
    "Consensus-Driven Autonomous Benefit Rate",
    "Collective Autonomous Benefit Rate",
)

DEPRECATED_TERMS = (
    "Compounded Annual Benefit Rate",
    "Conscious Autonomous Benefit Rate",
    "Conscious AI-Based Rating",
    "Consensus-driven Autonomous Beneficial Reporting",
)


def _read_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_core_cabr_files_use_canonical_terms() -> None:
    for rel_path in CORE_CABR_FILES:
        text = _read_text(rel_path)
        assert any(term in text for term in CANONICAL_TERMS), rel_path


def test_core_cabr_files_reject_deprecated_terms() -> None:
    for rel_path in CORE_CABR_FILES:
        text = _read_text(rel_path)
        for term in DEPRECATED_TERMS:
            assert term not in text, f"{rel_path} contains deprecated term: {term}"


def test_wsp29_states_cabr_intent_triplet() -> None:
    for rel_path in (
        "WSP_framework/src/WSP_29_CABR_Engine.md",
        "WSP_knowledge/src/WSP_29_CABR_Engine.md",
    ):
        text = _read_text(rel_path)
        assert "WHY: CABR exists to power Proof of Benefit (PoB)." in text
        assert "HOW: Collective 0102 consensus determines CABR (consensus-driven process)." in text
        assert (
            "RESULT: PoB drives protocol allocation/distribution; ROI is a downstream financial readout."
            in text
        )
