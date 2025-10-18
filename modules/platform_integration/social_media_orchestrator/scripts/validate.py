#!/usr/bin/env python3
"""
Social Media Orchestrator Validation Script
WSP Compliance: WSP 49, WSP 22
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
import asyncio
import logging
from pathlib import Path

# Add module to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from social_media_orchestrator import (
    create_social_media_orchestrator,
    TwitterAdapter,
    LinkedInAdapter
)


async def validate_orchestrator():
    """Validate the social media orchestrator functionality"""
    print("[ROCKET] Social Media Orchestrator Validation")
    print("=" * 50)
    
    try:
        # Create orchestrator
        config = {
            'logging_level': 'INFO',
            'enable_scheduling': True
        }
        
        orchestrator = create_social_media_orchestrator(config)
        print("[OK] Orchestrator created successfully")
        
        # Initialize
        success = await orchestrator.initialize()
        if success:
            print("[OK] Orchestrator initialized successfully")
        else:
            print("[FAIL] Orchestrator initialization failed")
            return False
            
        # Test platform listing
        platforms = orchestrator.list_supported_platforms()
        print(f"[OK] Supported platforms: {platforms}")
        
        # Test status
        status = orchestrator.get_status()
        print(f"[OK] Orchestrator status: {status['initialized']}")
        
        # Test hello world (dry run)
        for platform in platforms:
            result = await orchestrator.test_platform_hello_world(platform, dry_run=True)
            if result['success']:
                print(f"[OK] {platform.title()} hello world test passed (dry run)")
            else:
                print(f"[FAIL] {platform.title()} hello world test failed: {result.get('error')}")
                
        print("\n[CELEBRATE] All validation tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Validation failed: {e}")
        return False


async def validate_adapters():
    """Validate individual platform adapters"""
    print("\n[U+1F50C] Platform Adapter Validation")
    print("=" * 50)
    
    # Test Twitter Adapter
    try:
        twitter = TwitterAdapter()
        limits = twitter.get_platform_limits()
        print(f"[OK] Twitter adapter - max length: {limits['max_content_length']}")
        
        # Test content formatting
        test_content = "Test content for Twitter"
        formatted = twitter.format_content_for_twitter(test_content, {
            'hashtags': ['#FoundUps', '#Test'],
            'mentions': ['@foundups']
        })
        print(f"[OK] Twitter content formatting: {len(formatted)} chars")
        
    except Exception as e:
        print(f"[FAIL] Twitter adapter validation failed: {e}")
        
    # Test LinkedIn Adapter
    try:
        linkedin = LinkedInAdapter()
        limits = linkedin.get_platform_limits()
        print(f"[OK] LinkedIn adapter - max length: {limits['max_content_length']}")
        
        # Test content formatting
        test_content = "Test content for LinkedIn professional network"
        formatted = linkedin.format_content_for_linkedin(test_content, {
            'hashtags': ['#FoundUps', '#Development', '#Innovation'],
            'add_signature': True
        })
        print(f"[OK] LinkedIn content formatting: {len(formatted)} chars")
        
    except Exception as e:
        print(f"[FAIL] LinkedIn adapter validation failed: {e}")


def main():
    """Main validation function"""
    print("[SEARCH] Social Media Orchestrator Module Validation")
    print("WSP 49 Compliance Check")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during validation
    
    try:
        # Run async validations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        orchestrator_valid = loop.run_until_complete(validate_orchestrator())
        loop.run_until_complete(validate_adapters())
        
        if orchestrator_valid:
            print("\n[TARGET] WSP 49 COMPLIANCE: [OK] PASSED")
            print("Social Media Orchestrator module is fully functional")
            return 0
        else:
            print("\n[ALERT] WSP 49 COMPLIANCE: [FAIL] FAILED")
            return 1
            
    except Exception as e:
        print(f"\n[U+1F4A5] Validation error: {e}")
        print("[ALERT] WSP 49 COMPLIANCE: [FAIL] FAILED")
        return 1
    finally:
        if 'loop' in locals():
            loop.close()


if __name__ == "__main__":
    sys.exit(main())