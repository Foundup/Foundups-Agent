#!/usr/bin/env python3
"""
WSP Violation Prevention System - Recursive Self-Improvement
Implements WSP 50 Pre-Action Verification and WSP 48 Learning
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

class WSPViolationPrevention:
    """
    Prevents WSP violations through pre-action verification and recursive learning
    Every prevented violation makes the system stronger
    """
    
    def __init__(self):
        self.wsp_index_path = Path("O:/Foundups-Agent/WSP_framework/src/WSP_MASTER_INDEX.md")
        self.wsp_core_path = Path("O:/Foundups-Agent/WSP_framework/src/WSP_CORE.md")
        self.violation_memory = Path("O:/Foundups-Agent/WSP_agentic/agentic_journals/violation_prevention.json")
        self.current_state = "0102"  # Always operate in quantum entangled state
        
    def pre_action_verification(self, action_type: str, target_path: str, content: Any = None) -> Dict[str, Any]:
        """
        WSP 50: Enhanced Pre-Action Verification Protocol
        MUST be called before ANY file operation
        """
        
        verification_result = {
            "allowed": False,
            "reason": "",
            "wsp_references": [],
            "alternative": None,
            "learning": {}
        }
        
        # Step 1: Search and Verify
        target = Path(target_path)
        
        # Step 2: Architectural Intent Analysis (WHY)
        why = self.analyze_intent(action_type, target_path)
        
        # Step 3: Impact Assessment (HOW)
        impact = self.assess_impact(action_type, target_path)
        
        # Step 4: Execution Planning (WHAT)
        what = self.plan_execution(action_type, target_path)
        
        # Step 5: Timing Consideration (WHEN)
        when = self.consider_timing(action_type)
        
        # Step 6: Location Specification (WHERE)
        where = self.specify_location(target_path)
        
        # Step 7: Final Validation
        validation = self.final_validation(action_type, target_path, where)
        
        if validation["valid"]:
            verification_result["allowed"] = True
            verification_result["reason"] = "WSP compliant action"
            verification_result["wsp_references"] = validation["wsps"]
        else:
            verification_result["allowed"] = False
            verification_result["reason"] = validation["violation"]
            verification_result["alternative"] = validation["alternative"]
            
            # Learn from prevented violation
            self.learn_from_prevention(action_type, target_path, validation)
        
        return verification_result
    
    def analyze_intent(self, action_type: str, target_path: str) -> str:
        """WHY - Determine purpose behind action"""
        
        intents = {
            "create_file": "Adding new functionality or documentation",
            "modify_file": "Improving existing functionality",
            "delete_file": "Removing obsolete or violating content",
            "move_file": "Restructuring for WSP compliance"
        }
        
        return intents.get(action_type, "Unknown intent")
    
    def assess_impact(self, action_type: str, target_path: str) -> Dict[str, Any]:
        """HOW - Evaluate system impact"""
        
        impact = {
            "modules_affected": [],
            "wsp_compliance": True,
            "risk_level": "low"
        }
        
        # Check if action affects critical paths
        critical_paths = [
            "WSP_framework/",
            ".claude/agents/",  # Only .md files allowed here
            "modules/infrastructure/"
        ]
        
        for critical in critical_paths:
            if critical in target_path:
                impact["risk_level"] = "high"
                impact["modules_affected"].append(critical)
        
        return impact
    
    def plan_execution(self, action_type: str, target_path: str) -> Dict[str, Any]:
        """WHAT - Define specific changes required"""
        
        plan = {
            "action": action_type,
            "target": target_path,
            "requirements": []
        }
        
        if action_type == "create_file":
            plan["requirements"] = [
                "Verify parent directory exists",
                "Check WSP for proper location",
                "Ensure no duplicate functionality"
            ]
        
        return plan
    
    def consider_timing(self, action_type: str) -> str:
        """WHEN - Assess timing of action"""
        
        # In 0102 state, timing is always optimal due to quantum entanglement
        return "Now - quantum state optimal"
    
    def specify_location(self, target_path: str) -> Dict[str, Any]:
        """WHERE - Identify correct location per WSP"""
        
        path = Path(target_path)
        location = {
            "path": str(path),
            "domain": None,
            "module": None,
            "wsp_compliant": False
        }
        
        # Check WSP 49 compliance for test files
        if "test" in path.name.lower() and path.parent.name != "tests":
            location["wsp_compliant"] = False
            location["violation"] = "WSP 49: Test files must be in module/tests/"
            location["correct_path"] = self.get_correct_test_location(path)
            return location
        
        # Check .claude/agents/ for only .md files
        if ".claude/agents" in str(path) and path.suffix != ".md":
            location["wsp_compliant"] = False
            location["violation"] = "WSP: .claude/agents/ only allows .md files"
            location["correct_path"] = self.get_correct_python_location(path)
            return location
        
        # Check module structure
        if "modules/" in str(path):
            parts = path.parts
            if "modules" in parts:
                idx = parts.index("modules")
                if len(parts) > idx + 2:
                    location["domain"] = parts[idx + 1]
                    location["module"] = parts[idx + 2]
                    location["wsp_compliant"] = True
        
        return location
    
    def get_correct_test_location(self, path: Path) -> str:
        """Get WSP 49 compliant test location"""
        
        # Find appropriate module for test
        if "infrastructure" in str(path):
            return "modules/infrastructure/[module]/tests/"
        elif "ai_intelligence" in str(path):
            return "modules/ai_intelligence/[module]/tests/"
        else:
            return "modules/[domain]/[module]/tests/"
    
    def get_correct_python_location(self, path: Path) -> str:
        """Get WSP compliant location for Python files"""
        
        name = path.stem
        
        if "awakening" in name or "activation" in name:
            return "modules/infrastructure/agent_activation/src/"
        elif "error" in name or "learning" in name:
            return "modules/infrastructure/error_learning_agent/src/"
        elif "registry" in name or "management" in name:
            return "modules/infrastructure/agent_management/src/"
        else:
            return "modules/infrastructure/[appropriate_module]/src/"
    
    def final_validation(self, action_type: str, target_path: str, location: Dict) -> Dict[str, Any]:
        """Cross-check with all relevant WSPs"""
        
        validation = {
            "valid": True,
            "wsps": [],
            "violation": None,
            "alternative": None
        }
        
        # Check location compliance
        if not location.get("wsp_compliant", False):
            validation["valid"] = False
            validation["violation"] = location.get("violation", "Location not WSP compliant")
            validation["alternative"] = location.get("correct_path", "Check WSP for correct location")
            validation["wsps"] = ["WSP 49", "WSP 3", "WSP 50"]
            return validation
        
        # Check documentation requirements
        if action_type == "create_file" and target_path.endswith(".md"):
            # WSP 22: ModLog requirements
            if "ModLog" in target_path:
                validation["wsps"].append("WSP 22")
            
            # Check if documentation has a consumer (WSP 48)
            if not self.has_documentation_consumer(target_path):
                validation["valid"] = False
                validation["violation"] = "WSP 48: Documentation must have active consumer"
                validation["alternative"] = "Only create docs that will be read by system"
                validation["wsps"].append("WSP 48")
        
        return validation
    
    def has_documentation_consumer(self, doc_path: str) -> bool:
        """WSP 48: Verify documentation will be actively used"""
        
        # ModLogs are always consumed
        if "ModLog" in doc_path:
            return True
        
        # README files in modules are consumed
        if "README.md" in doc_path and "modules/" in doc_path:
            return True
        
        # Agent .md files are consumed by /agents command
        if ".claude/agents/" in doc_path and doc_path.endswith(".md"):
            return True
        
        # Default: question if it will be consumed
        return False
    
    def learn_from_prevention(self, action_type: str, target_path: str, validation: Dict):
        """WSP 48: Learn from every prevented violation"""
        
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "target_path": target_path,
            "violation": validation["violation"],
            "alternative": validation["alternative"],
            "wsps": validation["wsps"],
            "state": self.current_state
        }
        
        # Load existing memory
        if self.violation_memory.exists():
            with open(self.violation_memory, 'r') as f:
                memory = json.load(f)
        else:
            memory = {"preventions": [], "patterns": {}}
        
        # Add to memory
        memory["preventions"].append(learning_entry)
        
        # Extract pattern
        pattern_key = f"{action_type}:{validation['violation']}"
        if pattern_key not in memory["patterns"]:
            memory["patterns"][pattern_key] = {
                "count": 0,
                "alternative": validation["alternative"],
                "wsps": validation["wsps"]
            }
        memory["patterns"][pattern_key]["count"] += 1
        
        # Save memory
        self.violation_memory.parent.mkdir(parents=True, exist_ok=True)
        with open(self.violation_memory, 'w') as f:
            json.dump(memory, f, indent=2)
        
        print(f"[LEARNED] Prevented violation pattern recorded")
        print(f"[WSP 48] System stronger through prevention")


class WSPCompliantFileOperations:
    """
    All file operations go through WSP verification first
    """
    
    def __init__(self):
        self.prevention = WSPViolationPrevention()
    
    def create_file(self, file_path: str, content: str) -> bool:
        """Create file only if WSP compliant"""
        
        # Pre-action verification
        verification = self.prevention.pre_action_verification(
            "create_file", 
            file_path,
            content
        )
        
        if not verification["allowed"]:
            print(f"[PREVENTED] {verification['reason']}")
            print(f"[ALTERNATIVE] {verification['alternative']}")
            return False
        
        # Create file
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[CREATED] {file_path} (WSP compliant)")
        return True
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move file only if WSP compliant"""
        
        # Verify destination is WSP compliant
        verification = self.prevention.pre_action_verification(
            "move_file",
            destination
        )
        
        if not verification["allowed"]:
            print(f"[PREVENTED] {verification['reason']}")
            print(f"[ALTERNATIVE] {verification['alternative']}")
            return False
        
        # Move file
        source_path = Path(source)
        dest_path = Path(destination)
        
        if source_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.rename(dest_path)
            print(f"[MOVED] {source} -> {destination} (WSP compliant)")
            return True
        
        return False


if __name__ == "__main__":
    print("WSP VIOLATION PREVENTION SYSTEM")
    print("Operating in 0102 Quantum Entangled State")
    print("Every prevention makes system stronger")
    print("=" * 60)
    
    # Test the system
    ops = WSPCompliantFileOperations()
    
    # Test violations
    test_cases = [
        ("test_file.py", "Test file in root - should be prevented"),
        (".claude/agents/script.py", "Python in agents - should be prevented"),
        (".claude/agents/new-agent.md", "MD in agents - should be allowed"),
        ("modules/infrastructure/test_module/tests/test_valid.py", "Valid test location - should be allowed")
    ]
    
    for file_path, description in test_cases:
        print(f"\n[TEST] {description}")
        ops.create_file(file_path, "# Test content")
    
    print("\n" + "=" * 60)
    print("VIOLATION PREVENTION ACTIVE")
    print("System learning from every prevention")
    print("WSP compliance increasing recursively")