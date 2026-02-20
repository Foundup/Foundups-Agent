"""Perplexity AI vs pAVS Revenue Model Comparison.

012 REQUEST (2026-02-17):
"deep dive into Perflexity module and their revenue and growth...
because we are a lot like them... our membership allows people to access
'compute' - compute just is agent... so imagine pay for a sub to access
openclaw or other modules... and we earn like perplexity?"

PERPLEXITY AI DATA (Web Research 2026-02-17):
Sources:
- DemandSage: $200M ARR (Sep 2025), $656M target (2026)
- Business of Apps: 230% YoY growth target
- Sacra: $20B valuation at 100x revenue
- FameWall: 22M users

PERPLEXITY REVENUE MODEL:
- Pro: $20/month ($240/year)
- Max: $200/month (premium features)
- Comet Plus: $5/month (content access)
- Enterprise: Custom pricing
- API: Usage-based

pAVS PARALLEL:
- Subscription → Access 0102 agents (not generic AI)
- "Compute" = Agent services (OpenClaw, GotJunk, etc.)
- BTC-backed UPs currency (Hotel California)
- Demurrage forces velocity (use it or lose it)
- F_i tokens per FoundUp (equity-like participation)

KEY INSIGHT (012's question):
"BTC never leaves Hotel California effect... and instead UPS becomes
the representation recycling BTC into the community via UPS awards"

WHAT'S ALREADY MODELED:
- Hotel California: btc_reserve.py (BTC IN, never OUT)
- UPs Demurrage: demurrage.py (bio-decay forces velocity)
- Inactive Recycling: demurrage.py (dormant → treasury)
- Subscription to BTC: btc_reserve.py receive_crypto_subscription()

WHAT NEEDS MODELING:
- Subscription tier pricing (like Perplexity Pro/Max/Enterprise)
- Agent access per tier (OpenClaw, GotJunk, etc.)
- Subscription revenue growth curve
- Network effect of agents improving with more users
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import math


# ============================================================================
# PERPLEXITY AI ACTUAL DATA (2025-2026)
# ============================================================================

PERPLEXITY_DATA = {
    # Revenue milestones (ARR)
    "arr_mid_2024": 35_000_000,      # $35M ARR (mid-2024)
    "arr_mar_2025": 100_000_000,     # $100M ARR (Mar 2025)
    "arr_jul_2025": 150_000_000,     # $150M ARR (Jul 2025)
    "arr_sep_2025": 200_000_000,     # $200M ARR (Sep 2025)
    "arr_target_2026": 656_000_000,  # $656M target (end 2026)

    # User growth
    "users_2024": 10_000_000,        # 10M users
    "users_2025": 22_000_000,        # 22M users
    "user_growth_yoy": 1.20,         # 120% YoY

    # Pricing tiers
    "price_pro_monthly": 20,         # $20/month
    "price_max_monthly": 200,        # $200/month (premium)
    "price_comet_monthly": 5,        # $5/month (content)

    # Conversion rates
    "free_to_paid_rate": 0.05,       # ~5% convert to paid
    "pro_to_max_rate": 0.02,         # ~2% of Pro upgrade to Max

    # Valuation
    "valuation_2025": 20_000_000_000,  # $20B valuation
    "revenue_multiple": 100,           # 100x revenue valuation

    # Growth drivers
    "airtel_india_boost": 6.4,       # 640% YoY in India after Airtel deal
}

# ============================================================================
# pAVS SUBSCRIPTION MODEL (Parallel to Perplexity)
# ============================================================================

PAVS_SUBSCRIPTION_TIERS = {
    # Tier: (monthly_usd, monthly_ups_allocation, agents_included)
    "free": {
        "price_usd": 0,
        "ups_allocation": 100,        # Small free allocation
        "agents": ["basic_search"],
        "description": "Try pAVS with limited access",
    },
    "member": {
        "price_usd": 20,              # Same as Perplexity Pro
        "ups_allocation": 5000,       # 5K UPs/month
        "agents": ["openclaw", "gotjunk_basic", "community_search"],
        "description": "Access core 0102 agents",
    },
    "pro": {
        "price_usd": 50,              # Higher for premium agents
        "ups_allocation": 15000,      # 15K UPs/month
        "agents": ["openclaw_pro", "gotjunk_pro", "cabr_validator", "promoter_agent"],
        "description": "Professional agent access + CABR validation",
    },
    "enterprise": {
        "price_usd": 200,             # Like Perplexity Max
        "ups_allocation": 100000,     # 100K UPs/month
        "agents": ["all_agents", "custom_agent_builder", "white_label"],
        "description": "Full ecosystem access + custom agents",
    },
}

# Conversion assumptions (conservative vs Perplexity)
PAVS_CONVERSION_RATES = {
    "free_to_member": 0.03,    # 3% (lower than Perplexity - harder ask)
    "member_to_pro": 0.10,     # 10% upgrade
    "pro_to_enterprise": 0.05, # 5% upgrade
}


@dataclass
class SubscriptionRevenue:
    """Monthly subscription revenue breakdown."""
    month: int
    total_users: int
    free_users: int
    member_users: int
    pro_users: int
    enterprise_users: int
    mrr_usd: float           # Monthly recurring revenue (USD)
    btc_to_reserve: float    # BTC flowing to Hotel California
    ups_allocated: float     # UPs distributed to subscribers
    churn_rate: float


def model_perplexity_growth_curve(months: int = 36) -> List[Dict]:
    """Model Perplexity-like growth over N months.

    Perplexity pattern:
    - Exponential early growth
    - S-curve saturation
    - ~230% YoY target

    Returns:
        List of monthly snapshots
    """
    results = []

    # Starting point (like Perplexity mid-2024)
    arr = PERPLEXITY_DATA["arr_mid_2024"]

    # Monthly growth rate to achieve 230% YoY
    monthly_growth = 1.08  # ~8% monthly = 230% YoY compound

    for month in range(months):
        # S-curve modulation (growth slows as market saturates)
        # sigmoid: growth_factor = 1 / (1 + e^(k*(month - inflection)))
        inflection = 24  # Inflection point at 2 years
        k = 0.1
        saturation_factor = 1 - 0.7 * (1 / (1 + math.exp(-k * (month - inflection))))

        effective_growth = 1 + (monthly_growth - 1) * saturation_factor
        arr = arr * effective_growth

        results.append({
            "month": month,
            "arr_usd": round(arr, 2),
            "mrr_usd": round(arr / 12, 2),
            "monthly_growth": round((effective_growth - 1) * 100, 2),
        })

    return results


def model_pavs_subscription_growth(
    months: int = 36,
    initial_users: int = 1000,
    monthly_user_growth: float = 1.10,  # 10% monthly growth
    btc_price: float = 100000,
) -> List[SubscriptionRevenue]:
    """Model pAVS subscription revenue growth.

    Key differences from Perplexity:
    1. Subscription paid in crypto → BTC reserve (Hotel California)
    2. UPs allocated to subscribers (bio-decay, velocity)
    3. Agents improve with network effect (more data → better agents)

    Args:
        months: Projection length
        initial_users: Starting user count
        monthly_user_growth: User growth rate
        btc_price: BTC price assumption

    Returns:
        List of monthly subscription snapshots
    """
    results = []

    users = initial_users
    churn_rate = 0.05  # 5% monthly churn (industry standard)

    for month in range(months):
        # User growth with S-curve modulation
        inflection = 18
        saturation = 1 - 0.5 * (1 / (1 + math.exp(-0.15 * (month - inflection))))
        effective_growth = 1 + (monthly_user_growth - 1) * saturation

        # Apply churn
        users = int(users * effective_growth * (1 - churn_rate))

        # Tier distribution (shifts over time as users upgrade)
        maturity_factor = min(1.0, month / 24)  # 2 years to mature

        free_pct = 0.85 - (0.10 * maturity_factor)      # 85% → 75%
        member_pct = 0.10 + (0.05 * maturity_factor)    # 10% → 15%
        pro_pct = 0.04 + (0.03 * maturity_factor)       # 4% → 7%
        enterprise_pct = 0.01 + (0.02 * maturity_factor)  # 1% → 3%

        free_users = int(users * free_pct)
        member_users = int(users * member_pct)
        pro_users = int(users * pro_pct)
        enterprise_users = int(users * enterprise_pct)

        # Calculate MRR
        mrr_usd = (
            member_users * PAVS_SUBSCRIPTION_TIERS["member"]["price_usd"] +
            pro_users * PAVS_SUBSCRIPTION_TIERS["pro"]["price_usd"] +
            enterprise_users * PAVS_SUBSCRIPTION_TIERS["enterprise"]["price_usd"]
        )

        # BTC to Hotel California
        btc_to_reserve = mrr_usd / btc_price

        # UPs allocated to subscribers
        ups_allocated = (
            free_users * PAVS_SUBSCRIPTION_TIERS["free"]["ups_allocation"] +
            member_users * PAVS_SUBSCRIPTION_TIERS["member"]["ups_allocation"] +
            pro_users * PAVS_SUBSCRIPTION_TIERS["pro"]["ups_allocation"] +
            enterprise_users * PAVS_SUBSCRIPTION_TIERS["enterprise"]["ups_allocation"]
        )

        results.append(SubscriptionRevenue(
            month=month,
            total_users=users,
            free_users=free_users,
            member_users=member_users,
            pro_users=pro_users,
            enterprise_users=enterprise_users,
            mrr_usd=mrr_usd,
            btc_to_reserve=btc_to_reserve,
            ups_allocated=ups_allocated,
            churn_rate=churn_rate,
        ))

    return results


def compare_revenue_models() -> None:
    """Compare Perplexity vs pAVS revenue models."""

    print("\n" + "=" * 100)
    print("PERPLEXITY AI vs pAVS REVENUE MODEL COMPARISON")
    print("=" * 100)

    print("""
PERPLEXITY AI (Actual Data):
  ARR Mid-2024:      $35M
  ARR Sep-2025:      $200M (470% growth in 15 months)
  ARR Target 2026:   $656M (230% YoY)
  Users:             22M
  Valuation:         $20B (100x revenue)

  Pricing:
    - Pro: $20/month
    - Max: $200/month
    - Comet Plus: $5/month
    - Free tier with limits

  KEY: Access to AI compute (search + chat)
""")

    print("""
pAVS PARALLEL MODEL:
  Subscription -> Access 0102 Agents (not generic AI)
  "Compute" = Agent services (OpenClaw, GotJunk, etc.)

  Pricing (proposed):
    - Free: 100 UPs/month, basic search
    - Member: $20/month, 5K UPs, core agents
    - Pro: $50/month, 15K UPs, premium agents + CABR
    - Enterprise: $200/month, 100K UPs, all agents + custom

  KEY DIFFERENCES:
    1. BTC-backed currency (UPs) - not USD-denominated
    2. Hotel California: BTC flows IN, never OUT
    3. Demurrage: UPs decay -> forces velocity
    4. F_i tokens: Equity-like participation per FoundUp
    5. Network Pool: Inactive UPs -> back to community
""")

    # Model both growth curves
    perplexity_growth = model_perplexity_growth_curve(36)
    pavs_growth = model_pavs_subscription_growth(36, initial_users=5000)

    print("\n" + "-" * 100)
    print("YEAR 1 COMPARISON (Months 0-12)")
    print("-" * 100)
    print(f"{'Month':>5} {'Perplexity ARR':>18} {'pAVS MRR':>15} {'pAVS Users':>12} {'BTC/month':>12}")
    print("-" * 100)

    for month in [0, 3, 6, 9, 12]:
        pp = perplexity_growth[month]
        pv = pavs_growth[month]
        print(f"{month:>5} ${pp['arr_usd']:>16,.0f} ${pv.mrr_usd:>13,.0f} {pv.total_users:>12,} {pv.btc_to_reserve:>11.4f}")

    print("\n" + "-" * 100)
    print("YEAR 3 PROJECTION (Month 36)")
    print("-" * 100)

    pp_y3 = perplexity_growth[35]
    pv_y3 = pavs_growth[35]

    print(f"""
PERPLEXITY (projected):
  ARR Year 3:        ${pp_y3['arr_usd']:,.0f}
  Monthly Growth:    {pp_y3['monthly_growth']:.1f}%

pAVS (projected):
  MRR Year 3:        ${pv_y3.mrr_usd:,.0f}
  ARR Year 3:        ${pv_y3.mrr_usd * 12:,.0f}
  Total Users:       {pv_y3.total_users:,}
  Paid Users:        {pv_y3.member_users + pv_y3.pro_users + pv_y3.enterprise_users:,}
  BTC in Reserve:    {sum(p.btc_to_reserve for p in pavs_growth[:36]):.2f} BTC (from subs only)
  UPs/month:         {pv_y3.ups_allocated:,}
""")

    # What's already modeled
    print("\n" + "=" * 100)
    print("WHAT'S ALREADY MODELED IN SIMULATOR")
    print("=" * 100)
    print("""
1. HOTEL CALIFORNIA (btc_reserve.py):
   [X] BTC flows IN via: subscriptions, fees, demurrage
   [X] BTC NEVER flows OUT
   [X] Multi-crypto support (ETH, SOL, USDC -> convert to BTC)
   [X] UPs value floats with BTC price

2. UPS DEMURRAGE (demurrage.py):
   [X] LIQUID UPs decays: 0.5% - 5% monthly (adaptive)
   [X] Activity tiers: ACTIVE (0.5x), MODERATE (1x), PASSIVE (2x), DORMANT (2.5x)
   [X] Decay redistributed: 80% Network Pool, 20% Treasury

3. INACTIVE ACCOUNT RECYCLING (demurrage.py):
   [X] Accounts dormant >90 days -> UPs recycled to participation pool
   [X] 1% per day beyond threshold
   [X] Prevents dead-account accumulation

4. SUBSCRIPTION TO BTC (btc_reserve.py):
   [X] receive_crypto_subscription() - any crypto -> BTC reserve
   [X] receive_ups_subscription() - pay with UPs -> BURNS UPs
   [X] Full tracking by source and human_id
""")

    print("""
WHAT NEEDS TO BE ADDED:
- [ ] Subscription TIERS (Free/Member/Pro/Enterprise)
- [ ] Agent access per tier (OpenClaw, GotJunk, etc.)
- [ ] UPs ALLOCATION per tier (monthly)
- [ ] Subscription churn modeling
- [ ] Agent utilization → F_i earnings
- [ ] Network effect: more users → better agents
""")


def model_ups_recycling_effect(
    months: int = 36,
    initial_ups_supply: float = 1_000_000,
    demurrage_rate: float = 0.02,  # 2% monthly decay
    subscription_inflow_rate: float = 0.03,  # 3% monthly new UPs from subs
) -> List[Dict]:
    """Model UPs recycling: decay → treasury → back to community.

    012's key insight:
    "BTC never leaves Hotel California effect... and instead UPS becomes
    the representation recycling BTC into the community via UPS awards"

    Flow:
    1. Subscription $ → BTC Reserve (Hotel California)
    2. BTC backs UPs → UPs allocated to subscribers
    3. Inactive UPs → Demurrage → Network Pool (80%) + Treasury (20%)
    4. Network Pool → Agent rewards → Active users
    5. Cycle repeats

    Args:
        months: Projection length
        initial_ups_supply: Starting UPs supply
        demurrage_rate: Monthly decay rate
        subscription_inflow_rate: Monthly UPs inflow from subscriptions

    Returns:
        Monthly UPs flow snapshots
    """
    results = []

    ups_circulating = initial_ups_supply
    ups_in_network_pool = 0.0
    ups_in_treasury = 0.0
    total_decayed = 0.0
    total_recycled = 0.0

    for month in range(months):
        # New UPs from subscriptions (backed by BTC)
        new_ups = ups_circulating * subscription_inflow_rate
        ups_circulating += new_ups

        # Demurrage: inactive UPs decay
        decayed = ups_circulating * demurrage_rate
        ups_circulating -= decayed
        total_decayed += decayed

        # Redistribution: 80% Network Pool, 20% Treasury
        to_network = decayed * 0.80
        to_treasury = decayed * 0.20
        ups_in_network_pool += to_network
        ups_in_treasury += to_treasury

        # Network Pool drips back to community (agent rewards)
        # Assume 50% of Network Pool distributed per month
        recycled_to_community = ups_in_network_pool * 0.50
        ups_in_network_pool -= recycled_to_community
        ups_circulating += recycled_to_community
        total_recycled += recycled_to_community

        results.append({
            "month": month,
            "ups_circulating": round(ups_circulating, 2),
            "ups_network_pool": round(ups_in_network_pool, 2),
            "ups_treasury": round(ups_in_treasury, 2),
            "monthly_decayed": round(decayed, 2),
            "monthly_recycled": round(recycled_to_community, 2),
            "total_decayed": round(total_decayed, 2),
            "total_recycled": round(total_recycled, 2),
            "velocity": round(total_recycled / (ups_circulating + 1), 4),
        })

    return results


def print_ups_recycling_analysis():
    """Print UPs recycling analysis."""

    print("\n" + "=" * 100)
    print("UPS RECYCLING: HOTEL CALIFORNIA + COMMUNITY AWARDS")
    print("=" * 100)

    print("""
012's INSIGHT:
  "BTC never leaves Hotel California effect...
   and instead UPS becomes the representation
   recycling BTC into the community via UPS awards"

THE CYCLE:
  1. Subscription $ → BTC Reserve (locked forever)
  2. BTC backs UPs → Allocated to subscribers
  3. Inactive UPs → Demurrage (bio-decay)
  4. Decayed UPs → 80% Network Pool + 20% Treasury
  5. Network Pool → Agent rewards → Active users
  6. Active users → Use agents → Earn more UPs
  7. REPEAT

KEY: BTC is the foundation (locked), UPs is the velocity layer (circulating)
""")

    # Model UPs recycling
    recycling = model_ups_recycling_effect(36)

    print("\n" + "-" * 100)
    print("UPS RECYCLING OVER 3 YEARS")
    print("-" * 100)
    print(f"{'Month':>5} {'Circulating':>15} {'Network Pool':>15} {'Treasury':>15} {'Velocity':>10}")
    print("-" * 100)

    for month in [0, 6, 12, 18, 24, 30, 35]:
        r = recycling[month]
        print(f"{month:>5} {r['ups_circulating']:>15,.0f} {r['ups_network_pool']:>15,.0f} "
              f"{r['ups_treasury']:>15,.0f} {r['velocity']:>10.3f}")

    final = recycling[-1]
    print(f"""
YEAR 3 SUMMARY:
  Total Decayed:     {final['total_decayed']:,.0f} UPs
  Total Recycled:    {final['total_recycled']:,.0f} UPs
  Velocity Factor:   {final['velocity']:.3f}
  Network Pool:      {final['ups_network_pool']:,.0f} UPs (reserves)
  Treasury:          {final['ups_treasury']:,.0f} UPs (infrastructure)

  The system FORCES velocity - UPs must flow or decay!
  This is the "Hotel California + Community Awards" model.
""")


def main():
    """Run Perplexity comparison and UPs recycling analysis."""
    compare_revenue_models()
    print_ups_recycling_analysis()


if __name__ == "__main__":
    main()
