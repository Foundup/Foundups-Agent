"""Exit Scenario Simulator - Compare F_i exit models.

Tests five models to find optimal fee structure:
- Current: MINED 11%, STAKED 5%, BOUGHT ???
- Model A: Creation-time fee, fungible exit
- Model B: DEX includes exit fee
- Model C: Vesting-only (no type distinction)
- Hybrid: Creation fee + Vesting discount

Run: python -m modules.foundups.simulator.economics.exit_scenario_sim
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple
import random
import math


class FiType(Enum):
    MINED = "mined"
    STAKED = "staked"
    BOUGHT = "bought"


class ExitModel(Enum):
    CURRENT = "current"
    CREATION_FEE = "creation_fee"
    DEX_INCLUDES_EXIT = "dex_includes_exit"
    VESTING_ONLY = "vesting_only"
    HYBRID = "hybrid"


@dataclass
class ModelConfig:
    """Fee configuration for each model."""

    # Creation fees (applied when F_i is acquired)
    mined_creation: float = 0.0
    staked_creation: float = 0.03
    bought_creation: float = 0.0

    # Exit fees (applied when converting F_i to UPS)
    mined_exit: float = 0.11
    staked_exit: float = 0.05
    bought_exit: float = 0.08

    # Vesting discounts (multiplier on exit fee)
    vesting_schedule: Dict[str, float] = field(default_factory=lambda: {
        "0-1yr": 1.0,
        "1-2yr": 0.9,
        "2-4yr": 0.75,
        "4-8yr": 0.6,
        "8+yr": 0.5,
    })

    # Use vesting instead of type-based exit
    vesting_only: bool = False
    vesting_base_fee: float = 0.15  # Base fee when vesting_only=True

    # DEX and final exit
    dex_fee: float = 0.02
    dex_includes_type_fee: bool = False  # Model B
    cashout_fee: float = 0.07


# Pre-configured models
MODELS = {
    ExitModel.CURRENT: ModelConfig(
        mined_creation=0.0,
        staked_creation=0.03,
        mined_exit=0.11,
        staked_exit=0.05,
        bought_exit=0.08,  # Assumed middle ground
    ),
    ExitModel.CREATION_FEE: ModelConfig(
        mined_creation=0.11,
        staked_creation=0.03,
        bought_creation=0.0,
        mined_exit=0.05,  # Universal after creation
        staked_exit=0.05,
        bought_exit=0.05,
    ),
    ExitModel.DEX_INCLUDES_EXIT: ModelConfig(
        mined_creation=0.0,
        staked_creation=0.03,
        mined_exit=0.11,
        staked_exit=0.05,
        bought_exit=0.08,
        dex_includes_type_fee=True,
    ),
    ExitModel.VESTING_ONLY: ModelConfig(
        mined_creation=0.0,
        staked_creation=0.03,
        vesting_only=True,
        vesting_base_fee=0.15,
    ),
    ExitModel.HYBRID: ModelConfig(
        mined_creation=0.11,
        staked_creation=0.03,
        bought_creation=0.0,
        vesting_only=True,
        vesting_base_fee=0.10,  # Lower base since creation fee already paid
    ),
}


@dataclass
class Agent:
    """Simulated agent with F_i holdings."""

    id: str
    fi_type: FiType
    fi_amount: float
    acquired_epoch: int
    hold_years: float = 0.0

    def vesting_tier(self) -> str:
        """Get vesting tier based on hold duration."""
        if self.hold_years >= 8:
            return "8+yr"
        elif self.hold_years >= 4:
            return "4-8yr"
        elif self.hold_years >= 2:
            return "2-4yr"
        elif self.hold_years >= 1:
            return "1-2yr"
        else:
            return "0-1yr"


@dataclass
class ExitResult:
    """Result of an exit simulation."""

    agent_id: str
    fi_type: FiType
    fi_amount: float
    hold_years: float
    exit_path: str  # "direct" or "dex"

    # Fees paid
    creation_fee: float
    exit_fee: float
    dex_fee: float
    cashout_fee: float
    total_fee: float

    # Final amounts
    fi_after_creation: float
    ups_received: float
    btc_received: float

    # Efficiency
    efficiency: float  # btc_received / fi_amount (before creation fee)


def simulate_exit(
    agent: Agent,
    model: ExitModel,
    use_dex: bool = False,
) -> ExitResult:
    """Simulate an agent exiting with given model."""

    config = MODELS[model]

    # 1. Creation fee (already paid at acquisition, but affects fi_amount)
    if agent.fi_type == FiType.MINED:
        creation_fee = config.mined_creation
    elif agent.fi_type == FiType.STAKED:
        creation_fee = config.staked_creation
    else:
        creation_fee = config.bought_creation

    fi_after_creation = agent.fi_amount * (1 - creation_fee)

    # 2. Exit fee (type-based or vesting-based)
    if config.vesting_only:
        vesting_tier = agent.vesting_tier()
        vesting_mult = config.vesting_schedule.get(vesting_tier, 1.0)
        exit_fee_rate = config.vesting_base_fee * vesting_mult
    else:
        if agent.fi_type == FiType.MINED:
            base_exit = config.mined_exit
        elif agent.fi_type == FiType.STAKED:
            base_exit = config.staked_exit
        else:
            base_exit = config.bought_exit

        # Apply vesting discount
        vesting_tier = agent.vesting_tier()
        vesting_mult = config.vesting_schedule.get(vesting_tier, 1.0)
        exit_fee_rate = base_exit * vesting_mult

    # 3. DEX path
    dex_fee_rate = 0.0
    if use_dex:
        dex_fee_rate = config.dex_fee
        if config.dex_includes_type_fee:
            # Model B: DEX sell includes exit fee
            exit_fee_rate = exit_fee_rate  # Already calculated
        else:
            # Other models: DEX is just 2%, exit fee is separate
            pass

    # 4. Calculate amounts
    # Path: F_i → (creation already done) → exit → DEX? → UPS → BTC

    # After exit fee
    ups_before_dex = fi_after_creation * (1 - exit_fee_rate)

    # After DEX fee (if used)
    if use_dex:
        ups_after_dex = ups_before_dex * (1 - dex_fee_rate)
    else:
        ups_after_dex = ups_before_dex

    # After cashout
    btc_received = ups_after_dex * (1 - config.cashout_fee)

    # Calculate actual fees paid
    creation_fee_paid = agent.fi_amount * creation_fee
    exit_fee_paid = fi_after_creation * exit_fee_rate
    dex_fee_paid = ups_before_dex * dex_fee_rate if use_dex else 0
    cashout_fee_paid = ups_after_dex * config.cashout_fee
    total_fee_paid = creation_fee_paid + exit_fee_paid + dex_fee_paid + cashout_fee_paid

    efficiency = btc_received / agent.fi_amount if agent.fi_amount > 0 else 0

    return ExitResult(
        agent_id=agent.id,
        fi_type=agent.fi_type,
        fi_amount=agent.fi_amount,
        hold_years=agent.hold_years,
        exit_path="dex" if use_dex else "direct",
        creation_fee=creation_fee_paid,
        exit_fee=exit_fee_paid,
        dex_fee=dex_fee_paid,
        cashout_fee=cashout_fee_paid,
        total_fee=total_fee_paid,
        fi_after_creation=fi_after_creation,
        ups_received=ups_after_dex,
        btc_received=btc_received,
        efficiency=efficiency,
    )


def run_scenario(
    scenario_name: str,
    agents: List[Agent],
    model: ExitModel,
    use_dex_pct: float = 0.5,
) -> Dict:
    """Run a scenario and return aggregate results."""

    results = []
    for agent in agents:
        use_dex = random.random() < use_dex_pct
        result = simulate_exit(agent, model, use_dex)
        results.append(result)

    total_fi = sum(r.fi_amount for r in results)
    total_btc = sum(r.btc_received for r in results)
    total_fees = sum(r.total_fee for r in results)

    # Fee breakdown
    total_creation = sum(r.creation_fee for r in results)
    total_exit = sum(r.exit_fee for r in results)
    total_dex = sum(r.dex_fee for r in results)
    total_cashout = sum(r.cashout_fee for r in results)

    avg_efficiency = total_btc / total_fi if total_fi > 0 else 0

    return {
        "scenario": scenario_name,
        "model": model.value,
        "agents": len(agents),
        "total_fi_in": total_fi,
        "total_btc_out": total_btc,
        "total_fees": total_fees,
        "fee_breakdown": {
            "creation": total_creation,
            "exit": total_exit,
            "dex": total_dex,
            "cashout": total_cashout,
        },
        "avg_efficiency": avg_efficiency,
        "protocol_capture": total_fees / total_fi if total_fi > 0 else 0,
    }


def create_test_agents(
    n_miners: int = 100,
    n_stakers: int = 50,
    n_traders: int = 30,
    fi_per_agent: float = 1000,
    hold_years_range: Tuple[float, float] = (0.1, 10),
) -> List[Agent]:
    """Create a diverse set of test agents."""

    agents = []

    # Miners - earned F_i through work
    for i in range(n_miners):
        hold = random.uniform(*hold_years_range)
        agents.append(Agent(
            id=f"miner_{i}",
            fi_type=FiType.MINED,
            fi_amount=fi_per_agent * random.uniform(0.5, 2.0),
            acquired_epoch=0,
            hold_years=hold,
        ))

    # Stakers - invested UPS
    for i in range(n_stakers):
        hold = random.uniform(*hold_years_range)
        agents.append(Agent(
            id=f"staker_{i}",
            fi_type=FiType.STAKED,
            fi_amount=fi_per_agent * random.uniform(0.8, 1.5),
            acquired_epoch=0,
            hold_years=hold,
        ))

    # Traders - bought on DEX
    for i in range(n_traders):
        # Traders typically hold shorter
        hold = random.uniform(0.1, 2.0)
        agents.append(Agent(
            id=f"trader_{i}",
            fi_type=FiType.BOUGHT,
            fi_amount=fi_per_agent * random.uniform(0.3, 1.0),
            acquired_epoch=0,
            hold_years=hold,
        ))

    return agents


def run_all_models(agents: List[Agent], scenario_name: str) -> List[Dict]:
    """Run all models on same agent set for comparison."""

    results = []
    for model in ExitModel:
        result = run_scenario(scenario_name, agents, model)
        results.append(result)

    return results


def print_comparison(results: List[Dict]):
    """Print formatted comparison table."""

    print("\n" + "=" * 80)
    print(f"SCENARIO: {results[0]['scenario']}")
    print(f"Agents: {results[0]['agents']}")
    print(f"Total F_i: {results[0]['total_fi_in']:,.0f}")
    print("=" * 80)

    print(f"\n{'Model':<20} {'BTC Out':>12} {'Total Fees':>12} {'Efficiency':>10} {'Capture':>10}")
    print("-" * 64)

    for r in results:
        print(
            f"{r['model']:<20} "
            f"{r['total_btc_out']:>12,.0f} "
            f"{r['total_fees']:>12,.0f} "
            f"{r['avg_efficiency']:>9.1%} "
            f"{r['protocol_capture']:>9.1%}"
        )

    print("\nFee Breakdown:")
    print(f"{'Model':<20} {'Creation':>10} {'Exit':>10} {'DEX':>10} {'Cashout':>10}")
    print("-" * 60)

    for r in results:
        fb = r['fee_breakdown']
        print(
            f"{r['model']:<20} "
            f"{fb['creation']:>10,.0f} "
            f"{fb['exit']:>10,.0f} "
            f"{fb['dex']:>10,.0f} "
            f"{fb['cashout']:>10,.0f}"
        )


def main():
    """Run exit scenario simulations."""

    print("\n" + "#" * 80)
    print("# F_i EXIT SCENARIO SIMULATION")
    print("# Comparing 5 fee models across different agent behaviors")
    print("#" * 80)

    random.seed(42)  # Reproducible results

    # Scenario 1: Normal distribution of agents
    print("\n\n>>> SCENARIO 1: Normal Distribution (100 miners, 50 stakers, 30 traders)")
    agents = create_test_agents()
    results = run_all_models(agents, "normal_distribution")
    print_comparison(results)

    # Scenario 2: Mass miner exit (short hold)
    print("\n\n>>> SCENARIO 2: Miner Dump (200 miners, 0.1-0.5 year hold)")
    agents = create_test_agents(
        n_miners=200,
        n_stakers=10,
        n_traders=10,
        hold_years_range=(0.1, 0.5),
    )
    results = run_all_models(agents, "miner_dump")
    print_comparison(results)

    # Scenario 3: Long-term holders exit
    print("\n\n>>> SCENARIO 3: Long-Term Exit (6-10 year holds)")
    agents = create_test_agents(
        n_miners=50,
        n_stakers=50,
        n_traders=20,
        hold_years_range=(6, 10),
    )
    results = run_all_models(agents, "long_term_exit")
    print_comparison(results)

    # Scenario 4: Heavy DEX usage (arbitrage attempt)
    print("\n\n>>> SCENARIO 4: DEX Arbitrage (90% use DEX path)")
    agents = create_test_agents(hold_years_range=(0.1, 1.0))
    results = []
    for model in ExitModel:
        result = run_scenario("dex_arbitrage", agents, model, use_dex_pct=0.9)
        results.append(result)
    print_comparison(results)

    # Summary recommendation
    print("\n" + "=" * 80)
    print("SUMMARY: Protocol Capture by Model (higher = more for BTC Reserve)")
    print("=" * 80)

    all_scenarios = ["normal_distribution", "miner_dump", "long_term_exit", "dex_arbitrage"]
    model_captures = {m.value: [] for m in ExitModel}

    # Re-run to collect all captures
    random.seed(42)
    scenarios_data = [
        create_test_agents(),
        create_test_agents(n_miners=200, n_stakers=10, n_traders=10, hold_years_range=(0.1, 0.5)),
        create_test_agents(n_miners=50, n_stakers=50, n_traders=20, hold_years_range=(6, 10)),
        create_test_agents(hold_years_range=(0.1, 1.0)),
    ]

    for scenario_name, agents in zip(all_scenarios, scenarios_data):
        for model in ExitModel:
            dex_pct = 0.9 if scenario_name == "dex_arbitrage" else 0.5
            result = run_scenario(scenario_name, agents, model, use_dex_pct=dex_pct)
            model_captures[model.value].append(result['protocol_capture'])

    print(f"\n{'Model':<20} {'Normal':>10} {'Dump':>10} {'Long-Term':>10} {'DEX Arb':>10} {'Average':>10}")
    print("-" * 70)

    for model_name, captures in model_captures.items():
        avg = sum(captures) / len(captures)
        print(
            f"{model_name:<20} "
            f"{captures[0]:>9.1%} "
            f"{captures[1]:>9.1%} "
            f"{captures[2]:>9.1%} "
            f"{captures[3]:>9.1%} "
            f"{avg:>9.1%}"
        )

    print("\n" + "=" * 80)
    print("RECOMMENDATION: See FI_EXIT_SCENARIOS.md for analysis")
    print("=" * 80)


if __name__ == "__main__":
    main()
