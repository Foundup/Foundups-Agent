# LiveChat Module Test Suite

This directory contains tests for the LiveChat module, which handles YouTube livestream chat functionality.

## Refactored Test Structure

The tests have been refactored into smaller, focused test files to improve maintainability and clarity. This approach aligns with the WSP guidelines for modular testing.

| Test File | Description |
|-----------|-------------|
| test_livechat_initialization.py | Tests for LiveChatListener initialization, parameter handling, session setup, ID handling, and greeting messages |
| test_livechat_message_polling.py | Tests for polling messages from YouTube API, error handling, rate limiting, and chat cycles |
| test_livechat_message_processing.py | Tests for message processing, metadata extraction, author role detection, trigger pattern detection, log entry creation, and file logging |
| test_livechat_message_sending.py | Tests for the `send_chat_message` method functionality, including success cases, truncation, error handling, greeting message sending, and emoji trigger message interactions |
| test_livechat_auth_handling.py | Tests for authentication error handling (`_handle_auth_error` method) |
| test_livechat_emoji_triggers.py | Tests for emoji trigger detection and response |
| test_livechat_rate_limiting.py | Tests for user rate limiting functionality (`_is_rate_limited` and `_update_trigger_time` methods) |
| test_livechat_logging.py | Tests for message logging functionality |
| test_livechat_viewer_tracking.py | Tests for the `_update_viewer_count` method, covering successful updates, error handling for API errors, and handling of various malformed API responses |
| test_livechat_lifecycle.py | Tests for the listener lifecycle (start/stop) including `start_listening`, `stop_listening`, and `_poll_chat_cycle` methods that control the operational lifecycle of the LiveChatListener |
| test_livechat_session_management.py | Tests for session management functionality, including getting and validating live chat IDs (`_get_live_chat_id`) and initializing chat sessions (`_initialize_chat_session`) with proper error handling |
| test_livechat_auto_moderation.py | Tests for auto-moderation functionality, including banned phrase detection, user timeout logic, YouTube API integration, cooldown management, and error handling for the AutoModerator class and its integration with LiveChatListener |
| test_quota_manager.py | *Note: This file tests the QuotaManager class from utils.oauth_manager and is not directly related to the LiveChatListener. It will be relocated to a more appropriate location (utils/tests/ or utils/oauth_manager/tests/) as part of a planned task (see APS Task List).* |

## Test Coverage

The test suite aims to achieve over 90% coverage of the LiveChat module code, as required by WSP 5. The refactoring into smaller test files helps identify coverage gaps more effectively.

## Known Issues

- *All major issues have been resolved through the test consolidation and refactoring process*
- *The `test_quota_manager.py` file is currently misplaced in this directory and will be relocated to an appropriate utils test directory in a future task*

## Running Tests

To run all tests for the LiveChat module:

```bash
python -m pytest modules/livechat/tests/
```

To run specific test files:

```bash
python -m pytest modules/livechat/tests/test_livechat_initialization.py
```

To run with coverage reporting:

```bash
python -m pytest modules/livechat/tests/ --cov=modules.livechat.src --cov-report term-missing
```

## Refactoring Progress

- ✅ Initialization tests consolidated in test_livechat_initialization.py (Phase 3a complete)
- ✅ Message polling tests consolidated in test_livechat_message_polling.py (Phase 3b complete)
- ✅ Message processing tests consolidated in test_livechat_message_processing.py (Phase 3c complete)
- ✅ Message sending tests consolidated in test_livechat_message_sending.py (Phase 3d complete)
- ✅ Session management tests created in test_livechat_session_management.py (Phase 3e complete)
- ✅ Authentication handling tests consolidated in test_livechat_auth_handling.py (Phase 3f complete)
- ✅ Rate limiting tests consolidated in test_livechat_rate_limiting.py (Phase 3g complete)
- ✅ Emoji trigger tests consolidated in test_livechat_emoji_triggers.py (Phase 3h complete)
- ✅ Lifecycle tests consolidated in test_livechat_lifecycle.py (Phase 3i complete)
- ✅ Viewer tracking tests created in test_livechat_viewer_tracking.py (Phase 3j complete)
- ✅ Logging tests consolidated in test_livechat_logging.py (Phase 3k complete)
- ✅ Auto-moderation tests created in test_livechat_auto_moderation.py (Phase 3l complete)
- ✅ Remove duplicate tests from test_livechat.py
- ✅ Complete remaining specialized test files

## Consolidation Notes

- Initialization tests from test_initialize_session_coverage.py have been moved to test_livechat_initialization.py
- Poll chat cycle tests from test_chat_cycle_coverage.py have been moved to test_livechat_message_polling.py
- Message sending tests have been consolidated into a comprehensive test suite in test_livechat_message_sending.py
- Removed duplicate `test_handle_emoji_trigger_send_failure` from test_emoji_trigger_coverage.py as its functionality is now covered in test_livechat_message_sending.py
- Session management tests written from scratch to test `_get_live_chat_id` and `_initialize_chat_session` methods
- Auth handling tests moved from test_handle_auth_error_minimal.py to test_livechat_auth_handling.py
- Rate limiting tests consolidated in test_livechat_rate_limiting.py with new tests for `_is_rate_limited` and `_update_trigger_time` 
- Emoji trigger tests moved from test_emoji_trigger_coverage.py to test_livechat_emoji_triggers.py
- Lifecycle tests (start/stop listening, poll_chat_cycle) consolidated in test_livechat_lifecycle.py, including implementation of a new test for stop_listening method 
- Viewer tracking tests added to test the `_update_viewer_count` method, including successful updates and handling of various error conditions 
- Logging tests consolidated in test_livechat_logging.py, including comprehensive tests for the `_log_to_user_file` method with tests for success cases, file errors, directory creation errors, and JSON serialization errors 
- Auto-moderation tests created in test_livechat_auto_moderation.py, covering the AutoModerator class functionality, integration with LiveChatListener, banned phrase detection, timeout logic, API error handling, and cooldown management
- All specialized test files have been fully consolidated, with their functionality moved to the appropriate modular test files 