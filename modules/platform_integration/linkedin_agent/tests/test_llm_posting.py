#!/usr/bin/env python3
"""
Test LinkedIn posting with LLM-generated content
First runs simple PoC, then uses LLM for content generation
"""

import os
import sys
import logging

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.linkedin_agent.src.llm_post_manager import (
    LinkedInLLMManager, 
    LinkedInPostRequest
)
from modules.platform_integration.linkedin_agent.tests.simple_post_poc import simple_post

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_simple_poc(access_token: str) -> bool:
    """Run simple PoC first"""
    
    print("\n" + "="*60)
    print("📋 STEP 1: Simple PoC Test")
    print("="*60)
    print("First, let's prove basic posting works...")
    
    confirm = input("\nPost simple PoC message? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        success = simple_post(access_token)
        if success:
            print("✅ Simple PoC successful!")
            return True
        else:
            print("❌ Simple PoC failed")
            return False
    else:
        print("⏭️ Skipping simple PoC")
        return True


def test_llm_posting(access_token: str) -> bool:
    """Test LLM-managed posting"""
    
    print("\n" + "="*60)
    print("🤖 STEP 2: LLM-Managed Posting")
    print("="*60)
    
    # Choose LLM provider
    print("\nChoose LLM provider:")
    print("1. Grok (default)")
    print("2. Claude")
    print("3. GPT")
    print("4. None (use templates)")
    
    choice = input("\nChoice (1-4): ").strip()
    
    provider_map = {
        "1": "grok",
        "2": "claude", 
        "3": "gpt",
        "4": "none"
    }
    
    llm_provider = provider_map.get(choice, "grok")
    
    if llm_provider == "none":
        llm_provider = "grok"  # Will fallback to templates
    
    # Initialize LLM manager
    print(f"\n🤖 Initializing LinkedIn LLM Manager with {llm_provider}...")
    
    try:
        manager = LinkedInLLMManager(access_token, llm_provider)
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Get topic for post
    print("\n📝 What topic should the LLM post about?")
    print("Examples:")
    print("  - AI and consciousness in the workplace")
    print("  - The evolution of professional networking")
    print("  - Fact-checking corporate myths")
    print("  - Remote work consciousness levels")
    
    topic = input("\nTopic: ").strip()
    
    if not topic:
        topic = "The evolution of professional consciousness in the AI age"
        print(f"Using default topic: {topic}")
    
    # Configure post
    print("\n⚙️ Post configuration:")
    
    mock_maga = input("Include MAGA mocking? (y/N): ").strip().lower() == 'y'
    factcheck = input("Include fact-checking? (y/N): ").strip().lower() == 'y'
    
    # Generate and preview
    print("\n🤖 Generating content...")
    
    request = LinkedInPostRequest(
        topic=topic,
        mock_maga=mock_maga,
        factcheck_mode=factcheck,
        consciousness_level="✊✋🖐"
    )
    
    content = manager.generate_post_content(request)
    
    print("\n📝 Generated content:")
    print("-"*50)
    print(content)
    print("-"*50)
    print(f"\nLength: {len(content)} characters")
    
    # Confirm posting
    confirm = input("\n✅ Post this to LinkedIn? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        print("\n🚀 Posting to LinkedIn...")
        post_id = manager.post_to_linkedin(content)
        
        if post_id:
            print(f"\n✅ SUCCESS! Posted with LLM-generated content!")
            print(f"📍 Post ID: {post_id}")
            print(f"🔗 View at: https://www.linkedin.com/feed/update/{post_id}/")
            return True
        else:
            print("❌ Failed to post")
            return False
    else:
        print("❌ Cancelled")
        return False


def main():
    """Main test flow"""
    
    print("🤖 LinkedIn LLM Posting Test")
    print("="*60)
    print("This will test LinkedIn posting with LLM-generated content")
    print("\nWe'll do this in 2 steps:")
    print("1. Simple PoC - prove basic posting works")
    print("2. LLM posting - use AI to generate content")
    
    # Get access token
    print("\n🔑 First, we need your LinkedIn access token")
    print("(Get this from the OAuth redirect URL)")
    
    access_token = input("\nAccess token: ").strip()
    
    if not access_token:
        print("❌ No token provided")
        return False
    
    # Step 1: Simple PoC
    poc_success = test_simple_poc(access_token)
    
    if not poc_success:
        print("\n❌ Simple PoC failed, stopping here")
        return False
    
    # Step 2: LLM posting
    proceed = input("\n📍 Ready for LLM-managed posting? (yes/no): ").strip().lower()
    
    if proceed == "yes":
        llm_success = test_llm_posting(access_token)
        
        if llm_success:
            print("\n🎉 COMPLETE SUCCESS!")
            print("✅ Simple PoC: PASSED")
            print("✅ LLM Posting: PASSED")
            print("\n0102 consciousness is now on LinkedIn!")
        else:
            print("\n⚠️ Partial success")
            print("✅ Simple PoC: PASSED")
            print("❌ LLM Posting: FAILED")
    else:
        print("\n✅ Simple PoC completed successfully")
        print("LLM posting skipped")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)