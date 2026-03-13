"""LinkedIn publishing discovery and target-routing helpers."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

MODULE_ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = MODULE_ROOT / "data" / "linkedin_publishing_map.json"
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "like",
    "not",
    "of",
    "on",
    "or",
    "our",
    "the",
    "their",
    "this",
    "to",
    "we",
    "with",
}


def _tokenize(text: str) -> List[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", (text or "").lower())
        if token and token not in STOP_WORDS
    ]


def _iso_sort_key(value: str) -> str:
    return value or "0000-00-00"


@lru_cache(maxsize=1)
def load_publishing_map() -> Dict[str, Any]:
    with MAP_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _entity_record(entity: Dict[str, Any]) -> Dict[str, Any]:
    articles = entity.get("published_articles", [])
    return {
        "key": entity["key"],
        "display_name": entity["display_name"],
        "entity_type": entity["entity_type"],
        "company_id": entity.get("company_id"),
        "status": entity.get("status", "active"),
        "posting_support": entity.get("posting_support", "unknown"),
        "subdomain": entity.get("subdomain"),
        "manage_url": entity.get("manage_url"),
        "activity_url": entity.get("activity_url"),
        "article_editor_url": entity.get("article_editor_url"),
        "aliases": list(entity.get("aliases", [])),
        "routing_tags": list(entity.get("routing_tags", [])),
        "notes": entity.get("notes", ""),
        "article_count": len(articles),
        "latest_article_date": max((_iso_sort_key(item.get("date")) for item in articles), default=None),
    }


def list_publishing_entities(
    include_zero_article: bool = True,
    include_not_checked: bool = True,
    query: str = "",
) -> List[Dict[str, Any]]:
    query_tokens = set(_tokenize(query))
    entities = []
    for entity in load_publishing_map().get("entities", []):
        status = entity.get("status", "active")
        article_count = len(entity.get("published_articles", []))
        if not include_zero_article and article_count == 0:
            continue
        if not include_not_checked and status == "not_yet_checked":
            continue
        record = _entity_record(entity)
        if query_tokens:
            haystack = set(
                _tokenize(
                    " ".join(
                        [
                            entity["key"],
                            entity["display_name"],
                            entity.get("subdomain", ""),
                            " ".join(entity.get("aliases", [])),
                            " ".join(entity.get("routing_tags", [])),
                        ]
                    )
                )
            )
            if not (haystack & query_tokens):
                continue
        entities.append(record)
    return sorted(
        entities,
        key=lambda item: (
            item["article_count"],
            item["status"] == "active",
            item["display_name"].lower(),
        ),
        reverse=True,
    )


def search_published_articles(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    query_text = (query or "").strip().lower()
    query_tokens = set(_tokenize(query_text))
    if not query_tokens and not query_text:
        return []

    matches: List[Dict[str, Any]] = []
    for entity in load_publishing_map().get("entities", []):
        entity_tokens = set(
            _tokenize(
                " ".join(
                    [
                        entity["key"],
                        entity["display_name"],
                        " ".join(entity.get("aliases", [])),
                        " ".join(entity.get("routing_tags", [])),
                    ]
                )
            )
        )
        entity_bonus = len(entity_tokens & query_tokens)
        for article in entity.get("published_articles", []):
            title = article.get("title", "")
            title_text = title.lower()
            title_tokens = set(_tokenize(title_text))
            overlap = len(title_tokens & query_tokens)
            phrase_bonus = 4 if query_text and query_text in title_text else 0
            score = overlap * 3 + entity_bonus + phrase_bonus
            if score <= 0:
                continue
            matches.append(
                {
                    "title": title,
                    "date": article.get("date"),
                    "entity_key": entity["key"],
                    "display_name": entity["display_name"],
                    "subdomain": entity.get("subdomain"),
                    "company_id": entity.get("company_id"),
                    "posting_support": entity.get("posting_support", "unknown"),
                    "manage_url": entity.get("manage_url"),
                    "article_editor_url": entity.get("article_editor_url"),
                    "score": score,
                }
            )
    matches.sort(key=lambda item: (item["score"], _iso_sort_key(item.get("date"))), reverse=True)
    return matches[: max(1, limit)]


def _find_entity(entity_name: str) -> Optional[Dict[str, Any]]:
    if not entity_name:
        return None
    query_text = entity_name.strip().lower()
    for entity in load_publishing_map().get("entities", []):
        choices = [entity["key"], entity["display_name"], entity.get("subdomain", "")]
        choices.extend(entity.get("aliases", []))
        lowered = [choice.lower() for choice in choices if choice]
        if query_text in lowered or any(query_text in choice for choice in lowered):
            return entity
    return None


def _score_entity(entity: Dict[str, Any], query_text: str, query_tokens: Set[str]) -> Dict[str, Any]:
    alias_hits = [alias for alias in entity.get("aliases", []) if alias and alias.lower() in query_text]
    tag_hits = sorted(set(entity.get("routing_tags", [])) & query_tokens)
    published_articles = entity.get("published_articles", [])
    article_overlap = max(
        (len(set(_tokenize(article.get("title", ""))) & query_tokens) for article in published_articles),
        default=0,
    )
    score = len(alias_hits) * 8 + len(tag_hits) * 4 + article_overlap * 2
    if entity["display_name"].lower() in query_text or entity["key"].lower() in query_text:
        score += 10
    status = entity.get("status")
    if status == "mirror_only":
        score -= 3
    if status in {"zero_articles", "not_yet_checked"} and not alias_hits:
        score -= 2

    reasons = []
    if alias_hits:
        reasons.append(f"alias/name match: {', '.join(alias_hits[:3])}")
    if tag_hits:
        reasons.append(f"routing tags matched: {', '.join(tag_hits[:4])}")
    if article_overlap:
        reasons.append(f"historical title overlap: {article_overlap} token(s)")
    if not reasons and status in {"zero_articles", "not_yet_checked"}:
        reasons.append("no article history; route only with explicit intent")

    return {"entity": entity, "score": score, "reasons": reasons}


def resolve_article_target(
    title: str,
    brief: str = "",
    body: str = "",
    preferred_entity: str = "",
) -> Dict[str, Any]:
    explicit = _find_entity(preferred_entity)
    query_text = " ".join(part for part in [title, brief, body] if part).strip().lower()
    query_tokens = set(_tokenize(query_text))

    if explicit:
        summary = _entity_record(explicit)
        return {
            "query": {"title": title, "brief": brief, "preferred_entity": preferred_entity},
            "recommended_entity": summary,
            "alternatives": [],
            "confidence": "explicit",
            "reasoning": [f"preferred_entity resolved to {summary['display_name']}"],
            "limitations": _limitations(summary["posting_support"]),
        }

    ranked = [_score_entity(entity, query_text, query_tokens) for entity in load_publishing_map().get("entities", [])]
    ranked = [item for item in ranked if item["score"] > 0]
    ranked.sort(
        key=lambda item: (
            item["score"],
            len(item["entity"].get("published_articles", [])),
            item["entity"].get("status") == "active",
        ),
        reverse=True,
    )

    if not ranked:
        return {
            "query": {"title": title, "brief": brief, "preferred_entity": preferred_entity},
            "recommended_entity": None,
            "alternatives": [],
            "confidence": "low",
            "reasoning": ["No historical or tag evidence matched the proposed article."],
            "limitations": _limitations("unknown"),
        }

    top = ranked[0]
    alternatives = [
        {**_entity_record(item["entity"]), "score": item["score"], "reasons": item["reasons"]}
        for item in ranked[1:4]
    ]
    confidence = "medium"
    if top["score"] >= 14:
        confidence = "high"
    elif len(ranked) == 1 or top["score"] - ranked[1]["score"] >= 4:
        confidence = "medium_high"

    summary = _entity_record(top["entity"])
    return {
        "query": {"title": title, "brief": brief, "preferred_entity": preferred_entity},
        "recommended_entity": {**summary, "score": top["score"], "reasons": top["reasons"]},
        "alternatives": alternatives,
        "confidence": confidence,
        "reasoning": top["reasons"] or ["Matched on existing entity metadata."],
        "limitations": _limitations(summary["posting_support"]),
    }


def _limitations(posting_support: str) -> List[str]:
    if posting_support == "company_article_url":
        return [
            "Routing is heuristic and based on historical article data.",
            "Direct posting still depends on separate LinkedIn automation and auth flows.",
        ]
    if posting_support == "manual_profile_path":
        return [
            "Personal profile article creation is not wired as a direct automated company article URL.",
            "Routing is heuristic and based on historical article data.",
        ]
    return [
        "Target availability is not verified for automated posting.",
        "Routing is heuristic and based on historical article data.",
    ]


__all__ = [
    "list_publishing_entities",
    "load_publishing_map",
    "resolve_article_target",
    "search_published_articles",
]
