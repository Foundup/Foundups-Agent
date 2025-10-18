#!/usr/bin/env python3
"""
Test LinkedIn Posting Only - Step 1
Tests: MCP Server → Selenium → Gemini Vision → Training Data

Run: python test_linkedin_only.py
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import asyncio
import json
import os
from datetime import datetime

async def test_linkedin_only():
    """Test LinkedIn posting with MCP and Gemini Vision"""

    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    print("="*80)
    print("TESTING LINKEDIN POSTING ONLY (NO X)")
    print("="*80)
    print()

    # Import unified interface
    from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import (
        post_general_content,
        LinkedInCompanyPage
    )

    # Simple test content
    test_content = """Testing MCP Integration - LinkedIn Only

This is a test post to verify:
- Social Media DAE orchestration
- MCP Server communication
- Selenium browser automation
- Gemini Vision UI analysis
- Training data collection

#Testing #Automation"""

    print("LinkedIn Content:")
    print(test_content)
    print()
    print("Target: FoundUps Company Page (ID: 1263645)")
    print()
    print("-"*80)
    print()
    print("Starting LinkedIn post (NO X auto-trigger)...")
    print("Expected timing: 3-8 seconds (anti-detection delays)")
    print()

    try:
        result = await post_general_content(
            content=test_content,
            company_page=LinkedInCompanyPage.FOUNDUPS,
            duplicate_key=f"test_linkedin_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        print()
        print("="*80)
        print("RESULT")
        print("="*80)
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Timestamp: {result.timestamp}")
        print(f"Content Type: {result.content_type.value}")
        print(f"Company Page: {result.company_page.value}")
        print()

        if result.success:
            print("✅ LinkedIn posting successful!")
            print()
            print("Next step: Check training patterns in holo_index/training/selenium_patterns.json")
        else:
            print("⚠️  Posting failed - check message above")

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
    asyncio.run(test_linkedin_only())
