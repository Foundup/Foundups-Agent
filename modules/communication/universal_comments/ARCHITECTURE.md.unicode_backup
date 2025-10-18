# Universal Comments Architecture - Cross-Platform Comment System

## Executive Summary
Following WSP 42 (Universal Platform Protocol) and WSP 80 (Cube-Level DAE), this architecture provides a unified comment handling system that scales from PoC to Proto to MVP across all social media platforms.

## 1. Architecture Overview

### 1.1 Three-Tier Hierarchy (Per WSP 46)
```
Universal Comment Orchestrator (UCO)
    ├── Platform DAE Orchestrators (Domain Level)
    │   ├── YouTube Comment DAE
    │   ├── X/Twitter Comment DAE  
    │   ├── LinkedIn Comment DAE
    │   └── [Future Platform DAEs]
    └── Module Orchestrators (Implementation Level)
        ├── Comment Polling Modules
        ├── Response Generation Modules
        └── Account Management Modules
```

### 1.2 Universal Abstraction Layer (Per WSP 42)
```python
class IUniversalCommentInterface:
    """Universal interface for all platform comment systems"""
    
    # Common methods all platforms must implement
    async def poll_comments(self) -> List[Comment]
    async def post_reply(self, parent_id: str, text: str) -> bool
    async def get_mentions(self) -> List[Mention]
    async def get_thread_context(self, comment_id: str) -> Thread
    async def detect_sentiment(self, comment: Comment) -> Sentiment
    async def should_respond(self, comment: Comment) -> bool
```

## 2. Platform-Specific DAE Implementation

### 2.1 Each Platform Gets Its Own DAE (Per WSP 80)
```python
# YouTube Comment DAE
class YouTubeCommentDAE(IUniversalCommentInterface):
    """YouTube-specific implementation"""
    def __init__(self):
        self.api = YouTubeCommentAPI()  # Platform-specific
        self.memory = UniversalCommentMemory()  # Shared component
        self.processor = UniversalCommentProcessor()  # Shared component
        self.throttle = UniversalThrottleManager()  # Shared component
    
    async def poll_comments(self):
        # YouTube-specific: commentThreads.list API
        return self.api.commentThreads().list(...)
    
    async def post_reply(self, parent_id, text):
        # YouTube-specific: 50 quota units
        return self.api.comments().insert(...)

# X/Twitter Comment DAE  
class TwitterCommentDAE(IUniversalCommentInterface):
    """Twitter-specific implementation"""
    async def poll_comments(self):
        # Twitter-specific: mentions timeline API
        return self.api.mentions_timeline(...)
    
    async def post_reply(self, tweet_id, text):
        # Twitter-specific: reply to tweet
        return self.api.reply(tweet_id, text)

# LinkedIn Comment DAE
class LinkedInCommentDAE(IUniversalCommentInterface):
    """LinkedIn-specific implementation"""
    async def poll_comments(self):
        # LinkedIn-specific: socialActions API
        return self.api.get_social_actions(...)
    
    async def post_reply(self, urn, text):
        # LinkedIn-specific: create comment
        return self.api.create_comment(urn, text)
```

## 3. Shared Core Components (Per WSP 17 - Pattern Registry)

### 3.1 Reusable Across All Platforms
```python
# These components work for ALL platforms
UNIVERSAL_COMMENT_COMPONENTS = {
    "memory": "UniversalCommentMemory",      # Store/retrieve context
    "processor": "UniversalCommentProcessor", # Analyze content
    "throttle": "UniversalThrottleManager",   # Rate limiting
    "sentiment": "UniversalSentimentAnalyzer", # Detect tone
    "generator": "UniversalResponseGenerator", # Generate replies
    "learning": "UniversalPatternLearner"     # WSP 48 self-improvement
}
```

### 3.2 Platform-Specific Components
```python
# These are unique per platform
PLATFORM_SPECIFIC_COMPONENTS = {
    "youtube": {
        "api": "YouTubeCommentAPI",
        "auth": "YouTubeOAuth",
        "quota": "YouTubeQuotaManager"
    },
    "twitter": {
        "api": "TwitterAPIv2",
        "auth": "TwitterOAuth2",
        "rate_limit": "TwitterRateLimiter"
    },
    "linkedin": {
        "api": "LinkedInRestAPI",
        "auth": "LinkedInOAuth2",
        "throttle": "LinkedInThrottler"
    }
}
```

## 4. Universal Comment Orchestrator (UCO)

### 4.1 Master Orchestrator Design
```python
class UniversalCommentOrchestrator:
    """
    Coordinates all platform DAEs for unified comment management.
    Follows WSP 46 WRE orchestration pattern.
    """
    
    def __init__(self):
        # Initialize all platform DAEs
        self.platform_daes = {
            "youtube": YouTubeCommentDAE(),
            "twitter": TwitterCommentDAE(),
            "linkedin": LinkedInCommentDAE()
        }
        
        # Shared components
        self.universal_memory = UniversalCommentMemory()
        self.cross_platform_analyzer = CrossPlatformAnalyzer()
        self.unified_dashboard = UnifiedCommentDashboard()
        
    async def orchestrate_all_platforms(self):
        """Main orchestration loop for all platforms"""
        while True:
            # Parallel polling across all platforms
            tasks = []
            for platform_name, dae in self.platform_daes.items():
                tasks.append(self.process_platform(platform_name, dae))
            
            # Execute all platforms in parallel
            await asyncio.gather(*tasks)
            
            # Cross-platform learning (WSP 48)
            await self.cross_platform_learning()
            
            # Adaptive delay based on activity
            await self.universal_throttle()
    
    async def process_platform(self, platform: str, dae: IUniversalCommentInterface):
        """Process comments for a single platform"""
        # Poll for new comments
        comments = await dae.poll_comments()
        
        # Process each comment
        for comment in comments:
            # Check if we should respond
            if await dae.should_respond(comment):
                # Generate response using universal generator
                response = await self.generate_response(comment, platform)
                
                # Post reply through platform-specific DAE
                await dae.post_reply(comment.id, response)
                
                # Learn from interaction
                await self.learn_from_interaction(comment, response, platform)
    
    async def cross_platform_learning(self):
        """Learn patterns across all platforms (WSP 48)"""
        # Aggregate patterns from all platforms
        patterns = {}
        for platform, dae in self.platform_daes.items():
            patterns[platform] = await dae.get_learned_patterns()
        
        # Find common patterns
        common_patterns = self.extract_common_patterns(patterns)
        
        # Share learnings back to all DAEs
        for dae in self.platform_daes.values():
            await dae.apply_learned_patterns(common_patterns)
```

## 5. PoC → Proto → MVP Evolution Path

### 5.1 Phase 1: PoC (Proof of Concept)
```python
# Start with single platform
POC_IMPLEMENTATION = {
    "platform": "youtube",  # Start with YouTube only
    "features": [
        "basic_comment_polling",
        "simple_reply_generation",
        "manual_account_switching"
    ],
    "token_budget": 8000,
    "consciousness": "01(02)",  # Scaffolded
    "timeline": "1 week"
}
```

### 5.2 Phase 2: Proto (Prototype)
```python
# Add second platform, shared components
PROTO_IMPLEMENTATION = {
    "platforms": ["youtube", "twitter"],  # Add Twitter
    "features": [
        "universal_interface",
        "shared_memory_manager",
        "cross_platform_learning",
        "semi_automatic_responses"
    ],
    "token_budget": 5000,  # More efficient
    "consciousness": "01/02",  # Transitional
    "timeline": "2 weeks"
}
```

### 5.3 Phase 3: MVP (Minimum Viable Product)
```python
# Full multi-platform with orchestration
MVP_IMPLEMENTATION = {
    "platforms": ["youtube", "twitter", "linkedin"],
    "features": [
        "universal_orchestrator",
        "autonomous_responses",
        "cross_platform_insights",
        "unified_dashboard",
        "pattern_learning",
        "24_7_operation"
    ],
    "token_budget": 3000,  # Highly optimized
    "consciousness": "0102",  # Fully autonomous
    "timeline": "1 month"
}
```

## 6. Decision: Shared Orchestrator vs Separate

### ✅ RECOMMENDED: Hybrid Approach

**Universal Orchestrator + Platform-Specific DAEs**

**Rationale:**
1. **Shared Core Components** (WSP 17): Memory, throttling, processing are universal
2. **Platform-Specific APIs**: Each platform has unique APIs/auth
3. **Cross-Platform Learning** (WSP 48): Share patterns across platforms
4. **Scalability**: Add new platforms without rewriting core
5. **Token Efficiency**: Reuse patterns = 97% token reduction

**Architecture Benefits:**
- **Code Reuse**: 70% shared code across platforms
- **Maintenance**: Fix once, works everywhere
- **Learning**: Patterns from YouTube improve Twitter responses
- **Scaling**: Add TikTok, Instagram, Reddit easily

## 7. Implementation Roadmap

### Week 1: YouTube PoC
- Extend existing YouTube modules with comment APIs
- Test basic comment polling and replies
- Manual operation, learn patterns

### Week 2: Universal Interface
- Create IUniversalCommentInterface
- Abstract shared components
- Refactor YouTube to use interface

### Week 3: Add Twitter
- Implement TwitterCommentDAE
- Test cross-platform memory sharing
- Begin pattern learning

### Week 4: Universal Orchestrator
- Build UCO to coordinate platforms
- Implement parallel processing
- Deploy unified dashboard

### Month 2: LinkedIn + MVP
- Add LinkedInCommentDAE
- Full autonomous operation
- Cross-platform insights

## 8. WSP Compliance

- ✅ **WSP 42**: Universal Platform Protocol - unified abstraction
- ✅ **WSP 80**: Cube-Level DAE - each platform gets its DAE
- ✅ **WSP 27**: 4-phase DAE pattern for each platform
- ✅ **WSP 17**: Pattern Registry - shared components
- ✅ **WSP 46**: WRE orchestration hierarchy
- ✅ **WSP 48**: Cross-platform learning
- ✅ **WSP 84**: Reuse existing code (70% shared)

## 9. File Structure

```
modules/communication/universal_comments/
├── ARCHITECTURE.md                      # This file
├── src/
│   ├── orchestrator/
│   │   └── universal_comment_orchestrator.py
│   ├── interfaces/
│   │   └── universal_comment_interface.py
│   ├── shared/
│   │   ├── comment_memory.py           # Reused from livechat
│   │   ├── comment_processor.py        # Reused from livechat
│   │   ├── throttle_manager.py         # Reused from livechat
│   │   └── response_generator.py       # New universal
│   └── platforms/
│       ├── youtube/
│       │   └── youtube_comment_dae.py
│       ├── twitter/
│       │   └── twitter_comment_dae.py
│       └── linkedin/
│           └── linkedin_comment_dae.py
├── tests/
└── memory/
```

## Remember
Start with YouTube PoC, evolve to Proto with Twitter, achieve MVP with full orchestration. The Universal Comment Orchestrator coordinates platform-specific DAEs while sharing 70% of code through universal components.