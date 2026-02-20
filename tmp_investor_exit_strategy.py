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
