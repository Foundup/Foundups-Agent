#!/usr/bin/env python3
"""
Test Direct Selenium LinkedIn Posting
Bypasses MCP layer to test Selenium directly

Run: python test_direct_selenium_linkedin.py
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

def test_direct_selenium():
    """Test LinkedIn posting directly via Selenium (no MCP)"""

    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    print("="*80)
    print("TESTING DIRECT SELENIUM LINKEDIN POSTING (NO MCP)")
    print("="*80)
    print()

    # Import the actual Selenium poster
    try:
        from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
    except ImportError as e:
        print(f"Error importing AntiDetectionLinkedIn: {e}")
        print("This module may need to be available")
        return

    # Simple test content
    test_content = """Testing Direct Selenium Integration

This is a test post to verify:
- Direct Selenium browser automation
- LinkedIn company page posting
- Anti-detection timing

#Testing #Automation"""

    print("LinkedIn Content:")
    print(test_content)
    print()
    print("Target: FoundUps Company Page (ID: 1263645)")
    print()
    print("-"*80)
    print()
    print("Starting direct Selenium post...")
    print()

    try:
        # Create poster instance (default company_id is already 1263645 - FoundUps)
        poster = AntiDetectionLinkedIn()

        print(f"Configured for company ID: {poster.company_id}")
        print(f"Admin URL: {poster.company_admin_url}")
        print()

        # Post to LinkedIn
        success = poster.post_to_company_page(content=test_content)

        print()
        print("="*80)
        print("RESULT")
        print("="*80)
        print(f"Success: {success}")
        print()

        if success:
            print("LinkedIn posting successful!")
            print()
            print("Verify at: https://www.linkedin.com/company/1263645/admin/page-posts/published/")
        else:
            print("Posting failed - check logs above")

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
    test_direct_selenium()
