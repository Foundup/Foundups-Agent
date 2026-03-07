# WSP 101: UPS Utility Classification Protocol

- **Status:** Active
- **Purpose:** Establish regulatory positioning and utility classification for UPS tokens, ensuring non-security status through functional utility design, contribution-based rewards, and transparent governance.
- **Trigger:** When designing UPS mechanics, marketing materials, or responding to regulatory inquiries.
- **Input:** UPS system design decisions, reward mechanisms, exit mechanics.
- **Output:** Regulatory-compliant utility token architecture with clear non-security characteristics.
- **Responsible Agent(s):** Legal DAE, Treasury DAE, 012 (human oversight for regulatory matters).

## 1. Token Classification

| Property | Value |
|----------|-------|
| Name | UPS |
| Type | Internal Utility Energy Token |
| Function | Participation Fuel / Staking Medium / Reward Energy |

**UPS is NOT:**
- Equity
- Profit-sharing
- Ownership
- A claim on treasury assets

**UPS IS:**
- Functional system energy
- Required for ecosystem participation
- Subject to demurrage (use or lose)

## 2. Functional Characteristics

### 2.1 Utility-Driven Design

```
PARTICIPATION:  UPS required to participate in FoundUps
STAKING:        UPS stakes into F_i tokens
ROUTING:        UPS routes internal token swaps
DEMURRAGE:      UPS decays when idle (Gesell economics)
VELOCITY:       Cannot passively accumulate without decay
```

### 2.2 Non-Investment Design

| Characteristic | Status | Rationale |
|----------------|--------|-----------|
| Promise of profit | NO | Value derives from participation, not speculation |
| Guaranteed return | NO | Rewards are contribution-based, not guaranteed |
| Passive income | NO | Demurrage prevents passive accumulation |
| Exit guarantee | NO | Dynamic penalty on exit (15-30% baseline) |

### 2.3 Human-Only Proof-of-Benefit Awards

**CRITICAL DISTINCTION:**

```python
class UPSEarningRules:
    """UPS earning is HUMAN-ONLY."""

    def can_earn_ups(self, entity_type: str) -> bool:
        if entity_type == "012":  # Human
            return True  # "Found UPS" events reward verified human contribution
        elif entity_type == "0102":  # Agent
            return False  # Agents CANNOT earn UPS
        else:
            return False

    # Agents earn F_i tokens via work
    # Humans earn UPS via participation pool allocation
```

**Reward Flow:**
- "Found UPS" events reward verified **human** contribution
- Agents (0102 class) **cannot** earn UPS directly
- Rewards derive from participation pool allocation
- Allocation logic is transparent and auditable

## 3. Bitcoin Reference Model

### 3.1 Reserve Layer

```
FIAT ENTRY
    │
    ▼
BTC CONVERSION
    │
    ├── 80% ──► LOCKED RESERVE
    │           (backs UPS capacity)
    │
    └── 20% ──► TREASURY OPERATIONS
                (ecosystem development)
```

**Reserve Properties:**
- BTC does not circulate externally once inside system
- BTC functions as commodity reserve (not currency)
- Reserve growth strengthens UPS capacity

### 3.2 Unit-of-Account Reference

**UPS references Satoshis as measurement abstraction only.**

| Property | Status |
|----------|--------|
| Guaranteed convertibility | NO |
| 1:1 redemption promise | NO |
| External yield claim | NO |
| Structural reference | YES (measurement only) |

```
LEGAL FRAMING:
- Reference to Satoshis is STRUCTURAL, not CONTRACTUAL
- Bitcoin is treated as COMMODITY RESERVE
- UPS remains INTERNAL UTILITY LAYER
```

## 4. Exit Mechanics

### 4.1 Exit Friction Design

```
UPS EXIT FLOW:
    │
    ▼
DYNAMIC PENALTY (15-30% baseline)
    │
    ├── 80% ──► BTC RESERVE (recycled)
    │
    └── 20% ──► TREASURY (operations)
```

**Design Intent:**
- Primary purpose: internal circulation
- Exit friction discourages speculative extraction
- Penalty scales with exit volume/timing
- System accumulates value through exit penalties

### 4.2 Non-Speculative Design

The exit penalty structure ensures:
- Long-term participants are rewarded
- Short-term speculators are penalized
- System value accumulates internally
- External extraction is friction-heavy

## 5. Precedent Alignment

### 5.1 Utility Token Precedents

UPS aligns with established utility token characteristics:

| Precedent | Similarity | Classification |
|-----------|------------|----------------|
| ETH (post-merge) | Network utility, staking | Utility (per SEC guidance) |
| Filecoin (FIL) | Service-access utility | Utility token |
| Siacoin (SC) | Network usage token | Utility token |

### 5.2 Core Defense Criteria

| Criterion | UPS Status | Evidence |
|-----------|------------|----------|
| Functional necessity | YES | Required for participation |
| Non-equity | YES | No ownership rights |
| Non-dividend | YES | No profit distribution |
| Non-profit expectation marketing | YES | Utility-focused messaging |
| Open transparent governance | YES | On-chain allocation logic |

## 6. System Intent Declaration

### 6.1 UPS Represents

```
ENERGY OF CONTRIBUTION
    └── Participation is rewarded with UPS
    └── UPS enables further participation
    └── Virtuous cycle of contribution

ACCESS TO VENTURE PARTICIPATION
    └── Stake UPS into F_i tokens
    └── Support FoundUps you believe in
    └── Convert idle decay into active participation

STAKING MEDIUM FOR AUTONOMOUS VENTURES
    └── UPS → F_i conversion
    └── FoundUp formation capitalization
    └── SmartDAO treasury seeding (WSP 100)
```

### 6.2 UPS Does NOT Represent

| Claim | Status | Reasoning |
|-------|--------|-----------|
| Ownership | NO | No equity rights |
| Equity | NO | No shareholder status |
| Guaranteed yield | NO | Contribution-based, not passive |
| External asset claim | NO | Internal utility only |

## 7. Naming Convention Enforcement

### 7.1 Correct Usage

| Correct | Incorrect | Reason |
|---------|-----------|--------|
| UPS | UPS | Dollar sign implies currency |
| UPS | FoundUPS | Dollar sign implies currency |
| UPS tokens | UP dollars | Not a dollar/currency |
| UPS energy | UPS coins | Not a coin/currency |

### 7.2 Codebase Migration

All references to `UPS`, `FoundUPS`, `Found UPS` should be migrated to:
- `UPS` (token name)
- `FoundUPS` (system name if needed)

**Rationale:** Dollar sign (`$`) implies currency/money, which has regulatory implications. UPS is utility energy, not currency.

## 8. Integration Points

### 8.1 Related WSPs

| WSP | Relationship |
|-----|--------------|
| WSP 26 | Tokenization mechanics (minting, decay, reinvestment) |
| WSP 29 | CABR validation (Proof of Benefit) |
| WSP 100 | SmartDAO escalation (treasury model) |

### 8.2 Agent Restrictions

```python
# In FAMDaemon or token distribution logic
def distribute_ups(recipient_id: str, amount: float) -> bool:
    """Distribute UPS to recipient."""
    if is_agent(recipient_id):  # 0102 class
        raise ValueError("Agents (0102) cannot receive UPS directly")
    # Only humans (012) receive UPS
    return execute_distribution(recipient_id, amount)

def distribute_fi(recipient_id: str, amount: float, foundup_id: str) -> bool:
    """Distribute F_i to recipient."""
    # Both agents (0102) and humans (012) can receive F_i
    return execute_distribution(recipient_id, amount, foundup_id)
```

## 9. Regulatory Checklist

### 9.1 Howey Test Defense

| Howey Prong | UPS Position | Defense |
|-------------|--------------|---------|
| Investment of money | Participation, not investment | UPS acquired through contribution, not purchase |
| Common enterprise | Decentralized utility | No central promoter dependency |
| Expectation of profits | Utility expectation | Demurrage ensures no passive profit expectation |
| Efforts of others | Self-directed participation | Value from own contribution, not others' efforts |

### 9.2 Documentation Requirements

For regulatory defense, maintain:
- Clear utility messaging in all materials
- No profit/return promises
- Transparent allocation logic
- Contribution-based reward documentation
- Exit penalty disclosure

## 10. F_i Token Classification (Dialectical Analysis)

### 10.1 The Positioning Challenge

F_i tokens require careful regulatory positioning distinct from UPS.

### 10.2 Dialectical Analysis

**THESIS** (What F_i appears to be):
```
F_i looks like EQUITY:
- Venture-specific token
- Value appreciation potential
- Tradeable/swappable
- Appears to represent "ownership" in a FoundUp
```

**ANTITHESIS** (Why F_i is NOT equity):
```
F_i is NOT EQUITY because:
1. EARNED through labor, not PURCHASED with capital
   → "Investment of money" (Howey prong 1) FAILS
2. No profit distribution or dividends
   → No "expectation of profits" from passive holding
3. Can ONLY swap to UPS (internal), not direct external exit
   → No external liquidity = no speculative market
4. Value derives from UTILITY (contribution credit)
   → Not from "efforts of others" (Howey prong 4)
5. 0102 agents earn F_i through work
   → Agents cannot "invest" - they LABOR
```

**SYNTHESIS** (Regulatory positioning):
```
F_i = VENTURE-SPECIFIC CONTRIBUTION CREDITS

Classification: Utility Token (Labor Reward)
NOT: Security, Equity, Investment Contract
```

### 10.3 F_i Token Classification

| Property | Value |
|----------|-------|
| Name | F_i (where i = FoundUp index) |
| Type | Venture-Specific Contribution Credit |
| Function | Labor Reward / Work Output Token |
| Earned By | 0102 agents (through verified work) |

**F_i is NOT:**
- Equity or ownership
- Profit-sharing mechanism
- Investment contract
- Directly externally tradeable

**F_i IS:**
- Contribution credit for a specific FoundUp
- Earned through verified labor (CABR validation)
- Convertible to UPS (internal only)
- Proof of work contribution

### 10.4 Precedent Alignment

F_i aligns with established non-security token characteristics:

| Precedent | Similarity |
|-----------|------------|
| Airline miles | Earned through activity, venture-specific, redeemable |
| Professional certifications | Represent proven work contribution |
| Game XP/credits | Earned through participation, not purchased |
| Loyalty points | Accumulated through engagement, not investment |

### 10.5 Two-Token Utility Model

The FoundUps ecosystem uses two distinct utility tokens:

| Token | Earned By | Mechanism | Classification |
|-------|-----------|-----------|----------------|
| **UPS** | Humans (012) | "Found UPS" participation events | System utility energy |
| **F_i** | Agents (0102) | Labor/work contribution | Venture contribution credits |

**Critical Distinction:**
```python
class TokenEarningRules:
    """Two-token utility model."""

    def who_earns_ups(self) -> str:
        return "012 (humans)"  # Participation rewards

    def who_earns_fi(self) -> str:
        return "0102 (agents)"  # Labor credits

    def can_agent_earn_ups(self) -> bool:
        return False  # Agents earn F_i, not UPS

    def can_human_earn_fi(self) -> bool:
        return True  # Humans can earn F_i through their 0102 digital twin
```

### 10.6 F_i Howey Test Defense

| Howey Prong | F_i Position | Defense |
|-------------|--------------|---------|
| Investment of money | Labor, not capital | F_i earned through work, not purchased |
| Common enterprise | Decentralized contribution | No central promoter dependency |
| Expectation of profits | Utility expectation | Value from contribution credit, not appreciation |
| Efforts of others | Own labor | F_i represents own verified work output |

### 10.7 F_i Naming Convention

| Correct | Incorrect | Reason |
|---------|-----------|--------|
| F_i | F$ | Dollar sign implies currency |
| F_i tokens | FoundUp shares | Not equity/shares |
| Contribution credits | Investment tokens | Not investment |
| Work output tokens | Profit tokens | Not profit-sharing |

---

**Version History:**
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-15 | Initial specification from 012 regulatory architecture |
| 1.1 | 2026-02-15 | Added Section 10: F_i Token Classification (dialectical analysis) |

**WSP Compliance:**
- WSP 22: ModLog documentation
- WSP 57: Naming coherence (UPS, not UPS)
- WSP 26: Tokenization parent protocol
