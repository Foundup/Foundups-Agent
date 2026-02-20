"""Runtime wiring tests for 012 allocation and pAVS treasury telemetry."""

from __future__ import annotations

from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel
import modules.foundups.simulator.mesa_model as mesa_model_module


def test_012_allocation_updates_state_and_emits_events(tmp_path, monkeypatch) -> None:
    """Allocation engine should execute against live pools and emit telemetry."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=1,
            seed=11,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )

    # Ensure a FoundUp exists and token pool is synced for allocation routing.
    ok, msg, foundup_id = model._fam_bridge.create_foundup(
        name="Allocation Runtime",
        owner_id="founder_0",
        token_symbol="ALOC",
    )
    assert ok, msg
    assert foundup_id is not None
    model._sync_token_econ_foundup_pools()

    account = model.token_economics.human_accounts["user_000"]
    assert account.ups_balance > 0

    # Force allocation branch execution deterministically.
    monkeypatch.setattr(mesa_model_module.random, "random", lambda: 0.0)
    model._simulate_012_allocations()

    assert model.allocation_engine.allocation_count > 0
    assert model.state_store.get_state().total_stakes > 0

    allocation_events = model.event_bus.get_events_by_type("ups_allocation_executed", limit=20)
    result_events = model.event_bus.get_events_by_type("ups_allocation_result", limit=20)
    assert allocation_events
    assert result_events
    assert any(evt.foundup_id == foundup_id for evt in result_events)


def test_demurrage_emits_treasury_separation_events(tmp_path) -> None:
    """Demurrage cycle should emit pAVS/network separation telemetry."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=1,
            seed=13,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )

    # Force one demurrage cycle.
    model._apply_demurrage_cycle()

    demurrage_events = model.event_bus.get_events_by_type("demurrage_cycle_completed", limit=10)
    treasury_events = model.event_bus.get_events_by_type("pavs_treasury_updated", limit=10)
    snapshot_events = model.event_bus.get_events_by_type("treasury_separation_snapshot", limit=10)

    assert demurrage_events
    assert treasury_events
    assert snapshot_events

    stats = model.get_stats()
    assert stats["pavs_treasury_ups"] >= 0
    assert stats["network_pool_ups"] >= 0
