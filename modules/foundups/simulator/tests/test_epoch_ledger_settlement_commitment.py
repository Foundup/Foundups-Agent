"""Tests for pre-settlement commitment payloads in epoch ledger."""

from __future__ import annotations

from modules.foundups.simulator.economics.epoch_ledger import EpochLedger


def test_prepare_settlement_commitment_returns_none_when_epoch_missing() -> None:
    ledger = EpochLedger("foundup_x")
    assert ledger.prepare_settlement_commitment(1) is None


def test_prepare_settlement_commitment_contains_expected_fields() -> None:
    ledger = EpochLedger("foundup_001")
    ledger.record_epoch(
        epoch=1,
        total=123.45,
        pool_allocations={"un": 60.0, "dao": 16.0, "du": 4.0, "network": 20.0, "fund": 0.0},
        participant_rewards={"alice": 70.0, "bob": 53.45},
    )

    commitment = ledger.prepare_settlement_commitment(1)
    assert commitment is not None
    assert commitment["status"] == "pre_settlement"
    assert commitment["wsp_78_layer"] == "D_pending"
    assert commitment["requires"] == "external_btc_anchor_connector"
    assert commitment["foundup_id"] == "foundup_001"
    assert commitment["epoch"] == 1
    assert len(commitment["anchor_hex"]) == 40
    assert commitment["participant_count"] == 2
    assert float(commitment["total_distributed"]) == 123.45
