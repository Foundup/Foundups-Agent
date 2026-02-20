# F_i Exit Scenarios Analysis

**Date**: 2026-02-17
**Status**: ACTIVE DESIGN - Requires 012 Decision
**Related**: WSP 26 Section 14, token_economics.py, dynamic_exit_friction.py

---

## 1. The Problem Statement

Three ways to acquire F_i, but exit fees create arbitrage:

| Acquisition | Entry Fee | Current Exit Fee | Path |
|-------------|-----------|------------------|------|
| MINE (work) | 0% | 11% | Agent earns |
| STAKE (invest) | 3% | 5% | Human stakes UPS |
| BUY (DEX) | 2% | ??? | Agent buys from seller |

**The Arbitrage Problem:**
```
Miner Direct:  F_i → Convert(11%) → UPS → BTC(7%) = 17.2% total
Miner via DEX: F_i → DEX(2%) → UPS → BTC(7%) = 8.9% total

Rational miners ALWAYS use DEX. The 11% fee is bypassed.
```

---

## 2. Dialectic Analysis

### THESIS: Differentiated Fees by Source
- MINED F_i penalized (11%) because it's "free money" from work
- STAKED F_i protected (5%) because it's returning capital
- Rationale: Discourage extraction of earned value

### ANTITHESIS: The DEX Bypass
- DEX enables fee arbitrage
- Miners sell on DEX (2%) instead of converting (11%)
- The differentiation becomes meaningless
- Creates two classes: sophisticated (use DEX) vs naive (direct convert)

### SYNTHESIS: Need a Unified Model
Options explored below...

---

## 3. Five Candidate Models

### MODEL A: Fee on Creation (Not Exit)

```
EARNING:
  Agent work → 89 F_i minted (11% fee at creation)

STAKING:
  UPS stake → 97 F_i minted (3% fee at creation)

EXIT (all F_i now fungible):
  F_i → UPS = 5% (universal)
  DEX trade = 2%
  UPS → BTC = 7%
```

**Pros:**
- No arbitrage possible
- F_i is truly fungible
- Simple mental model

**Cons:**
- Miners see lower headline earnings
- Changes economic feel ("I earned 100 but got 89")

### MODEL B: Exit Fee Applies at DEX Sell

```
DEX SELL (to UPS):
  MINED F_i → DEX → UPS = 11% + 2% = 13%
  STAKED F_i → DEX → UPS = 5% + 2% = 7%

DEX SWAP (F_i to F_i):
  Any F_i → DEX → different F_i = 2% only
```

**Pros:**
- No arbitrage for extraction
- F_i↔F_i trading stays cheap (2%)
- Maintains MINED/STAKED distinction

**Cons:**
- Complex implementation (track F_i type through DEX)
- What type does buyer receive?

### MODEL C: Vesting-Only (No Type Distinction)

```
ALL F_i is fungible. Exit fee based ONLY on hold duration:

< 1 year:   20% exit
1-2 years:  15% exit
2-4 years:  10% exit
4-8 years:   5% exit
8+ years:    2% exit (floor)
```

**Pros:**
- Dead simple
- Rewards loyalty regardless of source
- No arbitrage (fee is personal, not token-based)
- Aligns incentives: hold longer = lower cost

**Cons:**
- Miners who worked hard pay same as stakers
- Tracking per-user hold duration complex

### MODEL D: Hybrid (Type + Vesting)

```
BASE FEE by type:
  MINED: 11%
  STAKED: 5%
  BOUGHT: 8% (middle ground)

VESTING DISCOUNT (applies to all):
  1-2yr: -10%
  2-4yr: -25%
  4-8yr: -40%
  8+yr:  -50%

EXAMPLE - Miner holds 8 years:
  11% base × 50% discount = 5.5% exit
```

**Pros:**
- Maintains type distinction
- Still rewards long-term holders
- BOUGHT F_i has clear fee (8%)

**Cons:**
- Complex
- Still has DEX arbitrage unless MODEL B applied

### MODEL E: Protocol Fee + Market Dynamics

```
UNIVERSAL EXIT:
  All F_i → UPS = 5% protocol fee (fixed)

DEX DYNAMICS:
  Market sets F_i price
  If many want to exit → F_i price drops
  Natural economic pressure replaces artificial fees

MINED SCARCITY:
  Instead of 11% fee, MINED F_i has slower release curve
  Same total earned, but over longer period
```

**Pros:**
- Market-driven, not rule-driven
- Simple protocol fee
- Scarcity creates natural holding incentive

**Cons:**
- Less predictable
- Protocol captures less fee revenue
- Requires sophisticated DEX

---

## 4. Game Theory Analysis

### Players & Incentives

| Player | Wants | Optimal Model |
|--------|-------|---------------|
| Miner | Low exit cost | E (market) or C (vesting) |
| Staker | Capital preservation | A (creation fee) or C |
| Trader | Liquidity, low fees | E (market) or C |
| Protocol | Max BTC reserve | B (DEX includes exit) |
| FoundUp | Long-term holders | C (vesting) or D (hybrid) |

### Scenario: Mass Exit Event

**MODEL A (creation fee):**
- All F_i fungible, 5% exit
- Mass exit = 5% captured
- Predictable

**MODEL B (DEX includes exit):**
- Mass exit via DEX = 11% + 2% = 13%
- High capture but may discourage DEX use
- Pushes traders to OTC

**MODEL C (vesting only):**
- Early holders (8yr): 2% exit
- New holders: 20% exit
- Early builders protected, new entrants pay more

**MODEL E (market):**
- Mass exit crashes F_i price
- Protocol captures 5%
- Market punishes panic sellers naturally

---

## 5. First Principles: What Are We Optimizing For?

### Hotel California Principle
> BTC flows IN, never OUT (or costs to exit)

**Implication:** Higher exit fees = stronger reserve
**Best models:** B, D

### Reward Long-Term Builders
> Those who build should benefit most

**Implication:** Vesting discounts essential
**Best models:** C, D

### Fungible Tokens for Liquidity
> F_i should trade freely without type-baggage

**Implication:** Creation-time fee, not exit-time
**Best models:** A, E

### No Arbitrage
> Sophisticated users shouldn't have unfair advantage

**Implication:** DEX must include exit fee OR creation fee
**Best models:** A, B

---

## 6. Recommended Model: HYBRID A+C

**CREATION-TIME FEE (Model A) + VESTING DISCOUNT (Model C)**

```python
# At F_i creation
CREATION_FEES = {
    "mined": 0.11,    # Agent earns 89 F_i per 100 work
    "staked": 0.03,   # Human gets 97 F_i per 100 UPS
    "bought": 0.00,   # DEX buyer pays market price only
}

# All F_i now fungible
# Exit fee based on YOUR holding duration
VESTING_EXIT_FEES = {
    "< 1 year": 0.15,
    "1-2 years": 0.10,
    "2-4 years": 0.07,
    "4-8 years": 0.04,
    "8+ years": 0.02,
}

# DEX trading (F_i ↔ F_i or F_i ↔ UPS)
DEX_FEE = 0.02  # Always 2%

# Final exit to BTC
CASHOUT_FEE = 0.07  # 7% to leave system
```

**Example Scenarios:**

```
MINER - Work and Exit Immediately:
  Work 100 → 89 F_i (11% creation fee)
  89 F_i → DEX → 87.2 UPS (2% DEX)
  87.2 UPS → 74.1 UPS (15% vesting - held < 1yr)
  74.1 UPS → 68.9 BTC (7% cashout)
  TOTAL COST: 31.1%

MINER - Work and Hold 8 Years:
  Work 100 → 89 F_i (11% creation fee)
  89 F_i → 87.2 UPS (2% convert or DEX)
  87.2 UPS → 85.5 UPS (2% vesting - held 8yr)
  85.5 UPS → 79.5 BTC (7% cashout)
  TOTAL COST: 20.5%

STAKER - Stake and Exit After 4 Years:
  Stake 100 UPS → 97 F_i (3% creation fee)
  97 F_i → 95.1 UPS (2% DEX)
  95.1 UPS → 91.3 UPS (4% vesting)
  91.3 UPS → 84.9 BTC (7% cashout)
  TOTAL COST: 15.1%

TRADER - Buy on DEX, Sell on DEX:
  Buy 100 F_i (market price + 2% DEX)
  Sell 100 F_i (2% DEX)
  TOTAL COST: 4% (stays in system)
```

---

## 7. Simulation Parameters

To add to simulator:

```python
@dataclass
class ExitScenarioConfig:
    """Configuration for F_i exit scenario simulation."""

    # Model selection
    model: str  # "current", "creation_fee", "vesting_only", "hybrid"

    # Creation fees
    mined_creation_fee: float = 0.11
    staked_creation_fee: float = 0.03

    # Exit fees (if not using creation model)
    mined_exit_fee: float = 0.11
    staked_exit_fee: float = 0.05
    bought_exit_fee: float = 0.08

    # Vesting schedule
    vesting_tiers: Dict[str, float] = field(default_factory=lambda: {
        "0-1yr": 0.15,
        "1-2yr": 0.10,
        "2-4yr": 0.07,
        "4-8yr": 0.04,
        "8+yr": 0.02,
    })

    # DEX and cashout
    dex_fee: float = 0.02
    cashout_fee: float = 0.07


SCENARIOS_TO_TEST = [
    # Mass exit after 1 year
    {"name": "mass_exit_1yr", "exit_pct": 0.5, "hold_years": 1},

    # Gradual exit over 8 years
    {"name": "gradual_8yr", "exit_pct": 0.1, "hold_years": 8},

    # Miner dumps immediately
    {"name": "miner_dump", "exit_pct": 1.0, "hold_years": 0.1},

    # Staker panic exit
    {"name": "staker_panic", "exit_pct": 0.8, "hold_years": 0.5},

    # DEX arbitrage attempt
    {"name": "dex_arb", "path": "dex", "hold_years": 0.1},
]
```

---

## 8. Questions for 012

1. **Creation fee vs Exit fee?**
   - Creation: Miner sees "earned 89" (psychologically less)
   - Exit: Miner sees "earned 100, paid 11 to exit" (feels like tax)

2. **Should BOUGHT F_i have a fee?**
   - Yes: Prevents wash trading, captures more for reserve
   - No: Encourages DEX liquidity, simpler

3. **Vesting minimum floor?**
   - 2% proposed (8+ years)
   - Could be 0% for true long-term builders

4. **Should FoundUp tier affect exit?**
   - Current: F0=30%, F5=5%
   - Proposed: Remove, use vesting only
   - Or: Stack tier + vesting

---

## 9. Next Steps

1. [ ] 012 decides on model (A, B, C, D, E, or Hybrid)
2. [ ] Implement scenario simulator
3. [ ] Run Monte Carlo on 1000 agents
4. [ ] Measure: BTC reserve capture, exit patterns, DEX volume
5. [ ] Tune parameters based on results
6. [ ] Update WSP 26 with final model

---

## 10. Appendix: Full Fee Matrix

| Action | Current | Model A | Model C | Hybrid A+C |
|--------|---------|---------|---------|------------|
| MINE F_i | 0% | 11% | 0% | 11% |
| STAKE F_i | 3% | 3% | 3% | 3% |
| BUY F_i (DEX) | 2% | 2% | 2% | 2% |
| MINED exit | 11% | 5%* | 2-15%† | 2-15%† |
| STAKED exit | 5% | 5%* | 2-15%† | 2-15%† |
| BOUGHT exit | ???‡ | 5%* | 2-15%† | 2-15%† |
| DEX trade | 2% | 2% | 2% | 2% |
| UPS → BTC | 7% | 7% | 7% | 7% |

\* All F_i fungible after creation fee
† Based on vesting duration
‡ Currently undefined - this is the problem

---

## 11. Dynamic Fee Taper (Float System)

**Added**: 2026-02-17 (012 Request)

As treasury/reserve builds, fees automatically taper down. Self-regulating system.

### Reserve Health Ratio

```
reserve_ratio = btc_reserve / (total_fi_released * target_btc_per_fi)
```

### Fee Multiplier Curve (Sigmoid)

| Reserve Health | Fee Multiplier | Effective Exit (base 15%) |
|----------------|----------------|---------------------------|
| 0% (CRITICAL) | 1.93x | 29.0% |
| 10% (CRITICAL) | 1.86x | 27.9% |
| 20% (BUILDING) | 1.71x | 25.7% |
| 40% (HEALTHY) | 1.15x | 17.2% |
| 60% (STRONG) | 0.59x | 8.8% |
| 80% (ROBUST) | 0.37x | 5.5% |
| 100%+ | 0.31x | 4.7% |

### Implementation

```python
from dynamic_fee_taper import DynamicFeeTaper, HybridDynamicFees

# Initialize with target backing ratio
taper = DynamicFeeTaper(target_btc_per_fi=0.00001)

# Calculate effective fee
result = taper.calculate_effective_fee(
    base_fee=0.15,
    btc_reserve=0.5,
    total_fi_released=10_000_000,
)

print(f"Health: {result.health_status}")  # "STRONG"
print(f"Multiplier: {result.fee_multiplier:.2f}x")  # 0.59x
print(f"Effective Fee: {result.effective_fee:.1%}")  # 8.8%
```

### Combined Model: Hybrid + Dynamic Taper

```python
# Full model combining:
# 1. Creation fees (MINED 11%, STAKED 3%)
# 2. Vesting schedule (0-1yr → 8+yr)
# 3. Dynamic taper (based on reserve health)

model = HybridDynamicFees()

effective_fee, result = model.calculate_exit_fee(
    vesting_tier="4-8yr",  # Long-term holder
    btc_reserve=0.5,       # Strong reserve
    total_fi_released=10_000_000,
)

# Result: ~3-4% effective exit fee (rewarded for loyalty + strong reserve)
```

### Files

- `dynamic_fee_taper.py` - Core taper engine
- `exit_scenario_sim.py` - Monte Carlo simulation
- `FI_EXIT_SCENARIOS.md` - This document

### WSP References

- WSP 26 Section 14: Dynamic Exit Friction
- WSP 26 Section 7: BTC Reserve Model
- WSP 29: CABR Engine (reserve health affects CABR)

---

## 12. Simulation Results Summary

**Protocol Capture by Model** (from exit_scenario_sim.py):

| Model | Normal | Miner Dump | Long-Term | DEX Arb | **Average** |
|-------|--------|------------|-----------|---------|-------------|
| current | 14.4% | 17.8% | 13.5% | 17.6% | 15.8% |
| creation_fee | 17.8% | 21.6% | 16.3% | 19.8% | 18.9% |
| vesting_only | 18.3% | 21.8% | 17.0% | 23.0% | 20.0% |
| **hybrid** | **20.9%** | **25.7%** | **19.1%** | **23.9%** | **22.4%** |

**Recommendation**: HYBRID model with dynamic taper

- Captures 22.4% average for BTC reserve
- Protects against miner dumps (25.7% capture)
- Rewards long-term holders (lower effective fees)
- Self-regulating (fees drop as reserve strengthens)

---

## 13. 012 Decision Points

1. [x] **Model Selection**: HYBRID (creation fee + vesting)
2. [x] **Dynamic Taper**: Yes, float system based on reserve health
3. [x] **Target Reserve Ratio**: 0.000001 BTC per F_i (1 sat per 1,000 F_i)
4. [x] **Taper Curve**: Sigmoid (matches S-curve token release)
5. [x] **Floor Fee**: Minimum 2% even at 100% reserve

---

## 14. Staked F_i Pre-Backing (012-Confirmed 2026-02-17)

**Insight**: When UPS (backed by BTC) is staked into F_i, that F_i inherits backing.

```
UPS Staking Flow:
  UPS (BTC-backed) → Stake into FoundUp → F_i tokens (inherit backing)

  STAKED F_i: Already backed → doesn't need reserve coverage
  MINED F_i: Not backed → needs exit fee capture for reserve
```

**Model Update**: `ReserveHealth.fi_needing_backing` returns only `mined_fi`, not `total_fi`.

**Fee Implications**:
```
All mined (100%):  Reserve health = BTC / (mined_fi × target)
50% staked:        Reserve health doubles (same BTC, half target)
80% staked:        Reserve health 5x → OVERFLOW → drips to Network
```

**Example** (5 BTC reserve, 10M total F_i):
| Staked % | Mined F_i | Target BTC | Reserve Health | Exit Fee |
|----------|-----------|------------|----------------|----------|
| 0% | 10M | 10.0 | 50% STRONG | 12.4% |
| 50% | 5M | 5.0 | 100% OVERFLOW | 4.7% |
| 80% | 2M | 2.0 | 250% OVERFLOW | 4.5% |

---

## 15. Fractal Treasury Model (012-Confirmed 2026-02-17)

**Insight**: F_0 is the pAVS template that **DUPES** into every F_i.

```
F_0 = pAVS Template (blueprint, instance #0)
F_i = F_0.clone() → every FoundUp gets FULL pAVS machinery

F_0 is NOT special - just the first instance.
ALL F_i have SAME: treasury, fees, overflow, paywall capability.
```

**Template (F_0) duped into every F_i**:
```
F_i ──┬── paywalls/subs ──→ F_i Treasury (BTC)
      ├── staking ────────→ F_i Reserve (pre-backed)
      ├── exit fees ──────→ F_i Reserve (mined backing)
      └── overflow ───────→ Network Pool (shared ecosystem)
```

**Implementation**: `FractalTreasuryManager` in dynamic_fee_taper.py

**Per-FoundUp Reserve Tracking**:
```python
@dataclass
class FoundUpReserve:
    foundup_id: str       # F_0, F_1, F_2, ...
    btc_reserve: float    # F_i's BTC treasury
    staked_fi: float      # Pre-backed F_i
    mined_fi: float       # Needs backing
    paywall_revenue: float  # BTC from F_i's paywalls
```

**Network Health States**:
- `NETWORK_STRESSED`: >50% of F_i in CRITICAL
- `NETWORK_BALANCED`: Mixed health states
- `NETWORK_THRIVING`: >50% of F_i in OVERFLOW

**Example** (3 FoundUps):
| FoundUp | Reserve | Mined F_i | Health | Exit Fee | Overflow |
|---------|---------|-----------|--------|----------|----------|
| F_0 | 10 BTC | 5M | OVERFLOW | 4.5% | 5.0 BTC |
| F_1 | 5 BTC | 1M | OVERFLOW | 4.5% | 4.5 BTC |
| F_2 | 0.1 BTC | 500K | BUILDING | 25.7% | 0 |

Network Pool receives: 0.095 BTC/epoch (1% of overflow from F_0 + F_1)

---

## 16. SmartDAO Spawning Economics (012-Confirmed 2026-02-17)

**Insight**: F_i that gains traction → SmartDAO → uses overflow to spawn Tier 2 FoundUps.

```
F_i (F0_DAE) ──growth──► F_i (F1_EARLY) ──growth──► F_i (F2_GROWTH)
      │                        │                         │
      └── overflow ───────────►└── overflow ────────────►└── overflow
              │                        │                         │
              ▼                        ▼                         ▼
        Network Pool           Spawn Fund (20%)          Spawn Fund (20%)
                                     │                         │
                                     ▼                         ▼
                               Spawn F_j (Tier 1)        Spawn F_k (Tier 2)
```

**SmartDAO Reserve Split**:
```python
SMARTDAO_RESERVE_SPLIT = {
    "operations": 0.80,     # 80% for own operations
    "spawning_fund": 0.20,  # 20% for spawning new F_0s
}
```

**Tier Escalation Thresholds**:
| Tier | Adoption | Treasury (UPS) | Agents |
|------|----------|----------------|--------|
| F0_DAE | 0% | 0 | 0 |
| F1_EARLY | 16% | 100K | 10 |
| F2_GROWTH | 34% | 1M | 50 |
| F3_INFRA | 50% | 10M | 200 |
| F4_MEGA | 84% | 100M | 1,000 |
| F5_SYSTEMIC | 95% | 1B | 10,000 |

**Spawning Thresholds** (UPS in spawn fund to create new F_0):
| Parent Tier | Required | Seed to Child |
|-------------|----------|---------------|
| F1_EARLY | 10K | 1K |
| F2_GROWTH | 50K | 5K |
| F3_INFRA | 200K | 20K |
| F4_MEGA | 1M | 100K |
| F5_SYSTEMIC | 5M | 500K |

**Implementation**: `smartdao_spawning.py`

**Integration with Overflow**:
- F_0 (not SmartDAO): All overflow → Network Pool
- F_1+ (SmartDAO): Overflow split 80/20 (operations/spawning)
- Spawning fund accumulates → threshold → spawn new F_0

**Example Run** (F_0 → F_1 → spawns 12 children):
```
F_0 (F1_EARLY) [spawn_fund: 32,324 UPS]
  F_1 (F0_DAE)  ← Spawn Generation 1
  F_2 (F0_DAE)
  F_3 (F0_DAE)
  ...
  F_12 (F0_DAE)
```

---

*Document updated from 012-0102 dialectic session 2026-02-17*
*Files: FI_EXIT_SCENARIOS.md, exit_scenario_sim.py, dynamic_fee_taper.py, smartdao_spawning.py*
*012-Confirmed: Target ratio, Sigmoid curve, Floor fee, Overflow, Pre-backing, Fractal treasury, SmartDAO spawning*
