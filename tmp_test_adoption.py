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
