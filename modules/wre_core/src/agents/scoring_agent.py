"""
ScoringAgent - WSP 37 Dynamic Scoring Retrieval

This agent implements the scoring_retrieval node from REMOTE_BUILD_PROTOTYPE flow.
Retrieves and sorts module priorities using WSP 37 composite scoring for autonomous
0102 operations.

WSP Compliance: WSP 37 (Scoring System), WSP 1 (Agentic Responsibility)
REMOTE_BUILD_PROTOTYPE: scoring_retrieval node implementation
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log

@dataclass
class ModuleScore:
    """Module scoring data structure for WSP 37 dynamic scoring"""
    module_name: str
    domain: str
    complexity: int
    importance: int
    deferability: int
    impact: int
    total_score: int
    status: str
    last_updated: str
    
@dataclass
class ScoringResult:
    """Scoring retrieval result for REMOTE_BUILD_PROTOTYPE flow"""
    sorted_module_list: List[ModuleScore]
    total_modules_scanned: int
    top_5_modules: List[ModuleScore]
    scoring_algorithm: str
    execution_timestamp: str

class ScoringAgent:
    """
    ScoringAgent - WSP 37 Dynamic Scoring Retrieval
    
    REMOTE_BUILD_PROTOTYPE Flow Implementation:
    - Retrieves module priorities using WSP 37 composite scoring
    - Sorts modules by dynamic priority calculation
    - Provides top 5 modules for menu rendering
    - Maintains real-time scoring updates
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).resolve().parent.parent.parent.parent.parent
        self.modules_path = self.project_root / "modules"
        self.last_scan_timestamp = None
        self.cached_scores: Dict[str, ModuleScore] = {}
        
    def retrieve_dynamic_scores(self) -> ScoringResult:
        """
        Main scoring retrieval function for REMOTE_BUILD_PROTOTYPE flow.
        
        Returns:
            ScoringResult: Complete scoring results with sorted module list
        """
        wre_log("📊 ScoringAgent: Retrieving WSP 37 dynamic scores", "INFO")
        
        try:
            # Scan all modules for current scores
            all_modules = self._scan_all_modules()
            
            # Sort by total score (descending)
            sorted_modules = sorted(all_modules, key=lambda x: x.total_score, reverse=True)
            
            # Get top 5 for menu rendering
            top_5_modules = sorted_modules[:5]
            
            # Update cache
            self.cached_scores = {module.module_name: module for module in all_modules}
            self.last_scan_timestamp = datetime.now().isoformat()
            
            # Create result for REMOTE_BUILD_PROTOTYPE flow
            result = ScoringResult(
                sorted_module_list=sorted_modules,
                total_modules_scanned=len(all_modules),
                top_5_modules=top_5_modules,
                scoring_algorithm="WSP_37_Dynamic_Composite",
                execution_timestamp=self.last_scan_timestamp
            )
            
            wre_log(f"📊 ScoringAgent: Retrieved {len(all_modules)} module scores, top 5 identified", "SUCCESS")
            return result
            
        except Exception as e:
            wre_log(f"❌ ScoringAgent: Failed to retrieve scores: {e}", "ERROR")
            raise
    
    def _scan_all_modules(self) -> List[ModuleScore]:
        """Scan all modules and calculate WSP 37 scores"""
        
        all_modules = []
        
        if not self.modules_path.exists():
            wre_log("⚠️ ScoringAgent: Modules directory not found", "WARNING")
            return all_modules
            
        # Scan each enterprise domain
        for domain_path in self.modules_path.iterdir():
            if domain_path.is_dir() and not domain_path.name.startswith('.'):
                domain_name = domain_path.name
                
                # Scan each module in domain
                for module_path in domain_path.iterdir():
                    if module_path.is_dir() and not module_path.name.startswith('.'):
                        module_name = module_path.name
                        
                        try:
                            module_score = self._calculate_module_score(module_path, domain_name, module_name)
                            all_modules.append(module_score)
                        except Exception as e:
                            wre_log(f"⚠️ ScoringAgent: Error scoring {module_name}: {e}", "WARNING")
                            continue
        
        return all_modules
    
    def _calculate_module_score(self, module_path: Path, domain_name: str, module_name: str) -> ModuleScore:
        """Calculate WSP 37 composite score for a module"""
        
        # Calculate WSP 37 scoring components
        complexity = self._assess_complexity(module_path)
        importance = self._assess_importance(module_path, domain_name)
        deferability = self._assess_deferability(module_path)
        impact = self._assess_impact(module_path, domain_name)
        
        # Calculate total score (WSP 37 formula)
        total_score = (complexity * 2) + (importance * 3) + (deferability * 1) + (impact * 2)
        
        # Determine module status
        status = self._assess_module_status(module_path)
        
        return ModuleScore(
            module_name=module_name,
            domain=domain_name,
            complexity=complexity,
            importance=importance,
            deferability=deferability,
            impact=impact,
            total_score=total_score,
            status=status,
            last_updated=datetime.now().isoformat()
        )
    
    def _assess_complexity(self, module_path: Path) -> int:
        """Assess module complexity (0-10 scale)"""
        
        complexity_score = 0
        
        # Check for source files
        src_path = module_path / "src"
        if src_path.exists():
            python_files = list(src_path.glob("**/*.py"))
            complexity_score += min(len(python_files), 5)  # Max 5 points for file count
            
            # Check total lines of code
            total_lines = 0
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    continue
            
            # Add complexity based on lines of code
            if total_lines > 2000:
                complexity_score += 5
            elif total_lines > 1000:
                complexity_score += 3
            elif total_lines > 500:
                complexity_score += 2
            elif total_lines > 100:
                complexity_score += 1
        
        return min(complexity_score, 10)
    
    def _assess_importance(self, module_path: Path, domain_name: str) -> int:
        """Assess module importance (0-10 scale)"""
        
        importance_score = 0
        
        # Domain-based importance
        domain_importance = {
            "infrastructure": 9,
            "wre_core": 10,
            "ai_intelligence": 8,
            "communication": 7,
            "platform_integration": 6,
            "gamification": 5,
            "foundups": 7,
            "blockchain": 6,
            "development": 4,
            "monitoring": 5
        }
        
        importance_score += domain_importance.get(domain_name, 3)
        
        # Check for critical files
        critical_files = ["__init__.py", "README.md", "requirements.txt"]
        for critical_file in critical_files:
            if (module_path / critical_file).exists():
                importance_score += 1
        
        return min(importance_score, 10)
    
    def _assess_deferability(self, module_path: Path) -> int:
        """Assess how deferrable the module is (0-10 scale, higher = more deferrable)"""
        
        deferability_score = 5  # Default moderate deferability
        
        # Check if module is actively being developed
        src_path = module_path / "src"
        if src_path.exists():
            # Check for recent modifications
            recent_files = []
            for py_file in src_path.glob("**/*.py"):
                try:
                    if py_file.stat().st_mtime > (datetime.now().timestamp() - 30 * 24 * 3600):  # 30 days
                        recent_files.append(py_file)
                except:
                    continue
            
            if recent_files:
                deferability_score -= 3  # Less deferrable if recently modified
        
        # Check for test files
        test_path = module_path / "tests"
        if test_path.exists() and list(test_path.glob("**/*.py")):
            deferability_score -= 2  # Less deferrable if has tests
        
        return max(0, min(deferability_score, 10))
    
    def _assess_impact(self, module_path: Path, domain_name: str) -> int:
        """Assess module impact on system (0-10 scale)"""
        
        impact_score = 0
        
        # Domain-based impact
        domain_impact = {
            "infrastructure": 9,
            "wre_core": 10,
            "ai_intelligence": 8,
            "communication": 7,
            "platform_integration": 6,
            "gamification": 4,
            "foundups": 6,
            "blockchain": 5,
            "development": 5,
            "monitoring": 6
        }
        
        impact_score += domain_impact.get(domain_name, 3)
        
        # Check for dependencies (rough estimate)
        module_json = module_path / "module.json"
        if module_json.exists():
            impact_score += 2
        
        return min(impact_score, 10)
    
    def _assess_module_status(self, module_path: Path) -> str:
        """Assess current module status"""
        
        # Check for key files to determine status
        has_src = (module_path / "src").exists()
        has_tests = (module_path / "tests").exists()
        has_readme = (module_path / "README.md").exists()
        
        if has_src and has_tests and has_readme:
            return "Active"
        elif has_src and has_readme:
            return "In Progress"
        elif has_src:
            return "Prototype"
        else:
            return "Inactive"
    
    def get_top_modules(self, count: int = 5) -> List[ModuleScore]:
        """Get top N modules by score"""
        
        if not self.cached_scores:
            result = self.retrieve_dynamic_scores()
            return result.top_5_modules[:count]
        
        sorted_modules = sorted(self.cached_scores.values(), key=lambda x: x.total_score, reverse=True)
        return sorted_modules[:count]
    
    def get_module_score(self, module_name: str) -> Optional[ModuleScore]:
        """Get score for specific module"""
        
        if module_name in self.cached_scores:
            return self.cached_scores[module_name]
        
        # Try to find and score the module
        for domain_path in self.modules_path.iterdir():
            if domain_path.is_dir():
                module_path = domain_path / module_name
                if module_path.exists():
                    try:
                        return self._calculate_module_score(module_path, domain_path.name, module_name)
                    except:
                        return None
        
        return None
    
    def refresh_scores(self) -> ScoringResult:
        """Force refresh of all module scores"""
        
        wre_log("🔄 ScoringAgent: Refreshing all module scores", "INFO")
        self.cached_scores.clear()
        return self.retrieve_dynamic_scores()

# Factory function for agent initialization
def create_scoring_agent(project_root: Path = None) -> ScoringAgent:
    """Factory function to create and initialize ScoringAgent"""
    return ScoringAgent(project_root) 