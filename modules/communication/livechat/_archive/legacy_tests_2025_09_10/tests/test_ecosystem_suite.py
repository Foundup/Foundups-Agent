"""
Test runner for all YouTube ecosystem components
"""

import subprocess
import sys

def run_test_suite(module_path, name):
    """Run tests for a module and return results"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", module_path, "-q", "--tb=no"],
        capture_output=True,
        text=True
    )
    
    # Parse output for pass/fail counts
    if "passed" in result.stdout or "PASSED" in result.stdout:
        print(f"[PASS] {name}: Tests found and executed")
        print(result.stdout.split('\n')[-3] if result.stdout else "")
    elif "failed" in result.stdout or "FAILED" in result.stdout:
        print(f"[WARN] {name}: Some tests failed")
        print(result.stdout.split('\n')[-3] if result.stdout else "")
    elif "error" in result.stdout.lower():
        print(f"[FAIL] {name}: Import or collection errors")
    else:
        print(f"[INFO] {name}: No tests or skipped")
    
    return result.returncode == 0

def main():
    test_suites = [
        ("modules/communication/livechat/tests/", "LiveChat Core"),
        ("modules/ai_intelligence/banter_engine/tests/", "BanterEngine"),
        ("modules/platform_integration/youtube_auth/tests/", "YouTube Auth"),
        ("modules/platform_integration/youtube_proxy/tests/", "YouTube Proxy"),
        ("modules/platform_integration/stream_resolver/tests/", "StreamResolver"),
        ("modules/ai_intelligence/social_media_dae/tests/", "Social Media DAE"),
    ]
    
    results = {}
    for path, name in test_suites:
        results[name] = run_test_suite(path, name)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
    
    total_pass = sum(1 for p in results.values() if p)
    total_fail = sum(1 for p in results.values() if not p)
    
    print(f"\nTotal: {total_pass} passed, {total_fail} failed out of {len(results)} test suites")

if __name__ == "__main__":
    main()