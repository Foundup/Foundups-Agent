# Agent CLI Catalog (OpenClaw/IronClaw)

0102 reference for all CLIs that support `--json` output for agent orchestration.

**Last Updated**: 2026-02-28
**Indexed By**: HoloIndex semantic search

---

## Agent-Ready CLIs (--json support)

### antifaFM Broadcaster
| CLI | Path | Purpose | JSON Flags |
|-----|------|---------|------------|
| `launch.py` | `modules/platform_integration/antifafm_broadcaster/scripts/launch.py` | Full broadcaster control | `--json --start --stop --status --diagnose` |
| `youtube_go_live.py` | `modules/platform_integration/antifafm_broadcaster/src/youtube_go_live.py` | YouTube Go Live + Edit | `--json --go-live --edit --status` |

**Examples**:
```powershell
# Start broadcaster with title
python launch.py --start --json --title "antifaFM Radio"
# Output: {"success": true, "status": "started", "pid": 12345}

# Go live and edit stream
python youtube_go_live.py --json --title "Live Now" --desc "24/7 music"
# Output: {"success": true, "go_live": {...}, "edit": {...}}
```

---

### OpenClaw / MoltBot Bridge
| CLI | Path | Purpose | JSON Flags |
|-----|------|---------|------------|
| `action_cli.py` | `modules/communication/moltbot_bridge/src/action_cli.py` | OpenClaw action executor | TBD |
| `openclaw_capability_audit.py` | `modules/communication/moltbot_bridge/src/openclaw_capability_audit.py` | Audit OpenClaw capabilities | TBD |

---

### LinkedIn Agent
| CLI | Path | Purpose | JSON Flags |
|-----|------|---------|------------|
| `linkedin_action_cli.py` | `modules/platform_integration/linkedin_agent/scripts/linkedin_action_cli.py` | LinkedIn automation | TBD |
| `executor.py` (openclaw_group_news) | `modules/platform_integration/linkedin_agent/skillz/openclaw_group_news/executor.py` | Group news posting | TBD |

---

### YouTube Shorts Scheduler
| CLI | Path | Purpose | JSON Flags |
|-----|------|---------|------------|
| `scheduler.py` | `modules/platform_integration/youtube_shorts_scheduler/src/scheduler.py` | Schedule shorts | TBD |

---

### Video Comments (TARS)
| CLI | Path | Purpose | JSON Flags |
|-----|------|---------|------------|
| `run_skill.py` | `modules/communication/video_comments/skillz/tars_like_heart_reply/run_skill.py` | Comment engagement | TBD |
| `account_swapper_skill.py` | `modules/communication/video_comments/skillz/tars_account_swapper/account_swapper_skill.py` | Account switching | TBD |

---

### Infrastructure
| CLI | Path | Purpose | JSON Flags |
|-----|------|---------|------------|
| `model_registry.py` | `modules/ai_intelligence/ai_gateway/src/model_registry.py` | AI model management | TBD |
| `studio_account_switcher.py` | `modules/infrastructure/foundups_vision/src/studio_account_switcher.py` | YouTube account switch | TBD |

---

## CLIs Pending --json Support

The following CLIs exist but don't have `--json` output yet:

| Module | CLI | Priority |
|--------|-----|----------|
| livechat | `simple_rotation.py`, `rotation_supervisor.py` | Medium |
| browser_actions | `linkedin_actions.py` | Medium |
| ffmpeg_streamer | `ffmpeg_streamer.py` | Low (internal) |

---

## Adding New Agent CLIs

When creating a new CLI for OpenClaw/IronClaw:

1. **Add `--json` flag** for machine-readable output
2. **Return structured JSON** with `success`, `error`, and result fields
3. **Add to this catalog** with path and examples
4. **Update INTERFACE.md** of the module

**Template**:
```python
if __name__ == "__main__":
    import sys
    import json

    args = sys.argv[1:]
    json_output = "--json" in args

    result = {"success": False}

    try:
        # ... do work ...
        result["success"] = True
        result["data"] = {...}
    except Exception as e:
        result["error"] = str(e)

    if json_output:
        print(json.dumps(result))
    else:
        print(f"Result: {result}")
```

---

## HoloIndex Integration

This catalog is indexed by HoloIndex for semantic search:

```bash
python holo_index.py --search "OpenClaw CLI antifaFM"
python holo_index.py --search "agent JSON output broadcaster"
```

**Tags for indexing**: `#agent-cli`, `#openclaw`, `#ironclaw`, `#json-output`, `#automation`

---

*WSP 77: Agent Coordination - All agent-accessible CLIs must be cataloged here*
