# LinkedIn Module Architecture — Canonical Module

> **This is the canonical LinkedIn module.** All LinkedIn functionality should route through this module.

## Consolidated Structure

```
linkedin_agent/                        # ← CANONICAL LinkedIn module
├── src/
│   ├── linkedin_agent.py              # Core orchestrator & entry point
│   ├── anti_detection_poster.py       # Browser automation (posting)
│   ├── git_linkedin_bridge.py         # Git push → LinkedIn pipeline
│   ├── auth/                          # OAuth + session management
│   │   ├── credentials.py
│   │   ├── oauth_manager.py           # LinkedIn API v2 OAuth
│   │   └── session_manager.py
│   ├── engagement/                    # Feed reading & interaction
│   │   ├── feed_reader.py             # Read feed, identify posts
│   │   ├── interaction_manager.py     # Like, comment, react
│   │   ├── connection_manager.py      # Connection requests
│   │   └── messaging.py              # Direct messaging
│   ├── content/                       # Content generation
│   │   ├── content_templates.py       # Post templates (VC pushback, updates)
│   │   ├── hashtag_manager.py         # Hashtag strategy
│   │   ├── media_handler.py           # Image/video attachments
│   │   └── post_generator.py          # AI-generated content
│   └── automation/
│       └── post_scheduler.py          # Time-based scheduling
├── tests/                             # Full test suite
└── data/                              # Chrome profiles for browser automation
```

## Posting Paths

| Trigger             | Flow                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------- |
| Stream notification | `simple_posting_orchestrator` → `unified_linkedin_interface` → `anti_detection_poster`   |
| Git push            | `git_push_dae` / `idle_automation_dae` → `git_linkedin_bridge` → `anti_detection_poster` |
| Dev update          | `git_monitor_dae` → `unified_linkedin_interface` → `anti_detection_poster`               |
| Manual/scheduled    | `post_scheduler` → `anti_detection_poster`                                               |

## Engagement Paths

| Capability                         | Engine                                                 | Status                  |
| ---------------------------------- | ------------------------------------------------------ | ----------------------- |
| Feed reading + intelligent replies | `browser_actions/linkedin_actions.py` (UI-TARS Vision) | Primary — most advanced |
| Like, comment, connect             | `linkedin_agent/engagement/` (Selenium)                | Fallback                |

## Integration Points

| Consumer                | Imports                 | Purpose                                         |
| ----------------------- | ----------------------- | ----------------------------------------------- |
| `social_media_dae`      | `LinkedInAgent`         | AI decision layer — decides WHAT to post/engage |
| `workflow_orchestrator` | `LinkedInAgent`         | IDE-triggered workflows                         |
| `auto_stream_monitor`   | `AntiDetectionLinkedIn` | Stream notifications                            |
| `git_push_dae`          | `GitLinkedInBridge`     | Git commit posts                                |

## Deprecated Modules

| Module                          | Status              | Migration                                   |
| ------------------------------- | ------------------- | ------------------------------------------- |
| `linkedin_scheduler/`           | DEPRECATED          | API OAuth capabilities preserved in `auth/` |
| `utils/post_to_linkedin.py`     | DEPRECATED          | Import `AntiDetectionLinkedIn` directly     |
| `unified_linkedin_interface.py` | Pending deprecation | Will route through `linkedin_agent`         |

## Known Issues

1. **Browser Opens on Duplicates** — check happens after browser setup
2. **Failed Posts Keep Retrying** — needs max retry limit
3. **Dual Engagement Implementations** — UI-TARS and Selenium need unified entry point
