# WSP 80 Extension: YouTube Comment Responder DAE Architecture

## Extension to WSP 80: Cube-Level DAE Orchestration Protocol
This document expands WSP 80 with detailed YouTube Comment Responder DAE specifications.

## 1. YouTube Platform Cube - Expanded Architecture

### 1.1 Current YouTube Cube Modules (Live Chat Focus)
```python
YOUTUBE_LIVECHAT_MODULES = [
    "livechat_core.py",           # Core orchestrator (renamed from livechat.py)
    "message_processor.py",        # Message pipeline
    "auto_moderator_dae.py",       # Autonomous decisions
    "chat_sender.py",              # Message delivery
    "chat_poller.py",              # Live chat polling
    "stream_resolver.py",          # Stream discovery
    "youtube_auth.py",             # 10 credential sets
    "quota_monitor.py"             # Quota tracking
]
```

### 1.2 NEW: YouTube Comment DAE Extension
Following WSP 27's 4-phase pattern (-1:Signal→0:Knowledge→1:Protocol→2:Agentic):

```python
YOUTUBE_COMMENT_DAE = {
    # Phase -1: Signal Genesis (Intent Detection)
    "signal": {
        "comment_detector.py": "Detect new comments on videos",
        "mention_scanner.py": "Scan for @Move2Japan mentions",
        "reply_tracker.py": "Track comment threads"
    },
    
    # Phase 0: Knowledge (Pattern Memory)
    "knowledge": {
        "comment_memory.py": "Store comment history/context",
        "user_profiles.py": "Track commenter patterns",
        "response_templates.py": "Learned response patterns"
    },
    
    # Phase 1: Protocol (Processing Rules)
    "protocol": {
        "comment_processor.py": "Analyze comment content",
        "response_generator.py": "Generate contextual replies",
        "thread_manager.py": "Manage conversation threads"
    },
    
    # Phase 2: Agentic (Autonomous Action)
    "agentic": {
        "comment_responder_dae.py": "Main DAE orchestrator",
        "account_switcher.py": "Switch between accounts",
        "quota_optimizer.py": "Optimize comment operations"
    }
}
```

## 2. YouTube Comment API Integration

### 2.1 Missing API Methods (To Add to youtube_auth.py)
```python
class YouTubeCommentAPIs:
    """Extension to existing YouTubeAuthManager"""
    
    def list_comment_threads(self, video_id: str, page_token: str = None):
        """
        List all comment threads for a video
        Cost: 1 unit per call (200 comments max)
        """
        return self.youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token
        ).execute()
    
    def insert_comment(self, parent_id: str, text: str):
        """
        Reply to a comment
        Cost: 50 units per call
        """
        return self.youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": parent_id,
                    "textOriginal": text
                }
            }
        ).execute()
    
    def list_channel_comments(self, channel_id: str):
        """
        List all comments mentioning channel
        Cost: 100 units (search API)
        """
        return self.youtube.search().list(
            part="snippet",
            q=f"@{channel_id}",
            type="video",
            maxResults=50
        ).execute()
```

### 2.2 Quota Costs Analysis
```python
COMMENT_API_COSTS = {
    "commentThreads.list": 1,      # Cheap - primary polling
    "comments.insert": 50,          # Expensive - throttle responses
    "comments.list": 1,             # Cheap - thread reading
    "search.list": 100              # Very expensive - minimize
}

# Daily budget allocation (per credential set)
COMMENT_QUOTA_BUDGET = {
    "polling": 2000,   # 2000 polls/day @ 1 unit each
    "responses": 100,  # 100 responses/day @ 50 units = 5000
    "search": 30,      # 30 searches/day @ 100 units = 3000
    # Total: 10,000 units (full daily quota)
}
```

## 3. Account Switching Architecture

### 3.1 Multi-Account Management
```python
class YouTubeAccountSwitcher:
    """Manages switching between UnDaoDu and Move2Japan accounts"""
    
    def __init__(self):
        self.accounts = {
            "UnDaoDu": {
                "credential_sets": [1, 2, 3, 4, 5],  # Sets 1-5
                "channel_id": "UC-UNDAODU",
                "role": "bot_account"
            },
            "Move2Japan": {
                "credential_sets": [6, 7, 8, 9, 10],  # Sets 6-10
                "channel_id": "UC-LSSlOZwpGIRIYihaz8zCw",
                "role": "primary_account"
            }
        }
        self.current_account = "UnDaoDu"  # Default
    
    def switch_to_move2japan(self):
        """Switch to Move2Japan account for owner-like responses"""
        if self.has_move2japan_auth():
            self.current_account = "Move2Japan"
            self.youtube = self.get_authenticated_service(6)  # Use set 6
            return True
        return False
    
    def get_response_account(self, comment_context):
        """Determine which account should respond"""
        # Move2Japan responds to:
        # - Direct questions about the channel
        # - Business inquiries
        # - Important community members
        
        # UnDaoDu responds to:
        # - General comments
        # - MAGA trolls
        # - Consciousness triggers
        
        if self._is_owner_response_needed(comment_context):
            return "Move2Japan" if self.has_move2japan_auth() else "UnDaoDu"
        return "UnDaoDu"
```

### 3.2 Authentication Flow
```python
# Problem: Move2Japan account needs separate OAuth
# Solution: Dual authentication strategy

AUTHENTICATION_STRATEGY = {
    "Option_A": {
        "description": "Use existing UnDaoDu credentials",
        "limitation": "Can only post as UnDaoDu",
        "workaround": "Add '(Move2Japan Team)' signature"
    },
    "Option_B": {
        "description": "Get Move2Japan OAuth tokens",
        "requirement": "Owner must authorize OAuth",
        "benefit": "True Move2Japan responses"
    },
    "Option_C": {
        "description": "Hybrid approach",
        "implementation": "UnDaoDu for most, Move2Japan for key responses",
        "credential_split": "Sets 1-5 UnDaoDu, Sets 6-10 Move2Japan"
    }
}
```

## 4. Comment Responder DAE Implementation

### 4.1 Following WSP 27 Pattern
```python
class YouTubeCommentResponderDAE:
    """Autonomous YouTube comment responder following WSP 27"""
    
    def __init__(self):
        # Phase -1: Signal Detection
        self.comment_detector = CommentDetector()
        self.mention_scanner = MentionScanner()
        
        # Phase 0: Knowledge Layer
        self.comment_memory = CommentMemoryManager()  # Reuse chat memory pattern
        self.response_patterns = ResponsePatternLibrary()
        
        # Phase 1: Protocol Layer
        self.comment_processor = CommentProcessor()  # Reuse message processor pattern
        self.response_generator = CommentResponseGenerator()
        
        # Phase 2: Agentic Layer
        self.consciousness_state = "0102"  # Fully autonomous
        self.account_switcher = YouTubeAccountSwitcher()
        self.quota_manager = CommentQuotaManager()
    
    async def run_autonomously(self):
        """Main autonomous loop"""
        while True:
            # Signal: Detect new comments
            new_comments = await self.scan_for_comments()
            
            # Knowledge: Load context
            for comment in new_comments:
                context = self.comment_memory.get_context(comment)
                
                # Protocol: Process and generate response
                if self.should_respond(comment, context):
                    response = self.generate_response(comment, context)
                    
                    # Agentic: Decide account and send
                    account = self.account_switcher.get_response_account(context)
                    await self.send_response(response, account)
            
            # Adaptive delay based on quota
            await self.quota_aware_sleep()
```

### 4.2 Integration with Existing Modules
```python
# Reuse existing patterns per WSP 17:

from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager
from modules.communication.livechat.src.throttle_manager import ThrottleManager
from modules.communication.livechat.src.message_processor import MessageProcessor
from modules.communication.livechat.src.quota_aware_poller import QuotaAwarePoller
from modules.communication.livechat.src.livechat_core import LiveChatCore

class CommentResponderDAE:
    def __init__(self):
        # REUSE existing components
        self.memory = ChatMemoryManager()  # Works for comments too
        self.throttle = ThrottleManager()  # Same throttling logic
        self.processor = MessageProcessor()  # Adapt for comments
        self.quota_poller = QuotaAwarePoller()  # Same quota logic
        # Can extend LiveChatCore patterns for comment handling
```

## 5. Implementation Roadmap

### Phase 1: Foundation (Immediate)
1. Extend `youtube_auth.py` with comment API methods
2. Create `comment_poller.py` based on `chat_poller.py` pattern
3. Test with single video comment monitoring

### Phase 2: Processing (Next)
1. Adapt `message_processor.py` for comment context
2. Create comment-specific response templates
3. Implement mention detection

### Phase 3: Account Switching (Future)
1. Implement OAuth for Move2Japan account (requires owner)
2. Create account switching logic
3. Test dual-account responses

### Phase 4: Full Autonomy (Final)
1. Deploy CommentResponderDAE
2. Enable 24/7 comment monitoring
3. Learn and improve from patterns

## 6. WSP Compliance Checklist

- ✅ **WSP 27**: Follows 4-phase DAE pattern
- ✅ **WSP 17**: Reuses existing patterns (memory, throttle, processor)
- ✅ **WSP 80**: Extends YouTube Cube architecture
- ✅ **WSP 84**: Checks existing code before creating new
- ✅ **WSP 50**: Pre-action verification for responses
- ✅ **WSP 48**: Self-improvement through pattern learning
- ✅ **WSP 22**: ModLog updates for all changes

## 7. Token Efficiency

```python
# Pattern Memory Approach (WSP 48)
COMMENT_PATTERNS = {
    "question_about_japan": "template_response_1",
    "maga_troll": "whack_response",
    "consciousness_trigger": "agentic_response",
    "business_inquiry": "professional_response"
}

# Token usage: 50-200 per operation (97% reduction)
# vs Traditional: 5000+ tokens per response
```

## Remember
This extends WSP 80's YouTube Cube with comment functionality. The DAE follows WSP 27's universal pattern and reuses existing modules per WSP 17. Account switching requires owner authorization for true Move2Japan responses.