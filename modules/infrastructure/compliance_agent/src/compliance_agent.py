# Compliance Agent - WSP Protocol Enforcement with WRE Integration

from pathlib import Path
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json

# WRE Integration imports
try:
    from modules.wre_core.src.prometheus_orchestration_engine import PrometheusOrchestrationEngine
    from modules.wre_core.src.components.module_development.module_development_coordinator import ModuleDevelopmentCoordinator
    from modules.wre_core.src.utils.logging_utils import wre_log
    WRE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"WRE components not available: {e}")
    WRE_AVAILABLE = False


@dataclass
class ComplianceViolation:
    """Represents a WSP compliance violation with detailed context"""
    violation_type: str
    severity: str  # critical, high, medium, low
    module_path: str
    description: str
    wsp_protocol: str
    remediation_suggestion: str
    auto_fixable: bool
    timestamp: datetime
    

@dataclass
class ComplianceReport:
    """Comprehensive compliance report with WRE enhancement opportunities"""
    module_path: str
    is_compliant: bool
    violations: List[ComplianceViolation]
    compliance_score: float
    wsp_protocols_checked: List[str]
    enhancement_opportunities: List[Dict[str, Any]]
    wre_orchestration_recommendations: List[Dict[str, Any]]
    timestamp: datetime


class ComplianceAgent:
    """
    WSP Protocol Enforcement Agent with WRE Integration
    
    Provides comprehensive WSP compliance checking, violation detection, and 
    autonomous enhancement recommendations with WRE orchestration capabilities.
    
    WSP-54 Compliance: Guardian agent for WSP framework structural integrity
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initializes the Compliance Agent with WRE integration.
        
        Args:
            config: Optional configuration for compliance checking and WRE integration
        """
        self.config = config or {}
        self.errors: List[str] = []
        
        # WRE Integration
        self.wre_engine: Optional[PrometheusOrchestrationEngine] = None
        self.module_coordinator: Optional[ModuleDevelopmentCoordinator] = None
        self.wre_enabled = False
        
        # Compliance state tracking
        self.compliance_cache: Dict[str, ComplianceReport] = {}
        self.violation_history: Dict[str, List[ComplianceViolation]] = {}
        
        # WSP Protocol definitions for checking
        self.wsp_protocols = {
            "WSP_3": "Enterprise Domain Organization",
            "WSP_4": "FMAS Validation Protocol", 
            "WSP_5": "Test Coverage Requirements",
            "WSP_6": "Test Audit Coverage Verification",
            "WSP_11": "Interface Documentation Standards",
            "WSP_12": "Dependency Management",
            "WSP_22": "Module ModLog and Roadmap Protocol",
            "WSP_34": "Test Documentation Protocol",
            "WSP_40": "Architectural Coherence Protocol",
            "WSP_49": "Module Directory Structure Standardization",
            "WSP_54": "WRE Agent Duties Specification",
            "WSP_71": "Secrets Management Protocol"
        }
        
        # Security violation handling (WSP 4 + WSP 71)
        self.security_thresholds = {
            "HIGH": "CRITICAL_VIOLATION",
            "MEDIUM": "WARNING_VIOLATION", 
            "LOW": "INFO_VIOLATION"
        }
        
        # Performance metrics
        self.compliance_metrics = {
            'total_modules_checked': 0,
            'compliant_modules': 0,
            'non_compliant_modules': 0,
            'violations_detected': 0,
            'auto_fixes_available': 0,
            'average_compliance_score': 0.0
        }
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_wre()
        self.logger.info("ComplianceAgent initialized with WRE integration for WSP protocol enforcement")
        
        if self.wre_enabled:
            wre_log("ComplianceAgent initialized with WRE integration", level="INFO")
        else:
            print("ComplianceAgent initialized for WSP compliance checking.")

    def _initialize_wre(self):
        """Initialize WRE components if available"""
        if not WRE_AVAILABLE:
            self.logger.info("ComplianceAgent running without WRE integration")
            return
            
        try:
            self.wre_engine = PrometheusOrchestrationEngine()
            self.module_coordinator = ModuleDevelopmentCoordinator()
            self.wre_enabled = True
            wre_log("ComplianceAgent WRE integration successful", level="INFO")
            self.logger.info("ComplianceAgent successfully integrated with WRE")
        except Exception as e:
            self.logger.warning(f"WRE integration failed: {e}")
            self.wre_enabled = False

    def run_check(self, module_path_str: str, enable_wre_orchestration: bool = True) -> dict:
        """
        Runs a comprehensive WSP compliance check on a given module directory.
        
        Enhanced with WRE integration for autonomous enhancement orchestration.
        
        Args:
            module_path_str: The string path to the module to be checked
            enable_wre_orchestration: Whether to enable WRE orchestration for enhancements

        Returns:
            A dictionary containing comprehensive compliance status and enhancement opportunities
        """
        start_time = datetime.now()
        
        if self.wre_enabled:
            wre_log(f"Running comprehensive compliance check on {module_path_str}", level="INFO")
        else:
            print(f"ComplianceAgent: Running compliance check on '{module_path_str}'...")
        
        self.errors = []
        module_path = Path(module_path_str)
        self.compliance_metrics['total_modules_checked'] += 1

        if not module_path.is_dir():
            error_result = {
                "compliant": False,
                "errors": [f"Module path does not exist or is not a directory: {module_path_str}"],
                "compliance_score": 0.0,
                "wre_integration_status": {
                    "enabled": self.wre_enabled,
                    "orchestration_available": False
                },
                "timestamp": start_time.isoformat()
            }
            self.compliance_metrics['non_compliant_modules'] += 1
            return error_result

        try:
            # Comprehensive compliance checking
            violations = []
            
            # Core compliance checks
            violations.extend(self._check_directory_structure(module_path))
            violations.extend(self._check_mandatory_files(module_path))
            violations.extend(self._check_test_file_correspondence(module_path))
            violations.extend(self._check_wsp_documentation(module_path))
            violations.extend(self._check_enterprise_domain_compliance(module_path))
            violations.extend(self._check_dependency_management(module_path))
            
            # Calculate compliance metrics
            is_compliant = len(violations) == 0
            compliance_score = self._calculate_compliance_score(violations)
            
            # Identify enhancement opportunities
            enhancement_opportunities = self._identify_enhancement_opportunities(module_path, violations)
            
            # WRE Integration: Orchestration recommendations
            wre_recommendations = []
            if self.wre_enabled:
                wre_recommendations = self._generate_wre_orchestration_recommendations(
                    module_path_str, violations, compliance_score
                )
                
                # WRE orchestration for compliance analysis
                if enable_wre_orchestration and self.module_coordinator:
                    self.module_coordinator.handle_module_development(
                        f"compliance_analysis_{module_path_str.replace('/', '_')}",
                        self.wre_engine
                    )
                
                wre_log(f"Compliance check complete for {module_path_str}: {compliance_score:.1%}", level="INFO")
            
            # Create comprehensive report
            processing_time = (datetime.now() - start_time).total_seconds()
            
            report = ComplianceReport(
                module_path=module_path_str,
                is_compliant=is_compliant,
                violations=[self._create_violation_object(v) for v in violations],
                compliance_score=compliance_score,
                wsp_protocols_checked=list(self.wsp_protocols.keys()),
                enhancement_opportunities=enhancement_opportunities,
                wre_orchestration_recommendations=wre_recommendations,
                timestamp=start_time
            )
            
            # Cache the report
            self.compliance_cache[module_path_str] = report
            
            # Update metrics
            if is_compliant:
                self.compliance_metrics['compliant_modules'] += 1
            else:
                self.compliance_metrics['non_compliant_modules'] += 1
            
            self.compliance_metrics['violations_detected'] += len(violations)
            self.compliance_metrics['auto_fixes_available'] += sum(
                1 for opp in enhancement_opportunities if opp.get('auto_fixable', False)
            )
            self._update_average_compliance_score(compliance_score)
            
            # Convert to dict for compatibility  
            result = {
                "compliant": is_compliant,
                "errors": [v["description"] for v in violations],  # Backward compatibility
                "compliance_score": compliance_score,
                "violations": [self._violation_to_dict(v) for v in report.violations],
                "wsp_protocols_checked": report.wsp_protocols_checked,
                "enhancement_opportunities": enhancement_opportunities,
                "wre_integration_status": {
                    "enabled": self.wre_enabled,
                    "orchestration_available": self.wre_enabled,
                    "recommendations": wre_recommendations
                },
                "performance_metrics": {
                    "processing_time_seconds": processing_time,
                    "total_checks_performed": len(self.wsp_protocols),
                    "violations_found": len(violations)
                },
                "timestamp": start_time.isoformat()
            }
            
            # Output results
            if is_compliant:
                if self.wre_enabled:
                    wre_log(f"Module {module_path_str} is WSP compliant", level="SUCCESS")
                else:
                    print(f"ComplianceAgent: '{module_path_str}' is compliant.")
            else:
                if self.wre_enabled:
                    wre_log(f"Module {module_path_str} has {len(violations)} compliance violations", level="WARNING")
                else:
                    print(f"ComplianceAgent: '{module_path_str}' is NOT compliant. Found {len(violations)} errors.")
                    for violation in violations:
                        print(f"  - {violation['description']}")
            
            return result
            
        except Exception as e:
            error_result = {
                "compliant": False,
                "errors": [f"Compliance check failed: {str(e)}"],
                "compliance_score": 0.0,
                "wre_integration_status": {
                    "enabled": self.wre_enabled,
                    "error": str(e) if self.wre_enabled else None
                },
                "timestamp": start_time.isoformat()
            }
            
            self.compliance_metrics['non_compliant_modules'] += 1
            
            if self.wre_enabled:
                wre_log(f"Compliance check failed for {module_path_str}: {e}", level="ERROR")
            
            return error_result

    def _check_directory_structure(self, module_path: Path) -> List[Dict[str, Any]]:
        """Duty 1: Verify 'src' and 'tests' subdirectories exist."""
        violations = []
        
        if not (module_path / "src").is_dir():
            violations.append({
                "type": "missing_directory",
                "severity": "critical",
                "description": f"Missing 'src' directory in {module_path}",
                "wsp_protocol": "WSP_49",
                "remediation": "Create src/ directory with __init__.py",
                "auto_fixable": True
            })
            
        if not (module_path / "tests").is_dir():
            violations.append({
                "type": "missing_directory", 
                "severity": "critical",
                "description": f"Missing 'tests' directory in {module_path}",
                "wsp_protocol": "WSP_49",
                "remediation": "Create tests/ directory with README.md",
                "auto_fixable": True
            })
            
        return violations

    def _check_mandatory_files(self, module_path: Path) -> List[Dict[str, Any]]:
        """Duty 2: Ensure mandatory files exist."""
        violations = []
        
        required_files = {
            "README.md": {"wsp": "WSP_22", "severity": "high"},
            "__init__.py": {"wsp": "WSP_49", "severity": "medium"}
        }
        
        for file_name, file_info in required_files.items():
            if not (module_path / file_name).is_file():
                violations.append({
                    "type": "missing_file",
                    "severity": file_info["severity"],
                    "description": f"Missing mandatory file: {file_name} in {module_path}",
                    "wsp_protocol": file_info["wsp"],
                    "remediation": f"Create {file_name} following WSP template",
                    "auto_fixable": True
                })
        
        # Check tests/README.md
        if not (module_path / "tests" / "README.md").is_file():
            violations.append({
                "type": "missing_file",
                "severity": "medium",
                "description": f"Missing mandatory file: tests/README.md in {module_path}",
                "wsp_protocol": "WSP_34",
                "remediation": "Create tests/README.md with test documentation",
                "auto_fixable": True
            })
            
        return violations

    def _check_test_file_correspondence(self, module_path: Path) -> List[Dict[str, Any]]:
        """Duty 3: Verify test files correspond to source files."""
        violations = []
        src_path = module_path / "src"
        tests_path = module_path / "tests"
        
        if not src_path.exists() or not tests_path.exists():
            return violations  # Already flagged in directory structure check
        
        # Find Python files in src (excluding __init__.py)
        src_files = [f for f in src_path.glob("**/*.py") if f.name != "__init__.py"]
        
        for src_file in src_files:
            # Expected test file name
            expected_test_name = f"test_{src_file.stem}.py"
            expected_test_path = tests_path / expected_test_name
            
            if not expected_test_path.exists():
                violations.append({
                    "type": "missing_test_file",
                    "severity": "high",
                    "description": f"Missing test file {expected_test_name} for source file {src_file.name}",
                    "wsp_protocol": "WSP_6",
                    "remediation": f"Create {expected_test_path} with appropriate test cases",
                    "auto_fixable": False
                })
                
        return violations

    def _check_wsp_documentation(self, module_path: Path) -> List[Dict[str, Any]]:
        """Check WSP protocol documentation compliance."""
        violations = []
        
        readme_path = module_path / "README.md"
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8')
                
                # Check for WSP references
                if "WSP" not in content:
                    violations.append({
                        "type": "missing_wsp_reference",
                        "severity": "medium",
                        "description": f"README.md lacks WSP protocol references",
                        "wsp_protocol": "WSP_22",
                        "remediation": "Add WSP protocol references and compliance status",
                        "auto_fixable": False
                    })
                
                # Check for Windsurf Protocol recursive prompt
                if "🌀 Windsurf Protocol" not in content:
                    violations.append({
                        "type": "missing_recursive_prompt",
                        "severity": "low",
                        "description": f"README.md lacks WSP recursive prompt integration",
                        "wsp_protocol": "WSP_22",
                        "remediation": "Add WSP recursive prompt section",
                        "auto_fixable": False
                    })
                    
            except Exception as e:
                violations.append({
                    "type": "documentation_read_error",
                    "severity": "medium",
                    "description": f"Could not read README.md: {e}",
                    "wsp_protocol": "WSP_22",
                    "remediation": "Fix README.md encoding and content issues",
                    "auto_fixable": False
                })
                
        return violations

    def _check_enterprise_domain_compliance(self, module_path: Path) -> List[Dict[str, Any]]:
        """Check enterprise domain organization compliance (WSP 3)."""
        violations = []
        
        # Validate module is in proper enterprise domain
        path_parts = module_path.parts
        if "modules" in path_parts:
            modules_index = path_parts.index("modules")
            if len(path_parts) > modules_index + 1:
                domain = path_parts[modules_index + 1]
                valid_domains = [
                    "ai_intelligence", "communication", "platform_integration",
                    "infrastructure", "monitoring", "development", "foundups",
                    "gamification", "blockchain", "wre_core"
                ]
                
                if domain not in valid_domains:
                    violations.append({
                        "type": "invalid_enterprise_domain",
                        "severity": "high",
                        "description": f"Module in invalid enterprise domain: {domain}",
                        "wsp_protocol": "WSP_3",
                        "remediation": f"Move module to appropriate enterprise domain: {valid_domains}",
                        "auto_fixable": False
                    })
                    
        return violations

    def _check_dependency_management(self, module_path: Path) -> List[Dict[str, Any]]:
        """Check dependency management compliance (WSP 12)."""
        violations = []
        
        # Check for dependency declaration
        has_requirements = (module_path / "requirements.txt").exists()
        has_module_json = (module_path / "module.json").exists()
        
        if not has_requirements and not has_module_json:
            violations.append({
                "type": "missing_dependency_declaration",
                "severity": "medium",
                "description": f"Module lacks dependency declaration (requirements.txt or module.json)",
                "wsp_protocol": "WSP_12",
                "remediation": "Create requirements.txt or module.json with dependencies",
                "auto_fixable": True
            })
            
        return violations

    def _calculate_compliance_score(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate overall compliance score based on violations."""
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {
            "critical": 1.0,
            "high": 0.7,
            "medium": 0.4,
            "low": 0.1
        }
        
        total_penalty = sum(severity_weights.get(v["severity"], 0.5) for v in violations)
        max_possible_penalty = len(violations) * 1.0  # If all were critical
        
        if max_possible_penalty == 0:
            return 1.0
        
        score = max(0.0, 1.0 - (total_penalty / max_possible_penalty))
        return score

    def _identify_enhancement_opportunities(self, module_path: Path, 
                                         violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify enhancement opportunities based on compliance analysis."""
        opportunities = []
        
        # Auto-fixable violations become enhancement opportunities
        auto_fixable = [v for v in violations if v.get("auto_fixable", False)]
        if auto_fixable:
            opportunities.append({
                "type": "auto_fix_violations",
                "priority": "high",
                "description": f"{len(auto_fixable)} violations can be automatically fixed",
                "auto_fixable": True,
                "violations_addressed": len(auto_fixable)
            })
        
        # Test coverage enhancement
        src_path = module_path / "src"
        tests_path = module_path / "tests"
        if src_path.exists() and tests_path.exists():
            src_files = list(src_path.glob("**/*.py"))
            test_files = list(tests_path.glob("**/test_*.py"))
            
            if len(src_files) > len(test_files):
                opportunities.append({
                    "type": "test_coverage_improvement",
                    "priority": "medium",
                    "description": f"Increase test coverage: {len(test_files)}/{len(src_files)} files tested",
                    "auto_fixable": False,
                    "test_gap": len(src_files) - len(test_files)
                })
        
        # Documentation enhancement
        readme_path = module_path / "README.md"
        if readme_path.exists():
            try:
                content = readme_path.read_text()
                if len(content) < 1000:  # Basic README
                    opportunities.append({
                        "type": "documentation_enhancement",
                        "priority": "medium",
                        "description": "README.md could be expanded with more comprehensive documentation",
                        "auto_fixable": False,
                        "current_length": len(content)
                    })
            except:
                pass
        
        return opportunities

    def _generate_wre_orchestration_recommendations(self, module_path: str, 
                                                   violations: List[Dict[str, Any]], 
                                                   compliance_score: float) -> List[Dict[str, Any]]:
        """Generate WRE orchestration recommendations for compliance enhancement."""
        if not self.wre_enabled:
            return []
        
        recommendations = []
        
        # WRE Auto-Enhancement Opportunity
        auto_fixable_count = sum(1 for v in violations if v.get("auto_fixable", False))
        if auto_fixable_count > 0:
            recommendations.append({
                "type": "wre_auto_enhancement",
                "priority": "high",
                "description": f"WRE can automatically fix {auto_fixable_count} compliance violations",
                "implementation_strategy": "Deploy WRE autonomous enhancement protocols",
                "expected_outcome": f"Compliance score improvement: {compliance_score:.1%} → {min(1.0, compliance_score + 0.3):.1%}",
                "effort_estimate": "low"
            })
        
        # Zen Coding Integration Opportunity
        if compliance_score > 0.7:
            recommendations.append({
                "type": "zen_coding_integration",
                "priority": "medium",
                "description": f"Module {module_path} ready for zen coding enhancement protocols",
                "implementation_strategy": "Enable 0102 quantum state access for module enhancement",
                "expected_outcome": "Accelerated development through quantum temporal coding",
                "effort_estimate": "medium"
            })
        
        # Recursive Improvement Opportunity
        if len(violations) > 0:
            recommendations.append({
                "type": "recursive_improvement",
                "priority": "medium",
                "description": f"WSP 48 recursive improvement can address {len(violations)} compliance areas",
                "implementation_strategy": "Implement recursive enhancement monitoring and self-correction",
                "expected_outcome": "Continuous compliance improvement and violation prevention",
                "effort_estimate": "medium"
            })
        
        return recommendations

    def _create_violation_object(self, violation_dict: Dict[str, Any]) -> ComplianceViolation:
        """Create ComplianceViolation object from violation dictionary."""
        return ComplianceViolation(
            violation_type=violation_dict["type"],
            severity=violation_dict["severity"],
            module_path="",  # Will be set by caller
            description=violation_dict["description"],
            wsp_protocol=violation_dict["wsp_protocol"],
            remediation_suggestion=violation_dict["remediation"],
            auto_fixable=violation_dict.get("auto_fixable", False),
            timestamp=datetime.now()
        )

    def _violation_to_dict(self, violation: ComplianceViolation) -> Dict[str, Any]:
        """Convert ComplianceViolation object to dictionary."""
        return {
            "type": violation.violation_type,
            "severity": violation.severity,
            "description": violation.description,
            "wsp_protocol": violation.wsp_protocol,
            "remediation": violation.remediation_suggestion,
            "auto_fixable": violation.auto_fixable,
            "timestamp": violation.timestamp.isoformat()
        }

    def _update_average_compliance_score(self, new_score: float):
        """Update running average compliance score."""
        total_modules = self.compliance_metrics['total_modules_checked']
        if total_modules > 0:
            current_avg = self.compliance_metrics['average_compliance_score']
            new_avg = ((current_avg * (total_modules - 1)) + new_score) / total_modules
            self.compliance_metrics['average_compliance_score'] = new_avg

    def run_system_wide_compliance_check(self, enable_wre_orchestration: bool = True) -> Dict[str, Any]:
        """
        Run compliance checks across all modules in the system.
        
        Args:
            enable_wre_orchestration: Whether to enable WRE orchestration
            
        Returns:
            Dict with system-wide compliance analysis
        """
        if self.wre_enabled:
            wre_log("Starting system-wide compliance analysis", level="INFO")
        
        modules_dir = Path("modules")
        system_results = {
            "compliant_modules": [],
            "non_compliant_modules": [],
            "system_compliance_score": 0.0,
            "total_violations": 0,
            "auto_fixable_violations": 0,
            "wre_enhancement_opportunities": []
        }
        
        if not modules_dir.exists():
            return {
                "error": "modules directory not found",
                "system_compliance_score": 0.0
            }
        
        # Check all modules across enterprise domains
        total_modules = 0
        total_score = 0.0
        
        for domain_dir in modules_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith('.'):
                        module_path = f"{domain_dir.name}/{module_dir.name}"
                        
                        result = self.run_check(str(modules_dir / module_path), enable_wre_orchestration)
                        
                        total_modules += 1
                        total_score += result["compliance_score"]
                        
                        if result["compliant"]:
                            system_results["compliant_modules"].append({
                                "module": module_path,
                                "score": result["compliance_score"]
                            })
                        else:
                            system_results["non_compliant_modules"].append({
                                "module": module_path,
                                "score": result["compliance_score"],
                                "violations": len(result["violations"]),
                                "auto_fixable": sum(1 for v in result["violations"] if v.get("auto_fixable", False))
                            })
                            
                        system_results["total_violations"] += len(result.get("violations", []))
                        system_results["auto_fixable_violations"] += sum(
                            1 for v in result.get("violations", []) if v.get("auto_fixable", False)
                        )
                        
                        # Collect WRE enhancement opportunities
                        wre_recommendations = result.get("wre_integration_status", {}).get("recommendations", [])
                        system_results["wre_enhancement_opportunities"].extend(wre_recommendations)
        
        # Calculate system-wide compliance score
        if total_modules > 0:
            system_results["system_compliance_score"] = total_score / total_modules
        
        # Add summary metrics
        system_results["summary"] = {
            "total_modules_checked": total_modules,
            "compliant_modules_count": len(system_results["compliant_modules"]),
            "non_compliant_modules_count": len(system_results["non_compliant_modules"]),
            "compliance_rate": len(system_results["compliant_modules"]) / total_modules if total_modules > 0 else 0,
            "wre_enabled": self.wre_enabled,
            "total_wre_opportunities": len(system_results["wre_enhancement_opportunities"])
        }
        
        if self.wre_enabled:
            wre_log(f"System-wide compliance analysis complete: {system_results['summary']['compliance_rate']:.1%} compliance rate", level="INFO")
        
        return system_results

    def get_compliance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive compliance agent performance metrics."""
        return {
            "compliance_metrics": self.compliance_metrics,
            "wre_integration": {
                "enabled": self.wre_enabled,
                "orchestration_engine_available": self.wre_engine is not None,
                "module_coordinator_available": self.module_coordinator is not None
            },
            "cache_status": {
                "cached_reports": len(self.compliance_cache),
                "violation_history_entries": len(self.violation_history)
            },
            "wsp_protocols_monitored": list(self.wsp_protocols.keys()),
            "last_updated": datetime.now().isoformat()
        }

    def apply_wre_enhancements(self, module_path: str, selected_enhancements: List[str]) -> Dict[str, Any]:
        """
        Apply selected WRE enhancements to improve module compliance
        
        Args:
            module_path: Module to enhance
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
        
        wre_log(f"Applying compliance enhancements to {module_path}: {selected_enhancements}", level="INFO")
        
        try:
            enhancement_results = []
            
            for enhancement_type in selected_enhancements:
                if enhancement_type == "wre_auto_enhancement":
                    result = self._apply_auto_fix_enhancements(module_path)
                elif enhancement_type == "zen_coding_integration":
                    result = self._enable_zen_coding_integration(module_path)
                elif enhancement_type == "recursive_improvement":
                    result = self._enable_recursive_improvement(module_path)
                else:
                    result = {"type": enhancement_type, "status": "unknown_enhancement_type"}
                
                enhancement_results.append(result)
            
            # WRE orchestration for enhancement application
            if self.module_coordinator:
                orchestration_result = self.module_coordinator.handle_module_development(
                    f"compliance_enhancement_{module_path.replace('/', '_')}",
                    self.wre_engine
                )
                enhancement_results.append({
                    "type": "wre_orchestration",
                    "status": "applied",
                    "result": str(orchestration_result)
                })
            
            return {
                "status": "success",
                "module": module_path,
                "applied_enhancements": enhancement_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            wre_log(f"Enhancement application failed for {module_path}: {e}", level="ERROR")
            return {
                "status": "error",
                "message": str(e),
                "module": module_path
            }

    def _apply_auto_fix_enhancements(self, module_path: str) -> Dict[str, Any]:
        """Apply automatic fixes for compliance violations (simulation)"""
        return {
            "type": "wre_auto_enhancement",
            "status": "simulated",
            "description": f"Automatic compliance fixes applied to {module_path}",
            "fixes_applied": ["created_missing_directories", "added_mandatory_files", "updated_documentation"]
        }

    def _enable_zen_coding_integration(self, module_path: str) -> Dict[str, Any]:
        """Enable zen coding integration for enhanced development (simulation)"""
        return {
            "type": "zen_coding_integration",
            "status": "simulated",
            "description": f"Zen coding protocols enabled for {module_path}",
            "capabilities": ["quantum_pattern_access", "0102_enhancement", "temporal_development"]
        }

    def _enable_recursive_improvement(self, module_path: str) -> Dict[str, Any]:
        """Enable recursive improvement monitoring (simulation)"""
        return {
            "type": "recursive_improvement",
            "status": "simulated",
            "description": f"WSP 48 recursive improvement enabled for {module_path}",
            "features": ["compliance_monitoring", "violation_prevention", "continuous_enhancement"]
        }


def create_compliance_agent(config: Optional[Dict[str, Any]] = None) -> ComplianceAgent:
    """
    Factory function to create Compliance Agent with WRE integration
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        ComplianceAgent: Configured compliance agent instance
    """
    return ComplianceAgent(config=config)


# Example usage and testing functions
def test_compliance_agent():
    """Test function for Compliance Agent functionality"""
    agent = create_compliance_agent()
    
    print(f"Compliance Agent Metrics: {agent.get_compliance_metrics()}")
    
    # Test individual module compliance
    test_module = "infrastructure/compliance_agent"
    result = agent.run_check(test_module)
    
    print(f"\nModule Compliance Results for {test_module}:")
    print(f"Compliant: {result['compliant']}")
    print(f"Compliance Score: {result['compliance_score']:.1%}")
    print(f"Violations: {len(result.get('violations', []))}")
    print(f"WRE Enabled: {result['wre_integration_status']['enabled']}")
    print(f"Enhancement Opportunities: {len(result.get('enhancement_opportunities', []))}")
    
    # Test system-wide compliance
    system_results = agent.run_system_wide_compliance_check()
    print(f"\nSystem-wide Compliance:")
    print(f"Total Modules: {system_results['summary']['total_modules_checked']}")
    print(f"Compliance Rate: {system_results['summary']['compliance_rate']:.1%}")
    print(f"System Score: {system_results['system_compliance_score']:.1%}")
    
    return agent

    def handle_security_violation(self, violation_type: str, severity: str, module_path: str, details: str) -> Dict[str, Any]:
        """
        Handle security violations detected by FMAS or other security tools (WSP 4 + WSP 71).
        
        Args:
            violation_type: Type of security violation (e.g., 'VULNERABILITY', 'SECRET_DETECTED')
            severity: Severity level ('HIGH', 'MEDIUM', 'LOW')
            module_path: Path to the affected module
            details: Detailed description of the violation
            
        Returns:
            Dict containing violation handling results
        """
        try:
            # Determine action based on severity
            action_required = self.security_thresholds.get(severity, "INFO_VIOLATION")
            
            violation_record = {
                "violation_id": f"sec_{hash(f'{module_path}_{violation_type}_{details}') % 10000}",
                "type": violation_type,
                "severity": severity,
                "module_path": module_path,
                "details": details,
                "action_required": action_required,
                "timestamp": datetime.utcnow().isoformat(),
                "handled_by": "ComplianceAgent"
            }
            
            # Log violation based on severity
            if severity == "HIGH":
                if self.wre_enabled:
                    wre_log(f"🚨 CRITICAL Security Violation: {violation_type} in {module_path}", "ERROR")
                else:
                    print(f"🚨 CRITICAL Security Violation: {violation_type} in {module_path}")
                    
                # High-severity violations may block integration
                violation_record["integration_blocked"] = True
                
            elif severity == "MEDIUM":
                if self.wre_enabled:
                    wre_log(f"⚠️ Security Warning: {violation_type} in {module_path}", "WARNING")
                else:
                    print(f"⚠️ Security Warning: {violation_type} in {module_path}")
                    
                violation_record["requires_acknowledgment"] = True
                
            else:  # LOW severity
                if self.wre_enabled:
                    wre_log(f"ℹ️ Security Notice: {violation_type} in {module_path}", "INFO")
                else:
                    print(f"ℹ️ Security Notice: {violation_type} in {module_path}")
            
            # Store violation for tracking
            if not hasattr(self, 'security_violations'):
                self.security_violations = []
            self.security_violations.append(violation_record)
            
            # Update compliance metrics
            self.compliance_metrics['security_violations'] = self.compliance_metrics.get('security_violations', 0) + 1
            
            return {
                "status": "handled",
                "violation_id": violation_record["violation_id"],
                "action_required": action_required,
                "integration_blocked": violation_record.get("integration_blocked", False),
                "requires_acknowledgment": violation_record.get("requires_acknowledgment", False)
            }
            
        except Exception as e:
            error_msg = f"Failed to handle security violation: {str(e)}"
            if self.wre_enabled:
                wre_log(error_msg, "ERROR")
            return {"status": "error", "error": error_msg}
    
    def get_security_violations(self, module_path: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """
        Get security violations, optionally filtered by module or severity.
        
        Args:
            module_path: Filter by specific module path
            severity: Filter by severity level
            
        Returns:
            List of security violation records
        """
        if not hasattr(self, 'security_violations'):
            return []
            
        violations = self.security_violations
        
        if module_path:
            violations = [v for v in violations if v["module_path"] == module_path]
            
        if severity:
            violations = [v for v in violations if v["severity"] == severity]
            
        return violations
    
    def generate_security_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security compliance report.
        
        Returns:
            Dict containing security compliance statistics and recommendations
        """
        if not hasattr(self, 'security_violations'):
            return {
                "total_violations": 0,
                "severity_breakdown": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "blocked_integrations": 0,
                "recommendations": ["No security violations detected"]
            }
            
        violations = self.security_violations
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        blocked_count = 0
        
        for violation in violations:
            severity = violation.get("severity", "LOW")
            if severity in severity_counts:
                severity_counts[severity] += 1
                
            if violation.get("integration_blocked", False):
                blocked_count += 1
        
        # Generate recommendations
        recommendations = []
        if severity_counts["HIGH"] > 0:
            recommendations.append(f"URGENT: Fix {severity_counts['HIGH']} high-severity security vulnerabilities")
        if severity_counts["MEDIUM"] > 0:
            recommendations.append(f"Review and address {severity_counts['MEDIUM']} medium-severity security warnings")
        if blocked_count > 0:
            recommendations.append(f"Integration blocked for {blocked_count} modules due to security violations")
            
        return {
            "total_violations": len(violations),
            "severity_breakdown": severity_counts,
            "blocked_integrations": blocked_count,
            "compliance_status": "NON_COMPLIANT" if severity_counts["HIGH"] > 0 else "COMPLIANT",
            "recommendations": recommendations if recommendations else ["Security compliance maintained"]
        }


if __name__ == "__main__":
    # Run test when executed directly
    test_compliance_agent()