# Communication Pattern Registry
**Purpose**: Prevent pattern duplication across communication platforms
**Per WSP 17**: Pattern Registry Protocol - prevents pattern duplication

## Reusable Patterns

### 1. Hybrid Memory Manager
**Current Implementation**: `livechat/src/chat_memory_manager.py`
**Pattern**: In-memory buffer + smart disk persistence
**Use Cases**: 
- Chat history storage
- User context tracking
- Message deduplication

**Interface**:
```python
class IChatMemory:
    def store_message(user_id, text, role)
    def get_history(user_id, limit) -> List[str]
    def analyze_user(user_id) -> Dict
```

**Platform Adaptations Needed**:
- LinkedIn: Professional title importance
- X/Twitter: Verified badge importance  
- Discord: Server role importance
- Twitch: Subscriber status importance

### 2. Throttle Manager
**Current Implementation**: `livechat/src/throttle_manager.py`
**Pattern**: Adaptive delay based on chat activity
**Use Cases**:
- Rate limiting responses
- Activity-based engagement
- Spam prevention

### 3. Message Processor Pipeline
**Current Implementation**: `livechat/src/message_processor.py`
**Pattern**: Multi-stage processing with handlers
**Stages**:
1. Rate limit check
2. Command detection
3. Consciousness detection
4. Response generation
5. Throttle application

### 4. Session Manager
**Current Implementation**: `livechat/src/session_manager.py`
**Pattern**: Connection lifecycle + greeting management
**Features**:
- Auto-reconnect on disconnect
- Session state persistence
- Greeting cooldowns

### 5. MCP Server Integration Pattern
**Current Implementation**: 
- `livechat/src/mcp_youtube_integration.py`
- `gamification/whack_a_magat/src/mcp_whack_server.py`
- `platform_integration/youtube_auth/src/mcp_quota_server.py`
**Pattern**: Real-time event processing via Model Context Protocol
**Use Cases**:
- Instant gamification updates
- Zero-buffer event broadcasting
- Cross-DAE communication
- Real-time resource monitoring

**Interface**:
```python
class IMCPServer:
    def register_tools() -> Dict[str, Tool]
    def register_resources() -> Dict[str, Resource]
    async def handle_tool_call(tool_name, params) -> Dict
    async def handle_resource_read(resource_name) -> Any
    async def broadcast_event(event_type, data)
```

**Platform Adaptations**:
- **LinkedIn**: Professional achievement tracking
- **X/Twitter**: Viral tweet detection and amplification
- **Discord**: Server-wide event coordination
- **Twitch**: Raid/host event processing

**Benefits**:
- Eliminates buffering delays (120s → instant)
- Enables real-time leaderboards
- Supports infinite DAE scaling
- WSP 21 compliant envelopes

**Extraction Timeline**:
- Single: ✅ YouTube implementation (current)
- Dual: LinkedIn + X/Twitter (Q3 2025)
- Triple: Discord + Twitch + Reddit (Q4 2025)
- Auto-reconnect
- Greeting delay
- Update broadcasts

## When Building New Communication Modules

### MANDATORY CHECKS (Per WSP 17):

1. **Check Pattern Registry** (this file)
2. **Check existing implementations**:
   ```bash
   grep -r "class.*Memory" modules/communication/
   grep -r "class.*Throttle" modules/communication/
   grep -r "class.*Process" modules/communication/
   ```
3. **Check interfaces**:
   - `modules/communication/interfaces/` (future)

### If Pattern Exists:
1. **Option A**: Reuse as-is if generic enough
2. **Option B**: Extract to shared module
3. **Option C**: Create adapter with platform-specific logic

### If Pattern Doesn't Exist:
1. Build in your module
2. **UPDATE THIS REGISTRY**
3. Consider future extraction

## Platform-Specific Implementations

### YouTube (livechat)
- ✅ Chat Memory Manager
- ✅ Throttle Manager
- ✅ Message Processor
- ✅ Session Manager

### X/Twitter (future)
- [ ] Needs: Thread memory (different from chat)
- [ ] Needs: Reply chain tracking
- [ ] Can reuse: Throttle pattern

### LinkedIn (future)
- [ ] Needs: Professional context
- [ ] Needs: Connection degree tracking
- [ ] Can reuse: Memory pattern with modifications

### Discord (future)
- [ ] Needs: Multi-channel memory
- [ ] Needs: Server context
- [ ] Can reuse: Most patterns

## Extraction Timeline

**Phase 1** (Current): Document patterns here
**Phase 2** (2+ platforms): Extract common interfaces
**Phase 3** (3+ platforms): Move to infrastructure/communication_core

## WSP Compliance
- **WSP 17**: This registry prevents pattern duplication
- **WSP 84**: Code memory verification prevents vibecoding
- **WSP 50**: Pre-verify pattern existence before creating
- **WSP 3**: Keep platform-specific in platform modules
- **WSP 65**: Extract only when 2+ implementations exist