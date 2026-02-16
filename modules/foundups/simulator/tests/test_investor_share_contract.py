"""Investor share contract tests for pre/post repayment-hurdle behavior."""

from __future__ import annotations

import pytest

from modules.foundups.simulator.economics import InvestorPool


def _fully_vest_all(pool: InvestorPool) -> None:
    """Make all current investors fully vested for deterministic share tests."""
    for position in pool.investors.values():
        position.ii_tokens_vested = position.ii_tokens_total


def test_default_founder_share_is_pre_hurdle_max_rate() -> None:
    pool = InvestorPool()
    pool.invest_btc("seed", 1.0)

    assert pool.return_hurdle_met is False
    assert pool.founder_share_per_foundup == pytest.approx(0.1216, abs=1e-12)


def test_founder_share_transitions_to_min_rate_at_repayment_hurdle() -> None:
    pool = InvestorPool()
    pool.invest_btc("seed", 2.0)
    target = pool.repayment_target_btc

    pool.record_distribution_btc("seed", target * 0.99)
    assert pool.return_hurdle_met is False
    assert pool.founder_share_per_foundup == pytest.approx(0.1216, abs=1e-12)

    pool.record_distribution_btc("seed", target * 0.01)
    assert pool.return_hurdle_met is True
    assert pool.repayment_progress == pytest.approx(1.0, abs=1e-12)
    assert pool.founder_share_per_foundup == pytest.approx(0.0064, abs=1e-12)


def test_sum_of_investor_shares_tracks_current_pool_rate() -> None:
    pool = InvestorPool()
    pool.invest_btc("a", 1.0)
    pool.invest_btc("b", 1.0)
    _fully_vest_all(pool)

    pre_hurdle_sum = pool.calculate_founder_share("a") + pool.calculate_founder_share("b")
    assert pre_hurdle_sum == pytest.approx(0.1216, abs=1e-12)

    pool.record_distribution_btc("a", pool.repayment_target_btc)
    post_hurdle_sum = pool.calculate_founder_share("a") + pool.calculate_founder_share("b")
    assert post_hurdle_sum == pytest.approx(0.0064, abs=1e-12)


def test_claim_founder_fi_uses_dynamic_rate() -> None:
    pool = InvestorPool()
    pool.invest_btc("solo", 1.0)
    _fully_vest_all(pool)

    # One fully vested investor gets the full pool allocation for the FoundUp.
    pre_hurdle_claim = pool.claim_founder_fi(
        investor_id="solo",
        foundup_id="f-pre",
        foundup_minted_fi=10_000.0,
    )
    assert pre_hurdle_claim == pytest.approx(1216.0, abs=1e-9)

    pool.record_distribution_btc("solo", pool.repayment_target_btc)
    post_hurdle_claim = pool.claim_founder_fi(
        investor_id="solo",
        foundup_id="f-post",
        foundup_minted_fi=10_000.0,
    )
    assert post_hurdle_claim == pytest.approx(64.0, abs=1e-9)
    assert pool.claim_founder_fi("solo", "f-post", 10_000.0) == pytest.approx(0.0, abs=1e-12)


def test_recorded_distributions_surface_in_investor_returns() -> None:
    pool = InvestorPool()
    pool.invest_btc("seed", 1.5)
    pool.record_distribution_btc("seed", 0.75)
    pool.record_distribution_btc("seed", 0.25)

    returns = pool.get_investor_returns("seed")
    stats = pool.get_stats()

    assert returns["distributions_btc_recorded"] == pytest.approx(1.0, abs=1e-12)
    assert stats["cumulative_distributions_btc"] == pytest.approx(1.0, abs=1e-12)
    assert stats["return_hurdle_met"] is False


def test_post_hurdle_tail_is_permanent_after_lock() -> None:
    pool = InvestorPool()
    pool.invest_btc("seed", 1.0)
    pool.record_distribution_btc("seed", pool.repayment_target_btc)

    assert pool.return_hurdle_met is True
    assert pool.founder_share_per_foundup == pytest.approx(0.0064, abs=1e-12)

    # Add new principal after lock; tail remains permanent.
    pool.invest_btc("new_capital", 5.0)
    assert pool.post_hurdle_mode_locked is True
    assert pool.return_hurdle_met is True
    assert pool.founder_share_per_foundup == pytest.approx(0.0064, abs=1e-12)


def test_transfer_vested_ii_transfers_tail_economics() -> None:
    pool = InvestorPool()
    pool.invest_btc("a", 1.0)
    pool.invest_btc("b", 1.0)
    _fully_vest_all(pool)
    pool.record_distribution_btc("a", pool.repayment_target_btc)

    share_a_before = pool.calculate_founder_share("a")
    share_b_before = pool.calculate_founder_share("b")
    amount = pool.investors["a"].ii_tokens_vested * 0.5

    assert pool.transfer_vested_ii("a", "b", amount) is True

    share_a_after = pool.calculate_founder_share("a")
    share_b_after = pool.calculate_founder_share("b")
    assert share_a_after < share_a_before
    assert share_b_after > share_b_before
    assert (share_a_after + share_b_after) == pytest.approx(0.0064, abs=1e-12)


def test_transfer_vested_ii_blocks_unvested_amounts() -> None:
    pool = InvestorPool()
    pool.invest_btc("a", 1.0)
    # No vesting yet, so transfer must fail.
    assert pool.transfer_vested_ii("a", "b", 0.1) is False
