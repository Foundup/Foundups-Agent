"""pAVS Subscription Tier Economics - Usage-Based Model.

012 SPEC (2026-02-17):
"UPS = sats (satoshis)... Free then $2.95, $5.95, $9.95, $19.95, $29.95...
free get ups then you run out... for 2.95/m you double your ups and
the reset is sped up... should it be automatic or selection?"

TWO MODELS TO COMPARE:

A) AUTOMATIC ESCALATION (like mobile data overage)
   - User starts Free
   - When UPs run out, system prompts upgrade
   - If consent given, auto-bills next tier
   - Frictionless but can surprise users

B) MANUAL SELECTION (like Netflix plans)
   - User picks tier upfront
   - Gets fixed UPs/month
   - Runs out = waits for reset
   - Predictable but may lose engagement

C) HYBRID (recommended)
   - User picks base tier
   - Can buy "top-ups" when needed ($0.99 = 500 UPs)
   - Auto-upgrade prompts (not forced)
   - Best of both: predictable + flexible

UPs = SATS CONCEPTUAL MODEL:
- 1 BTC = 100,000,000 sats = 100,000,000 UPs (conceptual)
- At $100K BTC: 1 UP = $0.001 (1/10th of a cent)
- BUT: UPs float with BTC (demurrage model)
- UPs are EARNED (agent work) or BOUGHT (subscription)

AGENT COMPUTE COST MODEL:
- Simple query (search): ~10 UPs
- Standard task (OpenClaw basic): ~50 UPs
- Complex task (GotJunk listing): ~200 UPs
- Heavy compute (CABR validation): ~500 UPs
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math


# ============================================================================
# SUBSCRIPTION TIERS (012 Spec: $2.95, $5.95, $9.95, $19.95, $29.95)
# ============================================================================

@dataclass
class SubscriptionTier:
    """Subscription tier definition."""
    name: str
    price_usd: float
    # Legacy name kept for compatibility; this value is allocated PER RESET CYCLE.
    ups_monthly: int
    reset_days: int            # Days until wallet resets to ups_monthly
    ups_per_dollar: float      # Value proposition
    agents_included: List[str]
    description: str

    @property
    def cycles_per_30d(self) -> float:
        """Number of reset cycles in a 30-day period."""
        return 30 / self.reset_days if self.reset_days > 0 else 0.0

    @property
    def effective_ups_30d(self) -> int:
        """Effective UP allocation across 30 days at configured reset cadence."""
        return int(self.ups_monthly * self.cycles_per_30d)

    @property
    def daily_budget_ups(self) -> float:
        """Average daily UP budget implied by cycle resets."""
        return self.ups_monthly / self.reset_days if self.reset_days > 0 else 0.0


TIERS = {
    "free": SubscriptionTier(
        name="Free",
        price_usd=0.00,
        ups_monthly=1_000,      # ~100 simple queries
        reset_days=30,          # Monthly reset
        ups_per_dollar=float('inf'),
        agents_included=["basic_search", "community_browse"],
        description="Try pAVS - limited to basic search",
    ),
    "starter": SubscriptionTier(
        name="Starter",
        price_usd=2.95,
        ups_monthly=3_000,      # 3x free (not 2x - better value)
        reset_days=15,          # 2x faster reset
        ups_per_dollar=1017,
        agents_included=["basic_search", "community_browse", "simple_tasks"],
        description="Get started with faster resets",
    ),
    "basic": SubscriptionTier(
        name="Basic",
        price_usd=5.95,
        ups_monthly=7_000,      # ~2.3x starter
        reset_days=10,          # 3x faster reset
        ups_per_dollar=1176,
        agents_included=["openclaw_lite", "gotjunk_browse", "task_assist"],
        description="Access lite versions of core agents",
    ),
    "plus": SubscriptionTier(
        name="Plus",
        price_usd=9.95,
        ups_monthly=15_000,     # ~2x basic
        reset_days=7,           # Weekly reset
        ups_per_dollar=1508,
        agents_included=["openclaw", "gotjunk", "promoter_basic", "cabr_lite"],
        description="Full access to core agents",
    ),
    "pro": SubscriptionTier(
        name="Pro",
        price_usd=19.95,
        ups_monthly=40_000,     # ~2.7x plus
        reset_days=5,           # 6x faster reset
        ups_per_dollar=2005,
        agents_included=["openclaw_pro", "gotjunk_pro", "promoter", "cabr_validator", "custom_workflows"],
        description="Professional agent suite + CABR validation",
    ),
    "enterprise": SubscriptionTier(
        name="Enterprise",
        price_usd=29.95,
        ups_monthly=100_000,    # 2.5x pro
        reset_days=3,           # Near-continuous
        ups_per_dollar=3339,
        agents_included=["all_agents", "priority_queue", "custom_agent_builder", "white_label", "api_access"],
        description="Full ecosystem + custom agents + API",
    ),
}

# ============================================================================
# ANGEL TIER (Accredited Investors Only - $195/month)
# ============================================================================
#
# THE GATE STRUCTURE:
# - ALL FoundUps are INVITE-ONLY until they OPO
# - Angels ($195/month) are the ONLY way to access pre-OPO FoundUps
# - When F_i reaches RED HOT rating -> OPO alert sent to Angels
# - Angels can STAKE UPS to get F_i allocation (20% to pAVS treasury)
# - Angels can PASS (pay 100K UPS pass fee -> next Angel in queue)
# - After OPO: FoundUp becomes PUBLIC, all tiers can access
#
# This creates:
# 1. Scarcity: Pre-OPO F_i only available to Angels
# 2. Quality signal: Angel stakes = validation
# 3. Treasury flow: 20% of ALL Angel OPO activity
# 4. FOMO: Pass still costs UPS
#

@dataclass
class AngelTierConfig:
    """Angel tier for accredited investors - OPO deal flow access."""
    name: str = "Angel"
    price_usd: float = 195.00
    ups_monthly: int = 2_000_000      # 2M UPS for OPO staking
    reset_days: int = 1               # Daily reset - always ready for OPO
    ups_per_dollar: float = 10256.41  # Best value tier

    # OPO mechanics
    opo_treasury_fee: float = 0.20    # 20% of UPS stake -> pAVS treasury
    opo_fi_allocation: float = 0.80   # 80% of UPS stake -> F_i backing
    pass_fee_ups: int = 100_000       # 100K UPS if Angel passes on OPO

    # Gate requirements
    requires_accreditation: bool = True
    max_angels_per_opo: int = 10      # Cap per OPO to maintain scarcity
    opo_window_hours: int = 24        # Decision window

    # Included access
    agents_included: List[str] = None

    def __post_init__(self):
        if self.agents_included is None:
            self.agents_included = [
                "all_agents",
                "opo_alerts",           # RED HOT notifications
                "pre_opo_access",       # Invite-only FoundUp access
                "fi_rating_dashboard",  # Real-time F_i ratings
                "angel_syndicate",      # Coordinate with other Angels
                "priority_support",
            ]


ANGEL_TIER = AngelTierConfig()


@dataclass
class OPOStakeResult:
    """Result of an Angel staking in an OPO."""
    angel_id: str
    foundup_id: str
    ups_staked: int
    ups_to_treasury: int      # 20%
    ups_to_fi_backing: int    # 80%
    fi_tokens_received: int
    timestamp: str


@dataclass
class OPOPassResult:
    """Result of an Angel passing on an OPO."""
    angel_id: str
    foundup_id: str
    pass_fee_ups: int         # Goes to pAVS treasury
    next_angel_id: str        # Alert forwarded to
    timestamp: str


def calculate_angel_opo_stake(
    ups_to_stake: int,
    fi_available: int,
    total_ups_staked_so_far: int = 0,
) -> OPOStakeResult:
    """Calculate F_i allocation for an Angel OPO stake.

    Args:
        ups_to_stake: UPS the Angel wants to stake
        fi_available: Total F_i available in this OPO
        total_ups_staked_so_far: UPS already staked by other Angels

    Returns:
        OPOStakeResult with allocation breakdown
    """
    # Apply treasury fee
    ups_to_treasury = int(ups_to_stake * ANGEL_TIER.opo_treasury_fee)
    ups_to_fi_backing = ups_to_stake - ups_to_treasury

    # F_i allocation is proportional to UPS staked
    # (simplified - real implementation would use bonding curve)
    total_ups_pool = total_ups_staked_so_far + ups_to_fi_backing
    stake_ratio = ups_to_fi_backing / total_ups_pool if total_ups_pool > 0 else 1.0
    fi_tokens = int(fi_available * stake_ratio * 0.5)  # 50% of available per round

    return OPOStakeResult(
        angel_id="",  # Set by caller
        foundup_id="",  # Set by caller
        ups_staked=ups_to_stake,
        ups_to_treasury=ups_to_treasury,
        ups_to_fi_backing=ups_to_fi_backing,
        fi_tokens_received=fi_tokens,
        timestamp="",  # Set by caller
    )

# Top-up option (buy extra UPs anytime)
TOPUP_OPTIONS = {
    "small": {"price_usd": 0.99, "ups": 500, "ups_per_dollar": 505},
    "medium": {"price_usd": 2.99, "ups": 2000, "ups_per_dollar": 669},
    "large": {"price_usd": 4.99, "ups": 4000, "ups_per_dollar": 802},
    "mega": {"price_usd": 9.99, "ups": 10000, "ups_per_dollar": 1001},
}


# ============================================================================
# AGENT COMPUTE COSTS (UPs per operation)
# ============================================================================

AGENT_COSTS = {
    # Basic operations
    "basic_search": 10,
    "community_browse": 5,
    "simple_tasks": 20,

    # OpenClaw
    "openclaw_lite": 30,
    "openclaw": 50,
    "openclaw_pro": 80,

    # GotJunk
    "gotjunk_browse": 15,
    "gotjunk": 100,
    "gotjunk_pro": 150,
    "gotjunk_listing_create": 200,
    "gotjunk_pickup_schedule": 300,

    # Promoter
    "promoter_basic": 25,
    "promoter": 75,
    "promoter_campaign": 250,

    # CABR
    "cabr_lite": 50,
    "cabr_validator": 150,
    "cabr_full_audit": 500,

    # Custom
    "custom_workflows": 100,
    "custom_agent_builder": 500,
    "api_call": 10,
}


def calculate_monthly_capacity(tier_name: str) -> Dict[str, int]:
    """Calculate how many of each agent operation a tier can afford per month."""
    tier = TIERS.get(tier_name)
    if not tier:
        return {}

    capacity = {}
    for agent, cost in AGENT_COSTS.items():
        if agent in tier.agents_included or "all_agents" in tier.agents_included:
            capacity[agent] = tier.ups_monthly // cost

    return capacity


def model_usage_pattern(
    tier_name: str,
    daily_queries: int = 10,
    heavy_task_pct: float = 0.1,
) -> Dict:
    """Model typical usage pattern for a tier.

    Args:
        tier_name: Subscription tier
        daily_queries: Average queries per day
        heavy_task_pct: Percent of queries that are heavy compute

    Returns:
        Usage analysis
    """
    tier = TIERS.get(tier_name)
    if not tier:
        return {}

    # Cost calculation
    simple_cost = 20  # Average simple query
    heavy_cost = 200  # Average heavy task

    daily_ups = (daily_queries * (1 - heavy_task_pct) * simple_cost +
                 daily_queries * heavy_task_pct * heavy_cost)

    days_until_exhausted = tier.ups_monthly / daily_ups if daily_ups > 0 else float('inf')

    return {
        "tier": tier_name,
        "ups_monthly": tier.ups_monthly,
        "reset_days": tier.reset_days,
        "daily_queries": daily_queries,
        "daily_ups_used": round(daily_ups, 0),
        "days_until_exhausted": round(days_until_exhausted, 1),
        "sustainable": days_until_exhausted >= tier.reset_days,
        "headroom_pct": round((days_until_exhausted / tier.reset_days - 1) * 100, 1) if days_until_exhausted >= tier.reset_days else -round((1 - days_until_exhausted / tier.reset_days) * 100, 1),
    }


def recommend_tier(daily_queries: int, heavy_task_pct: float = 0.1) -> str:
    """Recommend appropriate tier based on usage."""
    for tier_name in ["free", "starter", "basic", "plus", "pro", "enterprise"]:
        usage = model_usage_pattern(tier_name, daily_queries, heavy_task_pct)
        if usage.get("sustainable"):
            return tier_name
    return "enterprise"


def get_tier_capacity_metrics() -> Dict[str, Dict]:
    """Return investor-facing capacity metrics per tier."""
    result: Dict[str, Dict] = {}
    for tier_name, tier in TIERS.items():
        result[tier_name] = {
            "price_usd": tier.price_usd,
            "ups_per_cycle": tier.ups_monthly,
            "reset_days": tier.reset_days,
            "daily_budget_ups": round(tier.daily_budget_ups, 2),
            "effective_ups_30d": tier.effective_ups_30d,
            "agents_included": list(tier.agents_included),
        }
    return result


# ============================================================================
# AUTOMATIC vs MANUAL ESCALATION MODELS
# ============================================================================

@dataclass
class UserUsage:
    """Track user's UPs usage."""
    tier: str
    ups_remaining: int
    ups_used_this_period: int
    days_since_reset: int
    auto_escalate_enabled: bool
    topups_purchased: int
    total_spent_usd: float


def simulate_auto_escalation(
    initial_tier: str = "free",
    daily_queries: int = 15,
    heavy_task_pct: float = 0.15,
    months: int = 3,
    auto_consent: bool = True,
) -> List[Dict]:
    """Simulate automatic tier escalation over time.

    When user runs out of UPs:
    - If auto_consent: Upgrade to next tier
    - If not: Wait for reset (lost engagement)
    """
    results = []
    tier = TIERS[initial_tier]
    current_tier_name = initial_tier
    ups_remaining = tier.ups_monthly
    total_spent = tier.price_usd
    day = 0
    upgrades = 0

    tier_order = ["free", "starter", "basic", "plus", "pro", "enterprise"]

    for month in range(months):
        for day_of_month in range(30):
            day += 1

            # Daily usage
            simple_cost = 20
            heavy_cost = 200
            daily_ups = (daily_queries * (1 - heavy_task_pct) * simple_cost +
                         daily_queries * heavy_task_pct * heavy_cost)

            ups_remaining -= daily_ups

            # Check if ran out
            if ups_remaining <= 0:
                if auto_consent and current_tier_name != "enterprise":
                    # Auto-upgrade
                    current_idx = tier_order.index(current_tier_name)
                    current_tier_name = tier_order[current_idx + 1]
                    tier = TIERS[current_tier_name]
                    ups_remaining = tier.ups_monthly
                    total_spent += tier.price_usd
                    upgrades += 1
                else:
                    # Wait for reset (skip days)
                    ups_remaining = 0

            # Check for reset
            if day_of_month > 0 and day_of_month % tier.reset_days == 0:
                ups_remaining = tier.ups_monthly

        results.append({
            "month": month + 1,
            "tier": current_tier_name,
            "total_spent": round(total_spent, 2),
            "upgrades": upgrades,
        })

    return results


def simulate_manual_selection(
    selected_tier: str = "basic",
    daily_queries: int = 15,
    heavy_task_pct: float = 0.15,
    months: int = 3,
    allow_topups: bool = True,
) -> List[Dict]:
    """Simulate manual tier selection with optional top-ups."""
    results = []
    tier = TIERS[selected_tier]
    ups_remaining = tier.ups_monthly
    total_spent = tier.price_usd * months  # Pay upfront
    topups = 0
    days_throttled = 0

    for month in range(months):
        for day_of_month in range(30):
            simple_cost = 20
            heavy_cost = 200
            daily_ups = (daily_queries * (1 - heavy_task_pct) * simple_cost +
                         daily_queries * heavy_task_pct * heavy_cost)

            if ups_remaining >= daily_ups:
                ups_remaining -= daily_ups
            elif allow_topups:
                # Buy top-up
                topup = TOPUP_OPTIONS["medium"]
                ups_remaining += topup["ups"]
                total_spent += topup["price_usd"]
                topups += 1
                ups_remaining -= daily_ups
            else:
                days_throttled += 1

            # Check for reset
            if day_of_month > 0 and day_of_month % tier.reset_days == 0:
                ups_remaining = tier.ups_monthly

        results.append({
            "month": month + 1,
            "tier": selected_tier,
            "total_spent": round(total_spent, 2),
            "topups": topups,
            "days_throttled": days_throttled,
        })

    return results


# ============================================================================
# REVENUE PROJECTION
# ============================================================================

def project_subscription_revenue(
    users: int = 10000,
    months: int = 12,
    btc_price: float = 100000,
) -> Dict:
    """Project subscription revenue with tier distribution.

    Assumes tier distribution based on typical SaaS patterns:
    - Free: 70% (high, need conversion)
    - Paid: 30% distributed across tiers
    """
    # Tier distribution (% of total users)
    distribution = {
        "free": 0.70,
        "starter": 0.12,
        "basic": 0.08,
        "plus": 0.05,
        "pro": 0.03,
        "enterprise": 0.02,
    }

    monthly_revenue = 0
    for tier_name, pct in distribution.items():
        tier = TIERS[tier_name]
        tier_users = int(users * pct)
        monthly_revenue += tier_users * tier.price_usd

    annual_revenue = monthly_revenue * 12
    btc_to_reserve = annual_revenue / btc_price

    # UPs distributed
    # - cycle_nominal: one cycle allocation per user (legacy view)
    # - effective_30d: reset-aware allocation inside a 30-day billing period
    monthly_ups_cycle_nominal = 0
    monthly_ups_effective_30d = 0
    for tier_name, pct in distribution.items():
        tier = TIERS[tier_name]
        tier_users = int(users * pct)
        monthly_ups_cycle_nominal += tier_users * tier.ups_monthly
        monthly_ups_effective_30d += tier_users * tier.effective_ups_30d

    return {
        "users": users,
        "paid_users": int(users * 0.30),
        "mrr_usd": round(monthly_revenue, 2),
        "arr_usd": round(annual_revenue, 2),
        "btc_to_reserve_annual": round(btc_to_reserve, 4),
        "ups_monthly_distributed": monthly_ups_cycle_nominal,  # legacy compatibility
        "ups_monthly_distributed_effective": monthly_ups_effective_30d,
        "arpu_paid": round(monthly_revenue / (users * 0.30), 2) if users > 0 else 0,
    }


def print_tier_analysis():
    """Print comprehensive tier analysis."""

    print("\n" + "=" * 100)
    print("pAVS SUBSCRIPTION TIER ECONOMICS")
    print("=" * 100)

    print("\nTIER PRICING (012 Spec):")
    print("-" * 100)
    print(f"{'Tier':<12} {'Price':<10} {'UPs/mo':<12} {'Reset':<10} {'UPs/$':<10} {'Agents':<30}")
    print("-" * 100)

    for name, tier in TIERS.items():
        agents_str = ", ".join(tier.agents_included[:3])
        if len(tier.agents_included) > 3:
            agents_str += f" +{len(tier.agents_included) - 3}"
        print(f"{tier.name:<12} ${tier.price_usd:<9.2f} {tier.ups_monthly:<12,} {tier.reset_days}d{'':<7} {tier.ups_per_dollar:<10.0f} {agents_str:<30}")

    print("\n" + "-" * 100)
    print("VALUE SCALING (Higher tier = better UPs/$ ratio)")
    print("-" * 100)
    print("""
    Free:       $0      ->  1,000 UPs  (baseline)
    Starter:    $2.95   ->  3,000 UPs  (1,017/$ - 3x value)
    Basic:      $5.95   ->  7,000 UPs  (1,176/$ - 7x value)
    Plus:       $9.95   -> 15,000 UPs  (1,508/$ - 15x value)
    Pro:        $19.95  -> 40,000 UPs  (2,005/$ - 40x value)
    Enterprise: $29.95  ->100,000 UPs  (3,339/$ - 100x value)

    INCENTIVE: Higher tiers are progressively better value.
""")

    # Usage modeling
    print("\n" + "=" * 100)
    print("USAGE PATTERNS - HOW LONG DO UPs LAST?")
    print("=" * 100)
    print(f"\nAssumption: User makes ~15 queries/day, 15% are heavy tasks")
    print("-" * 100)
    print(f"{'Tier':<12} {'UPs/mo':<12} {'Daily Use':<12} {'Days Last':<12} {'Sustainable?':<12} {'Headroom':<12}")
    print("-" * 100)

    for tier_name in TIERS:
        usage = model_usage_pattern(tier_name, daily_queries=15, heavy_task_pct=0.15)
        sustainable = "Yes" if usage["sustainable"] else "NO"
        headroom = f"{usage['headroom_pct']:+.0f}%" if usage["sustainable"] else f"{usage['headroom_pct']:.0f}%"
        print(f"{tier_name:<12} {usage['ups_monthly']:<12,} {usage['daily_ups_used']:<12,.0f} "
              f"{usage['days_until_exhausted']:<12.1f} {sustainable:<12} {headroom:<12}")

    # Model comparison
    print("\n" + "=" * 100)
    print("AUTO vs MANUAL ESCALATION (3-month simulation)")
    print("=" * 100)

    auto_results = simulate_auto_escalation("free", daily_queries=20, months=3)
    manual_results = simulate_manual_selection("plus", daily_queries=20, months=3)

    print(f"""
SCENARIO: User does 20 queries/day, 15% heavy tasks

A) AUTOMATIC ESCALATION (start Free, auto-upgrade when out):
   Month 1: {auto_results[0]['tier']} tier, spent ${auto_results[0]['total_spent']:.2f}
   Month 2: {auto_results[1]['tier']} tier, spent ${auto_results[1]['total_spent']:.2f}
   Month 3: {auto_results[2]['tier']} tier, spent ${auto_results[2]['total_spent']:.2f}
   Total upgrades: {auto_results[2]['upgrades']}

B) MANUAL SELECTION (pick Plus tier, buy top-ups when out):
   Month 1: {manual_results[0]['tier']} tier, spent ${manual_results[0]['total_spent']:.2f}, {manual_results[0]['topups']} top-ups
   Month 2: {manual_results[1]['tier']} tier, spent ${manual_results[1]['total_spent']:.2f}, {manual_results[1]['topups']} top-ups
   Month 3: {manual_results[2]['tier']} tier, spent ${manual_results[2]['total_spent']:.2f}, {manual_results[2]['topups']} top-ups

RECOMMENDATION: HYBRID MODEL
- User picks base tier (predictable cost)
- Can buy top-ups when needed (flexibility)
- Auto-upgrade PROMPTS (not forced) when usage pattern suggests
""")

    # Revenue projection
    print("\n" + "=" * 100)
    print("REVENUE PROJECTION (10K users)")
    print("=" * 100)

    rev = project_subscription_revenue(10000)
    print(f"""
Users:               {rev['users']:,}
Paid Users (30%):    {rev['paid_users']:,}
MRR:                 ${rev['mrr_usd']:,.2f}
ARR:                 ${rev['arr_usd']:,.2f}
BTC to Reserve/yr:   {rev['btc_to_reserve_annual']:.4f} BTC
UPs distributed/mo:  {rev['ups_monthly_distributed']:,}
UPs effective/30d:   {rev['ups_monthly_distributed_effective']:,}
ARPU (paid users):   ${rev['arpu_paid']:.2f}/month

At 100K users:
  MRR: ~${rev['mrr_usd'] * 10:,.0f}
  ARR: ~${rev['arr_usd'] * 10:,.0f}
  BTC: ~{rev['btc_to_reserve_annual'] * 10:.2f} BTC/year
""")


def main():
    """Run tier analysis."""
    print_tier_analysis()


if __name__ == "__main__":
    main()
