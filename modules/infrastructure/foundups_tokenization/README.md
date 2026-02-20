# FoundUps Tokenization System

**Purpose**: Bio-decay economic model for UPS universal participation token and FoundUp-specific tokens (e.g., JUNK$)

**Domain**: `modules/infrastructure/` (WSP 3 infrastructure domain)
**WSP Compliance**: WSP 26 (Tokenization), WSP 29 (CABR), WSP 58 (IP Lifecycle)

## Architecture Overview

### Two-Token System

```yaml
UPS_Universal_Token:
  scope: "All FoundUps (universal participation)"
  supply_formula: "(BTC_Reserve_Satoshis) / Num_FoundUps"
  minting_trigger: "CABR validation (WSP 29)"
  characteristics:
    - BTC-backed value
    - Bio-decay (ICE/LIQUID/VAPOR states)
    - Non-transferable between users
    - Swappable for FoundUp tokens

FoundUp_Specific_Tokens:
  scope: "Per-FoundUp (e.g., JUNK$ for GotJunk)"
  supply: "21,000,000 fixed (Bitcoin parity)"
  acquisition: "Swap UPS (one-way, burns UPS)"
  characteristics:
    - Stage-based release (Rogers Diffusion)
    - Decay rate varies by stage
    - Governance rights in FoundUp
    - Revenue sharing from fees
```

## Bio-Decay States (Water Analogy)

### State Machine

```
CABR Beneficial Action → Mint UPS → LIQUID (wallet)
                                         ↓
                    ┌────────────────────┼────────────────────┐
                    ↓                    ↓                    ↓
                  STAKE              LET DECAY             EXIT
                    ↓                    ↓                    ↓
              ICE (frozen)      RESERVOIR (returns)    VAPOR (15% tax)
              No decay          Redistributed          80% → BTC
              Earns yield       To active users        20% → Reservoir
```

### Decay Mathematics

**Adaptive Decay Rate** (Michaelis-Menten kinetics):
```
λ(t) = λ_min + (λ_max - λ_min) · (D / (K + D))

Parameters:
  D = days inactive
  λ_min = 0.005/day (0.5% monthly for active users)
  λ_max = 0.05/day (5% monthly for inactive users)
  K = 7 days (half-maximal constant)
```

**Circadian Pulse** (habit formation):
```
λ_pulse = λ(t) · (1 + c · Pulse(t_local))

Where:
  c = 0.3 (30% boost during pulse window)
  Pulse = 1 if 6-7 PM local time, else 0
```

**Exponential Decay**:
```
U(t) = U₀ · e^(-λ(t)·t)

Daily cap: max 3% per day (no shock losses)
```

## CABR Integration (WSP 29)

### UPS Minting Trigger

UPS is **ONLY** minted when CABR validates a beneficial action:

```python
class CABRMintingEngine:
    """
    Consensus-Driven Autonomous Benefit Rate (also referred to as
    Collective Autonomous Benefit Rate) triggers UPS creation
    WSP 29 integration
    """

    def validate_and_mint(self, action, user):
        # Step 1: CABR validates action is beneficial
        cabr_score = self.cabr_oracle.validate_benefit(action)

        # Step 2: Calculate UPS mint amount
        if cabr_score >= BENEFIT_THRESHOLD:
            base_amount = self.calculate_base_reward(action.type)
            quality_multiplier = cabr_score  # 0.0-1.0
            up_amount = base_amount * quality_multiplier

            # Step 3: Mint UPS to user's LIQUID wallet
            self.mint_ups_liquid(user, up_amount)

            # Step 4: Trigger decay timer
            self.start_decay_timer(user)

            # Step 5: Nudge user to stake
            self.send_stake_notification(user, up_amount)

            return {
                "minted": up_amount,
                "cabr_score": cabr_score,
                "state": "LIQUID",
                "decay_active": True
            }
        else:
            return {"error": "CABR validation failed - action not beneficial"}
```

### Beneficial Actions (GotJunk Examples)

```yaml
List_Item:
  cabr_validation:
    - Photo quality check (not blurry)
    - Description completeness
    - Reasonable pricing (not spam)
    - Geo-location valid (within 50km)
  base_reward: 1.0 UPS
  quality_range: 0.5-1.5 UPS (CABR score multiplier)

Sell_Item:
  cabr_validation:
    - Transaction completed successfully
    - Both parties confirmed
    - No disputes or fraud
  base_reward: 2.0 UPS
  quality_range: 1.0-3.0 UPS

Host_Storage:
  cabr_validation:
    - IPFS file served to peer
    - Merkle proof of hosting
    - Uptime > 95%
  base_reward: 0.01 UPS per file served
  quality_range: 0.005-0.02 UPS

Invite_Friend:
  cabr_validation:
    - Invite redeemed successfully
    - Invitee completes first action
    - No invite farming detected
  base_reward: 10.0 UPS
  quality_range: 5.0-15.0 UPS
```

## Module Structure

```
modules/infrastructure/foundups_tokenization/
├── README.md                          # This file
├── INTERFACE.md                       # Public API
├── ModLog.md                          # Change log
├── module.json                        # DAE discovery
├── requirements.txt                   # Python deps
├── package.json                       # Solidity deps
├── src/
│   ├── bio_decay_engine.py           # Decay math & state management
│   ├── cabr_minting_engine.py        # CABR → UPS minting
│   ├── btc_anchor_engine.py          # BTC reserve management
│   ├── distribution_dae.py           # Per-FoundUp token distribution
│   ├── invite_system.py              # Gmail-style invite codes
│   ├── contracts/
│   │   ├── UPSBioDecayEngine.sol     # Smart contract (Polygon)
│   │   ├── FoundUpToken.sol          # ERC-20 template
│   │   └── CABROracle.sol            # Off-chain CABR integration
│   └── models/
│       ├── user_state.py             # ICE/LIQUID/VAPOR positions
│       └── decay_params.py           # λ_min, λ_max, K constants
├── tests/
│   ├── test_bio_decay.py             # Decay math verification
│   ├── test_cabr_minting.py          # CABR validation tests
│   ├── test_btc_anchor.py            # BTC reserve tests
│   └── test_contracts/               # Solidity unit tests
└── docs/
    ├── BIO_DECAY_MODEL.md            # Mathematical spec
    ├── CABR_INTEGRATION.md           # WSP 29 integration
    ├── TOKENOMICS.md                 # Complete economic model
    └── DEPLOYMENT.md                 # Polygon deployment guide
```

## Quick Start

### Install Dependencies

```bash
cd modules/infrastructure/foundups_tokenization
pip install -r requirements.txt
npm install  # For Solidity contracts
```

### Deploy Contracts (Polygon Mumbai Testnet)

```bash
# Set environment variables
export POLYGON_RPC_URL="https://rpc-mumbai.matic.today"
export PRIVATE_KEY="your_private_key"

# Deploy bio-decay engine
npx hardhat run scripts/deploy_bio_decay.ts --network mumbai

# Deploy FoundUp token (example: JUNK$)
npx hardhat run scripts/deploy_foundup_token.ts --network mumbai --foundup gotjunk
```

### Integrate with FoundUp

```typescript
import { BioDe cayEngine, CABRMintingEngine } from '@foundups/tokenization';

// Initialize
const bioDecay = new BioDecayEngine({
  contractAddress: "0x...",
  polygon Network: "mumbai"
});

const cabrMinting = new CABRMintingEngine({
  contractAddress: "0x...",
  cabrOracleUrl: "https://cabr.foundups.org"
});

// On beneficial action
async function onUserListItem(userId, itemData) {
  // CABR validates
  const validation = await cabrMinting.validateAction({
    type: "list_item",
    data: itemData,
    user: userId
  });

  if (validation.passed) {
    // Mint UPS to user's LIQUID wallet
    await bioDecay.mintUPS(userId, validation.upAmount);

    // Start decay timer
    await bioDecay.startDecayTimer(userId);

    // Notify user
    sendNotification(userId, {
      title: "You earned UPS!",
      message: `${validation.upAmount} UPS → Stake to stop decay`
    });
  }
}
```

## Related Modules

- **WSP Framework**: Protocol definitions (WSP 26, 29, 58)
- **CABR Engine**: `modules/ai_intelligence/cabr_engine/` (WSP 29)
- **GotJunk**: Example FoundUp implementation
- **Cross-Platform Memory**: Pattern storage for tokenomics

## Links

- [WSP 26: FoundUPS DAE Tokenization](../../WSP_framework/src/WSP_26_FoundUPS_DAE_Tokenization.md)
- [WSP 29: CABR Engine](../../WSP_framework/src/WSP_29_CABR_Engine.md)
- [WSP 58: IP Lifecycle & Tokenization](../../WSP_framework/src/WSP_58_FoundUp_IP_Lifecycle_and_Tokenization_Protocol.md)
- [Bio-Decay Mathematical Model](docs/BIO_DECAY_MODEL.md)

---

**Status**: Phase 1 (Design Complete) → Phase 2 (Implementation) → Phase 3 (Testnet Deployment)

**Next Steps**:
1. Implement bio_decay_engine.py
2. Deploy UPSBioDecayEngine.sol to Polygon Mumbai
3. Integrate CABR validation oracle
4. Wire into GotJunk PWA

---

*Remember: UPS is ONLY minted through CABR validation - not arbitrary creation. This ensures all value creation is tied to beneficial actions.*
