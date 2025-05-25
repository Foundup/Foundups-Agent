# Banter Engine Module Interface

## Overview
The Banter Engine module processes chat messages to find emoji sequences and generates themed responses. It implements the Emoji Sentiment Mapper (ESM) that maps emoji sequences to different conversational tones and states.

## Exports
This module exports:
- `BanterEngine`: Class for processing emoji sequences and generating responses

## Classes

### `BanterEngine`
Processes chat messages for emoji sequences and generates appropriate responses based on the sequence detected.

#### Constructor

##### `__init__()`
Initializes a new BanterEngine instance.

**Parameters:**
- None

**Behavior:**
- Loads the SEQUENCE_MAP data from sequence_responses.py
- Initializes the theme-based response system
- Populates themed responses from the sequence map examples

#### Public Methods

##### `process_input(input_text: str) -> Tuple[str, Optional[str]]`
Processes input text to identify emoji sequences and returns the corresponding state/tone information and response.

**Parameters:**
- `input_text`: Input text to process for emoji sequences

**Returns:**
- Tuple containing:
  - A string describing the state/tone (e.g., "State: awakening in progress, Tone: metaphoric, humor, symbolic wit")
  - An optional response message (or None if no sequence detected)

**Behavior:**
- Detects emoji sequences like "✊✊✊", "✊✋🖐️", etc.
- Looks up the corresponding state and tone in the sequence map
- Returns a description of the state/tone and an example response

##### `get_random_banter(theme: str = "default") -> str`
Returns a random banter message for the specified theme.

**Parameters:**
- `theme`: Theme to get a banter message for (default: "default")

**Returns:**
- A random banter message for the specified theme

**Behavior:**
- Selects a random response from the available responses for the specified theme
- Falls back to the default theme if the specified theme doesn't exist

##### `list_themes() -> List[str]`
Returns a list of available themes.

**Parameters:**
- None

**Returns:**
- A list of available theme names

**Behavior:**
- Returns a list of all themes for which responses are available

## Usage Example
```python
from modules.banter_engine import BanterEngine

# Create a banter engine instance
banter_engine = BanterEngine()

# List available themes
themes = banter_engine.list_themes()
print(f"Available themes: {themes}")

# Process a message with emoji sequence
result, response = banter_engine.process_input("Hey everyone ✊✋🖐️")
if response:
    print(f"Detected: {result}")
    print(f"Response: {response}")
else:
    print("No valid sequence detected")

# Get a random banter message for a specific theme
roast_message = banter_engine.get_random_banter(theme="extreme roast with humor")
print(f"Random roast: {roast_message}")
```

## Dependencies
- logging
- random
- typing (Tuple, Optional, Dict, List)
- modules.banter_engine.sequence_responses (SEQUENCE_MAP) 