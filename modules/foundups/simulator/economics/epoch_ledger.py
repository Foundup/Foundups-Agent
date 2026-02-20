"""Epoch Ledger - Auditable Distribution Records (WSP 26 Section 15).

Implements transparent, cryptographically verifiable epoch distribution records:

FEATURES:
- Append-only chain (blockchain-lite)
- Merkle root per epoch for batch verification
- IPFS pinning for decentralized storage (optional)
- FAM daemon integration for event sourcing

LEDGER CHAIN:
- Each entry contains hash of previous entry (tamper detection)
- Entry hash = SHA-256(epoch + timestamp + pools + rewards + prev_hash)
- Chain validity verifiable by anyone with access

MERKLE TREE:
- Leaf nodes: hash of (participant_id, amount) pairs
- Root provides O(log n) verification of individual rewards
- Enables "prove my reward" without revealing others

ACCESS TIERS:
- Public: Merkle roots only
- Participant: Own rewards + epoch summaries
- Validator: Full epoch entries
- Auditor: Full ledger + Merkle proofs

Reference: WSP 26 Section 15, WSP 29 (CABR integration)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
import json


@dataclass
class EpochEntry:
    """Single epoch distribution record.

    Forms one link in the epoch ledger chain. Each entry
    cryptographically links to its predecessor.
    """

    epoch_number: int
    timestamp: str  # ISO 8601
    total_fi_distributed: float
    pool_allocations: Dict[str, float]  # un/dao/du/network/fund amounts
    participant_rewards: Dict[str, float]  # participant_id → amount
    entry_hash: str = ""  # SHA-256 of this entry (computed after creation)
    prev_hash: str = "genesis"  # Link to previous entry

    def compute_hash(self) -> str:
        """Compute deterministic hash of this entry.

        Uses sorted keys to ensure consistent hashing regardless
        of dict ordering.
        """
        payload = json.dumps(
            {
                "epoch": self.epoch_number,
                "timestamp": self.timestamp,
                "total": self.total_fi_distributed,
                "pools": self.pool_allocations,
                "rewards": sorted(self.participant_rewards.items()),
                "prev": self.prev_hash,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Export for JSON serialization."""
        return {
            "epoch_number": self.epoch_number,
            "timestamp": self.timestamp,
            "total_fi_distributed": self.total_fi_distributed,
            "pool_allocations": self.pool_allocations,
            "participant_count": len(self.participant_rewards),
            "entry_hash": self.entry_hash,
            "prev_hash": self.prev_hash,
        }


@dataclass
class MerkleProof:
    """Merkle proof for verifying a single participant's reward."""

    participant_id: str
    amount: float
    leaf_hash: str
    proof_path: List[Tuple[str, str]]  # (sibling_hash, direction)
    merkle_root: str
    epoch_number: int

    def verify(self) -> bool:
        """Verify this proof against the stored Merkle root."""
        current = self.leaf_hash

        for sibling_hash, direction in self.proof_path:
            if direction == "left":
                combined = sibling_hash + current
            else:
                combined = current + sibling_hash
            current = hashlib.sha256(combined.encode()).hexdigest()

        return current == self.merkle_root


class EpochLedger:
    """Auditable ledger of all epoch distributions.

    Maintains a cryptographic chain of epoch distribution records.
    Each epoch generates:
    - Entry hash (links to chain)
    - Merkle root (enables individual reward verification)

    Example usage:
        ledger = EpochLedger("foundup_001")

        # Record epoch (integrates with PoolDistributor)
        entry = ledger.record_epoch(
            epoch=1,
            total=1000.0,
            pool_allocations={"un": 600, "dao": 160, "du": 40, ...},
            participant_rewards={"alice": 100, "bob": 50, ...}
        )

        # Verify chain integrity
        assert ledger.verify_chain()

        # Get Merkle proof for participant
        proof = ledger.get_merkle_proof(1, "alice")
        assert proof.verify()
    """

    def __init__(self, foundup_id: str):
        """Initialize ledger for a FoundUp.

        Args:
            foundup_id: FoundUp this ledger tracks
        """
        self.foundup_id = foundup_id
        self.entries: List[EpochEntry] = []
        self.merkle_roots: Dict[int, str] = {}  # epoch → merkle root
        self.merkle_trees: Dict[int, List[List[str]]] = {}  # epoch → tree levels

    def record_epoch(
        self,
        epoch: int,
        total: float,
        pool_allocations: Dict[str, float],
        participant_rewards: Dict[str, float],
    ) -> EpochEntry:
        """Record an epoch distribution to the ledger.

        Args:
            epoch: Epoch number
            total: Total F_i distributed
            pool_allocations: Dict of pool name → amount
            participant_rewards: Dict of participant_id → reward amount

        Returns:
            The created EpochEntry with computed hashes
        """
        prev_hash = self.entries[-1].entry_hash if self.entries else "genesis"

        entry = EpochEntry(
            epoch_number=epoch,
            timestamp=datetime.utcnow().isoformat(),
            total_fi_distributed=total,
            pool_allocations=pool_allocations,
            participant_rewards=participant_rewards,
            entry_hash="",  # Computed below
            prev_hash=prev_hash,
        )
        entry.entry_hash = entry.compute_hash()

        self.entries.append(entry)
        self._build_merkle_tree(entry)

        return entry

    def record_from_distribution(self, distribution) -> EpochEntry:
        """Record from an EpochDistribution object (pool_distribution.py).

        Args:
            distribution: EpochDistribution from PoolDistributor

        Returns:
            The created EpochEntry
        """
        return self.record_epoch(
            epoch=distribution.epoch,
            total=distribution.total_rewards,
            pool_allocations={
                "un": distribution.un_pool,
                "dao": distribution.dao_pool,
                "du": distribution.du_pool,
                "network": distribution.network_pool,
                "fund": distribution.fund_pool,
            },
            participant_rewards=distribution.participant_rewards,
        )

    def _build_merkle_tree(self, entry: EpochEntry) -> str:
        """Build Merkle tree for participant rewards.

        Creates full tree structure for proof generation.

        Args:
            entry: EpochEntry to build tree for

        Returns:
            Merkle root hash
        """
        # Create leaf nodes: hash of (participant_id, amount) pairs
        sorted_rewards = sorted(entry.participant_rewards.items())
        leaves = [
            hashlib.sha256(f"{pid}:{amt}".encode()).hexdigest()
            for pid, amt in sorted_rewards
        ]

        if not leaves:
            merkle_root = hashlib.sha256(b"empty_epoch").hexdigest()
            self.merkle_roots[entry.epoch_number] = merkle_root
            self.merkle_trees[entry.epoch_number] = [[merkle_root]]
            return merkle_root

        # Build tree bottom-up, storing each level
        tree_levels = [leaves]

        current_level = leaves
        while len(current_level) > 1:
            # Pad with duplicate if odd
            if len(current_level) % 2 == 1:
                current_level = current_level + [current_level[-1]]

            # Hash pairs
            next_level = [
                hashlib.sha256((current_level[i] + current_level[i + 1]).encode()).hexdigest()
                for i in range(0, len(current_level), 2)
            ]
            tree_levels.append(next_level)
            current_level = next_level

        merkle_root = current_level[0]
        self.merkle_roots[entry.epoch_number] = merkle_root
        self.merkle_trees[entry.epoch_number] = tree_levels

        return merkle_root

    def get_merkle_proof(self, epoch: int, participant_id: str) -> Optional[MerkleProof]:
        """Generate Merkle proof for a participant's reward.

        Args:
            epoch: Epoch number
            participant_id: Participant to generate proof for

        Returns:
            MerkleProof if found, None otherwise
        """
        # Find entry
        entry = None
        for e in self.entries:
            if e.epoch_number == epoch:
                entry = e
                break

        if entry is None or participant_id not in entry.participant_rewards:
            return None

        amount = entry.participant_rewards[participant_id]
        tree_levels = self.merkle_trees.get(epoch)
        if not tree_levels:
            return None

        # Find leaf index
        sorted_rewards = sorted(entry.participant_rewards.items())
        try:
            leaf_index = [pid for pid, _ in sorted_rewards].index(participant_id)
        except ValueError:
            return None

        leaf_hash = hashlib.sha256(f"{participant_id}:{amount}".encode()).hexdigest()

        # Build proof path
        proof_path: List[Tuple[str, str]] = []
        index = leaf_index

        for level in tree_levels[:-1]:  # Exclude root
            # Pad level if needed
            padded_level = level[:]
            if len(padded_level) % 2 == 1:
                padded_level = padded_level + [padded_level[-1]]

            # Get sibling
            if index % 2 == 0:
                sibling_index = index + 1
                direction = "right"
            else:
                sibling_index = index - 1
                direction = "left"

            if sibling_index < len(padded_level):
                proof_path.append((padded_level[sibling_index], direction))

            index = index // 2

        return MerkleProof(
            participant_id=participant_id,
            amount=amount,
            leaf_hash=leaf_hash,
            proof_path=proof_path,
            merkle_root=self.merkle_roots[epoch],
            epoch_number=epoch,
        )

    def verify_entry(self, epoch_number: int) -> bool:
        """Verify the integrity of a specific epoch entry.

        Args:
            epoch_number: Epoch to verify

        Returns:
            True if entry hash is valid
        """
        for entry in self.entries:
            if entry.epoch_number == epoch_number:
                return entry.entry_hash == entry.compute_hash()
        return False

    def verify_chain(self) -> bool:
        """Verify the entire ledger chain integrity.

        Checks:
        - Each entry's hash is correct
        - Each entry's prev_hash matches previous entry

        Returns:
            True if entire chain is valid
        """
        for i, entry in enumerate(self.entries):
            # Verify entry hash
            if entry.entry_hash != entry.compute_hash():
                return False

            # Verify chain linkage
            if i == 0:
                if entry.prev_hash != "genesis":
                    return False
            else:
                if entry.prev_hash != self.entries[i - 1].entry_hash:
                    return False

        return True

    def get_audit_summary(self) -> Dict:
        """Generate audit summary for the entire ledger.

        Returns:
            Summary dict with key metrics and chain status
        """
        return {
            "foundup_id": self.foundup_id,
            "total_epochs": len(self.entries),
            "total_fi_distributed": sum(e.total_fi_distributed for e in self.entries),
            "unique_participants": len(
                set(pid for e in self.entries for pid in e.participant_rewards.keys())
            ),
            "latest_merkle_root": (
                self.merkle_roots.get(self.entries[-1].epoch_number, "none")
                if self.entries
                else "none"
            ),
            "chain_valid": self.verify_chain(),
            "first_epoch": self.entries[0].epoch_number if self.entries else None,
            "last_epoch": self.entries[-1].epoch_number if self.entries else None,
        }

    def get_participant_history(
        self, participant_id: str, limit: int = 50
    ) -> List[Dict]:
        """Get reward history for a participant.

        Args:
            participant_id: Participant to query
            limit: Maximum entries to return

        Returns:
            List of epoch summaries with this participant's rewards
        """
        history = []
        for entry in reversed(self.entries):
            if participant_id in entry.participant_rewards:
                history.append({
                    "epoch": entry.epoch_number,
                    "timestamp": entry.timestamp,
                    "reward": entry.participant_rewards[participant_id],
                    "total_distributed": entry.total_fi_distributed,
                })
                if len(history) >= limit:
                    break
        return history

    def anchor_to_chain(self, epoch: int) -> Optional[str]:
        """Generate anchor data for on-chain publishing.

        Creates a compact hash suitable for Bitcoin OP_RETURN
        or other anchoring mechanisms.

        Args:
            epoch: Epoch to anchor

        Returns:
            40-character hex string for OP_RETURN, or None if epoch not found
        """
        merkle_root = self.merkle_roots.get(epoch)
        if not merkle_root:
            return None

        anchor_data = {
            "protocol": "pAVS-v1",
            "type": "epoch_anchor",
            "foundup": self.foundup_id,
            "epoch": epoch,
            "merkle_root": merkle_root,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # 20-byte OP_RETURN payload (40 hex chars)
        op_return_hex = hashlib.sha256(
            json.dumps(anchor_data, sort_keys=True).encode()
        ).hexdigest()[:40]

        return op_return_hex


# Singleton management
_ledger_registry: Dict[str, EpochLedger] = {}


def get_epoch_ledger(foundup_id: str) -> EpochLedger:
    """Get or create ledger for a FoundUp.

    Args:
        foundup_id: FoundUp identifier

    Returns:
        EpochLedger instance
    """
    if foundup_id not in _ledger_registry:
        _ledger_registry[foundup_id] = EpochLedger(foundup_id)
    return _ledger_registry[foundup_id]


def reset_epoch_ledgers() -> None:
    """Reset all ledgers (for testing)."""
    global _ledger_registry
    _ledger_registry = {}


__all__ = [
    "EpochEntry",
    "MerkleProof",
    "EpochLedger",
    "get_epoch_ledger",
    "reset_epoch_ledgers",
]
