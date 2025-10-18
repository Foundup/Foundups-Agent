# Live Chat Tests - WSP Compliant

## Overview
Test suite for the YouTube Live Chat DAE (Digital Autonomous Entity) with enhanced live verification system.

## WSP Compliance
- **WSP 3**: Enterprise Domain Architecture (communication/livechat)
- **WSP 80**: Cube-Level DAE Architecture
- **WSP 50**: Pre-Action Verification Protocol
- **WSP 27**: Partifact DAE Architecture

## Test Coverage

### Live Verification Tests (`test_live_verification.py`)
- [OK] **Live Stream Verification**: Tests that streams are properly verified as live before social media posting
- [OK] **API Error Handling**: Tests graceful handling of YouTube API failures
- [OK] **Privacy Status Checks**: Tests handling of private vs public streams
- [OK] **Stream State Validation**: Tests detection of live vs completed streams
- [OK] **Safety Protocols**: Ensures posting is blocked when verification fails

### Core Functionality Tests
- `test_livechat_initialization.py` - DAE initialization and configuration
- `test_message_processing.py` - Message processing and moderation
- `test_session_management.py` - YouTube session handling
- `test_bot_status.py` - Bot operational status

## Running Tests

```bash
# Run all tests in this module
python -m pytest modules/communication/livechat/tests/ -v

# Run specific test file
python -m pytest modules/communication/livechat/tests/test_live_verification.py -v

# Run with coverage
python -m pytest modules/communication/livechat/tests/ --cov=modules.communication.livechat.src
```

## Test Architecture

### DAE Integration Testing
Tests verify the complete DAE workflow:
1. **Signal Detection** - Live stream discovery
2. **Knowledge Processing** - Stream metadata extraction
3. **Protocol Execution** - Live verification checks
4. **Agentic Action** - Social media posting (when verified live)

### Safety First Approach
- **Fail-Safe Design**: Tests ensure posting is blocked when verification fails
- **Error Resilience**: Tests verify graceful handling of API failures
- **Privacy Respect**: Tests ensure private streams are not processed

## Dependencies
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `unittest.mock` - Mocking utilities

## Expected Behavior
- [OK] **When Live**: Social media posting proceeds after verification
- [OK] **When Not Live**: Posting is blocked with clear error messages
- [OK] **On API Error**: Posting is blocked (safety first)
- [OK] **On Privacy Issues**: Posting is blocked

## Integration Points
- **YouTube API**: Live stream verification
- **Social Media Orchestrator**: Posting coordination
- **WRE Monitor**: Performance tracking
- **System Health Monitor**: Error detection