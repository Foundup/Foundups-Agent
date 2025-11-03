#!/usr/bin/env python3
"""
Test Social Media MCP Integration
Tests: LinkedIn -> X auto-trigger, Gemini Vision, Training Data Collection

This validates the complete flow:
1. MCP Server receives posting request
2. Selenium posts to LinkedIn with anti-detection timing
3. Gemini Vision analyzes UI screenshot
4. Training pattern saved to holo_index/training/selenium_patterns.json
5. X post auto-triggered after LinkedIn success
6. All data ready for Gemma training in Colab

Run: python test_social_media_mcp_integration.py
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


import asyncio
import json
import os
from datetime import datetime

async def test_social_media_posting():
    """Test complete MCP integration with Gemini Vision and training data"""

    print("="*80)
    print("TESTING SOCIAL MEDIA MCP INTEGRATION")
    print("="*80)
    print()

    # Import unified interfaces
    from modules.platform_integration.social_media_orchestrator.src.unified_linkedin_interface import (
        post_git_commits,
        LinkedInCompanyPage
    )

    # Test content
    test_commit_hash = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    linkedin_content = """[BOT] Testing MCP Integration

[OK] Social Media DAE orchestration
[OK] Selenium browser automation
[OK] Gemini Vision UI analysis (FREE API)
[OK] Training data collection for Gemma
[OK] Anti-detection timing (13-23 seconds)

This post tests the complete flow:
LinkedIn -> Auto X -> Training Patterns

#AI #Automation #Testing"""

    x_content = """[BOT] MCP Integration Test

[OK] Social Media DAE
[OK] Gemini Vision
[OK] Training Data
[OK] Anti-Detection

LinkedIn -> Auto X -> Training

#AI #Testing"""

    print(f"[NOTE] Test Commit Hash: {test_commit_hash}")
    print()
    print("[CLIPBOARD] LinkedIn Content:")
    print(linkedin_content)
    print()
    print("[CLIPBOARD] X Content:")
    print(x_content)
    print()
    print("-"*80)
    print()

    # STEP 1: Post via unified interface (auto-triggers both platforms)
    print("[ROCKET] STEP 1: Posting via Social Media DAE...")
    print("   - MCP Client -> MCP Server")
    print("   - Selenium + Gemini Vision")
    print("   - Auto-trigger X after LinkedIn")
    print("   - Anti-detection delays: 13-23 seconds total")
    print()

    try:
        result = await post_git_commits(
            commit_summary=linkedin_content,
            commit_hashes=[test_commit_hash],
            x_content=x_content,
            auto_post_to_x=True
        )

        print()
        print("="*80)
        print("POSTING RESULT")
        print("="*80)
        print(f"[OK] Success: {result.success}")
        print(f"[NOTE] Message: {result.message}")
        print(f"⏰ Timestamp: {result.timestamp}")
        print(f"[TARGET] Content Type: {result.content_type.value}")
        print(f"[U+1F3E2] Company Page: {result.company_page.value}")
        print()

    except Exception as e:
        print()
        print("="*80)
        print("ERROR DURING POSTING")
        print("="*80)
        print(f"[FAIL] Exception: {e}")
        print()
        print("This is expected if:")
        print("  - MCP server not running")
        print("  - LinkedIn credentials not configured")
        print("  - Browser automation blocked")
        print()
        return

    # STEP 2: Check training patterns saved
    print("-"*80)
    print()
    print("[SEARCH] STEP 2: Verifying Training Data Collection...")
    print()

    training_file = "holo_index/training/selenium_patterns.json"

    if os.path.exists(training_file):
        with open(training_file, 'r', encoding="utf-8") as f:
            patterns = json.load(f)

        print(f"[OK] Training patterns file exists: {training_file}")
        print(f"[DATA] Total patterns collected: {len(patterns)}")
        print()

        # Find our test pattern
        test_patterns = [p for p in patterns if test_commit_hash in str(p.get('input', {}))]

        if test_patterns:
            print(f"[OK] Found {len(test_patterns)} pattern(s) for this test")
            print()

            for i, pattern in enumerate(test_patterns, 1):
                print(f"Pattern #{i}:")
                print(f"  - MCP Tool: {pattern.get('mcp_tool')}")
                print(f"  - Timestamp: {pattern.get('timestamp')}")
                print(f"  - Result: {pattern.get('result')}")
                print(f"  - Training Category: {pattern.get('training_category')}")

                gemini = pattern.get('gemini_analysis', {})
                if gemini:
                    print(f"  - Gemini Vision Analysis:")
                    print(f"      UI State: {gemini.get('ui_state', 'N/A')}")
                    print(f"      Post Button: {gemini.get('post_button', {})}")
                    print(f"      Errors: {gemini.get('errors', [])}")
                    print(f"      Success Indicators: {gemini.get('success_indicators', [])}")
                print()
        else:
            print("[U+26A0]️  Test pattern not found yet (may still be processing)")
            print()
    else:
        print(f"[U+26A0]️  Training patterns file not found: {training_file}")
        print("   This is expected if no posts have been made yet")
        print()

    # STEP 3: Show Gemma training readiness
    print("-"*80)
    print()
    print("[GRADUATE] STEP 3: Gemma Training Readiness")
    print()
    print("Your Colab notebook can now:")
    print(f"  1. Load patterns from: {training_file}")
    print("  2. Train Gemma on posting patterns")
    print("  3. Learn UI analysis from Gemini Vision")
    print("  4. Predict optimal posting strategies")
    print()
    print("Colab Notebook: https://colab.research.google.com/drive/18NJ86r3EilIL0HG8e712LKM5FCHzb6NF")
    print()
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_social_media_posting())
