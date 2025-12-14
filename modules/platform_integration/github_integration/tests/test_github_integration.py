#!/usr/bin/env python3
"""
GitHub Integration Test Script
Tests the complete GitHub integration once token is configured.

Usage:
1. Add your GitHub token to .env file: GITHUB_TOKEN=your_token_here
2. Run: python test_github_integration.py
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
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path (4 levels up from this test file)
test_file = Path(__file__).resolve()
project_root = test_file.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_github_integration():
    """Test GitHub integration functionality"""
    
    print("[ROCKET] Testing GitHub Integration for FoundUps Agent")
    print("=" * 50)
    
    # Check if token is available
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("[FAIL] GITHUB_TOKEN not found in environment")
        print("[NOTE] Please add your GitHub token to the .env file:")
        print("   1. Generate token at: https://github.com/settings/tokens")
        print("   2. Add to .env: GITHUB_TOKEN=your_token_here")
        print("   3. Ensure token has 'repo' and 'workflow' scopes")
        return False
    
    try:
        # Import GitHub integration modules
        from modules.platform_integration.github_integration.src.wre_integration import WREGitHubIntegration
        from modules.platform_integration.github_integration.src.wsp_automation import WSPAutomationManager
        
        print("[OK] GitHub integration modules imported successfully")
        
        # Test 1: Health Check
        print("\n[U+1F3E5] Running health check...")
        integration = WREGitHubIntegration(token=token)
        health = await integration.health_check()
        
        if health["overall_status"]:
            print("[OK] GitHub integration is healthy!")
            print(f"   - User: {health.get('user', 'Unknown')}")
            print(f"   - Repository: {health.get('repository', 'Unknown')}")
            print(f"   - Rate limit: {health.get('rate_limit', {}).get('remaining', '?')}/{health.get('rate_limit', {}).get('limit', '?')}")
        else:
            print("[FAIL] GitHub integration has issues:")
            for error in health.get("errors", []):
                print(f"   - {error}")
            return False
        
        # Test 2: Repository Status
        print("\n[DATA] Checking repository status...")
        status = await integration.sync_repository_status()
        
        if "error" not in status:
            print("[OK] Repository status retrieved:")
            print(f"   - Repository: {status['repository']['name']}")
            print(f"   - Default branch: {status['repository']['default_branch']}")
            print(f"   - Branches: {status['branches']['total']}")
            print(f"   - Open PRs: {status['pull_requests']['open']}")
            print(f"   - Open Issues: {status['issues']['open']}")
            print(f"   - Workflows: {status['workflows']['total']}")
        else:
            print(f"[FAIL] Failed to get repository status: {status['error']}")
            return False
        
        # Test 3: WSP Compliance Scan
        print("\n[SEARCH] Running WSP compliance scan...")
        wsp_manager = WSPAutomationManager(token=token)
        violations = await wsp_manager.scan_for_violations()
        
        print(f"[OK] WSP scan complete: {len(violations)} violations found")
        if violations:
            # Group by type
            violation_types = {}
            for v in violations:
                v_type = v.violation_type.value
                if v_type not in violation_types:
                    violation_types[v_type] = 0
                violation_types[v_type] += 1
            
            print("   Violations by type:")
            for v_type, count in violation_types.items():
                print(f"   - {v_type}: {count}")
                
            # Count auto-fixable
            auto_fixable = sum(1 for v in violations if v.auto_fixable)
            print(f"   - Auto-fixable: {auto_fixable}/{len(violations)}")
        else:
            print("   [CELEBRATE] No violations found - perfect WSP compliance!")
        
        # Test 4: Generate Compliance Report
        print("\n[CLIPBOARD] Generating compliance report...")
        report = await wsp_manager.generate_compliance_report()
        
        print(f"[OK] Compliance report generated:")
        print(f"   - Compliance score: {report['compliance_score']}%")
        print(f"   - Total violations: {report['total_violations']}")
        print(f"   - Auto-fixable: {report['auto_fixable']}")
        print(f"   - Manual fixes needed: {report['manual_fixes_required']}")
        
        if report['violations_by_severity']:
            print("   Violations by severity:")
            for severity, count in report['violations_by_severity'].items():
                if count > 0:
                    print(f"   - {severity.title()}: {count}")
        
        print("\n[CELEBRATE] GitHub Integration Test Complete!")
        print("=" * 50)
        print("[OK] All tests passed - GitHub integration is working correctly!")
        print("\n[ROCKET] You can now use:")
        print("   - Automated PR creation")
        print("   - WSP violation detection and fixes") 
        print("   - Issue creation for violations")
        print("   - Repository status monitoring")
        print("   - Workflow automation")
        
        return True
        
    except ImportError as e:
        print(f"[FAIL] Failed to import GitHub integration modules: {e}")
        print("[IDEA] Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"[FAIL] Test failed with error: {e}")
        logger.exception("Test failed")
        return False

def main():
    """Main test function"""
    # Load environment variables
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        try:
            load_dotenv(env_file)
            print(f"[OK] Loaded environment variables from {env_file}")
        except ImportError:
            print("[U+26A0]️  python-dotenv not installed, reading environment manually")
            # Simple .env parsing
            with open(env_file, 'r', encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if value and not value.isspace():
                            os.environ[key.strip()] = value.strip()
    else:
        print("[U+26A0]️  No .env file found - relying on system environment variables")
    
    # Run the test
    success = asyncio.run(test_github_integration())
    
    if success:
        print("\n[OK] GitHub integration is ready for production use!")
    else:
        print("\n[FAIL] Please fix the issues above before using GitHub integration.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
