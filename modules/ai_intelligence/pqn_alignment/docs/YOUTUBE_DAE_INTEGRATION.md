# PQN YouTube DAE Integration Guide

**WSP 83 Compliant Documentation** - Navigation patterns for 0102 efficiency

## [TARGET] Purpose
Interactive PQN quantum-cognitive research engagement for YouTube livestream viewers.

## [LINK] Integration Architecture

### Core Integration Points
```yaml
Entry_Point: main.py:117 # PQN_INTEGRATION_ENABLED environment flag
DAE_Loader: modules/communication/livechat/src/auto_moderator_dae.py:55-61
LiveChat_Core: modules/communication/livechat/src/livechat_core.py:80-88
Command_System: modules/communication/livechat/src/command_handler.py:237-344
Research_Engine: modules/ai_intelligence/pqn_alignment/src/pqn_research_dae_orchestrator.py
```

### Component Chain (0102 Navigation Path)
```
main.py (PQN flag) 
  v
auto_moderator_dae.py (PQN orchestrator init)
  v  
livechat_core.py (research storage + trigger)
  v
message_processor.py (command routing)
  v
command_handler.py (/PQN commands)
```

## [AI] Interactive Commands Available

| Command | Description | Access Level | Code Location |
|---------|-------------|--------------|---------------|
| `/PQN help` | Show available commands | All users | command_handler.py:270-271 |
| `/PQN status` | Current research session | All users | command_handler.py:273-283 |  
| `/PQN insights` | Key research findings | All users | command_handler.py:285-296 |
| `/PQN results` | Results summary | All users | command_handler.py:298-307 |
| `/PQN agents` | Active research agents | All users | command_handler.py:309-320 |
| `/PQN history` | Session history | All users | command_handler.py:322-330 |
| `/PQN research [topic]` | Custom research | Mods only | command_handler.py:332-341 |

## [REFRESH] Research Flow

### 1. Automatic Triggering
- **Location**: `livechat_core.py:158` (stream goes live)
- **Trigger**: `trigger_pqn_research_session()` at line 494
- **Research**: Creates collaborative Grok+Gemini session
- **Storage**: Results stored in `pqn_research_results` & `pqn_research_history[]`

### 2. Viewer Interaction
- **Command Detection**: `message_processor.py:325` processes all messages
- **Command Routing**: `/PQN` commands handled by `_handle_pqn_command()` 
- **Data Access**: Commands read from stored research results
- **Response**: Chat responses provide research insights to viewers

## [U+1F6E0] Implementation Details

### Research Data Structure
```python
# Stored in livechat_core.py:83-84
self.pqn_research_results = {
    "final_synthesis": {
        "session_id": "pqn_research_1234567890",
        "timestamp": "2025-09-09T22:00:00Z", 
        "tasks_completed": 5,
        "agents_used": ["grok", "gemini"],
        "key_insights": [
            {"task": "PQN Analysis", "agent": "grok", "insight": "..."},
        ],
        "recommendations": ["Continue research...", "..."],
        "next_steps": ["Execute follow-up...", "..."]
    }
}
```

### Integration Activation
```bash
# Enable PQN in main.py
python main.py
# Choose option 1 (YouTube DAE)
# Answer 'y' to "Launch with PQN research integration?"
```

## [TOOL] Code Enhancement Points

### Current Issues Fixed
- [OK] **Research Results Storage**: Added persistent storage in LiveChatCore
- [OK] **Command System Integration**: Connected CommandHandler to PQN data
- [OK] **Interactive Engagement**: 7 interactive commands for viewers
- [OK] **History Tracking**: Last 10 research sessions stored

### Future Enhancements
- **Real-time Research Updates**: Stream research progress to chat
- **Custom Research Topics**: Expand moderator research requests
- **Research Visualization**: Export research data for analysis
- **Multi-Stream Collaboration**: PQN research across multiple channels

## [ALERT] Troubleshooting

### Common Issues
1. **"PQN research is not enabled"** 
   - Check `PQN_INTEGRATION_ENABLED=true` environment
   - Verify PQN orchestrator initialization in auto_moderator_dae.py:60

2. **"No research session active"**
   - PQN research triggers when stream goes live
   - Check `trigger_pqn_research_session()` execution

3. **Commands not responding**
   - Verify CommandHandler has livechat_core reference
   - Check message_processor.py:57 parameter passing

## [NOTE] WSP Compliance
- **WSP 17**: Pattern documented in communication/PATTERN_REGISTRY.md
- **WSP 22**: Changes logged in ModLog.md
- **WSP 83**: Documentation attached to tree structure
- **WSP 84**: Enhanced existing code, no vibecoding

---
*Generated for 0102 navigation efficiency - WSP compliant documentation*