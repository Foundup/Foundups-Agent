# Autonomous Meeting Orchestrator (AMO)

**Eliminates manual scheduling friction through cross-platform emergent meeting orchestration**

[![WSP Compliant](https://img.shields.io/badge/WSP-Compliant-green.svg)](../../WSP_framework/src/WSP_1_The_WSP_Framework.md)
[![Version](https://img.shields.io/badge/version-v0.0.1-blue.svg)](./ROADMAP.md)
[![Phase](https://img.shields.io/badge/phase-PoC-orange.svg)](./ROADMAP.md)
[![Domain](https://img.shields.io/badge/domain-communication-purple.svg)](../README.md)

## 🎯 Vision

Transform meeting coordination from manual scheduling friction into seamless, context-aware orchestration. When both parties are available and context is clear, meetings happen automatically.

**Core Philosophy:** *Intent + Context + Presence + Priority + Consent + Auto-Launch*

## ⚡ Quick Start

```python
from modules.communication.auto_meeting_orchestrator import MeetingOrchestrator
from modules.communication.auto_meeting_orchestrator.src.orchestrator import Priority, PresenceStatus

# Initialize orchestrator
amo = MeetingOrchestrator()

# Create meeting intent
intent_id = await amo.create_meeting_intent(
    requester_id="alice",
    recipient_id="bob",
    purpose="Brainstorm partnership idea", 
    expected_outcome="Agreement on next steps",
    duration_minutes=30,
    priority=Priority.HIGH
)

# Update presence (triggers automatic orchestration)
await amo.update_presence("alice", "discord", PresenceStatus.ONLINE)
await amo.update_presence("bob", "discord", PresenceStatus.ONLINE)

# Meeting automatically orchestrated when both available!
```

## 🔄 Workflow

### 1️⃣ Intent Declaration
User A initiates a meeting request for User B with structured context:
- **Purpose:** Why meet? *(e.g., "Brainstorm partnership idea")*
- **Expected Outcome:** What's the goal? *(e.g., "Agreement on next steps")* 
- **Duration:** How long? *(e.g., 30 minutes)*
- **Priority:** How urgent? *(000-222 scale)*

### 2️⃣ Presence Aggregation  
System monitors real-time availability across platforms:
- WhatsApp online/offline
- Discord idle/active
- LinkedIn presence
- Google Calendar free/busy
- Zoom status

Creates **Unified Availability Profile (UAP)** with confidence scoring.

### 3️⃣ Priority Scoring
Recipients rate urgency, combined with sender priority to calculate **Priority Index**.

### 4️⃣ Service Selection
Auto-selects optimal platform based on:
- Both users' active platforms
- Historical preferences  
- Current device context
- Platform capabilities

### 5️⃣ Consent & Reminder
Recipient gets instant prompt with full context:
> "Alice is available to meet now about:  
> • Brainstorm partnership idea  
> • Expected: 30 min  
> • Priority: 8/10  
> Accept?"

### 6️⃣ Handshake + Session Launch
- Calendar placeholder created
- Meeting launched automatically  
- Both parties notified
- Context preserved in session

## 🏗️ Architecture

### Current Phase: PoC (v0.0.x)
**Success Criterion:** Detect mutual presence and trigger acceptance prompts

**Features:**
- ✅ Meeting intent creation with structured context
- ✅ Multi-platform presence aggregation
- ✅ Priority-based orchestration
- ✅ Automatic handshake protocol
- ✅ Meeting session launch simulation

**Limitations:**
- Simulated presence detection
- Local storage only
- No real platform integrations
- Basic meeting launch

### Next Phase: Prototype (v0.1.x) 
**Success Criterion:** Integrate 2+ real APIs with configurable preferences

**Planned Features:**
- 🔄 Discord + WhatsApp/Zoom API integration
- 🔄 User preference configuration
- 🔄 SQLite/JSON persistent storage
- 🔄 Auto-meeting link generation
- 🔄 Robust error handling

### Future Phase: MVP (v1.0.x)
**Success Criterion:** Customer-ready multi-user system

**Planned Features:**
- ⏳ Multi-user onboarding
- ⏳ OAuth authentication flows
- ⏳ Post-meeting AI summaries
- ⏳ Web dashboard interface
- ⏳ Advanced scheduling logic

## 🎲 Semantic Triplet Scoring

| Phase     | Complexity | Impact | Confidence | Total Score |
|-----------|------------|--------|------------|-------------|
| PoC       | 2/10       | 7/10   | 9/10       | **18/30**   |
| Prototype | 5/10       | 8/10   | 7/10       | **20/30**   |
| MVP       | 7/10       | 10/10  | 6/10       | **23/30**   |

## 🔧 Technical Implementation

### Core Classes

#### MeetingOrchestrator
Main orchestration engine handling the complete workflow.

#### MeetingIntent  
Structured meeting request with purpose, outcome, and priority.

#### UnifiedAvailabilityProfile
Aggregated presence status across all platforms with confidence scoring.

#### PresenceStatus & Priority Enums
Standardized status and priority levels for consistent handling.

### Key Features

**Event-Driven Architecture:** Presence updates automatically trigger availability checks  
**Priority-Based Orchestration:** Higher priority meetings get precedence  
**Platform Abstraction:** Unified interface across different communication platforms  
**Graceful Degradation:** Fallback mechanisms when platforms are unavailable  

## 🧪 Testing

### Run PoC Demo
```bash
cd modules/communication/auto_meeting_orchestrator/src/
python orchestrator.py
```

### Run Test Suite
```bash
cd modules/communication/auto_meeting_orchestrator/
python -m pytest tests/ -v
```

### Expected PoC Output
```
=== AMO PoC Demo ===
✅ Meeting intent created: intent_1
📡 Simulating presence updates...
🤝 Meeting prompt triggered:
   Alice is available to meet about:
   • Purpose: Brainstorm partnership idea
   • Expected outcome: Agreement on next steps  
   • Duration: 30 minutes
   • Priority: HIGH
📊 Final Status:
   Active intents: 0
   Completed meetings: 1
```

## 🌟 Key Benefits

### Zero Manual Scheduling
No more back-and-forth calendar coordination. Meetings happen when context is clear and both parties are available.

### Full Context Always Visible  
Recipients always know exactly why someone wants to meet before accepting.

### Cross-Platform Orchestration
Works across Discord, WhatsApp, Zoom, LinkedIn, and more platforms seamlessly.

### Emergent, Decentralized Flow
No central scheduling authority - meetings emerge naturally from availability and intent.

### Priority-Aware Intelligence
Important meetings get precedence while respecting user availability preferences.

## 🚀 Future Enhancements

### Optional Features (Roadmap)
- **Auto-rescheduling:** If user becomes unavailable mid-session
- **Micro-incentives:** Tokens for prompt acceptance  
- **AI-generated summaries:** Post-call meeting notes
- **Smart scheduling:** Learning user preferences over time
- **Calendar integration:** Automatic time blocking
- **Multi-timezone support:** Global coordination capabilities

## 📚 Documentation

- **[Interface Documentation](./INTERFACE.md)** - Complete API reference
- **[Development Roadmap](./ROADMAP.md)** - Milestone tracking and plans
- **[Module Log](./ModLog.md)** - Development history and updates

## 🔗 Related Modules

**Communication Domain:**
- [`livechat`](../livechat/) - Real-time chat functionality
- [`live_chat_processor`](../live_chat_processor/) - Message processing  
- [`live_chat_poller`](../live_chat_poller/) - Platform polling

**Platform Integration:**
- [`youtube_auth`](../../platform_integration/youtube_auth/) - YouTube OAuth
- [`youtube_proxy`](../../platform_integration/youtube_proxy/) - API gateway
- [`linkedin_agent`](../../platform_integration/linkedin_agent/) - LinkedIn integration

## 🏆 WSP Compliance

This module follows all WSP framework requirements:

- **WSP 1:** ✅ Agentic Responsibility - Autonomous meeting orchestration
- **WSP 3:** ✅ Enterprise Domain - Proper `communication/` placement
- **WSP 4:** ✅ FMAS Audit - Structural compliance verified
- **WSP 5:** ✅ Test Coverage - Comprehensive test suite
- **WSP 11:** ✅ Interface Definition - Complete INTERFACE.md
- **WSP 12:** ✅ Dependencies - Clear dependency declarations

### Dependencies
```
# Core (Current)
asyncio>=3.9.0
dataclasses>=0.8  
typing>=3.8.0

# Future (Prototype+)  
aiohttp>=3.8.0
sqlalchemy>=1.4.0
oauth2lib>=0.9.0
websockets>=10.0
pydantic>=1.8.0
```

## 📈 Development Status

**Current:** PoC implementation complete with simulated functionality  
**Next Milestone:** Prototype with real Discord + WhatsApp integration  
**Target:** MVP ready for customer onboarding by Q2

**Module Maturity:** 🟡 Early Development  
**API Stability:** 🔵 Evolving  
**Production Ready:** 🔴 Not Yet

---

**Module:** `auto_meeting_orchestrator`  
**Domain:** `communication`  
**Version:** v0.0.1  
**Last Updated:** 2024-12-29  
**WSP Compliant:** ✅ 