"""Simulation step pipeline.

Phase-1 extraction from ``FoundUpsModel.step()`` so tick orchestration is
isolated from class construction/runtime wiring.

This preserves current behavior while creating a clean seam for the later
pure-step refactor (`next_state = step(current_state, params, rng, events)`).
"""

from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING, Any

from .state_contracts import build_sim_state
from .step_core import StepPolicy, StepState, compute_step_decision
from .step_pure import StepParams, step

if TYPE_CHECKING:
    from .mesa_model import FoundUpsModel

logger = logging.getLogger(__name__)


def _collect_actor_ups_balances(model: "FoundUpsModel") -> dict[str, float]:
    """Collect per-actor UPS balances from token-econ accounts."""
    balances: dict[str, float] = {}
    human_accounts = model._token_econ_engine.human_accounts
    for actor_id in model._agent_order:
        account = human_accounts.get(actor_id)
        balances[actor_id] = float(account.ups_balance) if account else 0.0
    return balances


def _capture_shadow_context(model: "FoundUpsModel") -> dict[str, Any]:
    """Capture pre-step immutable state for pure-step shadow parity."""
    pre_stats = model.get_stats()
    pre_runtime_state = model._state_store.get_state()
    pre_ups_balances = _collect_actor_ups_balances(model)
    pre_rank = {actor_id: int(model._agent_rank.get(actor_id, 1)) for actor_id in model._agent_order}
    pre_state = build_sim_state(
        pre_runtime_state,
        pre_stats,
        rank_by_actor=pre_rank,
        ups_balance_by_actor=pre_ups_balances,
    )
    pre_tokens = {
        actor_id: float(model._token_economy.get_balance(actor_id))
        for actor_id in model._agent_order
    }

    return {
        "pre_stats": pre_stats,
        "pre_state": pre_state,
        "pre_tokens": pre_tokens,
    }


def _emit_shadow_drift_event(
    model: "FoundUpsModel",
    *,
    tick: int,
    actor_drift: float,
    pool_drift: float,
    fi_drift: float,
    tick_match: bool,
) -> None:
    daemon = model._fam_bridge.get_daemon()
    if not daemon:
        return
    daemon.emit(
        event_type="pure_step_shadow_drift",
        payload={
            "tick": tick,
            "actor_drift_max": round(actor_drift, 8),
            "pool_drift_max": round(pool_drift, 8),
            "fi_drift": round(fi_drift, 8),
            "tick_match": tick_match,
        },
        actor_id="pure_step_shadow",
        foundup_id="F_0",
    )


def _run_shadow_parity_check(model: "FoundUpsModel", shadow_context: dict[str, Any] | None) -> None:
    """Run pure-step in shadow mode and report drift vs runtime state."""
    if not shadow_context:
        return

    try:
        pre_stats = shadow_context["pre_stats"]
        pre_state = shadow_context["pre_state"]
        pre_tokens = shadow_context["pre_tokens"]

        post_stats = model.get_stats()
        post_runtime_state = model._state_store.get_state()
        post_ups_balances = _collect_actor_ups_balances(model)
        post_rank = {
            actor_id: int(model._agent_rank.get(actor_id, 1))
            for actor_id in model._agent_order
        }
        post_state = build_sim_state(
            post_runtime_state,
            post_stats,
            rank_by_actor=post_rank,
            ups_balance_by_actor=post_ups_balances,
        )

        actor_earnings = {
            actor_id: float(model._token_economy.get_balance(actor_id)) - pre_tokens.get(actor_id, 0.0)
            for actor_id in model._agent_order
        }

        demurrage_delta = max(
            0.0,
            float(post_stats.get("total_demurrage_decayed", 0.0))
            - float(pre_stats.get("total_demurrage_decayed", 0.0)),
        )
        total_pre_ups = sum(actor.ups_balance for actor in pre_state.actors.values())
        demurrage_rate = demurrage_delta / total_pre_ups if total_pre_ups > 0 else 0.0

        network_delta = max(
            0.0,
            float(post_stats.get("network_pool_ups", 0.0))
            - float(pre_stats.get("network_pool_ups", 0.0)),
        )
        fund_delta = max(
            0.0,
            float(post_stats.get("fund_pool_ups", 0.0))
            - float(pre_stats.get("fund_pool_ups", 0.0)),
        )
        decay_split = network_delta + fund_delta
        network_share = network_delta / decay_split if decay_split > 0 else 0.80
        fund_share = fund_delta / decay_split if decay_split > 0 else 0.20

        fi_delta = max(
            0.0,
            float(post_stats.get("fi_outstanding", 0.0))
            - float(pre_stats.get("fi_outstanding", 0.0)),
        )

        predicted = step(
            pre_state,
            StepParams(
                demurrage_rate_per_tick=demurrage_rate,
                token_release_per_tick=fi_delta,
                network_share_of_demurrage=network_share,
                fund_share_of_demurrage=fund_share,
            ),
            actor_earnings=actor_earnings,
        )

        actor_ids = set(predicted.actors.keys()) | set(post_state.actors.keys())
        actor_drift = max(
            (
                abs(
                    (predicted.actors.get(actor_id).tokens if predicted.actors.get(actor_id) else 0.0)
                    - (post_state.actors.get(actor_id).tokens if post_state.actors.get(actor_id) else 0.0)
                )
                for actor_id in actor_ids
            ),
            default=0.0,
        )
        pool_drift = max(
            abs(predicted.pools.network_pool - post_state.pools.network_pool),
            abs(predicted.pools.fund_pool - post_state.pools.fund_pool),
        )
        fi_drift = abs(predicted.fi_released_total - post_state.fi_released_total)
        tick_match = predicted.tick == post_state.tick

        cfg = model._config
        ok = (
            tick_match
            and actor_drift <= cfg.pure_step_shadow_max_actor_drift
            and pool_drift <= cfg.pure_step_shadow_max_pool_drift
            and fi_drift <= cfg.pure_step_shadow_max_fi_drift
        )
        model._pure_step_shadow_checks += 1
        model._pure_step_shadow_last = {
            "tick": model._tick,
            "ok": ok,
            "actor_drift_max": actor_drift,
            "pool_drift_max": pool_drift,
            "fi_drift": fi_drift,
            "tick_match": tick_match,
        }

        if not ok:
            model._pure_step_shadow_failures += 1
            logger.warning(
                "[SHADOW] tick=%s parity drift actor=%0.6f pool=%0.6f fi=%0.6f tick_match=%s",
                model._tick,
                actor_drift,
                pool_drift,
                fi_drift,
                tick_match,
            )
            _emit_shadow_drift_event(
                model,
                tick=model._tick,
                actor_drift=actor_drift,
                pool_drift=pool_drift,
                fi_drift=fi_drift,
                tick_match=tick_match,
            )
        elif (
            cfg.pure_step_shadow_log_interval > 0
            and model._pure_step_shadow_checks % cfg.pure_step_shadow_log_interval == 0
        ):
            logger.info(
                "[SHADOW] tick=%s parity ok actor=%0.6f pool=%0.6f fi=%0.6f",
                model._tick,
                actor_drift,
                pool_drift,
                fi_drift,
            )

    except Exception as exc:  # pragma: no cover - shadow must never break runtime
        logger.exception("[SHADOW] parity check failed: %s", exc)


def run_step(model: "FoundUpsModel") -> None:
    """Execute one simulator tick for ``FoundUpsModel``.

    Behavior is intentionally identical to the prior in-class implementation.
    """
    shadow_context: dict[str, Any] | None = None
    if model._config.pure_step_shadow_enabled:
        shadow_context = _capture_shadow_context(model)

    decision = compute_step_decision(
        StepState(tick=model._tick, start_time=model._start_time),
        StepPolicy(
            subscription_month_reset_interval=model._subscription_month_reset_interval,
            subscription_refresh_interval=model._subscription_refresh_interval,
            demurrage_interval=model._demurrage_interval,
            rating_update_interval=model._rating_update_interval,
        ),
        now=time.time(),
    )
    model._tick = decision.next_tick

    model._event_bus.set_tick(model._tick)
    model._state_store.tick(model._tick, decision.elapsed_seconds)

    random.shuffle(model._agent_order)
    for agent_id in model._agent_order:
        agent = model._agents[agent_id]
        agent.step(model._tick)

    model._track_agent_lifecycle()
    model._advance_task_pipeline()
    model._simulate_market_activity()
    model._simulate_f0_investor_program()
    model._sync_token_econ_foundup_pools()
    model._simulate_012_allocations()

    if decision.should_reset_subscription_cycles:
        model._reset_subscription_cycles()
    if decision.should_refresh_subscription_allocations:
        model._refresh_subscription_allocations()

    if decision.should_apply_demurrage:
        model._apply_demurrage_cycle()

    if decision.should_record_ratio_snapshot:
        model._record_btc_fi_ratio()

    if decision.should_emit_rating_updates:
        model._emit_rating_updates()
        model._emit_cabr_updates()

    # Full Tide Economics: Process tide every N ticks (012-approved 2026-02-17)
    if model._tick % model._tide_epoch_interval == 0 and model._tick > 0:
        model._process_tide_epoch()

    # SmartDAO progression + cross-DAO funding (WSP 100 event wiring).
    if model._tick % model._smartdao_epoch_interval == 0 and model._tick > 0:
        model._process_smartdao_epoch()

    for agent_id in model._agent_order:
        balance = model._token_economy.get_balance(agent_id)
        current = model._state_store.get_state().agents.get(agent_id)
        if current and current.tokens != balance:
            delta = balance - current.tokens
            model._state_store.update_agent_tokens(agent_id, delta)

    if model._config.pure_step_shadow_enabled:
        _run_shadow_parity_check(model, shadow_context)
