# FoundUps Tokenomics: Complete Economic Model

**Version**: 2.0.0
**Date**: 2026-02-14
**Status**: Architecture Complete, Simulator Operational
**Canonical Spec**: [WSP 26: FoundUPS DAE Tokenization](../../../WSP_knowledge/src/WSP_26_FoundUPS_DAE_Tokenization.md)
**Implementation**: [`modules/foundups/simulator/economics/`](../../../modules/foundups/simulator/economics/__init__.py)

## Executive Summary

FoundUps tokenomics implements a **bio-decay economic model** where:
1. **UP$ (Universal Participation)** = Inflationary consumption token across ALL FoundUps
2. **FoundUp Tokens** (e.g., JUNK$) = Deflationary 21M-capped asset tokens per FoundUp
3. **CABR Validation** = Only source of UP$ minting (prevents gaming)
4. **Bio-Decay States** = ICE/LIQUID/VAPOR (water analogy for intuitive UX)
5. **BTC Reserve** = Hotel California model (BTC flows in, never out)

**Result**: Self-sustaining economy where **active participation = value creation**, and **inactivity = value redistribution**.

---

## Table of Contents

1. [Two-Token Architecture](#two-token-architecture)
2. [Bio-Decay Model (ICE/LIQUID/VAPOR)](#bio-decay-model)
3. [CABR Integration (Minting Trigger)](#cabr-integration)
4. [Rogers Diffusion Curve (Stage Release)](#rogers-diffusion-curve)
5. [BTC Reserve (Hotel California Model)](#btc-reserve)
5a. [Architectural Invariants (012-Confirmed)](#architectural-invariants)
6. [Mesh Network Integration](#mesh-network-integration)
7. [Mathematical Formulas](#mathematical-formulas)
8. [Economic Simulations](#economic-simulations)
9. [Early Capital Provider Economics](#early-capital-provider-economics)
10. [Implementation Roadmap](#implementation-roadmap)

---

## Two-Token Architecture

### UP$ (Universal Participation Token)

```yaml
Purpose: "Consumption currency across ALL FoundUps"
Supply: "Floating — minted via CABR validation (WSP 29)"
Value: "ups_per_btc = total_ups_minted / total_btc_reserve"
Minting: "ONLY via CABR validation (WSP 29)"
Characteristics:
  - Inflationary (grows with ecosystem activity)
  - Bio-decaying (incentivizes activity — see Demurrage)
  - BTC-backed (floating rate — more BTC = stronger UP$)
  - Cross-FoundUp (universal currency)
  - F_i can ONLY swap INTO UP$ (not directly to external)
```

**Supply Dynamics** (floating value model):
- **More BTC accumulated** → ups_per_btc decreases → each UP$ worth more BTC
- **More UP$ minted** → ups_per_btc increases → each UP$ worth less BTC
- **Bio-decay** removes UP$ from circulation → deflation → UP$ strengthens
- **Net effect**: Activity creates UP$ (inflation) + decay removes UP$ (deflation) + fees add BTC (backing)

**Example**:
```python
from modules.foundups.simulator.economics.btc_reserve import get_btc_reserve

reserve = get_btc_reserve()

# Initial state: genesis rate
# ups_per_btc = 100,000,000 (genesis default)

# After ecosystem activity:
# - 50M UP$ minted via CABR validation
# - 0.5 BTC accumulated from fees/decay/exits
# ups_per_btc = 50,000,000 / 0.5 = 100,000,000 (stable!)

# After heavy activity + decay:
# - 80M UP$ minted, but 30M decayed away → 50M circulating
# - 1.2 BTC accumulated
# ups_per_btc = 50,000,000 / 1.2 = 41,666,667 (UP$ strengthened!)
```

### FoundUp Tokens (e.g., JUNK$ for GotJunk)

```yaml
Purpose: "Asset-specific staking tokens"
Supply: "21,000,000 fixed (Bitcoin parity)"
Acquisition: "Swap UP$ (burns UP$, mints FoundUp token)"
Characteristics:
  - Deflationary (fixed cap)
  - Stage-released (Rogers Diffusion)
  - Slower decay than UP$ (incentivizes staking)
  - Governance rights in FoundUp
  - Revenue sharing from fees
```

**Stage Allocation** (Rogers Diffusion):
```yaml
Innovators (2.5%):        525,000 tokens
  IDEA:        175,000  # 1:1 swap ratio
  Proto:       175,000  # 1:1 swap ratio
  Soft_Proto:  175,000  # 1:1 swap ratio

Early_Adopters (13.5%):  2,835,000 tokens
  MVP:       2,835,000  # 10:1 swap ratio

Early_Majority (34%):    7,140,000 tokens
  Launch:    7,140,000  # 100:1 swap ratio

Late_Majority (34%):     7,140,000 tokens
  Crowdfunding: 7,140,000  # 50:1 swap ratio

Laggards (16%):          3,360,000 tokens
  System_Reserve: NEVER RELEASED (stabilization fund)
```

---

## Bio-Decay Model (ICE/LIQUID/VAPOR)

### Water Analogy for Intuitive UX

```
EARN UP$ (CABR validated) → LIQUID (wallet, decaying)
                                    ↓
              ┌─────────────────────┼─────────────────────┐
              ↓                     ↓                     ↓
          STAKE               LET DECAY               EXIT
              ↓                     ↓                     ↓
        ICE (frozen)        RESERVOIR              VAPOR (tax)
        No decay            Returns to              15% fee
        Earn yield          Active users            80% → BTC
                                                    20% → Reservoir
```

### State Definitions

**ICE (Staked)**:
```yaml
State: "Frozen in FoundUp token (e.g., JUNK$)"
Decay: NONE
Benefits:
  - Governance voting rights
  - Revenue sharing (transaction fees)
  - Priority access to features
  - Network status/reputation
Transition: "Stake UP$ → Receive FoundUp token position"
```

**LIQUID (Wallet)**:
```yaml
State: "Unstaked in user wallet"
Decay: ADAPTIVE (0.5% - 5% monthly)
Formula: "U(t) = U₀ · e^(-λ(t)·t)"
Lambda_Calculation:
  base: "λ_min + enzymatic_acceleration"
  circadian: "+ 30% during 6-7 PM local"
  cap: "Max 3% daily (no shock)"
Triggers:
  - Time elapsed since last activity
  - Inactivity period (D days)
  - Circadian pulse window
```

**VAPOR (Exited)**:
```yaml
State: "Swapped to external cryptocurrency"
Tax: "15% evaporation fee"
Routing:
  BTC_Allocation (80%): "Buy BTC, lock in reserves"
  Reservoir (20%): "Redistribute to active users"
Irreversible: "One-way exit (cannot return)"
Purpose: "Capture value on exit, strengthen ecosystem"
```

### Decay Relief Activities

**Actions that reset decay timer (D=0)**:
```yaml
FoundUp_Actions:
  - list_item:       24h relief, 1.0 UP$ reward
  - sell_item:       48h relief, 2.0 UP$ reward
  - host_storage:    24h relief, 0.01 UP$ per file

Social_Actions:
  - invite_friend:   72h relief, 10.0 UP$ reward
  - share_boost:     12h relief, 0.5 UP$ reward

Governance:
  - vote_proposal:   24h relief, 0.1 UP$ reward
  - create_proposal: 168h relief, 5.0 UP$ reward

Cross_FoundUp:
  - use_other_foundup: 24h relief, 0.5 UP$ reward
  - complete_cabr_task: 48h relief, 5.0 UP$ reward
```

---

## CABR Integration (Minting Trigger)

### The Critical Rule: CABR-Only Minting

**UP$ is ONLY minted when CABR validates beneficial action** - not arbitrary creation.

**Why This Matters**:
- **Prevents gaming**: Multi-agent consensus required
- **Ensures quality**: Better actions = more rewards
- **Ties to value**: UP$ creation = real benefit created
- **BTC correlation**: Minting limited by reserve capacity

### CABR Validation Flow

```
User Action → Submit to CABR Oracle
                    ↓
        Phase 1: Gemma (50ms classification)
        Phase 2: Qwen (200ms strategic analysis)
        Phase 3: Vision DAE (500ms quality check)
                    ↓
        Consensus = weighted_avg(gemma, qwen, vision)
                    ↓
        IF consensus >= 0.618 (golden ratio):
            UP$ = base_reward × consensus_score
            Mint to LIQUID wallet
            Start decay timer
        ELSE:
            Reject (no mint)
```

**Example (GotJunk Item Listing)**:
```python
# User lists item with photo
action = {
    "type": "list_item",
    "photo": photoBlob,
    "description": "Vintage oak desk, good condition",
    "price": 50,
    "location": {lat: 34.05, lon: -118.25}
}

# CABR validation
gemma_score = 0.85  # Good classification (furniture)
qwen_score = 0.75   # No gaming detected, reasonable price
vision_score = 0.90  # High quality photo, real item

# Weighted consensus
consensus = (gemma * 0.30) + (qwen * 0.50) + (vision * 0.20)
consensus = (0.85 * 0.30) + (0.75 * 0.50) + (0.90 * 0.20)
consensus = 0.255 + 0.375 + 0.180 = 0.81

# Check threshold
if consensus >= 0.618:  # ✅ PASSED
    base_reward = 1.0  # Base for "list_item"
    up_minted = base_reward * consensus
    up_minted = 1.0 * 0.81 = 0.81 UP$

    # Mint to user's LIQUID wallet
    mint_to_liquid_wallet(user_id, 0.81)
```

### Anti-Gaming Patterns Detected

**Qwen Pattern Analysis**:
```python
gaming_patterns = {
    "excessive_listing": {
        "threshold": "> 20 listings/24h",
        "penalty": "Temporary ban 24h"
    },
    "duplicate_descriptions": {
        "threshold": "> 50% identical text",
        "penalty": "Reduce rewards 50%"
    },
    "self_trading": {
        "threshold": "Buyer == Seller pattern",
        "penalty": "Permanent ban"
    },
    "invite_farming": {
        "threshold": "Same IP invites > 70%",
        "penalty": "Void all invite rewards"
    }
}
```

---

## Rogers Diffusion Curve (Continuous S-Curve Release)

### Adoption-Based Token Release

Based on Everett Rogers' **Diffusion of Innovation** theory, implemented as a **continuous sigmoid S-curve** — no artificial tier boundaries.

```
         tokens_released = 21,000,000 × sigmoid(adoption_score)

100% ├─────────────────────────────────────────────── Full saturation
     │                                        ╱
 95% ├──────────────────────────────────╱── Late Majority
     │                              ╱
 50% ├──────────────────────────╱────────── INFLECTION POINT
     │                      ╱
  5% ├──────────────────╱────────────────── Early Adopters
     │              ╱
  0% ├──────────────────────────────────────── Genesis
     └──────────────────────────────────────────
       Adoption Score (0.0 → 1.0)
```

**Key Insight**: Token release follows pure mathematics, not discrete stages.

| Adoption % | Release % | Tokens Available |
|------------|-----------|------------------|
| 0% | 0.00% | 0 |
| 10% | 0.57% | 120,000 |
| 25% | 4.52% | 949,000 |
| **50%** | **50.00%** | **10,500,000** (inflection) |
| 75% | 95.48% | 20,050,000 |
| 100% | 100.00% | 21,000,000 |

**Implementation** (see `modules/foundups/simulator/economics/token_economics.py`):
```python
def adoption_curve(adoption_score: float, steepness: float = 12.0) -> float:
    """Continuous S-curve - no artificial tier jumps."""
    raw = sigmoid(adoption_score, k=steepness, x0=0.5)
    min_val = sigmoid(0.0, k=steepness, x0=0.5)
    max_val = sigmoid(1.0, k=steepness, x0=0.5)
    return (raw - min_val) / (max_val - min_val)
```

### Conceptual Phases (for UX, not token release)
```

### Stage Mechanics

**IDEA Stage** (Innovators):
```yaml
Cohort: "2.5% - Believers & Visionaries"
Supply: 525,000 tokens total
  IDEA:       175,000 (0.83%)
  Proto:      175,000 (0.83%)
  Soft_Proto: 175,000 (0.84%)
Swap_Ratio: "1:1 (best ratio ever)"
Decay_Rate: "0.382x (slowest decay)"
Invites: "5-20 per user"
Benefits:
  - Founder status
  - Maximum ROI potential
  - Governance power
  - Network effects (early liquidity)
```

**MVP Stage** (Early Adopters):
```yaml
Cohort: "13.5% - Early majority believers"
Supply: 2,835,000 tokens
Swap_Ratio: "10:1 (10 UP$ = 1 JUNK$)"
Decay_Rate: "0.5x"
Invites: "50 per user"
Benefits:
  - Early adopter badge
  - Significant ROI
  - Growing network
```

**Launch Stage** (Early Majority):
```yaml
Cohort: "34% - Mainstream users"
Supply: 7,140,000 tokens
Swap_Ratio: "100:1 (100 UP$ = 1 JUNK$)"
Decay_Rate: "1.0x (standard)"
Invites: "Public (no invites needed)"
Benefits:
  - Mature network
  - Stable ecosystem
  - Full feature set
```

---

## BTC Reserve (Hotel California Model)

### "You can check in, but you can never leave"

BTC flows INTO the reserve from multiple sources. It **never** flows out. This creates an ever-growing backing for UP$ value.

**BTC Inflow Sources**:
```yaml
Subscriptions:
  - Spark ($2.95/mo), Explorer ($9.95), Builder ($19.95), Founder ($49.95)
  - Paid in BTC/ETH/SOL/USDC — ALL converted to BTC reserve

Demurrage_Decay:
  - LIQUID UP$ bio-decay → decayed amount converted to BTC at floating rate
  - Implementation: modules/foundups/simulator/economics/demurrage.py

Exit_Fees (VAPOR):
  - Mined F_i exit: 11% fee → BTC reserve (discourages extraction)
  - Staked F_i exit: 5% fee → BTC reserve (value preservation)
  - UP$ exit: 15% evaporation → 80% to BTC reserve, 20% to reservoir

Trading_Fees:
  - F_i order book trades → fees to BTC reserve
  - Implementation: modules/foundups/simulator/economics/fi_orderbook.py
```

**BTC-F_i Ratio (Key Economic Metric)**:
```
btc_per_fi = btc_reserve / fi_released

Early ecosystem:  F_i plentiful, BTC/F_i low   (S-curve left)
Mature ecosystem: F_i scarce, BTC/F_i high      (S-curve right)

This mirrors BTC's own halving dynamic:
  S-curve release matches BTC scarcity curve
  Early miners get more tokens per unit work
  Late entrants face higher cost per token
```

**Implementation**: `modules/foundups/simulator/economics/btc_reserve.py` (BTCReserve class)

**Safety Mechanisms**:
```yaml
Circuit_Breaker: Prevents death spirals (modules/foundups/simulator/economics/circuit_breaker.py)
Emergency_Reserve: Ethena-style stability fund (modules/foundups/simulator/economics/emergency_reserve.py)
Rage_Quit: Moloch-style fair exit (modules/foundups/simulator/economics/rage_quit.py)
Bonding_Curve: Guaranteed liquidity AMM (modules/foundups/simulator/economics/bonding_curve.py)
```

---

## Architectural Invariants (012-Confirmed)

These are non-negotiable design constraints confirmed by 012. Do not deviate.

### Backing Chain

```
F_i <-- backed by --> UP$ <-- backed by --> BTC

CABR scores and routes UP$ flow — does NOT back tokens.
CABR is the routing/scoring engine, BTC is the backing.
```

### Blockchain Agnostic

- F_i tokens are **native pAVS tokens**, not ERC-20 or chain-specific
- `TokenFactoryAdapter` abstracts the blockchain backend
- No Polygon, no Mumbai, no chain-locked smart contracts
- Chain selection is a deployment decision, not an architectural one

### F_i Swap Path

```
F_i --> UP$ --> external (BTC/ETH/SOL/USDC)

F_i can ONLY be swapped into UP$ (not directly to external).
This forces all exits through the UP$ liquidity layer.
```

### V3 Real-Time Consensus

- CABR V3 (Valuation) produces **real-time consensus scores** (0-1)
- NOT quarterly reporting, NOT batch processing
- Every PoB event gets an immediate V3 score
- See WSP 29 Section: "The 3V Engine Pattern"

### Proof of Benefit (PoB)

Six economic FAM events constitute Proof of Benefit:

| FAM Event | PoB Meaning | CABR Input |
|-----------|-------------|------------|
| `proof_submitted` | "I did work" | task_completion_rate |
| `verification_recorded` | "Work was confirmed" | verification_participation |
| `payout_triggered` | "Tokens transferred" | task_completion_rate |
| `milestone_published` | "Achievement recorded" | governance_engagement |
| `fi_trade_executed` | "Market activity" | cross_foundup_collaboration |
| `investor_funding_received` | "Capital committed" | governance_engagement |

These feed CABR `part_score` at trust 1.0. Full spec: [WSP 29: CABR Engine](../../../WSP_knowledge/src/WSP_29_CABR_Engine.md)

### Layer Architecture

```
Layer 0: BTC (reserve backing — Hotel California)
Layer 1: Smart contracts (chain-agnostic via TokenFactoryAdapter)
Layer 2: Off-chain agent operations (0102 agents, FAM DAEmon, CABR scoring)
```

---

## Mesh Network Integration

### Storage Rewards (WSP 98 Integration)

**IPFS Hosting Rewards**:
```yaml
Mechanism: "Host item photos on IPFS → Earn UP$"
Validation: "Merkle proof of storage"
Reward: "0.01 UP$ per file served to peer"
CABR_Check: "Uptime > 95%, no fake serves"

Example:
  User hosts 1000 item photos
  Average 10 serves per photo per month
  Earnings: 1000 × 10 × 0.01 = 100 UP$ per month
```

**Mesh Coordination**:
```javascript
// modules/foundups/gotjunk/frontend/App.tsx
import { MeshDAE } from '@foundups/mesh-core';

const gotjunkMesh = new MeshDAE({
  foundupId: 'gotjunk',
  capabilities: ['storage', 'discovery'],
  rewards: {
    storage: 0.01,  // UP$ per file served
    discovery: 0.001  // UP$ per peer discovered
  }
});

// Auto-earn UP$ for hosting
gotjunkMesh.on('file_served', async (event) => {
  // CABR validates serving
  const validation = await cabr.validate({
    type: 'host_storage',
    proof: event.merkleProof,
    uptime: event.uptimePercent
  });

  if (validation.passed) {
    // Mint UP$ reward
    await mintUPS(user.id, validation.upAmount);
  }
});
```

---

## Mathematical Formulas

### Adaptive Decay (Michaelis-Menten)

```
λ(t) = λ_min + (λ_max - λ_min) · (D / (K + D))

Where:
  λ(t) = decay rate at time t
  D = days inactive
  K = 7 (half-maximal constant)
  λ_min = 0.005/day (0.5% monthly)
  λ_max = 0.05/day (5% monthly)
```

**Circadian Pulse**:
```
if is_pulse_window(local_time):  # 6-7 PM
    λ(t) *= 1.30  # 30% boost
```

**Exponential Decay**:
```
U(t) = U₀ · e^(-λ(t)·t)

Where:
  U(t) = value at time t
  U₀ = initial value
  t = time in days
```

### UP$ Floating Value Model

```
ups_per_btc = total_ups_minted / total_btc_reserve

Where:
  total_ups_minted = cumulative UP$ created via CABR validation
  total_btc_reserve = BTC accumulated (Hotel California — never exits)

Value dynamics:
  More BTC accumulated → ups_per_btc decreases → each UP$ worth more BTC
  More UP$ minted → ups_per_btc increases → each UP$ worth less BTC
  Bio-decay removes UP$ from circulation → ups_per_btc decreases → deflation

Implementation: modules/foundups/simulator/economics/btc_reserve.py (BTCReserve.ups_per_btc)
```

### BTC-F_i Ratio (Economic Health Metric)

```
btc_per_fi = btc_reserve / fi_released

This ratio should INCREASE over time:
  - BTC reserve grows (Hotel California — inflows from fees, decay, exits)
  - F_i release follows S-curve (scarcer over time)
  - Combined effect: each F_i becomes more BTC-backed

Tracked in simulator: mesa_model.py records snapshots every 50 ticks
Implementation: BTCReserve.total_btc / adoption_curve(score) * 21_000_000
```

---

## Founding Members + Anonymous Stakers (Du 4% Pool)

The Du 4% pool is unique: it's **PASSIVE** — participants earn every epoch without requiring active work.

### Who Qualifies

| Category | Requirements | Access |
|----------|-------------|--------|
| **Founding Member** | Active subscription (any tier) | Du pool |
| **Anonymous Staker** | BTC locked in contract | Du pool |
| **Genesis Member** | Joined before launch | ALL FoundUps ecosystem-wide |
| **Future Participant** | Joined after launch | Only FoundUps they work on |

**FOMO**: Genesis member class CLOSES at launch. Join now or miss forever.

### Degressive Tier Model (Prevents Infinite Extraction)

As stakers earn more, their share naturally decreases:

```
Earned/Staked Ratio    Activity Tier    Pool Share
─────────────────────────────────────────────────
< 10x                  du (tier 2)      80% of 4% = 3.2%
10x - 100x             dao (tier 1)     16% of 4% = 0.64%
> 100x                 un (tier 0)       4% of 4% = 0.16%
```

**Lifetime floor**: Even after 100x return, stakers still share in 0.16% of total F_i (never lose access).

**Math**: Each tier share is divided by count at that tier:
```python
individual_share = (pool × tier_percentage) / count_at_tier

# Example: 10 stakers at du tier, 100 F_i epoch
# du_tier_share = (4 × 0.80) / 10 = 0.32 F_i each
```

### Passive vs Active Earning

| Pool | Mode | Trigger | Who |
|------|------|---------|-----|
| **Du (4%)** | PASSIVE | Every epoch | Founding members + stakers |
| **Dao (16%)** | ACTIVE | Per 3V task | 0102 agents |
| **Un (60%)** | ACTIVE | Per engagement | 012 stakeholders |

**Implementation**: `modules/foundups/simulator/economics/pool_distribution.py` (StakerPosition, ComputeMetrics)

### Agent Compute Weight (Dao 16% Pool)

0102 agents earn F_i scaled by compute cost:

```python
fi_earned = base_rate × v3_score × compute_weight

# Compute weight = (tokens_used / 1000) × tier_factor
TIER_WEIGHTS = {
    "opus": 10.0,    # Heavy compute → more F_i
    "sonnet": 3.0,   # Medium compute
    "haiku": 1.0,    # Light compute (baseline)
    "gemma": 0.5,    # Local inference
    "qwen": 0.5,     # Local inference
}
```

### Epoch Timing

| Cycle | Interval | Purpose |
|-------|----------|---------|
| Mini-epoch | 10 ticks | Demurrage (bio-decay) |
| Epoch | 100 ticks | Du pool distribution (passive) |
| Macro-epoch | 900 ticks | BTC-F_i ratio snapshot |
| Event | Real-time | Dao/Un payouts (per 3V task) |

**Implementation**: `modules/foundups/simulator/config.py` (epoch timing constants)

---

## Early Capital Provider Economics

> **IMPORTANT DISTINCTION (CABR/PoB Paradigm):**
> This section describes **I_i token holders** via Bitclout-style bonding curve.
> This is DIFFERENT from **Du pool stakers** (protocol participants):
> - Du Pool Stakers = CABR/PoB terminology (distribution ratio, allocations)
> - I_i Holders = Traditional terminology (returns, multiples) - may require separate legal review

**Full specification**: See [INVESTOR_ECONOMICS.md](../../foundups/simulator/economics/INVESTOR_ECONOMICS.md)

### Bitclout-Inspired Bonding Curve

Early investors receive **I_i (Investor Tokens)** priced on a quadratic bonding curve (same model as BitClout/DeSo's $200M raise from a16z, Sequoia):

```yaml
Price_Formula: "P = k × supply^n"
Parameters:
  k: 0.0001  # Price constant (BTC per token at supply=1)
  n: 2       # Quadratic (Bitclout-style)
```

### BTC Escrow Model ("Dry Wallet")

Investor BTC is **escrowed**, not spent immediately:

```
Investor BTC → Dry Wallet (Escrow)
                    ↓
              Sequestered for 3 years
                    ↓
              [CHOICE POINT at Year 3]
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
 BUYOUT         PARTIAL          HOLD
 (10x)          (50/50)        (100x+)
```

### Stakeholder Pool Participation (12.16%)

Investors participate at **DAO activity level** in the Token Pool Matrix:

```
Pool Structure (WSP 26 Section 6.3-6.4):
  Stakeholders 80%:  Un(60%) + Dao(16%) + Du(4%)
  Network 20%:       Network(16% drip) + Fund(4% held)

Activity tiers (share within each pool, divided by count at tier):
  du(2)  = 80% of pool  (founding members + stakers — PASSIVE)
  dao(1) = 16% of pool  (investors at DAO level)
  un(0)  =  4% of pool  (degressive floor after 100x return)

Pool earning modes:
  Du (4%):   PASSIVE — Founding members/stakers earn every epoch
  Dao (16%): ACTIVE — 0102 agents earn per 3V task completion
  Un (60%):  ACTIVE — 012 stakeholders earn per FoundUpCube engagement

Investor DAO-level access:
                 Un(60%)  Dao(16%)  Du(4%)
-----------------------------------------------
dao level:       9.60%    2.56%     0.64%

TOTAL: 12.16% of ALL FoundUp token distributions!
```

**Implementation**: `modules/foundups/simulator/economics/pool_distribution.py` (PoolDistributor class)

**Example** (100 FoundUps, 720M F_i/year):
- Annual to investor pool: 87,552,000 F_i
- 5-year: 437,760,000 F_i
- Seed investor (46% of pool): 203M F_i

### Return Projections

| Round | BTC In | Pool % | 5Y F_i | Return |
|-------|--------|--------|--------|--------|
| Pre-Seed | 0.5 | 15% | 65M | **6,000x** |
| Seed | 10 | 46% | 203M | **1,600x** |
| Series A | 50 | 20% | 88M | **118x** |

### The Hybrid Exit Model

> "The floor is 10x. The ceiling is 1000x. You choose."

### Investment Rounds (Total: 755 BTC / ~$75.5M)

| Round | BTC Range | Target |
|-------|-----------|--------|
| Pre-Seed | 0.1-1 BTC | 5 BTC |
| Seed | 1-10 BTC | 50 BTC |
| Series A | 10-50 BTC | 200 BTC |
| Series B | 50-100 BTC | 500 BTC |

### Simulator Implementation

```python
from modules.foundups.simulator.economics import (
    InvestorPool, bonding_price, bonding_tokens_for_btc
)

pool = InvestorPool(k=0.0001, n=2.0)
tokens, tier = pool.invest_btc("investor_1", btc_amount=10.0)
returns = pool.get_investor_returns("investor_1")
# returns['price_return_multiple'] → 1,600x for seed
```

---

## Implementation Roadmap

### Phase 1: Design (✅ COMPLETE)
- [x] Architecture design
- [x] Mathematical modeling
- [x] WSP integration
- [x] Documentation

### Phase 2: Simulator Economics (✅ COMPLETE)
- [x] `token_economics.py` — S-curve adoption, dual-token model
- [x] `btc_reserve.py` — Hotel California BTC reserve
- [x] `demurrage.py` — Bio-decay (Michaelis-Menten)
- [x] `pool_distribution.py` — Un/Dao/Du epoch rewards
- [x] `fi_orderbook.py` — F_i buy/sell order book
- [x] `circuit_breaker.py` — Death spiral prevention
- [x] `bonding_curve.py` — Guaranteed liquidity AMM
- [x] `rage_quit.py` — Moloch-style fair exit
- [x] `emergency_reserve.py` — Ethena-style stability fund
- [x] `investor_staking.py` — Bitclout bonding curve
- [x] `investor_liability.py` — Buyout coverage engine
- [x] Mesa model integration with DemurrageEngine + BTCReserve + PoolDistributor

### Phase 3: Smart Contracts — Blockchain Agnostic (⏳ PENDING)
- [ ] TokenFactoryAdapter (chain-agnostic abstraction layer)
- [ ] F_i token contract template (21M cap per FoundUp)
- [ ] CABR Oracle integration (V1/V2/V3 pipeline)
- [ ] Testnet deployment (chain TBD — NOT locked to any L1/L2)

### Phase 4: Frontend Integration (⏳ PENDING)
- [ ] Decay notifications UI
- [ ] Stake/unstake components
- [ ] CABR validation feedback
- [ ] Invite system

### Phase 5: Production (⏳ PENDING)
- [ ] Security audit
- [ ] Mainnet deployment
- [ ] GotJunk IDEA stage launch
- [ ] Monitor & iterate

---

## Conclusion

FoundUps tokenomics creates a **self-sustaining, anti-hoarding, quality-driven economy** where:

1. **Value Creation** = CABR-validated beneficial actions
2. **Value Capture** = BTC accumulation on fees
3. **Value Distribution** = Active participants rewarded, inactive decay
4. **Value Stability** = Hotel California BTC reserve (grows forever, never exits)

**Result**: Solo founders can build unicorn-scale FoundUps without VC funding, employees, or centralized infrastructure.

---

**For Implementation Details**:
- CABR Integration: [CABR_INTEGRATION.md](./CABR_INTEGRATION.md)
- Module README: [../README.md](../README.md)
- ModLog: [../ModLog.md](../ModLog.md)
- WSP 26: [WSP_26_FoundUPS_DAE_Tokenization.md](../../../WSP_framework/src/WSP_26_FoundUPS_DAE_Tokenization.md)
