# Stream Resolver Surgical Refactoring Analysis
**Date**: 2025-01-13
**Status**: First Principles Analysis Complete
**Compliance**: WSP 3, WSP 50, WSP 84, WSP 87

---

## 🎯 EXECUTIVE SUMMARY

**Problem**: `stream_resolver.py` violates WSP 3 at **1386 lines** (exceeds 1200 line guideline)

**Root Cause**: Mixing multiple domain responsibilities:
1. Stream resolution (✅ correct)
2. Social media posting (❌ wrong domain)
3. Channel routing logic (❌ wrong domain)
4. QWEN intelligence (❌ wrong domain)

**Solution**: **Surgical extraction** using existing superior implementations (not copy-paste!)

**Outcome**: 1386 → ~1000 lines (WSP 3 compliant)

---

## 📊 COMPARATIVE ANALYSIS - EXISTING VS STREAM_RESOLVER

### 🔍 Analysis 1: Social Media Posting

#### **STREAM_RESOLVER Implementation** (Lines 1231-1324, 94 lines)
```python
def _trigger_social_media_post(self, video_id: str, stream_title: str = None, channel_id: str = None):
    # Manual config file loading
    config_path = os.path.join(...)
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Manual enabled check
    if not posting_enabled:
        return

    # Get title manually
    final_title = stream_title or self._get_stream_title(video_id)

    # Get LinkedIn page manually
    linkedin_page = self._get_linkedin_page_for_channel(channel_id)

    # Call social_poster (PlatformPostingService)
    linkedin_result = self.social_poster.post_to_linkedin(...)
    x_result = self.social_poster.post_to_x(...)

    # Manual result checking
    if linkedin_result and linkedin_result.status.name == "SUCCESS":
        self.logger.info(...)
```

**Issues**:
- ❌ Duplicate config loading logic (should be in orchestrator)
- ❌ Manual title fetching (should be in orchestrator)
- ❌ Manual routing logic (should be in routing module)
- ❌ Manual result checking (should use PostingResult dataclass)
- ❌ No error recovery
- ❌ No duplicate prevention

#### **PlatformPostingService** (460 lines, production-ready)
```python
class PlatformPostingService:
    def __init__(self, browser_timeout: int = 120, posting_delay: int = 15):
        # Proper initialization with rate limiting
        self.browser_timeout = browser_timeout
        self.posting_delay = posting_delay
        self.last_post_time = 0

    def post_to_linkedin(self, title: str, url: str, linkedin_page: str) -> PostingResult:
        # ✅ Built-in page validation with mapping
        page_mapping = {
            "104834798": "GeoZai (Move2Japan)",
            "165749317": "UnDaoDu",
            "1263645": "FoundUps"
        }

        # ✅ Automatic rate limiting
        if time_since_last < self.posting_delay:
            time.sleep(delay_needed)

        # ✅ Proper error handling with typed results
        try:
            result = subprocess.run(...)
            return PostingResult(
                platform="linkedin",
                status=PostingStatus.SUCCESS,
                duration=time.time() - start_time
            )
        except subprocess.TimeoutExpired:
            return PostingResult(
                status=PostingStatus.TIMEOUT,
                error=f"Timeout after {self.browser_timeout}s"
            )

    def post_to_both_platforms(self, title, url, linkedin_page, x_account):
        # ✅ Coordinated dual posting with delay
        linkedin_result = self.post_to_linkedin(...)
        time.sleep(2)  # Platform delay
        x_result = self.post_to_x(...)
        return linkedin_result, x_result
```

**Advantages**:
- ✅ Typed results with PostingResult dataclass
- ✅ Built-in rate limiting (posting_delay)
- ✅ Browser timeout handling
- ✅ Platform coordination (`post_to_both_platforms`)
- ✅ Proper error categorization (SUCCESS, FAILED, TIMEOUT, etc.)
- ✅ Validation and logging at service level
- ✅ **Tested in production** with 27 tests

#### **VERDICT**: PlatformPostingService is SUPERIOR
**Action**: **DELETE** `_trigger_social_media_post()` entirely (already not being called at line 1175)

---

### 🔍 Analysis 2: LinkedIn Routing Logic

#### **STREAM_RESOLVER Implementation** (Lines 789-831, 43 lines)
```python
def _get_linkedin_page_for_channel(self, channel_id: str) -> str:
    # Load config file
    config_path = os.path.join(...)
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Check channel-specific routing
    channel_config = config.get('channel_routing', {}).get(channel_id)
    if channel_config:
        return channel_config.get('linkedin_page_id')

    # Fallback to default
    default = config.get('default_routing', {})
    return default.get('linkedin_page_id', '1263645')
```

**Issues**:
- ❌ Loads JSON config on every call (no caching)
- ❌ Duplicate logic with PlatformPostingService page validation
- ❌ No validation of returned page IDs
- ❌ Hardcoded fallback value

#### **PlatformPostingService Implementation** (Lines 86-115)
```python
# Inside post_to_linkedin method:
page_mapping = {
    "104834798": "GeoZai (Move2Japan)",
    "165749317": "UnDaoDu",
    "1263645": "FoundUps"
}

# Validation built-in
if linkedin_page not in page_mapping:
    return PostingResult(
        status=PostingStatus.FAILED,
        error=f"Unknown page ID: {linkedin_page}"
    )

# Additional mismatch detection
if "Move2Japan" in title and linkedin_page != "104834798":
    self.logger.warning(f"⚠️ MISMATCH detected")
```

**Advantages**:
- ✅ No file I/O (in-memory mapping)
- ✅ Built-in validation
- ✅ Mismatch detection using title
- ✅ Clear error messages

#### **BETTER APPROACH**: Create config module
```python
# modules/platform_integration/social_media_orchestrator/src/channel_routing.py
class ChannelRouting:
    """Centralized channel → LinkedIn page mapping"""

    MAPPINGS = {
        'UCSNTUXjAgpd4sgWYP0xoJgw': {  # UnDaoDu
            'linkedin_page': '165749317',
            'x_account': 'undaodu',
            'name': 'UnDaoDu'
        },
        'UC-LSSlOZwpGIRIYihaz8zCw': {  # FoundUps
            'linkedin_page': '1263645',
            'x_account': 'foundups',
            'name': 'FoundUps'
        },
        'UCklMTNnu5POwRmQsg5JJumA': {  # Move2Japan
            'linkedin_page': '104834798',  # GeoZai
            'x_account': 'geozai',
            'name': 'Move2Japan'
        }
    }

    @classmethod
    def get_linkedin_page(cls, channel_id: str) -> str:
        """Get LinkedIn page ID for YouTube channel"""
        mapping = cls.MAPPINGS.get(channel_id)
        if not mapping:
            raise ValueError(f"Unknown channel: {channel_id}")
        return mapping['linkedin_page']
```

#### **VERDICT**: Create new channel_routing.py module
**Action**:
1. Create `modules/platform_integration/social_media_orchestrator/src/channel_routing.py`
2. Move all routing logic there
3. Update stream_resolver to import from routing module
4. Update PlatformPostingService to use routing module

---

### 🔍 Analysis 3: QWEN Pattern Selection

#### **STREAM_RESOLVER Implementation** (Lines 729-787, 59 lines)
```python
def _select_channel_by_pattern(self, channel_predictions: Dict, available_channels: List):
    # Score each channel
    channel_scores = {}
    for channel_id in available_channels:
        if channel_id in channel_predictions:
            pred = channel_predictions[channel_id]
            confidence = pred.get('confidence', 0.0)

            # Time-based boost
            predicted_time_str = pred.get('predicted_time')
            if predicted_time_str:
                predicted_time = parser.parse(predicted_time_str)
                time_diff = abs((predicted_time - now).total_seconds())
                if time_diff < 7200:  # 2 hours
                    time_boost = (7200 - time_diff) / 7200
                    confidence *= (1.0 + time_boost)

            channel_scores[channel_id] = confidence

    # 80/20 exploration/exploitation
    if random.random() < 0.8:
        return max(channel_scores.keys(), key=lambda k: channel_scores[k])
    else:
        return random.choice(available_channels)

def _calculate_pattern_based_delay(self, channel_id, channel_predictions, attempt, base_delay):
    exp_delay = min(base_delay * (2 ** min(attempt - 1, 4)), 60.0)

    if channel_id in channel_predictions:
        confidence = channel_predictions[channel_id].get('confidence', 0.0)
        if confidence > 0.7:
            exp_delay *= 0.5  # High confidence
        elif confidence > 0.4:
            exp_delay *= 0.75  # Medium confidence

    return exp_delay
```

**Strengths**:
- ✅ Time-aware prediction boosting
- ✅ Exploration/exploitation balance (80/20)
- ✅ Confidence-based delay adjustment

#### **QWEN_YOUTUBE_INTEGRATION Implementation** (404 lines)
```python
class ChannelIntelligence:
    def should_check_now(self) -> Tuple[bool, str]:
        """Intelligent check timing based on learned patterns"""
        now = datetime.now()

        # Check cooldown from last 429 error
        if self.last_429_time:
            cooldown_remaining = 300 - (now - self.last_429_time).total_seconds()
            if cooldown_remaining > 0:
                return False, f"Cooling down for {cooldown_remaining:.0f}s after rate limit"

        # Check heat level (0-10 scale)
        if self.heat_level >= 5:
            return False, f"Channel heat too high ({self.heat_level}/10)"

        return True, "Safe to check"

class QwenYouTube:
    def get_channel_profile(self, channel_id: str, channel_name: str) -> ChannelIntelligence:
        """Get or create channel intelligence profile"""
        if channel_id not in self.channel_profiles:
            self.channel_profiles[channel_id] = ChannelIntelligence(channel_id, channel_name)
        return self.channel_profiles[channel_id]

    def sort_channels_by_intelligence(self, channels: List) -> List:
        """Sort channels by streaming likelihood"""
        scored = []
        for ch_id, name in channels:
            profile = self.get_channel_profile(ch_id, name)

            # BOOST 1: Heat level (recent activity)
            heat_score = profile.heat_level

            # BOOST 2: Pattern matching (typical streaming times)
            pattern_score = profile.get_time_pattern_score()

            # BOOST 3: Success rate
            success_score = profile.stream_success_rate()

            total_score = heat_score + pattern_score + success_score
            scored.append((ch_id, name, total_score, profile))

        # Sort by score descending
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored

    def record_stream_found(self, channel_id: str, channel_name: str = ""):
        """Learn from successful stream detection"""
        profile = self.get_channel_profile(channel_id, channel_name)
        profile.record_stream_found()

        # Pattern learning
        profile.stream_times.append(datetime.now())
        profile.heat_level = min(profile.heat_level + 2, 10)
```

**Advantages**:
- ✅ **Rate limit awareness** (429 error cooldown)
- ✅ **Heat level tracking** (0-10 scale)
- ✅ **Multi-factor scoring** (heat + pattern + success rate)
- ✅ **Pattern learning** (records stream times)
- ✅ **Persistent profiles** (maintains state across checks)
- ✅ **Global heat level** (system-wide rate limit awareness)

#### **HYBRID APPROACH** (Best of Both)
```python
# In qwen_youtube_integration.py - ADD these methods:

def select_channel_by_pattern(
    self,
    channel_predictions: Dict[str, Dict],
    available_channels: List[str]
) -> str:
    """
    Select next channel using QWEN intelligence + pattern predictions.
    Combines existing heat/pattern logic with prediction confidence.
    """
    scored = []
    for channel_id in available_channels:
        profile = self.get_channel_profile(channel_id)

        # BASE SCORE: QWEN intelligence
        base_score = profile.heat_level + profile.get_time_pattern_score()

        # BOOST: External pattern predictions (from database)
        if channel_id in channel_predictions:
            pred = channel_predictions[channel_id]
            confidence = pred.get('confidence', 0.0)

            # Time proximity boost (from stream_resolver logic)
            predicted_time_str = pred.get('predicted_time')
            if predicted_time_str:
                predicted_time = parser.parse(predicted_time_str)
                time_diff = abs((predicted_time - datetime.now()).total_seconds())
                if time_diff < 7200:  # Within 2 hours
                    time_boost = (7200 - time_diff) / 7200
                    confidence *= (1.0 + time_boost)

            base_score += confidence * 10  # Scale confidence to 0-10

        scored.append((channel_id, base_score, profile))

    # Sort by score
    scored.sort(key=lambda x: x[1], reverse=True)

    # Exploration vs exploitation (80/20)
    if random.random() < 0.8:
        return scored[0][0]  # Best channel
    else:
        return random.choice(available_channels)  # Explore

def calculate_pattern_based_delay(
    self,
    channel_id: str,
    channel_predictions: Dict,
    attempt: int,
    base_delay: float
) -> float:
    """
    Calculate check delay using QWEN intelligence + pattern confidence.
    """
    profile = self.get_channel_profile(channel_id)

    # Check if we should even check now
    should_check, reason = profile.should_check_now()
    if not should_check:
        # Force longer delay if in cooldown
        return 300.0  # 5 minutes minimum

    # Base exponential backoff
    exp_delay = min(base_delay * (2 ** min(attempt - 1, 4)), 60.0)

    # ADJUST: Based on QWEN heat level
    if profile.heat_level >= 7:
        exp_delay *= 2.0  # High heat = longer delay
    elif profile.heat_level <= 3:
        exp_delay *= 0.5  # Low heat = faster checks

    # ADJUST: Based on pattern confidence (from stream_resolver logic)
    if channel_id in channel_predictions:
        confidence = channel_predictions[channel_id].get('confidence', 0.0)
        if confidence > 0.7:
            exp_delay *= 0.5  # High confidence = check sooner
        elif confidence > 0.4:
            exp_delay *= 0.75  # Medium confidence = slight speedup

    return max(5.0, exp_delay)  # Never less than 5 seconds
```

#### **VERDICT**: Enhance QWEN with stream_resolver logic
**Action**:
1. Add `select_channel_by_pattern()` to qwen_youtube_integration.py
2. Add `calculate_pattern_based_delay()` to qwen_youtube_integration.py
3. Keep QWEN's rate limit awareness (superior)
4. Keep stream_resolver's time proximity boost (useful)
5. Delete stream_resolver methods after migration

---

## 🎯 SURGICAL REFACTORING PLAN

### Phase 1: Delete Unused Social Media Posting (SAFE)
**Time**: 5 minutes | **Risk**: ⚠️ None (already not being called)

```bash
# Line 1175 shows it's already commented out:
# self._trigger_social_media_post(video_id, stream_title)

# Action: Delete lines 1231-1324 (94 lines)
```

**Result**: 1386 → 1292 lines

---

### Phase 2: Create Channel Routing Module (NEW)
**Time**: 30 minutes | **Risk**: ⚠️ Low (new module, doesn't break existing)

**Create**: `modules/platform_integration/social_media_orchestrator/src/channel_routing.py`

```python
"""
Channel Routing Configuration
Maps YouTube channels to social media accounts
WSP 3: Functional distribution - routing is social media concern
"""

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ChannelRouting:
    linkedin_page: str
    x_account: str
    channel_name: str

class SocialMediaRouter:
    """Central routing for channel → social media mapping"""

    MAPPINGS = {
        'UCSNTUXjAgpd4sgWYP0xoJgw': ChannelRouting(
            linkedin_page='165749317',
            x_account='undaodu',
            channel_name='UnDaoDu'
        ),
        'UC-LSSlOZwpGIRIYihaz8zCw': ChannelRouting(
            linkedin_page='1263645',
            x_account='foundups',
            channel_name='FoundUps'
        ),
        'UCklMTNnu5POwRmQsg5JJumA': ChannelRouting(
            linkedin_page='104834798',  # GeoZai
            x_account='geozai',
            channel_name='Move2Japan'
        )
    }

    @classmethod
    def get_routing(cls, channel_id: str) -> Optional[ChannelRouting]:
        """Get routing for YouTube channel"""
        return cls.MAPPINGS.get(channel_id)

    @classmethod
    def get_linkedin_page(cls, channel_id: str) -> str:
        """Get LinkedIn page ID (backward compatible)"""
        routing = cls.get_routing(channel_id)
        if not routing:
            return '1263645'  # Default to FoundUps
        return routing.linkedin_page
```

**Delete from stream_resolver**: Lines 789-831 (43 lines)
**Delete from stream_resolver**: Lines 720-727 (channel display names → move to config)

**Update stream_resolver**:
```python
# Replace line 790 call with:
from modules.platform_integration.social_media_orchestrator.src.channel_routing import SocialMediaRouter
linkedin_page = SocialMediaRouter.get_linkedin_page(channel_id)
```

**Result**: 1292 → 1241 lines

---

### Phase 3: Enhance QWEN with Pattern Logic (SURGICAL)
**Time**: 60 minutes | **Risk**: ⚠️ Medium (requires testing)

**Add to qwen_youtube_integration.py**:
```python
def select_channel_by_pattern(self, channel_predictions, available_channels):
    # [Implementation from hybrid approach above]

def calculate_pattern_based_delay(self, channel_id, channel_predictions, attempt, base_delay):
    # [Implementation from hybrid approach above]
```

**Update stream_resolver.py** (lines 1010-1020):
```python
# OLD:
current_channel_id = self._select_channel_by_pattern(channel_predictions, channels_queue)

# NEW:
if self.qwen:
    current_channel_id = self.qwen.select_channel_by_pattern(channel_predictions, channels_queue)
else:
    current_channel_id = channels_queue.pop(0)  # Fallback
```

**Update stream_resolver.py** (lines 769-787):
```python
# OLD:
delay = self._calculate_pattern_based_delay(channel_id, channel_predictions, attempt, base_delay)

# NEW:
if self.qwen:
    delay = self.qwen.calculate_pattern_based_delay(channel_id, channel_predictions, attempt, base_delay)
else:
    delay = min(base_delay * (2 ** min(attempt - 1, 4)), 60.0)  # Simple fallback
```

**Delete from stream_resolver**:
- Lines 729-767: `_select_channel_by_pattern()` (39 lines)
- Lines 769-787: `_calculate_pattern_based_delay()` (19 lines)

**Result**: 1241 → 1183 lines

---

## 📊 FINAL STATE

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total Lines** | 1386 | 1183 | **-203 lines** ✅ |
| **WSP 3 Compliant** | ❌ No | ✅ Yes | **< 1200** |
| **Social Posting** | Duplicate | Removed | Use PlatformPostingService |
| **Channel Routing** | Inline | Module | channel_routing.py |
| **QWEN Logic** | Duplicate | Enhanced | qwen_youtube_integration.py |
| **Code Quality** | Mixed concerns | Clean | Single responsibility |

---

## 🧪 TESTING STRATEGY

### Phase 1 Testing (Delete Social Posting)
```bash
# 1. Verify no callers
grep -r "_trigger_social_media_post" modules/

# 2. Run stream resolver tests
pytest modules/platform_integration/stream_resolver/tests/ -v -k test_resolve

# 3. Verify imports still work
python -c "from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver"
```

### Phase 2 Testing (Channel Routing)
```bash
# 1. Test new routing module
python -c "from modules.platform_integration.social_media_orchestrator.src.channel_routing import SocialMediaRouter; print(SocialMediaRouter.get_linkedin_page('UC-LSSlOZwpGIRIYihaz8zCw'))"

# 2. Verify stream_resolver imports
pytest modules/platform_integration/stream_resolver/tests/ -v

# 3. Test posting service integration
pytest modules/platform_integration/social_media_orchestrator/tests/test_core_modules.py -v -k posting
```

### Phase 3 Testing (QWEN Enhancement)
```bash
# 1. Test QWEN methods
python -c "from modules.communication/livechat.src.qwen_youtube_integration import get_qwen_youtube; q = get_qwen_youtube(); print(q.select_channel_by_pattern({}, ['UC-LSSlOZwpGIRIYihaz8zCw']))"

# 2. Full stream resolver test
pytest modules/platform_integration/stream_resolver/tests/ -v

# 3. Integration test with NO-QUOTA mode
python modules/platform_integration/stream_resolver/src/stream_resolver.py
```

---

## 🎓 KEY LEARNINGS

### 1. **Existing Modules Are Superior**
- PlatformPostingService has 27 tests and production usage
- QWEN has rate limit awareness (critical for YouTube API)
- Don't recreate what exists - enhance it!

### 2. **Configuration Belongs in Modules**
- Channel routing is social media concern, not stream resolution
- Creating channel_routing.py makes this explicit
- Enables testing and reuse across modules

### 3. **QWEN Intelligence is Powerful**
- Heat level tracking prevents rate limits
- Pattern learning improves over time
- Combining database predictions + QWEN = superior to either alone

### 4. **WSP 3 is About Responsibilities**
- Stream resolver should ONLY resolve streams
- Social posting belongs in social_media_orchestrator
- Intelligence belongs in qwen modules
- Routing belongs in configuration modules

---

## 🚀 NEXT STEPS

1. **Get Approval** from 012 for surgical plan
2. **Execute Phase 1** (5 min, zero risk)
3. **Execute Phase 2** (30 min, low risk)
4. **Execute Phase 3** (60 min, medium risk with testing)
5. **Update ModLogs** with WSP 22 compliance
6. **Run Full Test Suite** to verify no regressions
7. **Commit Changes** with proper WSP references

---

**STATUS**: ✅ Analysis Complete - Awaiting Approval to Execute

**HoloIndex Used**: ✅ Yes (found PlatformPostingService, QWEN integration, routing patterns)
**QWEN Advisor**: ✅ Yes (analyzed code quality and module health)
**First Principles**: ✅ Yes (compared implementations, identified superior approaches)
**WSP Compliance**: ✅ Yes (WSP 3, 50, 84, 87)

---

*Generated by 0102 using HoloIndex semantic search + QWEN advisor + first principles analysis*
