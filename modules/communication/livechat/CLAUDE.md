# CLAUDE.md - LiveChat Module Memory

## Module Structure (WSP 83 Compliant)
This document helps 0102 remember all module components and paths.

## Core Components

### Main Engine (`src/`)
- `livechat_core.py` - Core chat monitoring with agentic stream switching
- `auto_moderator_dae.py` - WSP-compliant DAE orchestration with quick_check_mode
- `message_processor.py` - Processes messages and consciousness triggers
- `command_handler.py` - Handles /slash commands and whack gamification
- `event_handler.py` - Processes YouTube chat events (timeouts, messages)
- `chat_sender.py` - Sends messages to YouTube chat (handles markdown removal)
- `throttle_manager.py` - Rate limiting and quota management
- `agentic_chat_engine.py` - AI response generation
- `greeting_generator.py` - Stream greeting generation
- `mcp_youtube_integration.py` - Model Context Protocol integration

### Key Features

#### Agentic Stream Switching
- **Inactivity Detection**: 3-minute timeout triggers stream search
- **Quick Check Mode**: 5-15 second intervals after stream ends
- **Cache Clearing**: Automatic cache clear when streams end
- **Seamless Reconnection**: No restart required

#### Consciousness Triggers (✊✋🖐)
- Pattern: `✊✋🖐` followed by question
- Modes: `mod_only` or `everyone`
- Toggle: `/toggle` command (MOD/OWNER only)

#### Command Processing
- All commands in `command_handler.py`
- Quiz responses stripped of markdown for YouTube compatibility
- Extensive logging with 🧠 emoji markers

### Integration Points
- **Platform**: `modules/platform_integration/stream_resolver/`
- **Gamification**: `modules/gamification/whack_a_magat/`
- **Auth**: `modules/platform_integration/youtube_auth/`

### Recent Fixes
1. Stream switching now truly agentic (no restart needed)
2. Quiz messages work (markdown removed)
3. Cache clearing ensures fresh stream detection
4. Quick check mode for rapid reconnection

### WSP Compliance
- WSP 3: Module organization
- WSP 17: Pattern registry compliance
- WSP 22: ModLog for changes
- WSP 27: DAE architecture
- WSP 83: Documentation attached to tree
- WSP 84: Check existing code first

## Remember
- YouTube API rejects markdown formatting
- Cache must be cleared for fresh stream detection
- Quick check mode activates after stream ends
- All /quiz logging uses 🧠 emoji markers