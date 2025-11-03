#!/usr/bin/env python3
"""
Test Single Instance Enforcement
WSP 48: Verify duplicate process prevention works
"""

import sys
import os
import time
import subprocess
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from modules.infrastructure.shared_utilities.single_instance import SingleInstanceEnforcer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_single_instance():
    """Test single instance enforcement."""
    
    logger.info("="*60)
    logger.info("[U+1F9EA] TESTING SINGLE INSTANCE ENFORCEMENT")
    logger.info("="*60)
    
    # Test 1: Basic lock acquisition
    logger.info("\n1️⃣ Testing basic lock acquisition...")
    enforcer1 = SingleInstanceEnforcer("test_process")
    
    if enforcer1.acquire_lock():
        logger.info("[OK] First instance acquired lock")
    else:
        logger.error("[FAIL] First instance failed to acquire lock")
        return
    
    # Test 2: Try to acquire lock again (should fail)
    logger.info("\n2️⃣ Testing duplicate prevention...")
    enforcer2 = SingleInstanceEnforcer("test_process")
    
    if enforcer2.acquire_lock():
        logger.error("[FAIL] Second instance acquired lock (should have failed!)")
    else:
        logger.info("[OK] Second instance blocked as expected")
    
    # Test 3: Check status
    logger.info("\n3️⃣ Testing status check...")
    existing_pid = enforcer2.check_status()
    if existing_pid:
        logger.info(f"[OK] Detected existing instance (PID: {existing_pid})")
    else:
        logger.error("[FAIL] Failed to detect existing instance")
    
    # Test 4: Release and re-acquire
    logger.info("\n4️⃣ Testing lock release...")
    enforcer1.release_lock()
    logger.info("[U+1F513] Released first lock")
    
    if enforcer2.acquire_lock():
        logger.info("[OK] Second instance acquired lock after release")
        enforcer2.release_lock()
    else:
        logger.error("[FAIL] Second instance still blocked after release")
    
    # Test 5: Context manager
    logger.info("\n5️⃣ Testing context manager...")
    try:
        with SingleInstanceEnforcer("context_test") as lock:
            logger.info("[OK] Context manager acquired lock")
            # Try duplicate in context
            enforcer3 = SingleInstanceEnforcer("context_test")
            if not enforcer3.acquire_lock():
                logger.info("[OK] Duplicate blocked in context")
            else:
                logger.error("[FAIL] Duplicate not blocked in context")
    except Exception as e:
        logger.error(f"[FAIL] Context manager failed: {e}")
    
    # Verify lock released after context
    enforcer4 = SingleInstanceEnforcer("context_test")
    if enforcer4.acquire_lock():
        logger.info("[OK] Lock released after context exit")
        enforcer4.release_lock()
    else:
        logger.error("[FAIL] Lock still held after context exit")
    
    logger.info("\n" + "="*60)
    logger.info("[U+1F3C1] SINGLE INSTANCE TEST COMPLETE")
    logger.info("="*60)

if __name__ == "__main__":
    test_single_instance()
