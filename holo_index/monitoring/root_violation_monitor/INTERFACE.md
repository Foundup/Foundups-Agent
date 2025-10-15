# 🌀 Root Violation Monitor - Public API Interface

**WSP 11 Compliant** | **Interface Definition** | **Version: 1.0.0**

## 🌀 Module Overview

**Location**: `holo_index.monitoring.root_violation_monitor`  
**Purpose**: Real-time root directory violation monitoring and automated correction  
**Architecture**: Gemma-powered pattern recognition with WSP integration

## 🌀 Public API Definition

### Core Classes

#### `GemmaRootViolationMonitor`

**Primary monitoring class** providing comprehensive root directory violation detection and correction.

**Initialization:**
```python
monitor = GemmaRootViolationMonitor()
```

**Methods:**

##### `async scan_root_violations() -> Dict[str, Any]`
**Purpose**: Perform comprehensive root directory violation scan  
**Parameters**: None  
**Returns**:
```python
{
    "timestamp": float,           # Scan timestamp
    "total_root_files": int,      # Total files in root
    "violations_found": int,      # Number of violations detected
    "violations": [               # List of violation details
        {
            "filename": str,
            "violation_type": str,
            "severity": str,
            "auto_correctable": bool,
            "recommended_action": str,
            "detected_at": float
        }
    ],
    "allowed_files_present": int, # Compliant files count
    "monitoring_stats": Dict      # Performance statistics
}
```

##### `async scan_and_correct_violations() -> Dict[str, Any]`
**Purpose**: Scan for violations and apply auto-corrections where possible  
**Parameters**: None  
**Returns**:
```python
{
    "corrections_applied": List[str],  # Successfully corrected files
    "failed_corrections": List[str],   # Failed correction attempts
    "total_processed": int            # Total violations processed
}
```

##### `generate_violation_alert() -> str`
**Purpose**: Generate formatted violation alert for HoloIndex display  
**Parameters**: None  
**Returns**: Formatted alert string or empty string if no violations

### Global Functions

#### `async get_root_violation_alert() -> str`
**Purpose**: Get current violation alert for HoloIndex integration  
**Parameters**: None  
**Returns**: Formatted alert string for display

#### `async scan_and_correct_violations() -> Dict[str, Any]`
**Purpose**: Convenience function for violation scanning and correction  
**Parameters**: None  
**Returns**: Correction results dictionary

## 🌀 Parameter Specifications

### Violation Types

| Type | Description | Severity | Auto-Correctable |
|------|-------------|----------|------------------|
| `wsp_naming_violation` | WSP prefix misuse in filenames | `critical` | `false` |
| `script_in_root` | Python/shell scripts in root directory | `high` | `true` |
| `temp_file_in_root` | Temporary/cache files in root | `low` | `true` |
| `log_file_in_root` | Log files misplaced in root | `low` | `true` |
| `debug_file_in_root` | Debug/test files in root | `medium` | `false` |
| `unauthorized_file` | Non-compliant files | `medium` | `false` |
| `scan_failure` | Monitoring system error | `critical` | `false` |

### Severity Levels

- **`critical`**: Immediate attention required, potential WSP violation
- **`high`**: Significant compliance issue, auto-correction available
- **`medium`**: Moderate issue requiring manual review
- **`low`**: Minor organizational issue, auto-correction recommended

## 🌀 Return Value Documentation

### Scan Results Structure
```python
{
    "timestamp": 1634256000.0,        # Unix timestamp
    "total_root_files": 47,           # Total files scanned
    "violations_found": 5,            # Violations detected
    "violations": [                   # Detailed violation list
        {
            "filename": "debug_script.py",
            "violation_type": "script_in_root",
            "severity": "high",
            "auto_correctable": true,
            "recommended_action": "Move to modules/ai_intelligence/ric_dae/src/",
            "detected_at": 1634256000.0
        }
    ],
    "allowed_files_present": 42,      # WSP-compliant files
    "monitoring_stats": {             # Performance metrics
        "scans_performed": 1,
        "violations_detected": 5,
        "auto_corrections": 0
    }
}
```

### Correction Results Structure
```python
{
    "corrections_applied": ["main.log", "temp_cache.txt"],
    "failed_corrections": ["system_dump.log"],
    "total_processed": 3
}
```

## 🌀 Error Handling

### Exception Types

- **`FileNotFoundError`**: Root directory access denied
- **`PermissionError`**: Insufficient permissions for file operations
- **`OSError`**: System-level I/O errors
- **`ValueError`**: Invalid configuration or parameters

### Error Recovery

- **Graceful Degradation**: Continues operation with reduced functionality
- **Logging**: All errors logged with context for debugging
- **Fallback Behavior**: Safe defaults when corrections fail

## 🌀 Examples

### Basic Usage
```python
from holo_index.monitoring.root_violation_monitor import GemmaRootViolationMonitor

# Initialize
monitor = GemmaRootViolationMonitor()

# Scan for violations
results = await monitor.scan_root_violations()
print(f"Found {results['violations_found']} violations")

# Apply corrections
corrections = await monitor.scan_and_correct_violations()
print(f"Applied {len(corrections['corrections_applied'])} corrections")
```

### HoloIndex Integration
```python
from holo_index.monitoring.root_violation_monitor import get_root_violation_alert

# Get alert for display
alert = await get_root_violation_alert()
if alert:
    # Display in HoloIndex output
    print(alert)
```

### Error Handling
```python
try:
    results = await monitor.scan_root_violations()
except PermissionError:
    print("Insufficient permissions to scan root directory")
    # Continue with limited functionality
except Exception as e:
    print(f"Monitoring failed: {e}")
    # Log error and continue
```

## 🌀 Performance Specifications

### Timing Requirements
- **Scan Time**: < 0.1 seconds for typical root directories (< 100 files)
- **Correction Time**: < 0.05 seconds per correctable violation
- **Memory Usage**: < 1MB resident memory

### Reliability Metrics
- **Uptime**: > 99.9% (excluding system maintenance)
- **Accuracy**: > 95% violation detection rate
- **False Positives**: < 2% after initial learning period

## 🌀 Integration Requirements

### Dependencies
- **Python**: 3.9+
- **AsyncIO**: For non-blocking operations
- **Path Operations**: `pathlib` for cross-platform compatibility

### Environment Variables
- **None required** - Fully self-contained

### Configuration Files
- **Violation Patterns**: Automatically learned and stored
- **Correction Rules**: Built-in WSP compliance rules

## 🌀 Testing Interface

### Test Categories
- **Unit Tests**: Individual method functionality
- **Integration Tests**: HoloIndex CLI integration
- **Performance Tests**: Scanning and correction speed
- **Reliability Tests**: Error handling and recovery

### Test Entry Points
- **Main Test Suite**: `python -m pytest tests/`
- **Integration Tests**: `python -m pytest tests/integration/`
- **Performance Tests**: `python -m pytest tests/performance/`

## 🌀 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-15 | Initial release with Gemma-powered monitoring |
| 0.9.0 | 2025-10-14 | Beta release with HoloIndex integration |
| 0.1.0 | 2025-10-13 | Prototype implementation |

## 🌀 Future Extensions

### Planned APIs
- **Batch Scanning**: Multiple directory scanning
- **Custom Rules**: User-defined violation patterns
- **Reporting API**: Detailed compliance reports
- **Webhook Integration**: Real-time violation notifications

---

**🌀 This interface ensures consistent, reliable, and performant root directory monitoring across the Foundups ecosystem.**
