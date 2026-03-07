"""Operational-profit routing tests (agent work -> proxy UPS distribution)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import modules.foundups.simulator.mesa_model as mesa_model_module
from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.economics import (
    OperationalProfitPolicy,
    TokenEconomicsEngine,
)
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_operational_profit_routes_to_proxy_owner_not_agent_wallet() -> None:
    engine = TokenEconomicsEngine()
    engine.register_human("proxy_012", initial_ups=0.0)
    engine.register_agent("trader_0102", allocator_id="proxy_012")
    engine.register_foundup("f_trade")

    result = engine.distribute_operational_profit(
        foundup_id="f_trade",
        operator_agent_id="trader_0102",
        gross_profit_ups=100.0,
        operating_cost_ups=30.0,
    )

    assert result.proxy_owner_id == "proxy_012"
    assert result.net_profit_ups == pytest.approx(70.0, abs=1e-9)
    assert result.proxy_distribution_ups == pytest.approx(49.0, abs=1e-9)
    assert result.foundup_treasury_ups == pytest.approx(14.0, abs=1e-9)
    assert result.network_pool_ups == pytest.approx(7.0, abs=1e-9)
    assert engine.human_accounts["proxy_012"].ups_balance == pytest.approx(49.0, abs=1e-9)
    assert engine.agent_wallets["trader_0102"].ups_balance == pytest.approx(0.0, abs=1e-9)
    assert engine.foundup_pools["f_trade"].ups_treasury == pytest.approx(14.0, abs=1e-9)


def test_operational_profit_supports_proxy_stake_and_exit_actions() -> None:
    engine = TokenEconomicsEngine()
    engine.register_human("proxy_012", initial_ups=0.0)
    engine.register_agent("trader_0102", allocator_id="proxy_012")
    engine.register_foundup("f_trade")

    result = engine.distribute_operational_profit(
        foundup_id="f_trade",
        operator_agent_id="trader_0102",
        gross_profit_ups=200.0,
        operating_cost_ups=50.0,
        policy=OperationalProfitPolicy(
            proxy_share=0.70,
            foundup_treasury_share=0.20,
            network_pool_share=0.10,
            proxy_auto_stake_ratio=0.50,
            proxy_auto_exit_ratio=0.25,
            proxy_exit_fee_rate=0.10,
        ),
    )

    # Net = 150. Proxy lane = 105.
    assert result.net_profit_ups == pytest.approx(150.0, abs=1e-9)
    assert result.proxy_distribution_ups == pytest.approx(105.0, abs=1e-9)
    assert result.proxy_staked_ups == pytest.approx(52.5, abs=1e-9)
    assert result.proxy_exit_gross_ups == pytest.approx(13.125, abs=1e-9)
    assert result.proxy_exit_fee_ups == pytest.approx(1.3125, abs=1e-9)
    assert result.proxy_hold_ups == pytest.approx(39.375, abs=1e-9)
    assert engine.human_accounts["proxy_012"].ups_balance == pytest.approx(39.375, abs=1e-9)


def test_cabr_task_distribution_credits_proxy_owner_not_assignee(tmp_path) -> None:
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=0,
            seed=5,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )

    ok, msg, foundup_id = model._fam_bridge.create_foundup(
        name="Proxy Routing",
        owner_id="founder_0",
        token_symbol="PROX",
    )
    assert ok, msg
    assert foundup_id is not None
    model._demurrage.update_pavs_treasury_balance(10_000.0)

    model.token_economics.register_agent("trader_0102", allocator_id="proxy_012")
    task = SimpleNamespace(
        foundup_id=foundup_id,
        assignee_id="trader_0102",
        reward_amount=120.0,
        task_id="task_proxy",
    )
    model._route_cabr_ups_for_task(task)

    proxy_account = model.token_economics.human_accounts.get("proxy_012")
    assert proxy_account is not None
    assert proxy_account.ups_balance > 0
    assignee_account = model.token_economics.human_accounts.get("trader_0102")
    assert assignee_account is None or assignee_account.ups_balance == pytest.approx(0.0, abs=1e-9)


def test_trading_foundup_emits_operational_profit_distribution_event(tmp_path, monkeypatch) -> None:
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=0,
            seed=9,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )

    ok, msg, foundup_id = model._fam_bridge.create_foundup(
        name="TradingBot Alpha",
        owner_id="founder_0",
        token_symbol="TRAD",
    )
    assert ok, msg
    assert foundup_id is not None
    model._sync_token_econ_foundup_pools()

    monkeypatch.setattr(mesa_model_module.random, "random", lambda: 0.0)
    monkeypatch.setattr(mesa_model_module.random, "uniform", lambda a, b: a)

    model._simulate_autonomous_trading_profits()

    events = model.event_bus.get_events_by_type("operational_profit_distributed", limit=10)
    assert events
    payload = events[0].payload
    assert payload["foundup_id"] == foundup_id
    assert payload["net_profit_ups"] > 0

