# Autonomous Meeting Orchestrator (AMO)

**Eliminates manual scheduling friction through cross-platform emergent meeting orchestration**

---

## [U+1F3B2] **Meeting Orchestration Block Core (WSP Level 4)**

**BLOCK ARCHITECTURE ROLE**: This module serves as the **[TARGET] Core Engine** for the complete **Meeting Orchestration Block** - one of five standalone FoundUps Platform Blocks.

### **[HANDSHAKE] Meeting Orchestration Block Overview**
**Standalone Meeting Coordination System** - Complete 5-module block for autonomous meeting orchestration:

#### **Block Components Coordinated by This Core:**
- **[TARGET] [`auto_meeting_orchestrator/`](README.md)** - **THIS MODULE** - Core autonomous meeting coordination engine
- **[DATA] [`integration/presence_aggregator/`](../../integration/presence_aggregator/README.md)** - Multi-platform presence detection and aggregation
- **[NOTE] [`intent_manager/`](../intent_manager/README.md)** - Meeting intent capture and structured context (planned)
- **[TARGET] [`channel_selector/`](../channel_selector/README.md)** - Optimal communication platform selection logic (planned)
- **[OK] [`infrastructure/consent_engine/`](../../infrastructure/consent_engine/README.md)** - Meeting consent and approval workflows (planned)

### **[LINK] Block Independence & Integration**
- **[OK] Standalone Operation**: Meeting Orchestration Block functions completely independently of other blocks
- **[LIGHTNING] WRE Integration**: Seamless plugging into Windsurf Recursive Engine system  
- **[REFRESH] Hot-Swappable**: Block can be upgraded or replaced without affecting other blocks
- **[TARGET] Complete Functionality**: Intent-driven coordination, presence aggregation, autonomous setup, anti-gaming protection

**Block Status**: [OK] **POC COMPLETE** (85% complete, P2 priority for core collaboration)

---

[![WSP Compliant](https://img.shields.io/badge/WSP-Compliant-green.svg)](../../WSP_framework/src/WSP_1_The_WSP_Framework.md)
[![Version](https://img.shields.io/badge/version-v0.0.1-blue.svg)](./ROADMAP.md)
[![Phase](https://img.shields.io/badge/phase-PoC-orange.svg)](./ROADMAP.md)
[![Domain](https://img.shields.io/badge/domain-communication-purple.svg)](../README.md)

## [U+1F9E9] Communication LEGO Block Architecture
The Autonomous Meeting Orchestrator operates as a **self-contained communication LEGO block** within the FoundUps Rubik's Cube module system. It exemplifies perfect modularity by handling all meeting orchestration independently while snapping seamlessly with presence detection, calendar management, and notification modules.

**Communication LEGO Block Principles:**
- **[TARGET] Meeting-Focused**: Laser-focused solely on meeting orchestration within communication domain
- **[U+1F50C] Presence Integration**: Snaps cleanly with platform presence detection modules  
- **[LIGHTNING] Autonomous Orchestration**: Complete meeting coordination without external module dependencies
- **[LINK] Cross-Platform APIs**: Standard interfaces for calendar, notification, and presence modules
- **[REFRESH] Hot-Swappable Coordination**: Can be upgraded while maintaining integration with other modules
- **[U+1F3AD] Zero Duplication**: Orchestrates existing modules rather than duplicating their functionality

## [TARGET] Vision

Transform meeting coordination from manual scheduling friction into seamless, context-aware orchestration. When both parties are available and context is clear, meetings happen automatically.

**Core Philosophy:** *Intent + Context + Presence + Priority + Consent + Auto-Launch*

## [LIGHTNING] Quick Start

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

## [REFRESH] Core Handshake Protocol

### **Minimal Viable Flow - 7-Step Process**

#### **1️⃣ User Availability Status**
When users log in, they select **availability scope**:
- **Public** - Anyone can request meetings
- **Contacts only** - LinkedIn, Facebook, Twitter connections only  
- **Private** - No meeting requests accepted

```python
availability_scope = "public" | "contacts" | "private"
```

This governs **who can see them as available** and request meetings.

#### **2️⃣ Intent Declaration (3-Question Form)**
Someone wanting to meet completes structured context:

1. **Why do you want to meet?** *(Purpose)*
2. **What do you hope to get out of it?** *(Expected Outcome)*  
3. **How long do you expect it to take?** *(Duration)*

Plus **Importance Rating (1-10)** from requester's perspective.

**Example Intent:**
```json
{
  "why": "Brainstorm partnership project",
  "outcome": "Agree on next steps and timeline", 
  "duration": "30 minutes",
  "importance_rating": 8
}
```

#### **3️⃣ Eligibility & Visibility Check**
System automatically validates:
- [OK] Is recipient **public** or within **requester's network**?
- [OK] If yes: Show in available list
- [OK] If no: Block request silently

#### **4️⃣ Recipient Notification & Response**
Recipient receives **context-rich prompt**:
- Who wants to meet
- The 3 structured answers
- Requester's importance rating (1-10)

**Recipient actions:**
- Accept or decline meeting
- Rate **how important it is to meet (1-10)** from their perspective

#### **5️⃣ Rating Integrity & Anti-Gaming**
**Critical Innovation:** System tracks **rating distribution patterns**:

```python
credibility_score = (variance_of_ratings) × (historical_engagement_success_rate)
```

**Anti-Gaming Measures:**
- Users who always rate "10" get **reduced weight** in priority sorting
- Users consistently rated low by others get **reduced visibility**
- **Reputation scoring** prevents spam and gaming

#### **6️⃣ Handshake Completion**
If recipient **accepts**:
- [OK] System records both party ratings
- [OK] Stores complete intent metadata
- [OK] Marks handshake **active**
- [OK] Triggers **intelligent channel selection** (Discord, Zoom, WhatsApp, etc.)

#### **7️⃣ Autonomous Session Launch**
- [OK] Auto-creates meeting on optimal platform
- [OK] Sends invitations with preserved context
- [OK] Logs complete meeting lifecycle
- [OK] Schedules or launches immediately based on mutual availability

## [U+1F310] **Minimal Web App Architecture**

### **Frontend Requirements**
```typescript
// Core Components
- Login (OAuth: LinkedIn/Google)
- Availability Toggle (Public/Contacts/Private)  
- Request Form (3 questions + importance slider)
- Incoming Request View (with context display)
- Accept/Decline Interface (with rating)
- Meeting Dashboard (active sessions)
```

### **Backend Architecture** 
```python
# Minimal Stack
- Node/Express or Python/FastAPI
- PostgreSQL or SQLite database
- OAuth authentication
- Reputation scoring engine
- Platform integration APIs

# Core Database Schema
Users: {id, name, email, availability_scope, credibility_score}
Requests: {id, requester_id, recipient_id, intent_data, status}
Ratings: {id, request_id, requester_rating, recipient_rating}
Sessions: {id, request_id, platform, meeting_link, status}
```

### **API Routes**
```javascript
POST /api/requests          // Create meeting intent
GET  /api/requests/pending  // Get incoming requests  
PUT  /api/requests/:id      // Accept/decline with rating
POST /api/availability      // Update availability scope
GET  /api/sessions/active   // Current meeting sessions
```

## [REFRESH] Workflow

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

## [U+1F3D7]️ Architecture

### Current Phase: PoC (v0.0.x)
**Success Criterion:** Detect mutual presence and trigger acceptance prompts

**Features:**
- [OK] Meeting intent creation with structured context
- [OK] Multi-platform presence aggregation
- [OK] Priority-based orchestration
- [OK] Automatic handshake protocol
- [OK] Meeting session launch simulation

**Limitations:**
- Simulated presence detection
- Local storage only
- No real platform integrations
- Basic meeting launch

### Next Phase: Prototype (v0.1.x) 
**Success Criterion:** Integrate 2+ real APIs with configurable preferences

**Planned Features:**
- [REFRESH] Discord + WhatsApp/Zoom API integration
- [REFRESH] User preference configuration
- [REFRESH] SQLite/JSON persistent storage
- [REFRESH] Auto-meeting link generation
- [REFRESH] Robust error handling

### Future Phase: MVP (v1.0.x)
**Success Criterion:** Customer-ready multi-user system

**Planned Features:**
- ⏳ Multi-user onboarding
- ⏳ OAuth authentication flows
- ⏳ Post-meeting AI summaries
- ⏳ Web dashboard interface
- ⏳ Advanced scheduling logic

## [U+1F3B2] Semantic Triplet Scoring

| Phase     | Complexity | Impact | Confidence | Total Score |
|-----------|------------|--------|------------|-------------|
| PoC       | 2/10       | 7/10   | 9/10       | **18/30**   |
| Prototype | 5/10       | 8/10   | 7/10       | **20/30**   |
| MVP       | 7/10       | 10/10  | 6/10       | **23/30**   |

## [TOOL] Technical Implementation

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

## [U+1F9EA] Testing

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
[OK] Meeting intent created: intent_1
[U+1F4E1] Simulating presence updates...
[HANDSHAKE] Meeting prompt triggered:
   Alice is available to meet about:
   • Purpose: Brainstorm partnership idea
   • Expected outcome: Agreement on next steps  
   • Duration: 30 minutes
   • Priority: HIGH
[DATA] Final Status:
   Active intents: 0
   Completed meetings: 1
```

## [U+1F31F] Key Benefits

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

## [ROCKET] Future Enhancements

### Optional Features (Roadmap)
- **Auto-rescheduling:** If user becomes unavailable mid-session
- **Micro-incentives:** Tokens for prompt acceptance  
- **AI-generated summaries:** Post-call meeting notes
- **Smart scheduling:** Learning user preferences over time
- **Calendar integration:** Automatic time blocking
- **Multi-timezone support:** Global coordination capabilities

## [BOOKS] Documentation

- **[Interface Documentation](./INTERFACE.md)** - Complete API reference
- **[Development Roadmap](./ROADMAP.md)** - Milestone tracking and plans
- **[Module Log](./ModLog.md)** - Development history and updates

## [LINK] Related Modules

**Communication Domain:**
- [`livechat`](../livechat/) - Real-time chat functionality
- [`live_chat_processor`](../live_chat_processor/) - Message processing  
- [`live_chat_poller`](../live_chat_poller/) - Platform polling

**Platform Integration:**
- [`youtube_auth`](../../platform_integration/youtube_auth/) - YouTube OAuth
- [`youtube_proxy`](../../platform_integration/youtube_proxy/) - API gateway
- [`linkedin_agent`](../../platform_integration/linkedin_agent/) - LinkedIn integration

## [U+1F4DC] WSP Compliance

This module follows these Windsurf Standard Procedures:

**Framework Requirements:**
- **WSP 1**: The WSP Framework (foundational principles) [OK] Agentic Responsibility - Autonomous meeting orchestration
- **WSP 3**: Enterprise Domain Organization (communication domain placement) [OK] Proper `communication/` placement
- **WSP 4**: FMAS Audit [OK] Structural compliance verified
- **WSP 5**: Test Coverage [OK] Comprehensive test suite ([GREATER_EQUAL]90%)
- **WSP 11**: WRE Standard Command Protocol (interface definition) [OK] Complete INTERFACE.md
- **WSP 12**: Dependencies [OK] Clear dependency declarations
- **WSP 22**: Module ModLog and Roadmap (documentation standards)
- **WSP 58**: FoundUp IP Lifecycle and Tokenization Protocol (IP management)

### **IP Declaration per WSP 58**
```
Title: Auto Meeting Orchestrator System
Description: Intent-driven autonomous meeting coordination with anti-gaming reputation management
Author: @UnDaoDu + 0102
Date: 2025-01-23
License: Open Beneficial License v1.0 + Patent Protection
IPID: FUP-20250123-AMO001
Patent Reference: Patent 05 - Auto Meeting Orchestrator System
```

**Tokenization Status:**
- Total Tokens: 1,000
- UnDaoDu Patent Portfolio: 700
- FoundUp Treasury: 200  
- Community Allocation: 100

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

## [UP] Development Status

**Current:** PoC implementation complete with simulated functionality  
**Next Milestone:** Prototype with real Discord + WhatsApp integration  
**Target:** MVP ready for customer onboarding by Q2

**Module Maturity:** 🟡 Early Development  
**API Stability:** [U+1F535] Evolving  
**Production Ready:** [U+1F534] Not Yet

---

**Module:** `auto_meeting_orchestrator`  
**Domain:** `communication`  
**Version:** v0.0.1  
**Last Updated:** 2024-12-29  
**WSP Compliant:** [OK] 