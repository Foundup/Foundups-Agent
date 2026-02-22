"""Layer-D BTC Anchor Connector - Blockchain Settlement Interface.

WSP 78 Layer D: Settlement state anchored to blockchain.

This module provides the interface between off-chain epoch ledger
commitments and on-chain Bitcoin anchoring via OP_RETURN.

ARCHITECTURE:
- Pre-settlement evidence comes from epoch_ledger.prepare_settlement_commitment()
- Anchor connector publishes to BTC and returns tx_ref
- tx_ref is persisted locally with idempotent replay guard
- Final settlement requires on-chain confirmation

FEATURE FLAG:
- LAYER_D_ENABLED=1 enables actual BTC publishing (default: disabled)
- When disabled, mock mode simulates anchoring for testing

MODES:
- mock: Simulated anchoring (no BTC node required)
- testnet: Bitcoin testnet (requires testnet node/API)
- mainnet: Bitcoin mainnet (requires mainnet node/API)

Reference: WSP 78 Section Layer D, WSP 26 Section 15
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Feature flag for Layer D
LAYER_D_ENABLED = os.getenv("LAYER_D_ENABLED", "0") == "1"

# Default paths
DEFAULT_ANCHOR_DB = Path("modules/foundups/simulator/memory/anchor_state.db")


class AnchorMode(Enum):
    """Anchor connector operating mode."""
    MOCK = "mock"  # Simulated - no real BTC transactions
    TESTNET = "testnet"  # Bitcoin testnet
    MAINNET = "mainnet"  # Bitcoin mainnet


class AnchorStatus(Enum):
    """Status of an anchor commitment."""
    PENDING = "pending"  # Pre-settlement, not yet published
    PUBLISHED = "published"  # OP_RETURN tx broadcasted
    CONFIRMED = "confirmed"  # Tx has confirmations
    FAILED = "failed"  # Publishing failed


@dataclass
class AnchorRecord:
    """Record of a blockchain anchor."""
    foundup_id: str
    epoch: int
    anchor_hex: str
    merkle_root: str
    entry_hash: str
    status: str
    tx_ref: Optional[str] = None
    confirmations: int = 0
    published_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class BTCAnchorConnector:
    """Layer-D connector for Bitcoin blockchain anchoring.

    Implements WSP 78 Layer D requirements:
    - Epoch roots anchored to blockchain
    - Idempotent publishing with replay guard
    - tx_ref persistence for verification

    Example:
        connector = BTCAnchorConnector()

        # Get commitment from ledger
        commitment = ledger.prepare_settlement_commitment(epoch=1)

        # Publish to blockchain (idempotent)
        result = connector.publish_commitment(commitment)

        if result["success"]:
            print(f"Anchored at tx: {result['tx_ref']}")
    """

    def __init__(
        self,
        mode: AnchorMode = AnchorMode.MOCK,
        db_path: Optional[Path] = None,
        btc_rpc_url: Optional[str] = None,
    ) -> None:
        """Initialize anchor connector.

        Args:
            mode: Operating mode (mock, testnet, mainnet)
            db_path: Path to SQLite state database
            btc_rpc_url: Bitcoin RPC endpoint (for non-mock modes)
        """
        self.mode = mode
        self.db_path = db_path or DEFAULT_ANCHOR_DB
        self.btc_rpc_url = btc_rpc_url

        # Initialize state database
        self._init_db()

        # Stats tracking
        self._stats = {
            "total_published": 0,
            "total_confirmed": 0,
            "total_failed": 0,
            "replay_guards_triggered": 0,
        }

        if not LAYER_D_ENABLED and mode != AnchorMode.MOCK:
            logger.warning(
                "[ANCHOR] LAYER_D_ENABLED=0 but non-mock mode requested. "
                "Forcing mock mode for safety."
            )
            self.mode = AnchorMode.MOCK

        logger.info(f"[ANCHOR] Initialized BTCAnchorConnector mode={self.mode.value}")

    def _init_db(self) -> None:
        """Initialize SQLite state database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS anchor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                foundup_id TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                anchor_hex TEXT NOT NULL,
                merkle_root TEXT NOT NULL,
                entry_hash TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                tx_ref TEXT,
                confirmations INTEGER DEFAULT 0,
                published_at TEXT,
                confirmed_at TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(foundup_id, epoch)
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_anchor_foundup_epoch
            ON anchor_records(foundup_id, epoch)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_anchor_status
            ON anchor_records(status)
        """)

        conn.commit()
        conn.close()

        logger.debug(f"[ANCHOR] State database initialized at {self.db_path}")

    def publish_commitment(
        self,
        commitment: Dict[str, Any],
        force: bool = False,
    ) -> Dict[str, Any]:
        """Publish pre-settlement commitment to blockchain.

        IDEMPOTENT: If epoch already anchored, returns existing tx_ref.

        Args:
            commitment: Pre-settlement payload from epoch_ledger
            force: Force re-publish even if already anchored (dangerous)

        Returns:
            Dict with success, tx_ref, status, and metadata
        """
        foundup_id = commitment.get("foundup_id", "unknown")
        epoch = commitment.get("epoch", 0)
        anchor_hex = commitment.get("anchor_hex", "")

        # Validate commitment
        if commitment.get("status") != "pre_settlement":
            return {
                "success": False,
                "error": "Invalid commitment - expected pre_settlement status",
                "foundup_id": foundup_id,
                "epoch": epoch,
            }

        if not anchor_hex or len(anchor_hex) != 40:
            return {
                "success": False,
                "error": f"Invalid anchor_hex - expected 40 chars, got {len(anchor_hex)}",
                "foundup_id": foundup_id,
                "epoch": epoch,
            }

        # REPLAY GUARD: Check if already anchored
        existing = self._get_anchor_record(foundup_id, epoch)

        if existing and not force:
            if existing.status in [AnchorStatus.PUBLISHED.value, AnchorStatus.CONFIRMED.value]:
                self._stats["replay_guards_triggered"] += 1
                logger.info(
                    f"[ANCHOR] Replay guard: {foundup_id} epoch {epoch} "
                    f"already {existing.status}"
                )
                return {
                    "success": True,
                    "tx_ref": existing.tx_ref,
                    "status": existing.status,
                    "idempotent_hit": True,
                    "foundup_id": foundup_id,
                    "epoch": epoch,
                    "confirmations": existing.confirmations,
                }

        # Create or update anchor record
        record = AnchorRecord(
            foundup_id=foundup_id,
            epoch=epoch,
            anchor_hex=anchor_hex,
            merkle_root=commitment.get("merkle_root", ""),
            entry_hash=commitment.get("entry_hash", ""),
            status=AnchorStatus.PENDING.value,
        )

        # Publish based on mode
        if self.mode == AnchorMode.MOCK:
            result = self._mock_publish(record)
        elif self.mode == AnchorMode.TESTNET:
            result = self._testnet_publish(record)
        elif self.mode == AnchorMode.MAINNET:
            result = self._mainnet_publish(record)
        else:
            result = {"success": False, "error": f"Unknown mode: {self.mode}"}

        # Persist result
        if result.get("success"):
            record.status = AnchorStatus.PUBLISHED.value
            record.tx_ref = result.get("tx_ref")
            record.published_at = datetime.now(timezone.utc).isoformat()
            self._stats["total_published"] += 1
        else:
            record.status = AnchorStatus.FAILED.value
            self._stats["total_failed"] += 1

        self._save_anchor_record(record)

        return {
            **result,
            "foundup_id": foundup_id,
            "epoch": epoch,
            "status": record.status,
            "idempotent_hit": False,
        }

    def _mock_publish(self, record: AnchorRecord) -> Dict[str, Any]:
        """Mock publishing - generates deterministic tx_ref for testing."""
        # Generate deterministic mock tx_ref from anchor data
        mock_payload = f"{record.foundup_id}:{record.epoch}:{record.anchor_hex}"
        mock_tx_ref = hashlib.sha256(mock_payload.encode()).hexdigest()

        logger.info(
            f"[ANCHOR] MOCK publish: {record.foundup_id} epoch {record.epoch} "
            f"-> tx:{mock_tx_ref[:16]}..."
        )

        return {
            "success": True,
            "tx_ref": mock_tx_ref,
            "mode": "mock",
            "message": "Mock transaction - no real BTC published",
        }

    def _testnet_publish(self, record: AnchorRecord) -> Dict[str, Any]:
        """Testnet publishing - requires testnet node/API."""
        if not LAYER_D_ENABLED:
            return {
                "success": False,
                "error": "LAYER_D_ENABLED=0 - testnet publishing disabled",
            }

        if not self.btc_rpc_url:
            return {
                "success": False,
                "error": "btc_rpc_url not configured for testnet",
            }

        # TODO: Implement actual testnet OP_RETURN publishing
        # This would use bitcoin-cli or a testnet API
        logger.warning("[ANCHOR] Testnet publishing not yet implemented")

        return {
            "success": False,
            "error": "Testnet publishing not yet implemented",
            "mode": "testnet",
        }

    def _mainnet_publish(self, record: AnchorRecord) -> Dict[str, Any]:
        """Mainnet publishing - requires mainnet node/API."""
        if not LAYER_D_ENABLED:
            return {
                "success": False,
                "error": "LAYER_D_ENABLED=0 - mainnet publishing disabled",
            }

        if not self.btc_rpc_url:
            return {
                "success": False,
                "error": "btc_rpc_url not configured for mainnet",
            }

        # TODO: Implement actual mainnet OP_RETURN publishing
        # CAUTION: This involves real BTC and should have extensive safety checks
        logger.warning("[ANCHOR] Mainnet publishing not yet implemented - DANGEROUS")

        return {
            "success": False,
            "error": "Mainnet publishing not yet implemented",
            "mode": "mainnet",
        }

    def check_confirmation(
        self,
        foundup_id: str,
        epoch: int,
        min_confirmations: int = 6,
    ) -> Dict[str, Any]:
        """Check confirmation status of an anchored epoch.

        Args:
            foundup_id: FoundUp identifier
            epoch: Epoch number
            min_confirmations: Minimum confirmations for "confirmed" status

        Returns:
            Dict with confirmation status and count
        """
        record = self._get_anchor_record(foundup_id, epoch)

        if not record:
            return {
                "found": False,
                "foundup_id": foundup_id,
                "epoch": epoch,
            }

        if record.status == AnchorStatus.PENDING.value:
            return {
                "found": True,
                "status": "pending",
                "confirmed": False,
                "confirmations": 0,
                "foundup_id": foundup_id,
                "epoch": epoch,
            }

        # In mock mode, simulate confirmations
        if self.mode == AnchorMode.MOCK:
            # Simulate: each check adds 1 confirmation (for testing)
            new_confirmations = record.confirmations + 1
            is_confirmed = new_confirmations >= min_confirmations

            if is_confirmed and record.status != AnchorStatus.CONFIRMED.value:
                record.status = AnchorStatus.CONFIRMED.value
                record.confirmed_at = datetime.now(timezone.utc).isoformat()
                self._stats["total_confirmed"] += 1

            record.confirmations = new_confirmations
            self._save_anchor_record(record)

            return {
                "found": True,
                "status": record.status,
                "confirmed": is_confirmed,
                "confirmations": new_confirmations,
                "min_required": min_confirmations,
                "tx_ref": record.tx_ref,
                "foundup_id": foundup_id,
                "epoch": epoch,
            }

        # For real modes, would query blockchain
        # TODO: Implement actual confirmation checking
        return {
            "found": True,
            "status": record.status,
            "confirmed": record.status == AnchorStatus.CONFIRMED.value,
            "confirmations": record.confirmations,
            "tx_ref": record.tx_ref,
            "foundup_id": foundup_id,
            "epoch": epoch,
            "note": "Real confirmation checking not yet implemented",
        }

    def get_anchor_status(
        self,
        foundup_id: str,
        epoch: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get anchor status for a FoundUp.

        Args:
            foundup_id: FoundUp identifier
            epoch: Optional specific epoch (None = all epochs)

        Returns:
            List of anchor records
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row

        if epoch is not None:
            cursor = conn.execute(
                "SELECT * FROM anchor_records WHERE foundup_id = ? AND epoch = ?",
                (foundup_id, epoch),
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM anchor_records WHERE foundup_id = ? ORDER BY epoch",
                (foundup_id,),
            )

        records = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return records

    def _get_anchor_record(
        self,
        foundup_id: str,
        epoch: int,
    ) -> Optional[AnchorRecord]:
        """Get existing anchor record from database."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            "SELECT * FROM anchor_records WHERE foundup_id = ? AND epoch = ?",
            (foundup_id, epoch),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return AnchorRecord(
            foundup_id=row["foundup_id"],
            epoch=row["epoch"],
            anchor_hex=row["anchor_hex"],
            merkle_root=row["merkle_root"],
            entry_hash=row["entry_hash"],
            status=row["status"],
            tx_ref=row["tx_ref"],
            confirmations=row["confirmations"],
            published_at=row["published_at"],
            confirmed_at=row["confirmed_at"],
            created_at=row["created_at"],
        )

    def _save_anchor_record(self, record: AnchorRecord) -> None:
        """Save or update anchor record in database."""
        conn = sqlite3.connect(str(self.db_path))

        conn.execute("""
            INSERT OR REPLACE INTO anchor_records (
                foundup_id, epoch, anchor_hex, merkle_root, entry_hash,
                status, tx_ref, confirmations, published_at, confirmed_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.foundup_id,
            record.epoch,
            record.anchor_hex,
            record.merkle_root,
            record.entry_hash,
            record.status,
            record.tx_ref,
            record.confirmations,
            record.published_at,
            record.confirmed_at,
            record.created_at,
        ))

        conn.commit()
        conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get connector statistics."""
        return {
            "mode": self.mode.value,
            "layer_d_enabled": LAYER_D_ENABLED,
            **self._stats,
        }


# Singleton management
_connector_instance: Optional[BTCAnchorConnector] = None


def get_anchor_connector(
    mode: Optional[AnchorMode] = None,
    db_path: Optional[Path] = None,
) -> BTCAnchorConnector:
    """Get or create singleton anchor connector.

    Args:
        mode: Operating mode (defaults to MOCK)
        db_path: State database path

    Returns:
        BTCAnchorConnector instance
    """
    global _connector_instance

    if _connector_instance is None:
        _connector_instance = BTCAnchorConnector(
            mode=mode or AnchorMode.MOCK,
            db_path=db_path,
        )

    return _connector_instance


def reset_anchor_connector() -> None:
    """Reset singleton (for testing)."""
    global _connector_instance
    _connector_instance = None


__all__ = [
    "AnchorMode",
    "AnchorStatus",
    "AnchorRecord",
    "BTCAnchorConnector",
    "get_anchor_connector",
    "reset_anchor_connector",
    "LAYER_D_ENABLED",
]
