from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .cache import AdvisorCache
from .config import QwenAdvisorConfig
from .llm_engine import QwenInferenceEngine
from .pattern_coach import PatternCoach
from .wsp_master import WSPMaster
from .prompts import build_compliance_prompt
from .telemetry import record_advisor_event
from .rules_engine import ComplianceRulesEngine

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
    """Qwen-backed advisor with LLM intelligence.

    Uses local Qwen 1.5B coder model for intelligent code analysis and guidance,
    with rules engine fallback for compliance checking.
    """

    def __init__(
        self,
        config: Optional[QwenAdvisorConfig] = None,
        cache: Optional[AdvisorCache] = None,
    ) -> None:
        self.config = config or QwenAdvisorConfig.from_env()
        self.cache = cache or AdvisorCache(enabled=self.config.cache_enabled)
        self.rules_engine = ComplianceRulesEngine()  # Initialize rules engine

        # Initialize LLM engine for intelligent analysis
        self.llm_engine = QwenInferenceEngine(
            model_path=self.config.model_path,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )

        # Initialize WSP Master for comprehensive protocol guidance
        self.wsp_master = WSPMaster()

        # Initialize Pattern Coach for intelligent behavioral coaching
        self.pattern_coach = PatternCoach()
        self.pattern_coach.set_wsp_master(self.wsp_master)

    def generate_guidance(self, context: AdvisorContext) -> AdvisorResult:
        """Generate intelligent guidance using WSP Master, LLM, and Pattern Coach."""

        cache_key = self.cache.make_key(context.query, {"code": len(context.code_hits), "wsp": len(context.wsp_hits)})
        cube_tags = sorted({hit.get('cube') for hit in context.code_hits + context.wsp_hits if hit and hit.get('cube')})
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug("Advisor cache hit for query: %s", context.query)
            return AdvisorResult(**cached)

        # Step 1: WSP Master Analysis - Comprehensive protocol guidance
        wsp_analysis = self.wsp_master.analyze_query(context.query, context.code_hits)
        logger.debug("WSP Master analysis completed: intent=%s, risk=%s",
                    wsp_analysis.intent_category, wsp_analysis.risk_level)

        # Step 2: LLM Analysis - Intelligent code understanding
        prompt = build_compliance_prompt(context.query, context.code_hits, context.wsp_hits)
        llm_analysis = None
        try:
            llm_analysis = self.llm_engine.analyze_code_context(
                query=context.query,
                code_snippets=[hit.get('content', '')[:500] for hit in context.code_hits[:5]],
                wsp_guidance=[hit.get('content', '')[:300] for hit in context.wsp_hits[:3]]
            )
            logger.debug("LLM analysis completed successfully")
        except Exception as e:
            logger.warning(f"LLM analysis failed, falling back to rules engine: {e}")

        # Step 3: Rules Engine Fallback - Compliance checking
        rules_guidance = self.rules_engine.generate_contextual_guidance(
            context.query,
            context.code_hits,
            {"wsp_hits": context.wsp_hits}
        )

        # Step 4: Pattern Coach - Behavioral coaching
        # Note: Pattern coach is handled at CLI level for now, but could be integrated here

        # Combine all guidance sources
        guidance = self._synthesize_guidance(llm_analysis, wsp_analysis, rules_guidance)
        todos = self._synthesize_todos(llm_analysis, wsp_analysis, rules_guidance)
        reminders = self._synthesize_reminders(wsp_analysis, rules_guidance)

        # Add test-specific guidance
        query_lower = context.query.lower()
        if ('test' in query_lower) and "Review FMAS plan: WSP_framework/docs/testing/HOLOINDEX_QWEN_ADVISOR_FMAS_PLAN.md" not in todos:
            todos.append("Review FMAS plan: WSP_framework/docs/testing/HOLOINDEX_QWEN_ADVISOR_FMAS_PLAN.md")

        # Calculate confidence based on guidance sources
        confidence = self._calculate_confidence(llm_analysis, wsp_analysis)

        # Include violation information
        violations = []
        for violation in rules_guidance.get("violations", []):
            violations.append(f"[{violation['wsp_reference']}] {violation['guidance']}")

        result = AdvisorResult(
            guidance=guidance,
            reminders=reminders,
            todos=todos,
            metadata={
                "prompt": prompt,
                "model_path": str(self.config.model_path),
                "cache_key": cache_key,
                "cubes": cube_tags,
                "risk_level": wsp_analysis.risk_level,
                "violations": violations,
                "intent": {"category": wsp_analysis.intent_category, "prevention_focus": wsp_analysis.prevention_focus},
                "llm_used": llm_analysis is not None,
                "llm_confidence": confidence,
                "llm_model": llm_analysis.get("model_used") if llm_analysis else None,
                "wsp_analysis": {
                    "suggested_wsps": wsp_analysis.suggested_wsps,
                    "relevance_scores": wsp_analysis.wsp_relevance
                },
            },
        )

        self.cache.set(cache_key, result.__dict__)
        record_advisor_event(self.config.telemetry_path, {
            "query": context.query,
            "reminder_count": len(reminders),
            "todo_count": len(todos),
            "cubes": cube_tags,
            "llm_used": llm_analysis is not None,
            "intent": wsp_analysis.intent_category,
            "risk_level": wsp_analysis.risk_level,
        })

        return result

    def _synthesize_guidance(self, llm_analysis, wsp_analysis, rules_guidance) -> str:
        """Synthesize guidance from all sources."""
        guidance_parts = []

        # Primary: LLM analysis (if available)
        if llm_analysis and llm_analysis.get("guidance"):
            guidance_parts.append(llm_analysis["guidance"])
        else:
            # Secondary: WSP Master guidance
            wsp_guidance_items = self.wsp_master.generate_comprehensive_guidance(wsp_analysis)
            if wsp_guidance_items:
                top_guidance = wsp_guidance_items[0]
                guidance_parts.append(f"{top_guidance.wsp_reference}: {top_guidance.guidance}")

        # Tertiary: Rules engine fallback
        if not guidance_parts:
            guidance_parts.append(rules_guidance.get("primary_guidance", "Query processed. Follow WSP protocols."))

        return " ".join(guidance_parts)

    def _synthesize_todos(self, llm_analysis, wsp_analysis, rules_guidance) -> List[str]:
        """Synthesize TODOs from all sources."""
        todos = []

        # From rules engine
        todos.extend(rules_guidance.get("action_items", []))

        # From LLM recommendations
        if llm_analysis and llm_analysis.get("recommendations"):
            todos.extend(llm_analysis["recommendations"])

        # From WSP Master
        wsp_guidance_items = self.wsp_master.generate_comprehensive_guidance(wsp_analysis)
        for guidance in wsp_guidance_items[:2]:  # Top 2 WSP items
            todos.extend(guidance.action_items)

        return list(set(todos))  # Remove duplicates

    def _synthesize_reminders(self, wsp_analysis, rules_guidance) -> List[str]:
        """Synthesize reminders from WSP and rules sources."""
        reminders = []

        # From rules engine
        for reminder in rules_guidance.get("reminders", []):
            reminders.append(f"{reminder['wsp_reference']}: {reminder['guidance']}")

        # From WSP Master
        wsp_guidance_items = self.wsp_master.generate_comprehensive_guidance(wsp_analysis)
        for guidance in wsp_guidance_items[:3]:  # Top 3 WSP items
            if guidance.priority in ['CRITICAL', 'HIGH']:
                reminders.append(f"{guidance.wsp_reference}: {guidance.guidance}")

        return list(set(reminders))  # Remove duplicates

    def _calculate_confidence(self, llm_analysis, wsp_analysis) -> float:
        """Calculate overall confidence in the guidance."""
        confidence = 0.3  # Base confidence

        # LLM confidence
        if llm_analysis:
            confidence += llm_analysis.get("confidence", 0.5) * 0.4

        # WSP relevance confidence
        if wsp_analysis and wsp_analysis.wsp_relevance:
            max_relevance = max(wsp_analysis.wsp_relevance.values())
            confidence += max_relevance * 0.3

        # Risk level adjustment
        risk_multiplier = {'LOW': 1.0, 'MEDIUM': 0.9, 'HIGH': 0.8, 'CRITICAL': 0.7}
        confidence *= risk_multiplier.get(wsp_analysis.risk_level, 1.0)

        return min(confidence, 1.0)
