"""
Test script to verify JSON sanitizer fixes Unicode surrogate issues.
"""

import json
from utils.json_sanitizer import safe_json_dumps, sanitize_json_object, validate_json_string

# Test cases with problematic Unicode
test_cases = [
    # Normal emoji sequences (should work fine)
    {"type": "awakening", "emoji": "✊✋🖐️", "message": "Time to wake up"},
    
    # Emoji with variation selectors
    {"type": "entangled", "emoji": "🖐️🖐️🖐️", "message": "Full entanglement"},
    
    # Invalid surrogates (these cause the API error)
    {"type": "broken", "text": "Test \ud800 unpaired high surrogate"},
    {"type": "broken2", "text": "Test \udc00 unpaired low surrogate"},
    
    # Mixed content
    {"nested": {"emojis": ["✊", "✋", "🖐️"], "broken": "test\ud800test"}},
    
    # Large text with emoji at position 173191 (simulating your error)
    {"large": "x" * 173180 + "🖐️" + "\ud800" + "more text"},
]

print("Testing JSON Sanitizer for API Safety\n")
print("=" * 50)

for i, test_data in enumerate(test_cases, 1):
    print(f"\nTest {i}: {str(test_data)[:80]}...")
    
    # Try regular json.dumps (might fail)
    try:
        regular_json = json.dumps(test_data)
        is_valid, msg = validate_json_string(regular_json)
        print(f"  Regular JSON: {msg}")
    except Exception as e:
        print(f"  Regular JSON: Failed - {e}")
    
    # Try safe_json_dumps (should always work)
    try:
        safe_json = safe_json_dumps(test_data)
        is_valid, msg = validate_json_string(safe_json)
        print(f"  Safe JSON: {msg}")
        
        # Verify it can be parsed back
        parsed = json.loads(safe_json)
        print(f"  Parsed successfully: {type(parsed)}")
        
    except Exception as e:
        print(f"  Safe JSON: Failed - {e}")

print("\n" + "=" * 50)
print("\nSUMMARY: The sanitizer removes unpaired surrogates that cause API errors.")
print("Use 'from utils.json_sanitizer import safe_json_dumps' in any file")
print("that sends JSON to an API to prevent the 'no low surrogate' error.")