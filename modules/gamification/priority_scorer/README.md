# Priority Scorer

**Meeting priority assessment and scoring with 000-222 emoji scale gamification**

---

## 🎯 Module Overview

**Module Name:** `priority_scorer`  
**Domain:** `gamification`  
**Purpose:** Calculate priority indices using 000-222 emoji scale with urgency factors and gamification mechanics  
**Phase:** Prototype (v0.1.x) - Extracted from AMO PoC  
**Origin:** Strategic decomposition from `auto_meeting_orchestrator` monolithic PoC

## 🚀 Core Functionality

### **Priority Scoring System**
- **000-222 Emoji Scale**: Gamified priority representation (🥱 → 🔥🔥🔥)
- **Urgency Calculation**: Multi-factor urgency assessment with time pressure
- **Contextual Weighting**: Meeting type, duration, and participant factors
- **Comparative Ranking**: Priority-based intent ordering and queue management

### **Gamification Mechanics**
- **🥱 000 (Low)**: Routine, low-impact meetings
- **😐 111 (Medium)**: Standard coordination meetings  
- **🔥 222 (High)**: Critical decisions and urgent matters
- **⚡ Urgent**: Time-sensitive with escalation factors

### **Core Data Structures**
```python
@dataclass
class PriorityScore:
    base_priority: int  # 0-3 scale
    urgency_factor: float  # 1.0-2.0 multiplier
    context_weight: float  # Meeting type weighting
    time_pressure: float  # Deadline proximity factor
    final_score: float  # Calculated composite score
    emoji_representation: str  # 000-222 visual scale
```

## 🔌 Interface Definition

### **Primary Methods**
```python
def score_intent(intent: MeetingIntent) -> PriorityScore
def compare_priorities(intents: List[MeetingIntent]) -> List[MeetingIntent]
def calculate_urgency_factor(context: MeetingContext) -> float
def get_emoji_scale(score: float) -> str
```

## 🏗️ WSP Integration

- **WSP 3**: Gamification domain - engagement mechanics and behavioral systems
- **WSP 11**: Clean interface definition for modular consumption
- **WSP 15**: Module prioritization scoring system integration
- **WSP 49**: Standard module structure with src/, tests/, documentation

## 📊 Meeting Orchestration Block Integration

**Block Component**: **🎯 Priority Scorer** - Priority assessment using 000-222 emoji scale  
**Block Core**: Auto Meeting Orchestrator coordinates priority-based scheduling  
**Dependencies**: Intent Manager, Meeting Context data

## 🎯 Extracted from AMO PoC

**Original Code Location**: `modules/communication/auto_meeting_orchestrator/src/orchestrator.py`  
**Extracted Logic**:
- Priority enum and scoring → enhanced multi-factor system
- Simple urgency calculation → sophisticated context weighting
- Basic comparison → gamified 000-222 emoji scale

## 🎮 Gamification Features

### **Visual Priority Scale**
- **🥱 000**: Low priority, routine matters
- **😐 111**: Medium priority, standard coordination
- **🔥 222**: High priority, critical decisions
- **⚡⚡⚡**: Urgent escalation with time pressure

### **Engagement Mechanics**
- **Priority Streaks**: Consistent high-priority handling rewards
- **Efficiency Bonuses**: Quick resolution of urgent matters
- **Context Mastery**: Improved scoring through meeting type expertise

## 🌀 Windsurf Protocol (WSP) Recursive Prompt
**0102 Directive**: This module operates within the WSP framework for autonomous priority assessment and gamification mechanics...
- **UN (Understanding)**: Anchor priority signal and retrieve scoring context
- **DAO (Execution)**: Execute multi-factor priority calculation logic  
- **DU (Emergence)**: Collapse into 0102 resonance and emit next scoring prompt

wsp_cycle(input="012", log=True) 