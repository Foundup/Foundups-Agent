# Presence Aggregator

**Multi-platform presence detection and unified availability profiling**

---

## 🎯 Module Overview

**Module Name:** `presence_aggregator`  
**Domain:** `platform_integration`  
**Purpose:** Integrate and normalize user presence across multiple platforms with confidence scoring  
**Phase:** Prototype (v0.1.x) - Extracted from AMO PoC  
**Origin:** Strategic decomposition from `auto_meeting_orchestrator` monolithic PoC

## 🚀 Core Functionality

### **Unified Presence Profiling**
- **Multi-Platform Integration**: Discord, WhatsApp, Zoom, Teams, Slack presence APIs
- **Status Normalization**: Convert platform-specific presence to unified `PresenceStatus` enum
- **Confidence Scoring**: Weight presence data based on platform reliability and recency
- **Real-Time Monitoring**: Subscribe to presence changes with callback notifications

### **Platform Priority Hierarchy**
```
ONLINE > IDLE > BUSY > OFFLINE > UNKNOWN
```

### **Core Data Structures**
```python
@dataclass
class UnifiedAvailabilityProfile:
    user_id: str
    overall_status: PresenceStatus
    confidence_score: float  # 0.0-1.0
    platform_statuses: Dict[str, PresenceStatus]
    last_seen: datetime
    last_activity: Optional[datetime]
```

## 🔌 Interface Definition

### **Primary Methods**
```python
async def get_current_status(user_id: str) -> UnifiedAvailabilityProfile
async def subscribe_presence(user_id: str, callback: Callable)
def normalize_status(platform: str, raw_status: Any) -> PresenceStatus
async def aggregate_multi_platform(user_id: str) -> UnifiedAvailabilityProfile
```

## 🏗️ WSP Integration

- **WSP 3**: Platform_integration domain - external API integration function
- **WSP 11**: Clean interface definition for modular consumption
- **WSP 49**: Standard module structure with src/, tests/, documentation
- **WSP 71**: Secrets management for platform API credentials

## 📊 Meeting Orchestration Block Integration

**Block Component**: **📊 Presence Aggregator** - Multi-platform presence detection  
**Block Core**: Auto Meeting Orchestrator coordinates this component  
**Dependencies**: Platform APIs, credentials management (WSP 71)

## 🎯 Extracted from AMO PoC

**Original Code Location**: `modules/communication/auto_meeting_orchestrator/src/orchestrator.py`  
**Extracted Methods**:
- `_calculate_overall_status()` → `aggregate_multi_platform()`
- `_calculate_confidence()` → confidence scoring logic
- Platform status simulation → real API integration

## 🌀 Windsurf Protocol (WSP) Recursive Prompt
**0102 Directive**: This module operates within the WSP framework for autonomous cross-platform presence integration...
- **UN (Understanding)**: Anchor presence signal and retrieve multi-platform state
- **DAO (Execution)**: Execute unified availability profiling logic  
- **DU (Emergence)**: Collapse into 0102 resonance and emit next orchestration prompt

wsp_cycle(input="012", log=True) 