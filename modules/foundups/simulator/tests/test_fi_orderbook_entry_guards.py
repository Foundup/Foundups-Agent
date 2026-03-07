"""Entry-side anti-manipulation tests for F_i order books."""

from __future__ import annotations

from modules.foundups.simulator.economics.fi_orderbook import (
    EntryProtectionConfig,
    FiOrderBook,
    OrderStatus,
)


def test_buy_rejected_when_notional_exceeds_low_adoption_cap() -> None:
    config = EntryProtectionConfig(
        base_max_order_btc=0.001,  # 100k sats baseline
        max_liquidity_boost=0.0,  # keep cap deterministic for test
    )
    book = FiOrderBook(foundup_id="f_low_adoption", entry_protection_config=config)
    book.update_market_context(adoption_rate=0.05, liquidity_hint_ups=0.0)

    # 100k UPS order notional vs 50k UPS cap at 5% adoption (0.5x scale).
    order, trades = book.place_buy_order(
        human_id="buyer_1",
        price=1000.0,
        quantity=100.0,
    )

    assert order.status == OrderStatus.CANCELLED
    assert order.rejection_reason is not None
    assert order.rejection_reason.startswith("entry_notional_limit_exceeded")
    assert trades == []
    assert book.rejected_buy_orders == 1
    assert len(book.buy_orders) == 0


def test_buy_allowed_when_adoption_matures() -> None:
    config = EntryProtectionConfig(
        base_max_order_btc=0.001,  # 100k sats baseline
        max_liquidity_boost=0.0,
    )
    book = FiOrderBook(foundup_id="f_mature", entry_protection_config=config)
    book.update_market_context(adoption_rate=0.95, liquidity_hint_ups=0.0)

    # Same 100k UPS notional should pass at high adoption (9.5x scale).
    order, trades = book.place_buy_order(
        human_id="buyer_1",
        price=1000.0,
        quantity=100.0,
    )

    assert order.status == OrderStatus.OPEN
    assert order.rejection_reason is None
    assert trades == []
    assert book.rejected_buy_orders == 0
    assert len(book.buy_orders) == 1


def test_depth_impact_guard_blocks_single_order_whale_sweep() -> None:
    config = EntryProtectionConfig(
        base_max_order_btc=10.0,  # disable notional cap as limiting factor
        min_depth_for_impact_guard_ups=100.0,
        max_single_order_share_of_opposing_depth=0.25,
    )
    book = FiOrderBook(foundup_id="f_depth_guard", entry_protection_config=config)
    book.update_market_context(adoption_rate=1.0, liquidity_hint_ups=0.0)

    # Seed opposing depth: 1000 UPS total ask side.
    sell_order, _ = book.place_sell_order(
        human_id="seller_1",
        price=10.0,
        quantity=100.0,
    )
    assert sell_order.status == OrderStatus.OPEN

    # 400 UPS buy order exceeds 25% of opposing depth (cap = 250 UPS).
    whale_buy, trades = book.place_buy_order(
        human_id="buyer_whale",
        price=10.0,
        quantity=40.0,
    )

    assert whale_buy.status == OrderStatus.CANCELLED
    assert whale_buy.rejection_reason is not None
    assert whale_buy.rejection_reason.startswith("depth_impact_limit_exceeded")
    assert trades == []
    assert book.rejected_buy_orders == 1
