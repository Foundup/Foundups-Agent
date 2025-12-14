"""
Tests for UITarsBridge and VisionExecutor

WSP Reference: WSP 34 (Test Documentation)
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path

# Import modules under test
from modules.infrastructure.foundups_vision.src.ui_tars_bridge import (
    UITarsBridge,
    ActionResult,
    Screenshot,
    UITarsConnectionError,
)
from modules.infrastructure.foundups_vision.src.vision_executor import (
    VisionExecutor,
    ActionStep,
    WorkflowResult,
)


class TestUITarsBridge:
    """Test UITarsBridge functionality."""

    def test_bridge_init(self):
        """Test bridge initialization."""
        bridge = UITarsBridge()
        assert bridge.browser_port == 9222
        assert not bridge._connected
        assert bridge._session_id is None

    def test_bridge_init_custom_port(self):
        """Test bridge with custom port."""
        bridge = UITarsBridge(browser_port=9333)
        assert bridge.browser_port == 9333

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connection to UI-TARS."""
        bridge = UITarsBridge()
        
        # Should connect (creates directories)
        result = await bridge.connect()
        assert result is True
        assert bridge._connected is True
        assert bridge._session_id is not None
        
        bridge.close()
        assert bridge._connected is False

    @pytest.mark.asyncio
    async def test_execute_action(self):
        """Test action execution."""
        bridge = UITarsBridge()
        await bridge.connect()
        
        result = await bridge.execute_action(
            action="click",
            description="test button",
            context={"test": True},
        )
        
        assert isinstance(result, ActionResult)
        assert result.action == "click"
        assert result.description == "test button"
        assert result.duration_ms >= 0
        
        bridge.close()

    @pytest.mark.asyncio
    async def test_click_helper(self):
        """Test click convenience method."""
        bridge = UITarsBridge()
        await bridge.connect()
        
        result = await bridge.click("Like button")
        
        assert result.action == "click"
        assert result.description == "Like button"
        
        bridge.close()

    def test_observer_registration(self):
        """Test telemetry observer registration."""
        events = []
        
        def observer(event, payload):
            events.append((event, payload))
        
        bridge = UITarsBridge(observers=[observer])
        
        # Should have captured init event
        assert len(events) > 0
        assert events[0][0] == "bridge_init"

    def test_action_result_to_dict(self):
        """Test ActionResult serialization."""
        result = ActionResult(
            success=True,
            action="click",
            description="test",
            duration_ms=100,
            confidence=0.95,
        )
        
        d = result.to_dict()
        assert d["success"] is True
        assert d["action"] == "click"
        assert d["confidence"] == 0.95


class TestVisionExecutor:
    """Test VisionExecutor functionality."""

    @pytest.mark.asyncio
    async def test_executor_init(self):
        """Test executor initialization."""
        bridge = UITarsBridge()
        await bridge.connect()
        
        executor = VisionExecutor(bridge)
        assert executor.max_retries == 3
        assert executor.verify_each is True
        
        bridge.close()

    @pytest.mark.asyncio
    async def test_execute_step(self):
        """Test single step execution."""
        bridge = UITarsBridge()
        await bridge.connect()
        
        executor = VisionExecutor(bridge)
        
        step = ActionStep(
            action="click",
            description="test button",
            wait_after=0.1,
        )
        
        result = await executor.execute_step(step)
        
        assert isinstance(result, ActionResult)
        
        bridge.close()

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test multi-step workflow execution."""
        bridge = UITarsBridge()
        await bridge.connect()
        
        executor = VisionExecutor(bridge, verify_each=False)
        
        steps = [
            ActionStep(action="scroll", description="scroll down", wait_after=0.1),
            ActionStep(action="click", description="button", wait_after=0.1),
        ]
        
        result = await executor.execute_workflow(steps)
        
        assert isinstance(result, WorkflowResult)
        assert result.steps_total == 2
        assert len(result.step_results) == 2
        
        bridge.close()

    @pytest.mark.asyncio
    async def test_like_and_reply_workflow(self):
        """Test pre-built like and reply workflow."""
        bridge = UITarsBridge()
        await bridge.connect()
        
        executor = VisionExecutor(bridge, verify_each=False)
        
        result = await executor.like_and_reply_workflow(
            video_id="test123",
            comment_id="comment456",
            reply_text="Great video!",
        )
        
        assert isinstance(result, WorkflowResult)
        assert result.steps_total == 5  # scroll, like, reply btn, type, submit
        
        bridge.close()

    def test_action_step_defaults(self):
        """Test ActionStep default values."""
        step = ActionStep(action="click", description="button")
        
        assert step.text is None
        assert step.wait_after == 0.5
        assert step.required is True
        assert step.max_retries == 2

    def test_workflow_result_to_dict(self):
        """Test WorkflowResult serialization."""
        result = WorkflowResult(
            success=True,
            steps_completed=3,
            steps_total=3,
            total_duration_ms=1500,
        )
        
        d = result.to_dict()
        assert d["success"] is True
        assert d["steps_completed"] == 3
        assert d["total_duration_ms"] == 1500


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])



