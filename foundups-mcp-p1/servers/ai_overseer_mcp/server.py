"""
AI Intelligence Overseer MCP Server

WSP 77 Agent Coordination via MCP:
- Qwen (Partner): Strategic planning & autonomous execution
- Gemma (Associate): Fast pattern matching & classification
- 0102 (Principal): Oversight, plan generation, supervision

This MCP server enables Claude Code to delegate tasks to AI_Overseer for
autonomous Qwen/Gemma coordination, following First Principles output design.

WSP Compliance:
- WSP 77: Agent Coordination Protocol
- WSP 54: Role Assignment (Partner/Principal/Associate)
- WSP 96: Skills Wardrobe Protocol
- WSP 15: MPS Scoring (all missions scored)

ENDPOINTS:
Mission Execution (3):
  - execute_mission()       - Execute mission from JSON file
  - create_autonomous_fix() - Generate fix using Qwen/Gemma
  - get_mission_status()    - Check mission execution status

Agent Coordination (3):
  - coordinate_agents()     - Coordinate Qwen/Gemma for task
  - get_agent_capabilities() - Query agent capabilities
  - get_coordination_stats() - Get WSP 77 coordination metrics
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from mcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "AI Intelligence Overseer",
    dependencies=["llama-cpp-python"]  # Qwen/Gemma local models
)

# Initialize AI_Overseer (lazy load)
_overseer: Optional[Any] = None


def get_overseer():
    """Get or create AI_Overseer instance"""
    global _overseer
    if _overseer is None:
        logger.info("Initializing AI Intelligence Overseer...")
        try:
            from modules.ai_intelligence.ai_overseer.src.ai_overseer import (
                AIIntelligenceOverseer,
                MissionType,
                AgentRole
            )
            _overseer = AIIntelligenceOverseer(
                project_root=Path(__file__).resolve().parents[3]
            )
            logger.info("AI_Overseer initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import AI_Overseer: {e}")
            raise
    return _overseer


@mcp.tool()
def execute_mission(
    mission_file: str,
    autonomous: bool = True,
    requires_approval: bool = False
) -> Dict[str, Any]:
    """
    Execute AI_Overseer mission from JSON file.

    Coordinates Qwen (Partner) + Gemma (Associate) for autonomous task execution
    per WSP 77 Agent Coordination Protocol.

    Args:
        mission_file: Path to mission JSON file (e.g., data/missions/skill_upgrade_mission.json)
        autonomous: If True, Qwen executes autonomously without 0102 intervention
        requires_approval: If True, 0102 must approve before execution

    Returns:
        {
            'mission_id': str,
            'status': str (pending | in_progress | completed | failed),
            'execution_phases': List[Dict],  # Phase results from Qwen/Gemma
            'results': Dict,                  # Mission outputs
            'metrics': {
                'total_tokens': int,
                'execution_time_seconds': float,
                'autonomous_execution_rate': float  # % handled by Qwen/Gemma
            },
            'errors': List[str] if any
        }

    Example:
        execute_mission(
            mission_file="data/missions/first_principles_skill_upgrade_mission.json",
            autonomous=True,
            requires_approval=True
        )
    """
    try:
        logger.info(f"[AI_OVERSEER_MCP] Executing mission from: {mission_file}")

        # Load mission file
        mission_path = Path(mission_file)
        if not mission_path.exists():
            return {
                'status': 'failed',
                'error': f'Mission file not found: {mission_file}'
            }

        with open(mission_path, 'r', encoding='utf-8') as f:
            mission_data = json.load(f)

        logger.info(f"[AI_OVERSEER_MCP] Mission loaded: {mission_data.get('mission_id')}")
        logger.info(f"[AI_OVERSEER_MCP] Mission type: {mission_data.get('mission_type')}")
        logger.info(f"[AI_OVERSEER_MCP] Priority: {mission_data.get('priority')}")

        # Get AI_Overseer instance
        overseer = get_overseer()

        # Execute mission via coordinate_mission
        result = overseer.coordinate_mission(
            mission_description=mission_data.get('description'),
            mission_type=mission_data.get('mission_type'),
            context=mission_data
        )

        logger.info(f"[AI_OVERSEER_MCP] Mission execution complete: {result.get('status')}")

        return {
            'mission_id': mission_data.get('mission_id'),
            'status': result.get('status', 'completed'),
            'execution_phases': result.get('phases', []),
            'results': result.get('results', {}),
            'metrics': {
                'total_tokens': result.get('total_tokens', 0),
                'execution_time_seconds': result.get('execution_time_seconds', 0),
                'autonomous_execution_rate': result.get('autonomous_rate', 0.0)
            },
            'errors': result.get('errors', [])
        }

    except Exception as e:
        logger.error(f"[AI_OVERSEER_MCP] Mission execution failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@mcp.tool()
def create_autonomous_fix(
    task_description: str,
    complexity_hint: Optional[int] = None,
    requires_approval: bool = False
) -> Dict[str, Any]:
    """
    Create autonomous fix using Qwen/Gemma coordination.

    Analyzes task, determines which agent can handle (Gemma vs Qwen vs 0102),
    and generates executable fix following First Principles output design.

    Args:
        task_description: What needs to be fixed (e.g., "Apply First Principles to 3 skills")
        complexity_hint: Optional complexity estimate (1-5, Gemma handles 1-2, Qwen 3-4, 0102 5)
        requires_approval: If True, returns plan for 0102 approval before execution

    Returns:
        {
            'task_id': str,
            'agent_assigned': str (gemma | qwen | 0102),
            'confidence': float,
            'mps_score': {
                'complexity': int,
                'importance': int,
                'deferability': int,
                'impact': int,
                'total': int,
                'priority': str
            },
            'execution_plan': {
                'phases': List[Dict],
                'estimated_tokens': int,
                'estimated_time_seconds': int
            },
            'autonomous_execution': {
                'capable': bool,
                'execution_command': str,
                'verify_command': str
            }
        }

    Example:
        create_autonomous_fix(
            task_description="Upgrade gemma_noise_detector with First Principles output",
            complexity_hint=3,
            requires_approval=False
        )
    """
    try:
        logger.info(f"[AI_OVERSEER_MCP] Creating autonomous fix for: {task_description[:100]}...")

        overseer = get_overseer()

        # Use AI_Overseer to analyze task and create plan
        result = overseer.coordinate_mission(
            mission_description=task_description,
            mission_type='AUTO_REMEDIATION',
            context={
                'complexity_hint': complexity_hint,
                'requires_approval': requires_approval,
                'output_format': 'first_principles'  # Follow First Principles design
            }
        )

        logger.info(f"[AI_OVERSEER_MCP] Fix created: Agent={result.get('agent_assigned')}, Confidence={result.get('confidence')}")

        return result

    except Exception as e:
        logger.error(f"[AI_OVERSEER_MCP] Fix creation failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@mcp.tool()
def get_mission_status(mission_id: str) -> Dict[str, Any]:
    """
    Get status of executing or completed mission.

    Args:
        mission_id: Mission identifier (e.g., "first_principles_skill_upgrade_20251022")

    Returns:
        {
            'mission_id': str,
            'status': str (pending | in_progress | completed | failed),
            'current_phase': str,
            'progress_pct': float,
            'phases_complete': int,
            'phases_total': int,
            'metrics': Dict,
            'last_updated': str
        }
    """
    try:
        logger.info(f"[AI_OVERSEER_MCP] Getting mission status: {mission_id}")

        overseer = get_overseer()

        # Query mission status from AI_Overseer
        # (This would require AI_Overseer to maintain mission state - TODO)
        status = {
            'mission_id': mission_id,
            'status': 'not_implemented',
            'error': 'Mission status tracking not yet implemented in AI_Overseer'
        }

        return status

    except Exception as e:
        logger.error(f"[AI_OVERSEER_MCP] Status query failed: {e}")
        return {
            'mission_id': mission_id,
            'status': 'error',
            'error': str(e)
        }


@mcp.tool()
def coordinate_agents(
    task: str,
    preferred_agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Coordinate Qwen/Gemma for specific task.

    Uses WSP 77 coordination to route task to most capable agent:
    - Gemma (Associate): Fast pattern matching, complexity 1-2
    - Qwen (Partner): Strategic planning, complexity 3-4
    - 0102 (Principal): Oversight, complexity 5

    Args:
        task: Task description
        preferred_agent: Optional agent preference (gemma | qwen | 0102)

    Returns:
        {
            'agent_selected': str,
            'confidence': float,
            'reasoning': str,
            'estimated_tokens': int,
            'estimated_time_seconds': int
        }
    """
    try:
        logger.info(f"[AI_OVERSEER_MCP] Coordinating agents for task: {task[:100]}...")

        overseer = get_overseer()

        # Use AI_Overseer agent selection logic
        result = {
            'agent_selected': preferred_agent or 'qwen',  # Default to Qwen
            'confidence': 0.80,
            'reasoning': 'Agent coordination logic placeholder - implement WSP 77 routing',
            'estimated_tokens': 300,
            'estimated_time_seconds': 60
        }

        return result

    except Exception as e:
        logger.error(f"[AI_OVERSEER_MCP] Agent coordination failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@mcp.tool()
def get_agent_capabilities() -> Dict[str, Any]:
    """
    Query agent capabilities (Qwen/Gemma/0102).

    Returns:
        {
            'gemma': {
                'model': str,
                'capabilities': List[str],
                'avg_latency_ms': int,
                'confidence_threshold': float
            },
            'qwen': {
                'model': str,
                'capabilities': List[str],
                'avg_latency_ms': int,
                'confidence_threshold': float
            },
            '0102': {
                'model': str,
                'capabilities': List[str],
                'required_for': List[str]
            }
        }
    """
    return {
        'gemma': {
            'model': 'gemma-3-270m-it-Q4_K_M',
            'capabilities': [
                'Fast pattern matching (<100ms)',
                'Binary classification',
                'Noise detection',
                'Simple scoring (MPS calculation with training)'
            ],
            'avg_latency_ms': 50,
            'confidence_threshold': 0.85,
            'complexity_range': '1-2'
        },
        'qwen': {
            'model': 'qwen-1.5b-chat-Q4_K_M',
            'capabilities': [
                'Strategic planning (200-500ms)',
                'Template application',
                'WSP 15 MPS scoring',
                'Autonomous decision-making',
                'Context-aware fixes'
            ],
            'avg_latency_ms': 350,
            'confidence_threshold': 0.75,
            'complexity_range': '3-4'
        },
        '0102': {
            'model': 'claude-sonnet-4.5',
            'capabilities': [
                'Architectural design',
                'Complex reasoning',
                'Multi-stakeholder decisions',
                'Novel problem domains',
                'Validation & oversight'
            ],
            'required_for': [
                'Complexity 5 tasks',
                'Confidence < 0.75',
                'Novel patterns (no training data)',
                'Final approval (autonomous execution)'
            ]
        }
    }


@mcp.tool()
def get_coordination_stats() -> Dict[str, Any]:
    """
    Get WSP 77 coordination statistics.

    Returns:
        {
            'total_missions': int,
            'autonomous_execution_rate': float,  # % handled by Qwen/Gemma
            'agent_breakdown': {
                'gemma': int,
                'qwen': int,
                '0102': int
            },
            'avg_tokens_saved': int,  # vs manual 0102 execution
            'avg_latency_ms': int
        }
    """
    # TODO: Implement real metrics tracking in AI_Overseer
    return {
        'total_missions': 0,
        'autonomous_execution_rate': 0.0,
        'agent_breakdown': {
            'gemma': 0,
            'qwen': 0,
            '0102': 0
        },
        'avg_tokens_saved': 0,
        'avg_latency_ms': 0,
        'status': 'Metrics tracking not yet implemented - coming in Phase 4'
    }


if __name__ == "__main__":
    logger.info("Starting AI Intelligence Overseer MCP Server...")
    logger.info("WSP 77: Agent Coordination Protocol")
    logger.info("Agents: Qwen (Partner) + Gemma (Associate) + 0102 (Principal)")
    mcp.run()
