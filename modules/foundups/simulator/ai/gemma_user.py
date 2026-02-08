"""Gemma User Brain - Fast investment decisions.

Uses Gemma 3 270M for:
- Evaluating FoundUp quality signals (50-100ms)
- Deciding like/stake amounts based on confidence
- Binary classification for investment decisions
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .llm_inference import SimulatorLLM
from .cabr_estimator import CABRScore

logger = logging.getLogger(__name__)


@dataclass
class InvestmentDecision:
    """Decision on whether/how much to invest in a FoundUp."""

    action: str  # "like", "stake", "follow", "skip"
    amount: int  # Tokens to stake (if staking)
    confidence: float  # 0-1
    reasoning: str


@dataclass
class FoundUpSignals:
    """Quality signals for a FoundUp."""

    foundup_id: str
    name: str
    token_symbol: str
    likes: int
    stakes: int
    total_staked: int
    tasks_completed: int
    tasks_total: int
    cabr_score: Optional[CABRScore] = None


class GemmaUserBrain:
    """AI-driven user agent brain using Gemma."""

    # Investment thresholds
    LIKE_THRESHOLD = 0.3
    FOLLOW_THRESHOLD = 0.5
    STAKE_THRESHOLD = 0.6

    def __init__(self, use_ai: bool = True, risk_tolerance: float = 0.5) -> None:
        """Initialize user brain.

        Args:
            use_ai: Whether to use Gemma for decisions
            risk_tolerance: 0-1, higher = more willing to stake
        """
        self._use_ai = use_ai
        self._risk_tolerance = risk_tolerance
        self._gemma: Optional[SimulatorLLM] = None

        if use_ai:
            self._gemma = SimulatorLLM.get_gemma()

        # Track investments to avoid over-concentration
        self._investments: Dict[str, int] = {}

    def evaluate_foundup(
        self,
        signals: FoundUpSignals,
        available_balance: int,
    ) -> InvestmentDecision:
        """Evaluate a FoundUp and decide on action.

        Args:
            signals: Quality signals for the FoundUp
            available_balance: Available tokens to invest

        Returns:
            InvestmentDecision with action and amount
        """
        # Try AI evaluation first
        if self._use_ai and self._gemma and self._gemma.available:
            decision = self._ai_evaluate(signals, available_balance)
            if decision:
                return decision

        # Fall back to heuristic evaluation
        return self._heuristic_evaluate(signals, available_balance)

    def _ai_evaluate(
        self,
        signals: FoundUpSignals,
        available_balance: int,
    ) -> Optional[InvestmentDecision]:
        """Use Gemma for fast evaluation."""
        # Build compact prompt for fast classification
        cabr_info = ""
        if signals.cabr_score:
            cabr_info = f"CABR: {signals.cabr_score.total:.2f}"

        prompt = f"""Evaluate FoundUp investment (answer 1-4):

{signals.name} ({signals.token_symbol})
Likes: {signals.likes}, Stakes: {signals.stakes}, Staked: {signals.total_staked}
Tasks: {signals.tasks_completed}/{signals.tasks_total} completed
{cabr_info}

1. SKIP (low potential)
2. LIKE (show interest)
3. FOLLOW (medium confidence)
4. STAKE (high confidence)

Answer:"""

        result = self._gemma.generate(prompt, max_tokens=10, temperature=0.1)

        # Parse response
        text = result.text.strip()
        try:
            for char in text:
                if char.isdigit():
                    choice = int(char)
                    if choice == 1:
                        return InvestmentDecision(
                            action="skip",
                            amount=0,
                            confidence=0.8,
                            reasoning="Gemma: low potential",
                        )
                    elif choice == 2:
                        return InvestmentDecision(
                            action="like",
                            amount=0,
                            confidence=0.6,
                            reasoning="Gemma: shows interest",
                        )
                    elif choice == 3:
                        return InvestmentDecision(
                            action="follow",
                            amount=0,
                            confidence=0.7,
                            reasoning="Gemma: medium confidence",
                        )
                    elif choice == 4:
                        # Calculate stake amount
                        stake = self._calculate_stake(signals, available_balance)
                        return InvestmentDecision(
                            action="stake",
                            amount=stake,
                            confidence=0.85,
                            reasoning="Gemma: high confidence investment",
                        )
                    break
        except Exception:
            pass

        return None

    def _heuristic_evaluate(
        self,
        signals: FoundUpSignals,
        available_balance: int,
    ) -> InvestmentDecision:
        """Heuristic evaluation based on signals."""
        # Calculate quality score
        quality = self._calculate_quality(signals)

        # Adjust for risk tolerance
        threshold_modifier = 1.0 - (self._risk_tolerance * 0.3)

        if quality < self.LIKE_THRESHOLD * threshold_modifier:
            return InvestmentDecision(
                action="skip",
                amount=0,
                confidence=0.5,
                reasoning=f"Quality {quality:.2f} below threshold",
            )
        elif quality < self.FOLLOW_THRESHOLD * threshold_modifier:
            return InvestmentDecision(
                action="like",
                amount=0,
                confidence=0.5 + quality * 0.3,
                reasoning=f"Quality {quality:.2f} - like only",
            )
        elif quality < self.STAKE_THRESHOLD * threshold_modifier:
            return InvestmentDecision(
                action="follow",
                amount=0,
                confidence=0.6 + quality * 0.2,
                reasoning=f"Quality {quality:.2f} - follow",
            )
        else:
            stake = self._calculate_stake(signals, available_balance)
            return InvestmentDecision(
                action="stake",
                amount=stake,
                confidence=0.7 + quality * 0.3,
                reasoning=f"Quality {quality:.2f} - stake {stake}",
            )

    def _calculate_quality(self, signals: FoundUpSignals) -> float:
        """Calculate quality score from signals."""
        score = 0.0

        # Social proof (likes and stakes)
        if signals.likes > 0:
            score += min(0.2, signals.likes * 0.05)
        if signals.stakes > 0:
            score += min(0.2, signals.stakes * 0.1)

        # Activity level (tasks)
        if signals.tasks_total > 0:
            completion_rate = signals.tasks_completed / signals.tasks_total
            score += completion_rate * 0.3

        # CABR score is strongest signal
        if signals.cabr_score:
            score += signals.cabr_score.total * 0.4

        return min(1.0, score)

    def _calculate_stake(
        self,
        signals: FoundUpSignals,
        available_balance: int,
    ) -> int:
        """Calculate stake amount based on signals and balance."""
        # Don't stake more than 20% of balance
        max_stake = int(available_balance * 0.2)

        # Adjust based on CABR score
        if signals.cabr_score:
            multiplier = signals.cabr_score.total
        else:
            multiplier = 0.5

        # Apply risk tolerance
        stake = int(max_stake * multiplier * (0.5 + self._risk_tolerance * 0.5))

        # Minimum stake
        stake = max(10, min(stake, max_stake))

        # Track investment
        current = self._investments.get(signals.foundup_id, 0)
        self._investments[signals.foundup_id] = current + stake

        return stake

    def rank_foundups(
        self,
        foundups: List[FoundUpSignals],
    ) -> List[Tuple[FoundUpSignals, float]]:
        """Rank FoundUps by investment potential.

        Args:
            foundups: List of FoundUp signals

        Returns:
            List of (signals, score) tuples sorted by score descending
        """
        scored = []
        for fp in foundups:
            quality = self._calculate_quality(fp)
            scored.append((fp, quality))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def get_portfolio_summary(self) -> Dict[str, int]:
        """Get summary of investments made."""
        return dict(self._investments)

    def reset_portfolio(self) -> None:
        """Reset investment tracking."""
        self._investments.clear()
