# Economics Vocabulary

Token economics and pool terminology for pAVS.

## Core Tokens

| Term | Definition | Backing |
|------|------------|---------|
| **F_i** | FoundUp-specific token (earned by agents) | F_i ← UPS ← BTC |
| **UPS** | Universal Points (1 UPS = 1 satoshi) | UPS ← BTC |
| **BTC** | Bitcoin reserve (Hotel California: enters, never exits) | Reserve asset |

## Token Backing Chain

```
STAKED F_i: F_i ← UPS ← BTC (UPS swapped for F_i, backs the FoundUp)
MINED F_i:  Compute energy (agents earn from work, no BTC backing)
```

## Pool Structure (80/20 Split)

| Pool | % | Subpools | Purpose |
|------|---|----------|---------|
| **Stakeholders** | 80% | Un(60%) + Dao(16%) + Du(4%) | Active participants |
| **Network** | 20% | Network(16%) + Fund(4%) | System operations |

### Stakeholder Subpools

| Pool | % of Total | Access | Description |
|------|------------|--------|-------------|
| **Un** | 60% | Active work | Unrestricted pool for active contributors |
| **Dao** | 16% | Active + governance | DAO-governed allocation |
| **Du** | 4% | Passive stakers | BTC stakers earn passively |

## Scoring & Flow

| Term | Definition | Range |
|------|------------|-------|
| **CABR** | Contribution-Adjusted Benefit Ratio | 0-1 (pipe size) |
| **PoB** | Proof of Benefit (6 economic events) | Boolean |
| **V1** | Validation gate | Pass/fail |
| **V2** | Verification proof | Evidence |
| **V3** | Valuation score | 0-1 |

## PoB Events (6 Economic Proofs)

```python
proof_submitted          # "I did work"
verification_recorded    # "Work was confirmed"
payout_triggered         # "Tokens transferred"
milestone_published      # "Achievement recorded"
fi_trade_executed        # "Market activity"
investor_funding_received # "Capital committed"
```

## Epoch Timing

| Epoch Type | Ticks | Purpose |
|------------|-------|---------|
| Mini-epoch | 10 | Demurrage cycle |
| Epoch | 100 | Du pool distribution (passive) |
| Macro-epoch | 900 | BTC-F_i ratio snapshot |

## Demurrage (UPS Redistribution)

```
Decayed UPS → 80% Network Pool + 20% pAVS Treasury
```

## Tier Backing Ratios (at $100K/BTC)

| Tier | sats/F_i | Scale |
|------|----------|-------|
| F0_DAE | 0 | Seed |
| F1_OPO | 4.76 | $100K |
| F2_GROWTH | 47.6 | $1M |
| F3_INFRA | 476 | $10M |
| F4_MEGA | 4,762 | $100M |
| F5_SYSTEMIC | 47,619 | $1B |

## Lifecycle Stages

```
F0_DAE (60%) = PRE-OPO (invite-only, Angels access only)
F1_OPO+ (40%) = POST-OPO (public, full fee revenue)
```

## Common Mishearings

| Misheard | Correct |
|----------|---------|
| fee, fi | F_i |
| ups, UPs | UPS |
| cap-r, caber | CABR |
| pob, P.O.B. | PoB |

---
*Category: Economics | HoloIndex indexed*
