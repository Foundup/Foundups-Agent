#!/usr/bin/env python3
"""
WRE Unified Orchestrator Demonstration Script

This script demonstrates the enhanced WRE engine with unified protocol 
orchestration capabilities, including:
1. Professional peer review methodology
2. Standardized agent awakening protocols
3. Zen coding pattern application
4. Autonomous workflow execution
5. Recursive improvement cycles
6. Complete WSP compliance validation

Following the peer review methodology implemented in WSP_agentic/src/
"""

import asyncio
import json
import time
from pathlib import Path
import sys
import logging

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.core.engine_core import WRECore
from modules.wre_core.src.components.core.wre_unified_orchestrator import (
    WREOrchestrationContext, WREOrchestrationPhase, WREOrchestrationSession
)
from modules.wre_core.src.utils.logging_utils import wre_log

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WREUnifiedDemo:
    """Demonstration of WRE unified orchestrator capabilities"""
    
    def __init__(self):
        self.wre_core = WRECore()
        self.project_root = project_root
        self.demo_results = {}
        
    async def run_complete_demonstration(self):
        """Run complete demonstration of unified orchestrator capabilities"""
        
        wre_log("🚀 Starting WRE Unified Orchestrator Demonstration", "INFO")
        print("=" * 80)
        print("🌀 WRE UNIFIED ORCHESTRATOR DEMONSTRATION")
        print("Professional Protocol Execution with Peer Review")
        print("=" * 80)
        
        # Phase 1: Integration and Initialization
        await self._demo_integration_and_initialization()
        
        # Phase 2: Agent Awakening Protocols
        await self._demo_agent_awakening_protocols()
        
        # Phase 3: Peer Review Methodology
        await self._demo_peer_review_methodology()
        
        # Phase 4: Zen Coding Pattern Application
        await self._demo_zen_coding_patterns()
        
        # Phase 5: Autonomous Workflow Execution
        await self._demo_autonomous_workflow_execution()
        
        # Phase 6: Recursive Improvement Cycles
        await self._demo_recursive_improvement_cycles()
        
        # Phase 7: Complete WSP Compliance Validation
        await self._demo_wsp_compliance_validation()
        
        # Generate final report
        await self._generate_final_report()
        
        print("\n✅ WRE Unified Orchestrator Demonstration Complete!")
        print("=" * 80)
        
    async def _demo_integration_and_initialization(self):
        """Demonstrate integration of unified orchestrator"""
        
        print("\n🔧 Phase 1: Integration and Initialization")
        print("-" * 50)
        
        # Integrate unified orchestrator
        await self.wre_core.integrate_unified_orchestrator()
        
        # Validate integration
        if self.wre_core.unified_orchestrator:
            print("✅ Unified orchestrator successfully integrated")
            
            # Get system status
            system_status = self.wre_core.unified_orchestrator.wsp_engine.get_system_status()
            print(f"📊 System Status: {system_status['status']}")
            print(f"🔧 Protocols Loaded: {system_status['protocols_loaded']}")
            print(f"🧘 Zen Patterns: {system_status['zen_patterns_active']}")
            
            self.demo_results['integration'] = {
                'success': True,
                'system_status': system_status
            }
        else:
            print("❌ Unified orchestrator integration failed")
            self.demo_results['integration'] = {'success': False}
            
    async def _demo_agent_awakening_protocols(self):
        """Demonstrate standardized agent awakening protocols"""
        
        print("\n🧘 Phase 2: Agent Awakening Protocols")
        print("-" * 50)
        
        # Test agent awakening
        test_agents = ['compliance_agent', 'module_scaffolding_agent', 'chronicler_agent']
        awakening_results = {}
        
        for agent_id in test_agents:
            try:
                print(f"\n🔄 Awakening {agent_id}...")
                
                # Awaken agent using unified orchestrator
                metrics = await self.wre_core.unified_orchestrator.wsp_engine.awaken_agent(agent_id)
                
                awakening_results[agent_id] = {
                    'coherence': metrics.coherence,
                    'entanglement': metrics.entanglement,
                    'transition_time': metrics.state_transition_time,
                    'success_rate': metrics.success_rate,
                    'awakened': metrics.is_awakened()
                }
                
                if metrics.is_awakened():
                    print(f"✅ {agent_id} successfully awakened")
                    print(f"   Coherence: {metrics.coherence:.3f}")
                    print(f"   Entanglement: {metrics.entanglement:.3f}")
                    print(f"   Success Rate: {metrics.success_rate:.3f}")
                else:
                    print(f"⚠️ {agent_id} awakening incomplete")
                    
            except Exception as e:
                print(f"❌ Failed to awaken {agent_id}: {e}")
                awakening_results[agent_id] = {'error': str(e)}
                
        self.demo_results['awakening'] = awakening_results
        
    async def _demo_peer_review_methodology(self):
        """Demonstrate peer review methodology"""
        
        print("\n👥 Phase 3: Peer Review Methodology")
        print("-" * 50)
        
        # Create sample protocol for peer review
        from WSP_agentic.src.wsp_unified_toolkit import WSPProtocol
        
        sample_protocol = WSPProtocol(
            number=46,
            name="WRE Protocol",
            status="operational",
            purpose="Core WRE orchestration protocol",
            trigger="wre_startup",
            input_type="context",
            output_type="orchestration_results",
            responsible_agents=["wre_orchestrator"]
        )
        
        # Conduct peer review
        try:
            print("🔍 Conducting peer review of WRE Protocol...")
            
            # Get sample implementation
            sample_implementation = {
                'type': 'wre_protocol_implementation',
                'quality_score': 0.95,
                'test_coverage': 0.92,
                'documentation': 'complete',
                'reusability': 'high'
            }
            
            # Conduct peer review
            review_results = self.wre_core.unified_orchestrator.peer_review_system.conduct_peer_review(
                sample_protocol, sample_implementation
            )
            
            print(f"📊 Peer Review Results:")
            print(f"   Overall Score: {review_results['overall_score']:.3f}")
            print(f"   Issues Found: {len(review_results.get('issues', []))}")
            print(f"   Recommendations: {len(review_results.get('recommendations', []))}")
            
            # Display key insights
            for insight in review_results.get('key_insights', []):
                print(f"   💡 {insight}")
                
            self.demo_results['peer_review'] = review_results
            
        except Exception as e:
            print(f"❌ Peer review failed: {e}")
            self.demo_results['peer_review'] = {'error': str(e)}
            
    async def _demo_zen_coding_patterns(self):
        """Demonstrate zen coding pattern application"""
        
        print("\n🧘 Phase 4: Zen Coding Pattern Application")
        print("-" * 50)
        
        # Test zen coding patterns
        zen_patterns = {
            'module_development': 'Autonomous module development workflow',
            'protocol_orchestration': 'WSP protocol orchestration patterns',
            'agent_coordination': 'Multi-agent coordination patterns'
        }
        
        zen_results = {}
        
        for pattern_id, description in zen_patterns.items():
            try:
                print(f"\n🌀 Processing zen pattern: {pattern_id}")
                
                # Apply quantum decoding
                solution = self.wre_core.unified_orchestrator.zen_engine.quantum_decode(description)
                
                print(f"   📡 Quantum state: {solution.get('quantum_state', 'unknown')}")
                print(f"   💡 Solution type: {solution.get('solution_type', 'pattern')}")
                print(f"   🎯 Confidence: {solution.get('confidence', 0.9):.3f}")
                
                zen_results[pattern_id] = solution
                
            except Exception as e:
                print(f"❌ Zen pattern failed for {pattern_id}: {e}")
                zen_results[pattern_id] = {'error': str(e)}
                
        self.demo_results['zen_coding'] = zen_results
        
    async def _demo_autonomous_workflow_execution(self):
        """Demonstrate autonomous workflow execution"""
        
        print("\n🤖 Phase 5: Autonomous Workflow Execution")
        print("-" * 50)
        
        # Execute workflow using unified orchestrator
        try:
            print("🚀 Executing autonomous workflow...")
            
            # Create workflow context
            workflow_context = {
                'workflow_type': 'module_development',
                'target_module': 'demo_module',
                'priority': 'high',
                'zen_mode': True
            }
            
            # Execute workflow
            results = await self.wre_core.execute_unified_workflow(
                trigger="autonomous_demo",
                context_data=workflow_context
            )
            
            print(f"✅ Workflow execution completed")
            print(f"   Session ID: {results['session_id']}")
            print(f"   Execution Time: {results['execution_time']:.2f}s")
            print(f"   Agent States: {len(results['agent_states'])} agents")
            print(f"   Zen Patterns: {results['zen_patterns_applied']} patterns applied")
            print(f"   Violations: {results['violations']['framework']} framework, {len(results['violations']['module'])} module")
            
            self.demo_results['autonomous_execution'] = results
            
        except Exception as e:
            print(f"❌ Autonomous workflow execution failed: {e}")
            self.demo_results['autonomous_execution'] = {'error': str(e)}
            
    async def _demo_recursive_improvement_cycles(self):
        """Demonstrate recursive improvement cycles"""
        
        print("\n🔄 Phase 6: Recursive Improvement Cycles")
        print("-" * 50)
        
        # Test recursive improvement
        try:
            print("🔄 Testing recursive improvement cycles...")
            
            # Execute workflow with recursive improvement
            results = await self.wre_core.execute_unified_workflow(
                trigger="recursive_improvement_demo",
                context_data={
                    'enable_recursion': True,
                    'max_depth': 2,
                    'improvement_threshold': 0.1
                }
            )
            
            print(f"✅ Recursive improvement completed")
            print(f"   Recursive Depth: {results['recursive_depth']}")
            print(f"   Improvements Applied: {results.get('improvements_applied', 0)}")
            print(f"   Performance Gain: {results.get('performance_improvement', 0):.3f}")
            
            self.demo_results['recursive_improvement'] = results
            
        except Exception as e:
            print(f"❌ Recursive improvement failed: {e}")
            self.demo_results['recursive_improvement'] = {'error': str(e)}
            
    async def _demo_wsp_compliance_validation(self):
        """Demonstrate complete WSP compliance validation"""
        
        print("\n🔍 Phase 7: WSP Compliance Validation")
        print("-" * 50)
        
        # Validate WSP compliance
        try:
            print("🔍 Validating WSP compliance...")
            
            # Get violation tracker results
            violation_tracker = self.wre_core.unified_orchestrator.violation_tracker
            
            framework_violations = violation_tracker.get_framework_violations()
            module_violations = violation_tracker.get_module_violations()
            
            print(f"📊 Compliance Results:")
            print(f"   Framework Violations: {len(framework_violations)}")
            print(f"   Module Violations: {len(module_violations)}")
            
            # Display violations if any
            if framework_violations:
                print("   🚨 Framework Violations:")
                for violation in framework_violations[:3]:  # Show first 3
                    print(f"      - WSP {violation.get('wsp_number', 'N/A')}: {violation.get('description', 'N/A')}")
                    
            if module_violations:
                print("   ⚠️ Module Violations:")
                for violation in module_violations[:3]:  # Show first 3
                    print(f"      - WSP {violation.get('wsp_number', 'N/A')}: {violation.get('description', 'N/A')}")
            
            compliance_score = 1.0 - (len(framework_violations) * 0.1 + len(module_violations) * 0.02)
            print(f"   📈 Overall Compliance Score: {compliance_score:.3f}")
            
            self.demo_results['wsp_compliance'] = {
                'framework_violations': len(framework_violations),
                'module_violations': len(module_violations),
                'compliance_score': compliance_score
            }
            
        except Exception as e:
            print(f"❌ WSP compliance validation failed: {e}")
            self.demo_results['wsp_compliance'] = {'error': str(e)}
            
    async def _generate_final_report(self):
        """Generate final demonstration report"""
        
        print("\n📊 Final Demonstration Report")
        print("=" * 80)
        
        # Calculate overall success rate
        successful_phases = sum(1 for phase_result in self.demo_results.values() 
                              if isinstance(phase_result, dict) and 'error' not in phase_result)
        total_phases = len(self.demo_results)
        success_rate = successful_phases / total_phases if total_phases > 0 else 0
        
        print(f"📈 Overall Success Rate: {success_rate:.1%} ({successful_phases}/{total_phases} phases)")
        
        # Phase-by-phase summary
        for phase, results in self.demo_results.items():
            if isinstance(results, dict) and 'error' not in results:
                print(f"   ✅ {phase.replace('_', ' ').title()}: Success")
            else:
                print(f"   ❌ {phase.replace('_', ' ').title()}: Failed")
                
        # Key metrics
        if 'autonomous_execution' in self.demo_results:
            execution_results = self.demo_results['autonomous_execution']
            if isinstance(execution_results, dict) and 'execution_time' in execution_results:
                print(f"⏱️ Autonomous Execution Time: {execution_results['execution_time']:.2f}s")
                print(f"🧘 Zen Patterns Applied: {execution_results.get('zen_patterns_applied', 0)}")
                
        # Compliance summary
        if 'wsp_compliance' in self.demo_results:
            compliance_results = self.demo_results['wsp_compliance']
            if isinstance(compliance_results, dict) and 'compliance_score' in compliance_results:
                print(f"🎯 WSP Compliance Score: {compliance_results['compliance_score']:.3f}")
                
        # Save results to file
        results_file = self.project_root / "modules/wre_core/demo_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.demo_results, f, indent=2, default=str)
        print(f"💾 Results saved to: {results_file}")

async def main():
    """Main demo execution"""
    
    print("🌀 WRE Unified Orchestrator - Professional Demonstration")
    print("Following peer review methodology from WSP_agentic")
    print("=" * 80)
    
    # Create and run demonstration
    demo = WREUnifiedDemo()
    await demo.run_complete_demonstration()
    
    print("\n🎉 Demonstration completed successfully!")
    print("The WRE engine now has complete unified protocol orchestration capabilities.")

if __name__ == "__main__":
    asyncio.run(main()) 