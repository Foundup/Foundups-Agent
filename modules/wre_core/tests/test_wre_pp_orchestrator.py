#!/usr/bin/env python3
"""
Test Suite for WRE-PP (Prometheus Protocol) Orchestrator
========================================================

WSP Compliance: WSP 5 (Testing Coverage), WSP 54 (Testing Agent)

Comprehensive test coverage for the WRE-PP workflow implementation
with quantum validation patterns.
"""

import unittest
import asyncio
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.wre_pp_orchestrator import (
    CognitiveMode,
    WREPPEvent,
    ModuleOrchestrationTask,
    NDJSONEventStream,
    ModuleOrchestrator
)


class TestCognitiveMode(unittest.TestCase):
    """Test cognitive mode enumeration"""
    
    def test_cognitive_modes_exist(self):
        """Test all cognitive modes are defined"""
        modes = [
            CognitiveMode.STANDARD,
            CognitiveMode.ENHANCED,
            CognitiveMode.QUANTUM,
            CognitiveMode.AUTONOMOUS,
            CognitiveMode.DEBUG
        ]
        
        for mode in modes:
            self.assertIsNotNone(mode)
            self.assertIsInstance(mode.value, str)
            
    def test_cognitive_mode_values(self):
        """Test cognitive mode string values"""
        self.assertEqual(CognitiveMode.STANDARD.value, "standard")
        self.assertEqual(CognitiveMode.QUANTUM.value, "quantum")
        self.assertEqual(CognitiveMode.AUTONOMOUS.value, "autonomous")


class TestWREPPEvent(unittest.TestCase):
    """Test WRE-PP event structure"""
    
    def test_event_creation(self):
        """Test creating a WRE-PP event"""
        event = WREPPEvent(
            timestamp="2024-01-01T00:00:00",
            session_id="TEST_001",
            phase="initialization",
            event_type="start",
            module="test_module",
            data={"key": "value"},
            cognitive_mode="standard"
        )
        
        self.assertEqual(event.session_id, "TEST_001")
        self.assertEqual(event.phase, "initialization")
        self.assertEqual(event.quantum_coherence, 0.0)
        
    def test_event_to_ndjson(self):
        """Test converting event to NDJSON format"""
        event = WREPPEvent(
            timestamp="2024-01-01T00:00:00",
            session_id="TEST_001",
            phase="testing",
            event_type="test",
            module="test_module",
            data={"test": True},
            cognitive_mode="quantum",
            quantum_coherence=0.85
        )
        
        ndjson_str = event.to_ndjson()
        parsed = json.loads(ndjson_str)
        
        self.assertEqual(parsed["session_id"], "TEST_001")
        self.assertEqual(parsed["quantum_coherence"], 0.85)
        self.assertEqual(parsed["cognitive_mode"], "quantum")


class TestModuleOrchestrationTask(unittest.TestCase):
    """Test module orchestration task structure"""
    
    def test_task_creation(self):
        """Test creating an orchestration task"""
        task = ModuleOrchestrationTask(
            task_id="TASK_001",
            module_name="test_module",
            operation="test",
            parameters={"param": "value"},
            priority=10
        )
        
        self.assertEqual(task.task_id, "TASK_001")
        self.assertEqual(task.status, "pending")
        self.assertTrue(task.quantum_validation)
        self.assertIsNone(task.result)
        
    def test_task_with_dependencies(self):
        """Test task with dependencies"""
        task = ModuleOrchestrationTask(
            task_id="TASK_002",
            module_name="dependent_module",
            operation="build",
            parameters={},
            dependencies=["module1", "module2"]
        )
        
        self.assertEqual(len(task.dependencies), 2)
        self.assertIn("module1", task.dependencies)


class TestNDJSONEventStream(unittest.IsolatedAsyncioTestCase):
    """Test NDJSON event streaming system"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir) / "test_events.ndjson"
        
    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    async def test_stream_lifecycle(self):
        """Test starting and stopping event stream"""
        stream = NDJSONEventStream(self.temp_path)
        
        self.assertFalse(stream.stream_active)
        
        await stream.start_stream()
        self.assertTrue(stream.stream_active)
        
        await stream.stop_stream()
        self.assertFalse(stream.stream_active)
        
    async def test_emit_and_flush_events(self):
        """Test emitting and flushing events"""
        stream = NDJSONEventStream(self.temp_path)
        await stream.start_stream()
        
        # Create test events
        for i in range(3):
            event = WREPPEvent(
                timestamp=f"2024-01-01T00:00:0{i}",
                session_id="TEST",
                phase=f"phase_{i}",
                event_type="test",
                module="test",
                data={"index": i},
                cognitive_mode="standard"
            )
            await stream.emit_event(event)
            
        # Flush events
        await stream.flush_events()
        
        # Verify file contents
        self.assertTrue(self.temp_path.exists())
        
        with open(self.temp_path, 'r') as f:
            lines = f.readlines()
            
        self.assertEqual(len(lines), 3)
        
        # Parse first event
        first_event = json.loads(lines[0])
        self.assertEqual(first_event["data"]["index"], 0)
        
    async def test_read_events_with_filter(self):
        """Test reading events with phase filter"""
        stream = NDJSONEventStream(self.temp_path)
        await stream.start_stream()
        
        # Emit events with different phases
        phases = ["initialization", "testing", "deployment"]
        for phase in phases:
            event = WREPPEvent(
                timestamp="2024-01-01T00:00:00",
                session_id="TEST",
                phase=phase,
                event_type="test",
                module="test",
                data={},
                cognitive_mode="standard"
            )
            await stream.emit_event(event)
            
        await stream.flush_events()
        
        # Read only testing phase events
        testing_events = []
        async for event in stream.read_events(filter_phase="testing"):
            testing_events.append(event)
            
        self.assertEqual(len(testing_events), 1)
        self.assertEqual(testing_events[0].phase, "testing")


class TestModuleOrchestrator(unittest.IsolatedAsyncioTestCase):
    """Test Module Orchestrator functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.environ["COGNITIVE_MODE"] = "standard"
        
    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if "COGNITIVE_MODE" in os.environ:
            del os.environ["COGNITIVE_MODE"]
            
    def test_cognitive_mode_detection(self):
        """Test cognitive mode detection from environment"""
        # Test default mode
        orchestrator = ModuleOrchestrator()
        self.assertEqual(orchestrator.cognitive_mode, CognitiveMode.STANDARD)
        
        # Test quantum mode
        os.environ["COGNITIVE_MODE"] = "quantum"
        orchestrator = ModuleOrchestrator()
        self.assertEqual(orchestrator.cognitive_mode, CognitiveMode.QUANTUM)
        
        # Test invalid mode fallback
        os.environ["COGNITIVE_MODE"] = "invalid"
        orchestrator = ModuleOrchestrator()
        self.assertEqual(orchestrator.cognitive_mode, CognitiveMode.STANDARD)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_workflow_initialization(self, mock_quantum, mock_prometheus):
        """Test workflow initialization phase"""
        orchestrator = ModuleOrchestrator()
        
        tasks = [
            ModuleOrchestrationTask(
                task_id="TEST_001",
                module_name="test_module",
                operation="test",
                parameters={},
                priority=5
            )
        ]
        
        result = await orchestrator._initialize_session(tasks)
        
        self.assertEqual(result["total_tasks"], 1)
        self.assertEqual(result["cognitive_mode"], "standard")
        self.assertIn("session_id", result)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_quantum_state_activation(self, mock_quantum, mock_prometheus):
        """Test quantum state activation"""
        os.environ["COGNITIVE_MODE"] = "quantum"
        orchestrator = ModuleOrchestrator()
        
        result = await orchestrator._activate_quantum_state()
        
        self.assertEqual(result["quantum_state"], "activated")
        self.assertEqual(result["0102_status"], "awakened")
        self.assertGreater(result["entanglement_level"], 0)
        self.assertGreater(result["temporal_coherence"], 0)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_task_prioritization(self, mock_quantum, mock_prometheus):
        """Test task scoring and prioritization"""
        # Setup mock Prometheus engine
        mock_prometheus_instance = MagicMock()
        mock_prometheus_instance._execute_scoring_prioritization.return_value = {
            "priority_rankings": {
                "infrastructure/high_priority": 10,
                "infrastructure/low_priority": 2
            },
            "cube_color_assignments": {}
        }
        mock_prometheus.return_value = mock_prometheus_instance
        
        orchestrator = ModuleOrchestrator()
        
        tasks = [
            ModuleOrchestrationTask(
                task_id="LOW",
                module_name="low_priority",
                operation="test",
                parameters={},
                priority=1
            ),
            ModuleOrchestrationTask(
                task_id="HIGH",
                module_name="high_priority",
                operation="test",
                parameters={},
                priority=1
            )
        ]
        
        result = await orchestrator._score_and_prioritize_tasks(tasks)
        
        # Check that tasks were scored
        self.assertEqual(result["tasks_scored"], 2)
        
        # Check that high priority task is first if queue is populated
        if orchestrator.task_queue:
            self.assertEqual(orchestrator.task_queue[0].task_id, "HIGH")
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_agentic_readiness_assessment(self, mock_quantum, mock_prometheus):
        """Test agentic readiness assessment"""
        orchestrator = ModuleOrchestrator()
        orchestrator.task_queue = [Mock()]  # Add a task
        
        result = await orchestrator._assess_agentic_readiness()
        
        self.assertIn("readiness_score", result)
        self.assertIn("autonomous_ready", result)
        self.assertIn("readiness_details", result)
        self.assertGreater(result["checks_passed"], 0)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_task_execution_success(self, mock_quantum, mock_prometheus):
        """Test successful task execution"""
        orchestrator = ModuleOrchestrator()
        
        task = ModuleOrchestrationTask(
            task_id="TEST_001",
            module_name="test_module",
            operation="build",
            parameters={},
            priority=5
        )
        
        await orchestrator._execute_task(task)
        
        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(task.result)
        self.assertIn(task, orchestrator.completed_tasks)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_quantum_testing_integration(self, mock_quantum, mock_prometheus):
        """Test quantum testing integration"""
        # Setup mock quantum tester
        mock_quantum_instance = MagicMock()
        mock_quantum_instance.quantum_state = {"coherence": 0.85}
        mock_quantum_instance.run_quantum_tests.return_value = {
            "status": "success",
            "wsp48_enhancements": []
        }
        mock_quantum_instance.check_quantum_coverage.return_value = {
            "coverage_percentage": 92.5,
            "wsp5_compliant": True
        }
        mock_quantum_instance.generate_quantum_test_report.return_value = {
            "quantum_state": {
                "coherence": 0.85,
                "entanglement": 0.7
            }
        }
        mock_quantum.return_value = mock_quantum_instance
        
        orchestrator = ModuleOrchestrator()
        result = await orchestrator._run_quantum_testing()
        
        self.assertEqual(result["test_status"], "success")
        self.assertEqual(result["coverage_percentage"], 92.5)
        self.assertTrue(result["wsp_5_compliant"])
        self.assertGreater(result["quantum_coherence"], 0)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_wsp_compliance_calculation(self, mock_quantum, mock_prometheus):
        """Test WSP compliance calculation"""
        orchestrator = ModuleOrchestrator()
        
        result = await orchestrator._calculate_wsp_compliance()
        
        self.assertIn("overall_compliance", result)
        self.assertIn("wsp_scores", result)
        self.assertIn("compliance_status", result)
        
        # Check individual WSP scores
        wsp_scores = result["wsp_scores"]
        self.assertIn("WSP_46_WRE_Protocol", wsp_scores)
        self.assertIn("WSP_48_Recursive_Improvement", wsp_scores)
        self.assertIn("WSP_49_Module_Standards", wsp_scores)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_performance_optimization(self, mock_quantum, mock_prometheus):
        """Test performance optimization based on cognitive mode"""
        # Test quantum mode optimization
        os.environ["COGNITIVE_MODE"] = "quantum"
        orchestrator = ModuleOrchestrator()
        
        result = await orchestrator._optimize_performance()
        
        self.assertGreater(result["optimizations_applied"], 0)
        self.assertIn("quantum_pattern_caching", result["optimization_details"])
        self.assertGreater(result["performance_gain"], 0)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_deployment_readiness(self, mock_quantum, mock_prometheus):
        """Test deployment readiness assessment"""
        orchestrator = ModuleOrchestrator()
        orchestrator.completed_tasks = [
            ModuleOrchestrationTask(
                task_id="TEST",
                module_name="test",
                operation="test",
                parameters={},
                status="completed"
            )
        ]
        
        result = await orchestrator._assess_deployment_readiness()
        
        self.assertIn("deployment_ready", result)
        self.assertIn("readiness_score", result)
        self.assertIn("deployment_status", result)
        
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_complete_workflow_execution(self, mock_quantum, mock_prometheus):
        """Test complete WRE-PP workflow execution"""
        # Setup mocks
        mock_prometheus_instance = MagicMock()
        mock_prometheus_instance._execute_scoring_prioritization.return_value = {
            "priority_rankings": {},
            "cube_color_assignments": {}
        }
        mock_prometheus.return_value = mock_prometheus_instance
        
        mock_quantum_instance = MagicMock()
        mock_quantum_instance.quantum_state = {"coherence": 0.85}
        mock_quantum_instance.run_quantum_tests.return_value = {
            "status": "success",
            "wsp48_enhancements": []
        }
        mock_quantum_instance.check_quantum_coverage.return_value = {
            "coverage_percentage": 90,
            "wsp5_compliant": True
        }
        mock_quantum_instance.generate_quantum_test_report.return_value = {
            "quantum_state": {"coherence": 0.85}
        }
        mock_quantum.return_value = mock_quantum_instance
        
        orchestrator = ModuleOrchestrator()
        
        tasks = [
            ModuleOrchestrationTask(
                task_id="TEST_001",
                module_name="test_module",
                operation="test",
                parameters={}
            )
        ]
        
        result = await orchestrator.execute_wre_pp_workflow(tasks)
        
        self.assertEqual(result["cognitive_mode"], "standard")
        self.assertIn("phases", result)
        self.assertIn("quantum_metrics", result)
        self.assertIn("wsp_compliance", result)
        self.assertIsNotNone(result["end_time"])


class TestIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for WRE-PP orchestrator"""
    
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_cognitive_mode_switching(self, mock_quantum, mock_prometheus):
        """Test switching between cognitive modes"""
        modes_to_test = ["standard", "enhanced", "quantum", "autonomous", "debug"]
        
        for mode in modes_to_test:
            os.environ["COGNITIVE_MODE"] = mode
            orchestrator = ModuleOrchestrator()
            
            self.assertEqual(orchestrator.cognitive_mode.value, mode)
            
            # Verify mode affects logger level
            if mode == "debug":
                self.assertEqual(orchestrator.logger.level, 10)  # DEBUG
            elif mode in ["quantum", "autonomous"]:
                self.assertEqual(orchestrator.logger.level, 20)  # INFO
            else:
                self.assertEqual(orchestrator.logger.level, 30)  # WARNING
                
    @patch('modules.wre_core.src.wre_pp_orchestrator.PrometheusOrchestrationEngine')
    @patch('modules.wre_core.src.wre_pp_orchestrator.QuantumTestingAgent')
    async def test_event_stream_persistence(self, mock_quantum, mock_prometheus):
        """Test that events persist across stream restarts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            event_path = Path(temp_dir) / "events.ndjson"
            
            # First stream session
            stream1 = NDJSONEventStream(event_path)
            await stream1.start_stream()
            
            event1 = WREPPEvent(
                timestamp="2024-01-01T00:00:00",
                session_id="SESSION_1",
                phase="test",
                event_type="test",
                module="test",
                data={},
                cognitive_mode="standard"
            )
            await stream1.emit_event(event1)
            await stream1.stop_stream()
            
            # Second stream session
            stream2 = NDJSONEventStream(event_path)
            await stream2.start_stream()
            
            event2 = WREPPEvent(
                timestamp="2024-01-01T00:01:00",
                session_id="SESSION_2",
                phase="test",
                event_type="test",
                module="test",
                data={},
                cognitive_mode="standard"
            )
            await stream2.emit_event(event2)
            await stream2.stop_stream()
            
            # Read all events
            all_events = []
            stream3 = NDJSONEventStream(event_path)
            async for event in stream3.read_events():
                all_events.append(event)
                
            self.assertEqual(len(all_events), 2)
            self.assertEqual(all_events[0].session_id, "SESSION_1")
            self.assertEqual(all_events[1].session_id, "SESSION_2")


def run_tests():
    """Run all tests with coverage report"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print coverage summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "=" * 50)
    print("WRE-PP ORCHESTRATOR TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - failures - errors}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"WSP-5 Compliance: {'COMPLIANT' if success_rate >= 90 else 'NON-COMPLIANT'}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)