# CABR Integration: UP$ Minting Trigger

**Critical Insight**: UP$ is **ONLY** minted when CABR (Consensus-driven Autonomous Beneficial Reporting) validates a beneficial action. This prevents arbitrary token creation and ensures all value is tied to real benefit.

## The Problem We're Solving

**Without CABR validation**:
- Users could game the system (spam actions for tokens)
- No quality control on what earns rewards
- Inflationary spiral with no value backing
- No way to measure "beneficial" objectively

**With CABR validation**:
- Every UP$ minted represents verified beneficial action
- Multi-agent consensus prevents gaming
- Quality multiplier ensures better actions = more rewards
- BTC reserve growth matches real value creation

## CABR → UP$ Flow (Complete Architecture)

```
User Action → CABR Validation → UP$ Minting → Bio-Decay Starts
     ↓              ↓                 ↓               ↓
  (GotJunk)    (WSP 29)          (WSP 26)        (ICE/LIQUID/VAPOR)
```

### Step-by-Step Breakdown

#### 1. User Performs Action (FoundUp Level)

```typescript
// GotJunk example: User lists item
async function handleListItem(photoBlob, description, price, location) {
  const itemData = {
    photo: photoBlob,
    description,
    price,
    latitude: location.lat,
    longitude: location.lon,
    timestamp: Date.now(),
    userId: currentUser.id
  };

  // Upload to IPFS
  const ipfsCid = await uploadToIPFS(photoBlob);

  // Submit for CABR validation
  const cabr Validation = await submitForCABR({
    action_type: "list_item",
    foundup_id: "gotjunk",
    data: {
      ...itemData,
      ipfsCid
    }
  });

  return cabrValidation;
}
```

#### 2. CABR Multi-Agent Validation (WSP 29)

```python
class CABRValidationOrchestrator:
    """
    Multi-agent consensus validation
    Prevents gaming, ensures benefit
    """

    def __init__(self):
        self.gemma_validator = GemmaValidator()  # Fast pattern matching
        self.qwen_strategist = QwenStrategist()  # Strategic analysis
        self.vision_dae = VisionDAE()            # Image quality
        self.consensus_threshold = 0.618         # Golden ratio

    async def validate_action(self, action):
        """
        Three-phase validation (WSP 77 coordination)
        """

        # Phase 1: Gemma (fast classification)
        gemma_score = await self.gemma_validator.classify(action)

        if gemma_score < 0.382:  # Below minimum threshold
            return {
                "passed": False,
                "reason": "Failed Gemma classification",
                "score": gemma_score
            }

        # Phase 2: Qwen (strategic analysis)
        qwen_analysis = await self.qwen_strategist.analyze(action)

        # Check for gaming patterns
        if qwen_analysis.gaming_detected:
            return {
                "passed": False,
                "reason": "Gaming pattern detected",
                "pattern": qwen_analysis.gaming_pattern
            }

        # Phase 3: Vision DAE (if image-based action)
        if action.has_image:
            vision_score = await self.vision_dae.analyze_quality(action.image)

            if vision_score < 0.5:  # Poor quality image
                return {
                    "passed": False,
                    "reason": "Image quality too low",
                    "score": vision_score
                }
        else:
            vision_score = 1.0  # N/A for non-image actions

        # Calculate consensus score (weighted average)
        consensus_score = (
            gemma_score * 0.30 +
            qwen_analysis.benefit_score * 0.50 +
            vision_score * 0.20
        )

        # Must meet consensus threshold
        if consensus_score >= self.consensus_threshold:
            # Calculate UP$ mint amount
            base_reward = self.get_base_reward(action.type)
            quality_multiplier = consensus_score
            up_amount = base_reward * quality_multiplier

            return {
                "passed": True,
                "consensus_score": consensus_score,
                "up_amount": up_amount,
                "breakdown": {
                    "gemma": gemma_score,
                    "qwen": qwen_analysis.benefit_score,
                    "vision": vision_score
                }
            }
        else:
            return {
                "passed": False,
                "reason": "Below consensus threshold",
                "score": consensus_score,
                "threshold": self.consensus_threshold
            }

    def get_base_reward(self, action_type):
        """Base UP$ rewards per action type"""
        rewards = {
            "list_item": 1.0,
            "sell_item": 2.0,
            "host_storage": 0.01,
            "invite_friend": 10.0,
            "governance_vote": 0.1,
            "complete_task": 5.0,
            "mentor_user": 3.0,
        }
        return rewards.get(action_type, 0.0)
```

#### 3. UP$ Minting (Only if CABR Passes)

```solidity
// UPSBioDecayEngine.sol

contract UPSBioDecayEngine {
    mapping(address => uint256) public cabrValidatedMints;
    address public cabrOracleAddress;

    event UPSMinted(
        address indexed user,
        uint256 amount,
        string actionType,
        uint256 cabrScore,
        uint256 timestamp
    );

    /**
     * Mint UP$ - ONLY callable by CABR Oracle
     */
    function mintUPS(
        address user,
        uint256 amount,
        string memory actionType,
        uint256 cabrScore
    ) external onlyCABROracle {
        require(cabrScore >= CONSENSUS_THRESHOLD, "CABR score too low");
        require(amount > 0, "Amount must be positive");

        // Mint to user's LIQUID wallet
        userStates[user].liquidUPS += amount;
        userStates[user].lastActivityTime = block.timestamp;
        userStates[user].lastDecayTick = block.timestamp;

        // Reset decay to minimum (fresh activity)
        userStates[user].daysInactive = 0;
        userStates[user].currentLambda = LAMBDA_MIN;

        // Track total mints
        cabrValidatedMints[user] += amount;
        totalUPSSupply += amount;

        emit UPSMinted(user, amount, actionType, cabrScore, block.timestamp);
    }

    modifier onlyCABROracle() {
        require(msg.sender == cabrOracleAddress, "Only CABR oracle can mint");
        _;
    }
}
```

#### 4. Bio-Decay Starts Immediately

```typescript
// Client-side notification after minting
async function onUPSMinted(userId, amount, actionType) {
  // Calculate decay projection
  const decayRate = await bioDecay.getCurrentDecayRate(userId);
  const projectedDecay7Days = amount * (1 - Math.exp(-decayRate * 7));

  // Show notification with urgency
  showNotification({
    type: "success",
    title: `You earned ${amount.toFixed(2)} UP$!`,
    message: `Action: ${actionType}`,
    warning: `${projectedDecay7Days.toFixed(2)} UP$ will decay in 7 days if unstaked`,
    cta: {
      primary: "Stake Now (Stop Decay)",
      secondary: "View Details"
    }
  });

  // Start decay timer UI
  startDecayTimerUI(userId, amount, decayRate);
}
```

## CABR Anti-Gaming Mechanisms

### Pattern Detection (Qwen Analysis)

```python
class AntiGamingDetector:
    """
    Detects and prevents gaming patterns
    """

    def detect_spam(self, user_history):
        """Detect spam listing patterns"""
        recent_actions = user_history.last_24h

        # Too many listings in short time?
        if len(recent_actions) > 20:
            return {
                "gaming": True,
                "pattern": "excessive_listing_rate",
                "penalty": "temporary_ban_24h"
            }

        # Identical descriptions (copy-paste)?
        descriptions = [a.description for a in recent_actions]
        if len(set(descriptions)) < len(descriptions) * 0.5:
            return {
                "gaming": True,
                "pattern": "duplicate_descriptions",
                "penalty": "reduce_rewards_50pct"
            }

        # Fake transactions (self-buying)?
        buyer_sellers = [(a.buyer, a.seller) for a in user_history.sales]
        if self.detect_self_trading(buyer_sellers):
            return {
                "gaming": True,
                "pattern": "self_trading",
                "penalty": "permanent_ban"
            }

        return {"gaming": False}

    def detect_invite_farming(self, inviter, invitees):
        """Detect fake invite chains"""

        # All invitees from same IP?
        ips = [invitee.ip_address for invitee in invitees]
        if len(set(ips)) < 3:  # Less than 3 unique IPs
            return {
                "gaming": True,
                "pattern": "same_ip_invites",
                "penalty": "void_all_invite_rewards"
            }

        # Invitees never take actions?
        inactive_rate = sum(1 for i in invitees if i.action_count == 0) / len(invitees)
        if inactive_rate > 0.7:  # 70% inactive
            return {
                "gaming": True,
                "pattern": "inactive_invitee_farming",
                "penalty": "reduce_invite_rewards_75pct"
            }

        return {"gaming": False}
```

### Vision DAE Quality Checks

```python
class VisionQualityValidator:
    """
    Uses Gemini Vision API to validate image quality
    """

    async def validate_listing_photo(self, image_data):
        """
        Checks:
        - Not blurry
        - Shows actual item (not screenshot)
        - Reasonable lighting
        - No misleading images
        """

        analysis = await gemini_vision.analyze(image_data, prompt="""
        Evaluate this listing photo for quality:
        1. Is it blurry or out of focus?
        2. Does it show a real physical item (not screenshot)?
        3. Is lighting adequate?
        4. Is it misleading (wrong item, stock photo)?

        Return JSON: {
          "quality_score": 0.0-1.0,
          "blurry": boolean,
          "real_item": boolean,
          "adequate_lighting": boolean,
          "misleading": boolean,
          "reasoning": "..."
        }
        """)

        # Reject if fails any check
        if analysis.blurry or not analysis.real_item or analysis.misleading:
            return {
                "passed": False,
                "score": 0.0,
                "reason": analysis.reasoning
            }

        return {
            "passed": True,
            "score": analysis.quality_score,
            "details": analysis
        }
```

## BTC Reserve Correlation

**Critical**: UP$ supply MUST correlate with BTC reserve growth.

```python
class BTCReserveCorrelation:
    """
    Ensure UP$ minting doesn't exceed BTC backing capacity
    """

    def check_minting_limit(self, requested_mint_amount):
        """
        Prevent inflation beyond BTC reserves
        """

        # Current state
        total_ups_supply = self.get_total_ups()
        btc_reserve_value_usd = self.get_btc_reserve_value()

        # Calculate backing ratio
        ups_value_per_token = btc_reserve_value_usd / total_ups_supply if total_ups_supply > 0 else 0

        # New supply after mint
        new_total_supply = total_ups_supply + requested_mint_amount
        new_backing_ratio = btc_reserve_value_usd / new_total_supply

        # Minimum backing ratio: 0.1 (10% BTC-backed)
        MIN_BACKING_RATIO = 0.1

        if new_backing_ratio < MIN_BACKING_RATIO:
            return {
                "allowed": False,
                "reason": "Would dilute BTC backing below minimum",
                "current_ratio": new_backing_ratio,
                "minimum_ratio": MIN_BACKING_RATIO,
                "max_mintable": self.calculate_max_mintable(btc_reserve_value_usd, total_ups_supply)
            }

        return {
            "allowed": True,
            "new_backing_ratio": new_backing_ratio
        }

    def calculate_max_mintable(self, btc_reserve, current_supply):
        """How much UP$ can be minted without breaking backing ratio?"""
        max_supply = btc_reserve / MIN_BACKING_RATIO
        return max_supply - current_supply
```

## Complete Flow Example (GotJunk)

```
User lists item with photo
        ↓
CABR Phase 1: Gemma classifies (furniture, good condition) → 0.85
        ↓
CABR Phase 2: Qwen analyzes (no gaming, reasonable price) → 0.75
        ↓
CABR Phase 3: Vision DAE (clear photo, real item) → 0.90
        ↓
Consensus Score: 0.85*0.3 + 0.75*0.5 + 0.90*0.2 = 0.81
        ↓
Threshold Check: 0.81 >= 0.618 ✓ PASSED
        ↓
Calculate Mint: base 1.0 UP$ * quality 0.81 = 0.81 UP$
        ↓
BTC Check: New supply ratio 0.15 >= 0.1 ✓ ALLOWED
        ↓
Mint UP$ to user's LIQUID wallet
        ↓
Start Decay Timer: λ = λ_min (0.005/day)
        ↓
Notify User: "0.81 UP$ earned → Stake to stop decay"
        ↓
User stakes in JUNK$ → Moves to ICE state → Decay stops
```

## Summary: Why CABR is Critical

1. **Quality Control**: Multi-agent consensus prevents spam
2. **Anti-Gaming**: Pattern detection stops exploitation
3. **Value Correlation**: Ensures UP$ ~ BTC reserve growth
4. **Decentralized Trust**: No single authority can mint
5. **Beneficial Alignment**: Only beneficial actions create value

**Without CABR**: Arbitrary minting → Inflation → Value collapse
**With CABR**: Validated minting → Scarcity → Sustainable value

---

*Every UP$ in circulation represents a CABR-validated beneficial action. This is the foundation of the FoundUps economy.*
