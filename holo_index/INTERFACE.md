# HoloIndex Public Interface

## Module API

### Core Search Interface

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

# Index WSP documents
holo.index_wsp_entries(paths=[Path("WSP_framework/")])

# Index everything
holo.index_all()
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