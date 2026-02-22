"""Tests for Layer-D BTC Anchor Connector."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from modules.foundups.simulator.economics.btc_anchor_connector import (
    AnchorMode,
    AnchorStatus,
    BTCAnchorConnector,
    reset_anchor_connector,
)
from modules.foundups.simulator.economics.epoch_ledger import EpochLedger


@pytest.fixture
def temp_db():
    """Provide temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield Path(f.name)


@pytest.fixture
def connector(temp_db):
    """Create test connector with temp database."""
    reset_anchor_connector()
    conn = BTCAnchorConnector(mode=AnchorMode.MOCK, db_path=temp_db)
    yield conn
    reset_anchor_connector()


@pytest.fixture
def sample_commitment():
    """Sample pre-settlement commitment payload."""
    return {
        "status": "pre_settlement",
        "wsp_78_layer": "D_pending",
        "requires": "external_btc_anchor_connector",
        "foundup_id": "foundup_test",
        "epoch": 1,
        "anchor_hex": "a" * 40,  # 40 hex chars
        "merkle_root": "b" * 64,
        "entry_hash": "c" * 64,
        "total_distributed": 1000.0,
        "participant_count": 5,
        "timestamp": "2026-02-22T12:00:00Z",
    }


class TestMockPublishing:
    """Tests for mock publishing mode."""

    def test_publish_commitment_returns_success(self, connector, sample_commitment):
        """Mock publishing should succeed and return tx_ref."""
        result = connector.publish_commitment(sample_commitment)

        assert result["success"] is True
        assert result["tx_ref"] is not None
        assert len(result["tx_ref"]) == 64  # SHA-256 hex
        assert result["status"] == AnchorStatus.PUBLISHED.value
        assert result["idempotent_hit"] is False

    def test_publish_generates_deterministic_tx_ref(self, connector, sample_commitment):
        """Same commitment should generate same tx_ref."""
        result1 = connector.publish_commitment(sample_commitment)
        tx_ref1 = result1["tx_ref"]

        # Create new connector with same data - should get same mock tx_ref
        reset_anchor_connector()
        connector2 = BTCAnchorConnector(mode=AnchorMode.MOCK, db_path=connector.db_path)
        result2 = connector2.publish_commitment(sample_commitment, force=True)
        tx_ref2 = result2["tx_ref"]

        assert tx_ref1 == tx_ref2

    def test_invalid_commitment_status_fails(self, connector):
        """Commitment with wrong status should fail."""
        invalid = {"status": "invalid", "foundup_id": "x", "epoch": 1}
        result = connector.publish_commitment(invalid)

        assert result["success"] is False
        assert "pre_settlement" in result["error"]

    def test_invalid_anchor_hex_fails(self, connector, sample_commitment):
        """Commitment with wrong anchor_hex length should fail."""
        sample_commitment["anchor_hex"] = "short"
        result = connector.publish_commitment(sample_commitment)

        assert result["success"] is False
        assert "anchor_hex" in result["error"]


class TestIdempotentReplayGuard:
    """Tests for idempotent replay guard."""

    def test_second_publish_returns_existing_tx_ref(self, connector, sample_commitment):
        """Re-publishing same epoch should return existing tx_ref."""
        result1 = connector.publish_commitment(sample_commitment)
        tx_ref1 = result1["tx_ref"]

        result2 = connector.publish_commitment(sample_commitment)

        assert result2["success"] is True
        assert result2["tx_ref"] == tx_ref1
        assert result2["idempotent_hit"] is True
        assert result2["status"] == AnchorStatus.PUBLISHED.value

    def test_replay_guard_increments_stats(self, connector, sample_commitment):
        """Replay guard should increment statistics."""
        connector.publish_commitment(sample_commitment)
        connector.publish_commitment(sample_commitment)
        connector.publish_commitment(sample_commitment)

        stats = connector.get_stats()
        assert stats["replay_guards_triggered"] == 2
        assert stats["total_published"] == 1

    def test_force_bypasses_replay_guard(self, connector, sample_commitment):
        """Force flag should allow re-publishing."""
        result1 = connector.publish_commitment(sample_commitment)
        result2 = connector.publish_commitment(sample_commitment, force=True)

        assert result2["success"] is True
        assert result2["idempotent_hit"] is False
        # Stats show 2 publishes
        stats = connector.get_stats()
        assert stats["total_published"] == 2

    def test_different_epochs_not_blocked(self, connector, sample_commitment):
        """Different epochs should not trigger replay guard."""
        result1 = connector.publish_commitment(sample_commitment)

        sample_commitment["epoch"] = 2
        result2 = connector.publish_commitment(sample_commitment)

        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["tx_ref"] != result2["tx_ref"]
        assert result2["idempotent_hit"] is False


class TestTxRefPersistence:
    """Tests for tx_ref persistence."""

    def test_tx_ref_persists_across_restarts(self, temp_db, sample_commitment):
        """tx_ref should persist when connector is recreated."""
        connector1 = BTCAnchorConnector(mode=AnchorMode.MOCK, db_path=temp_db)
        result1 = connector1.publish_commitment(sample_commitment)
        tx_ref1 = result1["tx_ref"]

        # "Restart" - create new connector
        connector2 = BTCAnchorConnector(mode=AnchorMode.MOCK, db_path=temp_db)
        records = connector2.get_anchor_status("foundup_test", epoch=1)

        assert len(records) == 1
        assert records[0]["tx_ref"] == tx_ref1
        assert records[0]["status"] == AnchorStatus.PUBLISHED.value

    def test_get_anchor_status_returns_all_epochs(self, connector, sample_commitment):
        """get_anchor_status without epoch returns all."""
        for epoch in [1, 2, 3]:
            sample_commitment["epoch"] = epoch
            connector.publish_commitment(sample_commitment)

        records = connector.get_anchor_status("foundup_test")

        assert len(records) == 3
        assert [r["epoch"] for r in records] == [1, 2, 3]


class TestConfirmationChecking:
    """Tests for confirmation checking."""

    def test_check_confirmation_on_unpublished(self, connector):
        """Checking unpublished epoch returns not found."""
        result = connector.check_confirmation("foundup_x", epoch=99)

        assert result["found"] is False

    def test_mock_confirmation_increments(self, connector, sample_commitment):
        """Mock mode should increment confirmations on each check."""
        connector.publish_commitment(sample_commitment)

        result1 = connector.check_confirmation("foundup_test", epoch=1)
        assert result1["confirmations"] == 1
        assert result1["confirmed"] is False

        result2 = connector.check_confirmation("foundup_test", epoch=1)
        assert result2["confirmations"] == 2

    def test_confirmation_threshold_triggers_confirmed_status(
        self, connector, sample_commitment
    ):
        """Reaching min_confirmations should set CONFIRMED status."""
        connector.publish_commitment(sample_commitment)

        # Check 6 times to reach threshold
        for i in range(6):
            result = connector.check_confirmation(
                "foundup_test", epoch=1, min_confirmations=6
            )

        assert result["confirmed"] is True
        assert result["status"] == AnchorStatus.CONFIRMED.value

        # Stats updated
        stats = connector.get_stats()
        assert stats["total_confirmed"] == 1


class TestEpochLedgerIntegration:
    """Tests for integration with EpochLedger."""

    def test_publish_from_epoch_ledger_commitment(self, connector):
        """Connector should work with real epoch_ledger commitment."""
        ledger = EpochLedger("foundup_integration")
        ledger.record_epoch(
            epoch=1,
            total=500.0,
            pool_allocations={"un": 300, "dao": 80, "du": 20, "network": 100},
            participant_rewards={"alice": 200, "bob": 150, "carol": 150},
        )

        commitment = ledger.prepare_settlement_commitment(epoch=1)
        assert commitment is not None

        result = connector.publish_commitment(commitment)

        assert result["success"] is True
        assert result["foundup_id"] == "foundup_integration"
        assert result["epoch"] == 1
        assert len(result["tx_ref"]) == 64


class TestFeatureFlag:
    """Tests for LAYER_D_ENABLED feature flag."""

    def test_mock_mode_works_without_flag(self, temp_db):
        """Mock mode should work regardless of feature flag."""
        connector = BTCAnchorConnector(mode=AnchorMode.MOCK, db_path=temp_db)

        commitment = {
            "status": "pre_settlement",
            "foundup_id": "test",
            "epoch": 1,
            "anchor_hex": "f" * 40,
            "merkle_root": "0" * 64,
            "entry_hash": "1" * 64,
        }

        result = connector.publish_commitment(commitment)
        assert result["success"] is True

    def test_testnet_requires_flag(self, temp_db):
        """Testnet mode should fail without LAYER_D_ENABLED."""
        # Feature flag is off by default
        connector = BTCAnchorConnector(mode=AnchorMode.TESTNET, db_path=temp_db)

        # Should be forced to mock mode
        assert connector.mode == AnchorMode.MOCK
