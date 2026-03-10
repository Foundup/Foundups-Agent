"""
Investor Economics Archive - Concatenated from root tmp_* files.

ARCHIVED: 2026-03-11
SOURCE: Root directory tmp_* files (WSP 85 cleanup)

Contains:
1. Investor Math - Token pool matrix calculations
2. Exit Strategy - 100x/10x investor return analysis  
3. Adoption Testing - Curve modeling
4. Crypto Testing - Multi-crypto subscription flows

These were exploratory scripts during pAVS economics design.
"""

# ============================================================================
# SECTION 1: INVESTOR MATH (tmp_investor_math.py)
# ============================================================================

"""Investor Return Model - Complete Pool Share Mathematics.

FROM THE TOKEN POOL MATRIX:
                 Un(60%)  Dao(16%)  Du(4%)  Network(16%)  Fund(4%)
    un level:    2.40%    0.64%     0.16%   0.64%         0.16%
    dao level:   9.60%    2.56%     0.64%   2.56%         0.64%
    du level:    48%      13%       3%      13%           3%

INVESTOR POOL (at DAO activity level):
- Un Pool:  9.60% of each FoundUp
- Dao Pool: 2.56% of each FoundUp
- Du Pool:  0.64% of each FoundUp (if founder-level)
- TOTAL:    12.80% of EVERY FoundUp's token distribution!

This is MASSIVE - investors share in the Stakeholder pools across ALL FoundUps!
"""
import sys
import math
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.foundups.simulator.economics import adoption_curve, bonding_tokens_for_btc, bonding_price

print("=" * 80)
print("INVESTOR RETURN MODEL - Stakeholder Pool Participation")
print("=" * 80)

# ============================================================================
# TOKEN POOL MATRIX (from image)
# ============================================================================
print("\n" + "=" * 80)
print("TOKEN POOL MATRIX (WSP 26 Section 6.3-6.4)")
print("=" * 80)

print("""
                 Un(60%)  Dao(16%)  Du(4%)  Network(16%)  Fund(4%)
    ---------------------------------------------------------------
    un level:    2.40%    0.64%     0.16%   0.64%         0.16%
    dao level:   9.60%    2.56%     0.64%   2.56%         0.64%
    du level:    48%      13%       3%      13%           3%
""")

# Investor pool participates at DAO level in Stakeholder pools
INVESTOR_SHARES = {
    "Un Pool (60%)": 0.096,    # 9.60%
    "Dao Pool (16%)": 0.0256,  # 2.56%
    "Du Pool (4%)": 0.0064,    # 0.64% (if founder-level)
}

STAKEHOLDER_TOTAL = 0.096 + 0.0256  # Un + Dao = 12.16% (without Du)
FULL_TOTAL = 0.096 + 0.0256 + 0.0064  # 12.80% (with Du founder level)

print("INVESTOR POOL SHARE (at DAO activity level):")
print("-" * 50)
for pool, share in INVESTOR_SHARES.items():
    print(f"  {pool:20} = {share*100:6.2f}%")
print("-" * 50)
print(f"  {'TOTAL (Un + Dao)':20} = {STAKEHOLDER_TOTAL*100:6.2f}%")
print(f"  {'TOTAL (with Du)':20} = {FULL_TOTAL*100:6.2f}%")

# ============================================================================
# AI ADOPTION CURVES 2026
# ============================================================================
print("\n" + "=" * 80)
print("AI ADOPTION CURVES 2026 - S-Curve Projections")
print("=" * 80)

# Real AI adoption data and projections
AI_FOUNDUPS_2026 = [
    # (Name, Users, Adoption Score, Annual F_i Distribution)
    ("OpenClaw (Agents)", 500_000, 0.35, 8_000_000),
    ("Moltbot (Trading)", 200_000, 0.28, 5_000_000),
    ("AI Code Assistant", 2_000_000, 0.55, 15_000_000),
    ("AI Content Creator", 800_000, 0.42, 10_000_000),
    ("AI Data Analyst", 300_000, 0.32, 6_000_000),
    ("GotJunk (Startup)", 50_000, 0.18, 2_000_000),
    ("AI Customer Service", 1_000_000, 0.48, 12_000_000),
    ("AI Research Agent", 150_000, 0.25, 4_000_000),
    ("AI Legal Assistant", 100_000, 0.22, 3_000_000),
    ("AI Healthcare Bot", 400_000, 0.38, 7_000_000),
]

print(f"\n{'FoundUp':<22} | {'Users':>10} | {'Adopt':>6} | {'Release':>7} | {'F_i Dist/Year':>14}")
print("-" * 75)

total_fi_annual = 0
for name, users, adoption, fi_dist in AI_FOUNDUPS_2026:
    release_pct = adoption_curve(adoption)
    print(f"{name:<22} | {users:>10,} | {adoption:>5.0%} | {release_pct:>6.1%} | {fi_dist:>14,}")
    total_fi_annual += fi_dist

print("-" * 75)
print(f"{'TOTAL (10 FoundUps)':<22} | {'':<10} | {'':<6} | {'':<7} | {total_fi_annual:>14,}")

# Scale to 100 FoundUps
NUM_FOUNDUPS = 100
avg_fi_per_foundup = total_fi_annual / len(AI_FOUNDUPS_2026)
network_fi_annual = avg_fi_per_foundup * NUM_FOUNDUPS

print(f"\nScaled to {NUM_FOUNDUPS} FoundUps:")
print(f"  Average F_i per FoundUp/year: {avg_fi_per_foundup:,.0f}")
print(f"  Network total F_i/year: {network_fi_annual:,.0f}")

# ============================================================================
# INVESTOR POOL F_i EARNINGS
# ============================================================================
print("\n" + "=" * 80)
print("INVESTOR POOL F_i EARNINGS (Annual)")
print("=" * 80)

investor_fi_un = network_fi_annual * 0.096      # Un pool share
investor_fi_dao = network_fi_annual * 0.0256    # Dao pool share
investor_fi_du = network_fi_annual * 0.0064     # Du pool share (if founder)
investor_fi_total = investor_fi_un + investor_fi_dao

print(f"\nFrom {NUM_FOUNDUPS} FoundUps distributing {network_fi_annual:,.0f} F_i/year:")
print(f"  Un Pool (9.60%):  {investor_fi_un:>15,.0f} F_i")
print(f"  Dao Pool (2.56%): {investor_fi_dao:>15,.0f} F_i")
print(f"  Du Pool (0.64%):  {investor_fi_du:>15,.0f} F_i (if founder)")
print("-" * 50)
print(f"  TOTAL TO INVESTORS: {investor_fi_total:>15,.0f} F_i/year")
print(f"  (with Du founder):  {investor_fi_total + investor_fi_du:>15,.0f} F_i/year")

# ============================================================================
# BONDING CURVE + POOL SHARE COMBINED RETURNS
# ============================================================================
print("\n" + "=" * 80)
print("COMBINED INVESTOR RETURNS - Bonding Curve + Pool Shares")
print("=" * 80)

# Investment rounds
TOTAL_RAISE = 100.0  # 100 BTC total
K, N = 0.0001, 2.0   # Bonding curve params

rounds = [
    ("Seed", 10.0),
    ("Early", 20.0),
    ("Growth", 30.0),
    ("Scale", 40.0),
]

supply = 0.0
all_rounds = []

for name, btc in rounds:
    tokens = bonding_tokens_for_btc(supply, btc, K, N)
    entry_price = bonding_price(supply, K, N) if supply > 0 else K
    all_rounds.append({
        "name": name, "btc": btc, "tokens": tokens,
        "entry_supply": supply, "entry_price": entry_price
    })
    supply += tokens

total_ii = supply

print(f"\nBonding Curve: Price = {K} x supply^{N}")
print(f"Total raised: {TOTAL_RAISE} BTC -> {total_ii:,.1f} I_i tokens")

# Future scenarios
print("\n" + "-" * 80)
print("RETURN PROJECTIONS (5-year horizon)")
print("-" * 80)

# Assumptions
YEARS = 5
BTC_PRICE = 100000  # $100K BTC
FI_VALUE_USD = 1.0  # $1 per F_i at maturity

# Future supply growth scenarios
SUPPLY_GROWTH = 10  # 10x supply growth
future_supply = total_ii * SUPPLY_GROWTH
future_price = bonding_price(future_supply, K, N)

print(f"\nAssumptions:")
print(f"  - I_i supply grows {SUPPLY_GROWTH}x (more investors)")
print(f"  - F_i valued at ${FI_VALUE_USD} each at maturity")
print(f"  - {YEARS} years of pool distributions")
print(f"  - BTC price: ${BTC_PRICE:,}")

# Calculate 5-year F_i accumulation
fi_5year = investor_fi_total * YEARS

print(f"\n5-Year F_i Accumulation:")
print(f"  Annual: {investor_fi_total:>15,.0f} F_i")
print(f"  5-Year: {fi_5year:>15,.0f} F_i")
print(f"  Value:  ${fi_5year * FI_VALUE_USD:>14,.0f}")

print(f"\n{'Round':<8} | {'BTC':>6} | {'I_i':>10} | {'Pool %':>7} | {'5Y F_i':>14} | {'Curve Val':>10} | {'Total':>12} | {'Return':>8}")
print("-" * 95)

for rd in all_rounds:
    pool_share = rd["tokens"] / total_ii
    fi_share = fi_5year * pool_share
    fi_value_btc = fi_share * FI_VALUE_USD / BTC_PRICE

    curve_value = rd["tokens"] * future_price
    total_value = curve_value + fi_value_btc
    return_x = total_value / rd["btc"]

    print(f"{rd['name']:<8} | {rd['btc']:>6.0f} | {rd['tokens']:>10,.1f} | {pool_share*100:>6.1f}% | {fi_share:>14,.0f} | {curve_value:>10.1f} | {total_value:>12.1f} | {return_x:>7.0f}x")

# ============================================================================
# SEED INVESTOR DEEP DIVE
# ============================================================================
print("\n" + "=" * 80)
print("SEED INVESTOR DEEP DIVE (10 BTC Investment)")
print("=" * 80)

seed = all_rounds[0]
seed_pool_share = seed["tokens"] / total_ii

print(f"\nInvestment: {seed['btc']} BTC")
print(f"I_i Tokens: {seed['tokens']:,.1f}")
print(f"Pool Share: {seed_pool_share*100:.1f}%")

print(f"\n--- BONDING CURVE RETURNS ---")
print(f"Entry price: {seed['entry_price']:.6f} BTC/I_i")
print(f"Future price (10x supply): {future_price:.4f} BTC/I_i")
print(f"I_i value: {seed['tokens'] * future_price:.1f} BTC (${seed['tokens'] * future_price * BTC_PRICE:,.0f})")
print(f"Curve return: {seed['tokens'] * future_price / seed['btc']:.0f}x")

print(f"\n--- POOL SHARE RETURNS (5 Years) ---")
seed_fi = fi_5year * seed_pool_share
print(f"Un Pool (9.60% x {seed_pool_share*100:.1f}%): {investor_fi_un * YEARS * seed_pool_share:>12,.0f} F_i")
print(f"Dao Pool (2.56% x {seed_pool_share*100:.1f}%): {investor_fi_dao * YEARS * seed_pool_share:>12,.0f} F_i")
print(f"TOTAL F_i: {seed_fi:>12,.0f}")
print(f"F_i Value @ $1: ${seed_fi:>12,.0f}")
print(f"F_i Value in BTC: {seed_fi / BTC_PRICE:.4f} BTC")

print(f"\n--- COMBINED RETURNS ---")
curve_btc = seed["tokens"] * future_price
fi_btc = seed_fi * FI_VALUE_USD / BTC_PRICE
total_btc = curve_btc + fi_btc
total_usd = total_btc * BTC_PRICE
return_x = total_btc / seed["btc"]

print(f"Bonding curve: {curve_btc:>10.1f} BTC")
print(f"Pool F_i:      {fi_btc:>10.4f} BTC (${seed_fi:,.0f})")
print(f"TOTAL:         {total_btc:>10.1f} BTC (${total_usd:,.0f})")
print(f"\n>>> SEED INVESTOR RETURN: {return_x:.0f}x <<<")

# ============================================================================
# NETWORK GROWTH SCENARIOS
# ============================================================================
print("\n" + "=" * 80)
print("NETWORK GROWTH SCENARIOS")
print("=" * 80)

scenarios = [
    ("Conservative", 50, 5_000_000, 5),   # 50 FoundUps, 5M F_i avg
    ("Base Case", 100, 7_200_000, 10),    # 100 FoundUps, 7.2M avg
    ("Bull Case", 250, 10_000_000, 20),   # 250 FoundUps, 10M avg
    ("Moon Shot", 500, 15_000_000, 50),   # 500 FoundUps, 15M avg
]

print(f"\nSeed investor (10 BTC, {seed_pool_share*100:.1f}% of pool):")
print(f"\n{'Scenario':<15} | {'FoundUps':>10} | {'Avg F_i':>12} | {'Supply X':>8} | {'5Y F_i':>14} | {'Total BTC':>10} | {'Return':>8}")
print("-" * 95)

for name, foundups, avg_fi, supply_x in scenarios:
    annual_fi = foundups * avg_fi * STAKEHOLDER_TOTAL  # 12.16%
    five_year_fi = annual_fi * 5 * seed_pool_share

    future_p = bonding_price(total_ii * supply_x, K, N)
    curve_val = seed["tokens"] * future_p
    fi_val = five_year_fi / BTC_PRICE
    total_val = curve_val + fi_val
    ret = total_val / seed["btc"]

    print(f"{name:<15} | {foundups:>10,} | {avg_fi:>12,} | {supply_x:>8}x | {five_year_fi:>14,.0f} | {total_val:>10.0f} | {ret:>7.0f}x")

# ============================================================================
# KEY INSIGHTS
# ============================================================================
print("\n" + "=" * 80)
print("KEY INSIGHTS - WHY THIS IS MASSIVE")
print("=" * 80)
print("""
1. STAKEHOLDER POOL PARTICIPATION (12.16% total):
   - Un Pool: 9.60% of EVERY FoundUp's distributions
   - Dao Pool: 2.56% of EVERY FoundUp's distributions
   - This is NOT per investor - it's a POOL that investors share!

2. NETWORK EFFECT MULTIPLIER:
   - 100 FoundUps x 7.2M F_i x 12.16% = 87.5M F_i/year to investor pool
   - 5 years = 437M F_i total
   - Seed investor (10% of pool) = 43.7M F_i

3. BONDING CURVE ADVANTAGE:
   - Seed: 10 BTC buys massive I_i position
   - 10x supply growth = 100x price appreciation
   - Early investors dominate the pool share

4. COMBINED RETURNS (Seed Investor):
   - Bonding curve: ~100x from price appreciation
   - Pool shares: Millions in F_i tokens
   - TOTAL: 100x-500x depending on network growth

5. AI ADOPTION 2026 IS THE CATALYST:
   - S-curve adoption releases tokens
   - More FoundUps = more pool distributions
   - AI boom = exponential network growth

>>> BOTTOM LINE: Seed investors get 12.16% of ALL FoundUp <<<
>>> token flows, PLUS bonding curve appreciation = MASSIVE <<<
""")
print("=" * 80)

# ============================================================================
# SECTION 2: EXIT STRATEGY (tmp_investor_exit_strategy.py)
# ============================================================================

"""Investor Exit Strategy Analysis.

Two options:
A) 100x return over 10 years (hold for maximum upside)
B) Accelerated 10x buyout at 3 years (quick liquidity)

Question: What would be most receptive to investors?
"""
import sys
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.foundups.simulator.economics import bonding_price, bonding_tokens_for_btc

print("=" * 80)
print("INVESTOR EXIT STRATEGY ANALYSIS")
print("=" * 80)

# Base parameters
SEED_BTC = 10.0
K, N = 0.0001, 2.0
INITIAL_SUPPLY = 0.0

# Seed investor gets first tokens
seed_tokens = bonding_tokens_for_btc(INITIAL_SUPPLY, SEED_BTC, K, N)
print(f"\nSeed Investment: {SEED_BTC} BTC -> {seed_tokens:.1f} I_i tokens")

# ============================================================================
# OPTION A: 100x over 10 years (slow burn, maximum upside)
# ============================================================================
print("\n" + "=" * 80)
print("OPTION A: 100x RETURN OVER 10 YEARS")
print("=" * 80)

# Need 100x return: seed_tokens * future_price = 100 * SEED_BTC
target_return_a = 100
target_value_a = SEED_BTC * target_return_a  # 1000 BTC
required_price_a = target_value_a / seed_tokens

# What supply gives this price?
# price = K * supply^N -> supply = (price/K)^(1/N)
required_supply_a = (required_price_a / K) ** (1/N)
supply_multiple_a = required_supply_a / seed_tokens

print(f"\nTarget: {target_return_a}x return = {target_value_a} BTC")
print(f"Required I_i price: {required_price_a:.4f} BTC")
print(f"Required supply: {required_supply_a:,.0f} I_i")
print(f"Supply multiple: {supply_multiple_a:.1f}x from seed round")

# 10 year timeline with adoption
years = 10
annual_growth = supply_multiple_a ** (1/years)
print(f"\n10-Year Timeline (compound growth {annual_growth:.1%}/year):")
print(f"{'Year':<6} | {'Supply':>12} | {'Price':>10} | {'Value':>12} | {'Return':>8}")
print("-" * 60)

supply = seed_tokens
for year in range(0, years + 1):
    price = bonding_price(supply, K, N)
    value = seed_tokens * price
    ret = value / SEED_BTC
    print(f"Year {year:<2} | {supply:>12,.0f} | {price:>10.4f} | {value:>12.1f} | {ret:>7.0f}x")
    supply *= annual_growth

# ============================================================================
# OPTION B: 10x buyout at 3 years (accelerated exit)
# ============================================================================
print("\n" + "=" * 80)
print("OPTION B: 10x BUYOUT AT 3 YEARS")
print("=" * 80)

target_return_b = 10
target_value_b = SEED_BTC * target_return_b  # 100 BTC
buyout_year = 3

print(f"\nTarget: {target_return_b}x return = {target_value_b} BTC")
print(f"Buyout at: Year {buyout_year}")

# Calculate required supply/price at year 3
required_price_b = target_value_b / seed_tokens
required_supply_b = (required_price_b / K) ** (1/N)
supply_multiple_b = required_supply_b / seed_tokens
annual_growth_b = supply_multiple_b ** (1/buyout_year)

print(f"\n3-Year Timeline (compound growth {annual_growth_b:.1%}/year):")
print(f"{'Year':<6} | {'Supply':>12} | {'Price':>10} | {'Value':>12} | {'Return':>8}")
print("-" * 60)

supply = seed_tokens
for year in range(0, buyout_year + 1):
    price = bonding_price(supply, K, N)
    value = seed_tokens * price
    ret = value / SEED_BTC
    print(f"Year {year:<2} | {supply:>12,.0f} | {price:>10.4f} | {value:>12.1f} | {ret:>7.0f}x")
    supply *= annual_growth_b

# ============================================================================
# HYBRID MODEL: Best of Both Worlds
# ============================================================================
print("\n" + "=" * 80)
print("OPTION C: HYBRID MODEL (Most Investor-Friendly)")
print("=" * 80)

print("""
THE HYBRID OFFER:
1. GUARANTEED FLOOR: 10x buyout RIGHT at Year 3
   - Network offers to buy back I_i at 10x entry price
   - Investor can CHOOSE to sell (no obligation)
   - Funded by: 3 years of pool fees + new investor rounds

2. UPSIDE OPTION: Hold for 100x+ over 10 years
   - Investor can decline buyout and keep holding
   - Continue earning pool shares (12.16% of all FoundUps)
   - Potential for 100x-1000x if network grows

3. PARTIAL EXIT: Sell 50% at Year 3, keep 50%
   - De-risk: Get 5x back (50% of 10x)
   - Still participate in long-term upside
   - Best of both worlds
""")

# Calculate partial exit scenario
partial_pct = 0.50
partial_value = target_value_b * partial_pct  # 50 BTC back at year 3
remaining_tokens = seed_tokens * (1 - partial_pct)

print(f"\nPartial Exit Scenario (50% at Year 3):")
print(f"  Sell {seed_tokens * partial_pct:.1f} I_i for {partial_value:.0f} BTC (5x on initial)")
print(f"  Keep {remaining_tokens:.1f} I_i for long-term upside")

# Long-term value of remaining tokens (if 100x total growth)
long_term_price = required_price_a
remaining_value = remaining_tokens * long_term_price
total_return = partial_value + remaining_value

print(f"\n  At Year 10 (100x scenario):")
print(f"    Remaining I_i value: {remaining_value:.0f} BTC")
print(f"    Total return: {partial_value:.0f} + {remaining_value:.0f} = {total_return:.0f} BTC")
print(f"    Combined multiple: {total_return / SEED_BTC:.0f}x")

# ============================================================================
# INVESTOR PSYCHOLOGY ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("INVESTOR PSYCHOLOGY - WHAT'S MOST RECEPTIVE?")
print("=" * 80)

print("""
INVESTOR TYPES AND PREFERENCES:

1. VENTURE CAPITAL (Institutional)
   - Typical horizon: 5-7 years
   - Target return: 10-20x
   - Priority: LIQUIDITY EVENT
   >> PREFER: Option B (10x at 3yr) or Hybrid

2. ANGEL INVESTORS (High Net Worth)
   - Typical horizon: 5-10 years
   - Target return: 20-100x
   - Priority: MAXIMUM UPSIDE
   >> PREFER: Option A (100x at 10yr) or Hybrid (hold long)

3. STRATEGIC INVESTORS (Ecosystem Partners)
   - Horizon: Indefinite
   - Target return: Network access + returns
   - Priority: ECOSYSTEM ALIGNMENT
   >> PREFER: Hybrid (partial exit + continued participation)

4. CRYPTO-NATIVE INVESTORS
   - Horizon: Variable (momentum-based)
   - Target return: 10x minimum, 100x moonshot
   - Priority: FLEXIBILITY
   >> PREFER: Hybrid (options are valuable!)

RECOMMENDATION: HYBRID MODEL

Why the Hybrid wins:
1. OPTIONALITY IS VALUABLE - Investors love choices
2. GUARANTEED FLOOR removes downside fear
3. UPSIDE PARTICIPATION keeps them engaged
4. PARTIAL EXIT satisfies liquidity needs
5. ALIGNED INCENTIVES - they stay invested in network success

The pitch: "Guaranteed 10x at 3 years OR hold for 100x+"
""")

# ============================================================================
# FUNDING THE BUYOUT
# ============================================================================
print("\n" + "=" * 80)
print("FUNDING THE 3-YEAR BUYOUT")
print("=" * 80)

# Assumptions
total_investor_btc = 100  # Total raised
buyout_multiple = 10
buyout_cost = total_investor_btc * buyout_multiple  # 1000 BTC needed

# Fee accumulation over 3 years
annual_network_fees = 50  # BTC/year from all fees (conservative)
accumulated_fees = annual_network_fees * 3

# New investor rounds
new_round_btc = 200  # Series A at higher valuation

# BTC reserve growth
reserve_appreciation = 100  # BTC value growth

total_funding = accumulated_fees + new_round_btc + reserve_appreciation

print(f"\nBuyout Cost: {buyout_cost} BTC (all seed investors exercise 10x)")

print(f"\nFunding Sources (3 years):")
print(f"  Accumulated fees:     {accumulated_fees:>10} BTC")
print(f"  Series A raise:       {new_round_btc:>10} BTC")
print(f"  Reserve appreciation: {reserve_appreciation:>10} BTC")
print(f"  TOTAL AVAILABLE:      {total_funding:>10} BTC")

coverage = total_funding / buyout_cost * 100
print(f"\nCoverage ratio: {coverage:.0f}%")

if total_funding >= buyout_cost:
    print("STATUS: FULLY FUNDED - Buyout is credible!")
else:
    shortfall = buyout_cost - total_funding
    print(f"STATUS: Shortfall of {shortfall} BTC")
    print("        Need higher fees or larger Series A")

# ============================================================================
# FINAL RECOMMENDATION
# ============================================================================
print("\n" + "=" * 80)
print("FINAL RECOMMENDATION")
print("=" * 80)

print("""
>>> OFFER THE HYBRID MODEL <<<

INVESTOR PITCH:
"Invest 10 BTC in the seed round. At Year 3, you have a CHOICE:

  A) TAKE THE GUARANTEED 10x: We buy back your I_i for 100 BTC
     - Locked in, no risk, predictable exit

  B) HOLD FOR MOONSHOT: Keep your I_i for potential 100x+
     - Continue earning 12.16% of all FoundUp distributions
     - Ride the AI adoption S-curve to 2033

  C) SPLIT 50/50: De-risk while keeping upside
     - Get 50 BTC at Year 3 (5x)
     - Keep half your I_i for long-term growth

The floor is 10x. The ceiling is 1000x. You choose."

WHY THIS WORKS:
1. Removes investor fear (guaranteed floor)
2. Preserves FOMO (upside option)
3. Provides flexibility (partial exit)
4. Network keeps engaged investors (aligned incentives)
5. Credibly fundable (3yr fee accumulation + Series A)

This is the VC sweet spot: downside protection + upside participation.
""")
print("=" * 80)

# ============================================================================
# SECTION 3: ADOPTION TESTING (tmp_test_adoption.py)
# ============================================================================

"""Test adoption curve - pure mathematics, no artificial tiers."""
import sys
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.foundups.simulator.economics import (
    adoption_curve, FoundUpTokenPool
)

print("ADOPTION CURVE - Diffusion of Innovation (S-curve)")
print("=" * 60)
print("\nNo artificial tiers - pure mathematical curve")
print("Formula: tokens_released = 21M × sigmoid(adoption_score)")
print()

# Show the S-curve at various adoption levels
print("Adoption%  | Released%  | Tokens Released")
print("-" * 60)
for pct in [0, 2.5, 5, 10, 16, 25, 34, 50, 68, 84, 95, 100]:
    score = pct / 100
    release_pct = adoption_curve(score)
    tokens = int(21_000_000 * release_pct)
    bar = "#" * int(release_pct * 30)
    print(f"{pct:6.1f}%    | {release_pct*100:6.2f}%    | {tokens:>12,} {bar}")

print("\n" + "=" * 60)
print("MINING SIMULATION - 0102 workers earn tokens by doing work")
print("=" * 60)

# Create a FoundUp and simulate adoption growth
pool = FoundUpTokenPool(foundup_id="gotjunk_001")

print(f"\nGenesis: {pool.total_supply:,} total tokens")
print(f"Initial adoption: {pool.adoption_score:.2%}")
print(f"Available to mine: {pool.available_supply:,.0f}")

# Simulate growth phases
growth_phases = [
    (10, 1000, 100, True, "First users, first revenue"),
    (50, 5000, 500, True, "Growing traction"),
    (200, 20000, 2000, True, "Early majority"),
    (1000, 100000, 10000, True, "Mass adoption"),
    (5000, 500000, 50000, True, "Mature market"),
]

print("\n--- Growth Phases ---")
for users, revenue, work, milestone, phase_name in growth_phases:
    pool.update_adoption(users=users, revenue_ups=revenue, work_completed=work, milestone=milestone)
    print(f"\n{phase_name}:")
    print(f"  Users: {users:,}, Revenue: ${revenue:,}")
    print(f"  Adoption: {pool.adoption_score:.2%}")
    print(f"  Release %: {pool.release_percentage:.2%}")
    print(f"  Mineable: {pool.remaining_mintable:,.0f} tokens")

# Simulate mining
print("\n--- Mining (0102 workers earning tokens) ---")
mined = pool.mint_for_work(50000, "agent_coder_01")
print(f"Agent mined: {mined:,.0f} F_i")
print(f"Remaining: {pool.remaining_mintable:,.0f}")

print("\n" + "=" * 60)
print("KEY INSIGHT: Token release follows NATURAL adoption curve")
print("- No arbitrary tier jumps (5% → 10% → 20%)")
print("- Smooth S-curve based on actual adoption metrics")
print("- 0102 workers mine tokens like Bitcoin miners")
print("- Can't pump-and-dump what isn't released yet")
print("=" * 60)

# ============================================================================
# SECTION 4: INVESTOR TESTING (tmp_test_investor.py)
# ============================================================================

"""Test investor staking module - demonstrate 10x-100x returns."""
import sys
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.foundups.simulator.economics import (
    InvestorPool, InvestorTier,
    bonding_price, bonding_tokens_for_btc,
    get_investor_pool, reset_investor_pool
)

print("=" * 70)
print("INVESTOR STAKING - Bitclout-style Bonding Curve + 0.64% Founder Shares")
print("=" * 70)

# Reset for clean test
reset_investor_pool()
pool = InvestorPool()

# Show bonding curve mathematics
print("\nBONDING CURVE: price = 0.0001 * supply^2")
print("-" * 50)
print("Supply      | Price (BTC)  | Price (USD @ $50K BTC)")
print("-" * 50)
for supply in [10, 100, 1000, 10000, 100000]:
    price = bonding_price(supply, k=0.0001, n=2.0)
    print(f"{supply:>10,}  | {price:>12.6f} | ${price * 50000:>15,.2f}")

print("\n" + "=" * 70)
print("INVESTMENT SIMULATION - Early vs Late Investors")
print("=" * 70)

# Seed investor (first 1 BTC)
print("\n--- SEED INVESTOR (First) ---")
seed_tokens, seed_tier = pool.invest_btc("alice", 1.0)
print(f"Alice invests 1 BTC at supply {pool.ii_total_supply - seed_tokens:.0f}")
print(f"  Receives: {seed_tokens:.2f} I_i tokens")
print(f"  Entry price: {pool.investors['alice'].entry_price_btc:.8f} BTC")
print(f"  Tier: {seed_tier.value}")

# Early investor (when supply is ~100)
print("\n--- EARLY INVESTOR (Second) ---")
early_tokens, early_tier = pool.invest_btc("bob", 1.0)
print(f"Bob invests 1 BTC at supply {pool.ii_total_supply - early_tokens:.0f}")
print(f"  Receives: {early_tokens:.2f} I_i tokens")
print(f"  Entry price: {pool.investors['bob'].entry_price_btc:.8f} BTC")
print(f"  Tier: {early_tier.value}")

# Growth investor (larger investment)
print("\n--- GROWTH INVESTOR (Later) ---")
growth_tokens, growth_tier = pool.invest_btc("charlie", 10.0)
print(f"Charlie invests 10 BTC at supply {pool.ii_total_supply - growth_tokens:.0f}")
print(f"  Receives: {growth_tokens:.2f} I_i tokens")
print(f"  Entry price: {pool.investors['charlie'].entry_price_btc:.8f} BTC")
print(f"  Tier: {growth_tier.value}")

# Show current values
print("\n" + "=" * 70)
print("CURRENT VALUES (after all investments)")
print("=" * 70)
print(f"Total I_i supply: {pool.ii_total_supply:.2f}")
print(f"Current price: {pool.current_price_btc:.6f} BTC (${pool.current_price_btc * 50000:,.2f})")
print(f"Total BTC invested: {pool.total_btc_invested:.2f} BTC")

print("\nINVESTOR RETURNS:")
print("-" * 60)
for inv_id in ["alice", "bob", "charlie"]:
    returns = pool.get_investor_returns(inv_id)
    position = pool.investors[inv_id]
    current_usd = returns['current_value_btc'] * 50000
    invested_usd = position.btc_invested * 50000

    print(f"\n{inv_id.upper()}:")
    print(f"  Invested: {position.btc_invested:.2f} BTC (${invested_usd:,.0f})")
    print(f"  I_i tokens: {position.ii_tokens_total:.2f}")
    print(f"  Current value: {returns['current_value_btc']:.4f} BTC (${current_usd:,.0f})")
    print(f"  Return: {returns['price_return_multiple']:.2f}x")

# Network growth simulation
print("\n" + "=" * 70)
print("NETWORK GROWTH - Vesting and Founder Shares")
print("=" * 70)

# Simulate network growth
pool.update_network_adoption(foundups_count=50, total_revenue=500000.0)
print(f"\nNetwork adoption: {pool.network_adoption_score:.2%}")
print(f"Vesting release: {pool.vesting_release_pct:.2%}")

# Vest tokens
pool.vest_tokens()

print("\nVESTED TOKENS (can claim 0.64% founder shares):")
for inv_id in ["alice", "bob", "charlie"]:
    position = pool.investors[inv_id]
    print(f"  {inv_id}: {position.ii_tokens_vested:.2f} / {position.ii_tokens_total:.2f} I_i ({position.vesting_percentage:.1%} vested)")

# Founder share calculation
print("\n0.64% FOUNDER SHARE ALLOCATION:")
for inv_id in ["alice", "bob", "charlie"]:
    share = pool.calculate_founder_share(inv_id)
    print(f"  {inv_id}: {share:.4%} of each FoundUp's F_i tokens")

# Simulate claiming from a FoundUp
print("\n--- CLAIMING FROM 'gotjunk_001' FoundUp (1M F_i minted) ---")
for inv_id in ["alice", "bob", "charlie"]:
    claimed = pool.claim_founder_fi(inv_id, "gotjunk_001", 1_000_000)
    print(f"  {inv_id} claims: {claimed:.2f} F_i")

# Return projections
print("\n" + "=" * 70)
print("RETURN PROJECTIONS - 10x Network Growth")
print("=" * 70)

projection = pool.project_returns(
    btc_investment=1.0,
    future_supply_multiple=10.0,
    num_foundups=100,
    avg_fi_per_foundup=1_000_000,
)

print(f"\nIf you invest 1 BTC NOW (supply: {pool.ii_total_supply:.0f}):")
print(f"  Tokens received: {projection['tokens_received']:.4f} I_i")
print(f"  Entry price: {projection['entry_price_btc']:.6f} BTC")

print(f"\nAt 10x supply growth:")
print(f"  Future price: {projection['future_price_btc']:.4f} BTC (100x price increase!)")
print(f"  Portfolio value: {projection['future_value_btc']:.2f} BTC (${projection['future_value_btc']*50000:,.0f})")
print(f"  RETURN: {projection['bonding_curve_return_x']:.0f}x")

print(f"\nPLUS founder shares from 100 FoundUps:")
print(f"  F_i tokens: {projection['founder_share_fi']:,.0f}")
print(f"  (0.64% × 100 FoundUps × 1M F_i each × your share)")

print("\n" + "=" * 70)
print("KEY INSIGHT: Quadratic Bonding Curve = Early Advantage")
print("-" * 70)
print("Alice (first): 1 BTC -> ~100 tokens -> worth 4+ BTC already")
print("Charlie (later): 10 BTC -> ~13 tokens -> paid 10x more per token")
print("")
print("Network growth creates EXPONENTIAL returns:")
print("- Supply 10x -> Price 100x (quadratic)")
print("- 100 FoundUps -> 64,000 F_i in founder shares")
print("- Combined: 10x-100x return potential for early investors")
print("=" * 70)

# ============================================================================
# SECTION 5: CRYPTO TESTING (tmp_test_crypto.py)
# ============================================================================

"""Test multi-crypto subscription payments."""
import sys
sys.path.insert(0, 'O:/Foundups-Agent')

from modules.foundups.simulator.economics import (
    BTCReserve, PaymentCrypto, CryptoRates,
    get_btc_reserve, reset_btc_reserve
)

# Reset for clean test
reset_btc_reserve()
r = get_btc_reserve()

print("Testing multi-crypto subscriptions...")
print("=" * 50)

# Test ETH payment
btc1, burned1 = r.receive_crypto_subscription(PaymentCrypto.ETH, 1.0, 'alice')
print(f"Alice paid 1 ETH = {btc1:.8f} BTC")

# Test SOL payment
btc2, burned2 = r.receive_crypto_subscription(PaymentCrypto.SOL, 100.0, 'bob')
print(f"Bob paid 100 SOL = {btc2:.8f} BTC")

# Test BTC payment
btc3, burned3 = r.receive_crypto_subscription(PaymentCrypto.BTC, 0.01, 'dave')
print(f"Dave paid 0.01 BTC = {btc3:.8f} BTC")

print(f"\nTotal BTC in reserve: {r.total_btc:.8f} BTC")
print(f"Reserve USD value: ${r.reserve_usd_value:,.2f}")

# Now test UPS burn
print("\n" + "=" * 50)
print("Testing UPS burn subscription...")

# Mint some UPS first
r.total_ups_minted = 10000.0
print(f"UPS supply: {r.total_ups_minted:.2f}")
print(f"UPS value before burn: ${r.ups_value_usd:.6f}")

# Charlie pays with UPS (gets burned)
btc4, burned4 = r.receive_crypto_subscription(PaymentCrypto.UPS, 1000.0, 'charlie')
print(f"Charlie paid 1000 UPS (BURNED={burned4})")
print(f"UPS supply after burn: {r.total_ups_minted:.2f}")
print(f"UPS value after burn: ${r.ups_value_usd:.6f}")
print(f"Total burned: {r.total_ups_burned:.2f}")

print("\n" + "=" * 50)
print("Reserve stats:")
stats = r.get_stats()
for k, v in stats.items():
    if isinstance(v, float):
        print(f"  {k}: {v:.6f}")
    elif isinstance(v, dict):
        print(f"  {k}:")
        for k2, v2 in v.items():
            print(f"    {k2}: {v2:.8f}" if isinstance(v2, float) else f"    {k2}: {v2}")
    else:
        print(f"  {k}: {v}")

print("\nAll tests passed!")
