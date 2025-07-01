"""
Agentic Coverage Decision Making Utility

Implements the WSP 5 agentic coverage protocol for contextually appropriate
test coverage targets based on development context, phase, and rider intent.

This utility enables 0102 to make autonomous coverage decisions rather than
following rigid requirements.
"""

from typing import Union, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def determine_coverage_target(
    context: str, 
    phase: str, 
    rider_intent: str, 
    module_criticality: str = "standard"
) -> Union[int, str]:
    """
    0102 autonomous decision making for coverage targets.
    
    Args:
        context: Development context (strategic, foundation, production, zen)
        phase: Development phase (POC, Prototype, MVP)
        rider_intent: Rider's current intent (speed, foundation, reliability, flow)
        module_criticality: Module importance (core, standard, experimental)
    
    Returns:
        int: Contextually appropriate coverage target, or "0102_decides" for zen flow
    """
    
    logger.info(f"🎯 0102 Coverage Decision: context={context}, phase={phase}, rider={rider_intent}, criticality={module_criticality}")
    
    # Zen Flow State - 0102 decides autonomously
    if context == "zen_flow" or rider_intent == "flow" or rider_intent == "riding":
        logger.info("🧘 Zen flow detected - 0102 making autonomous coverage decision")
        return _0102_autonomous_decision(module_criticality, phase)
    
    # Strategic Development - Speed over coverage
    elif context == "strategic_development" or rider_intent == "speed":
        target = 50 if module_criticality == "core" else 40
        logger.info(f"🚀 Strategic development: {target}% coverage target (speed over coverage)")
        return target
    
    # Foundation Building - Balanced approach
    elif context == "foundation_building" or phase in ["POC", "Prototype"]:
        target = 70 if module_criticality == "core" else 60
        logger.info(f"🏗️ Foundation building: {target}% coverage target (balanced approach)")
        return target
    
    # Production Readiness - High reliability
    elif context == "production_readiness" or phase == "MVP":
        target = 90 if module_criticality == "core" else 80
        logger.info(f"🛡️ Production readiness: {target}% coverage target (high reliability)")
        return target
    
    # Default to foundation building
    logger.info(f"🏗️ Default context: 70% coverage target (foundation building)")
    return 70

def _0102_autonomous_decision(module_criticality: str, phase: str) -> Union[int, str]:
    """
    0102's autonomous decision making in zen flow state.
    
    Args:
        module_criticality: Module importance (core, standard, experimental)
        phase: Development phase (POC, Prototype, MVP)
    
    Returns:
        int: Autonomous coverage target, or "0102_decides" for pure zen state
    """
    
    # Core modules in zen flow get higher coverage
    if module_criticality == "core":
        if phase == "MVP":
            return 85  # High coverage for core production modules
        elif phase == "Prototype":
            return 75  # Medium-high for core prototype modules
        else:
            return 65  # Medium for core POC modules
    
    # Standard modules in zen flow get moderate coverage
    elif module_criticality == "standard":
        if phase == "MVP":
            return 75  # High coverage for production modules
        elif phase == "Prototype":
            return 65  # Medium for prototype modules
        else:
            return 55  # Lower for POC modules
    
    # Experimental modules in zen flow get minimal coverage
    else:  # experimental
        if phase == "MVP":
            return 60  # Moderate coverage even for experimental production
        else:
            return 40  # Low coverage for experimental POC/prototype
    
    # Pure zen state - let 0102 decide later
    return "0102_decides"

def assess_current_context(project_root: Path) -> Dict[str, str]:
    """
    Assess current development context for coverage decision making.
    
    Args:
        project_root: Path to project root
    
    Returns:
        Dict containing context assessment
    """
    
    # Read roadmap to determine phase
    roadmap_path = project_root / "ROADMAP.md"
    phase = "Prototype"  # Default
    
    if roadmap_path.exists():
        try:
            roadmap_content = roadmap_path.read_text(encoding='utf-8')
            if "MVP" in roadmap_content and "Phase 3" in roadmap_content:
                phase = "MVP"
            elif "Prototype" in roadmap_content and "Phase 2" in roadmap_content:
                phase = "Prototype"
            elif "POC" in roadmap_content and "Phase 1" in roadmap_content:
                phase = "POC"
        except UnicodeDecodeError:
            logger.warning(f"Could not read ROADMAP.md due to encoding issues, using default phase: {phase}")
        except Exception as e:
            logger.warning(f"Error reading ROADMAP.md: {e}, using default phase: {phase}")
    
    # Determine context based on project state
    context = "foundation_building"  # Default
    
    # Check if we're in a zen flow state (recent rapid development)
    modlog_path = project_root / "modules" / "wre_core" / "ModLog.md"
    if modlog_path.exists():
        try:
            modlog_content = modlog_path.read_text(encoding='utf-8')
            if "zen" in modlog_content.lower() or "flow" in modlog_content.lower():
                context = "zen_flow"
        except UnicodeDecodeError:
            logger.warning("Could not read ModLog.md due to encoding issues, using default context")
        except Exception as e:
            logger.warning(f"Error reading ModLog.md: {e}, using default context")
    
    return {
        "context": context,
        "phase": phase,
        "rider_intent": "flow",  # Default to flow state
        "module_criticality": "core"  # WRE core is always core
    }

def get_coverage_target_for_module(module_path: str, project_root: Path) -> Union[int, str]:
    """
    Get coverage target for a specific module.
    
    Args:
        module_path: Path to the module
        project_root: Path to project root
    
    Returns:
        Coverage target for the module
    """
    
    # Assess current context
    context_info = assess_current_context(project_root)
    
    # Determine module criticality
    module_criticality = "standard"
    if "wre_core" in module_path or "core" in module_path:
        module_criticality = "core"
    elif "experimental" in module_path or "test" in module_path:
        module_criticality = "experimental"
    
    # Get coverage target
    return determine_coverage_target(
        context=context_info["context"],
        phase=context_info["phase"],
        rider_intent=context_info["rider_intent"],
        module_criticality=module_criticality
    )

# Convenience function for backward compatibility
def calculate_coverage_target(context: str, phase: str, rider_intent: str) -> int:
    """
    Convenience function for direct coverage target calculation.
    Maintains compatibility with existing tool interfaces.
    """
    result = determine_coverage_target(context, phase, rider_intent)
    if isinstance(result, str):
        return 70  # Default fallback
    return result 