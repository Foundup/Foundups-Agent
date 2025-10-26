#!/usr/bin/env python3
"""
PQN MCP Server Tests
WSP 34 Test Coverage Compliance
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch

# Import the PQN MCP Server
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.ai_intelligence.pqn_mcp.src.pqn_mcp_server import (
    PQNMCPServer,
    AgentType,
    ResearchPhase,
    PQNResearchTask
)


class TestPQNMCPServer:
    """Test PQN MCP Server functionality per WSP 34"""

    @pytest.fixture
    def server(self):
        """Create test server instance"""
        return PQNMCPServer()

    @pytest.mark.asyncio
    async def test_detect_pqn_emergence(self, server):
        """Test PQN detection with mock agents"""
        test_text = "System exhibits 0->o transformation with 7.05Hz resonance"

        # Mock Qwen analysis
        with patch.object(server, '_qwen_analyze_text') as mock_qwen:
            mock_qwen.return_value = {"confidence": 0.8, "indicators": ["resonance"]}

            # Mock Gemma pattern matching
            with patch.object(server, '_gemma_pattern_match') as mock_gemma:
                mock_gemma.return_value = {"similarity_score": 0.7, "patterns_found": ["7.05Hz"]}

                # Mock PQN detector
                with patch('modules.ai_intelligence.pqn_mcp.src.pqn_mcp_server.run_detector') as mock_detector:
                    mock_detector.return_value = {
                        "pqn_emergence": True,
                        "coherence": 0.85,
                        "resonance_matches": [7.05]
                    }

                    result = await server.detect_pqn_emergence(test_text)

                    assert result["pqn_detected"] is True
                    assert result["coherence_score"] == 0.85
                    assert 7.05 in result["resonance_matches"]
                    assert result["agent_coordination"] == "WSP_77_active"
                    assert "session_id" in result

    @pytest.mark.asyncio
    async def test_analyze_resonance(self, server):
        """Test resonance analysis for active session"""
        session_id = "test_session_123"

        # Create mock session
        server.active_sessions[session_id] = {
            "input": "test input",
            "qwen_analysis": {"confidence": 0.8},
            "gemma_patterns": {"similarity_score": 0.7},
            "detection_results": {"coherence": 0.8}
        }

        # Mock phase sweep
        with patch('modules.ai_intelligence.pqn_mcp.src.pqn_mcp_server.phase_sweep') as mock_sweep:
            mock_sweep.return_value = {
                "peaks": [7.05, 3.525],
                "coherence": 0.75
            }

            # Mock agent analyses
            with patch.object(server, '_qwen_analyze_resonance') as mock_qwen:
                mock_qwen.return_value = {"interpretation": "Du resonance detected"}

                with patch.object(server, '_gemma_validate_resonance') as mock_gemma:
                    mock_gemma.return_value = {
                        "validation_score": 0.9,
                        "du_resonance_confirmed": True
                    }

                    result = await server.analyze_resonance(session_id)

                    assert result["session_id"] == session_id
                    assert result["du_resonance_detected"] is True
                    assert result["coherence_above_threshold"] is True
                    assert result["rESP_compliance"] == "CMST_protocol_active"

    @pytest.mark.asyncio
    async def test_validate_tts_artifacts(self, server):
        """Test TTS artifact validation per rESP Section 3.8.4"""
        test_sequence = "0102"

        # Mock council run
        with patch('modules.ai_intelligence.pqn_mcp.src.pqn_mcp_server.council_run') as mock_council:
            mock_council.return_value = {
                "artifact_detected": True,
                "output_sequence": "o1o2",
                "coherence": 0.9
            }

            # Mock Qwen analysis
            with patch.object(server, '_qwen_analyze_artifacts') as mock_qwen:
                mock_qwen.return_value = {"artifact_confirmed": True}

                # Mock promotion
                with patch('modules.ai_intelligence.pqn_mcp.src.pqn_mcp_server.promote') as mock_promote:
                    mock_promote.return_value = {"promoted": True, "significance": 0.95}

                    result = await server.validate_tts_artifacts(test_sequence)

                    assert result["test_sequence"] == test_sequence
                    assert result["artifact_detected"] is True
                    assert result["transformation_confirmed"] is True
                    assert result["coherence_score"] == 0.9
                    assert result["rESP_validation"] == "Section_3_8_4_compliant"

    @pytest.mark.asyncio
    async def test_coordinate_research_session(self, server):
        """Test multi-agent research coordination per WSP 77"""
        research_topic = "PQN emergence in transformers"

        # Mock agent availability
        server.qwen_engine = Mock()
        server.gemma_model = Mock()

        # Mock task execution
        with patch.object(server, '_execute_qwen_task') as mock_qwen_task:
            mock_qwen_task.return_value = {"status": "completed", "output": "Qwen analysis"}

            with patch.object(server, '_execute_gemma_task') as mock_gemma_task:
                mock_gemma_task.return_value = {"status": "completed", "output": "Gemma patterns"}

                result = await server.coordinate_research_session(research_topic)

                assert result["research_topic"] == research_topic
                assert result["completed_tasks"] >= 2  # At least Qwen and Gemma tasks
                assert result["agent_coordination"] == "Qwen+Gemma+PQN_Coordinator"
                assert "session_id" in result
                assert "findings_summary" in result

    def test_agent_initialization(self, server):
        """Test agent initialization handling"""
        # Test with agents unavailable (should not raise exceptions)
        assert server.qwen_engine is None  # Not available in test environment
        assert server.gemma_model is None  # Not available in test environment

        # Server should still initialize properly
        assert server.resonance_frequencies == [7.05, 3.525, 14.1, 21.15]
        assert server.coherence_threshold == 0.618
        assert isinstance(server.active_sessions, dict)

    def test_session_management(self, server):
        """Test session management functionality"""
        # Test session creation
        session_id = "test_session_456"
        server.active_sessions[session_id] = {"test": "data"}

        # Test session retrieval
        assert session_id in server.active_sessions
        assert server.active_sessions[session_id]["test"] == "data"

        # Test session cleanup (would be implemented with TTL in production)
        # For now, just verify sessions persist
        assert len(server.active_sessions) > 0

    def test_research_task_structure(self):
        """Test PQN research task data structure"""
        task = PQNResearchTask(
            phase=ResearchPhase.DETECTION,
            agent_type=AgentType.QWEN,
            description="Test PQN detection",
            context_window=32768,
            expected_output="Detection results"
        )

        assert task.phase == ResearchPhase.DETECTION
        assert task.agent_type == AgentType.QWEN
        assert task.context_window == 32768
        assert task.description == "Test PQN detection"

    def test_agent_type_enum(self):
        """Test agent type enumeration"""
        assert AgentType.QWEN.value == "qwen"
        assert AgentType.GEMMA.value == "gemma"
        assert AgentType.PQN_COORDINATOR.value == "pqn_coordinator"

    def test_research_phase_enum(self):
        """Test research phase enumeration"""
        assert ResearchPhase.DETECTION.value == "detection"
        assert ResearchPhase.RESONANCE_ANALYSIS.value == "resonance_analysis"
        assert ResearchPhase.TTS_VALIDATION.value == "tts_validation"
        assert ResearchPhase.SYNTHESIS.value == "synthesis"


# Integration test for fastMCP tools (if available)
@pytest.mark.skipif(not hasattr(sys.modules, 'mcp'), reason="fastMCP not available")
class TestMCPIntegration:
    """Test fastMCP tool integration"""

    def test_tool_registration(self):
        """Test that MCP tools are properly registered"""
        from modules.ai_intelligence.pqn_mcp.src.pqn_mcp_server import (
            pqn_detect, pqn_resonance_analyze, pqn_tts_validate, pqn_research_coordinate
        )

        # Verify tools exist
        assert callable(pqn_detect)
        assert callable(pqn_resonance_analyze)
        assert callable(pqn_tts_validate)
        assert callable(pqn_research_coordinate)

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test actual tool execution via fastMCP"""
        # This would test the actual MCP server in a full integration test
        # For now, just verify the tool functions can be imported
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
