"""
News Context Provider for LiveChat Agent

Fetches live news via DuckDuckGo to ground agent responses in current events.
Implements topic-triggered search with TTL caching to avoid excessive API calls.

NAVIGATION: Provides current news context to LLM prompt pipeline
-> Called by: intelligent_livechat_reply.py, llm_integration.py
-> Uses: duckduckgo_search (DDGS) for zero-cost news fetching
-> Cache: In-memory dict with 1-hour TTL per topic

WSP Compliance: WSP 50 (search before respond), WSP 77 (agent coordination)
"""

from __future__ import annotations

import logging
import time
import threading
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# How long cached news stays fresh (seconds)
NEWS_CACHE_TTL = 3600  # 1 hour

# Max snippet length injected into prompts (YouTube chat = 180 chars total,
# so news context must be concise enough for the LLM to summarise)
MAX_NEWS_CONTEXT_CHARS = 600

# Keywords that trigger a news search when detected in chat messages
TRIGGER_KEYWORDS: Dict[str, List[str]] = {
    "ice_raids": [
        "ice", "deportation", "deport", "raids", "immigration",
        "migra", "undocumented", "illegal alien", "border",
        "detention", "pretti", "renee good", "ice arrest",
    ],
    "maga_politics": [
        "trump", "maga", "project 2025", "fascist", "fascism",
        "proud boys", "oath keepers", "january 6", "j6",
        "white nationalist", "christo-fascist",
    ],
    "anti_fascism": [
        "antifa", "anti-fascist", "resist", "resistance",
        "abolish ice", "no ban", "solidarity", "mutual aid",
    ],
    "japan": [
        "japan visa", "move to japan", "japanese immigration",
        "work in japan", "japan news",
    ],
}

# Known-figure context (injected without search when names appear)
KNOWN_FIGURES: Dict[str, str] = {
    "pretti": (
        "Pretti is a known ICE informant / collaborator figure discussed in "
        "anti-ICE activist circles. Search 'Pretti ICE informant' for latest."
    ),
    "renee good": (
        "Renee Good is connected to ICE enforcement actions and has been "
        "discussed in immigrant rights communities. Search for latest updates."
    ),
}

# --------------------------------------------------------------------------- #
# Cache
# --------------------------------------------------------------------------- #

_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()


def _cache_get(topic: str) -> Optional[str]:
    """Return cached news summary if still fresh, else None."""
    with _cache_lock:
        entry = _cache.get(topic)
        if entry and (time.time() - entry["ts"]) < NEWS_CACHE_TTL:
            return entry["text"]
    return None


def _cache_set(topic: str, text: str) -> None:
    with _cache_lock:
        _cache[topic] = {"text": text, "ts": time.time()}


# --------------------------------------------------------------------------- #
# DuckDuckGo news search
# --------------------------------------------------------------------------- #

_ddg = None


def _get_ddg():
    global _ddg
    if _ddg is None:
        try:
            from duckduckgo_search import DDGS
            _ddg = DDGS()
            logger.info("[NEWS] DuckDuckGo search initialised")
        except ImportError:
            logger.warning("[NEWS] duckduckgo_search not installed")
    return _ddg


def _search_news(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Run a DuckDuckGo news search, return list of {title, body, url, date}."""
    ddg = _get_ddg()
    if not ddg:
        return []
    try:
        results = list(ddg.news(query, max_results=max_results, timelimit="w"))
        logger.info(f"[NEWS] Searched '{query}' -> {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"[NEWS] Search failed for '{query}': {e}")
        return []


def _summarise_results(results: List[Dict[str, str]], max_chars: int = MAX_NEWS_CONTEXT_CHARS) -> str:
    """Condense news results into a compact text block for prompt injection."""
    if not results:
        return ""
    lines = []
    chars = 0
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        date = r.get("date", "")
        # Prefer body (snippet), fall back to title
        snippet = body[:120] if body else title[:80]
        if date:
            line = f"- [{date[:10]}] {snippet}"
        else:
            line = f"- {snippet}"
        if chars + len(line) > max_chars:
            break
        lines.append(line)
        chars += len(line) + 1  # +1 for newline
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def detect_news_topics(message: str) -> List[str]:
    """
    Scan a chat message for topic triggers.

    Returns list of matched topic keys (e.g. ["ice_raids", "maga_politics"]).
    """
    msg_lower = message.lower()
    matched = []
    for topic, keywords in TRIGGER_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                matched.append(topic)
                break  # one match per topic is enough
    return matched


def detect_known_figures(message: str) -> Optional[str]:
    """
    Check if message mentions known figures (Pretti, Renee Good, etc.).

    Returns static context string or None.
    """
    msg_lower = message.lower()
    parts = []
    for name, context in KNOWN_FIGURES.items():
        if name in msg_lower:
            parts.append(context)
    return " ".join(parts) if parts else None


def get_news_context(
    message: str,
    *,
    force_topics: Optional[List[str]] = None,
    max_chars: int = MAX_NEWS_CONTEXT_CHARS,
) -> Optional[str]:
    """
    Main entry point: given a chat message, return news context to inject into
    the LLM prompt.  Returns None if no relevant topics detected.

    Flow:
      1. Detect topic triggers in message
      2. Check known-figure static context
      3. For each topic, check cache or fetch fresh news
      4. Combine into a single context block

    Args:
        message: The chat message text
        force_topics: Override automatic detection (for fact-check)
        max_chars: Max total chars for combined context

    Returns:
        News context string to inject, or None
    """
    topics = force_topics or detect_news_topics(message)
    if not topics:
        # Still check known figures even without topic triggers
        figure_ctx = detect_known_figures(message)
        return figure_ctx  # may be None

    sections = []
    total_chars = 0

    # Known figures first (free, no API call)
    figure_ctx = detect_known_figures(message)
    if figure_ctx:
        sections.append(f"KNOWN FIGURES: {figure_ctx}")
        total_chars += len(sections[-1])

    # News per topic (cached or fresh)
    topic_queries = {
        "ice_raids": "ICE raids deportation arrests 2026",
        "maga_politics": "Trump MAGA news 2026",
        "anti_fascism": "anti-fascist resistance movement 2026",
        "japan": "Japan immigration visa news 2026",
    }

    for topic in topics:
        if total_chars >= max_chars:
            break

        # Check cache first
        cached = _cache_get(topic)
        if cached:
            section = cached
        else:
            query = topic_queries.get(topic, topic.replace("_", " ") + " news 2026")
            results = _search_news(query, max_results=4)
            section = _summarise_results(results, max_chars=max_chars - total_chars)
            if section:
                _cache_set(topic, section)

        if section:
            sections.append(f"[{topic.upper()}]\n{section}")
            total_chars += len(sections[-1])

    if not sections:
        return None

    context = "\n\n".join(sections)
    if len(context) > max_chars:
        context = context[:max_chars]

    logger.info(f"[NEWS] Context built: {len(context)} chars, topics={topics}")
    return context


def get_fact_check_context(
    target_messages: List[str],
    max_chars: int = MAX_NEWS_CONTEXT_CHARS,
) -> Optional[str]:
    """
    Build news context specifically for fact-checking a user's statements.

    Scans all target messages for topics, then fetches relevant news.
    """
    combined = " ".join(target_messages)
    all_topics = detect_news_topics(combined)

    if not all_topics:
        # Fall back: search the raw claims
        all_topics = ["general"]
        # Build a search from the user's actual words
        snippet = combined[:100].replace("\n", " ")
        _cache_key = f"fc_{hash(snippet)}"
        cached = _cache_get(_cache_key)
        if cached:
            return cached
        results = _search_news(f"fact check: {snippet}", max_results=3)
        summary = _summarise_results(results, max_chars=max_chars)
        if summary:
            _cache_set(_cache_key, summary)
            return f"CURRENT NEWS/FACTS:\n{summary}"
        return None

    return get_news_context(combined, force_topics=all_topics, max_chars=max_chars)
