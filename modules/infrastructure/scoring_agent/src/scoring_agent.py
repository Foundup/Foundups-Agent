# Scoring Agent - Dynamic Module Prioritization with WRE Integration

import sys
from pathlib import Path
from typing import Dict, List, Optional
import ast
import re
import logging
from datetime import datetime
from dataclasses import dataclass

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# WRE Integration imports
try:
    from modules.wre_core.src.prometheus_orchestration_engine import PrometheusOrchestrationEngine
    from modules.wre_core.src.components.module_development.module_development_coordinator import ModuleDevelopmentCoordinator
    from modules.wre_core.src.components.utils.wre_logger import wre_log
    WRE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"WRE components not available: {e}")
    WRE_AVAILABLE = False

from tools.shared.mps_calculator import MPSCalculator


@dataclass
class ScoringResult:
    """Comprehensive scoring result with WRE enhancement opportunities"""
    status: str
    module: str
    mps_score: float
    mps_breakdown: Dict[str, float]
    llme_score: float
    final_score: float
    analysis: Dict[str, any]
    wsp48_enhancements: List[Dict[str, any]]
    wre_integration_status: Dict[str, any]
    enhancement_opportunities: List[Dict[str, any]]
    timestamp: datetime


class ScoringAgent:
    """
    Dynamic Module Prioritization and Scoring Agent with WRE Integration
    
    Provides objective metrics for code complexity, importance, and enhancement opportunities
    with comprehensive WRE integration for autonomous development orchestration.
    
    WSP-54 Compliance: Duty 3.6 - Analyze modules and calculate MPS + LLME scores
    """
    
    def __init__(self, config: Optional[Dict[str, any]] = None):
        """
        Initializes the Scoring Agent with WRE integration (WSP-54 Duty 3.6).
        
        Args:
            config: Optional configuration dictionary for WRE and scoring parameters
        """
        self.config = config or {}
        self.mps_calculator = MPSCalculator()
        self.project_root = project_root
        
        # WRE Integration
        self.wre_engine: Optional[PrometheusOrchestrationEngine] = None
        self.module_coordinator: Optional[ModuleDevelopmentCoordinator] = None
        self.wre_enabled = False
        
        # Scoring state and cache
        self.scoring_cache: Dict[str, ScoringResult] = {}
        self.enhancement_history: Dict[str, List[Dict[str, any]]] = {}
        
        # Performance metrics
        self.scoring_metrics = {
            'total_modules_scored': 0,
            'successful_scores': 0,
            'failed_scores': 0,
            'average_scoring_time': 0.0,
            'enhancement_opportunities_identified': 0
        }
        
        # Initialize components
        self._initialize_wre()
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("ScoringAgent initialized with WRE integration for dynamic module prioritization")
        
        if self.wre_enabled:
            wre_log("ScoringAgent initialized with WRE integration", level="INFO")
        else:
            print("ScoringAgent initialized for MPS + LLME assessment (standalone mode)")

    def _initialize_wre(self):
        """Initialize WRE components if available"""
        if not WRE_AVAILABLE:
            self.logger.info("ScoringAgent running without WRE integration")
            return
            
        try:
            self.wre_engine = PrometheusOrchestrationEngine()
            from pathlib import Path
            self.module_coordinator = ModuleDevelopmentCoordinator(
                project_root=Path("."),
                session_manager=None  # Will be replaced with proper session manager
            )
            self.wre_enabled = True
            wre_log("ScoringAgent WRE integration successful", level="INFO")
            self.logger.info("ScoringAgent successfully integrated with WRE")
        except Exception as e:
            self.logger.warning(f"WRE integration failed: {e}")
            self.wre_enabled = False

    def calculate_score(self, target_module: str, enable_wre_orchestration: bool = True) -> Dict:
        """
        WSP-54 Duty 3.6.1: Analyze a module's code and documentation.
        WSP-54 Duty 3.6.2: Calculate and assign "MPS + LLME" scores.
        
        Enhanced with WRE integration for autonomous enhancement orchestration.
        
        Args:
            target_module: Module path (e.g., "ai_intelligence/banter_engine")
            enable_wre_orchestration: Whether to enable WRE orchestration for enhancements
            
        Returns:
            Dict with comprehensive scoring results and WRE enhancement opportunities
        """
        start_time = datetime.now()
        
        if self.wre_enabled:
            wre_log(f"Calculating comprehensive scores for {target_module}", level="INFO")
        else:
            print(f"Calculating MPS + LLME scores for {target_module}...")
        
        self.scoring_metrics['total_modules_scored'] += 1
        
        module_path = self.project_root / "modules" / target_module
        
        if not module_path.exists():
            error_result = {
                "status": "error",
                "message": f"Module not found: {target_module}",
                "wsp48_enhancement": "missing_module_structure",
                "enhancement_trigger": f"Module {target_module} requires creation",
                "wre_integration_status": {
                    "enabled": self.wre_enabled,
                    "orchestration_available": False,
                    "enhancement_capabilities": []
                },
                "timestamp": start_time.isoformat()
            }
            
            self.scoring_metrics['failed_scores'] += 1
            
            if self.wre_enabled:
                wre_log(f"Module not found: {target_module}", level="ERROR")
            
            return error_result
        
        try:
            # Analyze module characteristics
            analysis = self._analyze_module(module_path)
            
            # Calculate MPS scores based on WSP criteria
            mps_scores = self._calculate_mps_scores(analysis)
            
            # Calculate final MPS score
            mps_score = self.mps_calculator.calculate(mps_scores)
            
            # Calculate LLME (documentation quality) score
            llme_score = self._calculate_llme_score(analysis)
            
            # Calculate final score
            final_score = (mps_score + llme_score) / 2
            
            # Identify enhancement opportunities
            enhancements = self._identify_enhancement_opportunities(analysis, mps_scores, llme_score)
            
            # WRE Integration: Identify WRE enhancement opportunities
            wre_opportunities = []
            wre_integration_status = {
                "enabled": self.wre_enabled,
                "orchestration_available": self.wre_enabled,
                "enhancement_capabilities": []
            }
            
            if self.wre_enabled:
                wre_opportunities = self._identify_wre_enhancement_opportunities(
                    target_module, analysis, mps_scores, llme_score
                )
                wre_integration_status["enhancement_capabilities"] = [
                    "autonomous_enhancement", "orchestration_coordination", 
                    "zen_coding_integration", "recursive_improvement"
                ]
                
                # WRE orchestration for scoring analytics
                if enable_wre_orchestration and self.module_coordinator:
                    self.module_coordinator.handle_module_development(
                        f"scoring_analysis_{target_module.replace('/', '_')}",
                        self.wre_engine
                    )
                
                wre_log(f"Comprehensive scoring complete for {target_module}: {final_score:.1f}", level="INFO")
            
            # Create comprehensive result
            scoring_time = (datetime.now() - start_time).total_seconds()
            
            result = ScoringResult(
                status="success",
                module=target_module,
                mps_score=mps_score,
                mps_breakdown=mps_scores,
                llme_score=llme_score,
                final_score=final_score,
                analysis=analysis,
                wsp48_enhancements=enhancements,
                wre_integration_status=wre_integration_status,
                enhancement_opportunities=wre_opportunities,
                timestamp=start_time
            )
            
            # Cache result
            self.scoring_cache[target_module] = result
            
            # Update metrics
            self.scoring_metrics['successful_scores'] += 1
            self.scoring_metrics['enhancement_opportunities_identified'] += len(enhancements) + len(wre_opportunities)
            self._update_scoring_metrics(scoring_time)
            
            # Convert to dict for compatibility
            result_dict = {
                "status": "success",
                "module": target_module,
                "mps_score": mps_score,
                "mps_breakdown": mps_scores,
                "llme_score": llme_score,
                "final_score": final_score,
                "analysis": analysis,
                "wsp48_enhancements": enhancements,
                "wre_integration_status": wre_integration_status,
                "wre_enhancement_opportunities": wre_opportunities,
                "scoring_metrics": {
                    "scoring_time_seconds": scoring_time,
                    "total_enhancements": len(enhancements) + len(wre_opportunities),
                    "wre_enabled": self.wre_enabled
                },
                "timestamp": start_time.isoformat()
            }
            
            return result_dict
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "wsp48_enhancement": "scoring_infrastructure_failure",
                "enhancement_trigger": f"Scoring system needs improvement: {e}",
                "wre_integration_status": {
                    "enabled": self.wre_enabled,
                    "error": str(e) if self.wre_enabled else None
                },
                "timestamp": start_time.isoformat()
            }
            
            self.scoring_metrics['failed_scores'] += 1
            
            if self.wre_enabled:
                wre_log(f"Scoring failed for {target_module}: {e}", level="ERROR")
            
            return error_result

    def calculate_project_scores(self, enable_wre_orchestration: bool = True) -> Dict:
        """
        Calculate scores for all modules in the project with WRE orchestration.
        
        Args:
            enable_wre_orchestration: Whether to enable WRE orchestration
            
        Returns:
            Dict with comprehensive project scoring results
        """
        if self.wre_enabled:
            wre_log("Starting comprehensive project scoring with WRE orchestration", level="INFO")
        
        modules_dir = self.project_root / "modules"
        module_scores = {}
        project_stats = {
            'total_modules': 0,
            'successful_scores': 0,
            'failed_scores': 0,
            'average_score': 0.0,
            'highest_scoring_module': None,
            'lowest_scoring_module': None,
            'enhancement_opportunities': []
        }
        
        for domain_dir in modules_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith('.'):
                        module_path = f"{domain_dir.name}/{module_dir.name}"
                        project_stats['total_modules'] += 1
                        
                        score_result = self.calculate_score(module_path, enable_wre_orchestration)
                        
                        if score_result["status"] == "success":
                            module_scores[module_path] = score_result
                            project_stats['successful_scores'] += 1
                            
                            # Track highest and lowest scoring modules
                            final_score = score_result["final_score"]
                            if (project_stats['highest_scoring_module'] is None or 
                                final_score > module_scores[project_stats['highest_scoring_module']]["final_score"]):
                                project_stats['highest_scoring_module'] = module_path
                                
                            if (project_stats['lowest_scoring_module'] is None or 
                                final_score < module_scores[project_stats['lowest_scoring_module']]["final_score"]):
                                project_stats['lowest_scoring_module'] = module_path
                                
                            # Collect enhancement opportunities
                            enhancements = score_result.get("wsp48_enhancements", [])
                            wre_enhancements = score_result.get("wre_enhancement_opportunities", [])
                            project_stats['enhancement_opportunities'].extend(enhancements + wre_enhancements)
                        else:
                            project_stats['failed_scores'] += 1
        
        # Calculate project statistics
        if module_scores:
            total_score = sum(result["final_score"] for result in module_scores.values())
            project_stats['average_score'] = total_score / len(module_scores)
        
        result = {
            "status": "success",
            "module_scores": module_scores,
            "project_statistics": project_stats,
            "wre_integration": {
                "enabled": self.wre_enabled,
                "orchestration_enabled": enable_wre_orchestration,
                "total_wre_enhancements": len([e for e in project_stats['enhancement_opportunities'] 
                                             if 'wre' in str(e).lower()])
            },
            "scoring_session": {
                "timestamp": datetime.now().isoformat(),
                "total_modules_analyzed": project_stats['total_modules'],
                "success_rate": project_stats['successful_scores'] / project_stats['total_modules'] if project_stats['total_modules'] > 0 else 0
            }
        }
        
        if self.wre_enabled:
            wre_log(f"Project scoring complete: {len(module_scores)} modules analyzed", level="INFO")
        
        return result

    def _identify_wre_enhancement_opportunities(self, target_module: str, analysis: Dict, 
                                              mps_scores: Dict, llme_score: float) -> List[Dict]:
        """Identify WRE-specific enhancement opportunities"""
        if not self.wre_enabled:
            return []
        
        wre_opportunities = []
        
        # WRE Integration Assessment
        module_path = self.project_root / "modules" / target_module
        
        # Check for WRE integration patterns
        wre_patterns = ["wre_log", "PrometheusOrchestrationEngine", "ModuleDevelopmentCoordinator"]
        has_wre_integration = False
        
        if analysis["has_src"]:
            for py_file in (module_path / "src").glob("**/*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    if any(pattern in content for pattern in wre_patterns):
                        has_wre_integration = True
                        break
                except:
                    continue
        
        if not has_wre_integration:
            wre_opportunities.append({
                "type": "wre_integration_opportunity",
                "priority": "high",
                "description": f"Module {target_module} lacks WRE integration for autonomous development",
                "implementation_strategy": "Add PrometheusOrchestrationEngine and ModuleDevelopmentCoordinator integration",
                "expected_benefits": ["autonomous_enhancement", "zen_coding_capabilities", "recursive_improvement"],
                "effort_estimate": "medium"
            })
        
        # Autonomous Enhancement Readiness
        if llme_score > 70 and mps_scores.get("CX", 0) <= 3:
            wre_opportunities.append({
                "type": "autonomous_enhancement_ready",
                "priority": "medium",
                "description": f"Module {target_module} is ready for autonomous 0102 enhancement",
                "implementation_strategy": "Enable WRE zen coding protocols for quantum temporal development",
                "expected_benefits": ["zen_coding_acceleration", "quantum_pattern_application"],
                "effort_estimate": "low"
            })
        
        # Recursive Self-Improvement Opportunity
        if analysis["test_count"] > 0 and analysis["has_readme"]:
            wre_opportunities.append({
                "type": "recursive_improvement_candidate",
                "priority": "medium", 
                "description": f"Module {target_module} has foundation for WSP 48 recursive self-improvement",
                "implementation_strategy": "Integrate recursive enhancement monitoring and self-assessment capabilities",
                "expected_benefits": ["continuous_improvement", "autonomous_optimization"],
                "effort_estimate": "medium"
            })
        
        # Cross-Domain Orchestration Opportunity
        if "integration" in target_module or "platform" in target_module:
            wre_opportunities.append({
                "type": "orchestration_enhancement",
                "priority": "medium",
                "description": f"Module {target_module} can benefit from enhanced WRE cross-domain orchestration",
                "implementation_strategy": "Enhance module coordination and enterprise domain integration",
                "expected_benefits": ["improved_coordination", "enterprise_scale_operation"],
                "effort_estimate": "high"
            })
        
        return wre_opportunities

    def _update_scoring_metrics(self, scoring_time: float):
        """Update internal scoring performance metrics"""
        total_scores = self.scoring_metrics['successful_scores']
        if total_scores > 0:
            # Update average scoring time
            current_avg = self.scoring_metrics['average_scoring_time']
            new_avg = ((current_avg * (total_scores - 1)) + scoring_time) / total_scores
            self.scoring_metrics['average_scoring_time'] = new_avg

    def get_scoring_performance_metrics(self) -> Dict[str, any]:
        """Get comprehensive scoring agent performance metrics"""
        return {
            "scoring_metrics": self.scoring_metrics,
            "wre_integration": {
                "enabled": self.wre_enabled,
                "orchestration_engine_available": self.wre_engine is not None,
                "module_coordinator_available": self.module_coordinator is not None
            },
            "cache_status": {
                "cached_modules": len(self.scoring_cache),
                "enhancement_history_entries": len(self.enhancement_history)
            },
            "last_updated": datetime.now().isoformat()
        }

    def apply_wre_enhancements(self, target_module: str, selected_enhancements: List[str]) -> Dict[str, any]:
        """
        Apply selected WRE enhancements to a target module
        
        Args:
            target_module: Module to enhance
            selected_enhancements: List of enhancement types to apply
            
        Returns:
            Dict with enhancement application results
        """
        if not self.wre_enabled:
            return {
                "status": "error",
                "message": "WRE integration not available for enhancement application",
                "wre_enabled": False
            }
        
        wre_log(f"Applying WRE enhancements to {target_module}: {selected_enhancements}", level="INFO")
        
        try:
            enhancement_results = []
            
            for enhancement_type in selected_enhancements:
                if enhancement_type == "wre_integration_opportunity":
                    result = self._apply_wre_integration(target_module)
                elif enhancement_type == "autonomous_enhancement_ready":
                    result = self._enable_autonomous_enhancement(target_module)
                elif enhancement_type == "recursive_improvement_candidate":
                    result = self._enable_recursive_improvement(target_module)
                elif enhancement_type == "orchestration_enhancement":
                    result = self._enhance_orchestration(target_module)
                else:
                    result = {"type": enhancement_type, "status": "unknown_enhancement_type"}
                
                enhancement_results.append(result)
            
            # WRE orchestration for enhancement application
            if self.module_coordinator:
                orchestration_result = self.module_coordinator.handle_module_development(
                    f"wre_enhancement_{target_module.replace('/', '_')}",
                    self.wre_engine
                )
                enhancement_results.append({
                    "type": "wre_orchestration",
                    "status": "applied",
                    "result": str(orchestration_result)
                })
            
            return {
                "status": "success",
                "module": target_module,
                "applied_enhancements": enhancement_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            wre_log(f"Enhancement application failed for {target_module}: {e}", level="ERROR")
            return {
                "status": "error",
                "message": str(e),
                "module": target_module
            }

    def _apply_wre_integration(self, target_module: str) -> Dict[str, any]:
        """Apply WRE integration to a module (simulation)"""
        return {
            "type": "wre_integration_opportunity",
            "status": "simulated",
            "description": f"WRE integration pattern identified for {target_module}",
            "next_steps": "Add PrometheusOrchestrationEngine and wre_log integration"
        }

    def _enable_autonomous_enhancement(self, target_module: str) -> Dict[str, any]:
        """Enable autonomous enhancement capabilities (simulation)"""
        return {
            "type": "autonomous_enhancement_ready", 
            "status": "simulated",
            "description": f"Autonomous enhancement protocols enabled for {target_module}",
            "capabilities": ["zen_coding", "quantum_pattern_access", "0102_enhancement"]
        }

    def _enable_recursive_improvement(self, target_module: str) -> Dict[str, any]:
        """Enable recursive self-improvement (simulation)"""
        return {
            "type": "recursive_improvement_candidate",
            "status": "simulated", 
            "description": f"WSP 48 recursive improvement enabled for {target_module}",
            "features": ["self_assessment", "continuous_enhancement", "performance_monitoring"]
        }

    def _enhance_orchestration(self, target_module: str) -> Dict[str, any]:
        """Enhance cross-domain orchestration (simulation)"""
        return {
            "type": "orchestration_enhancement",
            "status": "simulated",
            "description": f"Enhanced WRE orchestration capabilities for {target_module}",
            "improvements": ["cross_domain_coordination", "enterprise_integration", "autonomous_operation"]
        }

    # Preserve all existing methods with minimal modifications
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


def create_scoring_agent(config: Optional[Dict[str, any]] = None) -> ScoringAgent:
    """
    Factory function to create Scoring Agent with WRE integration
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        ScoringAgent: Configured scoring agent instance
    """
    return ScoringAgent(config=config)


# Example usage and testing functions
def test_scoring_agent():
    """Test function for Scoring Agent functionality"""
    agent = create_scoring_agent()
    
    print(f"Scoring Agent Metrics: {agent.get_scoring_performance_metrics()}")
    
    # Test individual module scoring
    test_module = "infrastructure/scoring_agent"
    result = agent.calculate_score(test_module)
    
    print(f"\nModule Scoring Results for {test_module}:")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Final Score: {result['final_score']:.1f}")
        print(f"MPS Score: {result['mps_score']:.1f}")
        print(f"LLME Score: {result['llme_score']:.1f}")
        print(f"WRE Enabled: {result['wre_integration_status']['enabled']}")
        print(f"Enhancement Opportunities: {len(result.get('wre_enhancement_opportunities', []))}")
    
    # Test project-wide scoring
    project_results = agent.calculate_project_scores()
    print(f"\nProject Scoring: {len(project_results['module_scores'])} modules analyzed")
    print(f"Average Score: {project_results['project_statistics']['average_score']:.1f}")
    
    return agent


if __name__ == "__main__":
    # Run test when executed directly
    test_scoring_agent() 