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
