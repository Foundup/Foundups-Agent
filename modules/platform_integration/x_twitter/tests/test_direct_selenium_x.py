#!/usr/bin/env python3
"""
Test Direct Selenium X/Twitter Posting
Tests X posting with anti-detection timing

Run: python test_direct_selenium_x.py
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


from datetime import datetime

def test_direct_x():
    """Test X/Twitter posting directly via Selenium"""

    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    print("="*80)
    print("TESTING DIRECT SELENIUM X/TWITTER POSTING")
    print("="*80)
    print()

    # Import the X poster
    try:
        from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX
    except ImportError as e:
        print(f"Error importing AntiDetectionX: {e}")
        return

    # Test content (must be ≤280 chars for X)
    test_content = """Testing X Integration

Direct Selenium automation
Anti-detection timing
Manual Post control

#Testing #Automation"""

    print("X Content:")
    print(test_content)
    print()
    print(f"Length: {len(test_content)} chars (limit: 280)")
    print("Target: @foundups account")
    print()
    print("-"*80)
    print()
    print("Starting direct Selenium post to X...")
    print()

    try:
        # Create poster instance
        poster = AntiDetectionX()

        # Post to X
        success = poster.post_to_x(content=test_content)

        print()
        print("="*80)
        print("RESULT")
        print("="*80)
        print(f"Success: {success}")
        print()

        if success:
            print("X posting successful!")
        else:
            print("Posting failed or cancelled - check logs above")

    except Exception as e:
        print()
        print("="*80)
        print("ERROR")
        print("="*80)
        print(f"Exception: {e}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_x()
