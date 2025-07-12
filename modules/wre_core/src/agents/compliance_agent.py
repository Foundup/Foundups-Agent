"""
ComplianceAgent - Agentic Readiness Verification

This agent implements the agentic_readiness_check node from REMOTE_BUILD_PROTOTYPE flow.
Validates that all modules and agents are in compliant, ready state for autonomous
0102 operations.

WSP Compliance: WSP 54 (Agent Duties), WSP 1 (Agentic Responsibility)
REMOTE_BUILD_PROTOTYPE: agentic_readiness_check node implementation
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
class AgentReadinessStatus:
    """Agent readiness status for compliance verification"""
    agent_name: str
    is_ready: bool
    readiness_score: float
    blocking_issues: List[str]
    warnings: List[str]
    last_assessment: str
    
@dataclass
class ModuleComplianceStatus:
    """Module compliance status for readiness verification"""
    module_name: str
    domain: str
    wsp_compliance_score: float
    critical_violations: List[str]
    warnings: List[str]
    is_build_ready: bool
    last_checked: str

@dataclass
class ReadinessResult:
    """Complete readiness verification result for REMOTE_BUILD_PROTOTYPE flow"""
    readiness_status: str  # "READY", "PARTIAL", "NOT_READY"
    overall_readiness_score: float
    agent_readiness: List[AgentReadinessStatus]
    module_compliance: List[ModuleComplianceStatus]
    system_health_score: float
    blocking_issues: List[str]
    recommendations: List[str]
    execution_timestamp: str

class ComplianceAgent:
    """
    ComplianceAgent - Agentic Readiness Verification
    
    REMOTE_BUILD_PROTOTYPE Flow Implementation:
    - Validates all modules and agents are in compliant, ready state
    - Checks WSP protocol compliance across system
    - Verifies agent operational readiness
    - Provides readiness recommendations for autonomous operations
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).resolve().parent.parent.parent.parent.parent
        self.modules_path = self.project_root / "modules"
        self.wsp_framework_path = self.project_root / "WSP_framework" / "src"
        self.last_compliance_check = None
        self.cached_compliance_results: Dict[str, Any] = {}
        
        # Critical WSP protocols for compliance checking
        self.critical_wsp_protocols = [
            "WSP_1", "WSP_3", "WSP_4", "WSP_5", "WSP_37", "WSP_46", "WSP_54", "WSP_63"
        ]
        
    def verify_readiness(self) -> ReadinessResult:
        """
        Main readiness verification function for REMOTE_BUILD_PROTOTYPE flow.
        
        Returns:
            ReadinessResult: Complete readiness verification results
        """
        wre_log("🔍 ComplianceAgent: Verifying agentic readiness", "INFO")
        
        try:
            # Verify agent readiness
            agent_readiness = self._verify_agent_readiness()
            
            # Verify module compliance
            module_compliance = self._verify_module_compliance()
            
            # Check system health
            system_health_score = self._check_system_health()
            
            # Determine overall readiness
            overall_readiness_score = self._calculate_overall_readiness(
                agent_readiness, module_compliance, system_health_score
            )
            
            # Determine readiness status
            readiness_status = self._determine_readiness_status(overall_readiness_score)
            
            # Collect blocking issues and recommendations
            blocking_issues = self._collect_blocking_issues(agent_readiness, module_compliance)
            recommendations = self._generate_recommendations(agent_readiness, module_compliance, system_health_score)
            
            # Create result for REMOTE_BUILD_PROTOTYPE flow
            result = ReadinessResult(
                readiness_status=readiness_status,
                overall_readiness_score=overall_readiness_score,
                agent_readiness=agent_readiness,
                module_compliance=module_compliance,
                system_health_score=system_health_score,
                blocking_issues=blocking_issues,
                recommendations=recommendations,
                execution_timestamp=datetime.now().isoformat()
            )
            
            # Update cache
            self.cached_compliance_results = {
                "last_result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            wre_log(f"🔍 ComplianceAgent: Readiness verification complete - Status: {readiness_status}", "SUCCESS")
            return result
            
        except Exception as e:
            wre_log(f"❌ ComplianceAgent: Failed to verify readiness: {e}", "ERROR")
            raise
    
    def _verify_agent_readiness(self) -> List[AgentReadinessStatus]:
        """Verify readiness of all required agents"""
        
        # Required agents for REMOTE_BUILD_PROTOTYPE flow
        required_agents = [
            "ScoringAgent",
            "ComplianceAgent", 
            "ModuleScaffoldingAgent",
            "ModularizationAuditAgent",
            "TestingAgent",
            "DocumentationAgent"
        ]
        
        agent_readiness = []
        
        for agent_name in required_agents:
            try:
                readiness_status = self._assess_agent_readiness(agent_name)
                agent_readiness.append(readiness_status)
            except Exception as e:
                # Agent not found or failed assessment
                agent_readiness.append(AgentReadinessStatus(
                    agent_name=agent_name,
                    is_ready=False,
                    readiness_score=0.0,
                    blocking_issues=[f"Agent assessment failed: {e}"],
                    warnings=[],
                    last_assessment=datetime.now().isoformat()
                ))
        
        return agent_readiness
    
    def _assess_agent_readiness(self, agent_name: str) -> AgentReadinessStatus:
        """Assess readiness of a specific agent"""
        
        # Check if agent file exists
        agent_file = self.project_root / "modules" / "wre_core" / "src" / "agents" / f"{agent_name.lower()}.py"
        
        blocking_issues = []
        warnings = []
        readiness_score = 0.0
        
        if not agent_file.exists():
            blocking_issues.append(f"Agent file not found: {agent_file}")
        else:
            readiness_score += 0.3  # File exists
            
            # Check for basic class structure
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if f"class {agent_name}" in content:
                    readiness_score += 0.2  # Class defined
                else:
                    blocking_issues.append(f"Agent class {agent_name} not found")
                
                # Check for required methods
                required_methods = self._get_required_methods(agent_name)
                for method in required_methods:
                    if f"def {method}" in content:
                        readiness_score += 0.1
                    else:
                        warnings.append(f"Missing method: {method}")
                
                # Check for WSP compliance documentation
                if "WSP Compliance:" in content:
                    readiness_score += 0.1
                else:
                    warnings.append("Missing WSP compliance documentation")
                
                # Check for REMOTE_BUILD_PROTOTYPE documentation
                if "REMOTE_BUILD_PROTOTYPE" in content:
                    readiness_score += 0.1
                else:
                    warnings.append("Missing REMOTE_BUILD_PROTOTYPE documentation")
                    
            except Exception as e:
                blocking_issues.append(f"Failed to analyze agent file: {e}")
        
        # Additional checks based on agent type
        if agent_name == "ScoringAgent":
            # Check for WSP 37 integration
            if "WSP_37" in content or "WSP 37" in content:
                readiness_score += 0.1
            else:
                warnings.append("Missing WSP 37 integration")
        
        return AgentReadinessStatus(
            agent_name=agent_name,
            is_ready=readiness_score >= 0.7 and not blocking_issues,
            readiness_score=readiness_score,
            blocking_issues=blocking_issues,
            warnings=warnings,
            last_assessment=datetime.now().isoformat()
        )
    
    def _get_required_methods(self, agent_name: str) -> List[str]:
        """Get required methods for each agent type"""
        
        method_map = {
            "ScoringAgent": ["retrieve_dynamic_scores", "get_top_modules"],
            "ComplianceAgent": ["verify_readiness", "check_wsp_compliance"],
            "ModuleScaffoldingAgent": ["create_module_scaffold", "validate_structure"],
            "ModularizationAuditAgent": ["audit_modularity", "check_wsp_63_compliance"],
            "TestingAgent": ["run_test_suite", "validate_coverage"],
            "DocumentationAgent": ["update_documentation", "validate_documentation"]
        }
        
        return method_map.get(agent_name, [])
    
    def _verify_module_compliance(self) -> List[ModuleComplianceStatus]:
        """Verify compliance of all modules"""
        
        module_compliance = []
        
        if not self.modules_path.exists():
            wre_log("⚠️ ComplianceAgent: Modules directory not found", "WARNING")
            return module_compliance
        
        # Check each domain and module
        for domain_path in self.modules_path.iterdir():
            if domain_path.is_dir() and not domain_path.name.startswith('.'):
                domain_name = domain_path.name
                
                for module_path in domain_path.iterdir():
                    if module_path.is_dir() and not module_path.name.startswith('.'):
                        module_name = module_path.name
                        
                        try:
                            compliance_status = self._assess_module_compliance(module_path, domain_name, module_name)
                            module_compliance.append(compliance_status)
                        except Exception as e:
                            wre_log(f"⚠️ ComplianceAgent: Error assessing {module_name}: {e}", "WARNING")
                            continue
        
        return module_compliance
    
    def _assess_module_compliance(self, module_path: Path, domain_name: str, module_name: str) -> ModuleComplianceStatus:
        """Assess compliance of a specific module"""
        
        critical_violations = []
        warnings = []
        compliance_score = 0.0
        
        # Check for mandatory files (WSP 49)
        mandatory_files = ["README.md", "INTERFACE.md", "requirements.txt", "__init__.py"]
        for file_name in mandatory_files:
            if (module_path / file_name).exists():
                compliance_score += 0.1
            else:
                if file_name in ["README.md", "__init__.py"]:
                    critical_violations.append(f"Missing mandatory file: {file_name}")
                else:
                    warnings.append(f"Missing recommended file: {file_name}")
        
        # Check for src directory
        src_path = module_path / "src"
        if src_path.exists():
            compliance_score += 0.1
        else:
            critical_violations.append("Missing src/ directory")
        
        # Check for tests directory
        tests_path = module_path / "tests"
        if tests_path.exists():
            compliance_score += 0.1
        else:
            warnings.append("Missing tests/ directory")
        
        # Check for memory directory (WSP 60)
        memory_path = module_path / "memory"
        if memory_path.exists():
            compliance_score += 0.1
        else:
            warnings.append("Missing memory/ directory (WSP 60)")
        
        # Check for WSP 63 compliance (directory organization)
        if src_path.exists():
            src_items = list(src_path.iterdir())
            if len(src_items) > 8:  # WSP 63 threshold
                critical_violations.append(f"WSP 63 violation: {len(src_items)} items in src/ (threshold: 8)")
            else:
                compliance_score += 0.1
        
        # Check for WSP 62 compliance (file size)
        if src_path.exists():
            large_files = []
            for py_file in src_path.glob("**/*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        line_count = len(f.readlines())
                        if line_count > 500:  # WSP 62 threshold
                            large_files.append(f"{py_file.name}: {line_count} lines")
                except:
                    continue
            
            if large_files:
                critical_violations.append(f"WSP 62 violations: {len(large_files)} files exceed 500 lines")
            else:
                compliance_score += 0.1
        
        # Check for documentation quality
        readme_path = module_path / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                    
                if "WSP Compliance" in readme_content:
                    compliance_score += 0.1
                else:
                    warnings.append("README missing WSP compliance section")
                    
                if len(readme_content) > 100:  # Basic content check
                    compliance_score += 0.1
                else:
                    warnings.append("README appears to be incomplete")
                    
            except Exception as e:
                warnings.append(f"Could not read README: {e}")
        
        # Determine if module is build-ready
        is_build_ready = (
            compliance_score >= 0.7 and
            not critical_violations and
            (module_path / "src").exists() and
            (module_path / "README.md").exists()
        )
        
        return ModuleComplianceStatus(
            module_name=module_name,
            domain=domain_name,
            wsp_compliance_score=compliance_score,
            critical_violations=critical_violations,
            warnings=warnings,
            is_build_ready=is_build_ready,
            last_checked=datetime.now().isoformat()
        )
    
    def _check_system_health(self) -> float:
        """Check overall system health"""
        
        health_score = 0.0
        
        # Check WSP framework accessibility
        if self.wsp_framework_path.exists():
            health_score += 0.2
            
            # Check for critical WSP protocols
            existing_protocols = 0
            for protocol in self.critical_wsp_protocols:
                protocol_files = list(self.wsp_framework_path.glob(f"{protocol}*.md"))
                if protocol_files:
                    existing_protocols += 1
            
            health_score += (existing_protocols / len(self.critical_wsp_protocols)) * 0.3
        
        # Check modules directory structure
        if self.modules_path.exists():
            health_score += 0.2
            
            # Check for enterprise domains
            expected_domains = ["infrastructure", "ai_intelligence", "communication", "platform_integration"]
            existing_domains = 0
            for domain in expected_domains:
                if (self.modules_path / domain).exists():
                    existing_domains += 1
            
            health_score += (existing_domains / len(expected_domains)) * 0.3
        
        return health_score
    
    def _calculate_overall_readiness(self, agent_readiness: List[AgentReadinessStatus], 
                                   module_compliance: List[ModuleComplianceStatus], 
                                   system_health_score: float) -> float:
        """Calculate overall readiness score"""
        
        # Agent readiness (40% weight)
        agent_scores = [agent.readiness_score for agent in agent_readiness]
        avg_agent_score = sum(agent_scores) / len(agent_scores) if agent_scores else 0.0
        
        # Module compliance (40% weight)
        module_scores = [module.wsp_compliance_score for module in module_compliance]
        avg_module_score = sum(module_scores) / len(module_scores) if module_scores else 0.0
        
        # System health (20% weight)
        overall_score = (avg_agent_score * 0.4) + (avg_module_score * 0.4) + (system_health_score * 0.2)
        
        return overall_score
    
    def _determine_readiness_status(self, overall_score: float) -> str:
        """Determine readiness status from overall score"""
        
        if overall_score >= 0.8:
            return "READY"
        elif overall_score >= 0.6:
            return "PARTIAL"
        else:
            return "NOT_READY"
    
    def _collect_blocking_issues(self, agent_readiness: List[AgentReadinessStatus],
                               module_compliance: List[ModuleComplianceStatus]) -> List[str]:
        """Collect all blocking issues"""
        
        blocking_issues = []
        
        # Collect agent blocking issues
        for agent in agent_readiness:
            if not agent.is_ready:
                blocking_issues.extend([f"Agent {agent.agent_name}: {issue}" for issue in agent.blocking_issues])
        
        # Collect module blocking issues  
        for module in module_compliance:
            if not module.is_build_ready and module.critical_violations:
                blocking_issues.extend([f"Module {module.module_name}: {violation}" for violation in module.critical_violations])
        
        return blocking_issues
    
    def _generate_recommendations(self, agent_readiness: List[AgentReadinessStatus],
                                module_compliance: List[ModuleComplianceStatus],
                                system_health_score: float) -> List[str]:
        """Generate recommendations for improving readiness"""
        
        recommendations = []
        
        # Agent recommendations
        not_ready_agents = [agent for agent in agent_readiness if not agent.is_ready]
        if not_ready_agents:
            recommendations.append(f"Implement missing agents: {', '.join([agent.agent_name for agent in not_ready_agents])}")
        
        # Module recommendations
        non_compliant_modules = [module for module in module_compliance if not module.is_build_ready]
        if non_compliant_modules:
            recommendations.append(f"Fix compliance issues in modules: {', '.join([module.module_name for module in non_compliant_modules[:3]])}")
        
        # System health recommendations
        if system_health_score < 0.7:
            recommendations.append("Improve system health: Check WSP framework and module structure")
        
        return recommendations
    
    def check_wsp_compliance(self, module_name: str = None) -> Dict[str, Any]:
        """Check WSP compliance for specific module or entire system"""
        
        if module_name:
            # Check specific module
            for domain_path in self.modules_path.iterdir():
                if domain_path.is_dir():
                    module_path = domain_path / module_name
                    if module_path.exists():
                        return self._assess_module_compliance(module_path, domain_path.name, module_name)
            
            return {"error": f"Module {module_name} not found"}
        else:
            # Check entire system
            return self.verify_readiness()
    
    def get_cached_results(self) -> Optional[ReadinessResult]:
        """Get cached compliance results"""
        
        if self.cached_compliance_results:
            return self.cached_compliance_results.get("last_result")
        return None

# Factory function for agent initialization
def create_compliance_agent(project_root: Path = None) -> ComplianceAgent:
    """Factory function to create and initialize ComplianceAgent"""
    return ComplianceAgent(project_root) 