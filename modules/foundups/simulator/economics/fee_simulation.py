"""Fee Configuration Simulation - Find Optimal Economic Parameters.

This is the PURPOSE of the simulator: test different fee structures
and observe their economic effects before committing to production.

Scenarios to test:
1. Different MINED F_i exit fees (5%, 8%, 11%, 15%)
2. Different STAKED F_i round-trip fees (5%, 8%, 10%)
3. Subscription tier impact on staking behavior
4. Demurrage avoidance (how much goes to staking?)
5. Value preservation (do users lose money?)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import logging

from .token_economics import (
    FeeConfig,
    TokenEconomicsEngine,
    HumanUPSAccount,
    FoundUpTokenPool,
    SubscriptionTier,
    SUBSCRIPTION_TIERS,
)
from .pool_distribution import (
    PoolDistributor,
    ParticipantType,
    ActivityLevel,
)

logger = logging.getLogger(__name__)


@dataclass
class FeeScenario:
    """A fee configuration scenario to test."""

    name: str
    mined_exit_fee: float  # MINED F_i -> UP$ extraction fee
    staked_entry_fee: float  # UP$ -> STAKED F_i entry fee
    staked_exit_fee: float  # STAKED F_i -> UP$ exit fee

    @property
    def staked_roundtrip(self) -> float:
        """Total round-trip cost for staking."""
        return self.staked_entry_fee + self.staked_exit_fee


@dataclass
class SimulationResult:
    """Results from running a fee scenario simulation."""

    scenario: FeeScenario
    epochs_run: int

    # Value preservation metrics
    total_ups_staked: float = 0.0
    total_ups_unstaked: float = 0.0
    value_preserved_pct: float = 0.0  # How much value users kept

    # Extraction metrics
    total_mined_fi: float = 0.0
    total_mined_extracted: float = 0.0
    mined_extraction_rate: float = 0.0  # % of mined F_i that got extracted

    # System revenue
    total_fees_collected: float = 0.0
    btc_vault_total: float = 0.0

    # Behavior metrics
    avg_stake_duration_epochs: float = 0.0
    churn_rate: float = 0.0  # Unstakes per epoch


def create_fee_config(scenario: FeeScenario) -> FeeConfig:
    """Create FeeConfig from scenario parameters."""
    config = FeeConfig()

    # Set MINED F_i exit fee (distribute across categories)
    total_mined = scenario.mined_exit_fee
    config.mined_fee_ops = total_mined * 0.27  # ~3% of 11%
    config.mined_fee_vault = total_mined * 0.45  # ~5% of 11%
    config.mined_fee_insurance = total_mined * 0.18  # ~2% of 11%
    config.mined_fee_network = total_mined * 0.10  # ~1% of 11%
    config.mined_fi_exit_fee = total_mined

    # Set STAKED F_i fees
    config.staked_fi_entry_fee = scenario.staked_entry_fee
    config.staked_fi_exit_fee = scenario.staked_exit_fee

    return config


def run_scenario(
    scenario: FeeScenario,
    num_humans: int = 10,
    num_foundups: int = 3,
    num_epochs: int = 12,  # One "year" of monthly epochs
    ups_per_epoch: float = 1000.0,
) -> SimulationResult:
    """Run a simulation scenario and return results.

    Simulates:
    1. Humans earning UP$ through subscriptions
    2. Agents mining F_i for humans
    3. Humans staking UP$ for value preservation
    4. Some humans extracting MINED F_i
    5. Some humans unstaking after N epochs
    """
    # Create engine with scenario fees
    fee_config = create_fee_config(scenario)
    engine = TokenEconomicsEngine(fee_config=fee_config)

    # Create pool distributor for UP$ distribution
    pool_distributor = PoolDistributor()

    result = SimulationResult(scenario=scenario, epochs_run=num_epochs)

    # Register FoundUps
    foundups = []
    for i in range(num_foundups):
        fid = f"foundup_{i}"
        pool = engine.register_foundup(fid)
        pool.progress_tier()  # Move to Seeded tier
        pool.progress_tier()  # Move to Active tier
        foundups.append(fid)

    # Register humans with different subscription tiers
    humans = []
    tiers = list(SubscriptionTier)
    for i in range(num_humans):
        hid = f"human_{i}"
        account = engine.register_human(hid, initial_ups=100.0)
        # Distribute tiers
        tier = tiers[i % len(tiers)]
        account.upgrade_subscription(tier)

        # Register in pool distributor
        p_type = ParticipantType.UN if i < 6 else (ParticipantType.DAO if i < 9 else ParticipantType.DU)
        activity = ActivityLevel.UN if i % 3 == 0 else (ActivityLevel.DAO if i % 3 == 1 else ActivityLevel.DU)
        pool_distributor.register_participant(hid, p_type, activity)

        # Register agent for this human
        aid = f"agent_{i}"
        engine.register_agent(aid, hid)
        engine.human_allocates_to_agent(hid, aid, 50.0)

        humans.append(hid)

    # Track staking for duration calculation
    stake_epochs: Dict[str, List[int]] = {h: [] for h in humans}

    # Run epochs
    for epoch in range(num_epochs):
        # 1. Distribute UP$ rewards
        epoch_dist = pool_distributor.distribute_epoch(epoch, ups_per_epoch)

        # 2. Agents mine F_i for their humans
        for i, hid in enumerate(humans):
            aid = f"agent_{i}"
            fid = foundups[i % num_foundups]

            # Agent does work, earns F_i
            work_reward = 100.0 + (i * 10)  # Vary by human
            success, fi_earned = engine.agent_completes_task(aid, fid, 10.0, work_reward)
            if success and fi_earned > 0:
                result.total_mined_fi += fi_earned

        # 3. Some humans stake UP$ (value preservation behavior)
        for i, hid in enumerate(humans):
            account = engine.human_accounts[hid]
            fid = foundups[i % num_foundups]

            # Credit epoch rewards to account
            reward = epoch_dist.participant_rewards.get(hid, 0.0)
            if reward > 0:
                account.earn_ups(reward, "epoch_distribution")

            # Stake 60% of balance (demurrage avoidance)
            stake_amount = account.ups_balance * 0.6
            if stake_amount > 10.0:
                fi_received, fee = engine.human_stakes_ups(hid, fid, stake_amount)
                if fi_received > 0:
                    result.total_ups_staked += stake_amount
                    stake_epochs[hid].append(epoch)

        # 4. Some humans extract MINED F_i (every 4 epochs)
        if epoch % 4 == 3:
            for i, hid in enumerate(humans):
                account = engine.human_accounts[hid]
                # Extract from first FoundUp with tokens
                for fid, balance in list(account.foundup_tokens.items()):
                    if balance > 50.0:
                        extract_amt = balance * 0.5  # Extract 50%
                        ups_received, fees = engine.human_converts_mined_fi_to_ups(hid, fid, extract_amt)
                        if ups_received > 0:
                            result.total_mined_extracted += extract_amt
                            result.total_fees_collected += fees.get("total", 0.0)
                        break

        # 5. Some humans unstake (after 6 epochs)
        if epoch >= 6:
            for i, hid in enumerate(humans):
                if i % 3 == 0:  # Every 3rd human unstakes
                    account = engine.human_accounts[hid]
                    for fid, staked in list(account.staked_positions.items()):
                        if staked > 50.0:
                            unstake_amt = staked * 0.3  # Unstake 30%
                            ups_received, fee = engine.human_unstakes_fi(hid, fid, unstake_amt)
                            if ups_received > 0:
                                result.total_ups_unstaked += ups_received
                                result.total_fees_collected += fee

    # Calculate metrics
    if result.total_ups_staked > 0:
        result.value_preserved_pct = (result.total_ups_unstaked / result.total_ups_staked) * 100

    if result.total_mined_fi > 0:
        result.mined_extraction_rate = (result.total_mined_extracted / result.total_mined_fi) * 100

    # Calculate BTC vault total
    for pool in engine.foundup_pools.values():
        result.btc_vault_total += pool.btc_vault_balance

    # Calculate avg stake duration
    total_duration = 0
    stake_count = 0
    for hid, epochs in stake_epochs.items():
        if epochs:
            total_duration += (num_epochs - min(epochs))
            stake_count += 1
    if stake_count > 0:
        result.avg_stake_duration_epochs = total_duration / stake_count

    return result


def compare_scenarios() -> List[SimulationResult]:
    """Run multiple scenarios and compare results."""
    scenarios = [
        FeeScenario("Low Extraction (5%)", 0.05, 0.02, 0.03),
        FeeScenario("Medium Extraction (8%)", 0.08, 0.03, 0.04),
        FeeScenario("High Extraction (11%)", 0.11, 0.03, 0.05),
        FeeScenario("Very High (15%)", 0.15, 0.04, 0.06),
        FeeScenario("Balanced (11%/8%)", 0.11, 0.03, 0.05),  # Current proposal
    ]

    results = []
    for scenario in scenarios:
        result = run_scenario(scenario)
        results.append(result)

    return results


def print_comparison(results: List[SimulationResult]) -> None:
    """Print comparison table of scenario results."""
    print("\n" + "=" * 100)
    print("FEE SCENARIO COMPARISON - SIMULATION RESULTS")
    print("=" * 100)
    print(
        f"{'Scenario':<25} {'Mined Exit':<12} {'Staked RT':<12} "
        f"{'Value Kept%':<12} {'Extraction%':<12} {'BTC Vault':<12}"
    )
    print("-" * 100)

    for r in results:
        s = r.scenario
        print(
            f"{s.name:<25} {s.mined_exit_fee*100:.1f}%{'':<7} "
            f"{s.staked_roundtrip*100:.1f}%{'':<7} "
            f"{r.value_preserved_pct:.1f}%{'':<7} "
            f"{r.mined_extraction_rate:.1f}%{'':<7} "
            f"{r.btc_vault_total:.2f}"
        )

    print("=" * 100)
    print("\nKEY INSIGHTS:")
    print("- Higher mined extraction fee -> Lower extraction rate -> More value stays in ecosystem")
    print("- Lower staked round-trip fee -> Better value preservation for investors")
    print("- BTC vault grows faster with higher extraction fees (Hotel California effect)")
    print("\nRECOMMENDATION: Run simulation with your specific parameters to find optimal balance.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = compare_scenarios()
    print_comparison(results)
