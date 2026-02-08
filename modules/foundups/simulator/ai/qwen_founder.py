"""Qwen Founder Brain - Strategic FoundUp idea generation.

Uses Qwen 1.5B for:
- Generating FoundUp ideas with pain/outcome analysis
- Planning token economics
- Estimating team requirements
- Creating substantive tasks
"""

from __future__ import annotations

import json
import logging
import random
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .llm_inference import SimulatorLLM
from .cabr_estimator import FoundUpIdea, CABREstimator, CABRScore

logger = logging.getLogger(__name__)

# Sample problem domains for idea generation
PROBLEM_DOMAINS = [
    {
        "domain": "video",
        "pains": [
            "Centralized video platforms control creator monetization",
            "Video hosting is expensive and controlled by gatekeepers",
            "Content creators have no ownership of their audience data",
        ],
        "outcomes": [
            "Decentralized video hosting owned by users",
            "Creator-owned monetization without platform cuts",
            "Portable audience relationships across platforms",
        ],
    },
    {
        "domain": "social",
        "pains": [
            "Social media algorithms prioritize engagement over wellbeing",
            "User data is harvested without consent or compensation",
            "Platform lock-in prevents community portability",
        ],
        "outcomes": [
            "User-controlled algorithmic feeds",
            "Data ownership with fair compensation",
            "Portable social graphs across platforms",
        ],
    },
    {
        "domain": "finance",
        "pains": [
            "Banking excludes billions of unbanked people",
            "Cross-border payments are slow and expensive",
            "Traditional finance has high barriers to entry",
        ],
        "outcomes": [
            "Accessible financial services for the unbanked",
            "Instant, low-cost global payments",
            "Democratized access to financial instruments",
        ],
    },
    {
        "domain": "environment",
        "pains": [
            "Carbon tracking is opaque and unverifiable",
            "Renewable energy markets are fragmented",
            "Sustainability claims lack accountability",
        ],
        "outcomes": [
            "Transparent, verifiable carbon accounting",
            "Unified renewable energy marketplace",
            "Accountable sustainability with proof-of-impact",
        ],
    },
    {
        "domain": "education",
        "pains": [
            "Quality education is geographically limited",
            "Credentials are non-portable and siloed",
            "Tutoring is expensive and inaccessible",
        ],
        "outcomes": [
            "Global access to quality education",
            "Portable, verifiable credentials",
            "Affordable peer-to-peer tutoring networks",
        ],
    },
    {
        "domain": "infrastructure",
        "pains": [
            "Cloud computing is controlled by few providers",
            "DNS and identity systems are centralized",
            "Storage costs are unpredictable and high",
        ],
        "outcomes": [
            "Decentralized compute networks",
            "Self-sovereign identity systems",
            "Predictable, distributed storage",
        ],
    },
]

# Token symbol patterns
TOKEN_SYMBOLS = [
    "VID", "SOC", "PAY", "GRN", "EDU", "NET",
    "DATA", "FUND", "CRED", "STOR", "AUTH", "MESH",
    "FLOW", "LINK", "NODE", "SYNC", "CORE", "WAVE",
]


@dataclass
class TokenEconomics:
    """Token economics for a FoundUp."""

    symbol: str
    total_supply: int
    allocation: Dict[str, float]  # Percentages
    initial_price_usd: float
    vesting_months: int


class QwenFounderBrain:
    """AI-driven founder agent brain using Qwen."""

    def __init__(self, use_ai: bool = True) -> None:
        """Initialize founder brain.

        Args:
            use_ai: Whether to use Qwen for idea generation
        """
        self._use_ai = use_ai
        self._qwen: Optional[SimulatorLLM] = None
        self._cabr = CABREstimator(use_ai=use_ai)

        if use_ai:
            self._qwen = SimulatorLLM.get_qwen()

        # Track generated ideas to avoid duplicates
        self._generated_ideas: List[str] = []

    def generate_foundup_idea(
        self,
        seed_domain: Optional[str] = None,
    ) -> Tuple[FoundUpIdea, CABRScore]:
        """Generate a FoundUp idea with CABR score.

        Args:
            seed_domain: Optional domain to focus on

        Returns:
            (FoundUpIdea, CABRScore) tuple
        """
        # Pick a domain
        if seed_domain:
            domain = next(
                (d for d in PROBLEM_DOMAINS if d["domain"] == seed_domain),
                random.choice(PROBLEM_DOMAINS)
            )
        else:
            domain = random.choice(PROBLEM_DOMAINS)

        # Try AI generation first
        if self._use_ai and self._qwen and self._qwen.available:
            idea = self._ai_generate_idea(domain)
            if idea:
                cabr = self._cabr.estimate_idea_cabr(idea)
                return (idea, cabr)

        # Fall back to template generation
        idea = self._template_generate_idea(domain)
        cabr = self._cabr.estimate_idea_cabr(idea)
        return (idea, cabr)

    def _ai_generate_idea(self, domain: Dict) -> Optional[FoundUpIdea]:
        """Use Qwen to generate a FoundUp idea."""
        pain = random.choice(domain["pains"])
        outcome = random.choice(domain["outcomes"])

        prompt = f"""Create a FoundUp project to solve this problem:

Pain Point: {pain}
Desired Outcome: {outcome}

Generate a creative project with:
1. A catchy name (1-2 words)
2. A 3-4 letter token symbol
3. Team size needed (1-10)
4. Total token supply (millions)

Respond in JSON:
{{"name": "ProjectName", "symbol": "SYM", "team_size": N, "supply_millions": N}}"""

        result = self._qwen.generate(prompt, max_tokens=100, temperature=0.7)

        try:
            json_match = re.search(r'\{[^}]+\}', result.text)
            if json_match:
                data = json.loads(json_match.group())

                name = data.get("name", f"{domain['domain'].title()}Net")
                symbol = data.get("symbol", random.choice(TOKEN_SYMBOLS))[:4].upper()
                team_size = max(1, min(10, int(data.get("team_size", 3))))
                supply = int(data.get("supply_millions", 21)) * 1_000_000

                # Avoid duplicates
                if name in self._generated_ideas:
                    name = f"{name}_{len(self._generated_ideas)}"
                self._generated_ideas.append(name)

                return FoundUpIdea(
                    name=name,
                    token_symbol=symbol,
                    pain_point=pain,
                    outcome=outcome,
                    category=domain["domain"],
                    team_size=team_size,
                    total_supply=supply,
                    initial_allocation={
                        "treasury": 0.30,
                        "team": 0.15,
                        "community": 0.40,
                        "liquidity": 0.15,
                    },
                )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.debug(f"[QWEN-FOUNDER] Failed to parse AI idea: {e}")

        return None

    def _template_generate_idea(self, domain: Dict) -> FoundUpIdea:
        """Generate idea from templates."""
        pain = random.choice(domain["pains"])
        outcome = random.choice(domain["outcomes"])

        # Generate name from domain
        suffixes = ["Net", "Hub", "Chain", "DAO", "Protocol", "Labs", "Fi"]
        name = f"{domain['domain'].title()}{random.choice(suffixes)}"

        # Avoid duplicates
        if name in self._generated_ideas:
            name = f"{name}_{len(self._generated_ideas)}"
        self._generated_ideas.append(name)

        symbol = random.choice(TOKEN_SYMBOLS)

        return FoundUpIdea(
            name=name,
            token_symbol=symbol,
            pain_point=pain,
            outcome=outcome,
            category=domain["domain"],
            team_size=random.randint(2, 5),
            total_supply=21_000_000,
            initial_allocation={
                "treasury": 0.30,
                "team": 0.15,
                "community": 0.40,
                "liquidity": 0.15,
            },
        )

    def generate_task(
        self,
        foundup_name: str,
        category: str,
        task_number: int,
    ) -> Dict[str, any]:
        """Generate a substantive task for a FoundUp.

        Args:
            foundup_name: Name of the FoundUp
            category: FoundUp category
            task_number: Task sequence number

        Returns:
            Task dict with title, description, reward
        """
        # Try AI generation
        if self._use_ai and self._qwen and self._qwen.available:
            task = self._ai_generate_task(foundup_name, category, task_number)
            if task:
                return task

        # Fall back to templates
        return self._template_generate_task(foundup_name, category, task_number)

    def _ai_generate_task(
        self,
        foundup_name: str,
        category: str,
        task_number: int,
    ) -> Optional[Dict]:
        """Use Qwen to generate a task."""
        prompt = f"""Create task #{task_number} for {foundup_name} ({category} project):

Generate a specific, actionable task with:
1. Clear title (5-10 words)
2. Brief description (1-2 sentences)
3. Reward in tokens (10-100)

Respond in JSON:
{{"title": "...", "description": "...", "reward": N}}"""

        result = self._qwen.generate(prompt, max_tokens=100, temperature=0.6)

        try:
            json_match = re.search(r'\{[^}]+\}', result.text)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "title": data.get("title", f"Task {task_number}"),
                    "description": data.get("description", "Complete this task"),
                    "reward": max(10, min(100, int(data.get("reward", 25)))),
                }
        except Exception:
            pass

        return None

    def _template_generate_task(
        self,
        foundup_name: str,
        category: str,
        task_number: int,
    ) -> Dict:
        """Generate task from templates."""
        task_templates = {
            "video": [
                "Implement video upload endpoint",
                "Add transcoding worker",
                "Create thumbnail generator",
                "Build playback component",
            ],
            "social": [
                "Design user profile page",
                "Implement follow system",
                "Add notification service",
                "Create content feed algorithm",
            ],
            "finance": [
                "Implement wallet connect",
                "Add swap functionality",
                "Create liquidity pool",
                "Build transaction history",
            ],
            "environment": [
                "Integrate carbon API",
                "Build verification dashboard",
                "Create impact calculator",
                "Add certificate generator",
            ],
            "education": [
                "Design course structure",
                "Implement progress tracking",
                "Add quiz functionality",
                "Create certificate system",
            ],
            "infrastructure": [
                "Set up node network",
                "Implement consensus layer",
                "Add storage protocol",
                "Create monitoring dashboard",
            ],
        }

        templates = task_templates.get(category, task_templates["infrastructure"])
        title = templates[task_number % len(templates)]

        return {
            "title": f"{title} for {foundup_name}",
            "description": f"Task {task_number}: {title}. Deliver working implementation.",
            "reward": random.randint(10, 50),
        }

    def plan_token_economics(self, idea: FoundUpIdea) -> TokenEconomics:
        """Plan token economics for a FoundUp.

        Args:
            idea: The FoundUp idea

        Returns:
            TokenEconomics with allocation details
        """
        # Standard allocation (can be AI-optimized later)
        return TokenEconomics(
            symbol=idea.token_symbol,
            total_supply=idea.total_supply,
            allocation={
                "treasury": 0.30,  # DAO-controlled
                "team": 0.15,      # Founders + early contributors
                "community": 0.40, # Task rewards + staking
                "liquidity": 0.15, # DEX liquidity provision
            },
            initial_price_usd=0.01,  # Starting price
            vesting_months=24,  # Team vesting period
        )
