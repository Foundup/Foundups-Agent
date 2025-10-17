#!/usr/bin/env python3
"""
LinkedIn Visual URL Test - Standalone version that calls main.py
Opens browser windows to verify correct company pages

WSP Compliance: WSP 49 (Module Structure)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import asyncio
import sys
import os
from pathlib import Path

# Add repo root to path and change to it
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
os.chdir(str(repo_root))  # Change to repo root for imports to work

# Import the unified interface (must be at module level)
from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import (
    LinkedInPostRequest,
    LinkedInContentType,
    LinkedInCompanyPage,
    unified_linkedin
)

async def test_visual_company_urls():
    """Test each company page URL by actually posting (you can cancel)"""

    print("\n" + "="*70)
    print("LINKEDIN VISUAL URL VERIFICATION TEST")
    print("="*70)
    print("\nThis will trigger LinkedIn posting for each company.")
    print("Check the URL in the browser - then CANCEL the post.\n")

    # Test cases
    test_companies = [
        (LinkedInCompanyPage.MOVE2JAPAN, "Move2Japan/GeoZai", "https://www.linkedin.com/company/geozai/admin/..."),
        (LinkedInCompanyPage.UNDAODU, "UnDaoDu", "https://www.linkedin.com/company/undaodu/admin/..."),
        (LinkedInCompanyPage.FOUNDUPS, "FoundUps", "https://www.linkedin.com/company/foundups/admin/..."),
    ]

    for company_page, name, expected_url in test_companies:
        print("="*70)
        print(f"Testing: {name}")
        print("="*70)
        print(f"Expected URL pattern: {expected_url}")
        print("\n>>> OPENING BROWSER <<<")
        print("CHECK THE URL BAR - Does it match the expected company?")
        print("Then CANCEL the post window...\n")

        # Create post request
        request = LinkedInPostRequest(
            content=f"[TEST - DO NOT POST] Verifying {name} company page URL",
            content_type=LinkedInContentType.GENERAL_POST,
            company_page=company_page,
            duplicate_check_key=None  # Allow duplicate for testing
        )

        # This will open the browser
        result = await unified_linkedin.post_to_linkedin(request)

        print(f"Result: {result.message}")
        print()

        # Pause before next company
        await asyncio.sleep(2)

    print("="*70)
    print("VISUAL TEST COMPLETE")
    print("="*70)
    print("\nDid you see the correct URLs?")
    print("  [1] Move2Japan/GeoZai -> .../company/geozai/...")
    print("  [2] UnDaoDu          -> .../company/undaodu/...")
    print("  [3] FoundUps         -> .../company/foundups/...")
    print("\nIf all URLs were correct, the fix is working!\n")

if __name__ == "__main__":
    asyncio.run(test_visual_company_urls())
