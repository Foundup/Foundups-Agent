#!/usr/bin/env python3
"""
Quick test script to verify optimization improvements.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_session_cache():
    """Test session caching functionality."""
    print("🧪 Testing session cache...")
    
    try:
        from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
        from utils.oauth_manager import get_authenticated_service_with_fallback
        
        # Test authentication with forced credential set
        os.environ["FORCE_CREDENTIAL_SET"] = "2"
        auth_result = get_authenticated_service_with_fallback()
        
        if auth_result:
            service, creds, credential_set = auth_result
            print(f"✅ Authentication successful with {credential_set}")
            
            # Test stream resolver with caching
            resolver = StreamResolver(service)
            result = resolver.resolve_stream()
            
            if result:
                video_id, chat_id = result
                print(f"✅ Stream resolution successful: {video_id[:8]}...")
                print(f"✅ Session cache should be saved for next run")
            else:
                print("❌ No active stream found")
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("\n🧪 Testing circuit breaker...")
    
    try:
        from modules.platform_integration.stream_resolver.src.stream_resolver import circuit_breaker
        
        print(f"Circuit breaker state: {circuit_breaker.state}")
        print(f"Failure count: {circuit_breaker.failure_count}")
        print(f"Failure threshold: {circuit_breaker.failure_threshold}")
        
        if circuit_breaker.state == "OPEN":
            print("⚠️ Circuit breaker is OPEN - API calls will be blocked")
        else:
            print("✅ Circuit breaker is CLOSED - API calls allowed")
            
    except Exception as e:
        print(f"❌ Circuit breaker test failed: {e}")

def test_quota_management():
    """Test quota management functionality."""
    print("\n🧪 Testing quota management...")
    
    try:
        from utils.oauth_manager import quota_manager
        
        # Check cooldown status for all credential sets
        for i in range(1, 5):
            credential_set = f"set_{i}"
            is_cooldown = quota_manager.is_in_cooldown(credential_set)
            
            if is_cooldown:
                cooldown_start = quota_manager.cooldowns[credential_set]
                time_remaining = quota_manager.COOLDOWN_DURATION - (time.time() - cooldown_start)
                print(f"⏳ {credential_set}: IN COOLDOWN ({time_remaining/3600:.1f}h remaining)")
            else:
                print(f"✅ {credential_set}: AVAILABLE")
                
    except Exception as e:
        print(f"❌ Quota management test failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing FoundUps Agent Optimizations")
    print("=" * 50)
    
    test_session_cache()
    test_circuit_breaker()
    test_quota_management()
    
    print("\n" + "=" * 50)
    print("🎯 Optimization tests completed!")
    print("💡 Ready to start optimized bot with: python main.py") 