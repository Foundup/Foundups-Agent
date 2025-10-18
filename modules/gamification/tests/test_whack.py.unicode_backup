import pytest
from datetime import datetime, timedelta

from modules.gamification import (
    apply_whack,
    get_profile,
    classify_behavior,
    BehaviorTier,
)

# Access test helper by importing the module directly
from modules.gamification.src import whack as whack_mod


def setup_function():
    # Reset in-memory state before each test
    whack_mod._reset_state_for_tests()


def test_points_zero_for_10s():
    now = datetime.utcnow()
    action = apply_whack("mod1", "tgt1", 10, now)
    assert action.points == 0


@pytest.mark.parametrize(
    "duration_sec,expected_min",
    [
        (11, 1),           # 11–59s → 1 pt
        (59, 1),
        (60, 2),           # 1–14m → 2 pts
        (14 * 60, 2),
        (15 * 60, 3),      # 15–59m → 3 pts
        (59 * 60, 3),
        (60 * 60, 5),      # 60–239m → 5 pts
        (239 * 60, 5),
        (240 * 60, 8),     # 240–1439m → 8 pts
        (1439 * 60, 8),
        (24 * 60 * 60, 13) # 24h → 13 pts
    ],
)
def test_points_scale_by_duration(duration_sec, expected_min):
    now = datetime.utcnow()
    action = apply_whack("mod1", "tgt1", duration_sec, now)
    assert action.points >= expected_min


def test_diminishing_returns_same_target():
    now = datetime.utcnow()
    # First on target
    a1 = apply_whack("mod1", "tgt1", 60, now)
    # Repeat 1
    a2 = apply_whack("mod1", "tgt1", 60, now + timedelta(seconds=1))
    # Repeat 2
    a3 = apply_whack("mod1", "tgt1", 60, now + timedelta(seconds=2))
    # Repeat 3+
    a4 = apply_whack("mod1", "tgt1", 60, now + timedelta(seconds=3))

    assert a1.points == 2               # 100%
    assert a2.points == int(2 * 0.6)    # 60%
    assert a3.points == int(2 * 0.3)    # 30%
    assert a4.points == int(2 * 0.1)    # 10%


def test_daily_cap_enforced():
    now = datetime.utcnow()
    # Accumulate up to just below 100 using 60-min timeouts (5 pts base)
    total = 0
    for i in range(19):  # 19 * 5 = 95
        a = apply_whack("mod1", f"t{i}", 60 * 60, now + timedelta(minutes=i))
        total += a.points
    assert total == 95

    # Next ones should be capped to 5 remaining, then zero
    a20 = apply_whack("mod1", "cap", 60 * 60, now + timedelta(minutes=19))
    a21 = apply_whack("mod1", "cap2", 60 * 60, now + timedelta(minutes=20))
    assert a20.points == 5
    assert a21.points == 0


def test_behavior_classification_examples():
    # CAT_PLAY: multiple short with repeats≥2
    assert classify_behavior(30, 2) == BehaviorTier.CAT_PLAY
    # BRUTAL_HAMMER: >= 12h
    assert classify_behavior(12 * 60 * 60, 0) == BehaviorTier.BRUTAL_HAMMER
    # GENTLE_TOUCH: 1–15 min with no repeats
    assert classify_behavior(10 * 60, 0) == BehaviorTier.GENTLE_TOUCH
    # OBSERVER: represent as duration<=0 here
    assert classify_behavior(0, 0) == BehaviorTier.OBSERVER


def test_rank_and_level_progression():
    now = datetime.utcnow()
    mod = "modX"

    # Award 55 points (Silver; level 1 still)
    # Use 60-min timeouts (5 pts each), non-repeating targets
    for i in range(11):
        apply_whack(mod, f"t{i}", 60 * 60, now + timedelta(minutes=i))

    profile = get_profile(mod)
    assert profile.score == 55
    assert profile.rank == "Silver"
    assert profile.level == 1

    # Progress with daily cap across multiple days to exceed 200
    next_day = now + timedelta(hours=25)
    # Day 2: earn up to daily cap (100 pts)
    for i in range(40):  # 40 * 5 = 200 base, but capped at +100
        apply_whack(mod, f"d2_{i}", 60 * 60, next_day + timedelta(minutes=i))

    profile = get_profile(mod)
    assert profile.score == 55 + 100
    assert profile.rank in ("Silver", "Gold")

    # Day 3: another fresh 24h window → cap allows +100 again
    day3 = next_day + timedelta(hours=25)
    for i in range(40):
        apply_whack(mod, f"d3_{i}", 60 * 60, day3 + timedelta(minutes=i))

    profile = get_profile(mod)
    assert profile.score == 55 + 100 + 100
    assert profile.rank == "Gold"
    assert profile.level == 1 + ((profile.score) // 100)


