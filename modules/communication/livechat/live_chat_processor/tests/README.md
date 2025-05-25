# Live Chat Processor Module Test Suite

This directory contains tests for the Live Chat Processor module, which processes and handles incoming YouTube live chat messages.

## Test Files

| Test File | Description |
|-----------|-------------|
| test_live_chat_processor.py | Tests for message processing, parsing, filtering, and routing |

## Test Coverage

The test suite aims to maintain comprehensive coverage of the Live Chat Processor module in compliance with WSP 5 requirements.

## Running Tests

To run all tests for the Live Chat Processor module:

```bash
python -m pytest modules/live_chat_processor/tests/
```

To run with coverage reporting:

```bash
python -m pytest modules/live_chat_processor/tests/ --cov=modules.live_chat_processor.src --cov-report term-missing
```

## Module Test Focus

The Live Chat Processor tests focus on:

1. **Message Parsing**: Correctly extracting content, metadata, and user information
2. **Message Filtering**: Properly applying filters for spam, known patterns, and unwanted content
3. **Message Routing**: Directing messages to appropriate handlers based on content
4. **Command Detection**: Identifying and processing command-like messages
5. **Error Handling**: Gracefully handling malformed messages and edge cases

These tests ensure that incoming chat messages are properly processed and routed to the appropriate handlers within the system. 