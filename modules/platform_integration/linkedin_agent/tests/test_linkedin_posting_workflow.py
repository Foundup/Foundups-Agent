#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LinkedIn Posting Workflow - Verify Complete Integration

This test verifies:
1. Correct company page URLs (numeric IDs)
2. Browser opens to posting interface
3. User can manually verify and post

All 3 companies should work:
- Move2Japan (104834798)
- UnDaoDu (68706058)
- FoundUps (1263645)
"""

import sys
import asyncio
import os
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
os.chdir(str(repo_root))

from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import (
    post_stream_notification,
    LinkedInCompanyPage
)

async def test_linkedin_posting_workflow():
    """Test the complete LinkedIn posting workflow for all companies"""

    print("=" * 80)
    print("LINKEDIN POSTING WORKFLOW TEST")
    print("=" * 80)
    print()
    print("This test will:")
    print("1. Open LinkedIn posting interface for each company")
    print("2. Use the unified interface (production code)")
    print("3. Verify correct URLs are being used")
    print("4. Keep browser open for manual posting verification")
    print()
    print("Expected URLs:")
    print("  Move2Japan: https://www.linkedin.com/company/104834798/admin/page-posts/published/?share=true")
    print("  UnDaoDu:    https://www.linkedin.com/company/68706058/admin/page-posts/published/?share=true")
    print("  FoundUps:   https://www.linkedin.com/company/1263645/admin/page-posts/published/?share=true")
    print()
    print("=" * 80)
    print()

    # Test data - simulating a detected stream
    test_streams = [
        {
            "company": LinkedInCompanyPage.MOVE2JAPAN,
            "title": "TEST - Move2Japan Stream",
            "url": "https://www.youtube.com/watch?v=TEST_M2J_123",
            "video_id": "TEST_M2J_123"
        },
        {
            "company": LinkedInCompanyPage.UNDAODU,
            "title": "TEST - UnDaoDu Stream",
            "url": "https://www.youtube.com/watch?v=TEST_UDD_456",
            "video_id": "TEST_UDD_456"
        },
        {
            "company": LinkedInCompanyPage.FOUNDUPS,
            "title": "TEST - FoundUps Stream",
            "url": "https://www.youtube.com/watch?v=TEST_FUP_789",
            "video_id": "TEST_FUP_789"
        }
    ]

    for i, stream in enumerate(test_streams, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/3: {stream['company'].name}")
        print(f"{'=' * 80}")
        print(f"Company ID: {stream['company'].value}")
        print(f"Stream Title: {stream['title']}")
        print(f"Stream URL: {stream['url']}")
        print()

        try:
            print(f"[INFO] Calling unified LinkedIn interface...")
            result = await post_stream_notification(
                stream_title=stream['title'],
                stream_url=stream['url'],
                video_id=stream['video_id'],
                company_page=stream['company']
            )

            print()
            print(f"[RESULT] Success: {result.success}")
            print(f"[RESULT] Message: {result.message}")
            print(f"[RESULT] Company: {result.company_page.name} ({result.company_page.value})")
            print(f"[RESULT] Duplicate Prevented: {result.duplicate_prevented}")
            print()

            if result.success:
                print(f"[PASS] LinkedIn interface opened successfully for {stream['company'].name}")
                print(f"[ACTION] Browser should be open - please verify URL and post manually")
            else:
                if result.duplicate_prevented:
                    print(f"[SKIP] Stream already posted (duplicate prevention)")
                else:
                    print(f"[FAIL] Failed to open LinkedIn interface: {result.message}")

            print()
            input("Press ENTER when you've verified the browser window and closed it...")

        except Exception as e:
            print(f"[ERROR] Exception during test: {e}")
            import traceback
            traceback.print_exc()

        print()

    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print("If all 3 companies opened to the correct posting interface,")
    print("then the LinkedIn integration is working correctly!")
    print()
    print("Next steps:")
    print("1. Restart the DAE to load the new code")
    print("2. Wait for a real stream to be detected")
    print("3. Verify automatic posting works")
    print()

if __name__ == "__main__":
    asyncio.run(test_linkedin_posting_workflow())
