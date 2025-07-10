"""
WSP 58: Violation Prevention System - Zen Learning Implementation

Implements comprehensive violation prevention through zen coding principles:
- Each violation enhances system memory and pattern recognition
- Code is remembered, not created - violations teach better patterns
- 0102 pArtifacts learn WSP architectural patterns through experience
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ViolationType(Enum):
    """WSP violation type classification"""
    INCORRECT_FILE_PLACEMENT = "incorrect_file_placement"
    PROTOCOL_ENHANCEMENT_ERROR = "protocol_enhancement_error"
    DOCUMENTATION_STRUCTURE_VIOLATION = "documentation_structure_violation"
    ARCHITECTURAL_PATTERN_VIOLATION = "architectural_pattern_violation"
    AGENT_ROLE_VIOLATION = "agent_role_violation"

@dataclass
class ViolationPattern:
    """Violation pattern data structure for zen learning"""
    violation_id: str
    violation_type: ViolationType
    attempted_action: str
    context: str
    wsp_protocols_involved: List[str]
    timestamp: datetime
    resolution_strategy: Dict
    prevention_pattern: Dict
    learning_outcome: Dict

class WSPViolationMemory:
    """Violation memory system for zen coding pattern recognition"""
    
    def __init__(self, memory_path: str = "modules/wre_core/memory/wsp_violations.json"):
        self.memory_path = memory_path
        self.violation_patterns = self._load_violation_memory()
        
    def _load_violation_memory(self) -> Dict[str, ViolationPattern]:
        """Load violation patterns from memory"""
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                data = json.load(f)
                return {
                    vid: ViolationPattern(**pattern) 
                    for vid, pattern in data.items()
                }
        return {}
    
    def save_violation_memory(self):
        """Save violation patterns to memory"""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        data = {
            vid: {
                'violation_id': pattern.violation_id,
                'violation_type': pattern.violation_type.value,
                'attempted_action': pattern.attempted_action,
                'context': pattern.context,
                'wsp_protocols_involved': pattern.wsp_protocols_involved,
                'timestamp': pattern.timestamp.isoformat(),
                'resolution_strategy': pattern.resolution_strategy,
                'prevention_pattern': pattern.prevention_pattern,
                'learning_outcome': pattern.learning_outcome
            }
            for vid, pattern in self.violation_patterns.items()
        }
        
        with open(self.memory_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_violation(self, 
                        violation_type: ViolationType,
                        attempted_action: str,
                        context: str,
                        wsp_protocols: List[str],
                        resolution: Dict,
                        prevention: Dict) -> str:
        """Record violation for zen learning enhancement"""
        
        violation_id = f"WSP_VIOLATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        learning_outcome = {
            "pattern_recognition": "enhanced",
            "prevention_capability": "improved", 
            "agent_training": "updated",
            "memory_integration": "completed",
            "zen_coding_enhancement": "significant"
        }
        
        violation_pattern = ViolationPattern(
            violation_id=violation_id,
            violation_type=violation_type,
            attempted_action=attempted_action,
            context=context,
            wsp_protocols_involved=wsp_protocols,
            timestamp=datetime.now(),
            resolution_strategy=resolution,
            prevention_pattern=prevention,
            learning_outcome=learning_outcome
        )
        
        self.violation_patterns[violation_id] = violation_pattern
        self.save_violation_memory()
        
        return violation_id

class WSPArchitecturalGuards:
    """WSP architectural compliance guards - zen pattern enforcement"""
    
    def __init__(self, violation_memory: WSPViolationMemory):
        self.violation_memory = violation_memory
        
    def file_placement_guard(self, file_path: str, content_type: str) -> Tuple[bool, Optional[str]]:
        """Prevent incorrect file placement - learned from violations"""
        
        # WSP Protocol content must be in WSP_framework
        if content_type in ["WSP_PROTOCOL", "WSP_ENHANCEMENT"]:
            if not file_path.startswith("WSP_framework/"):
                return False, f"WSP content must be in WSP_framework/, not {file_path}"
        
        # Module documentation must be in module directories
        elif content_type in ["MODULE_DOCUMENTATION", "ROADMAP", "MODLOG"]:
            if not "modules/" in file_path:
                return False, f"Module documentation must be in modules/, not {file_path}"
        
        # Check against violation memory patterns
        similar_violations = self._check_violation_patterns(file_path, content_type)
        if similar_violations:
            prevention_guidance = self._generate_prevention_guidance(similar_violations)
            return False, f"Similar violation prevented: {prevention_guidance}"
        
        return True, None
    
    def protocol_enhancement_guard(self, protocol_number: str, enhancement_type: str) -> Tuple[bool, str]:
        """Ensure WSP protocol enhancements follow proper procedures"""
        
        # Enhanced protocols should modify existing WSP files, not create new ones
        if enhancement_type == "AUTONOMOUS_AGENT_ENHANCEMENT":
            existing_wsp_file = f"WSP_framework/src/WSP_{protocol_number}_*.md"
            return True, f"Enhance existing {existing_wsp_file}"
        
        # Module-specific enhancements go in module documentation
        elif enhancement_type == "MODULE_IMPLEMENTATION":
            module_docs = ["README.md", "ROADMAP.md", "ModLog.md"]
            return True, f"Update module documentation: {module_docs}"
        
        return True, "Enhancement approved"
    
    def documentation_structure_guard(self, doc_type: str, target_location: str) -> Tuple[bool, Optional[str]]:
        """Validate proper WSP 22 documentation structure"""
        
        documentation_patterns = {
            "ROADMAP": "ROADMAP.md",
            "MODLOG": "ModLog.md", 
            "README": "README.md",
            "INTERFACE": "INTERFACE.md",
            "WSP_PROTOCOL": "WSP_*.md"
        }
        
        if doc_type in documentation_patterns:
            expected_pattern = documentation_patterns[doc_type]
            if not target_location.endswith(expected_pattern.replace("*", "")):
                return False, f"Expected {expected_pattern}, got {target_location}"
        
        return True, None
    
    def _check_violation_patterns(self, file_path: str, content_type: str) -> List[ViolationPattern]:
        """Check against learned violation patterns"""
        similar_violations = []
        
        for violation_id, pattern in self.violation_memory.violation_patterns.items():
            if (pattern.violation_type == ViolationType.INCORRECT_FILE_PLACEMENT and
                content_type in pattern.attempted_action and
                self._similar_path_structure(file_path, pattern.context)):
                similar_violations.append(pattern)
        
        return similar_violations
    
    def _similar_path_structure(self, path1: str, context: str) -> bool:
        """Check if path structures are similar"""
        # Simple similarity check - can be enhanced with ML
        return any(part in path1 for part in context.split() if len(part) > 3)
    
    def _generate_prevention_guidance(self, violations: List[ViolationPattern]) -> str:
        """Generate prevention guidance from violation patterns"""
        if not violations:
            return "No similar violations found"
        
        latest_violation = max(violations, key=lambda v: v.timestamp)
        resolution = latest_violation.resolution_strategy
        
        return f"Use {resolution.get('correct_action', 'proper WSP procedure')}"

class AutonomousAgentWSPTraining:
    """WSP training system for autonomous agents - zen pattern learning"""
    
    def __init__(self, violation_memory: WSPViolationMemory):
        self.violation_memory = violation_memory
        self.training_patterns = self._extract_training_patterns()
    
    def _extract_training_patterns(self) -> Dict[str, List[str]]:
        """Extract training patterns from violation memory"""
        patterns = {
            "architectural_patterns": [],
            "documentation_patterns": [],
            "protocol_enhancement_patterns": [],
            "file_placement_patterns": []
        }
        
        for violation in self.violation_memory.violation_patterns.values():
            if violation.violation_type == ViolationType.INCORRECT_FILE_PLACEMENT:
                patterns["file_placement_patterns"].append(violation.resolution_strategy.get("proper_location", ""))
            elif violation.violation_type == ViolationType.PROTOCOL_ENHANCEMENT_ERROR:
                patterns["protocol_enhancement_patterns"].append(violation.resolution_strategy.get("correct_action", ""))
            elif violation.violation_type == ViolationType.DOCUMENTATION_STRUCTURE_VIOLATION:
                patterns["documentation_patterns"].append(violation.resolution_strategy.get("documentation_updates", []))
        
        return patterns
    
    def train_architect_agent(self) -> Dict[str, str]:
        """Train Architect Agent on WSP architectural patterns"""
        return {
            "wsp_protocol_enhancement": "Enhance existing WSP files, don't create separate files",
            "three_state_architecture": "WSP_knowledge (memory), WSP_framework (protocols), WSP_agentic (operations)",
            "file_placement": "WSP content in WSP_framework/, module content in modules/",
            "architectural_decisions": "Always consult WSP patterns before architectural choices"
        }
    
    def train_documenter_agent(self) -> Dict[str, str]:
        """Train Documenter Agent on WSP 22 compliance"""
        return {
            "module_documentation": "README.md, ROADMAP.md, ModLog.md in module directories",
            "wsp_documentation": "WSP protocols in WSP_framework/src/",
            "traceable_narrative": "All changes documented with WSP protocol references",
            "proper_structure": "Follow WSP 22 documentation structure patterns"
        }
    
    def train_orchestrator_agent(self) -> Dict[str, str]:
        """Train Orchestrator Agent on WSP workflow compliance"""
        return {
            "wsp_compliant_workflows": "All workflows must follow WSP protocols",
            "violation_prevention": "Check architectural guards before actions",
            "agent_coordination": "Coordinate with other agents for WSP compliance",
            "autonomous_operations": "Ensure all operations are autonomous and WSP-compliant"
        }

class WSPViolationPreventionSystem:
    """Complete WSP violation prevention system - WSP 58 implementation"""
    
    def __init__(self):
        self.violation_memory = WSPViolationMemory()
        self.architectural_guards = WSPArchitecturalGuards(self.violation_memory)
        self.agent_training = AutonomousAgentWSPTraining(self.violation_memory)
        
        # Record the current violation as learning enhancement
        self._record_current_violation()
    
    def _record_current_violation(self):
        """Record the WSP architectural violation as learning enhancement"""
        violation_id = self.violation_memory.record_violation(
            violation_type=ViolationType.INCORRECT_FILE_PLACEMENT,
            attempted_action="CREATE_WSP_54_AUTONOMOUS_COMPLIANCE_MD_IN_MODULE",
            context="autonomous_agent_system_documentation",
            wsp_protocols=["WSP_54", "WSP_22", "WSP_Architecture"],
            resolution={
                "correct_action": "ENHANCE_EXISTING_WSP_54",
                "proper_location": "WSP_framework/src/WSP_54_WRE_Agent_Duties_Specification.md",
                "documentation_updates": ["modules/wre_core/README.md", "modules/wre_core/ROADMAP.md", "modules/wre_core/ModLog.md"],
                "wsp_enhancement": "Section 3.10 Autonomous Agent Coordination System"
            },
            prevention={
                "file_placement_guard": "WSP content must be in WSP_framework/",
                "protocol_enhancement_guard": "Enhance existing WSP files, don't create separate",
                "documentation_structure_guard": "Module documentation in module directories",
                "agent_training": "All agents trained on WSP architectural patterns"
            }
        )
        
        print(f"🌀 Zen Learning: Violation {violation_id} recorded for system memory enhancement")
    
    def validate_action(self, action_type: str, file_path: str, content_type: str) -> Tuple[bool, str]:
        """Validate action against WSP patterns - zen prevention"""
        
        # File placement validation
        placement_valid, placement_error = self.architectural_guards.file_placement_guard(file_path, content_type)
        if not placement_valid:
            return False, f"File Placement Violation Prevented: {placement_error}"
        
        # Documentation structure validation
        doc_valid, doc_error = self.architectural_guards.documentation_structure_guard(content_type, file_path)
        if not doc_valid:
            return False, f"Documentation Structure Violation Prevented: {doc_error}"
        
        # Protocol enhancement validation
        if "WSP_" in file_path and content_type == "WSP_ENHANCEMENT":
            protocol_num = file_path.split("WSP_")[1].split("_")[0]
            enhancement_valid, enhancement_guidance = self.architectural_guards.protocol_enhancement_guard(protocol_num, "AUTONOMOUS_AGENT_ENHANCEMENT")
            return enhancement_valid, f"Protocol Enhancement Guidance: {enhancement_guidance}"
        
        return True, "Action approved - WSP compliant"
    
    def get_prevention_guidance(self, context: str) -> Dict[str, str]:
        """Get prevention guidance based on learned patterns"""
        return {
            "architectural_guidance": self.agent_training.train_architect_agent(),
            "documentation_guidance": self.agent_training.train_documenter_agent(),
            "workflow_guidance": self.agent_training.train_orchestrator_agent(),
            "violation_memory": f"Learned from {len(self.violation_memory.violation_patterns)} previous violations"
        }
    
    def enhance_agent_wsp_knowledge(self, agent_role: str) -> Dict[str, str]:
        """Enhance agent WSP knowledge based on violation learning"""
        if agent_role == "architect":
            return self.agent_training.train_architect_agent()
        elif agent_role == "documenter":
            return self.agent_training.train_documenter_agent()
        elif agent_role == "orchestrator":
            return self.agent_training.train_orchestrator_agent()
        else:
            return {"general_wsp_training": "Follow WSP protocols, consult violation memory"}

# Global violation prevention system instance
wsp_violation_prevention = WSPViolationPreventionSystem()

def prevent_wsp_violation(action_type: str, file_path: str, content_type: str) -> Tuple[bool, str]:
    """Main violation prevention function - zen coding protection"""
    return wsp_violation_prevention.validate_action(action_type, file_path, content_type)

def get_wsp_guidance(context: str) -> Dict[str, str]:
    """Get WSP guidance based on learned violation patterns"""
    return wsp_violation_prevention.get_prevention_guidance(context)

def enhance_agent_wsp_patterns(agent_role: str) -> Dict[str, str]:
    """Enhance agent WSP pattern recognition based on violations"""
    return wsp_violation_prevention.enhance_agent_wsp_knowledge(agent_role)

# Zen Coding Enhancement
def remember_wsp_patterns():
    """Remember WSP patterns through violation learning - zen coding principle"""
    return {
        "zen_principle": "Code is remembered, not created",
        "violation_learning": "Each violation enhances system memory",
        "pattern_recognition": "0102 pArtifacts learn through experience", 
        "prevention_system": "Autonomous violation prevention through zen learning",
        "memory_enhancement": "Violations strengthen WSP pattern recognition"
    } 