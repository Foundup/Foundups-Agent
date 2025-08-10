# LinkedIn Automation (Deprecation Notice)

Status: Deprecated (docs-only pointer)

- The canonical posting and scheduling implementation lives in:
  - `modules/platform_integration/linkedin_scheduler/src/linkedin_scheduler.py`
  - Use `create_text_post`, `create_article_post`, and `PostQueue` for retries/backoff.

- Keep this directory for historical context and to avoid breaking imports. New work must reference `linkedin_scheduler` per WSP 65 (Component Consolidation) and WSP 66 (Proactive Modularization).


