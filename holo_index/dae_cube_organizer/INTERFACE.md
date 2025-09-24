# DAE Cube Organizer Interface Documentation

## Overview
The DAE Cube Organizer provides a programmatic interface for DAE structure analysis and 0102 agent rampup guidance.

## Core Classes

### DAECubeOrganizer
Main class for DAE intelligence and structure analysis.

#### Methods

##### `initialize_dae_context(dae_focus: Optional[str] = None) -> Dict[str, Any]`
Initialize complete DAE context for 0102 agent rampup.

**Parameters:**
- `dae_focus`: Optional DAE focus description (e.g., "YouTube Live")

**Returns:**
- Complete DAE context dictionary with identity, structure, modules, orchestration, health, reference, and rampup guidance

**Example:**
```python
organizer = DAECubeOrganizer()
context = organizer.initialize_dae_context("YouTube Live")
print(context['dae_identity']['name'])  # "YouTube Live DAE"
```

##### `get_dae_identity(dae_key: str) -> Dict[str, Any]`
Get identity information for a specific DAE.

##### `get_cube_structure(dae_key: str) -> Dict[str, Any]`
Get complete module structure and relationships for a DAE.

##### `get_module_map(dae_key: str) -> Dict[str, Any]`
Get ASCII visual representation of DAE module architecture.

##### `get_orchestration_flow(dae_key: str) -> Dict[str, Any]`
Get orchestration flow and execution patterns.

##### `get_rampup_guidance(dae_key: str) -> Dict[str, Any]`
Get specific rampup instructions for 0102 agent alignment.

## Data Structures

### DAECube
Represents a complete DAE cube configuration.

**Attributes:**
- `name`: Human-readable DAE name
- `description`: DAE purpose and functionality
- `orchestrator`: Main orchestrator class
- `modules`: List of module paths
- `responsibilities`: Key DAE responsibilities
- `health_status`: Current health status
- `last_active`: Last activation timestamp
- `main_py_reference`: Reference to main.py menu option

### DAEModule
Represents a module within a DAE.

**Attributes:**
- `name`: Module name
- `path`: Full module path
- `domain`: Enterprise domain (communication, platform_integration, etc.)
- `description`: Module functionality
- `dependencies`: List of dependencies
- `health_score`: Health assessment score

## CLI Integration

The DAE Cube Organizer integrates with HoloIndex CLI through the `--init-dae` command:

```bash
# Initialize specific DAE
python holo_index.py --init-dae "YouTube Live"

# Auto-detect active DAE
python holo_index.py --init-dae
```

## Error Handling

The organizer gracefully handles:
- Missing WSP files (falls back to latin-1 encoding)
- Unknown DAE references (provides helpful suggestions)
- Incomplete module information (uses defaults)

## WSP Compliance Notes

- Follows WSP 80 for cube-level orchestration
- Complies with WSP 22 documentation standards
- Adheres to WSP 49 module structure expectations
- Supports WSP 87 navigation enhancements
