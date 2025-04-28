# Live Chat Poller Module Test Suite

This directory contains tests for the Live Chat Poller module, which is responsible for polling and retrieving messages from YouTube live chat streams.

## Test Files

| Test File | Description |
|-----------|-------------|
| test_live_chat_poller.py | Tests for message polling, connection management, and error handling |

## Test Coverage

The test suite aims to maintain comprehensive coverage of the Live Chat Poller module in compliance with WSP 5 requirements.

## Running Tests

To run all tests for the Live Chat Poller module:

```bash
python -m pytest modules/live_chat_poller/tests/
```

To run with coverage reporting:

```bash
python -m pytest modules/live_chat_poller/tests/ --cov=modules.live_chat_poller.src --cov-report term-missing
```

## Module Test Focus

The Live Chat Poller tests focus on:

1. **Connection Management**: Establishing and maintaining connections to the YouTube API
2. **Message Retrieval**: Properly fetching and formatting chat messages
3. **Error Handling**: Gracefully managing API errors, rate limits, and network issues
4. **Pagination**: Correctly handling message pagination and continuation tokens
5. **Performance**: Ensuring efficient message polling with appropriate throttling 