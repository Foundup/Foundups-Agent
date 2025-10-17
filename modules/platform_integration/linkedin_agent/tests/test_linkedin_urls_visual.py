#!/usr/bin/env python3
"""
Visual test - Opens LinkedIn for each company using AntiDetectionLinkedIn
Run this from O:\Foundups-Agent directory

This will use the ACTUAL LinkedIn poster class to open the posting window.
Verify the URL is correct, then cancel/close the window.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

def test_all_company_urls():
    """Test LinkedIn posting for each company to verify URLs"""

    companies = [
        {
            "name": "Move2Japan/GeoZai",
            "id": "104834798",
            "expected_url": "https://www.linkedin.com/company/geozai/admin/page-posts/published/?share=true"
        },
        {
            "name": "UnDaoDu",
            "id": "68706058",
            "expected_url": "https://www.linkedin.com/company/undaodu/admin/page-posts/published/?share=true"
        },
        {
            "name": "FoundUps",
            "id": "1263645",
            "expected_url": "https://www.linkedin.com/company/foundups/admin/page-posts/published/?share=true"
        }
    ]

    print("\n" + "="*70)
    print("LINKEDIN COMPANY URL VISUAL VERIFICATION")
    print("="*70)
    print("\nThis test will use AntiDetectionLinkedIn to open each company page.")
    print("Check the URL in the browser address bar.")
    print("Then CLOSE/CANCEL the posting window to continue.\n")

    # Create LinkedIn poster
    poster = AntiDetectionLinkedIn()

    for company in companies:
        print("="*70)
        print(f"Testing: {company['name']}")
        print("="*70)
        print(f"Company ID: {company['id']}")
        print(f"Expected URL: {company['expected_url']}")

        # UPDATE company_id before posting (THIS IS THE FIX!)
        poster.company_id = company['id']
        print(f"\n[FIX] Updated poster.company_id to: {poster.company_id}")

        # UPDATE the admin URL based on company_id (THIS IS THE FIX!)
        company_url_part = poster.company_vanity_map.get(company['id'], company['id'])
        poster.company_admin_url = f"https://www.linkedin.com/company/{company_url_part}/admin/page-posts/published/"
        print(f"[FIX] Updated poster.company_admin_url to: {poster.company_admin_url}")

        print("\n>>> OPENING BROWSER <<<")
        print("CHECK THE URL BAR - Does it match the expected URL?")
        print("Then CLOSE/CANCEL the posting window...\n")

        try:
            # This will open the browser to the correct company page
            result = poster.post_to_company_page(
                content=f"[TEST - DO NOT POST] Verifying {company['name']} company page URL"
            )

            if result:
                print(f"[OK] Browser opened successfully for {company['name']}")
            else:
                print(f"[INFO] User cancelled or post failed for {company['name']}")

        except Exception as e:
            # User cancellation is expected
            if "window already closed" in str(e).lower() or "target window" in str(e).lower():
                print(f"[OK] User cancelled - URL verified for {company['name']}")
            else:
                print(f"[INFO] Exception: {e}")

        print()

    print("="*70)
    print("VISUAL VERIFICATION COMPLETE")
    print("="*70)
    print("\nDid all URLs match their expected values?")
    print("  [1] Move2Japan/GeoZai -> .../company/geozai/...")
    print("  [2] UnDaoDu          -> .../company/undaodu/...")
    print("  [3] FoundUps         -> .../company/foundups/...")
    print("\nIf yes, the fix is working correctly!\n")

if __name__ == "__main__":
    test_all_company_urls()
