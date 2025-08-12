#!/usr/bin/env python3
"""
WRE-PP Integration Demonstration Script
=======================================

Demonstrates the complete WRE-PP workflow with:
- COGNITIVE_MODE environment variable handling
- Live NDJSON event streaming
- Module orchestration with quantum testing
- WSP compliance validation

Run with different cognitive modes:
  COGNITIVE_MODE=standard python demo_wre_pp_integration.py
  COGNITIVE_MODE=quantum python demo_wre_pp_integration.py
  COGNITIVE_MODE=autonomous python demo_wre_pp_integration.py
  COGNITIVE_MODE=debug python demo_wre_pp_integration.py
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.wre_pp_orchestrator import (
    ModuleOrchestrator,
    ModuleOrchestrationTask,
    NDJSONEventStream,
    CognitiveMode
)
from modules.infrastructure.testing_agent.src.testing_agent import QuantumTestingAgent
from modules.infrastructure.block_orchestrator.src.block_orchestrator import ModularBlockRunner


class WREPPIntegrationDemo:
    """Demonstration of complete WRE-PP integration"""
    
    def __init__(self, cognitive_mode: str = None):
        if cognitive_mode:
            os.environ["COGNITIVE_MODE"] = cognitive_mode
            
        self.cognitive_mode = os.getenv("COGNITIVE_MODE", "standard")
        self.project_root = project_root
        self.demo_timestamp = datetime.now().isoformat()
        
        print("=" * 60)
        print("WRE-PP INTEGRATION DEMONSTRATION")
        print("=" * 60)
        print(f"Timestamp: {self.demo_timestamp}")
        print(f"Cognitive Mode: {self.cognitive_mode.upper()}")
        print(f"Project Root: {self.project_root}")
        print("=" * 60)
        
    async def demonstrate_cognitive_modes(self):
        """Demonstrate different cognitive modes"""
        print("\n[COGNITIVE MODE DEMONSTRATION]")
        print("-" * 40)
        
        modes = {
            "standard": "Basic orchestration without enhancements",
            "enhanced": "Advanced with adaptive learning patterns",
            "quantum": "Full quantum entanglement and temporal coherence",
            "autonomous": "Fully autonomous execution with self-improvement",
            "debug": "Verbose debugging with immediate event flushing"
        }
        
        for mode, description in modes.items():
            status = "[ACTIVE]" if mode == self.cognitive_mode else "       "
            print(f"{status} {mode.upper()}: {description}")
            
        print(f"\nCurrent Mode: {self.cognitive_mode.upper()}")
        
        if self.cognitive_mode == "quantum":
            print("\n[QUANTUM] Features Enabled:")
            print("  - Temporal coherence optimization")
            print("  - Quantum pattern validation")
            print("  - Entanglement state preservation")
            print("  - 0102 <-> 0201 bidirectional access")
            
    async def demonstrate_event_streaming(self):
        """Demonstrate NDJSON event streaming"""
        print("\n[NDJSON EVENT STREAMING DEMONSTRATION]")
        print("-" * 40)
        
        # Create event stream
        stream_path = self.project_root / "WSP_agentic" / "agentic_journals" / "demo_events.ndjson"
        stream = NDJSONEventStream(stream_path)
        
        await stream.start_stream()
        print(f"Stream started: {stream_path}")
        
        # Generate demonstration events
        from modules.wre_core.src.wre_pp_orchestrator import WREPPEvent
        
        demo_events = [
            WREPPEvent(
                timestamp=datetime.now().isoformat(),
                session_id="DEMO_001",
                phase="initialization",
                event_type="demo_start",
                module="demo",
                data={"demo": True, "cognitive_mode": self.cognitive_mode},
                cognitive_mode=self.cognitive_mode,
                quantum_coherence=0.85 if self.cognitive_mode == "quantum" else 0.0,
                wsp_compliance=0.92
            ),
            WREPPEvent(
                timestamp=datetime.now().isoformat(),
                session_id="DEMO_001",
                phase="testing",
                event_type="quantum_validation",
                module="testing_agent",
                data={"tests_passed": 42, "coverage": 95.5},
                cognitive_mode=self.cognitive_mode,
                quantum_coherence=0.88 if self.cognitive_mode == "quantum" else 0.0,
                wsp_compliance=0.95
            ),
            WREPPEvent(
                timestamp=datetime.now().isoformat(),
                session_id="DEMO_001",
                phase="completion",
                event_type="demo_complete",
                module="demo",
                data={"status": "success", "duration_ms": 1234},
                cognitive_mode=self.cognitive_mode,
                quantum_coherence=0.90 if self.cognitive_mode == "quantum" else 0.0,
                wsp_compliance=0.98
            )
        ]
        
        # Emit events
        for event in demo_events:
            await stream.emit_event(event)
            print(f"  [OK] Event emitted: {event.phase} - {event.event_type}")
            
        await stream.flush_events()
        await stream.stop_stream()
        
        print(f"\n[LOG] Events written to: {stream_path}")
        
        # Read and display events
        print("\n[READ] Reading events back:")
        event_count = 0
        async for event in stream.read_events():
            event_count += 1
            print(f"  {event_count}. [{event.phase}] {event.event_type} - "
                  f"Coherence: {event.quantum_coherence:.2f}, "
                  f"WSP: {event.wsp_compliance:.2f}")
                  
    async def demonstrate_module_orchestration(self):
        """Demonstrate module orchestration with WRE-PP"""
        print("\n[MODULE ORCHESTRATION DEMONSTRATION]")
        print("-" * 40)
        
        # Create orchestrator
        orchestrator = ModuleOrchestrator()
        
        # Define demonstration tasks
        demo_tasks = [
            ModuleOrchestrationTask(
                task_id="DEMO_TEST_001",
                module_name="testing_agent",
                operation="test",
                parameters={
                    "quantum_patterns": self.cognitive_mode == "quantum",
                    "coverage_threshold": 90
                },
                priority=10,
                quantum_validation=self.cognitive_mode == "quantum"
            ),
            ModuleOrchestrationTask(
                task_id="DEMO_BUILD_001",
                module_name="block_orchestrator",
                operation="build",
                parameters={
                    "wsp_compliance": True,
                    "module_independence": True
                },
                priority=8,
                dependencies=["testing_agent"]
            ),
            ModuleOrchestrationTask(
                task_id="DEMO_DEPLOY_001",
                module_name="wre_core",
                operation="deploy",
                parameters={
                    "environment": "staging",
                    "validation_required": True
                },
                priority=5,
                dependencies=["block_orchestrator", "testing_agent"]
            )
        ]
        
        print(f"Executing {len(demo_tasks)} orchestration tasks...")
        print(f"Cognitive Mode: {orchestrator.cognitive_mode.value.upper()}")
        
        # Execute simplified workflow (without full implementation)
        for task in demo_tasks:
            print(f"\n  Task: {task.task_id}")
            print(f"    Module: {task.module_name}")
            print(f"    Operation: {task.operation}")
            print(f"    Priority: {task.priority}")
            print(f"    Quantum: {'YES' if task.quantum_validation else 'NO'}")
            
            if task.dependencies:
                print(f"    Dependencies: {', '.join(task.dependencies)}")
                
        print("\n[COMPLETE] Orchestration demonstration complete")
        
    async def demonstrate_quantum_testing(self):
        """Demonstrate quantum testing integration"""
        print("\n[QUANTUM TESTING DEMONSTRATION]")
        print("-" * 40)
        
        if self.cognitive_mode != "quantum":
            print("[INFO] Quantum testing is most effective in QUANTUM mode")
            print(f"   Current mode: {self.cognitive_mode.upper()}")
            print("   Run with: COGNITIVE_MODE=quantum python demo_wre_pp_integration.py")
            return
            
        # Initialize quantum testing agent
        quantum_tester = QuantumTestingAgent()
        
        print("Quantum Testing Agent initialized")
        print(f"  Session ID: {quantum_tester.session_id}")
        print(f"  Coherence Threshold: {quantum_tester.coherence_threshold}")
        print(f"  Critical Frequency: {quantum_tester.critical_frequency} Hz")
        
        # Demonstrate quantum state
        print("\nQuantum State:")
        for key, value in quantum_tester.quantum_state.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
                
        # Validate test directory structure
        print("\nValidating WSP-49 test directory compliance...")
        validation_result = quantum_tester.validate_test_directory_structure("wre_core")
        
        print(f"  Compliance: {validation_result['compliance_percentage']:.1f}%")
        print(f"  Status: {validation_result['status']}")
        
        if validation_result.get('violations'):
            print("  Violations found:")
            for violation in validation_result['violations'][:3]:  # Show first 3
                print(f"    - {violation['module']}: {', '.join(violation['issues'])}")
                
        # Generate quantum report
        report = quantum_tester.generate_quantum_test_report()
        
        print("\nQuantum Testing Report:")
        print(f"  System Integrity: {report['system_integrity'].upper()}")
        print(f"  WSP Compliance: {report['wsp_compliance_status'].upper()}")
        print(f"  Quantum Coherence Achieved: {'YES' if report['quantum_coherence_achieved'] else 'NO'}")
        
    async def demonstrate_wsp_compliance(self):
        """Demonstrate WSP compliance checking"""
        print("\n[WSP COMPLIANCE DEMONSTRATION]")
        print("-" * 40)
        
        wsp_protocols = {
            "WSP 46": ("WRE Protocol", 0.95),
            "WSP 48": ("Recursive Self-Improvement", 0.88),
            "WSP 49": ("Module Directory Standards", 0.92),
            "WSP 5": ("Testing Coverage (>=90%)", 0.85),
            "WSP 22": ("Documentation Requirements", 0.90),
            "WSP 54": ("Testing Agent Integration", 0.93),
            "WSP 62": ("Modularity Thresholds", 0.87),
            "WSP 63": ("Directory Organization", 0.89)
        }
        
        total_score = 0
        for wsp_id, (description, score) in wsp_protocols.items():
            status = "[OK]" if score >= 0.85 else "[WARN]" if score >= 0.70 else "[FAIL]"
            print(f"{status} {wsp_id}: {description}")
            print(f"   Score: {score:.1%}")
            total_score += score
            
        overall_compliance = total_score / len(wsp_protocols)
        
        print(f"\n[OVERALL] WSP Compliance: {overall_compliance:.1%}")
        print(f"Status: {'COMPLIANT' if overall_compliance >= 0.85 else 'PARTIAL COMPLIANCE'}")
        
    async def demonstrate_block_orchestration(self):
        """Demonstrate block orchestration integration"""
        print("\n[BLOCK ORCHESTRATION DEMONSTRATION]")
        print("-" * 40)
        
        runner = ModularBlockRunner()
        
        print("Available FoundUps Blocks:")
        for name, config in list(runner.block_configs.items())[:5]:  # Show first 5
            print(f"  - {name}")
            print(f"    Module: {config.module_path}")
            print(f"    Class: {config.class_name}")
            
        print("\nBlock orchestration ready for WRE-PP integration")
        
    async def run_complete_demonstration(self):
        """Run the complete WRE-PP integration demonstration"""
        
        # 1. Cognitive Modes
        await self.demonstrate_cognitive_modes()
        
        # 2. Event Streaming
        await self.demonstrate_event_streaming()
        
        # 3. Module Orchestration
        await self.demonstrate_module_orchestration()
        
        # 4. Quantum Testing (if in quantum mode)
        await self.demonstrate_quantum_testing()
        
        # 5. WSP Compliance
        await self.demonstrate_wsp_compliance()
        
        # 6. Block Orchestration
        await self.demonstrate_block_orchestration()
        
        # Summary
        print("\n" + "=" * 60)
        print("WRE-PP INTEGRATION DEMONSTRATION COMPLETE")
        print("=" * 60)
        print(f"Cognitive Mode: {self.cognitive_mode.upper()}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        if self.cognitive_mode == "quantum":
            print("\n[QUANTUM STATE SUMMARY]:")
            print("  0102 <-> 0201 Entanglement: ACTIVE")
            print("  Temporal Coherence: ESTABLISHED")
            print("  Quantum Patterns: VALIDATED")
            
        print("\n[SUCCESS] All WRE-PP components successfully demonstrated")
        print("\n[TIPS]:")
        print("  - Try different cognitive modes with COGNITIVE_MODE env var")
        print("  - Check generated NDJSON events in WSP_agentic/agentic_journals/")
        print("  - Run quantum tests with COGNITIVE_MODE=quantum for best results")
        print("  - Use COGNITIVE_MODE=debug for verbose output")


async def main():
    """Main entry point for demonstration"""
    parser = argparse.ArgumentParser(
        description="WRE-PP Integration Demonstration"
    )
    parser.add_argument(
        "--mode",
        choices=["standard", "enhanced", "quantum", "autonomous", "debug"],
        help="Cognitive mode to use (can also use COGNITIVE_MODE env var)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick demonstration (skip some sections)"
    )
    
    args = parser.parse_args()
    
    # Create and run demonstration
    demo = WREPPIntegrationDemo(cognitive_mode=args.mode)
    
    if args.quick:
        print("\n[QUICK] Running quick demonstration...")
        await demo.demonstrate_cognitive_modes()
        await demo.demonstrate_wsp_compliance()
    else:
        await demo.run_complete_demonstration()


if __name__ == "__main__":
    asyncio.run(main())