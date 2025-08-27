"""
JSON Sanitizer for API Requests

Fixes Unicode surrogate pair issues that cause API errors like:
"no low surrogate in string"

Per WSP 84: Utility for cleaning JSON before API submission
"""

import json
import re
from typing import Any, Dict, Union


def sanitize_json_string(text: str) -> str:
    """
    Remove or fix invalid Unicode surrogate characters.
    
    Surrogates are in ranges:
    - High surrogates: U+D800 to U+DBFF
    - Low surrogates: U+DC00 to U+DFFF
    
    These must appear in pairs (high followed by low) or be removed.
    """
    if not isinstance(text, str):
        return text
    
    # Pattern to match unpaired surrogates
    # High surrogate not followed by low surrogate
    high_surrogate_unpaired = re.compile(r'[\ud800-\udbff](?![\udc00-\udfff])')
    # Low surrogate not preceded by high surrogate
    low_surrogate_unpaired = re.compile(r'(?<![\ud800-\udbff])[\udc00-\udfff]')
    
    # Remove unpaired surrogates
    text = high_surrogate_unpaired.sub('', text)
    text = low_surrogate_unpaired.sub('', text)
    
    # Also remove any other control characters that might cause issues
    # Keep standard printable characters and common whitespace
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text


def sanitize_json_object(obj: Any) -> Any:
    """
    Recursively sanitize all strings in a JSON-serializable object.
    """
    if isinstance(obj, str):
        return sanitize_json_string(obj)
    elif isinstance(obj, dict):
        return {k: sanitize_json_object(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_object(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_json_object(item) for item in obj)
    else:
        return obj


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize object to JSON, removing invalid Unicode.
    
    Usage:
        import utils.json_sanitizer as jsan
        json_str = jsan.safe_json_dumps(data)
    """
    # First sanitize the object
    clean_obj = sanitize_json_object(obj)
    
    # Then serialize with ensure_ascii=False to handle Unicode properly
    # but also catch any remaining issues
    try:
        return json.dumps(clean_obj, ensure_ascii=False, **kwargs)
    except UnicodeDecodeError:
        # Fallback to ASCII-only encoding
        return json.dumps(clean_obj, ensure_ascii=True, **kwargs)


def validate_json_string(json_str: str) -> tuple[bool, str]:
    """
    Validate if a JSON string will cause API errors.
    
    Returns:
        (is_valid, error_message)
    """
    try:
        # Check for unpaired surrogates
        high_surrogate_unpaired = re.compile(r'[\ud800-\udbff](?![\udc00-\udfff])')
        low_surrogate_unpaired = re.compile(r'(?<![\ud800-\udbff])[\udc00-\udfff]')
        
        if high_surrogate_unpaired.search(json_str):
            return False, "Contains unpaired high surrogate"
        if low_surrogate_unpaired.search(json_str):
            return False, "Contains unpaired low surrogate"
        
        # Try to parse it
        json.loads(json_str)
        return True, "Valid JSON"
        
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


# Test the sanitizer
if __name__ == "__main__":
    # Test cases with invalid surrogates
    test_cases = [
        {"text": "Normal text"},
        {"text": "Text with high surrogate \ud800 unpaired"},
        {"text": "Text with low surrogate \udc00 unpaired"},
        {"text": "Valid surrogate pair \ud800\udc00"},
        {"nested": {"text": "Nested \ud800 issue"}},
        ["List with \udc00 issue"],
    ]
    
    print("Testing JSON sanitizer...")
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: {test}")
        sanitized = sanitize_json_object(test)
        print(f"Sanitized: {sanitized}")
        
        try:
            json_str = safe_json_dumps(test)
            is_valid, msg = validate_json_string(json_str)
            print(f"Result: {msg}")
        except Exception as e:
            print(f"Error: {e}")