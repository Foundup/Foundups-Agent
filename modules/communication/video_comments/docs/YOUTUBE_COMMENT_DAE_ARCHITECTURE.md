# YouTube Comment Responder DAE Architecture

This document describes the detailed architecture for the YouTube Comment Responder DAE, expanding on the Cube-Level DAE Orchestration Protocol.

## 1. YouTube Platform Cube Architecture

### 1.1 Core Modules
- `livechat_core.py`: Core orchestrator.
- `message_processor.py`: Message pipeline.
- `auto_moderator_dae.py`: Autonomous decisions.
- `chat_sender.py`: Message delivery.
- `chat_poller.py`: Live chat polling.
- `stream_resolver.py`: Stream discovery.
- `youtube_auth.py`: Credential management.
- `quota_monitor.py`: Quota tracking.

## 2. YouTube Comment DAE Extension (WSP 27 Pattern)

- **Signal**: `comment_detector.py`, `mention_scanner.py`, `reply_tracker.py`.
- **Knowledge**: `comment_memory.py`, `user_profiles.py`, `response_templates.py`.
- **Protocol**: `comment_processor.py`, `response_generator.py`, `thread_manager.py`.
- **Agentic**: `comment_responder_dae.py`, `account_switcher.py`, `quota_optimizer.py`.

## 3. API & Account Switching
- Uses `UC-LSSlOZwpGIRIYihaz8zCw` (Move2Japan) for primary responses.
- Uses `UCfHM9Fw9HD-NwiS0seD_oIA` (UnDaoDu) for community interactions.
- Implements smart account switching to minimize browser session disruptions.

*Refer to the original WSP 80 Extension (Archived) for detailed code snippets and quota cost analysis.*
