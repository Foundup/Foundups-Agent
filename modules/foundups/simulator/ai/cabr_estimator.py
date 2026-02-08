"""CABR Score Estimator for FoundUps.

Estimates Conscious Autonomous Benefit Rate scores:
- env_score: Environmental impact (0-1)
- soc_score: Social impact (0-1)
- part_score: Participation metrics (0-1, derived from FAM data)

Uses Qwen for impact analysis when available, falls back to heuristics.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, Optional

from .llm_inference import SimulatorLLM

logger = logging.getLogger(__name__)

# CABR consensus threshold (golden ratio)
CABR_THRESHOLD = 0.618


@dataclass
class CABRScore:
    """CABR score breakdown for a FoundUp."""

    foundup_id: str
    env_score: float  # Environmental impact (0-1)
    soc_score: float  # Social impact (0-1)
    part_score: float  # Participation (0-1)
    total: float  # Weighted average
    confidence: float  # How confident are we in this score
    reasoning: str  # Why this score


@dataclass
class FoundUpIdea:
    """A FoundUp idea with pain/outcome analysis."""

    name: str
    token_symbol: str
    pain_point: str  # What problem does it solve
    outcome: str  # What's the positive outcome
    category: str  # "defi", "social", "infrastructure", "creative", etc.
    team_size: int  # Estimated agents needed
    total_supply: int  # Token total supply
    initial_allocation: Dict[str, float]  # treasury, team, community, etc.


class CABREstimator:
    """Estimates CABR scores for FoundUps using AI analysis."""

    # Default weights (can evolve via CABR_DAE)
    WEIGHTS = {
        "env": 0.33,
        "soc": 0.33,
        "part": 0.34,
    }

    # Category impact baselines
    CATEGORY_BASELINES = {
        "defi": {"env": 0.2, "soc": 0.6},
        "social": {"env": 0.1, "soc": 0.8},
        "infrastructure": {"env": 0.5, "soc": 0.5},
        "creative": {"env": 0.1, "soc": 0.7},
        "environment": {"env": 0.9, "soc": 0.5},
        "governance": {"env": 0.2, "soc": 0.7},
        "education": {"env": 0.1, "soc": 0.9},
    }

    def __init__(self, use_ai: bool = True) -> None:
        """Initialize CABR estimator.

        Args:
            use_ai: Whether to use Qwen for analysis (if available)
        """
        self._use_ai = use_ai
        self._qwen: Optional[SimulatorLLM] = None

        if use_ai:
            self._qwen = SimulatorLLM.get_qwen()

    def estimate_idea_cabr(self, idea: FoundUpIdea) -> CABRScore:
        """Estimate CABR score for a FoundUp idea.

        Args:
            idea: The FoundUp idea to analyze

        Returns:
            CABRScore with breakdown
        """
        # Try AI analysis first
        if self._use_ai and self._qwen and self._qwen.available:
            return self._ai_estimate(idea)

        # Fall back to heuristic estimation
        return self._heuristic_estimate(idea)

    def _ai_estimate(self, idea: FoundUpIdea) -> CABRScore:
        """Use Qwen to analyze idea impact."""
        prompt = f"""Analyze this FoundUp project for CABR scoring:

Name: {idea.name}
Pain Point: {idea.pain_point}
Outcome: {idea.outcome}
Category: {idea.category}

Rate each dimension from 0.0 to 1.0:
1. Environmental Impact (resource efficiency, emissions, sustainability)
2. Social Impact (accessibility, empowerment, community benefit)

Respond in JSON format:
{{"env": 0.X, "soc": 0.X, "reasoning": "brief explanation"}}"""

        result = self._qwen.generate(prompt, max_tokens=150, temperature=0.3)

        # Parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', result.text)
            if json_match:
                data = json.loads(json_match.group())
                env_score = float(data.get("env", 0.5))
                soc_score = float(data.get("soc", 0.5))
                reasoning = data.get("reasoning", "AI analysis")

                # Clamp to valid range
                env_score = max(0.0, min(1.0, env_score))
                soc_score = max(0.0, min(1.0, soc_score))

                # Part score starts at 0 (no activity yet)
                part_score = 0.0

                total = self._calculate_total(env_score, soc_score, part_score)

                return CABRScore(
                    foundup_id=idea.name,
                    env_score=env_score,
                    soc_score=soc_score,
                    part_score=part_score,
                    total=total,
                    confidence=0.7,  # AI analysis confidence
                    reasoning=reasoning,
                )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.debug(f"[CABR] Failed to parse AI response: {e}")

        # Fall back to heuristic
        return self._heuristic_estimate(idea)

    def _heuristic_estimate(self, idea: FoundUpIdea) -> CABRScore:
        """Heuristic CABR estimation based on category and keywords."""
        # Get baseline from category
        baseline = self.CATEGORY_BASELINES.get(
            idea.category.lower(),
            {"env": 0.3, "soc": 0.5}
        )

        env_score = baseline["env"]
        soc_score = baseline["soc"]

        # Keyword modifiers
        pain_lower = idea.pain_point.lower()
        outcome_lower = idea.outcome.lower()

        # Environmental keywords
        env_keywords = ["carbon", "emission", "sustainable", "green", "renewable", "recycle"]
        for kw in env_keywords:
            if kw in pain_lower or kw in outcome_lower:
                env_score = min(1.0, env_score + 0.15)

        # Social keywords
        soc_keywords = ["access", "empower", "community", "education", "affordable", "open"]
        for kw in soc_keywords:
            if kw in pain_lower or kw in outcome_lower:
                soc_score = min(1.0, soc_score + 0.1)

        # Decentralization bonus
        if "decentralized" in pain_lower or "decentralized" in outcome_lower:
            soc_score = min(1.0, soc_score + 0.15)

        # Part score starts at 0 (no activity yet)
        part_score = 0.0

        total = self._calculate_total(env_score, soc_score, part_score)

        return CABRScore(
            foundup_id=idea.name,
            env_score=round(env_score, 2),
            soc_score=round(soc_score, 2),
            part_score=part_score,
            total=round(total, 2),
            confidence=0.5,  # Heuristic confidence
            reasoning=f"Heuristic: {idea.category} category baseline with keyword modifiers",
        )

    def update_participation(
        self,
        score: CABRScore,
        tasks_completed: int,
        tasks_total: int,
        active_agents: int,
        verifications: int,
    ) -> CABRScore:
        """Update CABR score with participation metrics.

        Args:
            score: Existing CABR score
            tasks_completed: Number of completed tasks
            tasks_total: Total tasks created
            active_agents: Number of active agents
            verifications: Number of verification events

        Returns:
            Updated CABRScore with part_score
        """
        if tasks_total == 0:
            part_score = 0.0
        else:
            # Participation formula from WSP 29
            completion_rate = tasks_completed / tasks_total
            verification_rate = min(1.0, verifications / max(1, tasks_completed))
            contributor_factor = min(1.0, active_agents / 10)  # Normalize to 10 agents

            part_score = (
                completion_rate * 0.25 +
                verification_rate * 0.25 +
                contributor_factor * 0.20 +
                0.15 +  # Placeholder for governance
                0.15   # Placeholder for cross-foundup
            )

        new_total = self._calculate_total(score.env_score, score.soc_score, part_score)

        return CABRScore(
            foundup_id=score.foundup_id,
            env_score=score.env_score,
            soc_score=score.soc_score,
            part_score=round(part_score, 2),
            total=round(new_total, 2),
            confidence=score.confidence,
            reasoning=f"{score.reasoning} + participation metrics",
        )

    def _calculate_total(
        self,
        env_score: float,
        soc_score: float,
        part_score: float,
    ) -> float:
        """Calculate weighted CABR total."""
        return (
            self.WEIGHTS["env"] * env_score +
            self.WEIGHTS["soc"] * soc_score +
            self.WEIGHTS["part"] * part_score
        )

    def meets_threshold(self, score: CABRScore) -> bool:
        """Check if score meets consensus threshold (0.618)."""
        return score.total >= CABR_THRESHOLD
