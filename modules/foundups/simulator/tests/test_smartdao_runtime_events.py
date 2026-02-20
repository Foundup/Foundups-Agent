"""Runtime wiring tests for SmartDAO and phase-command event emitters."""

from __future__ import annotations

from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_smartdao_emergence_emits_with_phase_command(tmp_path) -> None:
    """Crossing F0->F1 thresholds should emit emergence + phase command."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=10,
            seed=7,
            agent_action_probability=0.0,
        ),
        fam_daemon=daemon,
    )

    ok, msg, foundup_id = model._fam_bridge.create_foundup(
        name="Emergence",
        owner_id="founder_0",
        token_symbol="EMRG",
    )
    assert ok, msg
    assert foundup_id is not None

    model._sync_token_econ_foundup_pools()
    tile = model.state_store.get_state().foundups[foundup_id]
    tile.customer_count = 2  # 2 / 10 users = 20% adoption >= 16% threshold
    tile.tasks_completed = 9  # Active-agent heuristic pushes above F1 floor
    model._token_econ_engine.foundup_pools[foundup_id].ups_treasury = 100_000_000

    model._tick = 50
    model._process_smartdao_epoch()

    emergence = model.event_bus.get_events_by_type("smartdao_emergence", limit=10)
    escalations = model.event_bus.get_events_by_type("tier_escalation", limit=10)
    phase = model.event_bus.get_events_by_type("phase_command", limit=10)

    assert emergence
    assert escalations
    assert phase
    assert emergence[-1].foundup_id == foundup_id
    assert emergence[-1].payload["new_tier"] == "F1_OPO"
    assert phase[-1].payload["target_phase"] == "CELEBRATE"


def test_smartdao_autonomy_and_cross_dao_funding_emit(tmp_path) -> None:
    """F2+ promotion should emit autonomy and seed a lower-tier DAO."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=100,
            seed=11,
            agent_action_probability=0.0,
        ),
        fam_daemon=daemon,
    )

    ok_a, msg_a, donor_id = model._fam_bridge.create_foundup(
        name="Donor",
        owner_id="founder_0",
        token_symbol="DNR",
    )
    ok_b, msg_b, receiver_id = model._fam_bridge.create_foundup(
        name="Receiver",
        owner_id="founder_1",
        token_symbol="RCV",
    )
    assert ok_a, msg_a
    assert ok_b, msg_b
    assert donor_id is not None
    assert receiver_id is not None

    model._sync_token_econ_foundup_pools()
    state = model.state_store.get_state()

    donor_tile = state.foundups[donor_id]
    donor_tile.customer_count = 60
    donor_tile.tasks_completed = 40
    model._token_econ_engine.foundup_pools[donor_id].ups_treasury = 1_500_000_000

    receiver_tile = state.foundups[receiver_id]
    receiver_tile.customer_count = 0
    receiver_tile.tasks_completed = 0
    model._token_econ_engine.foundup_pools[receiver_id].ups_treasury = 10_000

    # Epoch 1: donor crosses into F1.
    model._tick = 50
    model._process_smartdao_epoch()
    # Epoch 2: donor crosses into F2, autonomy/cross-funding can emit.
    model._tick = 100
    model._process_smartdao_epoch()

    autonomy = model.event_bus.get_events_by_type("treasury_autonomy", limit=10)
    funding = model.event_bus.get_events_by_type("cross_dao_funding", limit=10)

    assert autonomy
    assert funding
    assert autonomy[-1].foundup_id == donor_id
    assert autonomy[-1].payload["tier"] in {"F2_GROWTH", "F3_INFRA", "F4_MEGA", "F5_SYSTEMIC"}
    assert funding[-1].payload["source_dao"] == donor_id
    assert funding[-1].payload["target_dao"] == receiver_id
    assert funding[-1].payload["amount"] > 0
