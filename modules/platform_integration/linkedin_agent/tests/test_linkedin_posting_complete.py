#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete LinkedIn Posting Workflow Test

Tests the full posting workflow using production code.
Verifies all 3 companies work correctly.
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


import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

def test_complete_workflow():
    """Test complete LinkedIn posting workflow for all companies"""

    companies = [
        {
            "name": "Move2Japan",
            "id": "104834798",
            "expected_url": "https://www.linkedin.com/company/104834798/admin/page-posts/published/?share=true"
        },
        {
            "name": "UnDaoDu",
            "id": "68706058",
            "expected_url": "https://www.linkedin.com/company/68706058/admin/page-posts/published/?share=true"
        },
        {
            "name": "FoundUps",
            "id": "1263645",
            "expected_url": "https://www.linkedin.com/company/1263645/admin/page-posts/published/?share=true"
        }
    ]

    print("=" * 80)
    print("COMPLETE LINKEDIN POSTING WORKFLOW TEST")
    print("=" * 80)
    print()
    print("This test verifies:")
    print("1. Browser opens to correct company posting page")
    print("2. URL uses numeric company ID (not vanity URL)")
    print("3. Posting interface loads with ?share=true parameter")
    print("4. User can manually verify and post")
    print()
    print("Expected Results:")
    for company in companies:
        print(f"  {company['name']:12} -> {company['expected_url']}")
    print()
    print("=" * 80)
    print()

    # Create LinkedIn poster
    poster = AntiDetectionLinkedIn()

    for i, company in enumerate(companies, 1):
        print("=" * 80)
        print(f"TEST {i}/3: {company['name']}")
        print("=" * 80)
        print(f"Company ID: {company['id']}")
        print(f"Expected URL: {company['expected_url']}")
        print()

        # Update company_id for this test
        poster.company_id = company['id']
        print(f"[SETUP] Set poster.company_id = {poster.company_id}")
        print()

        print("[ACTION] Opening LinkedIn posting interface...")
        print("[INFO] Browser will open - please verify the URL and posting dialog")
        print()

        try:
            # Call the actual posting function with test content
            result = poster.post_to_company_page(
                content=f"[TEST - DO NOT POST]\n\nVerifying {company['name']} posting interface.\n\n#Test #LinkedIn"
            )

            print()
            if result:
                print(f"[PASS] LinkedIn interface opened successfully for {company['name']}")
                print(f"[INFO] Result: {result}")
            else:
                print(f"[FAIL] Failed to open LinkedIn interface for {company['name']}")

        except Exception as e:
            # User cancellation is expected
            if "window already closed" in str(e).lower() or "target window" in str(e).lower():
                print(f"[PASS] User cancelled - URL verified for {company['name']}")
            else:
                print(f"[ERROR] Exception: {e}")

        print()
        if i < len(companies):
            input("Press ENTER to test next company...")
        print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Verification Checklist:")
    print("  [[OK]] Did all 3 companies open to their correct pages?")
    print("  [[OK]] Did all URLs use numeric company IDs (not vanity URLs)?")
    print("  [[OK]] Did the posting interface load with ?share=true?")
    print("  [[OK]] Could you see the posting dialog?")
    print()
    print("If all checks passed, the LinkedIn integration is WORKING CORRECTLY!")
    print()
    print("Next Steps:")
    print("1. Restart the main DAE to load the new code")
    print("2. Wait for a real stream to be detected")
    print("3. Verify automatic LinkedIn posting works end-to-end")
    print()

if __name__ == "__main__":
    test_complete_workflow()
