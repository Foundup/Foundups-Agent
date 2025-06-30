# Placeholder for the Scoring Agent

import sys
from pathlib import Path
from typing import Dict, List, Optional
import ast
import re

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.shared.mps_calculator import MPSCalculator

class ScoringAgent:
    def __init__(self):
        """Initializes the Scoring Agent (WSP-54 Duty 3.6)."""
        self.mps_calculator = MPSCalculator()
        self.project_root = project_root
        print("ScoringAgent initialized for MPS + LLME assessment.")

    def calculate_score(self, target_module: str) -> Dict:
        """
        WSP-54 Duty 3.6.1: Analyze a module's code and documentation.
        WSP-54 Duty 3.6.2: Calculate and assign "MPS + LLME" scores.
        
        Args:
            target_module: Module path (e.g., "ai_intelligence/banter_engine")
            
        Returns:
            Dict with scoring results and WSP_48 enhancement opportunities
        """
        print(f"Calculating MPS + LLME scores for {target_module}...")
        
        module_path = self.project_root / "modules" / target_module
        
        if not module_path.exists():
            return {
                "status": "error",
                "message": f"Module not found: {target_module}",
                "wsp48_enhancement": "missing_module_structure",
                "enhancement_trigger": f"Module {target_module} requires creation"
            }
        
        try:
            # Analyze module characteristics
            analysis = self._analyze_module(module_path)
            
            # Calculate MPS scores based on WSP criteria
            mps_scores = self._calculate_mps_scores(analysis)
            
            # Calculate final MPS score
            mps_score = self.mps_calculator.calculate(mps_scores)
            
            # Calculate LLME (documentation quality) score
            llme_score = self._calculate_llme_score(analysis)
            
            # Determine overall score and enhancement opportunities
            final_score = (mps_score + llme_score) / 2
            enhancements = self._identify_enhancement_opportunities(analysis, mps_scores, llme_score)
            
            return {
                "status": "success",
                "module": target_module,
                "mps_score": mps_score,
                "mps_breakdown": mps_scores,
                "llme_score": llme_score,
                "final_score": final_score,
                "analysis": analysis,
                "wsp48_enhancements": enhancements
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "wsp48_enhancement": "scoring_infrastructure_failure",
                "enhancement_trigger": f"Scoring system needs improvement: {e}"
            }

    def calculate_project_scores(self) -> Dict:
        """Calculate scores for all modules in the project."""
        modules_dir = self.project_root / "modules"
        module_scores = {}
        
        for domain_dir in modules_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith('.'):
                        module_path = f"{domain_dir.name}/{module_dir.name}"
                        score_result = self.calculate_score(module_path)
                        if score_result["status"] == "success":
                            module_scores[module_path] = score_result
        
        return {
            "status": "success",
            "module_scores": module_scores,
            "total_modules": len(module_scores)
        }

    def _analyze_module(self, module_path: Path) -> Dict:
        """Analyze module structure and characteristics."""
        analysis = {
            "has_readme": (module_path / "README.md").exists(),
            "has_src": (module_path / "src").exists(),
            "has_tests": (module_path / "tests").exists(),
            "has_init": (module_path / "__init__.py").exists(),
            "has_requirements": (module_path / "requirements.txt").exists() or (module_path / "module.json").exists(),
            "test_count": 0,
            "src_file_count": 0,
            "complexity_score": 0,
            "documentation_quality": 0,
            "dependency_count": 0
        }
        
        # Count source files
        if analysis["has_src"]:
            src_files = list((module_path / "src").glob("**/*.py"))
            analysis["src_file_count"] = len([f for f in src_files if f.name != "__init__.py"])
        
        # Count test files
        if analysis["has_tests"]:
            test_files = list((module_path / "tests").glob("**/test_*.py"))
            analysis["test_count"] = len(test_files)
        
        # Analyze README quality
        if analysis["has_readme"]:
            readme_content = (module_path / "README.md").read_text(encoding='utf-8')
            analysis["documentation_quality"] = self._analyze_readme_quality(readme_content)
        
        # Analyze code complexity
        if analysis["has_src"]:
            analysis["complexity_score"] = self._analyze_code_complexity(module_path / "src")
        
        # Count dependencies
        analysis["dependency_count"] = self._count_dependencies(module_path)
        
        return analysis

    def _calculate_mps_scores(self, analysis: Dict) -> Dict:
        """Calculate MPS component scores based on module analysis."""
        return {
            "IM": 5 if "core" in str(analysis) or "wre_core" in str(analysis) else 3,  # Importance
            "IP": min(5, 1 + analysis["test_count"]),  # Impact Probability
            "ADV": min(5, 1 + analysis["documentation_quality"]),  # Data Value
            "ADF": 5 if analysis["test_count"] > 0 else 1,  # Development Feasibility
            "DF": min(5, 1 + analysis["dependency_count"]),  # Dependency Factor
            "RF": max(1, min(5, analysis["complexity_score"])),  # Risk Factor
            "CX": max(1, min(5, analysis["src_file_count"]))  # Complexity
        }

    def _calculate_llme_score(self, analysis: Dict) -> float:
        """Calculate LLME (documentation quality) score."""
        base_score = 50  # Start with neutral score
        
        # README quality bonus
        base_score += analysis["documentation_quality"] * 10
        
        # Structure bonuses
        if analysis["has_readme"]: base_score += 10
        if analysis["has_src"]: base_score += 10
        if analysis["has_tests"]: base_score += 10
        if analysis["has_init"]: base_score += 5
        if analysis["has_requirements"]: base_score += 5
        
        # Test coverage bonus
        if analysis["test_count"] > 0 and analysis["src_file_count"] > 0:
            test_ratio = analysis["test_count"] / analysis["src_file_count"]
            base_score += min(20, test_ratio * 20)
        
        return min(100, max(0, base_score))

    def _analyze_readme_quality(self, content: str) -> float:
        """Analyze README.md quality (0-5 scale)."""
        quality_score = 0
        
        # Check for key sections
        if "# " in content: quality_score += 1  # Has title
        if "## " in content: quality_score += 1  # Has sections
        if "```" in content: quality_score += 1  # Has code examples
        if len(content) > 500: quality_score += 1  # Substantial content
        if "WSP" in content: quality_score += 1  # WSP compliance reference
        
        return quality_score

    def _analyze_code_complexity(self, src_path: Path) -> float:
        """Analyze code complexity (1-5 scale)."""
        total_complexity = 0
        file_count = 0
        
        for py_file in src_path.glob("**/*.py"):
            if py_file.name == "__init__.py":
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                complexity = self._calculate_cyclomatic_complexity(tree)
                total_complexity += complexity
                file_count += 1
            except:
                continue
        
        if file_count == 0:
            return 1
        
        avg_complexity = total_complexity / file_count
        return min(5, max(1, avg_complexity / 2))  # Scale to 1-5

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of AST."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity

    def _count_dependencies(self, module_path: Path) -> int:
        """Count module dependencies."""
        dependency_count = 0
        
        # Check requirements.txt
        req_file = module_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            dependency_count += len([line for line in content.split('\n') if line.strip() and not line.startswith('#')])
        
        # Check module.json
        json_file = module_path / "module.json"
        if json_file.exists():
            try:
                import json
                data = json.loads(json_file.read_text())
                deps = data.get('dependencies', [])
                dependency_count += len(deps)
            except:
                pass
        
        return dependency_count

    def _identify_enhancement_opportunities(self, analysis: Dict, mps_scores: Dict, llme_score: float) -> List[Dict]:
        """Identify WSP_48 enhancement opportunities."""
        enhancements = []
        
        # Documentation improvements
        if llme_score < 70:
            enhancements.append({
                "type": "documentation_enhancement",
                "current_score": llme_score,
                "target_score": 80,
                "priority": "medium",
                "description": "README and documentation quality below target"
            })
        
        # Test coverage improvements
        if analysis["test_count"] == 0:
            enhancements.append({
                "type": "test_implementation",
                "priority": "critical",
                "description": "Module lacks test coverage"
            })
        elif analysis["src_file_count"] > 0:
            test_ratio = analysis["test_count"] / analysis["src_file_count"]
            if test_ratio < 0.8:
                enhancements.append({
                    "type": "test_coverage_improvement",
                    "current_ratio": test_ratio,
                    "target_ratio": 1.0,
                    "priority": "high" if test_ratio < 0.5 else "medium"
                })
        
        # Structure improvements
        if not analysis["has_requirements"]:
            enhancements.append({
                "type": "dependency_documentation",
                "priority": "low",
                "description": "Module lacks dependency manifest"
            })
        
        # Complexity management
        if mps_scores["CX"] > 4:
            enhancements.append({
                "type": "complexity_reduction",
                "current_complexity": mps_scores["CX"],
                "priority": "medium",
                "description": "High complexity suggests refactoring opportunities"
            })
        
        return enhancements 