"""BTC Reserve - The "Hole in the Bucket" for Bitcoin.

FoundUps is a Bitcoin sink - BTC flows IN but NEVER flows OUT.
BTC gets transformed into UP$ backing.

SUBSCRIPTION PAYMENTS (Multi-Crypto):
- Pay in ANY crypto: BTC, ETH, SOL, USDC, etc.
- All crypto converts to BTC → Reserve
- Pay in UP$ → BURNS UP$ (reduces supply, strengthens currency)

BTC Sources:
1. Subscription payments (any crypto) → Convert to BTC → Reserve
2. Demurrage decay from unused wallet UP$ → Reserve
3. Exit fees (11% mined, 5% staked) → Reserve
4. F_i trading fees → Reserve

UP$ VALUE MODEL:
- UP$ floats with BTC price (not USD-pegged)
- UP$ value = (BTC Reserve × BTC Price) / UP$ Supply
- Natural contraction when BTC drops, expansion when BTC pumps
- No artificial circuit breaker needed - organic adjustment

Key Insight: The system absorbs Bitcoin and never releases it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from datetime import datetime

logger = logging.getLogger(__name__)


class BTCSourceType(Enum):
    """Sources of BTC flowing into the reserve."""
    SUBSCRIPTION = "subscription"  # Monthly subscription payments
    SUBSCRIPTION_UPS_BURN = "subscription_ups_burn"  # Subscription paid in UP$ (burned)
    DEMURRAGE = "demurrage"  # Decay from unused UP$ in wallets
    MINED_EXIT_FEE = "mined_exit_fee"  # 11% fee on mined F_i extraction
    STAKED_EXIT_FEE = "staked_exit_fee"  # 5% fee on staked F_i unstaking
    STAKED_ENTRY_FEE = "staked_entry_fee"  # 3% fee on staking
    TRADING_FEE = "trading_fee"  # Fees from F_i order book
    CASHOUT_FEE = "cashout_fee"  # 7% fee on UP$ → external


class PaymentCrypto(Enum):
    """Supported cryptocurrencies for subscription payments."""
    BTC = "btc"
    ETH = "eth"
    SOL = "sol"
    USDC = "usdc"
    USDT = "usdt"
    UPS = "ups"  # Pay with UP$ - gets BURNED


@dataclass
class CryptoRates:
    """Current crypto-to-BTC conversion rates (simulated)."""
    # All rates are: 1 unit of crypto = X BTC
    btc_per_eth: float = 0.035  # 1 ETH = 0.035 BTC (~$3,500 ETH, $100K BTC)
    btc_per_sol: float = 0.0015  # 1 SOL = 0.0015 BTC (~$150 SOL)
    btc_per_usdc: float = 0.00001  # 1 USDC = 0.00001 BTC ($1 = 0.00001 BTC at $100K)
    btc_per_usdt: float = 0.00001  # Same as USDC
    btc_usd_price: float = 100000.0  # Current BTC price in USD

    def get_btc_amount(self, crypto: PaymentCrypto, amount: float) -> float:
        """Convert any crypto amount to BTC equivalent."""
        if crypto == PaymentCrypto.BTC:
            return amount
        elif crypto == PaymentCrypto.ETH:
            return amount * self.btc_per_eth
        elif crypto == PaymentCrypto.SOL:
            return amount * self.btc_per_sol
        elif crypto == PaymentCrypto.USDC:
            return amount * self.btc_per_usdc
        elif crypto == PaymentCrypto.USDT:
            return amount * self.btc_per_usdt
        elif crypto == PaymentCrypto.UPS:
            # UP$ is valued at current UP$ price (floating with BTC)
            # This will be calculated by the reserve itself
            return 0.0  # Handled specially - burns UP$
        return 0.0


@dataclass
class BTCInflow:
    """Record of BTC flowing into the reserve."""
    source: BTCSourceType
    btc_amount: float
    usd_value: float  # USD value at time of inflow
    timestamp: str
    foundup_id: Optional[str] = None  # Which FoundUp (if applicable)
    human_id: Optional[str] = None  # Which human triggered this
    original_crypto: Optional[PaymentCrypto] = None  # What crypto was paid
    original_amount: Optional[float] = None  # Original amount before conversion


@dataclass
class BTCReserve:
    """The Bitcoin Reserve - backs UP$ supply.

    Hotel California: BTC checks in, never checks out.

    UP$ VALUE MODEL (Floating):
    - UP$ value floats with BTC price
    - ups_value_usd = (total_btc * btc_usd_price) / total_ups_minted
    - Natural expansion/contraction with BTC price moves
    """

    # Total BTC in reserve (only grows)
    total_btc: float = 0.0

    # Track by source for analytics
    btc_by_source: Dict[BTCSourceType, float] = field(default_factory=lambda: {
        BTCSourceType.SUBSCRIPTION: 0.0,
        BTCSourceType.SUBSCRIPTION_UPS_BURN: 0.0,
        BTCSourceType.DEMURRAGE: 0.0,
        BTCSourceType.MINED_EXIT_FEE: 0.0,
        BTCSourceType.STAKED_EXIT_FEE: 0.0,
        BTCSourceType.STAKED_ENTRY_FEE: 0.0,
        BTCSourceType.TRADING_FEE: 0.0,
        BTCSourceType.CASHOUT_FEE: 0.0,
    })

    # Track by FoundUp for individual backing
    btc_by_foundup: Dict[str, float] = field(default_factory=dict)

    # Inflow history
    inflows: List[BTCInflow] = field(default_factory=list)

    # UP$ supply tracking
    total_ups_minted: float = 0.0
    total_ups_burned: float = 0.0  # Track burns from UP$ subscriptions

    # Crypto conversion rates (simulated, updateable)
    crypto_rates: CryptoRates = field(default_factory=CryptoRates)

    # Genesis rate: initial UP$ per BTC when system starts
    # After genesis, UP$ value floats with reserve
    genesis_ups_per_btc: float = 100000.0  # 1 BTC = 100,000 UP$ at genesis

    @property
    def btc_usd_price(self) -> float:
        """Current BTC price in USD."""
        return self.crypto_rates.btc_usd_price

    @btc_usd_price.setter
    def btc_usd_price(self, value: float) -> None:
        """Update BTC price (for simulation)."""
        self.crypto_rates.btc_usd_price = value

    @property
    def ups_value_usd(self) -> float:
        """Current UP$ value in USD (floats with BTC).

        UP$ value = (BTC Reserve × BTC Price) / UP$ Supply
        """
        if self.total_ups_minted <= 0:
            return 1.0  # Genesis price
        return (self.total_btc * self.btc_usd_price) / self.total_ups_minted

    @property
    def ups_value_btc(self) -> float:
        """Current UP$ value in BTC."""
        if self.total_ups_minted <= 0:
            return 1.0 / self.genesis_ups_per_btc
        return self.total_btc / self.total_ups_minted

    def receive_btc(
        self,
        btc_amount: float,
        source: BTCSourceType,
        foundup_id: Optional[str] = None,
        human_id: Optional[str] = None,
        original_crypto: Optional[PaymentCrypto] = None,
        original_amount: Optional[float] = None,
    ) -> None:
        """Receive BTC into the reserve. One-way flow.

        This is the Hotel California - BTC enters, never leaves.
        """
        if btc_amount <= 0:
            return

        # Add to total
        self.total_btc += btc_amount

        # Track by source
        self.btc_by_source[source] = self.btc_by_source.get(source, 0.0) + btc_amount

        # Track by FoundUp if applicable
        if foundup_id:
            self.btc_by_foundup[foundup_id] = self.btc_by_foundup.get(foundup_id, 0.0) + btc_amount

        # Record inflow
        inflow = BTCInflow(
            source=source,
            btc_amount=btc_amount,
            usd_value=btc_amount * self.btc_usd_price,
            timestamp=datetime.now().isoformat(),
            foundup_id=foundup_id,
            human_id=human_id,
            original_crypto=original_crypto,
            original_amount=original_amount,
        )
        self.inflows.append(inflow)

        logger.info(
            f"[Reserve] +{btc_amount:.8f} BTC from {source.value} "
            f"(total: {self.total_btc:.8f} BTC = ${self.total_btc * self.btc_usd_price:,.2f})"
        )

    def receive_subscription_payment(
        self,
        usd_amount: float,
        human_id: str,
    ) -> float:
        """Convert subscription USD payment to BTC in reserve.

        Args:
            usd_amount: Subscription price in USD
            human_id: Subscriber

        Returns:
            BTC amount added to reserve
        """
        btc_amount = usd_amount / self.btc_usd_price
        self.receive_btc(
            btc_amount,
            BTCSourceType.SUBSCRIPTION,
            human_id=human_id,
            original_crypto=PaymentCrypto.USDC,  # Treat USD as USDC
            original_amount=usd_amount,
        )
        return btc_amount

    def receive_crypto_subscription(
        self,
        crypto: PaymentCrypto,
        amount: float,
        human_id: str,
    ) -> Tuple[float, bool]:
        """Receive subscription payment in any cryptocurrency.

        Pay with BTC, ETH, SOL, USDC, USDT, or UP$.
        All crypto converts to BTC. UP$ gets BURNED (strengthens currency).

        Args:
            crypto: Which cryptocurrency
            amount: Amount of that crypto
            human_id: Subscriber

        Returns:
            (btc_equivalent, was_ups_burned) tuple
        """
        if crypto == PaymentCrypto.UPS:
            # Special case: UP$ subscription BURNS the UP$
            return self.receive_ups_subscription(amount, human_id)

        # Convert crypto to BTC
        btc_amount = self.crypto_rates.get_btc_amount(crypto, amount)

        if btc_amount <= 0:
            logger.warning(f"[Reserve] Invalid crypto payment: {amount} {crypto.value}")
            return (0.0, False)

        self.receive_btc(
            btc_amount,
            BTCSourceType.SUBSCRIPTION,
            human_id=human_id,
            original_crypto=crypto,
            original_amount=amount,
        )

        logger.info(
            f"[Reserve] Subscription: {human_id} paid {amount:.4f} {crypto.value} "
            f"= {btc_amount:.8f} BTC"
        )
        return (btc_amount, False)

    def receive_ups_subscription(
        self,
        ups_amount: float,
        human_id: str,
    ) -> Tuple[float, bool]:
        """Receive subscription payment in UP$ - BURNS the UP$.

        Paying with UP$ is special:
        - UP$ gets burned (reduces supply)
        - Backing ratio IMPROVES (same BTC, less UP$)
        - This strengthens the currency for everyone

        Args:
            ups_amount: UP$ to burn for subscription
            human_id: Subscriber

        Returns:
            (btc_equivalent, was_ups_burned=True) tuple
        """
        # Calculate BTC equivalent at current UP$ value
        btc_equivalent = ups_amount * self.ups_value_btc

        # Burn the UP$ (reduce supply, BTC stays)
        self.total_ups_burned += ups_amount
        self.total_ups_minted -= ups_amount  # Reduce circulating supply

        # Track the burn (no BTC added, but track for analytics)
        self.btc_by_source[BTCSourceType.SUBSCRIPTION_UPS_BURN] = (
            self.btc_by_source.get(BTCSourceType.SUBSCRIPTION_UPS_BURN, 0.0) + btc_equivalent
        )

        # Record as special inflow (BTC equivalent, but actually a burn)
        inflow = BTCInflow(
            source=BTCSourceType.SUBSCRIPTION_UPS_BURN,
            btc_amount=0.0,  # No actual BTC added
            usd_value=ups_amount * self.ups_value_usd,
            timestamp=datetime.now().isoformat(),
            human_id=human_id,
            original_crypto=PaymentCrypto.UPS,
            original_amount=ups_amount,
        )
        self.inflows.append(inflow)

        logger.info(
            f"[Reserve] UP$ BURN: {human_id} paid {ups_amount:.2f} UP$ "
            f"(burned, new backing ratio: {self.backing_ratio:.2%})"
        )
        return (btc_equivalent, True)

    def process_demurrage(
        self,
        ups_decayed: float,
        human_id: str,
    ) -> float:
        """Process decayed UPS - burns supply, frees BTC capacity.

        HOTEL CALIFORNIA MODEL:
        - BTC is ALREADY in reserve (never leaves)
        - UPS decay = UPS destroyed = supply reduced
        - BTC backing is FREED (not added)
        - Freed capacity strengthens remaining UPS value

        This method:
        1. Burns the decayed UPS (reduces circulating supply)
        2. Returns the BTC capacity freed (for Network/Participation Pool routing)

        Args:
            ups_decayed: Amount of UPS that decayed
            human_id: Whose wallet decayed

        Returns:
            BTC capacity freed (NOT new BTC added - capacity for ecosystem use)
        """
        if ups_decayed <= 0:
            return 0.0

        # Calculate BTC capacity freed (not new BTC - capacity that was backing this UPS)
        btc_capacity_freed = ups_decayed / self.ups_per_btc

        # Burn the UPS (reduces supply, BTC stays locked)
        self.burn_ups(ups_decayed)

        # Track for analytics (but NOT as btc_received - just capacity freed)
        self.btc_by_source[BTCSourceType.DEMURRAGE] = (
            self.btc_by_source.get(BTCSourceType.DEMURRAGE, 0.0) + btc_capacity_freed
        )

        logger.info(
            f"[Reserve] Demurrage: {human_id} UPS burned {ups_decayed:.4f} "
            f"(capacity freed: {btc_capacity_freed:.8f} BTC equivalent, "
            f"new backing ratio: {self.backing_ratio:.2%})"
        )

        return btc_capacity_freed

    def receive_exit_fee(
        self,
        fee_ups: float,
        source: BTCSourceType,
        foundup_id: str,
        human_id: str,
    ) -> float:
        """Convert exit fee to BTC in reserve.

        Exit fees from F_i conversion go to BTC reserve.
        """
        btc_amount = fee_ups / self.ups_per_btc
        self.receive_btc(btc_amount, source, foundup_id=foundup_id, human_id=human_id)
        return btc_amount

    @property
    def ups_per_btc(self) -> float:
        """Current UP$ per BTC (floating rate).

        At genesis this equals genesis_ups_per_btc.
        As reserve grows relative to minted supply, this adjusts.
        """
        if self.total_btc <= 0 or self.total_ups_minted <= 0:
            return self.genesis_ups_per_btc
        return self.total_ups_minted / self.total_btc

    @property
    def ups_capacity(self) -> float:
        """Maximum UP$ that can be minted at genesis rate.

        Note: With floating UP$, this represents theoretical max if
        we used genesis conversion rate. Actual UP$ value floats.
        """
        return self.total_btc * self.genesis_ups_per_btc

    @property
    def ups_remaining(self) -> float:
        """UP$ that can still be minted at genesis rate."""
        return max(0.0, self.ups_capacity - self.total_ups_minted)

    @property
    def backing_ratio(self) -> float:
        """How much of minted UP$ is backed by BTC.

        With floating UP$, this is always 1.0 by definition
        (UP$ value adjusts to match backing).
        This metric is kept for monitoring reserve health.
        """
        if self.total_ups_minted == 0:
            return 1.0
        # In floating model, backing is always 100% by definition
        # But we track the ratio vs genesis rate for health monitoring
        return self.ups_capacity / self.total_ups_minted

    @property
    def reserve_usd_value(self) -> float:
        """Total USD value of BTC reserve."""
        return self.total_btc * self.btc_usd_price

    def mint_ups(self, amount: float) -> float:
        """Mint UP$ backed by BTC reserve.

        Returns:
            Actual amount minted (may be less if insufficient backing)
        """
        mintable = min(amount, self.ups_remaining)
        if mintable <= 0:
            logger.warning(f"[Reserve] Cannot mint {amount:.2f} UP$ - insufficient backing")
            return 0.0

        self.total_ups_minted += mintable
        logger.info(
            f"[Reserve] Minted {mintable:.2f} UP$ "
            f"(total: {self.total_ups_minted:.2f}, backing: {self.backing_ratio:.2%})"
        )
        return mintable

    def burn_ups(self, amount: float) -> None:
        """Burn UP$ (e.g., from demurrage or fees).

        The BTC backing stays in reserve - UP$ is destroyed.
        """
        self.total_ups_minted = max(0.0, self.total_ups_minted - amount)
        logger.info(
            f"[Reserve] Burned {amount:.2f} UP$ "
            f"(remaining: {self.total_ups_minted:.2f}, backing: {self.backing_ratio:.2%})"
        )

    def get_stats(self) -> Dict:
        """Get reserve statistics."""
        return {
            "total_btc": self.total_btc,
            "btc_usd_price": self.btc_usd_price,
            "reserve_usd_value": self.reserve_usd_value,
            "ups_minted": self.total_ups_minted,
            "ups_burned": self.total_ups_burned,
            "ups_circulating": self.total_ups_minted,  # After burns
            "ups_value_usd": self.ups_value_usd,
            "ups_value_btc": self.ups_value_btc,
            "backing_ratio_vs_genesis": self.backing_ratio,
            "btc_by_source": {k.value: v for k, v in self.btc_by_source.items()},
            "num_foundups_backed": len(self.btc_by_foundup),
            "total_inflows": len(self.inflows),
        }


# Global singleton for the BTC Reserve
_btc_reserve: Optional[BTCReserve] = None


def get_btc_reserve() -> BTCReserve:
    """Get the singleton BTC Reserve instance."""
    global _btc_reserve
    if _btc_reserve is None:
        _btc_reserve = BTCReserve()
    return _btc_reserve


def reset_btc_reserve() -> None:
    """Reset the BTC Reserve (for testing)."""
    global _btc_reserve
    _btc_reserve = None
