import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from .payment_types import PaymentRequest, TransactionResult, WalletStatus

# Lazy load AgentDB to avoid circular imports
# from modules.infrastructure.database.src.agent_db import AgentDB

logger = logging.getLogger(__name__)

class LobsterClient:
    """
    Client for the Lobster.cash open payment standard.
    
    Integrates:
    - Crossmint (Wallet & Policy)
    - Visa (Payment Rails)
    - Solana (Settlement Layer)
    - Circle (USDC Stablecoin)
    - Stytch (Auth)
    """

    def __init__(self, agent_id: str, network: str = "solana-mainnet"):
        self.agent_id = agent_id
        self.network = network
        self.logger = logger
        self._wallet_address = None
        self._policy_limits = {"daily_max_usdc": Decimal("50.00")}
        
        # Load DB connection lazily
        self._agent_db = None
        
        self.logger.info(f"LobsterClient initialized for agent {agent_id} on {network}")

    def _get_db(self):
        if self._agent_db is None:
            from modules.infrastructure.database.src.agent_db import AgentDB
            self._agent_db = AgentDB()
        return self._agent_db

    def get_wallet_status(self) -> WalletStatus:
        """Get current wallet balance and status."""
        # TODO: Integrate actual Crossmint API
        # For now, return mock status
        return WalletStatus(
            address=self._wallet_address or "mock-solana-address-123",
            balance={"USDC": Decimal("100.00"), "SOL": Decimal("0.5")},
            network=self.network,
            is_locked=False
        )

    def send_payment(self, request: PaymentRequest) -> TransactionResult:
        """
        Execute a payment to a pAVS or service.
        
        1. Check policy limits
        2. Create transaction
        3. Sign & Broadcast (via Crossmint)
        4. Record in AgentDB
        """
        tx_id = str(uuid.uuid4())
        
        self.logger.info(f"Initiating payment {tx_id}: {request.amount} {request.currency} to {request.recipient_address}")

        # 1. Policy Check
        if not self._check_policy(request):
            return TransactionResult(
                tx_id=tx_id,
                tx_hash=None,
                status="failed",
                timestamp=datetime.now(),
                error_message="Policy violation: Exceeds spending limit"
            )

        # 2. Execute (Mock for Phase 9)
        # In real implementation, this calls Crossmint SDK
        tx_hash = f"sig-{uuid.uuid4()}" # Mock signature
        status = "confirmed"

        # 3. Record in DB
        self._record_transaction(tx_id, request, tx_hash, status)

        return TransactionResult(
            tx_id=tx_id,
            tx_hash=tx_hash,
            status=status,
            timestamp=datetime.now()
        )

    def _check_policy(self, request: PaymentRequest) -> bool:
        """Check if transaction is allowed by agent policy."""
        if request.currency == "USDC" and request.amount > self._policy_limits["daily_max_usdc"]:
            self.logger.warning(f"Payment blocked using Lobster policy: {request.amount} > {self._policy_limits['daily_max_usdc']}")
            return False
        return True

    def _record_transaction(self, tx_id: str, request: PaymentRequest, tx_hash: str, status: str):
        """Persist transaction to AgentDB."""
        try:
            db = self._get_db()
            # We need to implement record_transaction in AgentDB next
            if hasattr(db, "record_transaction"):
                db.record_transaction(
                    tx_id=tx_id,
                    chain_tx_hash=tx_hash,
                    amount=float(request.amount),
                    currency=request.currency,
                    purpose=request.purpose,
                    status=status,
                    metadata=request.metadata
                )
        except Exception as e:
            self.logger.error(f"Failed to record transaction {tx_id}: {e}")
