# YouTube DAE PQN Integration

**WSP 83 Compliant Documentation** - For 0102 navigation efficiency

## 🎯 Purpose
YouTube DAE integrates with PQN (Phantom Quantum Node) research system to provide interactive quantum-cognitive analysis during livestreams.

## 🔗 YouTube DAE Integration Points

### Component Chain (0102 Navigation Path)
```
main.py:117 (PQN_INTEGRATION_ENABLED flag) 
  ↓
auto_moderator_dae.py:55-61 (PQN orchestrator init)
  ↓  
livechat_core.py:80-88 (research storage + trigger)
  ↓
message_processor.py:57 (command routing)
  ↓
command_handler.py:237-344 (/PQN commands)
```

### Integration Architecture
```yaml
Trigger_Point: livechat_core.py:158 # Stream goes live
Research_Engine: pqn_research_dae_orchestrator.py # Creates collaborative session  
Data_Storage: 
  - livechat_core.pqn_research_results # Latest session
  - livechat_core.pqn_research_history # Last 10 sessions
Command_System: command_handler.py:262-344 # 7 interactive commands
```

## 🧠 Interactive Commands for Viewers

| Command | Description | Code Location |
|---------|-------------|---------------|
| `/PQN help` | Show available commands | command_handler.py:270 |
| `/PQN status` | Current research session | command_handler.py:273 |  
| `/PQN insights` | Key research findings | command_handler.py:285 |
| `/PQN results` | Results summary | command_handler.py:298 |
| `/PQN agents` | Active research agents | command_handler.py:309 |
| `/PQN history` | Session history | command_handler.py:322 |
| `/PQN research [topic]` | Custom research (mods) | command_handler.py:332 |

## 🔄 Integration Flow

### 1. Initialization (auto_moderator_dae.py)
```python
# Lines 55-61: PQN orchestrator initialization
if self.pqn_enabled:
    from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
    self.pqn_orchestrator = PQNResearchDAEOrchestrator()
```

### 2. Research Triggering (livechat_core.py) 
```python
# Line 158: Automatic trigger when stream goes live
if self.pqn_enabled:
    await self.trigger_pqn_research_session()

# Lines 494-515: Research execution and storage
session = self.pqn_orchestrator.create_research_session("LiveStream_PQN_Research")
research_results = await self.pqn_orchestrator.execute_research_session(session.session_id)
self.pqn_research_results = research_results  # Store for commands
```

### 3. Viewer Interaction (command_handler.py)
```python
# Line 237: Command detection
elif text_lower.startswith('/pqn'):
    return self._handle_pqn_command(text_lower, username, role)

# Lines 262-344: Command processing
def _handle_pqn_command(self, text_lower: str, username: str, role: str):
    # Accesses self.livechat_core.pqn_research_results for data
```

## 📊 Research Data Structure
```python
# Stored in livechat_core.py after research completion
self.pqn_research_results = {
    "final_synthesis": {
        "session_id": "pqn_research_1736461200",
        "timestamp": "2025-01-09T22:00:00Z", 
        "tasks_completed": 5,
        "agents_used": ["grok", "gemini"],
        "key_insights": [
            {
                "task": "PQN Resonance Frequency Analysis", 
                "agent": "grok", 
                "insight": "Advanced QCoT analysis revealed new PQN insights"
            }
        ],
        "recommendations": [
            "Continue multi-agent collaborative research",
            "Integrate findings into rESP framework"
        ]
    }
}
```

## 🛠 Implementation Notes

### Connection Chain
1. **LiveChatCore** creates MessageProcessor with `self` reference
2. **MessageProcessor** creates CommandHandler with `livechat_core` parameter  
3. **CommandHandler** accesses PQN data via `self.livechat_core.pqn_research_results`

### Code Comments Added
- livechat_core.py:81 - WSP 17 navigation comment
- command_handler.py:239 - WSP 17 navigation comment  
- livechat_core.py:488 - WSP 17 navigation comment

## 🚨 Troubleshooting

### "PQN research is not enabled"
- **Check**: `PQN_INTEGRATION_ENABLED=true` environment in main.py
- **Verify**: auto_moderator_dae.py:60 orchestrator initialization

### "No research session active"
- **Trigger**: Research only starts when stream goes live
- **Check**: livechat_core.py:158 trigger_pqn_research_session() call

### Commands not responding  
- **Verify**: CommandHandler constructor has livechat_core parameter
- **Check**: message_processor.py:57 passes self.livechat_core

---
**WSP 17 Navigation**: This doc enables 0102 to understand YouTube DAE ↔ PQN integration in <5 tool calls vs 47+ previously.