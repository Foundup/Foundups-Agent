"""F_0 investor program + MVP offering flow tests."""

from __future__ import annotations

from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_proto_foundup_accepts_f0_bid_and_treasury_injection(tmp_path) -> None:
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=0,
            seed=21,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )
    bridge = model._fam_bridge

    ok, msg, foundup_id = bridge.create_foundup(
        name="Proto Target",
        owner_id="founder_0",
        token_symbol="PT",
    )
    assert ok, msg
    assert foundup_id is not None

    ok, msg, task_id = bridge.create_task(
        foundup_id=foundup_id,
        title="Deliver prototype",
        description="Ship a working prototype",
        reward_amount=100,
        creator_id="founder_0",
    )
    assert ok, msg
    assert task_id is not None

    ok, msg = bridge.claim_task(task_id, "user_000")
    assert ok, msg

    # claimed -> submitted -> verified -> paid
    for _ in range(4):
        model.step()

    state = model.state_store.get_state()
    assert state.foundups[foundup_id].lifecycle_stage == "Proto"

    ok, msg, _ = bridge.accrue_investor_terms("f0_investor_a", terms=5)
    assert ok, msg
    ok, msg, _ = bridge.accrue_investor_terms("f0_investor_b", terms=5)
    assert ok, msg

    ok, msg, _ = bridge.place_mvp_bid(foundup_id, "f0_investor_a", bid_ups=350)
    assert ok, msg
    ok, msg, _ = bridge.place_mvp_bid(foundup_id, "f0_investor_b", bid_ups=450)
    assert ok, msg

    ok, msg, allocations = bridge.resolve_mvp_offering(
        foundup_id=foundup_id,
        actor_id="treasury_0",
        token_amount=1_000,
        top_n=1,
    )
    assert ok, msg
    assert allocations is not None
    assert len(allocations) == 1
    assert allocations[0]["investor_id"] == "f0_investor_b"
    assert allocations[0]["bid_ups"] == 450

    post_state = model.state_store.get_state()
    tile = post_state.foundups[foundup_id]
    assert tile.mvp_bid_count >= 2
    assert tile.mvp_treasury_injection_ups == 450

    resolved_events = model.event_bus.get_events_by_type("mvp_offering_resolved", limit=20)
    assert len(resolved_events) >= 1
    assert resolved_events[-1].payload["total_injection_ups"] == 450
