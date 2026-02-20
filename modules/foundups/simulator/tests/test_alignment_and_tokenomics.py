"""Simulator alignment and tokenomics math validation tests."""

from __future__ import annotations

import pytest

from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.economics import (
    BondingCurveManager,
    InvestorPool,
    TokenEconomicsEngine,
    adoption_curve,
)
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_shared_daemon_drives_state_store_updates(tmp_path) -> None:
    """FoundUp events emitted by bridge must be visible in simulator state."""
    daemon = FAMDaemon(
        data_dir=tmp_path,
        heartbeat_interval_sec=60.0,
        auto_start=False,
    )
    config = SimulatorConfig(
        num_founder_agents=1,
        num_user_agents=0,
        seed=7,
        agent_action_probability=1.0,
        agent_cooldown_ticks=0,
        foundup_creation_cost=100,
    )
    model = FoundUpsModel(config=config, fam_daemon=daemon)
    for _ in range(12):
        model.step()

    state = model.state_store.get_state()
    created_events = model.event_bus.get_events_by_type("foundup_created", limit=20)

    assert len(created_events) > 0
    assert state.total_foundups > 0


def test_adoption_curve_bounds() -> None:
    assert adoption_curve(0.0) == pytest.approx(0.0, abs=1e-12)
    assert adoption_curve(1.0) == pytest.approx(1.0, abs=1e-12)
    assert 0.0 <= adoption_curve(0.5) <= 1.0


def test_foundup_mint_respects_available_supply_cap() -> None:
    engine = TokenEconomicsEngine()
    engine.register_human("h1", initial_ups=1000.0)
    engine.register_agent("a1", "h1")
    pool = engine.register_foundup("f1")
    pool.update_adoption(users=1500, revenue_ups=150000.0, work_completed=15000.0, milestone=True)

    minted_total = 0.0
    for _ in range(200):
        minted_total += pool.mint_for_work(1_000_000.0, "a1")

    assert minted_total == pytest.approx(pool.available_supply, rel=1e-9, abs=1e-6)
    assert minted_total <= pool.available_supply + 1e-6
    assert pool.remaining_mintable == pytest.approx(0.0, abs=1e-6)


def test_staking_roundtrip_fee_math() -> None:
    engine = TokenEconomicsEngine()
    engine.register_human("h1", initial_ups=1000.0)
    engine.register_foundup("f1")

    fi_received, entry_fee = engine.human_stakes_ups("h1", "f1", 200.0)
    ups_back, exit_fee = engine.human_unstakes_fi("h1", "f1", fi_received)

    assert fi_received == pytest.approx(194.0, abs=1e-9)  # 3% entry fee
    assert entry_fee == pytest.approx(6.0, abs=1e-9)
    assert ups_back == pytest.approx(184.3, abs=1e-9)  # 5% unstake fee on 194
    assert exit_fee == pytest.approx(9.7, abs=1e-9)
    assert 200.0 - ups_back == pytest.approx(15.7, abs=1e-9)


def test_bonding_curve_monotonic_price_direction() -> None:
    manager = BondingCurveManager()
    curve = manager.get_or_create_curve("f_curve", initial_ups=1000.0, initial_price=1.0)

    p0 = curve.get_spot_price()
    fi_out, _ = curve.buy(100.0, "buyer_1")
    p1 = curve.get_spot_price()
    curve.sell(fi_out * 0.2, "seller_1")
    p2 = curve.get_spot_price()

    assert p1 > p0
    assert p2 < p1


def test_investor_pool_early_entry_advantage() -> None:
    pool = InvestorPool()
    first_tokens, _ = pool.invest_btc("seed", 1.0)
    second_tokens, _ = pool.invest_btc("early", 1.0)

    assert first_tokens > second_tokens
    seed_returns = pool.get_investor_returns("seed")
    assert seed_returns["price_return_multiple"] > 1.0
