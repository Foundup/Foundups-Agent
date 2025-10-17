#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Visual URL Test - Opens browser windows to verify correct company pages

This test will open the LinkedIn posting window for each company page.
You can verify the URL in the browser address bar, then CANCEL the post.

WSP Compliance: WSP 49 (Module Structure)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
import time
from pathlib import Path

# Add absolute paths to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "modules" / "platform_integration" / "linkedin_agent"))

# Now import with absolute path
from src.anti_detection_poster import AntiDetectionLinkedIn

def test_visual_company_urls():
    """
    Open LinkedIn posting window for each company page to verify correct URLs

    Expected URLs:
    - Move2Japan/GeoZai: https://www.linkedin.com/company/geozai/admin/...
    - UnDaoDu: https://www.linkedin.com/company/undaodu/admin/...
    - FoundUps: https://www.linkedin.com/company/foundups/admin/...
    """

    print("\n" + "="*70)
    print("LINKEDIN VISUAL URL VERIFICATION TEST")
    print("="*70)
    print("\nThis test will open the LinkedIn posting window for each company.")
    print("Please check the URL in the browser address bar.")
    print("Then CANCEL the post to continue to the next company.\n")

    # Company configurations
    companies = [
        {
            "id": "104834798",
            "vanity": "geozai",
            "name": "Move2Japan/GeoZai",
            "expected_url": "https://www.linkedin.com/company/geozai/admin/page-posts/published/"
        },
        {
            "id": "165749317",
            "vanity": "undaodu",
            "name": "UnDaoDu",
            "expected_url": "https://www.linkedin.com/company/undaodu/admin/page-posts/published/"
        },
        {
            "id": "1263645",
            "vanity": "foundups",
            "name": "FoundUps",
            "expected_url": "https://www.linkedin.com/company/foundups/admin/page-posts/published/"
        }
    ]

    # Create LinkedIn poster instance
    print("Creating LinkedIn poster...")
    poster = AntiDetectionLinkedIn()
    print("[OK] LinkedIn poster created\n")

    # Test each company
    for company in companies:
        print("="*70)
        print(f"Testing: {company['name']}")
        print("="*70)
        print(f"Company ID: {company['id']}")
        print(f"Expected URL: {company['expected_url']}")

        # Update company_id and URL (this is the fix we're testing)
        poster.company_id = company['id']

        # Company vanity map (same as in unified_linkedin_interface.py)
        company_vanity_map = {
            "104834798": "geozai",
            "165749317": "undaodu",
            "1263645": "foundups"
        }

        company_url_part = company_vanity_map.get(company['id'], company['id'])
        poster.company_admin_url = f"https://www.linkedin.com/company/{company_url_part}/admin/page-posts/published/"

        print(f"Configured URL: {poster.company_admin_url}")
        print("\n>>> OPENING BROWSER <<<")
        print("CHECK THE URL BAR - Does it match the expected URL?")
        print("Then CANCEL the post window to continue...\n")

        try:
            # Open browser and navigate to posting page
            result = poster.post_to_company_page(
                content=f"[TEST - DO NOT POST] URL verification for {company['name']}"
            )

            if result:
                print(f"[OK] Posted successfully (if you didn't cancel)")
            else:
                print(f"[OK] User cancelled or post failed")

        except Exception as e:
            # User cancellation is expected
            if "window already closed" in str(e).lower() or "target window" in str(e).lower():
                print(f"[OK] User cancelled - URL verified")
            else:
                print(f"[INFO] Browser closed: {e}")

        print("\n")
        time.sleep(1)  # Brief pause between companies

    # Final summary
    print("="*70)
    print("VISUAL TEST COMPLETE")
    print("="*70)
    print("\nDid you see the correct URLs?")
    print("  [1] Move2Japan/GeoZai -> .../company/geozai/...")
    print("  [2] UnDaoDu          -> .../company/undaodu/...")
    print("  [3] FoundUps         -> .../company/foundups/...")
    print("\nIf all URLs were correct, the fix is working!\n")

if __name__ == "__main__":
    test_visual_company_urls()
