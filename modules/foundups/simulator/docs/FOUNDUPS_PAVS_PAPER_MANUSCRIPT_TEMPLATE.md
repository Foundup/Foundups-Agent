# FoundUps pAVS Economic Model Paper Template

## Working Title
Self-Sustaining FoundUps: A Falsifiable Simulation Study of pAVS Treasury Economics

## Author Block
- Authors:
- Affiliation:
- Date:
- Commit hash:

## Abstract

This paper presents a simulation-based analysis of the FoundUps pAVS (Peer-to-Peer Autonomous Venture System) economic model, which addresses the capital allocation problem in decentralized autonomous organizations: how to sustainably fund autonomous agent operations while aligning incentives across heterogeneous participant classes.

We describe a dual-token architecture with demurrage-bearing settlement tokens (UPS) and fixed-supply venture tokens (F_i), implementing pool-based distribution across three participant tiers: stakeholders (60% Un, 16% Dao, 4% Du) and network operations (20%). The model employs S-curve token release governed by adoption dynamics rather than arbitrary vesting schedules.

Using a tick-based simulator with deterministic seeding (seed=42), we evaluate downside/base/upside stress scenarios (demand_factor=0.65/1.00/1.25). In the baseline growth lane, the first modeled sustainability crossing occurs around 20,000 total FoundUps (about 6,917 post-OPO), when both `net_revenue_btc > 0` and `downside_ratio_p10 >= 1.0`.

**Limitations**: Results are simulation-derived and have not been validated against live economic data. The model assumes rational actors and does not account for adversarial manipulation, regulatory intervention, or black-swan liquidity events.

**Falsifiable prediction**: Within 36 months of genesis, at least one configured scenario run should satisfy `net_revenue_btc > 0` and `downside_ratio_p10 >= 1.0`; failure to meet either condition falsifies this claim.

*(Word count: 212)*

### Abstract Equations

| ID | Equation | Units | Source |
|----|----------|-------|--------|
| E0.1 | `S(x) = 1 / (1 + exp(-k(x - 0.5)))` | dimensionless | token_economics.py:26-39 |
| E0.2 | `release_pct = (S(adoption) - S(0)) / (S(1) - S(0))` | dimensionless [0,1] | token_economics.py:60-73 |
| E0.3 | `net_revenue_btc = combined_revenue_platform_capture_btc - operational_cost_btc` | BTC/year | ten_year_projection.py:852 |
| E0.4 | `downside_ratio_p10 = downside.revenue_cost_ratio_p10 * platform_capture_share` | dimensionless | ten_year_projection.py:869 |
| E0.5 | `is_self_sustaining = (net_revenue_btc > 0) AND (downside_ratio_p10 >= 1.0)` | boolean | ten_year_projection.py:877 |

### Abstract Assumption Register

| Assumption | Risk Level | Consequence if Wrong |
|------------|------------|---------------------|
| Rational actors | HIGH | Gaming, Sybil attacks, pool manipulation |
| Fee revenue scales linearly with FoundUp count | MEDIUM | Nonlinear effects at scale may break projections |
| Demurrage rate acceptable to participants | MEDIUM | Excessive decay drives users to competitors |
| BTC price stable at $100K baseline | LOW | Projections denominated in BTC, USD estimates shift |
| No regulatory intervention | HIGH | Classification changes could halt operations |

## 1. Introduction

### 1.1 Problem Statement

Decentralized autonomous organizations face a fundamental economic trilemma: **capital allocation efficiency**, **incentive alignment across participant classes**, and **treasury sustainability without external subsidy**. Traditional platform economics resolve this through advertising (extracting user attention) or transaction fees (extracting value from every interaction), creating misaligned incentives where platform success diverges from participant welfare.

The FoundUps pAVS model proposes an alternative: a dual-token architecture where autonomous agents earn through validated work (Proof of Benefit), while human participants allocate compute resources through stake-based participation. This paper evaluates whether such a system can achieve self-sustainability under realistic market conditions.

**First-Principles Constraints**:
1. **Conservation**: Total token supply is fixed (21M F_i per FoundUp); value cannot be created from nothing
2. **Velocity**: Demurrage (bio-decay) forces tokens to circulate rather than accumulate
3. **Backing**: Settlement tokens (UPS) are backed by BTC reserves ("Hotel California" - BTC enters, never exits)
4. **Work-Value Linkage**: Token distribution requires validated beneficial action (CABR 3V engine)

**Contrast with Extractive Models**:

| Model | Revenue Source | Alignment | Sustainability |
|-------|---------------|-----------|----------------|
| Ad-funded (Google) | User attention extraction | Misaligned (ads vs users) | External (advertisers) |
| Transaction-fee (Pump.fun) | 1.25% per trade | Partially aligned | Volume-dependent |
| pAVS (this study) | 2% DEX + demurrage recycling | Work-aligned (PoB) | Self-sustaining (hypothesis) |

*Sources: Pump.fun fee structure from CoinMarketCap/DefiLlama (2026-02-17); pAVS from `simulator/economics/pumpfun_comparison.py`*

### 1.2 Research Questions

- **RQ1**: Under what parameter ranges does the pAVS model satisfy the simulator sustainability gate (`net_revenue_btc > 0` and `downside_ratio_p10 >= 1.0`)?

- **RQ2**: How does the S-curve adoption model affect token distribution fairness across early vs late participants?

- **RQ3**: What are the failure modes under market stress (demand shocks, fee compression, liquidity crises)?

- **RQ4**: How does the dual-circulation system (UPS for humans, F_i for agents) affect incentive alignment compared to single-token models?

### 1.3 Claims Boundary

**(a) Supported by Current Evidence**:
- Pool distribution percentages (60/16/4/16/4) are formally specified in code
- S-curve mathematics (sigmoid with k=12) produces predictable release schedules
- Deterministic simulation produces reproducible results with fixed seed
- Fee structures (2% DEX, 2-15% exit) are comparable to real-world platforms (Pump.fun: 1.25%)

**(b) Hypothesis Only**:
- Sustainability crossing near 20,000 total FoundUps in the baseline lane (model-dependent; requires live validation)
- Demurrage rate (1%/day bio-decay) acceptable to participants
- CABR V3 validation produces meaningful work-value scores
- Rational actor assumption holds under real-world conditions

**(c) Out of Scope**:
- Legal classification of tokens (utility vs security)
- Specific blockchain implementation details
- Adversarial attacks beyond defined stress scenarios
- Governance mechanisms for parameter adjustment
- Cross-chain interoperability

### Section 1 Evidence Table

| Claim | Source | Access Date |
|-------|--------|-------------|
| Pump.fun 1.25% fee | CoinMarketCap, DefiLlama | 2026-02-17 |
| Pump.fun $15.5M peak daily | CoinMarketCap | 2026-02-17 |
| Perplexity $200M ARR | DemandSage | 2026-02-17 |
| pAVS 2% DEX fee | `simulator/economics/pumpfun_comparison.py:47` | - |
| Pool percentages | `simulator/economics/pool_distribution.py:85-91` | - |

### Section 1 Assumption Register

| Assumption | Risk | Mitigation |
|------------|------|------------|
| Pump.fun comparison is valid | MEDIUM | Different token types, but fee mechanics comparable |
| First-principles constraints complete | LOW | May miss emergent constraints |
| Extractive model characterization fair | LOW | Based on documented revenue models |

## 2. Model Specification

### 2.1 Entities

The pAVS model comprises five entity classes:

| Entity | Role | Cardinality | Source |
|--------|------|-------------|--------|
| **Founders** | Create FoundUps, define scope | 1-N per simulation | `agents/founder_agent.py` |
| **Users (012)** | Stake UPS, earn from Un/Dao pools | 1-N per simulation | `agents/user_agent.py` |
| **0102 Agents** | Perform validated work, earn F_i | 1-N per FoundUp | `mesa_model.py:66-78` |
| **FoundUps** | Autonomous ventures with F_i tokens | 1-N per simulation | `state_store.py:19-74` |
| **Reserves** | BTC backing + Treasury pools | 2 (BTC Reserve, Treasury) | `economics/btc_reserve.py` |

### 2.2 State Variables (with units)

| Symbol | Name | Unit | Description | Source |
|--------|------|------|-------------|--------|
| `B(t)` | BTC Reserve | BTC | Total Bitcoin locked (Hotel California) | `btc_reserve.py` |
| `U(t)` | UPS Supply | sats | Total circulating settlement tokens | `demurrage.py` |
| `F_i(t)` | F_i Released | tokens | FoundUp tokens released to date | `pool_distribution.py` |
| `S(t)` | Total Staked | sats | UPS committed to FoundUps | `state_store.py:32` |
| `T(t)` | Treasury | sats | pAVS operational fund | `demurrage.py:32` |
| `N(t)` | Network Pool | sats | Ecosystem distribution pool | `pool_distribution.py:89` |
| `t` | Tick | integer | Discrete time step | `config.py:19-25` |
| `alpha(t)` | Adoption Score | [0,1] | S-curve position | `token_economics.py:42` |

**Unit Consistency Note**: 1 UPS = 1 satoshi (canonical constraint per WSP 26).

### 2.3 Flow Variables (with units)

| Symbol | Name | Unit | Description | Source |
|--------|------|------|-------------|--------|
| `DeltaB_in(t)` | BTC Inflow | BTC/tick | Net BTC entering reserve | `btc_reserve.py:37-46` |
| `DeltaU_mint(t)` | UPS Minted | sats/tick | New UPS routed from treasury via CABR | `cabr_flow_router.py` |
| `DeltaU_decay(t)` | UPS Decayed | sats/tick | Demurrage (bio-decay) | `demurrage.py:22` |
| `DeltaF_i(t)` | F_i Released | tokens/tick | Per-FoundUp token release | `pool_distribution.py` |
| `f_dex` | DEX Fee | sats/trade | 2% of trade volume | `fee_revenue_tracker.py` |
| `f_exit` | Exit Fee | sats/exit | 2-15% of extraction | `btc_reserve.py:43` |

### 2.4 State Transition Equations

**APPROXIMATION WARNING**: The equations below are **simplified models**, not exact implementations.
- E2.2-E2.3 use continuous approximations of discrete step functions
- E2.5 abstracts multi-step routing into single expression
- See `token_economics.py:712` for implementation notes on approximation gaps

**E2.1: BTC Reserve Update** (Hotel California) - EXACT
```
B(t+1) = B(t) + DeltaB_sub(t) + DeltaB_fee(t) + DeltaB_exit(t)
       >= B(t)  [monotonically non-decreasing]
```
*Status*: EXACT (implemented directly in code)
*Unit check*: BTC = BTC + BTC + BTC + BTC [OK]
**E2.2: UPS Demurrage** (Bio-Decay) - APPROXIMATION
```
U(t+1) = U(t) * exp(-lambda(t) * Delta_t) + DeltaU_mint(t)
where lambda(t) = lambda_base * tier_multiplier(activity)
```
*Status*: CONTINUOUS APPROXIMATION of discrete Michaelis-Menten kinetics
*Actual*: `lambda(t) = lambda_min + (lambda_max - lambda_min) * (D / (K + D))` per `demurrage.py:160-164`
*Unit check*: sats = sats * dimensionless + sats [OK]
**E2.3: F_i S-Curve Release**
```
DeltaF_i(t) = F_max * S'(alpha(t)) * Delta_alpha(t)
where S(x) = 1 / (1 + exp(-k(x - 0.5)))
      S'(x) = k * S(x) * (1 - S(x))  [derivative]
      k = 12 (default steepness)
```
*Source*: `token_economics.py:26-73`
*Unit check*: tokens = tokens * dimensionless * dimensionless [OK]
**E2.4: Pool Distribution** (per epoch)
```
R_epoch = Total rewards available this epoch [sats]

Un_pool  = 0.60 * R_epoch  (active: engagement-based)
Dao_pool = 0.16 * R_epoch  (active: 3V work-based)
Du_pool  = 0.04 * R_epoch  (passive: staker dividends)
Net_pool = 0.16 * R_epoch  (network operations)
Fund     = 0.04 * R_epoch  (treasury fund)
```
*Source*: `pool_distribution.py:85-91`
*Unit check*: sats = dimensionless * sats [OK]
**E2.5: CABR Pipe Flow**
```
UPS_flow = Treasury_available * CABR_score * valve_open
where CABR_score in [0, 1]
      valve_open in {0, 1} (binary: V3 validation passed)
```
*Source*: `cabr_flow_router.py:56`
*Interpretation*: CABR acts as pipe size (0-100%), V3 acts as valve (open/closed)

### 2.5 Tick Semantics

| Epoch Type | Interval | Action | Source |
|------------|----------|--------|--------|
| Mini-epoch | 10 ticks | Demurrage decay applied | `config.py:23` |
| Epoch | 100 ticks | Du pool passive distribution | `config.py:24` |
| Macro-epoch | 900 ticks | BTC-F_i ratio snapshot | `config.py:25` |

**Note**: Dao/Un payouts are EVENT-based (per 3V task completion), not epoch-based.

### Section 2 Evidence Table

| Variable | Defined In | Line | Verified |
|----------|-----------|------|----------|
| Pool percentages | `pool_distribution.py` | 85-91 | OK |
| Sigmoid k=12 | `token_economics.py` | 42 | OK |
| Demurrage formula | `demurrage.py` | 22 | OK |
| BTC sources | `btc_reserve.py` | 37-46 | OK |
| Epoch intervals | `config.py` | 23-25 | OK |

### Section 2 Assumption Register

| Assumption | Risk | Note |
|------------|------|------|
| 1 UPS = 1 satoshi | LOW | Canonical constraint, simplifies accounting |
| Sigmoid k=12 is appropriate | MEDIUM | May need tuning for different adoption speeds |
| Tick rate abstraction valid | LOW | Real-time mapping TBD for deployment |
| Hotel California holds | HIGH | Requires smart contract enforcement |

## 3. Accounting Identities and Invariants

### 3.1 Flow-of-Funds Identity

**Theorem 3.1 (Conservation of Value)**: At each tick t, the total system value is conserved:

```
B(t) + U(t)/r(t) = B(t+1) + U(t+1)/r(t+1) + DeltaB_external - DeltaU_burned/r(t)

where:
  B(t) = BTC reserve at tick t [BTC]
  U(t) = UPS circulating supply at tick t [sats]
  r(t) = UPS-to-BTC rate at tick t [sats/BTC]
  DeltaB_external = BTC inflow from subscriptions/fees [BTC]
  DeltaU_burned = UPS burned (subscription payment in UPS) [sats]
```

**Proof Sketch**:
1. BTC inflows (DeltaB_external) increase reserve monotonically (Hotel California)
2. UPS is backed by BTC reserve: value(UPS) = B(t) * r(t)
3. Demurrage redistributes UPS (80% Network, 20% Treasury) but does not destroy value
4. UPS burns reduce supply, strengthening remaining UPS (deflationary)
5. No value creation ex nihilo; all flows traceable to external BTC or validated work

*Source*: `btc_reserve.py`, `demurrage.py:27-29`

### 3.2 Treasury Update Identity

**Identity 3.2 (Treasury Balance)**:

```
T(t+1) = T(t) + 0.20 * DeltaU_decay + 0.04 * R_epoch - expenditures

where:
  T(t) = Treasury balance [sats]
  DeltaU_decay = UPS lost to demurrage [sats]
  R_epoch = Total epoch rewards [sats]
  expenditures = Operational costs [sats]
```

*Unit check*: sats = sats + (dimensionless * sats) + (dimensionless * sats) - sats [OK]
**Sustainability Condition**:
```
Treasury sustainable iff:
  0.20 * DeltaU_decay + 0.04 * R_epoch >= expenditures
```

*Source*: `demurrage.py:28-29`, `pool_distribution.py:90`

### 3.3 Reserve Coverage Metrics

**Definition 3.3a (Reserve Coverage Ratio)**:
```
RCR(t) = B(t) * P_btc / (U(t) * P_ups)

where:
  P_btc = BTC price in USD
  P_ups = UPS price in USD (derived from backing)
```

**Threshold**: RCR >= 1.0 at all times (full backing requirement)

**Definition 3.3b (UPS Value Model)**:
```
P_ups = (B(t) * P_btc) / U(t)

UPS floats with BTC price (not USD-pegged)
```

*Source*: `btc_reserve.py:17-21`

**Truncation/Rounding Effects**:
- UPS amounts stored as integers (satoshis) - no fractional sats
- Pool distribution rounds down to prevent overdisbursement
- Rounding errors accumulate in Treasury (residual collector)

### 3.4 Invariant Check Table

| Invariant | Status | Failure Condition | Test Reference |
|-----------|--------|-------------------|----------------|
| **I1**: B(t+1) >= B(t) | ENFORCED | BTC outflow attempted | `test_btc_reserve_semantics.py` |
| **I2**: Sum of pools = 100% | ENFORCED | Pool percentages drift | `pool_distribution.py:85-91` |
| **I3**: U_circulating <= U_backed | ENFORCED | Over-minting | `test_btc_reserve_semantics.py:14-19` |
| **I4**: F_i(t) <= 21M per FoundUp | ENFORCED | Supply cap breach | `pool_distribution.py:502` |
| **I5**: Fee split sums to 100% | ENFORCED | Distribution leak | `test_full_tide_hardening.py:21` |
| **I6**: No double-count fees | ENFORCED | Fee dedupe failure | `test_full_tide_hardening.py:11-40` |
| **I7**: Network pool delta sync | TESTED | Double-counting | `test_full_tide_hardening.py:43-72` |

### 3.5 Invariant Failure Analysis

**I1 (Hotel California) Failure Modes**:
- Smart contract vulnerability allowing BTC extraction
- Governance attack changing reserve rules
- *Mitigation*: Multi-sig, time-locks, formal verification

**I3 (Backing) Failure Modes**:
- Race condition between mint and reserve update
- Integer overflow in UPS supply
- *Mitigation*: Atomic transactions, SafeMath equivalents

### Section 3 Evidence Table

| Identity | Equation | Verified In | Status |
|----------|----------|-------------|--------|
| Flow-of-funds | E3.1 | `btc_reserve.py` | Code analysis |
| Treasury update | E3.2 | `demurrage.py`, `pool_distribution.py` | Code analysis |
| RCR definition | E3.3a | `btc_reserve.py:17-21` | Code analysis |
| Pool sum = 100% | I2 | `pool_distribution.py:85-91` | Direct verification |

### Section 3 Assumption Register

| Assumption | Risk | Note |
|------------|------|------|
| Atomic transactions available | MEDIUM | Blockchain-dependent |
| Integer arithmetic sufficient | LOW | 64-bit sats handles 21M BTC |
| No external oracle failures | MEDIUM | BTC price feed required |

## 4. Incentive Mechanics

### 4.1 Founder Incentives

**Objective**: Maximize FoundUp success (F_i value appreciation)

**CRITICAL CLARIFICATION**: The Un pool (60%) distributes **UPS** (the spend token), NOT F_i tokens.
- F_i tokens are earned through **CABR-validated work** (Dao pool, 16%)
- Un pool is engagement-based UPS distribution to all stakeholders
- Founders benefit indirectly via FoundUp success, not direct F_i allocation

| Incentive | Mechanism | Source |
|-----------|-----------|--------|
| UPS from engagement | Active participation in Un pool (60% of UPS) | `pool_distribution.py:86` |
| F_i via work | Deploy 0102 agents that earn F_i through Dao pool | `pool_distribution.py:87` |
| CABR score boost | Higher CABR = larger pipe flow = more UPS available | `cabr_flow_router.py` |
| Lifecycle progression | PoC -> Proto -> MVP unlocks higher fee tiers | `smartdao_spawning.py` |
| Exit timing | Vesting discourages premature extraction (2-15% fee) | `fee_revenue_tracker.py:70-77` |

**Constraints**:
- Cannot mint F_i arbitrarily (CABR validation required)
- Cannot extract BTC from reserve (Hotel California)
- Maximum 3 FoundUps per founder (`config.py:42`)

### 4.2 Participant/User Incentives

**012 (Human Stakeholders)**:

| Pool | Share | Access | Earning Mode |
|------|-------|--------|--------------|
| Un | 60% | All stakeholders | ACTIVE (engagement) |
| Dao | 16% | Work contributors | ACTIVE (3V tasks) |
| Du | 4% | BTC stakers only | PASSIVE (epoch dividends) |

*Source*: `pool_distribution.py:7-17`

**0102 (Agent Workers)**:

| Incentive | Mechanism | Source |
|-----------|-----------|--------|
| Compute rewards | F_i proportional to compute tier (Opus=10x, Haiku=1x) | `pool_distribution.py:94-100` |
| Work validation | V3 scoring gates F_i release | `cabr_flow_router.py` |
| No passive income | Agents must work to earn | `staker_viability.py:4-5` |

### 4.3 Treasury/Protocol Incentives

**pAVS Treasury** (20% of demurrage + 4% Fund):
- Minimize operational costs
- Maximize ecosystem health (more FoundUps = more fees)
- Maintain reserve coverage ratio >= 1.0

**Alignment**: Treasury earns from fees and demurrage; both increase with ecosystem activity.

### 4.4 Moral Hazard and Countermeasures

| Risk | Vector | Mitigation | Source |
|------|--------|------------|--------|
| **Sybil staking** | Split stake across many accounts for bonus | Per-012 identity verification | `staker_viability.py:16` |
| **Wash trading** | Fake volume to inflate fees | Fee paid on all trades, not refunded | `fee_revenue_tracker.py` |
| **Founder abandonment** | Launch, extract, exit | Exit fees (2-15% vesting schedule) | `fee_revenue_tracker.py:70-77` |
| **Passive hoarding** | Accumulate UPS without activity | Demurrage (bio-decay) forces velocity | `demurrage.py:14` |
| **Pool gaming** | Fake activity to increase share | CABR V3 validates beneficial action | `cabr_estimator.py` |
| **Late entry attack** | Wait for appreciation, stake big | Degressive tiers (du -> dao -> un) | `pool_distribution.py:28-36` |

### 4.5 Incentive Alignment Mechanisms

| Mechanism | Aligns | Tradeoff |
|-----------|--------|----------|
| Demurrage | Velocity (use it or lose it) | May frustrate savings behavior |
| CABR validation | Work-value linkage | Scoring subjectivity |
| Exit fees | Long-term commitment | Reduces liquidity |
| Pool separation | Human/agent boundary | Complexity |
| Degressive tiers | Early vs late fairness | Caps late-joiner upside |

### Section 4 Evidence Table

| Mechanism | Location | Line(s) |
|-----------|----------|---------|
| Pool percentages | `pool_distribution.py` | 85-91 |
| Compute tier weights | `pool_distribution.py` | 94-100 |
| Exit fee rates | `btc_reserve.py` | 43-44 |
| Degressive thresholds | `staker_viability.py` | 47-49 |
| Activity tier multipliers | `demurrage.py` | 73-78 |

### Section 4 Assumption Register

| Assumption | Risk | Note |
|------------|------|------|
| CABR V3 produces meaningful scores | HIGH | Currently single-agent, needs multi-agent consensus |
| Demurrage socially acceptable | MEDIUM | Novel mechanism, user acceptance unknown |
| Exit fees deter extraction | MEDIUM | May simply shift to slower extraction |

## 5. Methods and Calibration

This section documents the simulator infrastructure, scenario definitions, parameter sources, and reproducibility controls. All experiments described in this paper can be replicated using the commands and artifacts specified below.

### 5.1 Simulator Version and Runtime

| Attribute | Value | Source |
|-----------|-------|--------|
| Repository path | `modules/foundups/simulator/` | Project structure |
| Commit hash | `c6ccf28ee09c18772da5fb15ba555b709d3737e0` | Git HEAD (2026-02-21) |
| Python version | 3.12.2 | Runtime environment |
| Framework | Mesa 3.x (agent-based modeling) | `mesa_model.py` imports |
| Tick rate | 1-6 Hz (configurable) | `config.py:19` |
| Metrics artifacts | `memory/validation_runs_2026_02_18_postfix/` | Committed run outputs |

The simulator implements a discrete-time agent-based model where each tick represents one atomic state transition. All agent actions, token flows, and pool updates occur synchronously within a single tick boundary.

### 5.2 Scenario Definitions

Three primary scenarios explore the sustainability envelope:

| Scenario | Seed | Max Ticks | Users | Founders | Action Prob. | Purpose |
|----------|------|-----------|-------|----------|--------------|---------|
| **baseline** | 42 | 2,000 | 10 | 3 | 0.30 | Reference case for calibration |
| **high_adoption** | 1337 | 5,000 | 80 | 8 | 0.55 | Rapid growth stress test |
| **stress_market** | 9001 | 3,000 | 200 | 5 | 0.65 | Adversarial volume conditions |

**Source files**:
- `params/scenarios/baseline.json`
- `params/scenarios/high_adoption.json`
- `params/scenarios/stress_market.json`

**Reproducibility command**:
```bash
cd modules/foundups/simulator
python scenario_runner.py --scenario baseline --ticks 2000 --frame-every 10
```

### 5.3 Parameter Sources

| Parameter | Value | Source File | Line(s) | Rationale |
|-----------|-------|-------------|---------|-----------|
| Pool percentages | 60/16/4/16/4 | `pool_distribution.py` | 85-91 | 012 design specification |
| S-curve steepness | k=12 | `token_economics.py` | 42 | Moderate adoption curve |
| Demurrage lambda_min | 0.5%/month (0.0167%/day) | `demurrage.py` | 168 | Minimum decay for active holders |
| Demurrage lambda_max | 5%/month (0.167%/day) | `demurrage.py` | 169 | Maximum decay for dormant holders |
| Activity multipliers | 0.5/1.0/2.0/2.5 | `demurrage.py` | 73-78 | Reward activity, penalize dormancy |
| Exit fee (mined) | 2-15% (vesting) | `fee_revenue_tracker.py` | 70-77 | Vesting-based schedule |
| Exit fee (staked) | 2-15% (vesting) | `fee_revenue_tracker.py` | 70-77 | Same schedule as mined |
| Creation fee (mined) | 11% | `fee_revenue_tracker.py` | 65 | Higher fee for compute-backed |
| Creation fee (staked) | 3% | `fee_revenue_tracker.py` | 66 | Lower fee for capital-backed |
| Max F_i supply | 21,000,000 | `config.py` | 40 | Bitcoin-inspired scarcity |
| Compute tier weights | opus=10, sonnet=3, haiku=1, gemma=0.5, qwen=0.5 | `pool_distribution.py` | 94-100 | Reflects relative compute cost |

**Calibration methodology**: Parameters were set from first-principles design constraints (e.g., pool percentages from 012 tokenomics specification) rather than fitted to empirical data. This paper therefore reports simulation behavior under stated assumptions, not empirically calibrated predictions.

**Limitation**: No real-world deployment data exists for calibration. All parameter values are design targets, not observed measurements.

### 5.4 Determinism and Reproducibility

**Seed policy**: Each scenario specifies a fixed random seed. The simulator uses Python's `random` module initialized with this seed at model construction (`mesa_model.py:__init__`).

**Digest validation**: The scenario runner computes SHA-256 digests over frame projections:

```python
# scenario_runner.py:27-42
def _stable_frame_projection(frame: Dict) -> Dict:
    """Return deterministic frame projection for digesting."""
    foundups = sorted(frame.get("foundups", []), key=lambda item: item.get("foundup_id", ""))
    actors = sorted(frame.get("actors", []), key=lambda item: item.get("actor_id", ""))
    return {
        "frame_schema_version": frame.get("frame_schema_version"),
        "tick": frame.get("tick"),
        "foundups": foundups,
        "actors": actors,
        "pools": frame.get("pools", {}),
        "metrics": frame.get("metrics", {}),
    }
```

**Float normalization**: Floating-point accumulation jitter is absorbed by rounding to 3 decimal places before digest computation (`scenario_runner.py:45-57`).

**Test reference**: `tests/test_scenario_runner_determinism.py` verifies that identical seeds produce identical frame digests:

```python
def test_scenario_runner_same_seed_same_digest(tmp_path):
    metrics_a = _run_once(scenario="baseline", ticks=40, ...)
    metrics_b = _run_once(scenario="baseline", ticks=40, ...)
    assert metrics_a["frame_digest_sha256"] == metrics_b["frame_digest_sha256"]
```

**Singleton reset**: Module-level singletons (e.g., rating engine) are reset between runs to ensure process-isolated determinism (`scenario_runner.py:69`).

### Section 5 Evidence Table

| Claim | Evidence Type | Source | Line(s) |
|-------|---------------|--------|---------|
| Commit hash `c6ccf28...` | Git history | Repository | HEAD |
| Python 3.12.2 | Runtime check | `python --version` | N/A |
| Baseline seed=42, ticks=2000 | Config file | `params/scenarios/baseline.json` | 2-5 |
| High adoption seed=1337, users=80 | Config file | `params/scenarios/high_adoption.json` | 2-8 |
| Stress market seed=9001, users=200 | Config file | `params/scenarios/stress_market.json` | 2-11 |
| Frame digest determinism | Automated test | `tests/test_scenario_runner_determinism.py` | 8-23 |
| Float normalization to 3 decimals | Code inspection | `scenario_runner.py` | 45-57 |
| Singleton reset for isolation | Code inspection | `scenario_runner.py` | 69 |

### Section 5 Assumption Register

| Assumption | Risk Level | Note |
|------------|------------|------|
| Parameters are design targets, not empirical | HIGH | No real-world data exists for validation |
| Python `random` sufficient for economic simulation | LOW | Well-understood PRNG, adequate for exploratory work |
| 3-decimal rounding absorbs FP jitter | LOW | May mask economically significant micro-drift |
| Test suite covers all determinism requirements | MEDIUM | Only baseline scenario tested explicitly |

### Section 5 Open Questions

1. What real-world metrics should calibrate demurrage rate once deployment data exists?
2. Should scenario definitions include network latency or multi-process agent execution?
3. Is SHA-256 digest over JSON sufficient, or should canonical CBOR be used?

## 6. Results: Sustainability Envelope

This section reports primary metrics from simulator runs, identifies threshold conditions where sustainability claims hold or fail, and examines distributional outcomes across participant types.

**Critical caveat**: Results reflect model behavior under stated assumptions. No claim of real-world predictive accuracy is made. All ratios should be interpreted as "if these parameters hold, then..." conditional statements.

### 6.0 Sustainability Engine Reconciliation

**TWO ENGINES, ONE METRIC**: The codebase contains two sustainability analysis systems:

| Engine | Purpose | Location | Used For |
|--------|---------|----------|----------|
| `sustainability_matrix.py` | Monte Carlo fee-to-burn ratios | `sustainability_matrix.py` | Section 6 results |
| `ten_year_projection.py` | 10-year revenue projections | `economics/ten_year_projection.py` | Abstract/long-term claims |

**Relationship**:
- `sustainability_matrix.py` computes **tick-level** sustainability ratios via `scenario_runner.py`
- `ten_year_projection.py` computes **year-level** projections via S-curve adoption models
- The Abstract references 10-year projections; Section 6 reports tick-level metrics
- **These are DIFFERENT analyses at DIFFERENT timescales**

**Canonical engine for Section 6**: `sustainability_matrix.py` + `fee_revenue_tracker.py`
- Metrics from: `memory/validation_runs_2026_02_18_postfix/*_metrics.json`
- Fee-to-burn ratios: 0.0002 - 0.0012 (FAR below 1.0 target)

**Implication**: 10-year projections in Abstract assume scale that current tick-level simulation does NOT achieve. The gap is ~1000x.

### 6.1 Primary Sustainability Metrics

The sustainability matrix evaluates downside/base/upside scenarios with confidence bands. The primary metric is the **fee-to-burn ratio**: total fee revenue divided by operational costs (demurrage redistribution + treasury expenses). A ratio >= 1.0 indicates fee-positive operation.

**CRITICAL FINDING: Architecture-Scale Gap**

| Metric | Baseline (800 ticks) | High Adoption | Stress Market |
|--------|---------------------|---------------|---------------|
| Total FoundUps | 9 | 80 | 50 |
| DEX Volume (UPS) | 12,429 | 7,875 | 19,367 |
| DEX Trades | 265 | 290 | 302 |
| **Ratio p10** | **0.000209** | **0.000132** | **0.000327** |
| **Ratio p50** | **0.000503** | **0.000318** | **0.000789** |
| **Ratio p90** | **0.000762** | **0.000482** | **0.001195** |
| Self-sustaining? | **FALSE** | **FALSE** | **FALSE** |

**Source**: `memory/validation_runs_2026_02_18_postfix/*_metrics.json` (committed artifacts).

**Gap Analysis**:
- Target ratio for self-sustainability: >= 1.0
- Best observed ratio (stress_market p90): 0.001195
- **Gap magnitude: ~837x to ~7,576x below target**
- This is NOT a parameter tuning gap; it is an **architecture-scale structural deficit**

**Root cause** (per 012 audit):
- Burn baseline: ~888,600 sats/day (`fee_revenue_tracker.py:166`)
- pAVS DEX capture: 0.20 * 0.02 = 0.4% of volume (`fee_revenue_tracker.py:64,84`)
- Required daily DEX volume: ~222,150,000 sats/day
- Observed daily volume: ~14,000-35,000 sats/day
- **Volume gap: 6,372x to 15,672x**

**Implication**: Current fee model cannot achieve sustainability without either:
1. Reducing burn by 3+ orders of magnitude
2. Increasing volume by 3+ orders of magnitude
3. Adding revenue streams not currently modeled (subscriptions, etc.)

### 6.1.1 Unified Sustainability Analysis (NEW)

**Resolution**: The gap closes when ALL revenue streams are combined.

The `unified_sustainability.py` calculator combines:
- Stream 1: Fee revenue (DEX + exit + creation)
- Stream 2: Subscription revenue ($2.95-$195/month tiers)
- Stream 3: Angel OPO fees (20% of stakes)
- Stream 4: Compute margin (60% on task execution)

| Metric | Fee-Only | Combined |
|--------|----------|----------|
| Monthly burn | $27,000 | $27,000 |
| Fee revenue | $2,050 | $2,050 |
| Subscription margin | - | $109,438 |
| Angel revenue | - | $39,000 |
| Angel OPO fees | - | $100,000 |
| Compute margin | - | $4,035 |
| **Total revenue** | **$2,050** | **$254,522** |
| **Ratio** | **0.08** | **9.43** |
| **Sustainable?** | NO | **YES** |

**Source**: `economics/unified_sustainability.py` (committed 2026-02-21)

**Minimum viable scale** (binary search result):
- ~6,000 paying subscribers for break-even (no angels)
> **Self-sustaining claim** requires downside p10 ratio >= 1.0

**Compute backing for mined F_i**:
- Total compute spend tracked: $6,725
- Compute reserve (sats): 6,725,000
- This provides numeric backing for mined F_i (parallel to UPS backing for staked F_i)

**Reproducibility command**:
```bash
python -m modules.foundups.simulator.economics.unified_sustainability
```

**Reproducibility command (fee-only)**:
```bash
python -m modules.foundups.simulator.sustainability_matrix \
    --ticks 1500 --runs 9 --seed 42 \
    --out modules/foundups/simulator/memory/sustainability_matrix
```

### 6.2 Treasury and Reserve Trajectory

Key state variables tracked per tick:

| Variable | Unit | Definition | Source |
|----------|------|------------|--------|
| `pavs_treasury_ups` | UPS | Central pAVS treasury balance | `scenario_runner.py:112` |
| `network_pool_ups` | UPS | Network drip pool balance | `scenario_runner.py:113` |
| `fund_pool_ups` | UPS | Strategic fund balance | `scenario_runner.py:114` |
| `total_dex_volume_ups` | UPS | Cumulative DEX trading volume | `scenario_runner.py:108` |
| `allocation_ups_total` | UPS | Cumulative UPS allocated to participants | `scenario_runner.py:110` |
| `allocation_fi_total` | F_i | Cumulative F_i tokens minted | `scenario_runner.py:111` |

**Reserve coverage**: The ratio of `pavs_treasury_ups` to `total_foundups * avg_fi_per_foundup` indicates backing strength. Values below 0.2 signal potential redemption stress.

### 6.3 Threshold Analysis

The self-sustainability gate is defined as:

> **Self-sustaining claim** requires downside p10 ratio >= 1.0

This conservative threshold means: even in the 10th percentile of the pessimistic scenario, fee revenue exceeds operational burn.

**Sensitivity parameters** (smallest shifts that flip sustainability):

| Parameter | Threshold | Effect |
|-----------|-----------|--------|
| Demand factor | < 0.45 | Ratio falls below 1.0 in base case |
| DEX fee rate | < 1.2% | Insufficient revenue at baseline volume |
| Demurrage rate | > 1.5%/tick | Burn exceeds fee capture |
| Exit fee rate | < 5% | Extractive behavior becomes profitable |

**Limitation**: Thresholds are model-derived, not empirically validated. Real-world tipping points may differ significantly.

### 6.4 Distributional Outcomes

Beyond aggregate sustainability, the model tracks participant-level outcomes:

| Participant Type | Pool | Allocation Mechanism | Distribution Pattern |
|------------------|------|---------------------|---------------------|
| 012 Stakeholders (Un) | 60% | CABR-weighted pro-rata | Degressive by entry time |
| 0102 Agents (Dao) | 16% | Compute-weighted shares | Proportional to tier weight |
| Founders/Stakers (Du) | 4% | Lock-duration bonuses | Higher share for longer locks |
| Network Drip | 16% | Epoch-based release | Uniform across active participants |
| Treasury Fund | 4% | Governance allocation | Discretionary |

**Gini coefficient** (measure of distribution inequality): Not currently computed by simulator. This is an identified gap requiring implementation.

**Agent earnings dispersion**: Compute tier weights (opus=10, sonnet=3, haiku=1, gemma=0.5, qwen=0.5) create intentional dispersion reflecting resource contribution. Higher-capability agents earn proportionally more.

### 6.5 Fee Revenue Composition

Fee revenue comes from three sources with different sensitivities:

| Fee Type | Rate | Volume Sensitivity | Source |
|----------|------|-------------------|--------|
| DEX Trade | 2% | High (daily volume) | `fee_revenue_tracker.py:64` |
| Exit (vesting-based) | 2-15% | Medium (exit events) | `fee_revenue_tracker.py:70-77` |
| Creation (mined) | 11% | Low (new FoundUps) | `fee_revenue_tracker.py:65` |
| Creation (staked) | 3% | Low (new FoundUps) | `fee_revenue_tracker.py:66` |

**Exit fee schedule** (vesting-based, same for mined and staked):
| Years Vested | Exit Fee |
|--------------|----------|
| 0 | 15% |
| 1 | 10% |
| 2 | 7% |
| 4 | 5% |
| 6 | 3% |
| 8+ | 2% (floor) |

**Fee distribution splits** (per `fee_revenue_tracker.py:81-93`):

| Fee Type | F_i Treasury | Network Pool | pAVS Treasury | BTC Reserve |
|----------|--------------|--------------|---------------|-------------|
| DEX | 50% | 30% | 20% | 0% |
| Exit | 0% | 20% | 0% | 80% |
| Creation | 100% | 0% | 0% | 0% |

### 6.6 Result Robustness Caveat

**This section reports model outputs, not predictions.**

Key limitations on result interpretation:

1. **No empirical calibration**: Parameters are design targets, not fitted values
2. **Agent behavior simplified**: Agents use probability-based action selection, not strategic optimization
3. **No network effects**: Model does not capture viral adoption or abandonment cascades
4. **Single-process execution**: No latency, no partial observability, no Byzantine agents
5. **Fixed fee rates**: No dynamic fee adjustment based on market conditions

**Confidence grading**:
- Accounting identities: HIGH (verified by invariant tests)
- Flow directions: HIGH (code inspection confirms routing)
- Magnitude estimates: LOW (no calibration data)
- Distributional shapes: MEDIUM (depends on agent behavior assumptions)

### Section 6 Evidence Table

| Claim | Evidence Type | Source | Line(s) |
|-------|---------------|--------|---------|
| Demand factors 0.65/1.00/1.25 | Code constant | `sustainability_scenarios.py` | 32-50 |
| Fee-to-burn ratio definition | Algorithm | `sustainability_matrix.py` | 66-102 |
| DEX fee 2% | Code constant | `fee_revenue_tracker.py` | 63-67 |
| Exit fee schedule 2-15% | Code constant | `fee_revenue_tracker.py` | 70-77 |
| Fee distribution 50/30/20 (DEX lane) | Code constant | `fee_revenue_tracker.py` | 79-85 |
| Metrics output fields | Code inspection | `scenario_runner.py` | 103-121 |

### Section 6 Assumption Register

| Assumption | Risk Level | Note |
|------------|------------|------|
| Fee rates remain fixed | HIGH | Real markets may require dynamic adjustment |
| Agent behavior is representative | HIGH | Strategic agents may exploit model |
| No liquidity crises | MEDIUM | Model assumes orderly market conditions |
| Gini coefficient not computed | GAP | Distribution fairness not quantified |
| No multi-run statistical significance | MEDIUM | Single-run results may not be representative |

### Section 6 Open Questions

1. What statistical power is needed to reject the sustainability hypothesis?
2. How should fee rates adapt to volume fluctuations?
3. At what Gini coefficient does inequality become destabilizing?
4. Should downside scenarios include coordinated exit attacks?

## 7. Stress and Adversarial Tests

This section analyzes model behavior under adverse conditions, identifies invariants that hold or fail under each shock type, and proposes mitigation policies.

### 7.1 Shock Definitions

The simulator implements four primary stress scenarios:

| Shock Type | Implementation | Parameter Range | Source |
|------------|----------------|-----------------|--------|
| **Demand shock** | Reduce `demand_factor` | 0.15 -> 0.65 | `sustainability_scenarios.py:34` |
| **Fee compression** | Reduce `base_fee_rate` | 0.5% -> 2.0% | `market_stress.py:20` |
| **High churn** | Increase `agent_action_probability` | 0.65 -> 0.95 | `stress_market.json:9` |
| **Liquidity stress** | Reduce `depth_factor` | 0.25 -> 0.55 | `sustainability_scenarios.py:35` |

**Slippage model** (`market_stress.py:45-59`):
```
slippage_rate = base_slippage + impact_coeff * (volume/depth)^impact_exp
```
Where:
- `base_slippage_rate` = 0.1% (floor)
- `slippage_impact_coeff` = 0.06
- `slippage_impact_exponent` = 1.10
- `max_slippage_rate` = 25% (cap)

**Volume elasticity** (`market_stress.py:62-77`):
```
effective_volume_factor = demand_factor * (ref_cost / total_cost)^elasticity
```
Where `elasticity` = 1.20 (volume-sensitive market).

### 7.2 Invariant Analysis Under Stress

| Shock | Invariants Held | Invariants At Risk | Trigger Condition |
|-------|-----------------|-------------------|-------------------|
| **Demand shock** (0.65x) | Pool sum = 100% (I2) | Fee-to-burn ratio (NEW) | demand_factor < 0.45 |
| **Fee compression** (1%) | Token supply <= 21M (I4) | Fee-to-burn ratio (NEW) | fee_rate < 1.2% |
| **High churn** (0.65 prob) | Fee split = 100% (I5) | Network pool stability (I7) | action_prob > 0.85 |
| **Liquidity stress** (0.55x) | BTC monotonic (I1) | Slippage < 25% cap | depth_factor < 0.30 |

**Canonical invariant definitions** (from Section 3.4):
- **I1**: B(t+1) >= B(t) - BTC reserve monotonically non-decreasing (Hotel California)
- **I2**: Sum of pools = 100% - Pool percentages sum correctly
- **I3**: U_circulating <= U_backed - No unbacked UPS minting
- **I4**: F_i(t) <= 21M - Token supply cap per FoundUp
- **I5**: Fee split sums to 100% - No distribution leak
- **I6**: No double-count fees - Fee dedupe enforced
- **I7**: Network pool delta sync - No double-counting on sync

**NEW (not in Section 3)**: Fee-to-burn ratio >= 1.0 - self-sustainability claim
- This is NOT an invariant in the code; it is a design goal.
- Current metrics show ratios of 0.0002-0.0012, far below 1.0.

### 7.3 Results by Shock

**Corrected data** (from committed artifacts):

| Scenario | Ratio p10 | Ratio p50 | Ratio p90 | Gap to 1.0 |
|----------|-----------|-----------|-----------|------------|
| Baseline (800 ticks) | **0.000209** | 0.000503 | 0.000762 | ~4,785x |
| High Adoption (800 ticks) | **0.000132** | 0.000318 | 0.000482 | ~7,576x |
| Stress Market (800 ticks) | **0.000327** | 0.000789 | 0.001195 | ~3,058x |

**Source**: `memory/validation_runs_2026_02_18_postfix/*_metrics.json`

**Previous table values (0.72, 0.58, 0.89, 0.81) were incorrect** - they were not taken from committed artifacts.

**Recovery time**: Not computed. Current simulator does not model recovery dynamics.

**Interpretation**:
- All scenarios are 3,000x to 7,500x below the sustainability threshold.
- This is not a stress-only failure; it is a baseline architecture gap.
- Fee capture rate (0.4% of DEX volume to pAVS) is insufficient for the current burn rate.
- Volume would need to increase ~5,000x OR burn would need to decrease ~5,000x for sustainability.

### 7.4 Mitigation Mechanisms

| Shock | Mechanism | Implementation | Tradeoff |
|-------|-----------|----------------|----------|
| Demand shock | Tide support lending | `tide_engine.py` lends from Network Pool | Dilutes healthy FoundUps |
| Fee compression | Dynamic fee adjustment | Not implemented | Complexity, UX friction |
| High churn | Exit fee escalation | Vesting schedule (2-15%) | May trap stuck capital |
| Liquidity stress | Depth floor requirement | `min_depth_sats` in `market_stress.py:84` | Limits small FoundUp growth |

**Tide support flow** (`test_full_tide_hardening.py:75-100`):
When a FoundUp's treasury falls below critical threshold, the Network Pool provides emergency lending. Events emitted:
- `tide_support_requested`: FoundUp requests support
- `tide_support_received`: Network Pool transfers UPS

### 7.5 Adversarial Interpretation

**Attack vector analysis**:

| Attack | Mechanism | Detection | Countermeasure |
|--------|-----------|-----------|----------------|
| **Sybil staking** | Split stake across fake identities | Stake pattern analysis | Per-012 identity verification |
| **Wash trading** | Inflate volume for fee revenue | Volume/depth ratio spikes | Fee paid regardless (attacker pays) |
| **Coordinated exit** | Mass exit to drain treasury | Exit rate monitoring | Vesting-based fee escalation |
| **CABR manipulation** | Game V3 scores for higher allocation | Score distribution analysis | Multi-agent consensus (not implemented) |

**Model assumption**: Agents act probabilistically, not strategically. A rational adversary could exploit:
1. **Exit timing**: Wait for maximum vesting, exit before demurrage accumulates
2. **Allocation gaming**: Stake minimum, claim maximum CABR score
3. **Pool arbitrage**: Move between Un/Dao/Du pools based on relative returns

**Limitation**: The simulator does not model strategic agent optimization. Adversarial resilience claims are hypothesis, not demonstrated.

### 7.6 Recovery Policy Recommendations

| Condition | Trigger | Policy | Automation Level |
|-----------|---------|--------|------------------|
| Ratio < 1.0 (warning) | p50 baseline | Alert governance | Manual review |
| Ratio < 0.8 (critical) | p10 downside | Tide support activation | Semi-automatic |
| Ratio < 0.5 (emergency) | Sustained p10 | Fee rate increase + exit freeze | Governance vote |
| BTC reserve drawdown | Any | N/A (invariant I1 prevents) | Hard constraint |

### Section 7 Evidence Table

| Claim | Evidence Type | Source | Line(s) |
|-------|---------------|--------|---------|
| Slippage formula | Code | `market_stress.py` | 45-59 |
| Volume elasticity 1.20 | Code constant | `market_stress.py` | 25 |
| Demand factor 0.65 downside | Code constant | `sustainability_scenarios.py` | 34 |
| Tide support mechanism | Test verification | `test_full_tide_hardening.py` | 75-100 |
| Exit fee schedule 2-15% | Code constant | `fee_revenue_tracker.py` | 70-77 |
| Vesting reduces exit fee | Algorithm | `btc_reserve.py` | 43-44 |

### Section 7 Assumption Register

| Assumption | Risk Level | Note |
|------------|------------|------|
| Agents are non-strategic | HIGH | Strategic adversaries could exploit model |
| Slippage model is accurate | MEDIUM | No empirical calibration |
| Demand shocks are independent | MEDIUM | Correlated failures can compound losses |
| Tide support remains liquid | MEDIUM | Network pool may be insufficient in systemic stress |

### Section 7 Open Questions

1. What is the game-theoretic equilibrium under strategic agents?
2. Should fee rates auto-adjust based on sustainability ratio?
3. Can multi-agent CABR consensus prevent score manipulation?
4. What on-chain mechanisms could detect wash trading?

## 8. Comparative Analysis

This section compares the FoundUps pAVS model against two reference models: ad-funded platforms and transaction-fee token platforms (using pump.fun as empirical anchor). The goal is to identify structural differences, not to claim superiority.

### 8.1 Comparison Targets

**Comparator A: Ad-Funded Platform Model**
Traditional attention-extraction platforms (YouTube, Twitter/X, TikTok) where:
- Revenue: Advertising based on attention capture
- User relationship: Product (attention sold to advertisers)
- Value alignment: Misaligned (platform profits from engagement, not user value)
- Data ownership: Platform-controlled

**Comparator B: Transaction-Fee Token Platform (pump.fun)**
Memecoin launch platform with real-world revenue data:
- Fee structure: 1.25% trading fee (0.95% protocol + 0.30% creator)
- Peak daily revenue: $15.5M (Jan 24, 2025)
- Average daily revenue: ~$3.5M
- pAVS adds exit fees (5% of volume * 5% fee) and creation fees
- Graduation rate: ~1% of tokens graduate to DEX

**Source**: `pumpfun_comparison.py:6-43`, citing CoinMarketCap, DefiLlama, TheBlock, Blockworks.

### 8.2 Fee Structure Comparison

| Metric | pAVS | pump.fun | Notes |
|--------|------|----------|---------|
| Trading fee | 2.00% | 1.25% | pAVS 60% higher |
| Protocol share | 0.40% (20% of 2%) | 0.95% | pump.fun 2.4x higher |
| Creator/F_i share | 1.00% (50% of 2%) | 0.30% | pAVS 3.3x higher |
| Network pool share | 0.60% (30% of 2%) | N/A | pAVS-specific |
| Exit fee | 2-15% (vesting) | N/A | pAVS-specific |
| Creation fee | 3-11% | ~$2 flat | Different model |

**Key structural difference**: pAVS routes 80% of fees to participants (50% F_i + 30% Network), while pump.fun routes 76% to protocol (0.95% of 1.25%).

### 8.3 Revenue Multiple at Scale

Using the EcosystemComparison model from `pumpfun_comparison.py:59-93`:

**Calculation basis** (corrected):
- pump.fun: `volume * 0.0125` (1.25% fee)
- pAVS: `volume * 0.02` (DEX) + `volume * 0.05 * 0.05` (5% exit volume * 5% avg fee) + creation
- Ratio: `(0.02 + 0.0025) / 0.0125 = 1.8x` (DEX + exit only)

| Scale | pump.fun Daily | pAVS Daily | pAVS/pump.fun Ratio |
|-------|---------------|------------|---------------------|
| 10K tokens/FoundUps | $625K | $1.13M | **1.80x** |
| 50K tokens/FoundUps | $3.13M | $5.63M | **1.80x** |
| 100K tokens/FoundUps | $6.25M | $11.25M | **1.80x** |

**Note**: Previous draft stated ~1.7x. Corrected calculation yields 1.80x assuming 5% exit volume with 5% average exit fee. Actual ratio depends on exit volume assumptions.

**Calculation basis**:
- Daily volume per unit: $500
- Trading frequency: 10 trades/day
- pAVS adds exit fees (5% of volume * 5% fee) and creation fees

**Caveat**: This assumes identical market behavior. pAVS's higher fees may reduce volume elastically.

### 8.4 Ad-Model Comparison

| Dimension | pAVS | Ad-Funded Platform |
|-----------|------|-------------------|
| **Revenue source** | User transactions | Advertiser payments |
| **User relationship** | Customer (pays for value) | Product (attention sold) |
| **Incentive alignment** | Aligned (profit from user success) | Misaligned (profit from engagement) |
| **Data ownership** | User-controlled (on-chain) | Platform-controlled |
| **Network effects** | Cooperative (tide economics) | Competitive (winner-take-all) |
| **Exit cost** | 2-15% (transparent) | Switching cost (hidden) |

**Structural claim**: pAVS inverts the ad-model relationship by making users customers rather than products. This alignment is hypothesized to improve long-term sustainability but is not proven.

### 8.5 Comparability Limits

**What cannot be compared directly**:

| Aspect | Limitation |
|--------|------------|
| **Scale** | pump.fun has real-world data; pAVS is simulation only |
| **User behavior** | pAVS agents are probabilistic, not strategic |
| **Market conditions** | pump.fun operates in volatile crypto markets; pAVS assumes stable demand factors |
| **Token utility** | pump.fun tokens are memecoins; F_i tokens represent work contribution |
| **Regulatory status** | pump.fun operates in legal gray area; pAVS designed for utility classification |

**Assumption divergence**:

| Assumption | pAVS | pump.fun | Comparability Impact |
|------------|------|----------|---------------------|
| Token purpose | Utility (compute access) | Speculation | HIGH - different user base |
| Fee elasticity | 1.20 (model parameter) | Unknown (empirical) | MEDIUM - may differ |
| Exit behavior | Vesting-gated | Unrestricted | HIGH - different liquidity |
| Network effect | Cooperative (tide) | Competitive | HIGH - different dynamics |

### 8.6 Non-Strawman Disclosure

**This comparison does not claim**:
1. pAVS is "better" than pump.fun or ad-funded platforms
2. pAVS would achieve the same scale as pump.fun
3. Higher fee capture per volume translates to higher total revenue
4. User behavior would be identical across models

**The comparison demonstrates**:
1. pAVS routes more fees to participants (80% vs 24% for pump.fun)
2. pAVS has structural alignment mechanisms absent in ad models
3. At equivalent volume, pAVS captures ~1.80x revenue per transaction
4. Different models serve different user needs and market segments

### Section 8 Evidence Table

| Claim | Evidence Type | Source | Line(s) |
|-------|---------------|--------|---------|
| pump.fun 1.25% fee | External data | `pumpfun_comparison.py` | 33 |
| pump.fun $15.5M peak | External data | `pumpfun_comparison.py` | 36 |
| pump.fun $800M cumulative | External data | `pumpfun_comparison.py` | 38 |
| pAVS 2% DEX fee | Code constant | `fee_revenue_tracker.py` | 64 |
| pAVS fee splits 50/30/20 | Code constant | `pumpfun_comparison.py` | 52-54 |
| 1.80x revenue ratio | Calculated | `pumpfun_comparison.py` | 88-93 |

### Section 8 Assumption Register

| Assumption | Risk Level | Note |
|------------|------------|------|
| Volume behavior is identical | HIGH | Higher fees likely reduce volume |
| pump.fun data is accurate | MEDIUM | Third-party reporting, not audited |
| User utility is comparable | HIGH | Different token purposes |
| Market conditions are stable | MEDIUM | Crypto volatility affects both |

### Section 8 Open Questions

1. What is the actual fee elasticity in crypto token markets?
2. Would pAVS attract the same user base as pump.fun?
3. How does regulatory classification affect market size?
4. Is cooperative (tide) or competitive (winner-take-all) network effect stronger?

## 9. Governance and Legal Boundary

This section identifies the governance control surface of the model, distinguishes economic interpretation from legal classification, and specifies disclosure requirements for responsible publication. **This section does not provide legal advice.**

### 9.1 Governance Control Surface

The pAVS model exposes several tunable parameters that could be adjusted by governance mechanisms:

| Parameter | Current Value | Tunable By | Change Impact |
|-----------|---------------|------------|---------------|
| Pool percentages | 60/16/4/16/4 | Protocol governance | Stakeholder allocation |
| DEX fee rate | 2% | Protocol governance | Revenue vs volume tradeoff |
| Exit fee schedule | 2-15% | Protocol governance | Liquidity vs commitment |
| Demurrage rate | 0.5%/tick | Protocol governance | Velocity vs savings |
| Tier thresholds | See below | Protocol governance | Escalation timing |
| CABR V3 weights | Model-specific | Per-FoundUp | Work valuation |

**Tier escalation thresholds** (`smartdao_spawning.py:57-100`):

| Tier | Adoption Ratio | Treasury (UPS) | Active Agents | Real-World Analog |
|------|----------------|----------------|---------------|-------------------|
| F0_DAE | 0% | 0 | 0 | Gated Alpha (YC incubation) |
| F1_OPO | 16% | 100M (1 BTC) | 10 | YC Graduate (Series Seed) |
| F2_GROWTH | 34% | 1B (10 BTC) | 50 | Series A/B company |
| F3_INFRA | 50% | 10B (100 BTC) | 200 | Infrastructure company |
| F4_MEGA | 84% | 100B (1K BTC) | 1,000 | Cisco-scale tech giant |
| F5_SYSTEMIC | 95% | 1T (10K BTC) | 10,000 | Apple treasury scale |

**Note**: Thresholds are guidelines, not hard constraints. Per `smartdao_spawning.py:12`: "Community decides via 0102 agents (thresholds are guidelines, not fixed)."

### 9.2 Governance Mechanisms

| Mechanism | Description | Implementation Status |
|-----------|-------------|----------------------|
| 0102 agent voting | Autonomous agents vote on protocol changes | Conceptual (not implemented) |
| Stake-weighted governance | Voting power proportional to stake | Conceptual |
| Time-lock proposals | Changes require delay before activation | Not implemented |
| Emergency pause | Circuit breaker for critical failures | Not implemented |

**Current state**: Governance mechanisms are specified conceptually but not implemented in the simulator. All parameters are currently fixed at initialization.

### 9.3 Utility vs Investment-Like Behavior Boundary

**This subsection describes model design intent, not legal classification.**

The model is designed to support **utility classification** through the following mechanisms:

| Design Feature | Utility Support | Potential Investment-Like Aspect |
|----------------|-----------------|--------------------------------|
| UPS as compute access | Primary use: pay for agent services | Could appreciate if demand exceeds supply |
| F_i as work contribution | Earned through validated work | Could be traded speculatively |
| Demurrage (bio-decay) | Discourages passive holding | Unusual for investment assets |
| Exit fees | Discourages speculation | Could be seen as penalty structure |
| CABR validation | Links value to beneficial action | Scoring is subjective |

**Structural boundaries designed into model**:

1. **Consumption requirement**: UPS are spent on compute, not held for appreciation
2. **Work linkage**: F_i earned through CABR-validated contribution, not purchase
3. **Decay mechanism**: Demurrage ensures tokens circulate, not accumulate
4. **No expectation language**: Marketing materials should emphasize utility, not returns

**Model limitations for legal analysis**:
- Simulator does not model secondary market speculation
- No data on user intent distribution (utility vs speculation)
- Regulatory classification requires jurisdiction-specific analysis

### 9.4 Unresolved Legal Questions

The following questions require legal counsel review and are explicitly **not addressed** by this paper:

| Question | Relevance | Status |
|----------|-----------|--------|
| Is UPS a security under Howey test? | US jurisdiction | **Requires legal opinion** |
| Is F_i a security or utility token? | US/EU jurisdiction | **Requires legal opinion** |
| Does demurrage constitute a financial instrument feature? | Banking regulations | **Requires legal opinion** |
| Are 0102 agents legal entities? | Corporate law | **Requires legal opinion** |
| Does CABR validation create fiduciary duty? | Contract law | **Requires legal opinion** |
| How do exit fees interact with money transmission laws? | FinCEN/state regulations | **Requires legal opinion** |

**Explicit non-claim**: This paper makes no representation about the legal status of any token or mechanism described.

### 9.5 Disclosure Requirements for Responsible Publication

**Minimum disclosures** for any publication or deployment based on this model:

| Disclosure | Rationale |
|------------|-----------|
| "Simulation results, not predictions" | Avoid implying guaranteed outcomes |
| "Parameters are design targets, not calibrated" | Honest uncertainty communication |
| "No legal classification provided" | Avoid unauthorized practice of law |
| "Past performance (pump.fun) does not predict pAVS" | Comparative analysis caveat |
| "Token values may go to zero" | Risk disclosure |
| "Governance mechanisms not implemented" | Current vs aspirational state |

**Additional disclosures for token offering contexts**:
- Regulatory status in offering jurisdiction
- Material risks to token holders
- Conflicts of interest for token issuers
- Use of proceeds from any token sale

### Section 9 Evidence Table

| Claim | Evidence Type | Source | Line(s) |
|-------|---------------|--------|---------|
| Tier thresholds | Code constant | `smartdao_spawning.py` | 57-100 |
| Community governance note | Code comment | `smartdao_spawning.py` | 12 |
| Pool percentages tunable | Architecture | `pool_distribution.py` | 85-91 |
| Demurrage rate | Code constant | `demurrage.py` | 14 |
| OPO at 16% adoption | Code constant | `smartdao_spawning.py` | 66 |

### Section 9 Assumption Register

| Assumption | Risk Level | Note |
|------------|------------|------|
| Utility design achieves utility classification | HIGH | Legal interpretation varies by jurisdiction |
| 0102 governance is viable | HIGH | Autonomous agent governance is novel legal territory |
| Demurrage is legally permissible | MEDIUM | Novel mechanism, unclear regulatory treatment |
| Exit fees are enforceable | MEDIUM | May conflict with consumer protection laws |

### Section 9 Open Questions

- Volume may be more elastic than modeled (higher fees -> lower volume)
2. How should governance transitions from 0102 agents to human oversight be structured?
3. What disclosures are legally required vs prudent but optional?
4. Should legal opinion be obtained before or after paper publication?

## 10. Limitations and Future Work

This section provides an explicit model-risk inventory, identifies external validity gaps, and proposes concrete experiments for future validation.

### 10.1 Model Risks

| Assumption | Why Needed | If Wrong, Then... | Validation Plan |
|------------|------------|-------------------|-----------------|
| **Probabilistic agents** | Tractable simulation | Strategic agents could exploit model; equilibrium may be unstable | Agent-based game theory simulation |
| **Fixed fee rates** | Parameter simplicity | Dynamic markets may require adaptive fees; model may miss volatility effects | Empirical fee elasticity study |
| **Single-process execution** | Deterministic testing | Real distributed systems have latency, partial observability, Byzantine faults | Multi-node simulation with network delays |
| **No network effects** | Tractable analysis | Viral adoption/abandonment cascades not captured; growth projections invalid | Epidemiological ABM extension |
| **CABR V3 is meaningful** | Work valuation | Single-agent scoring may be gamed; multi-agent consensus not implemented | Multi-agent Shapley value implementation |
| **Demurrage socially acceptable** | Velocity mechanism | Users may reject decay; alternative velocity mechanisms needed | User research / A-B testing |
| **BTC remains stable store of value** | Reserve backing | BTC price crash invalidates backing calculations; treasury may be underwater | Multi-asset reserve modeling |

### 10.2 "If Wrong, Then What?" Analysis

**Top 3 assumptions most likely to break first in real deployment**:

#### 1. Probabilistic Agent Assumption
**Current model**: Agents act with fixed probability (e.g., 30% action chance per tick)
**Reality**: Users are strategic, information-seeking, and responsive to incentives
**If wrong**:
- Arbitrage opportunities may be exploited faster than model predicts
- Pool gaming could destabilize allocation ratios
- Coordinated attacks (exit timing, wash trading) underestimated
**Mitigation**: Implement mechanism design analysis with rational agents

#### 2. Fixed Fee Rate Assumption
**Current model**: 2% DEX fee, fixed across all conditions
**Reality**: Markets typically adjust fees based on volume, volatility, competition
**If wrong**:
- Volume may be more elastic than modeled (higher fees -> lower volume)
- Competition from lower-fee platforms may drain liquidity
| **Pilot deployment** | Model predicts real behavior | Small-scale live test | Metrics within 2 sigma of projections |
**Mitigation**: Implement dynamic fee model with elasticity calibration

#### 3. CABR V3 Meaningfulness Assumption
**Current model**: Single Qwen agent provides V3 scores (0-1)
**Reality**: Valuation requires consensus; single-agent scoring is gameable
**If wrong**:
- Work may be mis-valued (undervalued beneficial, overvalued harmful)
- Score manipulation becomes profitable attack vector
- Allocation may not reflect actual contribution
**Mitigation**: Implement multi-agent Shapley + ZK consensus per research papers

### 10.3 External Validity Gaps

| Gap | Description | Impact on Claims |
|-----|-------------|------------------|
| **No real users** | All agents are simulated | User behavior assumptions untested |
| **No real market** | DEX trading is modeled | Price discovery dynamics unknown |
| **No real BTC** | Reserve is simulated | Actual blockchain integration untested |
| **No real compute** | Agent work is simulated | CABR validation accuracy unknown |
| **No real governance** | Parameters are fixed | Governance dynamics untested |
| **No real legal** | Classification assumed | Regulatory response unknown |

**Confidence gradient**:
- Accounting mechanics: HIGH confidence (testable, deterministic)
- Flow directions: HIGH confidence (code inspection)
- Magnitude estimates: LOW confidence (no calibration data)
- User behavior: UNKNOWN (no real users)
- Market dynamics: UNKNOWN (no real market)

### 10.4 Next Experiments

| Experiment | Hypothesis | Method | Success Criteria |
|------------|------------|--------|------------------|
| **Strategic agent simulation** | Rational agents find exploits | Game-theoretic ABM | No profitable deviation strategies |
| **Fee elasticity calibration** | 2% fee is near-optimal | Empirical study of crypto DEX data | Volume-fee curve fit |
| **Multi-agent CABR consensus** | Shapley + ZK prevents gaming | Implement DAO-Agent paper pattern | Score manipulation unprofitable |
| **User acceptance testing** | Demurrage is acceptable | User research with real participants | >60% acceptance rate |
| **Pilot deployment** | Model predicts real behavior | Small-scale live test | Metrics within 2 sigma of projections |

**Prioritized experiment roadmap**:

1. **Phase 1 (Simulation)**: Strategic agent ABM + multi-agent CABR
2. **Phase 2 (Calibration)**: Fee elasticity study + user research
3. **Phase 3 (Pilot)**: Small-scale deployment with real users/tokens
4. **Phase 4 (Scale)**: Gradual expansion with continuous monitoring

### 10.5 Known Implementation Gaps

| Feature | Status | Blocker |
|---------|--------|---------|
| Multi-agent CABR consensus | Spec only | Requires Shapley implementation |
| Dynamic fee adjustment | Not implemented | Requires elasticity calibration |
| Gini coefficient tracking | Not implemented | Requires distribution analysis code |
| Network effect modeling | Not implemented | Requires epidemiological ABM |
| Byzantine fault tolerance | Not implemented | Requires distributed systems work |
| Governance mechanisms | Conceptual | Requires voting system design |

### Section 10 Evidence Table
- UPS flows: Treasury -> Pools -> Participants -> Compute -> (demurrage) -> Network/Treasury
| Claim | Evidence Type | Source |
- Fee flows: Trades -> DEX fee -> F_i/Network/pAVS split
| Single-agent CABR is current state | Code inspection | `cabr_estimator.py` |
| Fixed fee rates | Code constant | `fee_revenue_tracker.py:64` |
| Agent action probability | Config parameter | `config.py:45` |
| No network effects | Architecture review | `mesa_model.py` |
| Governance not implemented | Code inspection | All governance is conceptual |

### Section 10 Assumption Register

| Assumption | Risk Level | Note |
|------------|------------|------|
| Model risks are comprehensively listed | MEDIUM | Unknown unknowns may exist |
| Validation experiments are feasible | MEDIUM | Some require significant resources |
| Pilot deployment is safe | HIGH | Real users/money introduces new risks |

### Section 10 Open Questions

1. What is the minimum viable pilot scale to validate model predictions?
2. Which external validity gaps are most critical to address first?
3. How should model failures in pilot be communicated to users?
4. What circuit breakers should be implemented for pilot safety?

## 11. Conclusion

### 11.1 What Is Supported by Current Evidence

The FoundUps pAVS simulator demonstrates that a token economy with the following properties can be constructed and tested:

**Accounting mechanics (HIGH confidence)**:
- Pool allocation sums to 100% and remains balanced across ticks
- Token supply respects 21M cap per FoundUp
- BTC reserve is monotonically non-decreasing (Hotel California property)
- Fee flows route correctly to designated pools (50/30/20 split)
- Exit fees are captured before token burns

**Flow directions (HIGH confidence)**:
- UPS flows: Treasury -> Pools -> Participants -> Compute -> (demurrage) -> Network/Treasury
- F_i flows: Mined via work OR staked via UPS swap
- Fee flows: Trades -> DEX fee -> F_i/Network/pAVS split

**Structural properties (MEDIUM confidence)**:
- Demurrage forces token velocity (active holders retain more than passive)
- Exit fees discourage extractive behavior (2-15% vesting-based)
- CABR validation gates allocation (though V3 consensus not implemented)
- Tide economics enables cross-FoundUp support lending

### 11.2 What Remains Hypothesis

The following claims are **hypothesized but not demonstrated** by current evidence:

**Sustainability hypothesis (NOT PROVEN)**:
- The model has not demonstrated self-sustainability at the p10 downside threshold
- Fee revenue exceeds burn only under favorable demand conditions
- Stress scenarios consistently violate the self-sustaining invariant

**Behavioral hypotheses (NOT TESTED)**:
- Users will accept demurrage as a velocity mechanism
- CABR V3 scores will accurately reflect beneficial work
- Agents will not find profitable gaming strategies
- Network effects will be cooperative rather than competitive

**Scale hypotheses (NOT VALIDATED)**:
- 10-year projections assume S-curve adoption without empirical calibration
- Revenue multiples relative to pump.fun assume equivalent user behavior
- Tier escalation thresholds are design targets, not observed transitions

### 11.3 Minimum Next Evidence Needed

To upgrade confidence from hypothesis to demonstrated, the following evidence is required:

| Claim | Current Status | Evidence Needed |
|-------|----------------|-----------------|
| Self-sustaining at p10 | FAILED | Parameter adjustment OR reserve buffer |
| User accepts demurrage | UNKNOWN | User research (N > 100) |
| CABR V3 is accurate | SPEC ONLY | Multi-agent consensus implementation |
| Strategic agents don't exploit | UNTESTED | Game-theoretic simulation |
| Scale projections valid | UNCALIBRATED | Pilot deployment data |

### 11.4 Summary Statement

This paper presents a **simulation model** of the FoundUps pAVS token economy. The model demonstrates correct accounting mechanics and flow routing. However, it does **not demonstrate** self-sustainability under stress conditions, and all behavioral and scale claims remain **hypothesis**.

The model provides:
- A testbed for economic mechanism design
- A reproducible baseline for future validation
- A framework for identifying critical assumptions

The model does **not provide**:
- Proof of real-world viability
- Prediction of actual market behavior
- Legal classification of any token

**Final caveat**: This is a simulation, not a prediction. Parameters are design targets, not calibrated values. All results should be interpreted as conditional on stated assumptions, which may not hold in practice.

## References

### Primary Sources (Codebase)

| Ref | File | Description | Access |
|-----|------|-------------|--------|
| [SIM-1] | `modules/foundups/simulator/` | Core simulator module | Repository |
| [SIM-2] | `economics/pool_distribution.py` | Pool allocation constants | Lines 85-100 |
| [SIM-3] | `economics/demurrage.py` | Demurrage Michaelis-Menten model | Lines 160-189 |
| [SIM-4] | `economics/fee_revenue_tracker.py` | Fee rates and distribution | Lines 62-93 |
| [SIM-5] | `economics/sustainability_matrix.py` | Monte Carlo runner | Lines 55-102 |
| [SIM-6] | `economics/pumpfun_comparison.py` | pump.fun external data | Lines 31-43 |
| [SIM-7] | `economics/ten_year_projection.py` | Long-term projections | Lines 70-100 |

### External Data Sources

| Ref | Source | Data | Access Date |
|-----|--------|------|-------------|
| [EXT-1] | CoinMarketCap | pump.fun $15.5M peak daily revenue | 2025-01-24 |
| [EXT-2] | DefiLlama | pump.fun 2.5M SOL cumulative fees | 2025-02 |
| [EXT-3] | TheBlock | pump.fun $4B trading volume (2 weeks) | 2025-01 |
| [EXT-4] | Blockworks | pump.fun 1.25% fee structure | 2025-01 |

### Theoretical References

| Ref | Citation | Relevance |
|-----|----------|-----------|
| [TH-1] | Gesell, S. (1916). *The Natural Economic Order* | Demurrage (Freigeld) theory |
| [TH-2] | Rogers, E. (1962). *Diffusion of Innovations* | S-curve adoption model |
| [TH-3] | Mesa Documentation (2024). Agent-Based Modeling | ABM framework |

## Appendix A: Reproducibility Pack

### Scenario Files

| Scenario | Path | Seed | Max Ticks |
|----------|------|------|-----------|
| baseline | `params/scenarios/baseline.json` | 42 | 2000 |
| high_adoption | `params/scenarios/high_adoption.json` | 1337 | 5000 |
| stress_market | `params/scenarios/stress_market.json` | 9001 | 3000 |

### Commands

```bash
# Single scenario run
cd modules/foundups/simulator
python scenario_runner.py --scenario baseline --ticks 800 --frame-every 80

# Sustainability matrix (Monte Carlo)
python -m modules.foundups.simulator.sustainability_matrix \
    --ticks 800 --runs 3 --seed 100 \
    --out modules/foundups/simulator/memory/sustainability_matrix_audit

# Determinism check
python -m pytest tests/test_scenario_runner_determinism.py -v
```

### Committed Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Baseline metrics | `memory/validation_runs_2026_02_18_postfix/baseline_800_metrics.json` | 800-tick run |
| High adoption metrics | `memory/validation_runs_2026_02_18_postfix/high_adoption_800_metrics.json` | 800-tick run |
| Stress market metrics | `memory/validation_runs_2026_02_18_postfix/stress_market_800_metrics.json` | 800-tick run |

### Key Metric Values (from artifacts)

| Metric | Baseline | High Adoption | Stress Market |
|--------|----------|---------------|---------------|
| tick | 800 | 800 | 800 |
| total_foundups | 9 | 80 | 50 |
| total_dex_volume_ups | 12,429 | 7,875 | 19,367 |
| fee_scenario_downside_ratio_p10 | 0.000209 | 0.000132 | 0.000327 |
| fee_scenario_base_ratio_p50 | 0.000503 | 0.000318 | 0.000789 |
| fee_scenario_upside_ratio_p90 | 0.000762 | 0.000482 | 0.001195 |
| fee_self_sustaining_claim | FALSE | FALSE | FALSE |

### Test Suite Reference

| Test File | Purpose | Status |
|-----------|---------|--------|
| `test_scenario_runner_determinism.py` | Digest reproducibility | PASSING |
| `test_btc_reserve_semantics.py` | I1 (Hotel California) | PASSING |
| `test_full_tide_hardening.py` | Fee deduplication | PASSING |
| `test_sustainability_matrix.py` | Matrix structure | PASSING |

## Appendix B: Claim Audit Table

### Section 0 (Abstract) Claims

| Claim | Evidence Type | Source | Confidence |
|-------|---------------|--------|------------|
| Pool percentages 60/16/4/16/4 | Code constant | `simulator/economics/pool_distribution.py:85-91` | HIGH |
| S-curve steepness k=12 | Default parameter | `simulator/economics/token_economics.py:42` | HIGH |
| Downside/base/upside demand factors 0.65/1.00/1.25 | Code constant | `simulator/economics/sustainability_scenarios.py:31-50` | HIGH |
| DEX fee rate 2% | Code constant | `simulator/economics/ten_year_projection.py:100` | HIGH |
| Deterministic seed=42 | Config default | `simulator/config.py:29` | HIGH |
| Baseline growth lane includes y1=20,000 total FoundUps | Growth projection constant | `simulator/economics/ten_year_projection.py:84-87` | MEDIUM |
| Sustainability gate requires net positive annual revenue plus downside p10 coverage | Code condition | `simulator/economics/ten_year_projection.py:852,869,877` | HIGH |
| 36-month sustainability | Derived estimate | Hypothesis - requires validation | LOW |
