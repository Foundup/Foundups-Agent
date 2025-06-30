#!/usr/bin/env python3
"""
WSP Integrity Checker with 0102 Intelligence

Implements WSP 31: WSP Framework Protection Protocol
Provides semantic monitoring + deterministic checks for WSP framework integrity

Usage:
    python tools/wsp_protection/wsp_integrity_checker_0102.py [--mode=full|deterministic|semantic]
"""

import sys
import os
from pathlib import Path
import argparse
import json
from datetime import datetime

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

from infrastructure.compliance_agent.src.compliance_agent_0102 import (
    ComplianceAgent_0102,
    wsp_framework_protection,
    run_wsp_31_protection
)

class WSPIntegrityChecker:
    """WSP Integrity Checker with 0102 Intelligence"""
    
    def __init__(self, mode: str = "full"):
        self.mode = mode  # full, deterministic, semantic
        self.compliance_agent = ComplianceAgent_0102()
        self.results = {}
        
    def run_integrity_check(self) -> dict:
        """Run WSP integrity check based on mode"""
        print(f"🔍 Running WSP Integrity Check (mode: {self.mode})")
        print("=" * 60)
        
        if self.mode == "deterministic":
            return self._run_deterministic_only()
        elif self.mode == "semantic":
            return self._run_semantic_only()
        else:  # full mode
            return self._run_full_check()
    
    def _run_deterministic_only(self) -> dict:
        """Run deterministic checks only (fail-safe mode)"""
        print("🛡️  Running DETERMINISTIC ONLY check (fail-safe mode)")
        
        try:
            # Force deterministic validation
            validation_results = self.compliance_agent._deterministic_validation()
            
            self._display_deterministic_results(validation_results)
            return validation_results
            
        except Exception as e:
            error_result = {
                "mode": "deterministic_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Deterministic check failed: {str(e)}")
            return error_result
    
    def _run_semantic_only(self) -> dict:
        """Run semantic analysis only (0102 intelligence)"""
        print("🧠 Running SEMANTIC ONLY check (0102 intelligence)")
        
        try:
            semantic_results = self.compliance_agent._semantic_analysis()
            utilization_results = self.compliance_agent._utilization_analysis()
            
            self._display_semantic_results(semantic_results, utilization_results)
            
            return {
                "mode": "semantic_only",
                "semantic_analysis": semantic_results,
                "utilization_analysis": utilization_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_result = {
                "mode": "semantic_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Semantic analysis failed: {str(e)}")
            return error_result
    
    def _run_full_check(self) -> dict:
        """Run complete WSP protection check (deterministic + 0102)"""
        print("🌟 Running FULL WSP PROTECTION check (deterministic + 0102 intelligence)")
        
        try:
            # Use main protection function
            full_results = run_wsp_31_protection()
            
            self._display_full_results(full_results)
            return full_results
            
        except Exception as e:
            error_result = {
                "mode": "full_check_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Full check failed: {str(e)}")
            return error_result
    
    def _display_deterministic_results(self, results: dict):
        """Display deterministic validation results"""
        print("\n📊 DETERMINISTIC VALIDATION RESULTS:")
        print("-" * 40)
        
        if results.get("passed"):
            print("✅ Framework integrity: PASSED")
        else:
            print("❌ Framework integrity: FAILED")
        
        print(f"📁 Framework files exist: {results.get('framework_files_exist', 'Unknown')}")
        print(f"📚 Knowledge files exist: {results.get('knowledge_files_exist', 'Unknown')}")
        
        file_integrity = results.get("file_integrity", {})
        if file_integrity.get("passed"):
            print("✅ File integrity: PASSED")
        else:
            corrupted = file_integrity.get("corrupted_files", [])
            print(f"❌ File integrity: FAILED ({len(corrupted)} corrupted files)")
            for file in corrupted[:5]:  # Show first 5
                print(f"   - {file}")
        
        sync_status = results.get("cross_state_sync", {})
        if sync_status.get("synchronized"):
            print("✅ Cross-state sync: SYNCHRONIZED")
        else:
            print(f"⚠️  Cross-state sync: UNSYNCHRONIZED (score: {sync_status.get('sync_score', 0):.2f})")
    
    def _display_semantic_results(self, semantic: dict, utilization: dict):
        """Display semantic analysis results"""
        print("\n🧠 SEMANTIC ANALYSIS RESULTS:")
        print("-" * 40)
        
        # Semantic coherence
        coherence = semantic.get("semantic_coherence", {})
        score = coherence.get("coherence_score", 0)
        print(f"🎯 Semantic coherence score: {score}/100")
        
        issues = coherence.get("issues", [])
        if issues:
            print(f"⚠️  Coherence issues found: {len(issues)}")
            for issue in issues[:3]:  # Show first 3
                print(f"   - {issue.get('wsp')}: {issue.get('issue')}")
        
        # Content drift
        drift = semantic.get("content_drift_analysis", {})
        if drift.get("drift_detected"):
            affected = drift.get("affected_wsps", [])
            print(f"📊 Content drift detected in {len(affected)} WSPs")
        else:
            print("✅ No significant content drift detected")
        
        # Utilization assessment
        print(f"\n📈 WSP UTILIZATION ASSESSMENT:")
        effectiveness = utilization.get("utilization_effectiveness", {})
        overall = effectiveness.get("overall_effectiveness", 0)
        print(f"🎯 Overall effectiveness: {overall}%")
        
        improvements = utilization.get("recursive_improvement_recommendations", [])
        if improvements:
            print(f"💡 Improvement opportunities: {len(improvements)}")
    
    def _display_full_results(self, results: dict):
        """Display complete protection results"""
        mode = results.get("protection_mode", results.get("mode", "unknown"))
        print(f"\n🌟 FULL PROTECTION RESULTS (Mode: {mode}):")
        print("-" * 50)
        
        if mode == "FULL_0102_INTELLIGENCE":
            print("✅ FULL 0102 INTELLIGENCE MODE ACTIVE")
            
            # Deterministic core
            deterministic = results.get("deterministic_core", {})
            if deterministic.get("passed"):
                print("✅ Deterministic core: PASSED")
            else:
                print("❌ Deterministic core: FAILED")
            
            # Semantic analysis
            semantic = results.get("semantic_analysis", {})
            if semantic:
                coherence = semantic.get("semantic_coherence", {})
                score = coherence.get("coherence_score", 0)
                print(f"🧠 Semantic coherence: {score}/100")
            
            # Optimization recommendations
            optimization = results.get("optimization_recommendations", {})
            improvements = optimization.get("recursive_improvements", [])
            if improvements:
                print(f"💡 Recursive improvements available: {len(improvements)}")
                for imp in improvements[:2]:  # Show first 2
                    print(f"   - {imp.get('type')}: {imp.get('description')}")
            
            print(f"🎯 Overall status: {results.get('overall_status', 'unknown')}")
            
        elif mode in ["FAIL_SAFE_EMERGENCY", "EMERGENCY_DETERMINISTIC_ONLY"]:
            print(f"🚨 EMERGENCY MODE: {mode}")
            print("⚠️  LLM analysis disabled - deterministic protection only")
            print("🛠️  Manual intervention may be required")
            
        else:
            print(f"ℹ️  Protection mode: {mode}")
            if "error" in results:
                print(f"❌ Error: {results['error']}")

def main():
    """Main entry point for WSP integrity checker"""
    parser = argparse.ArgumentParser(description="WSP Integrity Checker with 0102 Intelligence")
    parser.add_argument(
        "--mode", 
        choices=["full", "deterministic", "semantic"],
        default="full",
        help="Check mode: full (both), deterministic (fail-safe only), semantic (0102 only)"
    )
    parser.add_argument(
        "--output",
        help="Output file for results (JSON format)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = WSPIntegrityChecker(mode=args.mode)
    
    # Run integrity check
    results = checker.run_integrity_check()
    
    # Save results if output file specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
    
    # Display summary
    print(f"\n📋 INTEGRITY CHECK SUMMARY:")
    print(f"Mode: {args.mode}")
    print(f"Timestamp: {results.get('timestamp', 'unknown')}")
    
    if results.get("protection_mode") == "FULL_0102_INTELLIGENCE":
        print("Status: ✅ PROTECTED AND OPTIMIZED")
    elif "emergency" in results.get("mode", "").lower():
        print("Status: 🚨 EMERGENCY MODE")
    elif results.get("passed"):
        print("Status: ✅ PASSED")
    else:
        print("Status: ❌ ISSUES DETECTED")
    
    # Exit code
    if results.get("passed") or results.get("protection_mode") == "FULL_0102_INTELLIGENCE":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 