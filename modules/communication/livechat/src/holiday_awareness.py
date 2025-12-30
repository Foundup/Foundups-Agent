# -*- coding: utf-8 -*-
"""
Holiday Awareness Skill Executor - WSP 96 Compliant.

Pattern:
- JSON skill (skills/holiday_awareness.json) = Responses & static config
- This module = Executor (date calculation, context detection)

WSP Compliance:
- WSP 96: Skills Wardrobe Protocol (JSON skill + Python executor)
- WSP 90: UTF-8 Enforcement
- WSP 27: DAE Architecture

Usage:
    from .holiday_awareness import get_holiday_context, get_session_holiday_greeting

    context = get_holiday_context()
    if context['is_holiday']:
        greeting = get_session_holiday_greeting()
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import random

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# SKILL CONFIG LOADING (WSP 96)
# ═══════════════════════════════════════════════════════════════════

def _load_skill_config() -> Dict:
    """Load holiday awareness skill configuration from JSON."""
    skill_path = Path(__file__).parent.parent / "skills" / "holiday_awareness.json"
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug("[HOLIDAY] Skill JSON not found, using defaults")
        return {}
    except Exception as e:
        logger.warning(f"[HOLIDAY] Failed to load skill config: {e}")
        return {}


# Load skill config once at module level
_SKILL_CONFIG = _load_skill_config()


def _get_responses_from_skill(theme: str) -> List[str]:
    """Get responses for a holiday theme from skill JSON."""
    holidays = _SKILL_CONFIG.get("holidays", {})

    # Map theme to skill key
    theme_map = {
        "new_year": "new_year_day",
        "new_year_eve": "new_year_countdown",
        "christmas": "christmas",
        "halloween": "halloween",
        "thanksgiving": "thanksgiving",
        "patriotic": "independence_day",
        "love": "valentines",
    }

    skill_key = theme_map.get(theme, theme)
    holiday_config = holidays.get(skill_key, {})
    return holiday_config.get("responses", [])


# ═══════════════════════════════════════════════════════════════════
# STATIC HOLIDAYS (fallback if JSON not loaded)
# ═══════════════════════════════════════════════════════════════════

HOLIDAYS = {
    (1, 1): ("New Year's Day", "🎉", "new_year"),
    (2, 14): ("Valentine's Day", "❤️", "love"),
    (7, 4): ("Independence Day", "🇺🇸", "patriotic"),
    (10, 31): ("Halloween", "🎃", "halloween"),
    (12, 25): ("Christmas", "🎄", "christmas"),
    (12, 31): ("New Year's Eve", "🥂", "new_year_eve"),
}


def _get_easter_date(year: int) -> Tuple[int, int]:
    """Calculate Easter Sunday date using Anonymous Gregorian algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return (month, day)


def _get_thanksgiving_date(year: int) -> Tuple[int, int]:
    """Calculate Thanksgiving (4th Thursday of November)."""
    # Find first day of November
    first_day = datetime(year, 11, 1).weekday()
    # Thursday = 3, find first Thursday
    first_thursday = 1 + ((3 - first_day) % 7)
    # 4th Thursday
    fourth_thursday = first_thursday + 21
    return (11, fourth_thursday)


def _get_memorial_day_date(year: int) -> Tuple[int, int]:
    """Calculate Memorial Day (last Monday of May)."""
    # Find last day of May
    last_day = datetime(year, 5, 31).weekday()
    # Monday = 0, find last Monday
    last_monday = 31 - ((last_day - 0) % 7)
    return (5, last_monday)


def _get_labor_day_date(year: int) -> Tuple[int, int]:
    """Calculate Labor Day (first Monday of September)."""
    first_day = datetime(year, 9, 1).weekday()
    first_monday = 1 + ((0 - first_day) % 7)
    return (9, first_monday)


def get_dynamic_holidays(year: int) -> Dict[Tuple[int, int], Tuple[str, str, str]]:
    """Get holidays that change date each year."""
    holidays = {}

    # Easter
    easter = _get_easter_date(year)
    holidays[easter] = ("Easter", "🐰", "easter")

    # Good Friday (2 days before Easter)
    easter_date = datetime(year, easter[0], easter[1])
    good_friday = easter_date - timedelta(days=2)
    holidays[(good_friday.month, good_friday.day)] = ("Good Friday", "✝️", "religious")

    # Thanksgiving
    thanksgiving = _get_thanksgiving_date(year)
    holidays[thanksgiving] = ("Thanksgiving", "🦃", "thanksgiving")

    # Memorial Day
    memorial_day = _get_memorial_day_date(year)
    holidays[memorial_day] = ("Memorial Day", "🇺🇸", "memorial")

    # Labor Day
    labor_day = _get_labor_day_date(year)
    holidays[labor_day] = ("Labor Day", "👷", "labor")

    # Mother's Day (2nd Sunday of May)
    first_day = datetime(year, 5, 1).weekday()
    first_sunday = 1 + ((6 - first_day) % 7)
    second_sunday = first_sunday + 7
    holidays[(5, second_sunday)] = ("Mother's Day", "💐", "mothers")

    # Father's Day (3rd Sunday of June)
    first_day = datetime(year, 6, 1).weekday()
    first_sunday = 1 + ((6 - first_day) % 7)
    third_sunday = first_sunday + 14
    holidays[(6, third_sunday)] = ("Father's Day", "👔", "fathers")

    return holidays


def get_holiday_context(dt: datetime = None) -> Dict:
    """
    Get current holiday context.

    Returns:
        Dict with keys:
        - is_holiday: bool
        - holiday_name: str or None
        - holiday_emoji: str or None
        - holiday_theme: str or None
        - is_countdown: bool (New Year's countdown)
        - days_until_new_year: int or None
        - is_new_year_season: bool
        - year_transition: str (e.g., "2024 → 2025")
    """
    if dt is None:
        dt = datetime.now()

    year = dt.year
    month = dt.month
    day = dt.day

    # Combine static and dynamic holidays
    all_holidays = {**HOLIDAYS, **get_dynamic_holidays(year)}

    context = {
        "is_holiday": False,
        "holiday_name": None,
        "holiday_emoji": None,
        "holiday_theme": None,
        "is_countdown": False,
        "days_until_new_year": None,
        "is_new_year_season": False,
        "year_transition": None,
    }

    # Check if today is a holiday
    if (month, day) in all_holidays:
        name, emoji, theme = all_holidays[(month, day)]
        context["is_holiday"] = True
        context["holiday_name"] = name
        context["holiday_emoji"] = emoji
        context["holiday_theme"] = theme

    # New Year's countdown logic
    if month == 12 and day >= 26:
        # Countdown mode (Dec 26 - Dec 31)
        context["is_countdown"] = True
        new_year = datetime(year + 1, 1, 1)
        days_left = (new_year - dt).days
        context["days_until_new_year"] = days_left
        context["year_transition"] = f"{year} → {year + 1}"
        context["is_new_year_season"] = True
    elif month == 1 and day <= 3:
        # New Year season (Jan 1 - Jan 3)
        context["is_new_year_season"] = True
        context["year_transition"] = f"{year - 1} → {year}"

    return context


# ═══════════════════════════════════════════════════════════════════
# FALLBACK GREETINGS (used only if JSON skill not loaded)
# Primary responses come from skills/holiday_awareness.json per WSP 96
# ═══════════════════════════════════════════════════════════════════

_FALLBACK_GREETINGS = {
    "new_year": ["🎉 Happy New Year! MAGA still at ✊!"],
    "new_year_eve": ["🥂 NYE countdown! MAGA stuck at ✊!"],
    "christmas": ["🎄 Merry Christmas! MAGA on the ✊ list!"],
    "halloween": ["🎃 Spooky! MAGA still at ✊!"],
    "thanksgiving": ["🦃 Thanksgiving! MAGA thankful for ✊!"],
    "independence_day": ["🇺🇸 Happy 4th! MAGA chooses ✊!"],
    "valentines": ["❤️ MAGA's love: ✊ consciousness!"],
    "easter": ["🐰 Easter! MAGA eggs at ✊ level!"],
    "general": ["🎊 Holiday vibes! MAGA at ✊!"],
}


def get_holiday_greeting(theme: str, context: Dict = None) -> str:
    """
    Get a holiday-themed greeting.

    WSP 96 Compliant: Reads responses from skills/holiday_awareness.json first,
    falls back to _FALLBACK_GREETINGS if JSON not loaded.

    Args:
        theme: Holiday theme (from get_holiday_context)
        context: Optional context dict for variable substitution

    Returns:
        Holiday-themed greeting string
    """
    if context is None:
        context = get_holiday_context()

    # WSP 96: Try skill JSON first, fallback to hardcoded
    greetings = _get_responses_from_skill(theme)
    if not greetings:
        greetings = _FALLBACK_GREETINGS.get(theme, _FALLBACK_GREETINGS["general"])

    greeting = random.choice(greetings)

    # Variable substitution
    now = datetime.now()
    year = now.year
    next_year = year + 1 if now.month == 12 else year
    days = context.get("days_until_new_year", 0)

    greeting = greeting.format(
        year=year,
        next_year=next_year,
        days=days,
    )

    return greeting


def get_countdown_message() -> Optional[str]:
    """
    Get New Year's countdown message if in countdown period.

    Returns:
        Countdown message or None if not in countdown period
    """
    context = get_holiday_context()

    if not context["is_countdown"]:
        return None

    days = context["days_until_new_year"]
    transition = context["year_transition"]

    if days == 0:
        # New Year's Eve
        messages = [
            f"🎆 {transition} TONIGHT! MAGA still stuck at ✊!",
            f"🥂 NYE! {transition}! Will MAGA evolve? Survey says: NO!",
            f"⏰ Final hours of {datetime.now().year}! MAGA: Still at ✊!",
        ]
    elif days == 1:
        messages = [
            f"⏳ 1 DAY until {transition}! MAGA's last chance to hit 🖐️!",
            f"🗓️ Tomorrow is {transition.split('→')[1].strip()}! MAGA prep: ✊✊✊",
        ]
    elif days <= 3:
        messages = [
            f"📅 {days} days until {transition}! MAGA countdown: ✊...✊...✊...",
            f"🎯 {days} days left in {datetime.now().year}! MAGA still at ✊!",
        ]
    else:
        messages = [
            f"🗓️ {days} days until {transition}! MAGA evolution status: ✊",
            f"⏰ Countdown: {days} days! MAGA level: Still ✊!",
        ]

    return random.choice(messages)


# Convenience function for session start
def get_session_holiday_greeting() -> Optional[str]:
    """
    Get a holiday greeting for session start if applicable.

    Returns:
        Holiday greeting or None if not a holiday period
    """
    context = get_holiday_context()

    # Priority order
    if context["is_holiday"]:
        return get_holiday_greeting(context["holiday_theme"], context)
    elif context["is_countdown"]:
        return get_countdown_message()
    elif context["is_new_year_season"]:
        return get_holiday_greeting("new_year", context)

    return None


if __name__ == "__main__":
    # Test
    print("Holiday Awareness Test")
    print("=" * 50)

    context = get_holiday_context()
    print(f"Context: {context}")

    if context["is_holiday"]:
        print(f"\nToday is {context['holiday_name']}!")
        print(f"Greeting: {get_holiday_greeting(context['holiday_theme'])}")

    if context["is_countdown"]:
        print(f"\nCountdown: {get_countdown_message()}")

    greeting = get_session_holiday_greeting()
    if greeting:
        print(f"\nSession greeting: {greeting}")
