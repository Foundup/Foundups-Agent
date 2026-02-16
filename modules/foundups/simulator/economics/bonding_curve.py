"""Bonding Curve - Guaranteed Liquidity for F_i Tokens.

Replaces orderbook with automated market maker.

Advantages over orderbook:
1. GUARANTEED liquidity - always a buyer/seller
2. No counterparty needed
3. Automatic price discovery
4. No whale manipulation (slippage scales with size)
5. Fair for all participants

Formula (Bancor-style):
  price = reserve / (supply * ratio)
  buy: more buys → higher price
  sell: more sells → lower price

This prevents the illiquidity problem where users can't exit.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class BondingCurveConfig:
    """Configuration for bonding curve."""

    # Reserve ratio (Bancor-style)
    # 0.5 = 50% of market cap held in reserve
    # Higher = more stable price, lower = more volatile
    reserve_ratio: float = 0.5

    # Trading fee (goes to BTC Reserve)
    buy_fee: float = 0.01  # 1% on buys
    sell_fee: float = 0.02  # 2% on sells (discourages extraction)

    # Minimum reserve to prevent division by zero
    min_reserve: float = 100.0

    # Maximum slippage warning
    slippage_warning: float = 0.05  # Warn if > 5% slippage


@dataclass
class FiBondingCurve:
    """Bonding curve for a single FoundUp's F_i tokens.

    Implements Bancor-style automated market maker.
    Guaranteed liquidity at all price levels.
    """

    foundup_id: str
    config: BondingCurveConfig = field(default_factory=BondingCurveConfig)

    # Reserves
    ups_reserve: float = 0.0  # UP$ held in curve
    fi_supply: float = 0.0  # Total F_i minted by curve

    # Statistics
    total_buys: int = 0
    total_sells: int = 0
    total_buy_volume_ups: float = 0.0
    total_sell_volume_ups: float = 0.0
    total_fees_collected: float = 0.0

    def initialize(self, initial_ups: float, initial_price: float = 1.0) -> float:
        """Initialize curve with starting liquidity.

        Args:
            initial_ups: UP$ to seed the reserve
            initial_price: Starting price of F_i in UP$

        Returns:
            Initial F_i supply created
        """
        self.ups_reserve = initial_ups

        # Calculate initial supply from price and reserve ratio
        # price = reserve / (supply * ratio)
        # supply = reserve / (price * ratio)
        self.fi_supply = initial_ups / (initial_price * self.config.reserve_ratio)

        logger.info(
            f"[BondingCurve:{self.foundup_id}] Initialized: "
            f"{initial_ups:.2f} UP$ reserve, {self.fi_supply:.2f} F_i supply, "
            f"price={self.get_spot_price():.4f} UP$/F_i"
        )
        return self.fi_supply

    def get_spot_price(self) -> float:
        """Get current spot price of F_i in UP$.

        Formula: price = reserve / (supply * ratio)
        """
        if self.fi_supply <= 0:
            return 1.0  # Genesis price

        return self.ups_reserve / (self.fi_supply * self.config.reserve_ratio)

    def get_market_cap(self) -> float:
        """Get current market cap in UP$."""
        return self.fi_supply * self.get_spot_price()

    def calculate_buy_return(self, ups_amount: float) -> Tuple[float, float, float]:
        """Calculate F_i received for given UP$ input.

        Uses Bancor formula for continuous token model.

        Args:
            ups_amount: UP$ to spend

        Returns:
            (fi_out, fee, effective_price) tuple
        """
        if ups_amount <= 0:
            return (0.0, 0.0, 0.0)

        # Apply buy fee
        fee = ups_amount * self.config.buy_fee
        ups_after_fee = ups_amount - fee

        # Bancor formula for purchase
        # tokens_out = supply * ((1 + amount/reserve)^ratio - 1)
        if self.ups_reserve < self.config.min_reserve:
            # Bootstrap case: linear pricing
            fi_out = ups_after_fee / 1.0  # 1:1 at genesis
        else:
            ratio = self.config.reserve_ratio
            fi_out = self.fi_supply * (
                math.pow(1 + ups_after_fee / self.ups_reserve, ratio) - 1
            )

        effective_price = ups_amount / fi_out if fi_out > 0 else 0
        return (fi_out, fee, effective_price)

    def calculate_sell_return(self, fi_amount: float) -> Tuple[float, float, float]:
        """Calculate UP$ received for given F_i input.

        Args:
            fi_amount: F_i to sell

        Returns:
            (ups_out, fee, effective_price) tuple
        """
        if fi_amount <= 0 or fi_amount > self.fi_supply:
            return (0.0, 0.0, 0.0)

        # Bancor formula for sale
        # ups_out = reserve * (1 - (1 - amount/supply)^(1/ratio))
        ratio = self.config.reserve_ratio
        ups_before_fee = self.ups_reserve * (
            1 - math.pow(1 - fi_amount / self.fi_supply, 1 / ratio)
        )

        # Apply sell fee
        fee = ups_before_fee * self.config.sell_fee
        ups_out = ups_before_fee - fee

        effective_price = ups_out / fi_amount if fi_amount > 0 else 0
        return (ups_out, fee, effective_price)

    def get_slippage(self, ups_amount: float, is_buy: bool) -> float:
        """Calculate expected slippage for a trade.

        Returns:
            Slippage as decimal (0.05 = 5%)
        """
        spot = self.get_spot_price()

        if is_buy:
            _, _, effective = self.calculate_buy_return(ups_amount)
        else:
            fi_amount = ups_amount / spot  # Approximate
            _, _, effective = self.calculate_sell_return(fi_amount)

        if spot <= 0:
            return 0.0

        return abs(effective - spot) / spot

    def buy(self, ups_amount: float, buyer_id: str) -> Tuple[float, float]:
        """Execute a buy order.

        Args:
            ups_amount: UP$ to spend
            buyer_id: Who is buying

        Returns:
            (fi_received, fee_paid) tuple
        """
        fi_out, fee, effective_price = self.calculate_buy_return(ups_amount)

        if fi_out <= 0:
            logger.warning(f"[BondingCurve:{self.foundup_id}] Buy failed: 0 F_i output")
            return (0.0, 0.0)

        # Check slippage
        slippage = self.get_slippage(ups_amount, is_buy=True)
        if slippage > self.config.slippage_warning:
            logger.warning(
                f"[BondingCurve:{self.foundup_id}] High slippage on buy: {slippage*100:.1f}%"
            )

        # Execute trade
        self.ups_reserve += (ups_amount - fee)
        self.fi_supply += fi_out

        # Statistics
        self.total_buys += 1
        self.total_buy_volume_ups += ups_amount
        self.total_fees_collected += fee

        logger.info(
            f"[BondingCurve:{self.foundup_id}] BUY: {buyer_id} spent {ups_amount:.2f} UP$ "
            f"-> {fi_out:.2f} F_i @ {effective_price:.4f} (fee: {fee:.2f})"
        )

        return (fi_out, fee)

    def sell(self, fi_amount: float, seller_id: str) -> Tuple[float, float]:
        """Execute a sell order.

        Args:
            fi_amount: F_i to sell
            seller_id: Who is selling

        Returns:
            (ups_received, fee_paid) tuple
        """
        ups_out, fee, effective_price = self.calculate_sell_return(fi_amount)

        if ups_out <= 0:
            logger.warning(f"[BondingCurve:{self.foundup_id}] Sell failed: 0 UP$ output")
            return (0.0, 0.0)

        if ups_out > self.ups_reserve:
            logger.warning(f"[BondingCurve:{self.foundup_id}] Insufficient reserve for sell")
            return (0.0, 0.0)

        # Execute trade
        self.ups_reserve -= (ups_out + fee)  # Fee comes from reserve
        self.fi_supply -= fi_amount

        # Statistics
        self.total_sells += 1
        self.total_sell_volume_ups += ups_out
        self.total_fees_collected += fee

        logger.info(
            f"[BondingCurve:{self.foundup_id}] SELL: {seller_id} sold {fi_amount:.2f} F_i "
            f"-> {ups_out:.2f} UP$ @ {effective_price:.4f} (fee: {fee:.2f})"
        )

        return (ups_out, fee)

    def get_stats(self) -> Dict:
        """Get bonding curve statistics."""
        return {
            "foundup_id": self.foundup_id,
            "ups_reserve": self.ups_reserve,
            "fi_supply": self.fi_supply,
            "spot_price": self.get_spot_price(),
            "market_cap": self.get_market_cap(),
            "reserve_ratio": self.config.reserve_ratio,
            "total_buys": self.total_buys,
            "total_sells": self.total_sells,
            "buy_volume": self.total_buy_volume_ups,
            "sell_volume": self.total_sell_volume_ups,
            "fees_collected": self.total_fees_collected,
        }


class BondingCurveManager:
    """Manages bonding curves for all FoundUps."""

    def __init__(self, config: Optional[BondingCurveConfig] = None):
        self.config = config or BondingCurveConfig()
        self.curves: Dict[str, FiBondingCurve] = {}

    def get_or_create_curve(
        self,
        foundup_id: str,
        initial_ups: float = 1000.0,
        initial_price: float = 1.0,
    ) -> FiBondingCurve:
        """Get or create a bonding curve for a FoundUp."""
        if foundup_id not in self.curves:
            curve = FiBondingCurve(foundup_id=foundup_id, config=self.config)
            curve.initialize(initial_ups, initial_price)
            self.curves[foundup_id] = curve
        return self.curves[foundup_id]

    def buy(
        self,
        foundup_id: str,
        ups_amount: float,
        buyer_id: str,
    ) -> Tuple[float, float]:
        """Buy F_i tokens from a curve."""
        curve = self.curves.get(foundup_id)
        if not curve:
            curve = self.get_or_create_curve(foundup_id)
        return curve.buy(ups_amount, buyer_id)

    def sell(
        self,
        foundup_id: str,
        fi_amount: float,
        seller_id: str,
    ) -> Tuple[float, float]:
        """Sell F_i tokens to a curve."""
        curve = self.curves.get(foundup_id)
        if not curve:
            logger.warning(f"[BondingCurveManager] No curve for {foundup_id}")
            return (0.0, 0.0)
        return curve.sell(fi_amount, seller_id)

    def get_total_fees(self) -> float:
        """Get total fees across all curves."""
        return sum(c.total_fees_collected for c in self.curves.values())

    def get_all_stats(self) -> Dict:
        """Get statistics for all curves."""
        return {
            "num_curves": len(self.curves),
            "total_fees": self.get_total_fees(),
            "curves": {fid: c.get_stats() for fid, c in self.curves.items()},
        }
