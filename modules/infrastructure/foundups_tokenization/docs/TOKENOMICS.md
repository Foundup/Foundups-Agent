# FoundUps Tokenomics: Complete Economic Model

**Version**: 1.0.0
**Date**: 2025-11-03
**Status**: Architecture Complete, Phase 1 Design Finalized

## Executive Summary

FoundUps tokenomics implements a **bio-decay economic model** where:
1. **UP$ (Universal Participation)** = Inflationary consumption token across ALL FoundUps
2. **FoundUp Tokens** (e.g., JUNK$) = Deflationary 21M-capped asset tokens per FoundUp
3. **CABR Validation** = Only source of UP$ minting (prevents gaming)
4. **Bio-Decay States** = ICE/LIQUID/VAPOR (water analogy for intuitive UX)
5. **BTC Anchoring** = Autonomous meme → stable transformation

**Result**: Self-sustaining economy where **active participation = value creation**, and **inactivity = value redistribution**.

---

## Table of Contents

1. [Two-Token Architecture](#two-token-architecture)
2. [Bio-Decay Model (ICE/LIQUID/VAPOR)](#bio-decay-model)
3. [CABR Integration (Minting Trigger)](#cabr-integration)
4. [Rogers Diffusion Curve (Stage Release)](#rogers-diffusion-curve)
5. [BTC Anchoring (Meme → Stable Transformation)](#btc-anchoring)
6. [Mesh Network Integration](#mesh-network-integration)
7. [Mathematical Formulas](#mathematical-formulas)
8. [Economic Simulations](#economic-simulations)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Two-Token Architecture

### UP$ (Universal Participation Token)

```yaml
Purpose: "Consumption currency across ALL FoundUps"
Supply_Formula: "(BTC_Reserve_Satoshis) / Num_FoundUps"
Minting: "ONLY via CABR validation (WSP 29)"
Characteristics:
  - Inflationary (grows with ecosystem)
  - Bio-decaying (incentivizes activity)
  - BTC-backed (value correlated to reserves)
  - Cross-FoundUp (universal currency)
  - Swappable for FoundUp tokens (one-way)
```

**Supply Dynamics**:
- **More FoundUps Launch** → UP$ distributes across ecosystem → Scarcity per FoundUp
- **More BTC Accumulated** → UP$ value increases → Stronger backing ratio
- **More Activity** → More UP$ minted (via CABR) → But also more BTC accumulation

**Example**:
```python
# Initial state (1 FoundUp, 1 BTC reserve)
num_foundups = 1
btc_reserve = 1.0  # 1 BTC
satoshis = btc_reserve * 100_000_000
up_supply = satoshis / num_foundups
# Result: 100,000,000 UP$ available

# After 10 FoundUps launched, 10 BTC accumulated
num_foundups = 10
btc_reserve = 10.0
satoshis = btc_reserve * 100_000_000
up_supply = satoshis / num_foundups
# Result: Still 100,000,000 UP$ per FoundUp (stable!)
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

## Rogers Diffusion Curve (Stage Release)

### Market Adoption Lifecycle

Based on Everett Rogers' **Diffusion of Innovation** theory:

```
100% ├─────────────────────────────── Laggards (16%) System Reserve
     │                              ╱
 84% ├──────────────────────────╱── Late Majority (34%) Crowdfunding
     │                       ╱
 50% ├───────────────────╱────────── Early Majority (34%) Launch
     │                ╱
 16% ├────────────╱───────────────── Early Adopters (13.5%) MVP
     │         ╱
2.5% ├─────╱──────────────────────── Innovators (2.5%) IDEA/Proto/Soft-Proto
     └──────────────────────────────
       Time (Market Penetration %)
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

## BTC Anchoring (Meme → Stable Transformation)

### Autonomous Stabilization

**Vision**: FoundUp tokens start as pure meme coins, **autonomously** become BTC-backed stablecoins through ecosystem activity.

**Mechanism**:
```yaml
Fee_Collection:
  transaction_fee: "1% of every transaction"
  routing:
    btc_purchase: "80% buys BTC via DEX"
    operations: "20% platform costs"

BTC_Accumulation:
  destination: "Cold wallet per FoundUp"
  access: "Non-extractable (locked forever)"
  purpose: "Economic shadow anchor"

Backing_Ratio_Evolution:
  formula: "Backing_Ratio = BTC_Reserve_USD / FoundUp_Market_Cap"

  Month_1:   0% backed (pure meme)
  Year_1:   10% backed (hybrid)
  Year_3:   50% backed (STABLE COIN classification)
  Year_5+: 100% backed (FULL RESERVE)
```

**Mathematical Model**:
```python
class MemeToStableTransformation:
    def simulate_transformation(self, monthly_volume_usd, years=5):
        results = []
        btc_reserve = 0
        token_price = 0.01  # Initial meme price

        for month in range(years * 12):
            # Transaction volume grows 10% monthly
            volume = monthly_volume_usd * (1.1 ** month)

            # Collect 1% fees
            fees = volume * 0.01

            # 80% buys BTC
            btc_purchase_usd = fees * 0.80
            btc_price = 50000 * (1.02 ** month)  # 2% monthly appreciation
            btc_bought = btc_purchase_usd / btc_price
            btc_reserve += btc_bought

            # Calculate backing ratio
            btc_reserve_value = btc_reserve * btc_price
            market_cap = 21_000_000 * token_price
            backing_ratio = btc_reserve_value / market_cap if market_cap > 0 else 0

            # Classify stability
            if backing_ratio >= 1.0:
                stability = "FULL_RESERVE"
            elif backing_ratio >= 0.5:
                stability = "STABLE_COIN"
            elif backing_ratio >= 0.1:
                stability = "HYBRID"
            else:
                stability = "MEME_COIN"

            results.append({
                "month": month,
                "btc_reserve": btc_reserve,
                "backing_ratio": backing_ratio,
                "stability": stability
            })

        return results
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

### UP$ Supply Formula

```
Total_UP$ = (BTC_Reserve_Satoshis) / Num_FoundUps

Example:
  BTC_Reserve = 10 BTC
  Num_FoundUps = 10
  Satoshis = 10 × 100,000,000 = 1,000,000,000
  Total_UP$ = 1,000,000,000 / 10 = 100,000,000 per FoundUp
```

### BTC Backing Ratio

```
Backing_Ratio = BTC_Reserve_USD / (UP$_Supply × UP$_Price_USD)

Stability_Classification:
  Backing_Ratio >= 1.0  → FULL_RESERVE
  Backing_Ratio >= 0.5  → STABLE_COIN
  Backing_Ratio >= 0.1  → HYBRID
  Backing_Ratio < 0.1   → MEME_COIN
```

---

## Implementation Roadmap

### Phase 1: Design (✅ COMPLETE)
- [x] Architecture design
- [x] Mathematical modeling
- [x] WSP integration
- [x] Documentation

### Phase 2: Smart Contracts (🚧 IN PROGRESS)
- [ ] `UPSBioDecayEngine.sol` (Polygon)
- [ ] `FoundUpToken.sol` template
- [ ] `CABROracle.sol` integration
- [ ] Testnet deployment (Mumbai)

### Phase 3: Backend Services (⏳ PENDING)
- [ ] `bio_decay_engine.py`
- [ ] `cabr_minting_engine.py`
- [ ] `btc_anchor_engine.py`
- [ ] `distribution_dae.py`

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
4. **Value Stability** = Autonomous meme → stable transformation

**Result**: Solo founders can build unicorn-scale FoundUps without VC funding, employees, or centralized infrastructure.

---

**For Implementation Details**:
- CABR Integration: [CABR_INTEGRATION.md](./CABR_INTEGRATION.md)
- Module README: [../README.md](../README.md)
- ModLog: [../ModLog.md](../ModLog.md)
- WSP 26: [WSP_26_FoundUPS_DAE_Tokenization.md](../../../WSP_framework/src/WSP_26_FoundUPS_DAE_Tokenization.md)
