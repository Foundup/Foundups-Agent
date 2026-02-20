# Critical Analysis: FoundUps Economic Model

**Date**: 2026-02-10
**Purpose**: Deep analysis of potential failure modes and improvements based on external research

## Research Sources

- [Demurrage Currency (Wikipedia)](https://en.wikipedia.org/wiki/Demurrage_(currency)) - Gesell's theory, Freicoin lessons
- [Dual Token Model Pitfalls (CoinDesk)](https://www.coindesk.com/opinion/2022/07/22/to-use-or-hold-solving-the-classic-crypto-conundrum-with-a-dual-token-model)
- [Terra Luna Collapse Analysis (Harvard)](https://corpgov.law.harvard.edu/2023/05/22/anatomy-of-a-run-the-terra-luna-crash/)
- [Moloch DAO Rage Quit](https://molochdao.com/docs/introduction/wtf-is-moloch/)
- [Bonding Curves for Sustainability](https://medium.com/bonding-curve-research-group/exploring-bonding-curves-differentiating-primary-secondary-automated-market-makers-49ff51cb4563)
- [DeFi Circuit Breakers](https://olympixai.medium.com/circuit-breakers-in-web3-a-comprehensive-analysis-of-defis-emergency-brake-d76f838226f2)

---

## 1. POTENTIAL FAILURE MODES

### 1.1 Death Spiral Risk (Terra-style)

**Current Design**:
- BTC Reserve backs UPS supply
- If BTC crashes → reserve value drops → UPS capacity shrinks

**Failure Scenario**:
```
BTC crashes 50%
→ Reserve value halves
→ UPS capacity shrinks
→ Users panic, rush to convert F_i → UPS
→ 11% fee angers users
→ Users dump UPS for external
→ Demurrage accelerates on remaining wallets
→ More panic
→ DEATH SPIRAL
```

**Lesson from Terra**: Algorithmic backing without real collateral floor = disaster. Luna supply went 1B → 6T in 3 days.

### 1.2 Demurrage Subversion (Freicoin Problem)

**Current Design**:
- 0.5%-5%/month decay on LIQUID UPS
- Relief activities reset timer

**Failure Scenario**:
```
Users game relief activities:
- Fake "list_item" events
- Sybil accounts for "invite_friend" rewards
- Move funds to ICE right before decay, unstake after
- Create "decay avoidance" bots
```

**Lesson from Freicoin**: "Like Ripple, Freicoin's controlling body holds 80% of the currency... This has led some to try and subvert the process, removing demurrage altogether."

### 1.3 Orderbook Illiquidity

**Current Design**:
- F_i traded on orderbook (buy/sell orders)
- 2% trading fee

**Failure Scenario**:
```
Low user count → no counterparties
→ Wide bid-ask spread (e.g., bid: 0.5, ask: 2.0)
→ Users can't exit at fair price
→ Frustration → abandonment
OR: Whale manipulation possible with thin orderbook
```

### 1.4 Bootstrap Cold Start

**Current Design**:
- Subscriptions → BTC → backs UPS
- No subscriptions = no BTC = no UPS

**Failure Scenario**:
```
Day 1: 0 users, 0 BTC, 0 UPS capacity
→ No incentive to join (no UPS to earn)
→ Remains at 0
→ Chicken and egg never solved
```

### 1.5 Unfair Exit (Anti-Moloch)

**Current Design**:
- 11% exit fee on MINED F_i
- 8% round-trip on STAKED F_i

**Failure Scenario**:
```
FoundUp fails or rug pulls
→ Users want to exit
→ 11% fee = punitive
→ Users feel TRAPPED
→ Reputation damage
→ New users avoid system
```

**Lesson from Moloch**: "All members can withdraw their share of assets from it by ragequitting their shares... pro-rata claim on the treasury's assets."

---

## 2. PROPOSED IMPROVEMENTS

### 2.1 Circuit Breaker System

**Problem Solved**: Death spiral prevention

**Implementation**:
```python
class CircuitBreaker:
    """ERC-7265 inspired circuit breaker."""

    BACKING_THRESHOLD = 0.80  # 80%
    OUTFLOW_THRESHOLD = 0.10  # 10% of supply per day
    COOLDOWN_PERIOD = 24 * 3600  # 24 hours

    def check_triggers(self, reserve: BTCReserve, daily_outflow: float):
        """Check if circuit breaker should activate."""

        if reserve.backing_ratio < self.BACKING_THRESHOLD:
            return self._activate_backing_breaker()

        if daily_outflow > self.OUTFLOW_THRESHOLD * reserve.total_ups_minted:
            return self._activate_outflow_breaker()

        return False

    def _activate_backing_breaker(self):
        """Actions when backing drops too low."""
        # 1. Pause new exits temporarily
        # 2. Reduce demurrage rate to 0
        # 3. Halt F_i → UPS conversions
        # 4. Notify users via UI
        # 5. Await backing recovery or governance decision
        return "BACKING_BREAKER_ACTIVE"

    def _activate_outflow_breaker(self):
        """Actions when outflows exceed threshold."""
        # Queue exits instead of blocking
        # Process gradually (10% of queue per hour)
        return "OUTFLOW_BREAKER_ACTIVE"
```

**Rationale**: "When triggered, [circuit breakers] temporarily halt protocol-wide token outflows when a threshold is exceeded."

### 2.2 Bonding Curve for F_i (Replace Orderbook)

**Problem Solved**: Orderbook illiquidity

**Implementation**:
```python
class FiBondingCurve:
    """Guaranteed liquidity via bonding curve."""

    def __init__(self, foundup_id: str, initial_reserve: float):
        self.foundup_id = foundup_id
        self.ups_reserve = initial_reserve  # UPS in curve
        self.fi_supply = 0.0  # F_i minted by curve

        # Bancor-style constant product
        self.reserve_ratio = 0.5  # 50% reserve

    def buy_fi(self, ups_amount: float) -> float:
        """Buy F_i with UPS - always works."""
        # price = reserve / (supply * ratio)
        # More buys → higher price (scarcity)
        fi_out = self._calculate_purchase(ups_amount)
        self.ups_reserve += ups_amount
        self.fi_supply += fi_out
        return fi_out

    def sell_fi(self, fi_amount: float) -> float:
        """Sell F_i for UPS - always works."""
        # Guaranteed exit at fair price
        ups_out = self._calculate_sale(fi_amount)
        self.fi_supply -= fi_amount
        self.ups_reserve -= ups_out
        return ups_out

    def get_spot_price(self) -> float:
        """Current price of F_i in UPS."""
        if self.fi_supply == 0:
            return 1.0  # Genesis price
        return self.ups_reserve / (self.fi_supply * self.reserve_ratio)
```

**Rationale**: "Bonding curves provide a fair price discovery mechanism, ensure constant liquidity from day one, and create a sustainable funding model."

**Advantage over Orderbook**:
- No counterparty needed
- Guaranteed exit at market price
- No whale manipulation (slippage scales with size)
- Automatic price discovery

### 2.3 Rage Quit Option

**Problem Solved**: Unfair exit, trapped users

**Implementation**:
```python
class RageQuitAdapter:
    """Moloch-style fair exit for failing FoundUps."""

    FAILURE_CRITERIA = {
        "no_activity_epochs": 12,  # 1 year of no work
        "backing_below": 0.50,  # <50% backed
        "founder_exit": True,  # Founder abandoned
    }

    GRACE_PERIOD_DAYS = 7
    RAGEQUIT_FEE = 0.02  # 2% (vs 11% normal)

    def is_foundup_failing(self, foundup_id: str) -> bool:
        """Check if FoundUp qualifies for rage quit."""
        # Any of these triggers rage quit eligibility
        pass

    def rage_quit(self, human_id: str, foundup_id: str, fi_amount: float):
        """Exit at pro-rata value with minimal fee."""
        if not self.is_foundup_failing(foundup_id):
            raise ValueError("Rage quit only for failing FoundUps")

        # Calculate pro-rata share of treasury
        total_fi = get_total_fi_supply(foundup_id)
        treasury_value = get_treasury_value(foundup_id)

        pro_rata = (fi_amount / total_fi) * treasury_value
        fee = pro_rata * self.RAGEQUIT_FEE

        return pro_rata - fee
```

**Rationale**: "The most important property of the treasury is that all members can withdraw their share of assets from it by ragequitting... pro-rata claim."

### 2.4 Sustainable Demurrage Rate

**Problem Solved**: Over-aggressive decay driving users away

**Current**: 0.5%-5%/month (up to 60%/year)
**Freicoin**: 4.9%/year

**Proposal**: Reduce maximum demurrage

```python
class AdaptiveDemurrage:
    """Gentler, sustainable decay rates."""

    # Reduced from original
    LAMBDA_MIN = 0.005 / 30  # 0.5%/month (unchanged)
    LAMBDA_MAX = 0.02 / 30   # 2%/month (was 5%) = 24%/year max

    # Demurrage pauses when system stressed
    def get_effective_rate(self, base_rate: float, reserve: BTCReserve):
        if reserve.backing_ratio < 1.0:
            # Reduce demurrage when underbacked
            # Users shouldn't be penalized for system issues
            reduction = reserve.backing_ratio
            return base_rate * reduction
        return base_rate
```

**Rationale**: "These [demurrage] experiments were always local and never lasted more than a few months. This article shows that TRUST is the main issue."

### 2.5 Bootstrap Reserve Fund

**Problem Solved**: Cold start problem

**Implementation**:
```python
class BootstrapReserve:
    """Initial BTC seeding to solve chicken-and-egg."""

    BOOTSTRAP_BTC = 1.0  # Protocol seeds 1 BTC initially
    EARLY_USER_BONUS = 2.0  # 2x UPS allocation for first 100 users

    def __init__(self):
        # Protocol commits initial BTC
        self.btc_reserve = get_btc_reserve()
        self.btc_reserve.receive_btc(
            self.BOOTSTRAP_BTC,
            BTCSourceType.SUBSCRIPTION,  # Protocol is "subscriber 0"
            human_id="protocol_bootstrap"
        )

    def is_early_user(self, user_number: int) -> bool:
        return user_number <= 100

    def get_early_bonus(self, base_allocation: float, user_number: int) -> float:
        if self.is_early_user(user_number):
            # Decreasing bonus: user 1 gets 2x, user 100 gets 1.01x
            bonus = 1.0 + (1.0 * (100 - user_number) / 100)
            return base_allocation * bonus
        return base_allocation
```

**Rationale**: Accept under-backing initially, grow into it. Early users take risk, get reward.

### 2.6 CABR-Validated Relief Activities

**Problem Solved**: Gaming relief activities

**Implementation**:
```python
class ValidatedReliefActivity:
    """CABR validates all relief activities."""

    RATE_LIMITS = {
        "list_item": 20,  # Max per day
        "invite_friend": 5,  # Max per week
        "share_boost": 10,  # Max per day
    }

    async def validate_activity(
        self,
        activity_type: str,
        human_id: str,
        proof: dict
    ) -> bool:
        # 1. Check rate limits
        if self._exceeds_rate_limit(activity_type, human_id):
            return False

        # 2. CABR multi-agent consensus
        gemma_score = await self.gemma.classify(proof)
        qwen_score = await self.qwen.analyze(proof)

        consensus = (gemma_score * 0.4) + (qwen_score * 0.6)

        # 3. Golden ratio threshold
        if consensus < 0.618:
            return False

        # 4. Grant relief
        return True
```

### 2.7 Emergency Reserve Fund

**Problem Solved**: System sustainability during stress

**Implementation**:
```python
class EmergencyReserve:
    """Ethena-style reserve for emergencies."""

    RESERVE_PERCENTAGE = 0.10  # 10% of all fees → emergency fund

    def __init__(self):
        self.emergency_btc = 0.0
        self.never_touched = True  # Transparency

    def collect_from_fee(self, fee_btc: float):
        """Route 10% of every fee to emergency fund."""
        emergency_portion = fee_btc * self.RESERVE_PERCENTAGE
        self.emergency_btc += emergency_portion
        return fee_btc - emergency_portion

    def can_use(self) -> bool:
        """Only usable when circuit breaker active."""
        return CircuitBreaker.is_active()

    def deploy_for_backing(self, amount: float):
        """Use emergency funds to restore backing."""
        if not self.can_use():
            raise ValueError("Emergency funds locked")
        # Deploy to restore backing ratio
        pass
```

**Rationale from Ethena**: "$32.7 million reserve fund... importance of adequate reserve sizing."

---

## 3. REVISED ECONOMIC FLOW

```
                         ┌─────────────────────────────────────┐
                         │        CIRCUIT BREAKER              │
                         │  (pauses exits if backing < 80%)    │
                         └─────────────────────────────────────┘
                                          │
Subscription $ ────┐                      │
                   │                      ▼
Demurrage decay ───┼──> BTC Reserve (Hotel California)
                   │         │
Exit fees ─────────┤         ├──> 10% → Emergency Reserve
                   │         │
Trading fees ──────┘         ▼
                      UPS = f(BTC Reserve)
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   LIQUID (wallet)    ICE (staked)         VAPOR (exit)
   (2%/mo max decay)  (frozen, yield)      (via bonding curve)
        │                    │                    │
        │                    │                    ▼
        │                    │            RAGE QUIT available
        │                    │            if FoundUp failing
        │                    │            (2% fee vs 11%)
        │                    │
        └───── BONDING CURVE ─────────────────────┘
               (guaranteed liquidity, no orderbook)
```

---

## 4. SIMULATION TESTS NEEDED

1. **Death Spiral Simulation**: 50% BTC crash + 30% user panic exit
2. **Demurrage Gaming**: 1000 users trying to avoid decay
3. **Bootstrap Simulation**: 0 users → 100 users growth curve
4. **Circuit Breaker Trigger**: Test thresholds and recovery
5. **Bonding Curve vs Orderbook**: Liquidity and price stability
6. **Rage Quit Abuse**: Prevent gaming of "failing FoundUp" criteria

---

## 5. OPEN QUESTIONS

1. **What is the right demurrage rate?** 2%/month max or lower?
2. **Bonding curve reserve ratio?** 50% or different?
3. **Circuit breaker thresholds?** 80% backing or different?
4. **Rage quit criteria?** What defines "failing"?
5. **Emergency fund size?** 10% of fees or more?
6. **Bootstrap BTC amount?** How much to seed?

---

## 6. NEXT STEPS

1. Implement CircuitBreaker in simulator
2. Add BondingCurve as alternative to OrderBook
3. Add RageQuit adapter
4. Reduce demurrage max rate
5. Add EmergencyReserve
6. Run failure simulations
7. Tune parameters based on results

**The goal**: A system that is **anti-fragile** - gets stronger under stress, not weaker.
