#!/usr/bin/env python3
"""
Quota Tester - Test all OAuth credentials and sort by available quota
WSP-Compliant: WSP 48 (Recursive Improvement)

0102 Architect: Intelligently tests and sorts credentials by quota availability
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import logging
import os
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import time
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class QuotaTester:
    """Test and rank OAuth credentials by available quota"""
    
    def __init__(self):
        self.quota_status = {}
        self.test_results_file = "credentials/quota_test_results.json"
        self.last_test_time = None
        
    def test_single_credential(self, service, cred_set: int) -> Dict:
        """
        Test a single credential set for quota availability.
        
        Returns:
            Dict with quota status and score
        """
        result = {
            'credential_set': cred_set,
            'has_quota': False,
            'quota_score': 0,
            'error': None,
            'test_time': datetime.now().isoformat(),
            'api_calls_successful': 0,
            'last_error': None
        }
        
        try:
            # Test 1: Simple channels.list (costs 1 quota)
            logger.info(f"[TEST] Testing credential set {cred_set} - channels.list")
            response = service.channels().list(
                part="id",
                mine=True
            ).execute()
            result['api_calls_successful'] += 1
            result['quota_score'] += 10  # Base score for working
            
            # Test 2: Try search.list with minimal cost (costs ~100)
            logger.info(f"[TEST] Testing credential set {cred_set} - search.list")
            response = service.search().list(
                part="id",
                maxResults=1,
                type="video",
                eventType="live",
                q="test"
            ).execute()
            result['api_calls_successful'] += 1
            result['quota_score'] += 50  # Higher score for search working
            result['has_quota'] = True
            
            # Test 3: Try liveChatMessages.list if we can (costs 5)
            # This is optional - only if we have a known chat ID
            
            logger.info(f"[OK] Credential set {cred_set} has quota! Score: {result['quota_score']}")
            
        except HttpError as e:
            error_reason = str(e)
            result['error'] = error_reason
            
            if 'quotaExceeded' in error_reason:
                result['quota_score'] = 0
                result['last_error'] = 'quota_exceeded'
                logger.warning(f"[QUOTA] Credential set {cred_set} - Quota exhausted")
            elif 'forbidden' in error_reason.lower():
                result['quota_score'] = 1  # Might work for some calls
                result['last_error'] = 'forbidden'
                logger.warning(f"[WARN] Credential set {cred_set} - Forbidden (partial access)")
            else:
                result['quota_score'] = 2  # Unknown error, might be temporary
                result['last_error'] = 'unknown'
                logger.warning(f"[ERROR] Credential set {cred_set} - Error: {error_reason[:100]}")
                
        except Exception as e:
            result['error'] = str(e)
            result['quota_score'] = 0
            logger.error(f"[FAIL] Credential set {cred_set} - Failed: {e}")
            
        return result
    
    def test_all_credentials(self) -> List[Dict]:
        """
        Test all 10 credential sets and rank them by quota availability.
        
        Returns:
            List of credential results sorted by quota score
        """
        from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
        
        results = []
        logger.info("="*60)
        logger.info("[TEST] TESTING ALL OAUTH CREDENTIALS FOR QUOTA")
        logger.info("="*60)
        
        for cred_set in range(1, 11):  # Test sets 1-10
            logger.info(f"\n[{cred_set}/10] Testing credential set {cred_set}...")
            
            try:
                # Get service for this credential set
                service, actual_set = get_authenticated_service(
                    token_index=cred_set  # Use the correct parameter name
                )
                
                if service:
                    result = self.test_single_credential(service, cred_set)
                    results.append(result)
                else:
                    results.append({
                        'credential_set': cred_set,
                        'has_quota': False,
                        'quota_score': 0,
                        'error': 'Could not authenticate',
                        'test_time': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"Failed to test credential set {cred_set}: {e}")
                results.append({
                    'credential_set': cred_set,
                    'has_quota': False,
                    'quota_score': 0,
                    'error': str(e),
                    'test_time': datetime.now().isoformat()
                })
            
            # Small delay between tests to avoid rate limiting
            time.sleep(2)
        
        # Sort by quota score (highest first)
        results.sort(key=lambda x: x['quota_score'], reverse=True)
        
        # Save results
        self.save_results(results)
        
        # Display summary
        self.display_summary(results)
        
        return results
    
    def save_results(self, results: List[Dict]):
        """Save test results to file for persistence"""
        try:
            os.makedirs(os.path.dirname(self.test_results_file), exist_ok=True)
            
            data = {
                'test_time': datetime.now().isoformat(),
                'results': results,
                'recommended_order': [r['credential_set'] for r in results if r['quota_score'] > 0]
            }
            
            with open(self.test_results_file, 'w', encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"[SAVED] Test results saved to {self.test_results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def load_results(self) -> Optional[Dict]:
        """Load previous test results"""
        try:
            if os.path.exists(self.test_results_file):
                with open(self.test_results_file, 'r', encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
        return None
    
    def get_recommended_order(self) -> List[int]:
        """
        Get recommended credential order based on test results.
        
        Returns:
            List of credential set numbers in recommended order
        """
        # Load cached results if recent (within last hour)
        cached = self.load_results()
        if cached:
            test_time = datetime.fromisoformat(cached['test_time'])
            if datetime.now() - test_time < timedelta(hours=1):
                logger.info(f"Using cached quota test from {test_time}")
                return cached['recommended_order']
        
        # Otherwise run new test
        logger.info("Running fresh quota test...")
        results = self.test_all_credentials()
        return [r['credential_set'] for r in results if r['quota_score'] > 0]
    
    def display_summary(self, results: List[Dict]):
        """Display a summary of test results"""
        logger.info("\n" + "="*60)
        logger.info("[SUMMARY] QUOTA TEST SUMMARY")
        logger.info("="*60)
        
        working_sets = [r for r in results if r['has_quota']]
        partial_sets = [r for r in results if not r['has_quota'] and r['quota_score'] > 0]
        exhausted_sets = [r for r in results if r['quota_score'] == 0]
        
        logger.info(f"\n[OK] Working Sets ({len(working_sets)}): {[r['credential_set'] for r in working_sets]}")
        logger.info(f"[WARN] Partial Sets ({len(partial_sets)}): {[r['credential_set'] for r in partial_sets]}")
        logger.info(f"[EXHAUSTED] Exhausted Sets ({len(exhausted_sets)}): {[r['credential_set'] for r in exhausted_sets]}")
        
        if working_sets:
            logger.info(f"\n[RECOMMENDED] ORDER: {[r['credential_set'] for r in working_sets]}")
            logger.info(f"Best credential set: #{working_sets[0]['credential_set']} (score: {working_sets[0]['quota_score']})")
        else:
            logger.info("\n[WARNING] NO CREDENTIALS WITH AVAILABLE QUOTA!")
            logger.info("All credential sets appear to be exhausted.")
            logger.info("Quota typically resets at midnight Pacific Time.")
            
            # Calculate time until midnight Pacific
            from datetime import timezone
            from zoneinfo import ZoneInfo
            
            now = datetime.now(ZoneInfo('America/Los_Angeles'))
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            time_until_reset = midnight - now
            hours = time_until_reset.total_seconds() / 3600
            
            logger.info(f"Estimated time until reset: {hours:.1f} hours")
        
        logger.info("="*60)


def quick_test_credential(cred_set: int) -> bool:
    """
    Quick test to check if a credential has quota.
    
    Returns:
        True if credential has quota, False otherwise
    """
    from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
    
    try:
        service, actual_set = get_authenticated_service(
            token_index=cred_set
        )
        
        if not service:
            return False
            
        # Quick test with minimal quota cost
        response = service.channels().list(
            part="id",
            mine=True
        ).execute()
        
        return True
        
    except HttpError as e:
        if 'quotaExceeded' in str(e):
            return False
        return False  # Any error means not usable
        
    except Exception:
        return False


def get_best_credential_set() -> Optional[int]:
    """
    Get the best available credential set based on quota testing.
    
    Returns:
        Credential set number or None if all exhausted
    """
    tester = QuotaTester()
    order = tester.get_recommended_order()
    
    if order:
        return order[0]
    return None


if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode - just get best credential
        best = get_best_credential_set()
        if best:
            print(f"\n[OK] Best credential set: #{best}")
        else:
            print("\n[FAIL] No credentials with quota available")
    else:
        # Full test mode
        tester = QuotaTester()
        results = tester.test_all_credentials()
        
        print("\n[0102] Quota test complete. Results saved.")
        print("Use --quick flag for quick best credential check")