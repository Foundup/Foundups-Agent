"""Synthetic User Agent - AI-generated user for pre-launch market simulation.

Based on Simile AI research ($100M Series A, Feb 2026):
- Synthetic personas simulate real user behaviors, preferences, and decisions
- Created from demographic data, behavioral patterns, survey responses
- Acts as proxy for real customers before launch

See: modules/foundups/simulator/docs/SYNTHETIC_PERSONAS_RESEARCH.md
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from .base_agent import BaseSimAgent

if TYPE_CHECKING:
    from ..adapters.fam_bridge import FAMBridge
    from ..adapters.phantom_plugs import PhantomTokenEconomy, PhantomSocialActions
    from ..state_store import StateStore

logger = logging.getLogger(__name__)


class IncomeLevel(Enum):
    """Income bracket for price sensitivity."""
    LOW = "low"          # < $30k - very price sensitive
    MEDIUM = "medium"    # $30k-$100k - moderately sensitive
    HIGH = "high"        # $100k+ - less sensitive


class TechSavviness(Enum):
    """Technical sophistication level."""
    NOVICE = "novice"      # Needs simple UI, skeptical of new tech
    INTERMEDIATE = "intermediate"  # Comfortable with apps
    ADVANCED = "advanced"  # Early adopter, loves new tech


class RiskTolerance(Enum):
    """Willingness to try new products."""
    CONSERVATIVE = "conservative"  # Needs lots of social proof
    MODERATE = "moderate"          # Some proof needed
    ADVENTUROUS = "adventurous"    # Early adopter


@dataclass
class SyntheticPersona:
    """AI-generated user persona with behavioral attributes.

    Simile-style: Build digital twins simulating real behaviors.
    """
    # Demographics
    income_level: IncomeLevel = IncomeLevel.MEDIUM
    tech_savviness: TechSavviness = TechSavviness.INTERMEDIATE
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE

    # Pain points (what they're looking for)
    pain_points: List[str] = field(default_factory=list)

    # Network size (for viral coefficient)
    network_size: int = 100

    # Engagement patterns
    daily_app_time_minutes: int = 60  # How much time they spend on apps
    purchase_frequency_per_month: int = 3  # How often they buy things

    @classmethod
    def random(cls) -> "SyntheticPersona":
        """Generate a random persona with realistic distribution."""
        return cls(
            income_level=random.choices(
                list(IncomeLevel),
                weights=[0.4, 0.45, 0.15],  # More low/medium than high
            )[0],
            tech_savviness=random.choices(
                list(TechSavviness),
                weights=[0.3, 0.5, 0.2],  # Bell curve
            )[0],
            risk_tolerance=random.choices(
                list(RiskTolerance),
                weights=[0.4, 0.4, 0.2],  # Most are conservative/moderate
            )[0],
            pain_points=random.sample([
                "cost_savings", "time_savings", "community",
                "ownership", "transparency", "sustainability",
                "local_support", "peer_connection", "fair_pricing",
            ], k=random.randint(1, 3)),
            network_size=int(random.gauss(150, 100)),  # Dunbar number distribution
            daily_app_time_minutes=int(random.gauss(90, 45)),
            purchase_frequency_per_month=random.randint(1, 10),
        )

    def get_adoption_threshold(self) -> float:
        """Calculate CABR score threshold needed to adopt.

        Higher threshold = harder to convince.
        """
        base = 0.5  # Baseline threshold

        # Risk tolerance adjusts threshold
        if self.risk_tolerance == RiskTolerance.CONSERVATIVE:
            base += 0.2
        elif self.risk_tolerance == RiskTolerance.ADVENTUROUS:
            base -= 0.15

        # Tech savviness affects threshold
        if self.tech_savviness == TechSavviness.NOVICE:
            base += 0.1
        elif self.tech_savviness == TechSavviness.ADVANCED:
            base -= 0.1

        return max(0.3, min(0.9, base))  # Clamp to [0.3, 0.9]

    def get_price_sensitivity(self) -> float:
        """Price sensitivity multiplier (1.0 = neutral)."""
        if self.income_level == IncomeLevel.LOW:
            return 1.5  # 50% more sensitive
        elif self.income_level == IncomeLevel.HIGH:
            return 0.7  # 30% less sensitive
        return 1.0

    def get_viral_coefficient(self) -> float:
        """Expected referrals per adoption (viral coefficient)."""
        base = self.network_size / 100.0  # Normalize to ~1.0

        # Adventurous users share more
        if self.risk_tolerance == RiskTolerance.ADVENTUROUS:
            base *= 1.5
        elif self.risk_tolerance == RiskTolerance.CONSERVATIVE:
            base *= 0.5

        return min(3.0, base)  # Cap at 3.0


@dataclass
class AdoptionDecision:
    """Result of evaluating a FoundUp for adoption."""
    would_adopt: bool
    confidence: float  # 0-1
    reasons: List[str] = field(default_factory=list)
    price_sensitivity: float = 1.0
    viral_coefficient: float = 1.0


class SyntheticUserAgent(BaseSimAgent):
    """AI-generated user that simulates adoption behavior.

    Used for pre-launch market testing (Simile AI pattern):
    - Evaluate FoundUps based on persona attributes
    - Emit adoption/rejection events for CABR V1 validation
    - Model realistic user acquisition funnel
    """

    def __init__(
        self,
        agent_id: str,
        fam_bridge: "FAMBridge",
        token_economy: "PhantomTokenEconomy",
        social_actions: "PhantomSocialActions",
        state_store: "StateStore",
        persona: Optional[SyntheticPersona] = None,
        **kwargs,
    ) -> None:
        """Initialize synthetic user agent.

        Args:
            agent_id: Unique agent identifier
            fam_bridge: Bridge to FAM modules
            token_economy: Phantom token economy
            social_actions: Phantom social actions
            state_store: State store for recording actions
            persona: Pre-defined persona or None for random
        """
        super().__init__(
            agent_id=agent_id,
            fam_bridge=fam_bridge,
            token_economy=token_economy,
            social_actions=social_actions,
            state_store=state_store,
            action_probability=0.2,  # Lower action rate - more deliberate
            cooldown_ticks=10,       # Longer cooldown - realistic decision time
            **kwargs,
        )

        # Generate or use provided persona
        self.persona = persona or SyntheticPersona.random()
        self._adoption_threshold = self.persona.get_adoption_threshold()

        # Track evaluations
        self._evaluated_foundups: Dict[str, AdoptionDecision] = {}
        self._adopted_foundups: List[str] = []
        self._rejected_foundups: List[str] = []

        logger.debug(
            f"[SYNTH] {agent_id} created: "
            f"income={self.persona.income_level.value}, "
            f"tech={self.persona.tech_savviness.value}, "
            f"risk={self.persona.risk_tolerance.value}, "
            f"threshold={self._adoption_threshold:.2f}"
        )

    @property
    def agent_type(self) -> str:
        return "synthetic_user"

    def _choose_action(self, tick: int) -> Optional[str]:
        """Choose action - evaluate FoundUps for potential adoption."""
        foundups = self._state_store.get_foundup_ids()

        # Find FoundUps we haven't evaluated yet
        unevaluated = [
            f for f in foundups
            if f not in self._evaluated_foundups
        ]

        if unevaluated:
            return "evaluate"

        # Maybe re-evaluate an adopted FoundUp for continued engagement
        if self._adopted_foundups and random.random() < 0.3:
            return "engage"

        return None

    def _perform_action(self, action: str, tick: int) -> bool:
        """Perform the chosen action."""
        if action == "evaluate":
            return self._do_evaluate(tick)
        elif action == "engage":
            return self._do_engage(tick)
        return False

    def _do_evaluate(self, tick: int) -> bool:
        """Evaluate a FoundUp for adoption (Simile-style)."""
        foundups = self._state_store.get_foundup_ids()
        unevaluated = [
            f for f in foundups
            if f not in self._evaluated_foundups
        ]

        if not unevaluated:
            return False

        foundup_id = random.choice(unevaluated)
        decision = self.evaluate_foundup(foundup_id)

        self._evaluated_foundups[foundup_id] = decision

        # Emit event for CABR V1 integration
        if decision.would_adopt:
            self._adopted_foundups.append(foundup_id)
            self._emit_adoption_event(foundup_id, decision, tick)
            logger.debug(
                f"[SYNTH] {self.agent_id} ADOPTED {foundup_id} "
                f"(conf={decision.confidence:.2f}, reasons={decision.reasons})"
            )
        else:
            self._rejected_foundups.append(foundup_id)
            self._emit_rejection_event(foundup_id, decision, tick)
            logger.debug(
                f"[SYNTH] {self.agent_id} REJECTED {foundup_id} "
                f"(conf={decision.confidence:.2f}, reasons={decision.reasons})"
            )

        return True

    def evaluate_foundup(self, foundup_id: str) -> AdoptionDecision:
        """Evaluate a FoundUp - would this persona adopt?

        Simile-style evaluation based on:
        - CABR score vs adoption threshold
        - Pain point alignment
        - Price sensitivity
        - Social proof (likes, stakes)
        """
        state = self._state_store.get_state()
        tile = state.foundups.get(foundup_id)

        if not tile:
            return AdoptionDecision(
                would_adopt=False,
                confidence=0.0,
                reasons=["foundup_not_found"],
            )

        reasons = []
        score_factors = []

        # 1. Check CABR score (if available)
        cabr_score = getattr(tile, 'cabr_score', None) or 0.5
        if cabr_score >= self._adoption_threshold:
            score_factors.append(1.0)
            reasons.append("cabr_threshold_met")
        else:
            score_factors.append(0.3)
            reasons.append("cabr_below_threshold")

        # 2. Social proof (likes and stakes)
        likes = getattr(tile, 'likes', 0)
        stakes = getattr(tile, 'stakes', 0)

        social_proof = min(1.0, (likes + stakes * 2) / 50.0)
        if self.persona.risk_tolerance == RiskTolerance.CONSERVATIVE:
            # Conservative users need more proof
            if social_proof < 0.5:
                score_factors.append(0.2)
                reasons.append("insufficient_social_proof")
            else:
                score_factors.append(0.8)
                reasons.append("social_proof_validated")
        else:
            score_factors.append(0.5 + social_proof * 0.5)

        # 3. Task completion rate (signals working product)
        tasks_completed = getattr(tile, 'tasks_completed', 0)
        task_count = getattr(tile, 'task_count', 1) or 1
        completion_rate = tasks_completed / task_count

        if completion_rate > 0.5:
            score_factors.append(0.8)
            reasons.append("active_development")
        elif completion_rate > 0.2:
            score_factors.append(0.5)
            reasons.append("early_development")
        else:
            score_factors.append(0.3)
            reasons.append("minimal_progress")

        # 4. Pain point alignment (random for now - could be smarter)
        if random.random() < 0.6:  # 60% chance of alignment
            score_factors.append(0.8)
            reasons.append("pain_point_aligned")
        else:
            score_factors.append(0.4)
            reasons.append("pain_point_mismatch")

        # Calculate final confidence
        confidence = sum(score_factors) / len(score_factors) if score_factors else 0.5
        would_adopt = confidence >= self._adoption_threshold * 0.8  # Slight flexibility

        return AdoptionDecision(
            would_adopt=would_adopt,
            confidence=confidence,
            reasons=reasons,
            price_sensitivity=self.persona.get_price_sensitivity(),
            viral_coefficient=self.persona.get_viral_coefficient(),
        )

    def _emit_adoption_event(
        self,
        foundup_id: str,
        decision: AdoptionDecision,
        tick: int,
    ) -> None:
        """Emit synthetic_user_adopted event for CABR V1."""
        try:
            from modules.foundups.agent_market.src.fam_daemon import get_fam_daemon
            daemon = get_fam_daemon()
            daemon.emit_custom_event("synthetic_user_adopted", {
                "agent_id": self.agent_id,
                "foundup_id": foundup_id,
                "confidence": decision.confidence,
                "reasons": decision.reasons,
                "price_sensitivity": decision.price_sensitivity,
                "viral_coefficient": decision.viral_coefficient,
                "persona_income": self.persona.income_level.value,
                "persona_tech": self.persona.tech_savviness.value,
                "persona_risk": self.persona.risk_tolerance.value,
                "tick": tick,
            })
        except Exception as e:
            logger.debug(f"[SYNTH] Could not emit adoption event: {e}")

    def _emit_rejection_event(
        self,
        foundup_id: str,
        decision: AdoptionDecision,
        tick: int,
    ) -> None:
        """Emit synthetic_user_rejected event for CABR V1."""
        try:
            from modules.foundups.agent_market.src.fam_daemon import get_fam_daemon
            daemon = get_fam_daemon()
            daemon.emit_custom_event("synthetic_user_rejected", {
                "agent_id": self.agent_id,
                "foundup_id": foundup_id,
                "confidence": decision.confidence,
                "reasons": decision.reasons,
                "persona_income": self.persona.income_level.value,
                "persona_tech": self.persona.tech_savviness.value,
                "persona_risk": self.persona.risk_tolerance.value,
                "tick": tick,
            })
        except Exception as e:
            logger.debug(f"[SYNTH] Could not emit rejection event: {e}")

    def _do_engage(self, tick: int) -> bool:
        """Engage with an adopted FoundUp (like, follow, stake)."""
        if not self._adopted_foundups:
            return False

        foundup_id = random.choice(self._adopted_foundups)

        # Simple engagement - like the FoundUp
        success, _ = self._social.like(self.agent_id, foundup_id)
        if success:
            self._state_store.record_like(self.agent_id, foundup_id)
            logger.debug(f"[SYNTH] {self.agent_id} engaged with {foundup_id}")

        return success

    def get_stats(self) -> dict:
        """Get synthetic user statistics."""
        return {
            "persona": {
                "income": self.persona.income_level.value,
                "tech": self.persona.tech_savviness.value,
                "risk": self.persona.risk_tolerance.value,
            },
            "adoption_threshold": self._adoption_threshold,
            "evaluated": len(self._evaluated_foundups),
            "adopted": len(self._adopted_foundups),
            "rejected": len(self._rejected_foundups),
            "adoption_rate": (
                len(self._adopted_foundups) / len(self._evaluated_foundups)
                if self._evaluated_foundups else 0.0
            ),
            "balance": self.get_balance(),
        }
