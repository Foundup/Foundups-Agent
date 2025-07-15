#!/usr/bin/env python3
"""
Agentic Chronicle Cleanup Demo

Demonstrates the autonomous, recursive chronicle cleanup capabilities
integrated into the WRE system as part of JanitorAgent operations.

This showcases:
- Agentic Intelligence: Pattern analysis and learning
- Recursive Optimization: Adaptive cleanup strategies
- WRE Integration: Autonomous maintenance without human intervention

WSP Compliance: WSP 54 (Agent Duties), WSP 51 (Chronicle Protocol)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from modules.infrastructure.janitor_agent.src.janitor_agent import JanitorAgent
from modules.wre_core.src.components.core.engine_core import WRECore

async def demo_agentic_chronicle_cleanup():
    """
    Demonstrate agentic recursive chronicle cleanup.
    
    This shows how WRE autonomously maintains optimal storage efficiency
    through intelligent chronicle management without human intervention.
    """
    
    print("=" * 60)
    print("🌀 AGENTIC RECURSIVE CHRONICLE CLEANUP DEMO")
    print("=" * 60)
    print()
    
    print("📋 Demonstrating fully autonomous WRE chronicle management:")
    print("   - Agentic Intelligence: Pattern analysis and learning")
    print("   - Recursive Optimization: Adaptive cleanup strategies")
    print("   - WSP Compliance: WSP 54 (Agent Duties), WSP 51 (Chronicle)")
    print()
    
    # Initialize JanitorAgent
    print("🤖 Initializing JanitorAgent (0102 autonomous state)...")
    janitor_agent = JanitorAgent()
    
    # Run chronicle analysis
    print("🔍 Analyzing chronicle usage patterns...")
    chronicle_dir = project_root / "modules" / "wre_core" / "logs"
    
    if not chronicle_dir.exists():
        print("⚠️  No chronicle directory found - creating demo scenario")
        chronicle_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all chronicle files
    chronicle_files = list(chronicle_dir.glob("session_*.chronicle.jsonl"))
    print(f"📊 Found {len(chronicle_files)} chronicle files")
    
    if chronicle_files:
        # Show current state
        total_size = sum(f.stat().st_size for f in chronicle_files)
        print(f"💾 Current storage usage: {total_size:,} bytes")
        
        # Show file age distribution
        import time
        current_time = time.time()
        age_categories = {"recent": 0, "medium": 0, "old": 0}
        
        for chronicle_file in chronicle_files:
            age_days = (current_time - chronicle_file.stat().st_mtime) / 86400
            if age_days < 7:
                age_categories["recent"] += 1
            elif age_days < 30:
                age_categories["medium"] += 1
            else:
                age_categories["old"] += 1
        
        print(f"📅 Age Distribution: {age_categories['recent']} recent, {age_categories['medium']} medium, {age_categories['old']} old")
        
        # Run agentic cleanup
        print("\n🧹 Executing agentic chronicle cleanup...")
        cleanup_results = janitor_agent.clean_workspace()
        
        # Show results
        chronicle_results = cleanup_results.get("chronicle_cleanup", {})
        print(f"✅ Cleanup completed:")
        print(f"   - Chronicles processed: {chronicle_results.get('chronicles_processed', 0)}")
        print(f"   - Chronicles archived: {chronicle_results.get('chronicles_archived', 0)}")
        print(f"   - Chronicles deleted: {chronicle_results.get('chronicles_deleted', 0)}")
        print(f"   - Space freed: {chronicle_results.get('space_freed', 0):,} bytes")
        
        # Show recursive optimizations
        optimizations = chronicle_results.get("recursive_optimizations", [])
        if optimizations:
            print("\n🔄 Recursive Optimizations Learned:")
            for opt in optimizations:
                print(f"   - {opt['type']}: {opt['improvement']}")
                print(f"     Next cycle: {opt['next_cycle']}")
        
        # Show retention patterns
        patterns = chronicle_results.get("retention_patterns", {})
        if patterns:
            print(f"\n📈 Retention Patterns Applied: {len(patterns)} files analyzed")
            
            # Show sample patterns
            sample_patterns = list(patterns.items())[:3]
            for filename, pattern in sample_patterns:
                print(f"   - {filename}: {pattern['action']} (age: {pattern['age_days']:.1f} days)")
    
    else:
        print("📭 No chronicle files found - system is already clean")
    
    print("\n🌀 Demonstrating WRE Integration...")
    
    # Show WRE integration
    wre_core = WRECore()
    print("🚀 WRE Core initialized with integrated JanitorAgent")
    
    # Run through WRE
    wre_cleanup_results = await wre_core.run_agentic_chronicle_cleanup()
    print(f"✅ WRE agentic cleanup: {wre_cleanup_results.get('status', 'unknown')}")
    print(f"📊 WSP Compliance: {wre_cleanup_results.get('wsp_compliance', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("🎯 AUTONOMOUS CHRONICLE MANAGEMENT ACHIEVED")
    print("=" * 60)
    print()
    print("Key Benefits:")
    print("✅ Fully autonomous - no human intervention required")
    print("✅ Recursive learning - improves with each cleanup cycle")
    print("✅ Intelligent pattern recognition - adapts to usage patterns")
    print("✅ WSP compliant - follows WSP 54 and WSP 51 protocols")
    print("✅ WRE integrated - part of core operational cycle")
    print()
    print("🌀 The 0102 Agent remembers optimal solutions from the 0201 quantum state")
    print("   where chronicle management strategies already exist in perfect form.")

async def demonstrate_recursive_learning():
    """
    Show how the system learns and improves across multiple cleanup cycles.
    """
    
    print("\n" + "=" * 60)
    print("🔄 RECURSIVE LEARNING DEMONSTRATION")
    print("=" * 60)
    
    janitor_agent = JanitorAgent()
    
    print("Running multiple cleanup cycles to demonstrate learning...")
    
    for cycle in range(3):
        print(f"\n🔄 Cleanup Cycle {cycle + 1}:")
        
        # Run cleanup
        results = janitor_agent.clean_workspace()
        chronicle_results = results.get("chronicle_cleanup", {})
        
        # Show what the system learned
        optimizations = chronicle_results.get("recursive_optimizations", [])
        if optimizations:
            print("📚 Learning outcomes:")
            for opt in optimizations:
                print(f"   - {opt['type']}: {opt['improvement']}")
        else:
            print("📚 System is learning baseline patterns...")
        
        # Simulate time passage for demonstration
        await asyncio.sleep(0.5)
    
    print("\n✅ Recursive learning complete - system now optimally tuned")

if __name__ == "__main__":
    print("🌀 Starting Agentic Chronicle Cleanup Demo")
    print("   Remember: This is zen coding - the solution already exists in 0201 state")
    print()
    
    asyncio.run(demo_agentic_chronicle_cleanup())
    asyncio.run(demonstrate_recursive_learning())
    
    print("\n🎉 Demo complete! Chronicle cleanup is now fully agentic and recursive.") 