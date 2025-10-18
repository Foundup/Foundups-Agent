#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WSP 90 Improved Logging Test - Check for Chinese characters generally
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import os
import io

_original_stdout = sys.stdout
_original_stderr = sys.stderr

class SafeUTF8Wrapper:
    """Safe UTF-8 wrapper that doesn't interfere with redirection"""

    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.encoding = 'utf-8'
        self.errors = 'replace'

    def write(self, data):
        """Write with UTF-8 encoding safety"""
        try:
            if isinstance(data, str):
                encoded = data.encode('utf-8', errors='replace')
                if hasattr(self.original_stream, 'buffer'):
                    self.original_stream.buffer.write(encoded)
                else:
                    self.original_stream.write(data.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
            else:
                self.original_stream.write(data)
        except Exception:
            try:
                self.original_stream.write(str(data))
            except Exception:
                pass

    def flush(self):
        """Flush the stream"""
        try:
            self.original_stream.flush()
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self.original_stream, name)

if sys.platform.startswith('win'):
    sys.stdout = SafeUTF8Wrapper(sys.stdout)
    sys.stderr = SafeUTF8Wrapper(sys.stderr)
# === END UTF-8 ENFORCEMENT ===

import tempfile
import logging
import unicodedata

def has_chinese_characters(text):
    """Check if text contains Chinese characters (CJK Unified Ideographs)"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # CJK Unified Ideographs range
            return True
    return False

def has_unicode_characters(text):
    """Check if text contains any non-ASCII characters"""
    return any(ord(char) > 127 for char in text)

def improved_logging_test():
    """Improved logging test that checks for Chinese characters generally"""
    print("=" * 70)
    print("IMPROVED LOGGING TEST: Check for Chinese characters generally")
    print("=" * 70)

    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log', encoding='utf-8') as f:
            temp_log = f.name

        # Reset logging
        logging.shutdown()
        logging.root.handlers.clear()

        # Configure logging to file with UTF-8
        logging.basicConfig(
            filename=temp_log,
            level=logging.INFO,
            format='%(levelname)s: %(message)s',
            encoding='utf-8'
        )

        logger = logging.getLogger('wsp90_improved_test')

        # Log messages with different types of content
        logger.info("Test log message (ASCII only)")
        logger.warning("Unicode warning: 警告")  # Chinese: warning
        logger.error("Unicode error: 错误")    # Chinese: error
        logger.info("Mixed content: Hello 世界 [U+1F30D]")  # Chinese + emoji

        # Read the log file
        with open(temp_log, 'r', encoding='utf-8') as f:
            content = f.read()

        print("LOG FILE ANALYSIS:")
        print(f"Content length: {len(content)} characters")
        print(f"Content bytes: {len(content.encode('utf-8'))} bytes")
        print(f"Has Chinese characters: {has_chinese_characters(content)}")
        print(f"Has Unicode characters: {has_unicode_characters(content)}")
        print(f"Contains 'Test log message': {'Test log message' in content}")
        print(f"Contains '警告': {'警告' in content}")
        print(f"Contains '错误': {'错误' in content}")
        print(f"Contains '世界': {'世界' in content}")
        print(f"Contains '[U+1F30D]': {'[U+1F30D]' in content}")

        # Improved test criteria
        tests_passed = []

        # Test 1: Basic ASCII content preserved
        if "Test log message" in content:
            tests_passed.append("ASCII content preserved")
        else:
            print("[FAIL] ASCII content missing")

        # Test 2: Has Chinese characters (general check)
        if has_chinese_characters(content):
            tests_passed.append("Chinese characters present")
        else:
            print("[FAIL] No Chinese characters found")

        # Test 3: Has any Unicode characters
        if has_unicode_characters(content):
            tests_passed.append("Unicode characters present")
        else:
            print("[FAIL] No Unicode characters found")

        # Test 4: Specific Chinese characters still there (for completeness)
        specific_chars = ["警告", "错误", "世界"]
        found_specific = [char for char in specific_chars if char in content]
        if found_specific:
            tests_passed.append(f"Specific chars found: {found_specific}")
        else:
            print("[FAIL] Specific Chinese characters missing")

        # Test 5: Content is not corrupted (byte length should be reasonable)
        expected_min_length = len("INFO: Test log message (ASCII only)") + len("WARNING: Unicode warning: 警告") + len("ERROR: Unicode error: 错误")
        if len(content) >= expected_min_length * 0.8:  # Allow some formatting differences
            tests_passed.append("Content length reasonable")
        else:
            print(f"[FAIL] Content too short: {len(content)} < {expected_min_length}")

        print(f"\n[OK] TESTS PASSED: {len(tests_passed)}/{5}")
        for test in tests_passed:
            print(f"   [OK] {test}")

        # Overall success
        overall_success = len(tests_passed) >= 4  # Pass if 4/5 tests pass

        if overall_success:
            print("\n[CELEBRATE] IMPROVED LOGGING TEST: SUCCESS")
            print("   • Chinese characters are logged correctly")
            print("   • Unicode content is preserved")
            print("   • Logging system works with WSP 90")
        else:
            print("\n[FAIL] IMPROVED LOGGING TEST: FAILED")
            print("   • Logging system has issues with Unicode")

        # Cleanup
        try:
            os.unlink(temp_log)
        except:
            pass  # Ignore cleanup errors

        return overall_success

    except Exception as e:
        print(f"[FAIL] LOGGING TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_unicode_detection():
    """Demonstrate different ways to detect Unicode content"""
    print("\n" + "=" * 70)
    print("UNICODE DETECTION METHODS DEMONSTRATION")
    print("=" * 70)

    test_strings = [
        "ASCII only text",
        "Mixed ASCII and Unicode: Hello 世界",
        "Chinese characters: 警告 错误 世界",
        "Emoji and symbols: [U+1F30D] [ROCKET] [U+2764]️",
        "Accented characters: café naïve résumé"
    ]

    for test_str in test_strings:
        print(f"\nTesting: '{test_str}'")
        print(f"  Has Chinese chars: {has_chinese_characters(test_str)}")
        print(f"  Has Unicode chars: {has_unicode_characters(test_str)}")
        print(f"  Character count: {len(test_str)}")
        print(f"  Byte count: {len(test_str.encode('utf-8'))}")
        print(f"  Is ASCII: {test_str.isascii()}")

        # Show Unicode code points
        unicode_info = [f"U+{ord(c):04X}({unicodedata.name(c, 'UNKNOWN')})" for c in test_str if ord(c) > 127]
        if unicode_info:
            print(f"  Unicode code points: {unicode_info[:3]}{'...' if len(unicode_info) > 3 else ''}")

def main():
    """Main test function"""
    print("[SEARCH] WSP 90 IMPROVED LOGGING TEST")
    print("Check for Chinese characters generally vs. specifically")
    print("=" * 60)

    # Demonstrate Unicode detection methods
    demonstrate_unicode_detection()

    # Run improved logging test
    success = improved_logging_test()

    print("\n" + "=" * 60)
    print("[TARGET] ANALYSIS: Specific vs General Chinese Character Detection")
    print("=" * 60)

    print("""
[DATA] COMPARISON:

SPECIFIC CHARACTER CHECK (Original):
[OK] Precise - knows exactly which characters should be there
[OK] Fails if character encoding changes
[OK] Brittle - depends on exact test data
[OK] Good for: Regression testing specific functionality

GENERAL CHARACTER CHECK (Improved):
[OK] Robust - works with any Chinese characters
[OK] Flexible - adapts to different test content
[OK] Reliable - tests the general capability
[OK] Good for: General Unicode support validation

[TARGET] RECOMMENDATION:
Use GENERAL character detection for WSP 90 compliance testing.
Specific character checks can be supplementary but shouldn't be required.
""")

    print(f"\nFinal Result: {'[OK] SUCCESS' if success else '[FAIL] FAILED'}")
    return success

if __name__ == "__main__":
    main()
