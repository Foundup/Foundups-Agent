from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .cache import AdvisorCache
from .config import QwenAdvisorConfig
from .prompts import build_compliance_prompt
from .telemetry import record_advisor_event

logger = logging.getLogger(__name__)


@dataclass
class AdvisorContext:
    """Inputs collected from HoloIndex search results."""

    query: str
    code_hits: List[Dict[str, Any]]
    wsp_hits: List[Dict[str, Any]]


@dataclass
class AdvisorResult:
    """Structured advisor response consumed by the CLI."""

    guidance: str
    reminders: List[str]
    todos: List[str]
    metadata: Dict[str, Any]


class QwenAdvisor:
    """Scaffolding for the Qwen-backed advisor.

    Current version returns placeholder guidance until the model integration ships.
    """

    def __init__(
        self,
        config: Optional[QwenAdvisorConfig] = None,
        cache: Optional[AdvisorCache] = None,
    ) -> None:
        self.config = config or QwenAdvisorConfig.from_env()
        self.cache = cache or AdvisorCache(enabled=self.config.cache_enabled)

    def generate_guidance(self, context: AdvisorContext) -> AdvisorResult:
        """Return preliminary guidance with TODO scaffolding."""

        cache_key = self.cache.make_key(context.query, {"code": len(context.code_hits), "wsp": len(context.wsp_hits)})
        cube_tags = sorted({hit.get('cube') for hit in context.code_hits + context.wsp_hits if hit.get('cube')})
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug("Advisor cache hit for query: %s", context.query)
            return AdvisorResult(**cached)

        prompt = build_compliance_prompt(context.query, context.code_hits, context.wsp_hits)
        logger.debug("Advisor prompt prepared (length=%s)", len(prompt))

        # Placeholder response until Qwen inference is wired up.
        guidance = (
            "Qwen advisor scaffolding active. Review the listed WSP protocols, update TESTModLog, "
            "and consult the FMAS plan before coding."
        )
        reminders = [
            "Confirm ModLog updates (WSP 22).",
            "Validate reuse of existing modules (WSP 17).",
            "Record completion checklist per WSP 18."
        ]
        todos = [
            "Implement Qwen model inference for advisor.",
            "Persist telemetry to E:/HoloIndex/indexes/holo_usage.json.",
            "Collect 0102 rating feedback after each query."
        ]

        query_lower = context.query.lower()
        if ('test' in query_lower) and "Review FMAS plan: WSP_framework/docs/testing/HOLOINDEX_QWEN_ADVISOR_FMAS_PLAN.md" not in todos:
            todos.append("Review FMAS plan: WSP_framework/docs/testing/HOLOINDEX_QWEN_ADVISOR_FMAS_PLAN.md")

        result = AdvisorResult(
            guidance=guidance,
            reminders=reminders,
            todos=todos,
            metadata={
                "prompt": prompt,
                "model_path": str(self.config.model_path),
                "cache_key": cache_key,
                "cubes": cube_tags,
            },
        )

        self.cache.set(cache_key, result.__dict__)
        record_advisor_event(self.config.telemetry_path, {
            "query": context.query,
            "reminder_count": len(reminders),
            "todo_count": len(todos),
            "cubes": cube_tags,
        })

        return result
