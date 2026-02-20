# LiveChat Tests ModLog

## Test Coverage Summary
Tests for the YouTube LiveChat monitoring DAE system.

## Idle System Behavior Tests
- `test_idle_system_behavior.py` - Tests idle loop when no stream is active
  - Verifies NO-QUOTA mode is activated by default
  - Tests intelligent delay calculation progression
  - Ensures proper idle mode messages are displayed
  - Validates web scraping fallback when API unavailable

## NO-QUOTA Mode Tests
- `test_stream_detection_no_chatid.py` - Verifies stream detection works without chat_id
  - Tests that streams are accepted even when chat_id is None
  - Verifies proper logging when chat_id unavailable
  - Ensures system continues in NO-QUOTA mode

## Social Media Integration Tests
- `test_social_media_posting.py` - Tests LinkedIn/X posting when stream detected
  - Verifies SimplePostingOrchestrator is called
  - Tests NO-QUOTA mode triggers social posting
  - Ensures posting works without API credentials

## Core Functionality Tests
- `test_message_processor.py` - Message processing logic
- `test_chat_sender.py` - Chat message sending
- `test_chat_poller.py` - Chat polling mechanism
- `test_session_manager.py` - Session management

## System Test Utilities (Manual)
- `system_tests/verify_party.py` - Triggers hardened `!party` mode for UI-action verification (manual run)
- `system_tests/verify_party_behavior.py` - Connects to Chrome (9222) and runs a short reaction burst (manual run)

## Recent Improvements (2025-09-17)
- Enhanced NO-QUOTA mode to preserve API tokens
- Fixed stream detection to work without credentials
- Added social media posting in NO-QUOTA mode
- Improved title extraction for complete stream titles
- Fixed session initialization to continue for social posting

## Test Execution
```bash
# Run all tests
python -m pytest modules/communication/livechat/tests/ -v

# Run NO-QUOTA specific tests
python modules/communication/livechat/tests/test_stream_detection_no_chatid.py

# Run social media posting tests
python modules/communication/livechat/tests/test_social_media_posting.py
```

## Known Issues
- Some integration tests require live YouTube credentials
- Mock services used for testing when APIs unavailable