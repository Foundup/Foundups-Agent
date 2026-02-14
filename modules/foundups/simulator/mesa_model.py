"""Mesa model wrapper for FoundUps simulation.

Coordinates agent stepping and integrates with FAM modules.

Token Economics (WSP 26 Section 6.8):
- UP$: Universal fuel (humans EARN, agents SPEND allocated budgets)
- F_i: FoundUp-specific tokens (agents EARN through PoUW, humans OWN)
"""

from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from .config import SimulatorConfig, DEFAULT_CONFIG
from .event_bus import EventBus
from .state_store import StateStore
from .adapters.fam_bridge import FAMBridge
from .adapters.phantom_plugs import PhantomTokenEconomy, PhantomSocialActions
from .agents.base_agent import BaseSimAgent
from .agents.founder_agent import FounderAgent
from .agents.user_agent import UserAgent
from .economics.token_economics import TokenEconomicsEngine, FeeConfig, adoption_curve
from .economics.fi_orderbook import OrderBookManager
from .economics.investor_staking import InvestorPool
from .economics.btc_reserve import BTCReserve, get_btc_reserve, reset_btc_reserve
from .economics.demurrage import DemurrageEngine, DecayConfig
from .economics.pool_distribution import (
    PoolDistributor, FoundUpTokenDistributor,
    ParticipantType, ActivityLevel,
)
from .economics.fi_rating import FiRatingEngine, get_rating_engine
from .ai.cabr_estimator import CABREstimator, CABRScore, FoundUpIdea, CABR_THRESHOLD

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class FoundUpsModel:
    """Mesa-like model for FoundUps simulation.

    This is a simplified Mesa model that coordinates agents
    without requiring the full Mesa dependency. If Mesa is
    needed later, this can be subclassed from mesa.Model.

    Key responsibilities:
    - Initialize FAM components (bridge, token economy)
    - Create and manage agents
    - Step through simulation ticks
    - Maintain SSoT via StateStore
    """

    def __init__(
        self,
        config: Optional[SimulatorConfig] = None,
        fam_daemon: Optional["Any"] = None,
    ) -> None:
        """Initialize the model.

        Args:
            config: Simulation configuration
            fam_daemon: Optional FAMDaemon instance for event SSoT
        """
        self._config = config or DEFAULT_CONFIG
        self._seed = self._config.seed
        random.seed(self._seed)

        # Current tick
        self._tick: int = 0
        self._start_time: float = 0.0
        self._running: bool = False

        # FAM bridge (thin wrapper around FAM modules) with shared daemon if provided.
        self._fam_bridge = FAMBridge(fam_daemon=fam_daemon)

        # Event system (SSoT) - connect to FAMBridge's daemon
        self._event_bus = EventBus()
        daemon = self._fam_bridge.get_daemon()
        if daemon:
            self._event_bus.connect_fam_daemon(daemon)

        # State store (derived from events)
        self._state_store = StateStore(
            event_bus=self._event_bus,
            grid_width=self._config.grid_width,
            grid_height=self._config.grid_height,
        )

        # Phantom plugs (simulated token/social systems)
        self._token_economy = PhantomTokenEconomy(
            initial_balance=self._config.initial_agent_tokens,
        )
        self._social_actions = PhantomSocialActions(
            like_cost=self._config.like_cost,
            follow_cost=self._config.follow_cost,
            token_economy=self._token_economy,
        )

        # WSP 26 Section 6.8: Human vs Agent token economics
        # UP$ (humans earn), F_i (agents earn for human owners)
        self._token_econ_engine = TokenEconomicsEngine(fee_config=FeeConfig())
        self._orderbook = OrderBookManager(trading_fee_rate=0.02)
        self._investor_pool = InvestorPool()

        # BTC Reserve + Demurrage + Pool Distribution (wired for BTC-F_i mirror)
        reset_btc_reserve()  # Fresh reserve per simulation run
        self._btc_reserve = get_btc_reserve()
        self._demurrage = DemurrageEngine(
            config=DecayConfig(), btc_reserve=self._btc_reserve,
        )
        self._pool_distributor = PoolDistributor()
        self._fi_distributors: Dict[str, FoundUpTokenDistributor] = {}

        # BTC-F_i ratio tracking (key metric from 012)
        self._btc_fi_ratio_history: List[Dict] = []
        self._epoch_counter: int = 0

        # F_i Rating Engine (color temperature gradient for animation)
        self._rating_engine = get_rating_engine()
        self._rating_update_interval = 10  # Every 10 ticks, emit rating updates
        self._demurrage_interval: int = 10  # Apply demurrage every N ticks

        # CABR Score Estimator (3V engine: Validation -> Verification -> Valuation)
        self._cabr_estimator = CABREstimator(use_ai=False)  # Heuristic for simulation
        self._cabr_scores: Dict[str, CABRScore] = {}  # Cache per foundup

        self._f0_seed_btc = 10.0
        self._f0_seeded = False
        self._f0_source_foundup_id = "F_0"
        self._f0_investor_ids: List[str] = [f"f0_investor_{idx:03d}" for idx in range(8)]
        self._mvp_offerings_resolved = 0
        self._total_dex_trades = 0
        self._total_dex_volume_ups = 0.0

        # Agents
        self._agents: Dict[str, BaseSimAgent] = {}
        self._agent_order: List[str] = []

        # Initialize agents
        self._create_agents()

        logger.info(
            f"[MODEL] Initialized with {len(self._agents)} agents, "
            f"seed={self._seed}"
        )

    def _create_agents(self) -> None:
        """Create initial agent population."""
        use_ai = self._config.use_ai

        # Create founder agents (Qwen-powered if AI enabled)
        for i in range(self._config.num_founder_agents):
            agent_id = f"founder_{i:03d}"
            agent = FounderAgent(
                agent_id=agent_id,
                fam_bridge=self._fam_bridge,
                token_economy=self._token_economy,
                social_actions=self._social_actions,
                state_store=self._state_store,
                creation_cost=self._config.foundup_creation_cost,
                action_probability=self._config.agent_action_probability,
                cooldown_ticks=self._config.agent_cooldown_ticks,
                use_ai=use_ai,
            )
            self._agents[agent_id] = agent
            self._agent_order.append(agent_id)

            # Register with state store and token economy
            self._state_store.register_agent(
                agent_id, "founder", self._config.initial_agent_tokens
            )
            self._token_economy.register_agent(agent_id)

        # Create user agents (Gemma-powered if AI enabled)
        for i in range(self._config.num_user_agents):
            agent_id = f"user_{i:03d}"
            # Vary risk tolerance across users
            risk_tolerance = self._config.ai_risk_tolerance + (i % 5 - 2) * 0.1
            risk_tolerance = max(0.1, min(0.9, risk_tolerance))

            agent = UserAgent(
                agent_id=agent_id,
                fam_bridge=self._fam_bridge,
                token_economy=self._token_economy,
                social_actions=self._social_actions,
                state_store=self._state_store,
                like_cost=self._config.like_cost,
                follow_cost=self._config.follow_cost,
                stake_min=self._config.stake_min,
                stake_max=self._config.stake_max,
                action_probability=self._config.agent_action_probability,
                cooldown_ticks=self._config.agent_cooldown_ticks,
                use_ai=use_ai,
                risk_tolerance=risk_tolerance,
            )
            self._agents[agent_id] = agent
            self._agent_order.append(agent_id)

            # Register with state store and token economy
            self._state_store.register_agent(
                agent_id, "user", self._config.initial_agent_tokens
            )
            self._token_economy.register_agent(agent_id)

        logger.info(
            f"[MODEL] Created {self._config.num_founder_agents} founders, "
            f"{self._config.num_user_agents} users"
        )

    def step(self) -> None:
        """Execute one simulation tick.

        Mesa convention: model.step() advances simulation by one tick.
        """
        self._tick += 1
        elapsed = time.time() - self._start_time if self._start_time else 0.0

        # Update event bus tick
        self._event_bus.set_tick(self._tick)

        # Step state store
        self._state_store.tick(self._tick, elapsed)

        # Shuffle agent order for fairness
        random.shuffle(self._agent_order)

        # Step each agent
        for agent_id in self._agent_order:
            agent = self._agents[agent_id]
            agent.step(self._tick)

        # Advance task lifecycle through the FAM pipeline.
        self._advance_task_pipeline()
        self._simulate_market_activity()
        self._simulate_f0_investor_program()

        # Apply demurrage (bio-decay) every N ticks
        if self._tick % self._demurrage_interval == 0:
            self._apply_demurrage_cycle()

        # Track BTC-F_i ratio every epoch (every 50 ticks)
        if self._tick % 50 == 0:
            self._record_btc_fi_ratio()

        # Emit F_i rating updates for animation (every N ticks)
        if self._tick % self._rating_update_interval == 0:
            self._emit_rating_updates()
            self._emit_cabr_updates()  # CABR score alongside F_i rating

        # Sync balances from token economy to state store.
        for agent_id in self._agent_order:
            agent = self._agents[agent_id]
            # Sync token balance to state store
            balance = self._token_economy.get_balance(agent_id)
            current = self._state_store.get_state().agents.get(agent_id)
            if current and current.tokens != balance:
                delta = balance - current.tokens
                self._state_store.update_agent_tokens(agent_id, delta)

        if self._config.verbose:
            logger.debug(f"[MODEL] Tick {self._tick} complete")

    def _advance_task_pipeline(self) -> None:
        """Progress task states through submit -> verify -> payout -> publish.

        Snapshot lists are used so a task only advances one stage per tick.
        """
        claimed_tasks = list(self._fam_bridge.get_claimed_tasks())
        submitted_tasks = list(self._fam_bridge.get_submitted_tasks())
        verified_tasks = list(self._fam_bridge.get_verified_tasks())
        paid_tasks = list(self._fam_bridge.get_paid_tasks_pending_publication())

        if claimed_tasks:
            task = random.choice(claimed_tasks)
            submitter_id = task.assignee_id or "user_000"
            ok, msg, _ = self._fam_bridge.submit_proof(task.task_id, submitter_id=submitter_id)
            if not ok and self._config.verbose:
                logger.debug("[MODEL] submit_proof failed for %s: %s", task.task_id, msg)

        if submitted_tasks:
            task = random.choice(submitted_tasks)
            ok, msg, _ = self._fam_bridge.verify_task(task.task_id, verifier_id="verifier_0")
            if not ok and self._config.verbose:
                logger.debug("[MODEL] verify_task failed for %s: %s", task.task_id, msg)

        if verified_tasks:
            task = random.choice(verified_tasks)
            ok, msg, _ = self._fam_bridge.trigger_payout(task.task_id, treasury_actor_id="treasury_0")
            if ok:
                # Emit agent earning event for ticker
                agent_id = task.assignee_id or "agent_000"
                self._fam_bridge.emit_agent_earning(
                    agent_id=agent_id,
                    foundup_id=task.foundup_id,
                    amount=task.reward_amount,
                    task_id=task.task_id,
                )
            elif self._config.verbose:
                logger.debug("[MODEL] trigger_payout failed for %s: %s", task.task_id, msg)

        if paid_tasks:
            task = random.choice(paid_tasks)
            ok, msg, _ = self._fam_bridge.publish_milestone(task.task_id, distributor_id="distribution_0")
            if not ok and self._config.verbose:
                logger.debug("[MODEL] publish_milestone failed for %s: %s", task.task_id, msg)

    def _simulate_market_activity(self) -> None:
        """Simulate decentralized F_i exchange activity for active FoundUps."""
        foundup_ids = self._state_store.get_foundup_ids()
        user_ids = [agent_id for agent_id in self._agent_order if agent_id.startswith("user_")]
        if not foundup_ids or len(user_ids) < 2:
            return

        # Trade activity is continuous but not every tick.
        if random.random() >= 0.35:
            return

        foundup_id = random.choice(foundup_ids)
        tile = self._state_store.get_state().foundups.get(foundup_id)
        if tile is None:
            return

        base_price = 1.0 + (tile.tasks_completed * 0.12) + (tile.likes * 0.01) + (tile.stakes * 0.02)
        spread = max(0.02, base_price * 0.03)
        sell_price = max(0.01, base_price - spread * random.uniform(0.2, 1.0))
        buy_price = base_price + spread * random.uniform(0.2, 1.2)
        quantity = round(random.uniform(3.0, 20.0), 2)

        seller_id = random.choice(user_ids)
        buyer_pool = [uid for uid in user_ids if uid != seller_id]
        if not buyer_pool:
            return
        buyer_id = random.choice(buyer_pool)

        self._orderbook.place_sell(
            foundup_id=foundup_id,
            human_id=seller_id,
            price=round(sell_price, 4),
            quantity=quantity,
        )
        _, trades = self._orderbook.place_buy(
            foundup_id=foundup_id,
            human_id=buyer_id,
            price=round(buy_price, 4),
            quantity=quantity,
        )
        if not trades:
            return

        daemon = self._fam_bridge.get_daemon()
        for trade in trades:
            self._total_dex_trades += 1
            self._total_dex_volume_ups += trade.ups_total
            daemon.emit(
                event_type="fi_trade_executed",
                payload={
                    "trade_id": trade.trade_id,
                    "buyer_id": trade.buyer_id,
                    "seller_id": trade.seller_id,
                    "price": round(trade.price, 4),
                    "quantity": round(trade.quantity, 2),
                    "ups_total": round(trade.ups_total, 4),
                    "fee_ups": round(trade.fee_ups, 4),
                },
                actor_id=trade.buyer_id,
                foundup_id=trade.foundup_id,
            )

    def _seed_f0_investor_pool_once(self) -> None:
        """Seed the ecosystem once from F_0 BTC principal."""
        if self._f0_seeded:
            return

        ii_tokens, tier = self._investor_pool.invest_btc(
            investor_id="f0_seed",
            btc_amount=self._f0_seed_btc,
        )
        self._f0_seeded = True
        if ii_tokens <= 0:
            return

        # Seed is anchored to F_0, not individual FoundUps.
        self._fam_bridge.get_daemon().emit(
            event_type="investor_funding_received",
            payload={
                "investor_id": "f0_seed",
                "source_foundup_id": self._f0_source_foundup_id,
                "btc_amount": self._f0_seed_btc,
                "ii_tokens": round(ii_tokens, 6),
                "tier": tier.value,
                "seeded": True,
            },
            actor_id="f0_seed",
            foundup_id=self._f0_source_foundup_id,
        )

    def _simulate_f0_investor_program(self) -> None:
        """F_0-only investor flow: subscriptions hoard UP$, then bid on Proto FoundUps."""
        self._seed_f0_investor_pool_once()
        foundup_ids = self._state_store.get_foundup_ids()
        if not foundup_ids:
            return

        state = self._state_store.get_state()
        proto_targets = [
            foundup_id
            for foundup_id in foundup_ids
            if state.foundups.get(foundup_id) and state.foundups[foundup_id].lifecycle_stage == "Proto"
        ]
        if not proto_targets:
            return

        # Subscription accrual (UP$ hoarding) happens from the F_0 investor program.
        for investor_id in self._f0_investor_ids:
            if random.random() < 0.08:
                self._fam_bridge.accrue_investor_terms(
                    investor_id=investor_id,
                    terms=1,
                    term_ups=200,
                    max_terms=5,
                )

        if random.random() >= 0.25:
            return

        target_foundup = random.choice(proto_targets)
        bidder_id = random.choice(self._f0_investor_ids)
        bidder_state = self._fam_bridge.get_investor_subscription_state(bidder_id)
        available_ups = int(bidder_state.get("available_ups", 0))
        if available_ups <= 0:
            return

        bid_ups = max(50, min(available_ups, random.randint(50, 250)))
        ok, _, _ = self._fam_bridge.place_mvp_bid(
            foundup_id=target_foundup,
            investor_id=bidder_id,
            bid_ups=bid_ups,
        )
        if not ok:
            return

        bids = self._fam_bridge.get_mvp_bids(target_foundup)
        if len(bids) < 3:
            return

        ok, _, allocations = self._fam_bridge.resolve_mvp_offering(
            foundup_id=target_foundup,
            actor_id="treasury_0",
            token_amount=1_000,
            top_n=1,
        )
        if ok and allocations:
            self._mvp_offerings_resolved += 1

        self._investor_pool.update_network_adoption(
            foundups_count=state.total_foundups,
            total_revenue=float(state.total_stakes),
        )
        self._investor_pool.vest_tokens()

    def _apply_demurrage_cycle(self) -> None:
        """Apply bio-decay to all registered wallets.

        Decayed UP$ routes to BTC Reserve (Hotel California).
        Active participants get decay relief via pool rewards.
        """
        # Register any new agents as wallets if not already tracked
        for agent_id in self._agent_order:
            if agent_id not in self._demurrage.wallets:
                balance = self._token_economy.get_balance(agent_id)
                if balance > 0:
                    self._demurrage.register_wallet(agent_id, float(balance))

        # Apply decay (1 day per interval for simulation speed)
        decay_results = self._demurrage.apply_decay_all(time_elapsed_days=1.0)

        if decay_results:
            total_decay = sum(decay_results.values())
            logger.debug(
                f"[MODEL] Demurrage tick {self._tick}: "
                f"{total_decay:.2f} UP$ decayed from {len(decay_results)} wallets"
            )

        # Distribute epoch rewards via pool structure
        self._epoch_counter += 1
        state = self._state_store.get_state()
        epoch_rewards = float(state.total_stakes) * 0.01  # 1% of total stakes per epoch
        if epoch_rewards > 0 and self._pool_distributor.participants:
            self._pool_distributor.distribute_epoch(
                epoch=self._epoch_counter,
                total_ups_rewards=epoch_rewards,
            )

    def _record_btc_fi_ratio(self) -> None:
        """Record BTC-per-F_i ratio for tracking the mirror dynamic.

        Key metric: btc_per_fi = btc_reserve / fi_released
        Should increase over time (early cheap, late expensive).
        """
        btc_total = self._btc_reserve.total_btc
        econ_stats = self._token_econ_engine.get_system_stats()
        fi_outstanding = econ_stats.get("total_fi_outstanding", 0.0)

        # Calculate adoption score from simulation state
        state = self._state_store.get_state()
        # Simple adoption proxy: foundups created / target capacity
        adoption_score = min(1.0, state.total_foundups / max(1, 100))
        s_curve_release = adoption_curve(adoption_score)

        btc_per_fi = btc_total / max(1.0, fi_outstanding) if fi_outstanding > 0 else 0.0

        snapshot = {
            "tick": self._tick,
            "epoch": self._epoch_counter,
            "btc_reserve": round(btc_total, 8),
            "fi_outstanding": round(fi_outstanding, 2),
            "btc_per_fi": round(btc_per_fi, 8),
            "adoption_score": round(adoption_score, 4),
            "s_curve_release": round(s_curve_release, 4),
            "ups_minted": round(self._btc_reserve.total_ups_minted, 2),
            "ups_value_btc": round(self._btc_reserve.ups_value_btc, 8),
            "total_decayed": round(self._demurrage.total_decayed, 2),
        }
        self._btc_fi_ratio_history.append(snapshot)

        if self._config.verbose:
            logger.info(
                f"[MODEL] BTC/F_i ratio @ tick {self._tick}: "
                f"{btc_per_fi:.8f} BTC/F_i "
                f"(reserve={btc_total:.4f}, fi={fi_outstanding:.0f}, "
                f"adoption={adoption_score:.2%})"
            )

    def _emit_rating_updates(self) -> None:
        """Emit F_i rating updates for animation (color temperature gradient).

        Calculates rating dimensions from simulation state:
        - velocity: Task completion rate
        - traction: Customer/engagement counts
        - health: Lifecycle stage progress
        - potential: Founder track record (simulated)

        Emits 'fi_rating_updated' events for SSE streaming.
        """
        state = self._state_store.get_state()
        daemon = self._fam_bridge.get_daemon()
        if not daemon:
            return

        for foundup_id, tile in state.foundups.items():
            # Calculate velocity from task completion rate
            task_ratio = tile.tasks_completed / max(1, tile.task_count)
            velocity = min(1.0, task_ratio * 2)  # Scale to 0-1

            # Calculate traction from engagement
            engagement = tile.like_count + tile.customer_count * 10
            traction = min(1.0, engagement / 100)

            # Calculate health from lifecycle stage
            stage_health = {
                "Idea": 0.1,
                "PoC": 0.3,
                "Soft-Proto": 0.4,
                "Proto": 0.6,
                "MVP": 0.9,
                "Launch": 1.0,
            }
            health = stage_health.get(tile.lifecycle_stage, 0.2)

            # Potential: simulate founder track record (random for now)
            # In production, this comes from FounderTrackRecord
            potential = 0.5 + (hash(foundup_id) % 30) / 100  # 0.5-0.8 range

            # Update rating engine
            rating = self._rating_engine.get_or_create_rating(foundup_id)
            rating.velocity = velocity
            rating.traction = traction
            rating.health = health
            rating.potential = potential

            # Emit event for SSE
            rating_data = self._rating_engine.get_animation_data(foundup_id)
            daemon.emit(
                event_type="fi_rating_updated",
                payload=rating_data,
                actor_id="rating_engine",
                foundup_id=foundup_id,
            )

    def _emit_cabr_updates(self) -> None:
        """Emit CABR score updates for animation.

        Calculates CABR (Conscious Autonomous Benefit Rate) from simulation state:
        - env_score: Environmental impact (heuristic from category)
        - soc_score: Social impact (heuristic from category)
        - part_score: Participation metrics (task completion, verifications)

        Emits 'cabr_score_updated' events for SSE streaming.
        """
        state = self._state_store.get_state()
        daemon = self._fam_bridge.get_daemon()
        if not daemon:
            return

        for foundup_id, tile in state.foundups.items():
            # Initialize CABR score for new FoundUps
            if foundup_id not in self._cabr_scores:
                # Create FoundUpIdea from tile data for initial estimate
                idea = FoundUpIdea(
                    name=tile.name,
                    token_symbol=tile.token_symbol,
                    pain_point="simulation_default",  # Would come from FoundUp metadata
                    outcome="simulation_default",
                    category=self._get_foundup_category(tile.name),
                    team_size=3,
                    total_supply=tile.token_supply or 1_000_000,
                    initial_allocation={"treasury": 0.5, "team": 0.2, "community": 0.3},
                )
                self._cabr_scores[foundup_id] = self._cabr_estimator.estimate_idea_cabr(idea)

            # Update with live participation metrics
            cabr = self._cabr_scores[foundup_id]
            active_agents = len([
                a for a in state.agents
                if a.current_foundup_id == foundup_id
            ])
            cabr = self._cabr_estimator.update_participation(
                score=cabr,
                tasks_completed=tile.tasks_completed,
                tasks_total=tile.task_count,
                active_agents=active_agents,
                verifications=tile.tasks_completed,  # Proxy: completed = verified
            )
            self._cabr_scores[foundup_id] = cabr

            # Emit event for SSE
            daemon.emit(
                event_type="cabr_score_updated",
                payload={
                    "env_score": cabr.env_score,
                    "soc_score": cabr.soc_score,
                    "part_score": cabr.part_score,
                    "total": cabr.total,
                    "threshold": CABR_THRESHOLD,
                    "threshold_met": cabr.total >= CABR_THRESHOLD,
                    "confidence": cabr.confidence,
                },
                actor_id="cabr_engine",
                foundup_id=foundup_id,
            )

    def _get_foundup_category(self, name: str) -> str:
        """Infer category from FoundUp name for CABR heuristics."""
        name_lower = name.lower()
        if "junk" in name_lower or "waste" in name_lower:
            return "waste"
        elif "cloud" in name_lower or "kitchen" in name_lower or "food" in name_lower:
            return "food"
        elif "space" in name_lower or "rocket" in name_lower:
            return "infrastructure"
        elif "health" in name_lower or "med" in name_lower:
            return "healthcare"
        elif "solar" in name_lower or "energy" in name_lower:
            return "energy"
        elif "edu" in name_lower or "learn" in name_lower:
            return "education"
        elif "social" in name_lower or "twitter" in name_lower:
            return "social"
        elif "defi" in name_lower or "finance" in name_lower:
            return "defi"
        else:
            return "infrastructure"  # Default

    def start(self) -> None:
        """Start the simulation."""
        self._running = True
        self._start_time = time.time()
        logger.info("[MODEL] Simulation started")

    def stop(self) -> None:
        """Stop the simulation."""
        self._running = False
        logger.info(f"[MODEL] Simulation stopped at tick {self._tick}")

    @property
    def tick(self) -> int:
        """Current simulation tick."""
        return self._tick

    @property
    def running(self) -> bool:
        """Whether simulation is running."""
        return self._running

    @property
    def state_store(self) -> StateStore:
        """Get state store for rendering."""
        return self._state_store

    @property
    def event_bus(self) -> EventBus:
        """Get event bus."""
        return self._event_bus

    @property
    def config(self) -> SimulatorConfig:
        """Get simulation config."""
        return self._config

    @property
    def token_economics(self) -> TokenEconomicsEngine:
        """Get WSP 26 token economics engine."""
        return self._token_econ_engine

    @property
    def btc_reserve(self) -> BTCReserve:
        """Get BTC Reserve (Hotel California)."""
        return self._btc_reserve

    @property
    def demurrage(self) -> DemurrageEngine:
        """Get demurrage engine (bio-decay for LIQUID UP$)."""
        return self._demurrage

    @property
    def pool_distributor(self) -> PoolDistributor:
        """Get pool distributor (Un/Dao/Du)."""
        return self._pool_distributor

    @property
    def btc_fi_ratio_history(self) -> List[Dict]:
        """Get BTC-per-F_i ratio history for analysis."""
        return self._btc_fi_ratio_history

    def get_agent(self, agent_id: str) -> Optional[BaseSimAgent]:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def get_agents_by_type(self, agent_type: str) -> List[BaseSimAgent]:
        """Get all agents of a given type."""
        return [a for a in self._agents.values() if a.agent_type == agent_type]

    def get_stats(self) -> Dict:
        """Get simulation statistics."""
        state = self._state_store.get_state()
        econ_stats = self._token_econ_engine.get_system_stats()

        return {
            "tick": self._tick,
            "elapsed_seconds": state.elapsed_seconds,
            "total_foundups": state.total_foundups,
            "total_likes": state.total_likes,
            "total_stakes": state.total_stakes,
            "total_tokens": state.total_tokens_circulating,
            "total_dex_trades": state.total_dex_trades,
            "total_dex_volume_ups": state.total_dex_volume_ups,
            "agent_count": len(self._agents),
            "founders": len([a for a in self._agents.values() if a.agent_type == "founder"]),
            "users": len([a for a in self._agents.values() if a.agent_type == "user"]),
            # WSP 26 token economics stats
            "ups_circulation": econ_stats["total_ups_circulation"],
            "fi_outstanding": econ_stats["total_fi_outstanding"],
            "btc_vault_total": econ_stats["total_btc_vault"],
            "fees_collected": econ_stats["total_fees_ops"] + econ_stats["total_fees_insurance"],
            "investor_pool_rate": self._investor_pool.founder_share_per_foundup,
            "investor_hurdle_met": self._investor_pool.return_hurdle_met,
            "f0_seed_btc": self._f0_seed_btc,
            "f0_investor_count": len(self._f0_investor_ids),
            "mvp_offerings_resolved": self._mvp_offerings_resolved,
            # BTC Reserve + Demurrage (wired economics)
            "btc_reserve_total": self._btc_reserve.total_btc,
            "btc_reserve_usd": self._btc_reserve.reserve_usd_value,
            "ups_value_btc": self._btc_reserve.ups_value_btc,
            "total_demurrage_decayed": self._demurrage.total_decayed,
            "total_btc_from_decay": self._demurrage.total_btc_from_decay,
            "pool_participants": len(self._pool_distributor.participants),
            "epochs_completed": self._epoch_counter,
            # BTC-F_i mirror ratio (key metric)
            "btc_per_fi_latest": (
                self._btc_fi_ratio_history[-1]["btc_per_fi"]
                if self._btc_fi_ratio_history else 0.0
            ),
            "btc_fi_ratio_snapshots": len(self._btc_fi_ratio_history),
        }
