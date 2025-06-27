"""
WRE Module Prioritizer

Handles module priority scoring and roadmap generation using WSP_37 protocols.
This component determines which modules should be built next based on:
- MPS (Module Priority Score) calculations
- LLME (Level of Live Module Engagement) scoring
- Strategic value assessment
- Dependency analysis
- Risk and complexity factors

Core of the autonomous decision-making system for module development.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import sys
import json

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log
from tools.shared.mps_calculator import MPSCalculator


class ModulePrioritizer:
    """
    Handles module priority scoring and roadmap generation.
    
    Uses WSP_37 scoring protocols to determine:
    - Which modules to build first
    - LLME progression paths
    - Resource allocation priorities
    - Strategic development roadmaps
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.mps_calculator = MPSCalculator()
        self.module_scores: Dict[str, float] = {}
        self.roadmap_cache: Optional[List[Dict[str, Any]]] = None
        
    def calculate_module_priority(self, module_path: str, context: Dict[str, Any] = None) -> float:
        """Calculate MPS score for a specific module."""
        wre_log(f"📊 Calculating priority for module: {module_path}", "INFO")
        
        # Default scoring factors
        scores = {
            "IM": self._calculate_importance(module_path, context),
            "IP": self._calculate_impact(module_path, context),
            "ADV": self._calculate_advantage(module_path, context),
            "ADF": self._calculate_feasibility(module_path, context),
            "DF": self._calculate_dependency_factor(module_path),
            "RF": self._calculate_risk_factor(module_path),
            "CX": self._calculate_complexity(module_path)
        }
        
        priority_score = self.mps_calculator.calculate(scores)
        self.module_scores[module_path] = priority_score
        
        wre_log(f"📈 Priority Score for {module_path}: {priority_score:.2f}", "INFO")
        return priority_score
        
    def generate_development_roadmap(self, available_modules: List[str] = None) -> List[Dict[str, Any]]:
        """Generate a prioritized development roadmap."""
        if available_modules is None:
            available_modules = self._discover_modules()
            
        wre_log("🗺️ Generating development roadmap...", "INFO")
        
        # Calculate priorities for all modules
        module_priorities = []
        for module_path in available_modules:
            try:
                priority = self.calculate_module_priority(module_path)
                module_info = self._analyze_module_info(module_path)
                
                module_priorities.append({
                    "module_path": module_path,
                    "priority_score": priority,
                    "llme_current": module_info.get("llme_current", "000"),
                    "llme_target": module_info.get("llme_target", "111"),
                    "stage": module_info.get("stage", "POC"),
                    "dependencies": module_info.get("dependencies", []),
                    "estimated_effort": self._estimate_effort(module_path),
                    "strategic_value": self._assess_strategic_value(module_path)
                })
            except Exception as e:
                wre_log(f"⚠️ Error analyzing module {module_path}: {e}", "WARNING")
                
        # Sort by priority score (descending)
        module_priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Apply dependency ordering
        roadmap = self._apply_dependency_ordering(module_priorities)
        
        self.roadmap_cache = roadmap
        self._log_roadmap_summary(roadmap)
        
        return roadmap
        
    def get_next_module_recommendation(self) -> Optional[Dict[str, Any]]:
        """Get the next recommended module to work on."""
        if not self.roadmap_cache:
            self.generate_development_roadmap()
            
        # Find the highest priority module that's ready to work on
        for module in self.roadmap_cache:
            if self._is_module_ready(module):
                wre_log(f"🎯 Next recommendation: {module['module_path']} (Score: {module['priority_score']:.2f})", "INFO")
                return module
                
        return None
        
    def _calculate_importance(self, module_path: str, context: Dict[str, Any] = None) -> int:
        """Calculate importance score (1-5)."""
        # Core infrastructure modules get highest importance
        if "core" in module_path or "wre_core" in module_path:
            return 5
        if "infrastructure" in module_path:
            return 4
        if "ai_intelligence" in module_path:
            return 4
        if "platform_integration" in module_path:
            return 3
        return 2
        
    def _calculate_impact(self, module_path: str, context: Dict[str, Any] = None) -> int:
        """Calculate potential impact score (1-5)."""
        # Modules that affect many other modules have high impact
        if "core" in module_path:
            return 5
        if "agent" in module_path or "engine" in module_path:
            return 4
        if "integration" in module_path:
            return 4
        return 3
        
    def _calculate_advantage(self, module_path: str, context: Dict[str, Any] = None) -> int:
        """Calculate strategic advantage score (1-5)."""
        # AI and automation modules provide strategic advantage
        if "ai_intelligence" in module_path:
            return 5
        if "agent" in module_path:
            return 4
        if "automation" in module_path:
            return 4
        return 3
        
    def _calculate_feasibility(self, module_path: str, context: Dict[str, Any] = None) -> int:
        """Calculate development feasibility (1-5)."""
        # Simpler modules are more feasible
        module_info = self._analyze_module_info(module_path)
        complexity = module_info.get("complexity", "medium")
        
        if complexity == "low":
            return 5
        elif complexity == "medium":
            return 4
        elif complexity == "high":
            return 2
        return 3
        
    def _calculate_dependency_factor(self, module_path: str) -> int:
        """Calculate dependency complexity (1-5, lower is better)."""
        dependencies = self._get_module_dependencies(module_path)
        if len(dependencies) == 0:
            return 5  # No dependencies = easy
        elif len(dependencies) <= 2:
            return 4
        elif len(dependencies) <= 4:
            return 3
        else:
            return 2  # Many dependencies = complex
            
    def _calculate_risk_factor(self, module_path: str) -> int:
        """Calculate development risk (1-5, lower is better)."""
        # Experimental or unproven modules have higher risk
        if "experimental" in module_path or "beta" in module_path:
            return 2
        if "integration" in module_path:
            return 3  # Integration always has risks
        return 4  # Most modules have manageable risk
        
    def _calculate_complexity(self, module_path: str) -> int:
        """Calculate complexity score (1-5, lower is better)."""
        # AI and ML modules tend to be more complex
        if "ai_intelligence" in module_path and "rESP" in module_path:
            return 2  # Very complex
        if "blockchain" in module_path:
            return 2
        if "multi_agent" in module_path:
            return 3
        return 4  # Most modules have moderate complexity
        
    def _discover_modules(self) -> List[str]:
        """Discover available modules in the project."""
        modules_dir = self.project_root / "modules"
        if not modules_dir.exists():
            return []
            
        modules = []
        for item in modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                modules.append(str(item.relative_to(modules_dir)))
                
        return modules
        
    def _analyze_module_info(self, module_path: str) -> Dict[str, Any]:
        """Analyze module information from README and other files."""
        module_dir = self.project_root / "modules" / module_path
        
        info = {
            "llme_current": "000",
            "llme_target": "111",
            "stage": "POC",
            "dependencies": [],
            "complexity": "medium"
        }
        
        # Try to read module.json for structured info
        module_json_path = module_dir / "module.json"
        if module_json_path.exists():
            try:
                with open(module_json_path) as f:
                    module_data = json.load(f)
                    info.update(module_data)
            except Exception as e:
                wre_log(f"⚠️ Error reading module.json for {module_path}: {e}", "WARNING")
                
        return info
        
    def _get_module_dependencies(self, module_path: str) -> List[str]:
        """Get module dependencies."""
        module_info = self._analyze_module_info(module_path)
        return module_info.get("dependencies", [])
        
    def _estimate_effort(self, module_path: str) -> str:
        """Estimate development effort."""
        complexity = self._calculate_complexity(module_path)
        if complexity >= 4:
            return "Low"
        elif complexity == 3:
            return "Medium"
        else:
            return "High"
            
    def _assess_strategic_value(self, module_path: str) -> str:
        """Assess strategic value."""
        importance = self._calculate_importance(module_path)
        impact = self._calculate_impact(module_path)
        
        avg_score = (importance + impact) / 2
        if avg_score >= 4.5:
            return "Critical"
        elif avg_score >= 3.5:
            return "High"
        elif avg_score >= 2.5:
            return "Medium"
        else:
            return "Low"
            
    def _apply_dependency_ordering(self, module_priorities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply dependency ordering to the roadmap."""
        # Simple dependency resolution - move modules with dependencies later
        ordered_modules = []
        remaining_modules = module_priorities.copy()
        
        while remaining_modules:
            progress_made = False
            
            for module in remaining_modules[:]:
                dependencies = module.get("dependencies", [])
                
                # Check if all dependencies are satisfied
                if all(dep in [m["module_path"] for m in ordered_modules] for dep in dependencies):
                    ordered_modules.append(module)
                    remaining_modules.remove(module)
                    progress_made = True
                    
            # If no progress, add remaining modules (circular dependencies or missing deps)
            if not progress_made and remaining_modules:
                ordered_modules.extend(remaining_modules)
                break
                
        return ordered_modules
        
    def _is_module_ready(self, module: Dict[str, Any]) -> bool:
        """Check if a module is ready to be worked on."""
        # Check if dependencies are satisfied
        dependencies = module.get("dependencies", [])
        
        for dep in dependencies:
            dep_module = self.project_root / "modules" / dep
            if not dep_module.exists():
                return False
                
        return True
        
    def _log_roadmap_summary(self, roadmap: List[Dict[str, Any]]):
        """Log a summary of the generated roadmap."""
        wre_log("📋 Development Roadmap Generated:", "INFO")
        
        for i, module in enumerate(roadmap[:5], 1):  # Show top 5
            wre_log(f"  {i}. {module['module_path']} (Score: {module['priority_score']:.2f}, Value: {module['strategic_value']})", "INFO")
            
        if len(roadmap) > 5:
            wre_log(f"  ... and {len(roadmap) - 5} more modules", "INFO") 