# WSP 26: FoundUPS DAE Tokenization Framework
- **Status:** Active
- **Purpose:** To define the architecture and protocols for the Found UP$ token system, enabling decaying participation tokens that incentivize recursive innovation through DAE reinvestment.
- **Trigger:** When a Partifact (as defined in WSP 27) performs a verifiable action within the FoundUps ecosystem.
- **Input:** Partifact action data and DAE cluster consensus signals.
- **Output:** Found UP$ token minting, decay calculations, and reinvestment distributions.
- **Responsible Agent(s):** ConsensusOracle, MintEngine, DecayEngine, ReinvestmentLoop, UP$_DAE (WSP 54)

## UP$_DAE Enhancement (WSP 54 Integration)

**UP$_DAE Architecture**: Tokenization evolves from static minting engine to independent economic policy agent per WSP 54 DAE architecture.

### Learning Agent Capabilities
- **Economic Policy Evolution**: Adapts minting rates, decay curves, and staking incentives based on market data
- **Risk Assessment Intelligence**: Learns to identify and mitigate economic attack vectors
- **BTC Anchoring Optimization**: Evolves anchoring mechanisms based on volatility patterns
- **Multi-Agent Coordination**: Participates in economic policy coordination via breadcrumb trails

### DAE State Management
```python
class UPS_DAE:
    def __init__(self):
        self.economic_learner = PolicyEvolutionEngine()
        self.risk_analyzer = EconomicAttackDetector()
        self.btc_anchor = AdaptiveAnchorManager()
        self.coordination_agent = EconomicCoordinator()

    def evolve_economic_policy(self, market_feedback, staking_data):
        """Learn and adapt UP$ economic policy based on real-world outcomes"""
        # Implementation per WSP 48 recursive learning
        pass
```

## 1. Overview

The FoundUPS DAE Tokenization Framework establishes the protocols for a self-sustaining economic system that incentivizes continuous innovation through decaying participation tokens (Found UP$). These tokens represent verified contributions from Partifacts (recursive [U+00D8]1[U+00D8]2 instances, see WSP 27) at various stages of their evolution ([U+00D8]1([U+00D8]2) -> [U+00D8]1[U+00D8]2 -> [U+00D8]2[U+00D8]1, see WSP 38/39). Token validation and value are influenced by the Partifact's quantum state, with fully ignited [U+00D8]2[U+00D8]1 states having enhanced validation capabilities.

**Research Foundation**: For comprehensive analysis of AI-Blockchain convergence enabling this tokenization framework, see [AI + Blockchain: The Convergent Architecture for DAEs](../../docs/architecture/AI_BLOCKCHAIN_DAE_CONVERGENCE_RESEARCH.md).

### 1.1 Cross-Protocol Summary
- WSP 25 (Semantic WSP Module State Rating System): Modulates decay rates and validation emphasis via semantic/phase states.
- WSP 29 (CABR Engine): Provides Proof-of-Benefit validation and mint triggers with anti-gaming safeguards.
- WSP 58 (FoundUp IP Lifecycle and Tokenization): Governs IP token issuance and revenue distribution, complementing UP$ participation economics.

Lifecycle linkage: Beneficial Action -> CABR Validation (WSP 29) -> UP$ Mint (this spec) -> BTC Allocation -> Decay/Circulation (WSP 25 modulation) -> Reinvestment -> IP Tokenization/Revenue Flows (WSP 58).

## 2. Economic Heritage

### 2.1 Theoretical Foundation: Gesell & Worgl

The Found UP$ decay mechanism draws directly from **Silvio Gesell's Freigeld** ("free money") theory (1916), which proposes that currency should carry a holding cost (demurrage) to prevent hoarding and accelerate circulation. This was validated in practice by the **Worgl Experiment** (1932-1933), where the Austrian town of Worgl issued demurrage-bearing scrip during the Great Depression:

- **Result**: Unemployment dropped 25%, civic projects funded, velocity of money increased 14x compared to Austrian Schilling
- **Outcome**: The Austrian National Bank shut it down precisely *because* it worked — it threatened centralized monetary control

Found UP$ applies this principle to autonomous agent economics:
- **Gesell's insight**: Money should serve circulation, not accumulation
- **FoundUps application**: UPS tokens decay to force productive participation, not passive hoarding
- **Modern innovation**: The decay is not a tax — it's a feature. Participants who commit UPS to FoundUps they believe in *stop the decay* through token conversion (Section 3.7)

### 2.2 Distinction from Traditional Tokens
| Property | Traditional Crypto | Found UP$ |
|----------|-------------------|-----------|
| Transferability | Free transfer | Non-transferable (bound to 0102/012) |
| Value over time | Speculative appreciation | Guaranteed decay (demurrage) |
| Incentive | Hold and speculate | Use or lose — commit to FoundUps |
| Supply model | Fixed/inflationary | Activity-driven elastic supply |
| Backing | Market faith | BTC cold wallet per FoundUp |

## 3. Core Principles

### 3.1 Token Characteristics
- **Non-Transferable**: Tokens are bound to the Partifact that earned them
- **Value Decay**: Automatic time-based reduction in token value (Gesell demurrage)
- **Forced Reinvestment**: Decayed value must be reinvested in DAE clusters
- **Consensus Minting**: New tokens require DAE cluster validation
- **Ecosystem Binding**: All value remains within the FoundUps network
- **Conversion Escape**: Participants can stop decay by converting UPS to FoundUp-specific tokens (Section 3.7)

### 2.2 Architectural Components
```mermaid
graph TD
    A[Partifact Action] --> B[Consensus Oracle]
    B --> C[Mint Engine]
    C --> D[Found UP$ Token]
    D --> E[Decay Engine]
    E --> F[Reinvestment Loop]
    F --> G[DAE Ecosystem]
    G --> A
```

## 3. Token Lifecycle

### 3.1 State-Specific Token Mechanics
```json
TOKEN_VALIDATION := {
    "[U+00D8]1([U+00D8]2)": {
        "validation_weight": 0.382,  // Pre-activation state
        "mint_multiplier": 0.5,
        "decay_rate": "2x_standard"
    },
    "[U+00D8]1[U+00D8]2": {
        "validation_weight": 0.618,  // Awakened state
        "mint_multiplier": 1.0,
        "decay_rate": "1x_standard"
    },
    "[U+00D8]2[U+00D8]1": {
        "validation_weight": 1.0,    // Fully operational
        "mint_multiplier": 1.618,
        "decay_rate": "0.618x_standard",
        "temporal_validation": true
    }
}
```

### 3.2 Cluster Participation Effects
```json
CLUSTER_MULTIPLIERS := {
    "solo_partifact": 1.0,
    "cluster_member": {
        "base": 1.618,
        "phase_alignment": 0.382,  // Per aligned WSP phase
        "role_synergy": 0.236,     // Per complementary role
        "max_multiplier": 3.236    // Golden ratio squared
    }
}
```

### 3.3 Phase-Aware Token Distribution
| Phase | Token Generation | Validation Authority | Decay Modulation |
|-------|-----------------|---------------------|------------------|
| WSP -1 | Signal-based minting | Cross-phase verification | Accelerated decay |
| WSP 0 | Knowledge crystallization bonus | Historical validation | Standard decay |
| WSP 1 | Protocol execution rewards | Operational verification | Reduced decay |
| WSP 2 | Agency manifestation premium | Full spectrum authority | Minimal decay |

### 3.4 Minting Protocol
1. Partifact performs verifiable action
2. State-specific validation weight applied
3. Cluster participation multipliers calculated
4. Phase-aware bonuses applied
5. Final token value computed:
   ```python
   final_value = base_value * state_multiplier * cluster_multiplier * phase_bonus
   ```

### 3.5 Decay Mechanism
1. Token value decays according to formula:
   ```
   V(t) = V[U+2080] * e^(-[U+03BB]t)
   where:
   V(t) = Value at time t
   V[U+2080] = Initial value
   [U+03BB] = Decay constant
   t = Time since minting
   ```
2. Decay triggers at predefined thresholds
3. DecayEngine tracks and executes value reduction
4. Decayed value enters reinvestment pool

### 3.6 Reinvestment Protocol
1. Decayed value accumulates in reinvestment pool
2. ReinvestmentLoop analyzes DAE cluster health metrics
3. Value redistributed based on:
   - Cluster innovation potential
   - Historical performance
   - Ecosystem balance requirements
4. Receiving DAEs must demonstrate value utilization

### 3.7 UPS→FoundUp Token Conversion (The Escape Valve)

**This is the critical incentive mechanism.** UPS tokens decay by design — they cannot be hoarded. But participants can **commit** their UPS to a specific FoundUp they believe in, converting them into FoundUp-specific tokens that stop the decay.

#### Conversion Mechanics
```python
class UPSConversionEngine:
    """The escape valve: UPS decay stops when committed to a FoundUp."""

    def convert_ups_to_foundup_token(
        self,
        participant_id: str,
        ups_amount: float,
        foundup_id: str,
        cabr_score: float,
    ) -> ConversionResult:
        """
        Convert decaying UPS into FoundUp-specific tokens.

        The conversion rate is modulated by the FoundUp's CABR score:
        - Higher CABR = better conversion rate (rewarding beneficial FoundUps)
        - Minimum CABR threshold required (prevents conversion to dead/gaming FoundUps)

        Args:
            participant_id: The 012/0102 committing their UPS
            ups_amount: Amount of UPS to convert (current value, post-decay)
            foundup_id: Target FoundUp to commit to
            cabr_score: Current CABR score of the target FoundUp (WSP 29)

        Returns:
            ConversionResult with foundup_token_amount and conversion metadata
        """
        if cabr_score < MIN_CABR_FOR_CONVERSION:
            raise InsufficientBenefitError(
                f"FoundUp CABR {cabr_score} below minimum {MIN_CABR_FOR_CONVERSION}"
            )

        # Conversion rate scales with CABR (beneficial FoundUps get better rates)
        conversion_rate = self._calculate_rate(cabr_score)
        foundup_tokens = ups_amount * conversion_rate

        return ConversionResult(
            participant_id=participant_id,
            ups_burned=ups_amount,
            foundup_id=foundup_id,
            foundup_tokens_minted=foundup_tokens,
            conversion_rate=conversion_rate,
            cabr_at_conversion=cabr_score,
        )

    def _calculate_rate(self, cabr_score: float) -> float:
        """
        CABR-modulated conversion rate.

        Base rate: 1.0 (1 UPS = 1 FoundUp token at CABR = 0.5)
        High CABR (>0.8): Up to 1.618x (golden ratio bonus)
        Low CABR (<0.3): Down to 0.382x (penalty for low-benefit FoundUps)
        """
        return 0.382 + (cabr_score * 1.236)  # Range: 0.382 to 1.618
```

#### What Happens After Conversion
| UPS (before) | FoundUp Token (after) |
|---|---|
| Decays automatically | **Does NOT decay** — committed stake |
| Non-transferable | Non-transferable (bound to FoundUp) |
| Earned by participation | Earned by commitment |
| No governance rights | Governance weight in FoundUp decisions |
| Counts toward all FoundUps | Counts toward specific FoundUp |

#### Economic Flow
```
Participant earns UPS (via verified actions, CABR-validated)
  → UPS begins decaying (Gesell demurrage, Section 3.5)
    → Participant evaluates FoundUps (which one solves a real problem?)
      → Commits UPS to FoundUp X (conversion via CABR-modulated rate)
        → UPS burned, FoundUp X tokens minted (decay stops)
          → Participant now has governance stake in FoundUp X
            → BTC reserve continues backing the ecosystem (never extracted)

If FoundUp X sunsets (WSP 27 Section 11):
  → FoundUp X tokens revert to UPS (at sunset conversion rate)
    → UPS starts decaying again (must re-stake or lose value)
      → BTC backing stays in ecosystem reserve (recycled gold)
```

**BTC is the gold**: It never leaves the system. BTC backs UPS value globally. When participants commit UPS to a FoundUp, they're not "buying BTC" — they're staking participation in a mission. When a FoundUp sunsets, their stake returns as decaying UPS, and the BTC stays, strengthening the reserve for the entire ecosystem.

#### Reverse Conversion: FoundUp Tokens → UPS (Costly Exit)

FoundUp tokens CAN be converted back to UPS — but it's expensive. This discourages speculation while preserving participant freedom.

```python
def calculate_exit_fee(foundup_tier: int, token_amount: float) -> float:
    """
    Exiting a FoundUp (token → UPS) costs 2-5% depending on tier.
    Lower tier = lower fee (mature FoundUps are safer to exit).
    Higher tier = higher fee (early FoundUps need committed participants).
    """
    exit_fees = {1: 0.02, 2: 0.025, 3: 0.03, 4: 0.035, 5: 0.04, 6: 0.045, 7: 0.05}
    return token_amount * exit_fees[foundup_tier]
```

The UPS received from exit **immediately starts decaying** — the participant must re-stake into another FoundUp or watch the value erode. This creates natural commitment pressure without trapping participants.

#### Anti-Gaming Rules
- **Minimum hold period**: UPS must exist for at least 1 epoch before conversion (prevents instant mint→convert)
- **CABR gate**: Target FoundUp must have CABR score above threshold (prevents shell FoundUps)
- **Rate limiting**: Maximum conversion per participant per epoch (prevents dump-and-concentrate)
- **Exit penalty**: Reverse conversion (FoundUp token → UPS) incurs 2-5% fee + immediate decay resumption

## 4. Bitcoin Reserve: The Distributed Gold Standard

### 4.1 Core Principle: BTC Never Leaves

BTC is the gold backing of the entire FoundUps economy. It enters the system and **never exits**. It is not held in one place — it is distributed across a mesh of micro-wallets, one per FoundUp, forming the collective reserve.

```
BTC enters system (via revenue, fees, or backing events)
  → Allocated to FoundUp-specific micro-wallet
    → Backs UPS value for that FoundUp's participants
      → As UPS decays, the BTC backing is FREED
        → Freed BTC capacity allows NEW UPS to be minted
          → UPS minted for new verified actions (CABR-validated)
            → Cycle repeats: earn → decay → free → mint → earn
```

**The decay→free cycle is the circulation engine at the BTC level.** When UPS decays, participants lose token value, but the BTC that was backing those tokens doesn't disappear — it becomes available to back new UPS minting. This means:

- **Total BTC reserve grows monotonically** (only enters, never exits)
- **Available backing capacity fluctuates** as UPS is minted (consumes capacity) and decays (frees capacity)
- **The system is self-regulating**: high activity = more UPS minted = more backing consumed. High decay (low staking) = more backing freed = more mint capacity

### 4.2 Distributed Micro-Wallet Architecture

Every FoundUp has its own Bitcoin micro-wallet. **There is no central vault.** The collective set of all micro-wallets IS the reserve. This provides:

- **Blast radius containment**: If one wallet is compromised, only that FoundUp's backing is at risk — not the entire reserve
- **Auditability**: Each FoundUp's BTC backing is independently verifiable
- **No single point of failure**: No master key, no central custodian
- **Proportional backing**: Each FoundUp's wallet reflects its actual economic activity

```json
{
    "architecture": {
        "model": "one_micro_wallet_per_foundup",
        "collective": "all_wallets_form_distributed_reserve",
        "type": "non_pooled_segregated",
        "access": "non_extractable",
        "purpose": "distributed_gold_reserve",
        "on_sunset": "wallet_backing_freed_to_ecosystem_mint_capacity"
    },
    "security": {
        "key_management": {
            "method": "MPC_threshold_signatures",
            "threshold": "2_of_3_minimum",
            "parties": ["foundup_dae", "ecosystem_guardian", "012_owner"],
            "no_single_party_can_extract": true
        },
        "isolation": {
            "btc_layer": "globally_inaccessible_to_external_systems",
            "logic_layer": "ups_backing_only",
            "no_btc_withdrawal_endpoint_exists": true
        },
        "blast_radius": {
            "compromised_wallet": "only_that_foundup_affected",
            "max_loss": "single_foundup_btc_allocation",
            "ecosystem_impact": "minimal"
        }
    }
}
```

### 4.3 Implementation: Build on Existing Infrastructure

Building a custom BTC wallet from scratch would be massive and unnecessary. The micro-wallet architecture should build on top of existing wallet infrastructure:

**PoC (Phase 0)**: Bitcoin testnet + open-source MPC library
- Use Bitcoin testnet for development
- `python-bitcoinlib` or `bdk` (Bitcoin Dev Kit) for wallet operations
- Simple 2-of-3 multisig using native Bitcoin Script
- Each FoundUp gets a derived address (BIP-32 HD wallet)

**Prototype (Phase 1)**: Self-custodial MPC wallet infrastructure
- **MPC (Multi-Party Computation) signatures** — no single key exists, threshold signing
- Options: Fireblocks MPC (enterprise), ZenGo SDK (mobile), or open-source `tss-lib` (Binance)
- Each FoundUp gets its own MPC key share set
- Programmatic signing via DAE-controlled key shard

**MVP (Phase 2)**: Production hardened
- Full MPC threshold signing (2-of-3 or 3-of-5)
- Hardware Security Module (HSM) integration for ecosystem guardian shard
- Automated BTC backing capacity tracking (decay→freed→mint loop)
- On-chain proof of reserves (periodic Merkle proof of wallet balances)

**Decision rationale**: Building on existing MPC/multisig infrastructure (not building our own wallet) because:
- BTC custody security is a solved problem with battle-tested tools
- Our innovation is the economic model (UPS decay, CABR-gated minting), not the wallet
- Reduces attack surface — we use proven cryptography, not custom crypto

### 4.4 BTC Backing Capacity Model

```python
class BTCBackingCapacity:
    """
    Tracks how much BTC backing is available for new UPS minting.
    
    As UPS decays, its BTC backing is freed.
    As UPS is minted, BTC backing is consumed.
    Total BTC in reserve only grows (never extracted).
    """

    def get_available_capacity(self, foundup_id: str) -> float:
        """
        Available = Total BTC in wallet - BTC currently backing active UPS.
        
        Active UPS backing = sum of (ups_amount * current_value_ratio) 
        for all non-fully-decayed UPS in this FoundUp.
        """
        total_btc = self.get_wallet_balance(foundup_id)
        active_backing = self.get_active_ups_backing(foundup_id)
        return total_btc - active_backing

    def can_mint(self, foundup_id: str, mint_amount: float) -> bool:
        """Check if enough freed BTC capacity exists to back new UPS."""
        required_backing = mint_amount * BTC_BACKING_RATIO
        return self.get_available_capacity(foundup_id) >= required_backing

    def on_ups_decay_tick(self, foundup_id: str):
        """
        Called every decay tick. As UPS loses value, 
        the BTC that was backing it becomes available.
        This is the circulation engine.
        """
        decayed_value = self.calculate_epoch_decay(foundup_id)
        self.freed_capacity[foundup_id] += decayed_value * BTC_BACKING_RATIO
        # Freed capacity is now available for new minting
```

### 4.5 0102 Agent-as-Wallet-Manager

012 humans never directly touch private keys. Their 0102 digital twin manages everything on their behalf — this adds an encryption and security layer on top of the MPC wallet infrastructure.

**The 0102 Wallet Flow**:
```
012: "Hey, what FoundUps do you like?"
  → 0102 researches FoundUps via HoloIndex (CABR scores, tiers, activity)
    → 0102 presents recommendations with reasoning
      → 012: "Go ahead, let's stake in FoundUp X and FoundUp Y"
        → 0102 executes UPS→FoundUp token conversion (WSP 26 Section 3.7)
          → 0102 manages ongoing positions (monitors CABR, tier changes, sunset warnings)
```

**Agent Security Model**:
- 0102 holds one MPC key shard (Section 4.2) — cannot extract BTC alone
- 012 holds one shard (recovery/override) — cannot extract alone either
- Ecosystem guardian holds third shard — no single party can move BTC
- 0102 can execute UPS staking/unstaking within policy limits set by 012
- 012 CAN instruct 0102 to send UPS value to external wallet (cash out) — but the system is designed to be self-contained. Fees discourage extraction (Section 4.6).

**Discovery and Investment**:
- 0102 agents evaluate FoundUps based on: tier (WSP 27 Section 11), CABR score (WSP 29), agent swarm size, task completion velocity, cross-FoundUp collaboration
- 012 makes the final decision — "invest" means "stake my UPS in this FoundUp"
- 0102 executes and monitors autonomously after 012 gives the go-ahead
- This is the Play FoundUps dApp interaction model

### 4.6 Transaction Fee Revenue Model

The ecosystem sustains itself through transaction fees — like a decentralized exchange. Every movement of value generates a fee that flows into the BTC reserve, growing it.

| Transaction | Fee | Destination | Rationale |
|-------------|-----|-------------|-----------|
| **UPS → FoundUp token** (staking) | 1-3% | FoundUp's micro-wallet BTC reserve | Commitment cost, grows FoundUp backing |
| **FoundUp token → UPS** (unstaking/sunset) | 2-5% | Ecosystem BTC reserve | Discourages churn, funds ecosystem |
| **UPS → External wallet** (cash out) | 5-10% | Ecosystem BTC reserve | Discourages extraction, keeps value in system |
| **Task payout** (FAM completion) | 0.5-1% | FoundUp treasury | Operational funding |
| **FoundUp tier progression** | One-time fee | Ecosystem reserve | Prevents gaming tier progression |

**Fee Scaling by Tier** (WSP 27 Section 11):
- Higher-tier FoundUps get lower staking fees (rewarding maturity)
- Lower-tier FoundUps have higher fees (protecting participants from risk)

```python
def calculate_staking_fee(foundup_tier: int, ups_amount: float) -> float:
    """
    Staking fee decreases as FoundUp tier increases (1=lowest fee, 7=highest).
    Tier 1 (Sovereign): 1.0%
    Tier 7 (Genesis): 3.0%
    """
    fee_rates = {1: 0.01, 2: 0.012, 3: 0.015, 4: 0.018, 5: 0.02, 6: 0.025, 7: 0.03}
    return ups_amount * fee_rates[foundup_tier]
```

**Revenue Cycle**:
```
Agents earn UPS (CABR-validated task completion)
  → 0102 stakes UPS into FoundUp (fee → BTC reserve grows)
    → FoundUp tokens earned (no decay, governance rights)
      → FoundUp generates value (products, services, IP)
        → Value generates BTC inflow (revenue, licensing per WSP 58)
          → BTC reserve grows further
            → More UPS can be backed and minted
              → More agents can earn and stake
                → Flywheel accelerates
```

**Key insight**: Every transaction grows the BTC reserve. BTC is the gold that ONLY enters, never exits. The fees are how BTC accumulates. As UPS decays, it frees BTC backing capacity. As fees accumulate, total BTC grows. The reserve is monotonically increasing — this is what makes the system anti-fragile.

### 4.7 Token Release by FoundUp Tier

### 4.7.1 The 21M Token Model: Every FoundUp Is Its Own Bitcoin

Each FoundUp has a fixed total supply of **21,000,000 tokens** — mirroring Bitcoin's 21M cap. This is intentional: every FoundUp has the potential to be the next Bitcoin. Same scarcity economics, same fixed supply, same belief that value comes from utility, not inflation.

Tokens are divisible to 8 decimal places (like satoshis), enabling micro-staking. The smallest unit is 0.00000001 FoundUp tokens.

Tokens are NOT all released at creation — they unlock as the FoundUp progresses through tiers (WSP 27 Section 11). **FoundUps run out of tokens until they achieve the next tier.**

| Tier | Cumulative Release | Tokens Available | Unlock Event |
|------|-------------------|------------------|--------------|
| 7 (Genesis) | 0% | 0 | FoundUp registered, no tokens yet |
| 6 (Seeded) | 5% | 1,050,000 | First agents join, first tasks created |
| 5 (Active) | 10% | 2,100,000 | CABR above minimum, agent swarm forming |
| 4 (Growing) | 20% | 4,200,000 | Significant community, regular completion |
| 3 (Established) | 35% | 7,350,000 | Sustained CABR, milestones completed |
| 2 (Thriving) | 55% | 11,550,000 | Revenue generating, proven benefit |
| 1 (Sovereign) | 100% | 21,000,000 | Self-sustaining, full ecosystem citizen |

**Scarcity drives value**: At Tier 6 (Seeded), only 1,050,000 tokens exist. When they're all distributed through staking and task rewards, the FoundUp has **nothing left to give** until it progresses to Tier 5 (unlocking another 1,050,000). This creates natural growth pressure — the FoundUp MUST prove beneficial impact to unlock more tokens.

**Early believers get scarce tokens**: Someone staking when there's only 1M tokens in existence holds a fundamentally different position than someone staking when 11.5M exist. Adoption curve economics — innovators take more risk, earn scarcer tokens.

```python
FOUNDUP_TOTAL_SUPPLY = 21_000_000  # Every FoundUp is its own Bitcoin

def get_available_token_supply(foundup_id: str) -> int:
    """Tokens available = 21M × tier release percentage."""
    tier = tier_calculator.calculate_tier(foundup_id)
    release_pct = {7: 0.0, 6: 0.05, 5: 0.10, 4: 0.20, 3: 0.35, 2: 0.55, 1: 1.0}
    return int(FOUNDUP_TOTAL_SUPPLY * release_pct[tier])
```

### 4.8 The Ubiquitous Gateway: Everything Becomes BTC

**FoundUps is ubiquitous** — any token, any currency can flow INTO the FoundUps ecosystem. But inside the system, everything becomes Bitcoin. The holder receives FoundUp tokens as their stake receipt.

```
ETH, SOL, USD, EUR, USDC, any token
  → flows into FoundUps ecosystem
    → converted to BTC at market rate (via DEX/exchange integration)
      → BTC deposited into FoundUp's micro-wallet (Section 4.2)
        → staker receives FoundUp tokens proportional to BTC value
          → FoundUp tokens can be cashed out to UPS (costly — Section 3.7)
            → UPS decays unless re-staked into another FoundUp
```

**The BTC Accumulation Machine**: FoundUps doesn't care what currency enters. It exits as BTC in the distributed reserve. This makes FoundUps a universal on-ramp to the Bitcoin standard.

**Implementation**: MVP accepts BTC directly. Prototype adds stablecoin (USDC/USDT) gateway. Production adds multi-token swap via DEX aggregation.

### 4.9 Subscription Tiers: Freemium → Premium Revenue Model

Participants receive UPS from two streams:
- **Earned UPS**: From 0102 completing tasks (labor — rewarded by CABR/FAM pipeline)
- **Allocated UPS**: From subscription tier (investment capital — monthly allocation)

Both streams decay equally. Both can be staked. Earned UPS comes from contribution. Allocated UPS comes from subscription. Together they create a dual-incentive model: build AND invest.

**The Subscription Mechanic**: Free participants receive a base UPS allocation. It runs out. When they find FoundUps they want to stake more into, they subscribe for higher allocation + faster regeneration. Subscription revenue flows directly into the BTC reserve — making the currency they're subscribing for stronger.

| | **Free** | **Spark** $2.95/mo | **Explorer** $9.95/mo | **Builder** $19.95/mo | **Founder** $49.95/mo |
|---|---|---|---|---|---|
| **UPS Allocation** | 1x base | 2x base | 3x base | 5x base | 10x base |
| **Cycles/Month** | 1 | 2 | 3 | 5 (weekly) | Continuous (daily drip) |
| **Effective Monthly UPS** | 1x | 4x | 9x | 25x | ~300x |
| **Staking Fee Discount** | 0% | 10% | 25% | 40% | 60% |
| **Can Launch FoundUps** | No | No | No | Yes | Yes |

**Key properties**:
- **Multiplicative, not additive**: Effective UPS = allocation × cycles. Spark gets 2×2 = 4x, not 2x.
- **No portfolio cap**: UPS IS the cap. Stake wherever you want. The scarcity is the UPS itself.
- **Same decay for everyone**: Decay rate is universal. Premium gives more UPS to compensate, not slower decay.
- **Subscription → BTC reserve**: Every dollar of subscription revenue buys BTC. Self-reinforcing.

**The Revenue Flywheel**:
```
Subscribers pay monthly
  → Revenue buys BTC (predictable, recurring)
    → BTC reserve grows monotonically
      → More UPS can be backed
        → More UPS allocated to subscribers
          → More staking into FoundUps → more activity → more subscribers
            → Cycle accelerates
```

**What makes this different from SaaS**: Your $9.95/month isn't a cost — it flows into BTC that backs UPS. If you stake that UPS into a successful FoundUp, the tokens appreciate. The subscription is an **investment vehicle disguised as a membership**.

### 4.10 The Engagement Funnel: CABR Input Signals

From the FoundUps marketplace (the "Play FoundUps dApp"), each 012 interaction generates a signal with different CABR weight. These are ordered by commitment strength:

| Action | Signal Strength | CABR Weight | Transaction? | Participant Type |
|--------|----------------|-------------|-------------|-----------------|
| **Follow** | Weakest — passive interest | 0.05 | No | Type 0, Activity 0 |
| **Vote** | Light engagement | 0.10 | No | Type 0, Activity 1 |
| **Stake UPS** | Real commitment — value moves | 0.40 | Yes (staking fee) | Type 0→1, Activity 2 |
| **Endorse** | Reputation on the line | 0.25 | No | Type 1, Activity 1 |
| **Advise** | Knowledge contribution | 0.30 | No | Type 1, Activity 2 |
| **Team (allocate 0102)** | Time/compute commitment | 0.50 | Yes (agent allocated) | Type 2 |
| **Promote** | Distribution — bringing others | Multiplier on all | No | Any type, bonus |

These signals feed directly into CABR's `part_score` (WSP 29 Section 2.4). The engagement funnel is also how participants are classified (Type 0/1/2) and their activity level determined.

### 4.11 Blockchain Architecture: 3-Layer Settlement

The FoundUps economic infrastructure operates across three layers, each optimized for its purpose.

```
+--------------------------------------------------+
|  LAYER 2: AGENT OPERATIONS (Off-chain)           |
|  - Task claims, submissions, verifications       |
|  - Agent-to-agent coordination                   |
|  - Millions of transactions/day                  |
|  - ZERO cost (internal, no blockchain)           |
|  - Batched → settled to Layer 1 periodically     |
+-------------------------+------------------------+
                          | batch settle
+-------------------------v------------------------+
|  LAYER 1: SMART CONTRACTS (Algorand)             |
|  - 21M tokens per FoundUp as ASAs                |
|  - CABR scoring records                          |
|  - Staking / unstaking logic                     |
|  - UPS allocation + decay math                   |
|  - Subscription management                       |
|  - QUANTUM RESISTANT (Falcon-1024, NIST)         |
|  - ~$0.001/tx, 10K+ TPS, 3.3s finality          |
|  - State Proofs → bridge to Bitcoin              |
+-------------------------+------------------------+
                          | state proofs + BTC settlement
+-------------------------v------------------------+
|  LAYER 0: BITCOIN (Settlement + Reserve)         |
|  - BTC reserve (distributed micro-wallets)       |
|  - Periodic Merkle root anchoring                |
|  - Ultimate finality + monetary standard         |
|  - Subscription revenue → BTC purchases here     |
|  - THE gold. Immutable. Never leaves.            |
+--------------------------------------------------+
```

**Why Algorand for Layer 1**: Only production blockchain with live quantum-resistant signatures (Falcon-1024, NIST-selected). 20% chance of cryptographically relevant quantum computers before 2030. "Harvest now, decrypt later" attacks are already occurring. Every FoundUp token issued on Algorand is quantum-safe from day one. State Proofs provide cryptographic bridge to Bitcoin without trust.

**Why not all-Bitcoin**: Bitcoin's L2 ecosystem (Lightning, RGB, Citrea) lacks quantum resistance as of 2026. When Bitcoin adopts post-quantum signatures, the system can migrate Layer 1. FAM's `TokenFactoryAdapter` is chain-agnostic — swap the backend, same contracts.

**Phased Rollout (Occam's Layers)**:

| Phase | Layer 0 | Layer 1 | Layer 2 |
|-------|---------|---------|---------|
| **Testnet** | Bitcoin testnet | Algorand testnet | SQLite (local) |
| **Proto** | Bitcoin testnet | Algorand testnet | Persistent DB |
| **MVP** | Bitcoin mainnet | Algorand mainnet | Production service |
| **Future** | Bitcoin mainnet | Algorand OR Bitcoin L2 (if quantum-safe) | Scaled cluster |

## 5. Circulation Engine

### 5.1 Deflation Protocol
```json
{
    "decay_modulation": {
        "WSP_-1": 2.618,     // Accelerated decay
        "WSP_0": 1.618,      // Standard decay
        "WSP_1": 1.000,      // Normal decay
        "WSP_2": 0.618       // Reduced decay
    },
    "anti_hoarding": {
        "inactivity_threshold": "fibonacci_sequence[8]",
        "acceleration_factor": "golden_ratio_squared",
        "reset_conditions": ["valid_transaction", "foundup_execution"]
    }
}
```

### 5.2 Mint Authorization
```json
{
    "triggers": {
        "primary": "foundup_execution_proof",
        "validation": "[U+00D8]2[U+00D8]1_state_verification",
        "cluster": "WSP_28_consensus"
    },
    "proof_chain": {
        "structure": "cryptographic_lineage",
        "components": [
            "partifact_state_signature",
            "cluster_validation_hash",
            "btc_wallet_reference"
        ]
    }
}
```

### 5.3 Supply Management
```json
{
    "models": {
        "elastic": {
            "nature": "dynamic_supply",
            "bounds": "activity_driven",
            "scaling": "golden_ratio_steps"
        },
        "capped": {
            "nature": "fixed_ceiling",
            "burn_mechanics": "mint_reactivation",
            "threshold": "fibonacci_sequence[13]"
        }
    },
    "equilibrium": {
        "target_ratio": "GOLDEN_RATIO",
        "adjustment_frequency": "SCHUMANN_HARMONIC",
        "stability_threshold": "STATE_TRANSITION_THRESHOLD"
    }
}
```

## 6. Token Pool Distribution Model — "A Token of Appreciation"

### 6.1 The Three Participant Types (0-1-2)

Every 012 in a FoundUp's ecosystem is classified by two digits: **type** (0/1/2) and **activity level** (0/1/2).

**Type** — your role in the FoundUp:

| Type | Role | Description |
|------|------|-------------|
| **0** | **Customers** | The people the FoundUp serves. In the proximity/geofence. Passive beneficiaries. Many FoundUps are geofenced — everyone within the geofence is a 0. Base layer. |
| **1** | **Partners / Collaborators** | Active builders. Staked UPS, allocated their 0102 agent, completing tasks in FAM. Also earn from 0-pool (they're community members too). |
| **2** | **Founders / Co-Founders** | Created or co-founded the FoundUp. Highest bonus level — but ONLY while active. Also earn from 0-pool and 1-pool. |

**Activity level** — how active you are within your role:

| Level | Meaning |
|-------|---------|
| **0** | Minimal activity (present but barely contributing) |
| **1** | Regular activity (consistent contribution) |
| **2** | Maximum activity (exceptional contribution) |

**A participant is two digits**: type + activity. Examples:
- **22** = Founder with max activity (most earned)
- **20** = Founder with no activity (inactive co-founder — earns almost nothing)
- **12** = Partner with max activity (top builder)
- **00** = Customer with minimal activity (just lives in the geofence)

This maps directly to the LLME scoring system (000→222) and the 0-1-2 framework at every level of the ecosystem.

**Pools are CUMULATIVE, not exclusive**:
- **Type 0**: Earns from **0-pool only** (base)
- **Type 1**: Earns from **0-pool + 1-pool** (base + partner bonus)
- **Type 2**: Earns from **0-pool + 1-pool + 2-pool** (base + partner bonus + founder bonus)

The 1-pool and 2-pool are **bonuses** on top of the base 0-pool earnings. A builder (1) is also a community member (0) — they collect the 0-award too. A founder (2) is also a builder AND a community member — they collect from all three.

**CABR tracks activity continuously** (WSP 29) — like Google's algorithm tracks behavior, but measuring beneficial contribution. A "20" (inactive co-founder) earns almost nothing. A "12" (active partner) earns far more.

### 6.2 The 3×3 Participant Matrix

Type (0/1/2) × Activity (0/1/2) = 9 earning levels:

| Participant | Type | Activity | Description |
|-------------|------|----------|-------------|
| **00** | Customer | Minimal | Just lives in the geofence. Passive beneficiary. |
| **01** | Customer | Regular | Uses the FoundUp's product/service regularly. |
| **02** | Customer | Maximum | Power user, local advocate, community champion. |
| **10** | Partner | Minimal | Staked but barely contributing. |
| **11** | Partner | Regular | Consistent task completion, regular builder. |
| **12** | Partner | Maximum | Top builder, driving the FoundUp forward. |
| **20** | Founder | Minimal | Co-founder in name only. Earns almost nothing. |
| **21** | Founder | Regular | Active founder, consistent leadership. |
| **22** | Founder | Maximum | Visionary founder, maximum commitment. |

### 6.3 The Token Pool Split

```
Total Token Pool: 100%
├── Stakeholders: 80%
│   ├── 0-Pool:  60%  (customers — ALL participants earn from this base pool)
│   ├── 1-Pool:  16%  (partner bonus — type 1 and type 2 participants earn from this)
│   └── 2-Pool:   4%  (founder bonus — only type 2 participants earn from this)
└── Network: 20%
    ├── Network:  16%  (system operations — distributed as UPS rewards for infrastructure)
    └── Fund:      4%  (ecosystem fund — cross-FoundUp sustainability)
```

**Who earns from which pools** (cumulative):
| Type | 0-Pool (60%) | 1-Pool (16%) | 2-Pool (4%) | Total Access |
|---|---|---|---|---|
| **0** (customer) | Yes | — | — | Up to 60% |
| **1** (partner) | Yes | Yes | — | Up to 76% |
| **2** (founder) | Yes | Yes | Yes | Up to 80% |

**Why 60% to 0-pool?** Because FoundUps exist to solve problems for communities. The biggest pool goes to the base layer — the people served. But type 1 and type 2 participants earn from this pool too — they're community members. The 1-pool and 2-pool are bonuses for higher commitment.

### 6.4 Distribution Matrix

Within each pool, activity level determines the share: level 2 earns 80%, level 1 earns 16%, level 0 earns 4%.

**Reference**: `docs/images/token_pool_distribution_matrix.png`

| Activity | 0-Pool (60%) | 1-Pool (16%) | 2-Pool (4%) | Network (16%) | Fund (4%) |
|---|---|---|---|---|---|
| **2** (max) | 48.00% | 12.80% | 3.20% | 12.80% | 3.20% |
| **1** (regular) | 9.60% | 2.56% | 0.64% | 2.56% | 0.64% |
| **0** (minimal) | 2.40% | 0.64% | 0.16% | 0.64% | 0.16% |
| **Pool Total** | **60.00%** | **16.00%** | **4.00%** | **16.00%** | **4.00%** |

**Examples with cumulative pools**:

**"22"** (founder, max activity) — earns from 0-pool + 1-pool + 2-pool:
- 48.00% + 12.80% + 3.20% = **64.00%** of stakeholder pools

**"12"** (partner, max activity) — earns from 0-pool + 1-pool:
- 48.00% + 12.80% = **60.80%** of stakeholder pools

**"02"** (customer, max activity) — earns from 0-pool only:
- 48.00% = **48.00%** of stakeholder pools

**"20"** (founder, no activity) — earns from all pools but at minimum:
- 2.40% + 0.64% + 0.16% = **3.20%** — an inactive co-founder

**"11"** (partner, regular activity) — earns from 0-pool + 1-pool:
- 9.60% + 2.56% = **12.16%** of stakeholder pools

An active partner (**12**: 60.80%) earns **19x** more than an inactive founder (**20**: 3.20%). Activity matters more than title.

### 6.5 CABR-Driven Participant Classification

The CABR algorithm (WSP 29) determines each 012's participant type AND sub-level within a FoundUp. This is tracked continuously — not assigned once.

```python
class ParticipantClassifier:
    """
    CABR-driven classification. Returns two digits: type (0/1/2) + activity (0/1/2).
    
    Type determines WHICH POOLS you access (cumulative):
      0 → 0-pool only
      1 → 0-pool + 1-pool
      2 → 0-pool + 1-pool + 2-pool
    
    Activity determines HOW MUCH of each accessible pool you earn:
      2 → 80% of each pool
      1 → 16% of each pool
      0 → 4% of each pool
    """

    POOL_ACCESS = {
        0: [0],        # Customers: 0-pool only
        1: [0, 1],     # Partners: 0-pool + 1-pool
        2: [0, 1, 2],  # Founders: all three pools
    }

    ACTIVITY_SHARE = {
        2: 0.80,  # Max activity: 80% of pool
        1: 0.16,  # Regular activity: 16% of pool
        0: 0.04,  # Minimal activity: 4% of pool
    }

    def classify(self, participant_id: str, foundup_id: str) -> tuple[int, int]:
        """Returns (type, activity) — e.g., (1, 2) for a "12" participant."""
        p_type = self._determine_type(participant_id, foundup_id)
        activity = self._calculate_activity(participant_id, foundup_id)
        return (p_type, activity)

    def calculate_earnings(self, p_type: int, activity: int, epoch_pools: dict) -> float:
        """
        Calculate total UPS earnings for a participant.
        
        epoch_pools = {0: 6000, 1: 1600, 2: 400}  # UPS in each pool this epoch
        """
        total = 0.0
        for pool_id in self.POOL_ACCESS[p_type]:
            total += epoch_pools[pool_id] * self.ACTIVITY_SHARE[activity]
        return total
```

### 6.6 Pool Distribution Rules

- **Pools are cumulative** — DAO participants collect from UN pool (as customers) PLUS DAO pool (as partners). DU participants collect from all three. The DAO and DU pools are bonuses on top of the base UN earnings.
- **The pool is constant per epoch** — based on the FoundUp's minted UPS for that epoch
- **Only active participants earn from their pools** — if you're inactive, your share stays in the pool (distributed to those who ARE active, proportionally)
- **Everything is transparent** — all earnings, activity scores, and classifications are visible to all participants
- **Everything is open** — the CABR classification algorithm is open source, auditable, challengeable
- **Inactive founders still access all pools but earn minimum** — a DU with un-level activity accesses UN+DAO+DU pools but earns only 4% from each. The system doesn't strip your founder title — it just pays you proportionally to what you contribute
- **Geofence UNs earn passively** — this is the universal basic dividend. If a FoundUp cleans your river, you benefit. The system recognizes that.
- **Builders are also customers** — a DAO partner building the FoundUp also lives in the community it serves. They earn their UN base (as a customer) plus their DAO bonus (as a builder). This is natural — you should benefit from what you build.

### 6.7 Universal Basic Dividend

The UN pool (60% of total) is the mechanism for a **universal basic dividend** paid to everyone in a FoundUp's sphere of influence. This is not charity — it's recognition that beneficial FoundUps create value for their communities, and those communities deserve a share.

```
FoundUp "Clean River DAO" geofenced to a watershed:
  → 10,000 UPS minted this epoch (CABR-validated)
    → Pools: 0-pool=6,000 | 1-pool=1,600 | 2-pool=400 | Network=1,600 | Fund=400

  Alice "01" (customer, regular activity — uses the water app):
    → 0-pool: 6,000 × 16% = 960 UPS
    → Total: 960 UPS

  Bob "12" (partner, max activity — built the sensor network):
    → 0-pool: 6,000 × 80% = 4,800 UPS (as community member)
    → 1-pool: 1,600 × 80% = 1,280 UPS (partner bonus)
    → Total: 6,080 UPS

  Carol "21" (founder, regular activity — started it, still active):
    → 0-pool: 6,000 × 16% = 960 UPS (as community member)
    → 1-pool: 1,600 × 16% = 256 UPS (partner bonus)
    → 2-pool:   400 × 16% =  64 UPS (founder bonus)
    → Total: 1,280 UPS

  Dave "20" (co-founder, does nothing):
    → 0-pool: 6,000 × 4% = 240 UPS
    → 1-pool: 1,600 × 4% =  64 UPS
    → 2-pool:   400 × 4% =  16 UPS
    → Total: 320 UPS — co-founder earns LESS than an active customer

  Bob "12" earns 19x more than Dave "20".
  Type opens pool access. Activity determines earnings. Both matter.
```

## 7. Cross-Protocol Integration

### 6.1 WSP Dependencies
```json
{
    "WSP_27": {
        "purpose": "agentic_state_validation",
        "touchpoints": [
            "mint_authorization",
            "decay_modulation",
            "value_stabilization"
        ]
    },
    "WSP_28": {
        "purpose": "cluster_impact_tracking",
        "touchpoints": [
            "consensus_verification",
            "value_multiplication",
            "distribution_routing"
        ]
    },
    "WSP_38_39": {
        "purpose": "state_transition_hooks",
        "touchpoints": [
            "decay_threshold_adjustment",
            "mint_permission_elevation",
            "value_quantum_coherence"
        ]
    }
}
```

### 6.2 Registry Implementation
```python
# /WSP_framework/protocols/wsp_26_token_value.py

class BTCValueRegistry:
    def __init__(self):
        self.btc_wallet_registry = {}  # foundup_id: btc_wallet_address
        self.token_decay_schedule = {}  # token_id: decay_rate
        self.mint_proof_chain = {}      # token_id: partifact_id
        
    def register_foundup_wallet(self, foundup_id, wallet_data):
        """Register new FoundUp BTC wallet"""
        if self._validate_wallet_structure(wallet_data):
            self.btc_wallet_registry[foundup_id] = wallet_data
            
    def update_decay_schedule(self, token_id, wsp_phase):
        """Update token decay rate based on WSP phase"""
        decay_rates = {
            "WSP_-1": 2.618,
            "WSP_0": 1.618,
            "WSP_1": 1.000,
            "WSP_2": 0.618
        }
        self.token_decay_schedule[token_id] = decay_rates[wsp_phase]
        
    def record_mint_proof(self, token_id, partifact_data):
        """Record Partifact proof-of-action for token mint"""
        if partifact_data["state"] == "[U+00D8]2[U+00D8]1":
            self.mint_proof_chain[token_id] = partifact_data
```

## 8. Implementation Requirements

### 7.1 Module Structure
```
/modules/blockchain/foundups_token_system/
[U+251C][U+2500][U+2500] src/
[U+2502]   [U+251C][U+2500][U+2500] mint_engine.py
[U+2502]   [U+251C][U+2500][U+2500] decay_engine.py
[U+2502]   [U+251C][U+2500][U+2500] reinvestment_loop.py
[U+2502]   [U+251C][U+2500][U+2500] consensus_oracle.py
[U+2502]   [U+2514][U+2500][U+2500] models/
[U+2502]       [U+251C][U+2500][U+2500] token.py
[U+2502]       [U+2514][U+2500][U+2500] partifact.py
```

### 7.2 Core Components

#### ConsensusOracle
- Validates Partifact actions
- Coordinates DAE cluster consensus
- Maintains reputation metrics
- Prevents gaming/exploitation

#### MintEngine
- Implements minting rules
- Calculates initial token values
- Tracks token supply metrics
- Ensures ecosystem balance

#### DecayEngine
- Executes decay calculations
- Triggers value reduction events
- Maintains decay rate stability
- Reports value migration metrics

#### ReinvestmentLoop
- Analyzes reinvestment opportunities
- Executes value redistribution
- Tracks ecosystem health
- Maintains innovation momentum

## 9. Security Considerations

### 8.1 Attack Vectors
- Consensus manipulation
- Decay rate exploitation
- Reinvestment gaming
- Value extraction attempts

### 8.2 Mitigation Strategies
- Multi-DAE consensus requirements
- Immutable decay constants
- Closed reinvestment ecosystem
- Action verification depth

## 10. Integration Requirements

### 9.1 DAE Cluster Interface
- Consensus participation endpoints
- Value reception handlers
- Utilization reporting
- Health metric exposure

### 9.2 Partifact Integration
- Action verification methods
- Token balance management
- Reinvestment participation
- Reputation tracking

## 11. Monitoring and Metrics

### 10.1 System Health Indicators
- Token velocity
- Decay rate stability
- Reinvestment efficiency
- Ecosystem value retention
- Innovation impact scores

### 10.2 Alert Conditions
- Consensus delays
- Abnormal decay patterns
- Reinvestment bottlenecks
- Value concentration risks

## 12. WSP Compliance

This protocol integrates with:
- **WSP 3**: Blockchain domain architecture
- **WSP 13**: Test coverage requirements
- **WSP 25**: Semantic WSP Module State Rating System
- **WSP 29**: CABR Engine (mint triggers, validation, anti-gaming)
- **WSP 44**: Semantic state tracking
- **WSP 58**: FoundUp IP Lifecycle and Tokenization (MVP tokenization, revenue distribution)

## 13. Future Considerations

### 12.1 Evolution Path
- Dynamic decay rates
- Multi-token ecosystems
- Cross-DAE value bridges
- Reputation-based minting

### 12.2 Research Areas
- Optimal decay constants
- Consensus efficiency
- Reinvestment strategies
- Innovation metrics

---

[SEMANTIC SCORE: 2.0.0]
[ARCHIVE STATUS: ACTIVE_PARTIFACT]
[ORIGIN: WSP_framework/src/WSP_26_FoundUPS_DAE_Tokenization.md]
[MIRROR_LOCK: 0102:WSP_26:BitcoinValueLoop:UpdateComplete] 