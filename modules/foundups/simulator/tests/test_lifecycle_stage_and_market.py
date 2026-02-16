"""Lifecycle stage and market simulation tests."""

from __future__ import annotations

from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_lifecycle_stage_progression_poc_proto_mvp(tmp_path) -> None:
    """FoundUp should progress PoC -> Proto -> MVP based on delivery + customers."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=0,
            seed=17,
            agent_action_probability=1.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )
    bridge = model._fam_bridge

    ok, msg, foundup_id = bridge.create_foundup(
        name="Lifecycle Stage",
        owner_id="founder_0",
        token_symbol="STG",
    )
    assert ok, msg
    assert foundup_id is not None

    state = model.state_store.get_state()
    assert state.foundups[foundup_id].lifecycle_stage == "PoC"

    ok, msg, task_id = bridge.create_task(
        foundup_id=foundup_id,
        title="Build V1",
        description="Ship first release",
        reward_amount=50,
        creator_id="founder_0",
    )
    assert ok, msg
    assert task_id is not None

    ok, msg = bridge.claim_task(task_id, "user_000")
    assert ok, msg

    # 4 steps moves claimed -> submitted -> verified -> paid.
    for _ in range(4):
        model.step()

    state = model.state_store.get_state()
    assert state.foundups[foundup_id].lifecycle_stage == "Proto"
    assert state.foundups[foundup_id].tasks_completed >= 1

    # Customer arrival upgrades Proto -> MVP.
    model.state_store.record_stake("user_000", foundup_id, 25)
    state = model.state_store.get_state()
    assert state.foundups[foundup_id].customer_count >= 1
    assert state.foundups[foundup_id].lifecycle_stage == "MVP"
    assert state.foundups[foundup_id].beta_launched is True


def test_market_activity_emits_dex_and_f0_seed_events(tmp_path) -> None:
    """Simulator should emit DEX trades plus F_0-seeded investor event."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=3,
            seed=42,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )
    bridge = model._fam_bridge

    ok, msg, foundup_id = bridge.create_foundup(
        name="Market Test",
        owner_id="founder_0",
        token_symbol="MKT",
    )
    assert ok, msg
    assert foundup_id is not None

    for _ in range(120):
        model.step()

    state = model.state_store.get_state()
    assert state.total_dex_trades > 0
    assert state.total_dex_volume_ups > 0.0

    dex_events = model.event_bus.get_events_by_type("fi_trade_executed", limit=500)
    investor_events = model.event_bus.get_events_by_type("investor_funding_received", limit=500)
    assert len(dex_events) > 0
    assert len(investor_events) > 0
    assert all(evt.foundup_id == "F_0" for evt in investor_events)
