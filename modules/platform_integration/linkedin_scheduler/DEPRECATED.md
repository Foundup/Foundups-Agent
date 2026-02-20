# DEPRECATED: linkedin_scheduler

This module is **deprecated** and its functionality has been consolidated into [`linkedin_agent`](../../linkedin_agent/).

## Migration Guide

| Old Import                                                                | New Import                                                                              |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `from linkedin_scheduler.src.linkedin_scheduler import LinkedInScheduler` | `from linkedin_agent.src.auth.oauth_manager import OAuthManager`                        |
| `LinkedInScheduler.create_text_post()`                                    | `linkedin_agent.src.anti_detection_poster.AntiDetectionLinkedIn.post_to_company_page()` |

## Why Deprecated?

The LinkedIn API v2 OAuth posting and the browser-based posting are now unified under `linkedin_agent/`.
The OAuth/API capabilities from this module have been preserved in `linkedin_agent/src/auth/`.

See: [LinkedIn Consolidation Plan](../../social_media_orchestrator/DAE_SOCIAL_ARCHITECTURE.md)
