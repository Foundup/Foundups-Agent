#!/usr/bin/env python3
"""
WSP-Compliant Emoji Sequence Testing Module
Tests all 10 emoji sequences to ensure proper detection and response generation.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Also add the current working directory to ensure modules can be found
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('emoji_test_results.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def test_emoji_sequences():
    """Test all 10 emoji sequences following WSP procedures."""
    
    try:
        # Import the sequence map
        from modules.ai_intelligence.banter_engine.banter_engine.sequence_responses import SEQUENCE_MAP
        from modules.ai_intelligence.banter_engine.banter_engine.src.banter_engine import BanterEngine
        
        logger.info("🎯 Starting WSP-Compliant Emoji Sequence Testing")
        logger.info("=" * 60)
        
        # Initialize banter engine
        banter_engine = BanterEngine()
        logger.info("✅ BanterEngine initialized successfully")
        
        # Test all sequences
        test_results = {}
        total_sequences = len(SEQUENCE_MAP)
        
        logger.info(f"📊 Testing {total_sequences} emoji sequences:")
        
        for i, (sequence_tuple, info) in enumerate(SEQUENCE_MAP.items(), 1):
            emoji_sequence = info['emoji']
            logger.info(f"\n🔍 Test {i}/{total_sequences}: {emoji_sequence}")
            logger.info(f"   Tuple: {sequence_tuple}")
            logger.info(f"   State: {info['state']}")
            logger.info(f"   Tone: {info['tone']}")
            
            try:
                # Test the sequence with just the emoji sequence
                result = banter_engine.process_input(emoji_sequence)
                
                if result and hasattr(result, 'response') and result.response:
                    logger.info(f"   ✅ PASS - Response: {result.response}")
                    test_results[emoji_sequence] = {
                        'status': 'PASS',
                        'response': result.response,
                        'state': result.state if hasattr(result, 'state') else 'Unknown',
                        'tuple': sequence_tuple
                    }
                else:
                    logger.error(f"   ❌ FAIL - No response generated")
                    logger.debug(f"   Debug - Result: {result}")
                    test_results[emoji_sequence] = {
                        'status': 'FAIL',
                        'response': None,
                        'error': 'No response generated',
                        'tuple': sequence_tuple
                    }
                    
            except Exception as e:
                logger.error(f"   ❌ ERROR - {str(e)}")
                test_results[emoji_sequence] = {
                    'status': 'ERROR',
                    'response': None,
                    'error': str(e),
                    'tuple': sequence_tuple
                }
        
        # Generate summary report
        logger.info("\n" + "=" * 60)
        logger.info("📋 WSP TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for r in test_results.values() if r['status'] == 'PASS')
        failed = sum(1 for r in test_results.values() if r['status'] == 'FAIL')
        errors = sum(1 for r in test_results.values() if r['status'] == 'ERROR')
        
        logger.info(f"✅ PASSED: {passed}/{total_sequences}")
        logger.info(f"❌ FAILED: {failed}/{total_sequences}")
        logger.info(f"🚨 ERRORS: {errors}/{total_sequences}")
        
        if passed == total_sequences:
            logger.info("🎉 ALL TESTS PASSED - System is WSP compliant!")
        else:
            logger.warning("⚠️  Some tests failed - System needs attention")
            
        # Detailed results
        logger.info("\n📊 DETAILED RESULTS:")
        for sequence, result in test_results.items():
            status_emoji = "✅" if result['status'] == 'PASS' else "❌"
            logger.info(f"{status_emoji} {sequence} {result['tuple']}: {result['status']}")
            if result.get('response'):
                logger.info(f"   Response: {result['response']}")
            if result.get('error'):
                logger.info(f"   Error: {result['error']}")
        
        return test_results
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 Make sure all modules are properly installed and accessible")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return None

def test_specific_sequence(sequence):
    """Test a specific emoji sequence."""
    try:
        from modules.ai_intelligence.banter_engine.banter_engine.src.banter_engine import BanterEngine
        
        logger.info(f"🎯 Testing specific sequence: {sequence}")
        
        banter_engine = BanterEngine()
        result = banter_engine.process_input(sequence)
        
        if result and hasattr(result, 'response') and result.response:
            logger.info(f"✅ SUCCESS - Response: {result.response}")
            return True
        else:
            logger.error(f"❌ FAILED - No response for {sequence}")
            logger.debug(f"Debug - Result: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERROR testing {sequence}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific sequence
        sequence = sys.argv[1]
        test_specific_sequence(sequence)
    else:
        # Test all sequences
        test_emoji_sequences() 