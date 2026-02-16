# HoloIndex Public Interface

## Overview
HoloIndex has evolved into an autonomous intelligence foundation with HoloDAE - the "green foundation board agent" that comes with every LEGO set. Every search now triggers automatic intelligence analysis.

## Module API

### Core Search Interface (Now with HoloDAE Intelligence)

```python
from holo_index.cli import HoloIndex

# Initialize
holo = HoloIndex(ssd_path="E:/HoloIndex")

# Search for code and WSP guidance
results = holo.search(
    query="send chat message",
    limit=5  # Results per category
)

# Results structure
{
    'code': [
        {
            'score': float,  # Similarity score
            'module': str,   # Module path
            'function': str, # Function/class name
            'content': str,  # Code snippet
            'file': str,     # Source file
            'cube': str      # Optional cube tag
        }
    ],
    'wsps': [
        {
            'score': float,
            'wsp': str,      # WSP identifier
            'title': str,    # WSP title
            'content': str,  # Relevant section
            'file': str      # Source document
        }
    ],
    'health_notices': [...],  # Module health warnings
    'adaptive_learning': {...}  # Learning metrics
}
```

### Indexing Interface

```python
# Index code entries
holo.index_code_entries()
# Includes NAVIGATION + web assets under HOLO_WEB_INDEX_ROOTS (default: public/)

# Index WSP documents
holo.index_wsp_entries(paths=[Path("WSP_framework/")])

# Index everything
holo.index_all()
```

Web indexing controls:
- `HOLO_INDEX_WEB=1|0` (default `1`)
- `HOLO_WEB_INDEX_ROOTS` (default `public`, semicolon-separated)
- `HOLO_WEB_INDEX_EXTENSIONS` (default `.html;.js;.mjs;.cjs;.css`)
- `HOLO_WEB_INDEX_MAX_FILES` (default `300`)
- `HOLO_WEB_INDEX_MAX_CHARS` (default `5000`)

### HoloDAE Autonomous Intelligence Interface

```python
from holo_index.qwen_advisor.autonomous_holodae import autonomous_holodae

# Start autonomous monitoring (like YouTube DAE)
autonomous_holodae.start_autonomous_monitoring()

# Get status report
status = autonomous_holodae.get_status_report()
# Returns: {
#     'active': bool,
#     'uptime_minutes': int,
#     'files_watched': int,
#     'current_module': str,
#     'task_pattern': str,
#     'session_actions': int,
#     'last_activity': str
# }

# Stop monitoring
autonomous_holodae.stop_autonomous_monitoring()

# Manual request handling (automatic via CLI)
report = autonomous_holodae.handle_holoindex_request(query, search_results)
```

### AI Advisor Interface

```python
from holo_index.qwen_advisor.advisor import QwenAdvisor, AdvisorContext

# Initialize advisor
advisor = QwenAdvisor()

# Create context
context = AdvisorContext(
    query="create new module",
    code_hits=[...],  # From search results
    wsp_hits=[...]    # From search results
)

# Get guidance
result = advisor.generate_guidance(context)

# Result structure
{
    'guidance': str,        # Primary guidance text
    'reminders': List[str], # WSP reminders
    'todos': List[str],     # Action items
    'metadata': {
        'risk_level': str,
        'intent': str,
        'violations': List[str],
        'llm_used': bool,
        'wsp_analysis': {...}
    }
}
```

### Pattern Coach Interface

```python
from holo_index.qwen_advisor.pattern_coach import PatternCoach

# Initialize coach
coach = PatternCoach()

# Analyze and get coaching
coaching = coach.analyze_and_coach(
    query="test the system",
    search_results=[...],
    health_warnings=[...]
)

# Record outcome for learning
coach.record_coaching_outcome(
    coaching=coaching,
    followed=True,
    reward_earned=5
)

# Get statistics
stats = coach.get_coaching_stats()
```

### DAE Cube Organizer Interface

```python
from holo_index.dae_cube_organizer.dae_cube_organizer import DAECubeOrganizer

# Initialize organizer
organizer = DAECubeOrganizer()

# Get DAE context
context = organizer.initialize_dae_context("YouTube Live")

# Context structure
{
    'dae_identity': {
        'name': str,
        'emoji': str,
        'description': str,
        'orchestrator': str,
        'main_py_reference': str
    },
    'module_map': {
        'ascii_map': str,
        'modules': List[Dict]
    },
    'orchestration_flow': {
        'phases': List[str],
        'loop_type': str
    },
    'quick_reference': {...},
    'rampup_guidance': {...}
}
```

### Violation Tracking Interface

```python
from holo_index.violation_tracker import ViolationTracker

# Initialize tracker
tracker = ViolationTracker()

# Record violation
tracker.record_violation(
    wsp="WSP 49",
    module="holo_index",
    severity="MEDIUM",
    description="Missing required structure",
    agent="0102"
)

# Query violations
violations = tracker.get_violations_by_module("holo_index")
summary = tracker.get_summary()
```

## CLI Commands

### Search
```bash
python holo_index.py --search "query" [options]
  --limit N           # Results per category (default: 5)
  --llm-advisor      # Enable AI advisor
  --no-advisor       # Disable advisor
```

### Indexing
```bash
python holo_index.py --index-all     # Index everything
python holo_index.py --index-code    # Index code only
python holo_index.py --index-wsp     # Index WSP only
```

### HoloDAE Autonomous Monitoring
```bash
python holo_index.py --start-holodae  # Start autonomous monitoring
python holo_index.py --stop-holodae   # Stop monitoring
python holo_index.py --holodae-status # Get status report

# Or via main.py:
python main.py --holo                  # Start HoloDAE monitoring
```

### DAE Initialization
```bash
python holo_index.py --init-dae [DAE_NAME]
  # Examples:
  --init-dae                    # Auto-detect DAE
  --init-dae "YouTube Live"     # YouTube DAE
  --init-dae "AMO"             # Meeting orchestration
```

### Feedback
```bash
python holo_index.py --advisor-rating useful|needs_more
python holo_index.py --ack-reminders  # Acknowledge reminders
```

## Integration Points

### With NAVIGATION.py
```python
# HoloIndex automatically loads NAVIGATION.py mappings
from NAVIGATION import NEED_TO
# These are integrated into search results
```

### With main.py
```python
# DAE Cube Organizer understands main.py structure
# Provides menu option mappings and orchestrator references
```

### With WSP Framework
```python
# WSP Master loads all protocols from WSP_framework/
# Provides intelligent protocol selection and guidance
```

## Error Handling

All methods may raise:
- `FileNotFoundError`: Missing required files
- `ImportError`: Missing dependencies
- `ValueError`: Invalid parameters
- `RuntimeError`: Initialization failures

## Performance Considerations

- **First Load**: ~2-3 seconds (model loading)
- **Subsequent Searches**: <200ms
- **Memory Usage**: ~1GB with all models
- **SSD Required**: For ChromaDB performance
- **Cache**: Results cached for 15 minutes

## WSP Compliance

This interface follows:
- **WSP 11**: Complete interface documentation
- **WSP 49**: Module structure standards
- **WSP 87**: Code navigation protocol
- **WSP 84**: Code memory verification
