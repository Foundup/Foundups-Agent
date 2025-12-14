"""
Vision Executor - Multi-step workflow executor for vision-based automation

WSP Compliance:
    - WSP 77: AI Overseer integration (workflow telemetry)
    - WSP 48: Recursive improvement (pattern learning)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .ui_tars_bridge import UITarsBridge, ActionResult

logger = logging.getLogger(__name__)


@dataclass
class ActionStep:
    """Single step in a vision workflow."""
    action: str           # 'click', 'type', 'scroll', 'verify'
    description: str      # "blue Like button"
    text: Optional[str] = None   # For 'type' action
    wait_after: float = 0.5      # Seconds to wait after action
    required: bool = True        # If False, workflow continues on failure
    max_retries: int = 2         # Retry count for this step


@dataclass
class WorkflowResult:
    """Result of a multi-step workflow."""
    success: bool
    steps_completed: int
    steps_total: int
    step_results: List[ActionResult] = field(default_factory=list)
    total_duration_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "step_results": [r.to_dict() for r in self.step_results],
            "total_duration_ms": self.total_duration_ms,
            "error": self.error,
        }


class VisionExecutor:
    """
    Executes multi-step vision workflows with verification.
    
    Features:
    - Sequential step execution
    - Retry logic per step
    - Verification after each step (optional)
    - Telemetry for AI Overseer
    - Pattern learning integration
    
    Usage:
        executor = VisionExecutor(bridge)
        
        steps = [
            ActionStep(action="scroll", description="scroll to comments"),
            ActionStep(action="click", description="Like button"),
            ActionStep(action="type", description="reply box", text="Great!"),
            ActionStep(action="click", description="Reply submit button"),
        ]
        
        result = await executor.execute_workflow(steps)
    """

    def __init__(
        self,
        bridge: UITarsBridge,
        max_retries: int = 3,
        verify_each: bool = True,
    ) -> None:
        """
        Initialize executor.
        
        Args:
            bridge: UITarsBridge instance
            max_retries: Default max retry attempts per action
            verify_each: Whether to verify after each step by default
        """
        self.bridge = bridge
        self.max_retries = max_retries
        self.verify_each = verify_each
        
        logger.info(f"[VISION-EXEC] Initialized with max_retries={max_retries}")

    async def execute_step(
        self,
        step: ActionStep,
        context: Optional[Dict[str, Any]] = None,
    ) -> ActionResult:
        """
        Execute a single step with retry logic.
        
        Args:
            step: ActionStep to execute
            context: Additional context
            
        Returns:
            ActionResult from the action
        """
        context = context or {}
        
        # Add text to context for type actions
        if step.text:
            context["text"] = step.text
        
        retries = step.max_retries or self.max_retries
        last_result = None
        
        for attempt in range(retries + 1):
            logger.info(f"[VISION-EXEC] Step: {step.action} - {step.description} (attempt {attempt + 1})")
            
            result = await self.bridge.execute_action(
                action=step.action,
                description=step.description,
                context=context,
            )
            
            last_result = result
            
            if result.success:
                # Wait after successful action
                if step.wait_after > 0:
                    await asyncio.sleep(step.wait_after)
                return result
            
            if attempt < retries:
                logger.warning(f"[VISION-EXEC] Step failed, retrying: {result.error}")
                await asyncio.sleep(0.5)  # Brief pause before retry
        
        return last_result

    async def execute_workflow(
        self,
        steps: List[ActionStep],
        context: Optional[Dict[str, Any]] = None,
        verify_each: Optional[bool] = None,
    ) -> WorkflowResult:
        """
        Execute a series of vision actions.
        
        Args:
            steps: List of ActionStep objects
            context: Shared context for all steps
            verify_each: Override default verification behavior
            
        Returns:
            WorkflowResult with all step outcomes
        """
        verify = verify_each if verify_each is not None else self.verify_each
        context = context or {}
        
        start_time = time.time()
        step_results: List[ActionResult] = []
        steps_completed = 0
        error = None
        
        logger.info(f"[VISION-EXEC] Starting workflow with {len(steps)} steps")
        
        for i, step in enumerate(steps):
            logger.info(f"[VISION-EXEC] Executing step {i + 1}/{len(steps)}: {step.action}")
            
            result = await self.execute_step(step, context)
            step_results.append(result)
            
            if result.success:
                steps_completed += 1
                
                # Verify step if enabled
                if verify and step.action in ("click", "type"):
                    verify_result = await self.bridge.verify(
                        f"verify {step.action} on {step.description} succeeded"
                    )
                    if not verify_result.success:
                        logger.warning(f"[VISION-EXEC] Verification failed for step {i + 1}")
            else:
                if step.required:
                    error = f"Required step {i + 1} failed: {result.error}"
                    logger.error(f"[VISION-EXEC] {error}")
                    break
                else:
                    logger.warning(f"[VISION-EXEC] Optional step {i + 1} failed, continuing")
                    steps_completed += 1  # Count optional failures as "completed"
        
        total_duration_ms = int((time.time() - start_time) * 1000)
        success = steps_completed == len(steps)
        
        workflow_result = WorkflowResult(
            success=success,
            steps_completed=steps_completed,
            steps_total=len(steps),
            step_results=step_results,
            total_duration_ms=total_duration_ms,
            error=error,
        )
        
        logger.info(
            f"[VISION-EXEC] Workflow complete: {steps_completed}/{len(steps)} steps, "
            f"success={success}, duration={total_duration_ms}ms"
        )
        
        return workflow_result

    async def studio_heart_and_reply_workflow(
        self,
        filter_text: str,
        reply_text: str,
    ) -> WorkflowResult:
        """
        Workflow for YouTube Studio comments inbox:
        - Filter comments by the provided text
        - Heart + like the first matching comment
        - Reply with the given text
        """
        steps = [
            ActionStep(
                action="click",
                description="search comments box",
                wait_after=0.3,
            ),
            ActionStep(
                action="type",
                description="search comments box",
                text=filter_text,
                wait_after=0.2,
            ),
            ActionStep(
                action="click",
                description="apply search or filter button",
                wait_after=1.0,
            ),
            ActionStep(
                action="click",
                description="first comment card after filtering",
                wait_after=0.5,
            ),
            ActionStep(
                action="click",
                description="creator heart icon on the comment",
                wait_after=0.3,
            ),
            ActionStep(
                action="click",
                description="thumbs up like button on the comment",
                wait_after=0.3,
            ),
            ActionStep(
                action="click",
                description="reply button on the comment",
                wait_after=0.4,
            ),
            ActionStep(
                action="type",
                description="reply text area",
                text=reply_text,
                wait_after=0.3,
            ),
            ActionStep(
                action="click",
                description="reply publish button",
                wait_after=1.0,
            ),
        ]

        context = {
            "workflow": "studio_heart_and_reply",
            "filter_text": filter_text,
        }

        return await self.execute_workflow(steps, context)

    async def like_and_reply_workflow(
        self,
        video_id: str,
        comment_id: str,
        reply_text: str,
    ) -> WorkflowResult:
        """
        Pre-built workflow for liking and replying to a YouTube comment.
        
        Args:
            video_id: YouTube video ID
            comment_id: Comment thread ID
            reply_text: Text to reply with
            
        Returns:
            WorkflowResult with outcome
        """
        steps = [
            ActionStep(
                action="scroll",
                description="scroll to the comment section",
                wait_after=1.0,
            ),
            ActionStep(
                action="click",
                description=f"thumbs up Like button on comment {comment_id}",
                wait_after=0.5,
            ),
            ActionStep(
                action="click",
                description=f"Reply button on comment {comment_id}",
                wait_after=0.5,
            ),
            ActionStep(
                action="type",
                description="reply text input box",
                text=reply_text,
                wait_after=0.3,
            ),
            ActionStep(
                action="click",
                description="blue Reply submit button",
                wait_after=1.0,
            ),
        ]
        
        context = {
            "video_id": video_id,
            "comment_id": comment_id,
            "workflow": "like_and_reply",
        }
        
        return await self.execute_workflow(steps, context)


# Test function
async def _test_executor():
    """Test VisionExecutor functionality."""
    from .ui_tars_bridge import UITarsBridge
    
    bridge = UITarsBridge()
    await bridge.connect()
    
    executor = VisionExecutor(bridge)
    
    # Test simple workflow
    steps = [
        ActionStep(action="scroll", description="scroll down", wait_after=0.5),
        ActionStep(action="click", description="Like button", wait_after=0.5),
    ]
    
    result = await executor.execute_workflow(steps)
    print(f"Workflow result: {result.success}, {result.steps_completed}/{result.steps_total}")
    
    bridge.close()


if __name__ == "__main__":
    asyncio.run(_test_executor())



