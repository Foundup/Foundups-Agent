"""Hardening tests for Full Tide fee + support wiring."""

from __future__ import annotations

from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.economics.fee_revenue_tracker import FeeRevenueTracker
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_fee_collected_dedupe_allows_multiple_same_tick_sources(tmp_path) -> None:
    """Different fee source refs in the same tick must not collapse."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)

    payload_base = {
        "fee_type": "dex_trade",
        "foundup_id": "f_1",
        "amount_sats": 20,
        "volume_sats": 1000,
        "tick": 42,
        "distribution": {"fi_treasury": 10, "network_pool": 6, "pavs_treasury": 4, "btc_reserve": 0},
    }

    ok1, msg1 = daemon.emit(
        event_type="fee_collected",
        payload={**payload_base, "source_ref": "trade_a"},
        actor_id="fee_tracker",
        foundup_id="f_1",
    )
    ok2, msg2 = daemon.emit(
        event_type="fee_collected",
        payload={**payload_base, "source_ref": "trade_b"},
        actor_id="fee_tracker",
        foundup_id="f_1",
    )

    assert ok1, msg1
    assert ok2, msg2
    events = daemon.query_events(event_type="fee_collected", limit=10)
    assert len(events) == 2


def test_network_pool_delta_sync_uses_new_fees_only(tmp_path) -> None:
    """Fee network inflows should be synced once and not double-counted."""
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

    initial_network = model._tide_engine.get_network_pool()

    # 1,000,000 sats volume => 20,000 fee => 6,000 network split.
    model._tick = 1
    model._record_fee_from_trade("f_1", 1_000_000, source_ref="trade_1")
    assert model._fee_tracker.get_ecosystem_state().network_pool_sats == 6000

    model._tick = 100
    model._process_tide_epoch()
    assert model._tide_engine.get_network_pool() == initial_network + 6000
    assert model._network_pool_fees_synced_sats == 6000

    # No new fees; another epoch should not add more network fees.
    model._tick = 200
    model._process_tide_epoch()
    assert model._tide_engine.get_network_pool() == initial_network + 6000


def test_tide_support_received_event_emits_for_critical_foundup(tmp_path) -> None:
    """Critical FoundUp should receive support and emit both tide event names."""
    daemon = FAMDaemon(data_dir=tmp_path, heartbeat_interval_sec=60.0, auto_start=False)
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=0,
            seed=33,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        ),
        fam_daemon=daemon,
    )

    ok, msg, foundup_id = model._fam_bridge.create_foundup(
        name="Critical FoundUp",
        owner_id="founder_0",
        token_symbol="CRIT",
    )
    assert ok, msg
    assert foundup_id is not None

    # Seed some network pool inflow from fee tracker and keep FoundUp treasury low.
    model._tick = 1
    model._record_fee_from_trade(foundup_id, 100_000_000, source_ref="seed_trade")

    model._tick = 100
    model._process_tide_epoch()

    tide_in = model.event_bus.get_events_by_type("tide_in", limit=20)
    tide_support = model.event_bus.get_events_by_type("tide_support_received", limit=20)
    assert tide_in
    assert tide_support
    assert any(evt.foundup_id == foundup_id for evt in tide_in)
    assert any(evt.foundup_id == foundup_id for evt in tide_support)


def test_sustainability_metrics_use_conservative_capture_gate() -> None:
    """Conservative gate should use pAVS capture, not gross fee flow."""
    tracker = FeeRevenueTracker()
    for tick in range(1, 11):
        tracker.record_dex_trade(
            tick=tick,
            foundup_id="f_1",
            volume_sats=1_000_000,
            source_ref=f"trade_{tick}",
        )

    metrics = tracker.get_sustainability_metrics()
    assert metrics["gross_daily_revenue_btc"] > 0
    assert metrics["daily_revenue_btc"] > 0
    assert metrics["gross_daily_revenue_btc"] >= metrics["daily_revenue_btc"]
    assert metrics["protocol_capture_daily_btc"] >= metrics["daily_revenue_btc"]


def test_sustainability_requires_min_sample_window() -> None:
    """Self-sustaining milestone stays gated until sample window is mature."""
    tracker = FeeRevenueTracker()
    # High volume but short window + low foundup count => raw true, gated false.
    for tick in range(1, 11):
        tracker.record_dex_trade(
            tick=tick,
            foundup_id="f_1",
            volume_sats=500_000_000,  # Large volume to force raw ratio > 1
            source_ref=f"trade_{tick}",
        )

    metrics = tracker.get_sustainability_metrics()
    assert metrics["is_self_sustaining_raw"] is True
    assert metrics["has_min_sample_window"] is False
    assert metrics["is_self_sustaining"] is False


def test_sustainability_claim_requires_downside_pass() -> None:
    """Claim gate should track downside p10 ratio, not only base gate."""
    tracker = FeeRevenueTracker()

    # Build mature sample window + enough foundups.
    foundups = [f"f_{idx:02d}" for idx in range(30)]
    for tick in range(1, 1601):
        foundup_id = foundups[tick % len(foundups)]
        tracker.record_dex_trade(
            tick=tick,
            foundup_id=foundup_id,
            volume_sats=2_000_000,
            source_ref=f"trade_{tick}",
        )

    metrics = tracker.get_sustainability_metrics()
    assert metrics["has_min_sample_window"] is True
    assert metrics["is_self_sustaining_base_gate"] is True
    assert "downside" in metrics["scenario_pack"]
    assert metrics["downside_revenue_cost_ratio_p10"] > 0
    assert metrics["is_self_sustaining"] == metrics["is_self_sustaining_claim"]


def test_fractional_fee_carry_preserves_sub_sat_revenue() -> None:
    """Sub-sat fees should accumulate instead of being truncated away."""
    tracker = FeeRevenueTracker()

    # 13 sats trade volume @2% => 0.26 sat/trade.
    # Across 10 trades this should realize 2 sats with 0.6 sat carry.
    for tick in range(1, 11):
        tracker.record_dex_trade(
            tick=tick,
            foundup_id="f_1",
            volume_sats=13.0,
            source_ref=f"trade_{tick}",
        )

    state = tracker.get_ecosystem_state()
    assert state.total_dex_volume_sats == 130
    assert state.total_dex_fees_sats == 2
    assert state.pavs_treasury_sats > 0  # split from realized fee sats
    assert len(tracker.get_fee_history(fee_type=None, foundup_id="f_1", limit=100)) == 2
