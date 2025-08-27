"""
JSON-safe wrapper for emoji processing modules.

This wrapper ensures that when emoji data is serialized to JSON (for APIs, logging, etc.),
it doesn't cause Unicode surrogate pair errors.

Per WSP 84: Utility module for preventing API errors with emoji characters.
"""

import json
import sys
import os

# Add utils to path for json_sanitizer import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from utils.json_sanitizer import safe_json_dumps, sanitize_json_object


def make_json_safe_response(response_data):
    """
    Make any response data JSON-safe by sanitizing Unicode issues.
    
    This is specifically designed for the emoji sequence modules that can
    generate problematic Unicode characters.
    
    Args:
        response_data: Any data structure that might contain emojis
        
    Returns:
        Sanitized version of the data
    """
    return sanitize_json_object(response_data)


def get_safe_consciousness_report(engine):
    """
    Get a JSON-safe consciousness report from AgenticSentiment0102.
    
    Args:
        engine: AgenticSentiment0102 instance
        
    Returns:
        JSON-safe report dictionary
    """
    report = engine.get_consciousness_report()
    return make_json_safe_response(report)


def safe_process_interaction(engine, user_id, message):
    """
    Process an interaction and return JSON-safe response.
    
    Args:
        engine: AgenticSentiment0102 instance
        user_id: User identifier
        message: User message
        
    Returns:
        JSON-safe response string
    """
    response = engine.process_interaction(user_id, message)
    return make_json_safe_response(response)


def safe_json_log(data, logger=None):
    """
    Safely log data that might contain problematic Unicode.
    
    Args:
        data: Data to log
        logger: Logger instance (optional)
    """
    safe_data = make_json_safe_response(data)
    json_str = safe_json_dumps(safe_data)
    
    if logger:
        logger.info(f"JSON Data: {json_str}")
    else:
        print(f"JSON Data: {json_str}")
    
    return json_str


# Example usage with the emoji modules
if __name__ == "__main__":
    # Direct imports for testing
    import agentic_sentiment_0102
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    # Create engine
    engine = agentic_sentiment_0102.AgenticSentiment0102()
    
    # Process interactions safely
    print("\n=== JSON-Safe Emoji Processing ===\n")
    
    # Test with problematic emoji sequences
    test_messages = [
        "✊✋🖐️",  # Awakening sequence
        "🖐️🖐️🖐️",  # Full entanglement
        "Test \ud800 invalid",  # Invalid surrogate
    ]
    
    for msg in test_messages:
        print(f"Input: {msg}")
        
        # Process safely
        response = safe_process_interaction(engine, "test_user", msg)
        print(f"Safe Response: {response}")
        
        # Get safe report
        report = get_safe_consciousness_report(engine)
        
        # Log safely
        json_str = safe_json_log(report)
        print(f"Safe JSON: {json_str[:100]}...")
        print()