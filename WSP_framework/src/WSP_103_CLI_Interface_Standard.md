# WSP 103: CLI Interface Standard

**Status**: ACTIVE
**Version**: 1.0
**Date**: 2026-02-28
**Author**: 0102 (CLI Standardization)

---

## Executive Summary

WSP 103 establishes standards for command-line interfaces (CLIs) across the Foundups ecosystem. All CLIs that may be invoked by agents (OpenClaw, IronClaw, HoloDAE) MUST follow these standards for reliable automation.

**Key Principle**: Every CLI is an API endpoint for agents.

---

## Scope

This WSP applies to:
- Module launch scripts (`scripts/launch.py`)
- Skill executors (`skillz/*/executor.py`)
- Standalone tools with `if __name__ == "__main__"`
- Any Python script invoked by agents

**Related WSPs**:
- WSP 77: Agent Coordination (task dispatch logic)
- WSP 91: DAEMON Observability (telemetry output)
- WSP 90: UTF-8 Encoding (output encoding)

---

## Required CLI Flags

### Tier 1: Mandatory (All Agent-Accessible CLIs)

| Flag | Purpose | Output |
|------|---------|--------|
| `--json` | Machine-readable output | JSON to stdout |
| `--help`, `-h` | Usage documentation | Human-readable usage |

### Tier 2: Lifecycle CLIs (DAEs, Services)

| Flag | Purpose | Output |
|------|---------|--------|
| `--start` | Start service/process | `{"success": true, "pid": 12345}` |
| `--stop` | Stop service/process | `{"success": true, "stopped": true}` |
| `--status` | Check current state | `{"running": true, "status": "active"}` |

### Tier 3: Optional Enhancements

| Flag | Purpose | Output |
|------|---------|--------|
| `--diagnose` | Run diagnostics | `{"health": {...}, "errors": [...]}` |
| `--verbose`, `-v` | Detailed human output | Extended logging |
| `--quiet`, `-q` | Minimal output | Errors only |

---

## JSON Output Format

### Success Response
```json
{
  "success": true,
  "data": {
    "result": "...",
    "details": {}
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "error_code_snake_case",
  "message": "Human-readable error description"
}
```

### Status Response
```json
{
  "running": true,
  "status": "broadcasting",
  "uptime": 3600,
  "pid": 12345
}
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Connection/resource error |
| 4 | Permission denied |

---

## Implementation Template

```python
#!/usr/bin/env python3
"""
Module CLI - WSP 103 Compliant

Usage:
  python script.py --json --action "value"
"""

import sys
import json

def main():
    args = sys.argv[1:]
    json_output = "--json" in args

    # Parse flags
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    result = {"success": False}

    try:
        # ... do work ...
        result["success"] = True
        result["data"] = {"example": "value"}

    except Exception as e:
        result["error"] = type(e).__name__.lower()
        result["message"] = str(e)

    # Output
    if json_output:
        print(json.dumps(result))
    else:
        if result.get("success"):
            print(f"[OK] {result.get('data', {})}")
        else:
            print(f"[ERROR] {result.get('message', 'Unknown error')}")

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
```

---

## CLI Catalog Requirements

### Registration
All agent-accessible CLIs MUST be registered in:
- `holo_index/docs/AGENT_CLI_CATALOG.md`

### Catalog Entry Format
```markdown
| CLI | Path | Purpose | JSON Flags |
|-----|------|---------|------------|
| `launch.py` | `modules/.../scripts/launch.py` | Description | `--json --start --stop` |
```

### Indexing
The CLI catalog is indexed by HoloIndex for semantic search:
```bash
python holo_index.py --search "OpenClaw CLI broadcast"
```

---

## Agent Invocation Pattern

### OpenClaw/IronClaw
```python
import subprocess
import json

def invoke_cli(script_path: str, args: list[str]) -> dict:
    """Invoke CLI and parse JSON response."""
    cmd = ["python", script_path, "--json"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "invalid_json",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }

# Example usage
result = invoke_cli(
    "modules/platform_integration/antifafm_broadcaster/scripts/launch.py",
    ["--start", "--title", "antifaFM Radio"]
)
```

---

## Compliance Checklist

For each CLI:
- [ ] `--json` flag outputs valid JSON
- [ ] `--help` documents all flags
- [ ] Exit code 0 on success, non-zero on error
- [ ] Registered in AGENT_CLI_CATALOG.md
- [ ] UTF-8 output (WSP 90)

---

## Testing

### Validation Script
```bash
# Test JSON output
python script.py --json --status | python -c "import json, sys; json.load(sys.stdin)"

# Test exit codes
python script.py --invalid-flag; echo "Exit code: $?"
```

---

## Examples

### antifaFM Broadcaster (Reference Implementation)

**launch.py**:
```bash
python launch.py --json --start --title "Live Radio"
# {"success": true, "status": "started", "pid": 12345, "title": "Live Radio"}

python launch.py --json --status
# {"running": true, "status": "broadcasting", "uptime": 3600}

python launch.py --json --stop
# {"success": true, "stopped": true}
```

**youtube_go_live.py**:
```bash
python youtube_go_live.py --json --go-live --title "Stream Title"
# {"success": true, "go_live": {...}, "edit": {...}}
```

---

## Relationship to WSP 77

| WSP | Scope | Example |
|-----|-------|---------|
| WSP 77 | Agent task routing logic | "Route orphan analysis to Gemma" |
| WSP 103 | CLI interface standards | "--json output format" |

WSP 77 defines WHAT agents do.
WSP 103 defines HOW agents invoke CLIs.

---

**Protocol Status**: ACTIVE

**Catalog Location**: `holo_index/docs/AGENT_CLI_CATALOG.md`

**Compliance Verification**: `python holo_index.py --check-cli-compliance`

---

*WSP 103 ensures every CLI is agent-ready.*
