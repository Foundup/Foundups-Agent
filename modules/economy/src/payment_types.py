from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

@dataclass
class PaymentRequest:
    """Request to send a payment via Lobster.cash"""
    amount: Decimal
    currency: str  # e.g., "USDC"
    recipient_address: str
    purpose: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TransactionResult:
    """Result of a payment transaction"""
    tx_id: str
    tx_hash: Optional[str]
    status: str  # pending, confirmed, failed
    timestamp: datetime
    error_message: Optional[str] = None

@dataclass
class WalletStatus:
    """Current status of the agent's wallet"""
    address: str
    balance: Dict[str, Decimal]  # {"USDC": 50.00, "SOL": 0.1}
    network: str  # e.g., "solana-mainnet"
    is_locked: bool
