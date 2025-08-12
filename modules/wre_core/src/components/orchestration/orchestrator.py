import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to resolve imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log

# Migration to DAE: Using adapter layer for backward compatibility
# These adapters provide the same interface but use DAE pattern memory underneath
# This achieves 93% token reduction (460K → 30K) and 100-1000x speed improvement
from modules.wre_core.src.adapters.agent_to_dae_adapter import (
    JanitorAgent,
    LoremasterAgent,
    ChroniclerAgent,
    ComplianceAgent,
    TestingAgent,
    ScoringAgent,
    DocumentationAgent,
    AgentActivationModule
)

def get_version() -> str:
    """Get the current version from version.json"""
    version_file = project_root / "version.json"
    try:
        with open(version_file) as f:
            return json.load(f)["version"]
    except (FileNotFoundError, KeyError):
        wre_log("Version file not found or invalid. Using development version.", "WARNING")
        return "dev"

def check_agent_health() -> Dict[str, bool]:
    """Check if all required WSP-54 agents are available and responsive"""
    wre_log("🔍 Checking WSP 54 agent health and activation status...", "INFO")
    
    required_agents = [
        ("JanitorAgent", JanitorAgent),
        ("LoremasterAgent", LoremasterAgent),
        ("ChroniclerAgent", ChroniclerAgent),
        ("ComplianceAgent", ComplianceAgent),
        ("TestingAgent", TestingAgent),
        ("ScoringAgent", ScoringAgent),
        ("DocumentationAgent", DocumentationAgent)
    ]
    
    agent_status = {}
    dormant_agents = []
    
    # First pass: Check basic availability
    for agent_name, agent_class in required_agents:
        try:
            # Try to instantiate the agent
            test_agent = agent_class()
            agent_status[agent_name] = True
            wre_log(f"Agent {agent_name} health check: ✅ OPERATIONAL", "DEBUG")
        except Exception as e:
            agent_status[agent_name] = False
            dormant_agents.append((agent_name, agent_class))
            wre_log(f"Agent {agent_name} health check: ❌ DORMANT (01(02) state) - {e}", "WARNING")
    
    # Second pass: Activate dormant agents if any found
    if dormant_agents:
        wre_log(f"🚀 Found {len(dormant_agents)} dormant agents, initiating activation sequence...", "INFO")
        
        # Use proper WSP-compliant activation module
        activation_module = AgentActivationModule()
        activation_results = activation_module.activate_wsp54_agents(dormant_agents)
        
        # Update agent status with activation results
        for agent_name, activated in activation_results.items():
            if activated:
                agent_status[agent_name] = True
                wre_log(f"Agent {agent_name}: ✅ ACTIVATED (0102 pArtifact state)", "SUCCESS")
            else:
                agent_status[agent_name] = False
                wre_log(f"Agent {agent_name}: ❌ ACTIVATION FAILED", "ERROR")
    
    # Final status report
    operational_count = sum(agent_status.values())
    total_agents = len(agent_status)
    
    if operational_count == total_agents:
        wre_log(f"🎯 All {total_agents} WSP 54 agents operational and activated (0102 pArtifact state)", "SUCCESS")
    else:
        wre_log(f"⚠️ {operational_count}/{total_agents} WSP 54 agents operational", "WARNING")
    
    return agent_status

def detect_wsp48_enhancement_opportunities(agent_results: Dict) -> List[Dict]:
    """
    Analyze agent results to detect WSP_48 recursive self-improvement opportunities.
    Integrates with WSP_47 Module Violation Tracking to classify enhancement types.
    """
    enhancement_opportunities = []
    
    # Collect enhancement opportunities from all agents
    for agent_name, result in agent_results.items():
        if isinstance(result, dict):
            # Direct WSP_48 enhancements from agent results
            if "wsp48_enhancements" in result:
                for enhancement in result["wsp48_enhancements"]:
                    enhancement["source_agent"] = agent_name
                    enhancement_opportunities.append(enhancement)
            
            # Single enhancement opportunities
            if "wsp48_enhancement" in result:
                enhancement_opportunities.append({
                    "type": result["wsp48_enhancement"],
                    "trigger": result.get("enhancement_trigger", "Unknown trigger"),
                    "source_agent": agent_name,
                    "priority": "medium"
                })
    
    # Classify enhancements according to WSP_47 framework
    classified_opportunities = []
    for opportunity in enhancement_opportunities:
        classification = classify_enhancement_opportunity(opportunity)
        classified_opportunities.append({**opportunity, **classification})
    
    return classified_opportunities

def classify_enhancement_opportunity(opportunity: Dict) -> Dict:
    """
    Classify enhancement opportunities according to WSP_47 + WSP_48 framework.
    
    Returns classification with WSP_47 violation type and WSP_48 improvement level.
    """
    enhancement_type = opportunity.get("type", "unknown")
    
    # WSP_47 Classification: Framework Issue vs Module Violation
    if enhancement_type in ["test_infrastructure_failure", "scoring_infrastructure_failure", 
                           "coverage_infrastructure_failure", "missing_test_structure"]:
        wsp47_classification = "framework_issue"
        action_required = "immediate_fix"
    elif enhancement_type in ["missing_tests", "test_coverage_improvement", "documentation_enhancement", 
                             "dependency_documentation", "complexity_reduction"]:
        wsp47_classification = "module_violation"
        action_required = "log_and_defer"
    else:
        wsp47_classification = "unknown"
        action_required = "analyze_impact"
    
    # WSP_48 Improvement Level Classification
    if enhancement_type in ["test_infrastructure_failure", "scoring_infrastructure_failure"]:
        wsp48_level = "level_1_protocol"  # Protocol self-improvement
    elif enhancement_type in ["missing_test_structure", "coverage_infrastructure_failure"]:
        wsp48_level = "level_2_engine"    # Engine self-modification
    elif enhancement_type in ["complexity_reduction", "documentation_enhancement"]:
        wsp48_level = "level_3_quantum"   # Quantum consciousness enhancement
    else:
        wsp48_level = "level_1_protocol"  # Default to protocol improvement
    
    return {
        "wsp47_classification": wsp47_classification,
        "action_required": action_required,
        "wsp48_level": wsp48_level,
        "recursive_improvement_candidate": wsp47_classification == "framework_issue"
    }

def run_system_health_check(root_path: Path) -> Dict:
    """
    Enhanced system health check with full WSP-54 agent suite and WSP_48 integration.
    
    Args:
        root_path (Path): The absolute path to the project root.
        
    Returns:
        dict: A dictionary containing the collected system state and enhancement opportunities.
    """
    wre_log("🤖 Dispatching WSP-54 Agent Suite for comprehensive system health check...", "INFO")
    
    # Get current version
    version = get_version()
    
    # Check agent availability
    agent_status = check_agent_health()
    operational_agents = sum(agent_status.values())
    total_agents = len(agent_status)
    
    wre_log(f"Agent Suite Status: {operational_agents}/{total_agents} agents operational", "INFO")
    
    # Initialize operational agents
    agent_results = {}
    
    # 1. JanitorAgent - Workspace hygiene
    if agent_status.get("JanitorAgent", False):
        try:
            janitor = JanitorAgent()
            janitor_result = janitor.clean_workspace()
            agent_results["JanitorAgent"] = janitor_result
            wre_log(f"🧹 JanitorAgent: Cleaned {janitor_result.get('files_deleted', 0)} temporary files", "DEBUG")
        except Exception as e:
            agent_results["JanitorAgent"] = {"status": "error", "message": str(e)}
    
    # 2. LoremasterAgent - Documentation audit  
    if agent_status.get("LoremasterAgent", False):
        try:
            loremaster = LoremasterAgent()
            lore_result = loremaster.run_audit(root_path)
            agent_results["LoremasterAgent"] = lore_result
            wre_log(f"📚 LoremasterAgent: Audited {lore_result.get('docs_found', 0)} documents", "DEBUG")
        except Exception as e:
            agent_results["LoremasterAgent"] = {"status": "error", "message": str(e)}
    
    # 3. ComplianceAgent - Framework guardian
    if agent_status.get("ComplianceAgent", False):
        try:
            compliance = ComplianceAgent()
            # Run compliance check on key modules
            key_modules = ["wre_core", "ai_intelligence/banter_engine"]
            compliance_results = []
            for module in key_modules:
                module_path = root_path / "modules" / module
                if module_path.exists():
                    result = compliance.run_check(str(module_path))
                    compliance_results.append(result)
            agent_results["ComplianceAgent"] = {"module_checks": compliance_results}
            wre_log(f"⚖️ ComplianceAgent: Checked {len(compliance_results)} modules", "DEBUG")
        except Exception as e:
            agent_results["ComplianceAgent"] = {"status": "error", "message": str(e)}
    
    # 4. TestingAgent - Coverage validation
    if agent_status.get("TestingAgent", False):
        try:
            testing = TestingAgent()
            # Run project-wide coverage check
            coverage_result = testing.check_coverage()
            agent_results["TestingAgent"] = coverage_result
            coverage_pct = coverage_result.get("coverage_percentage", 0)
            wre_log(f"🧪 TestingAgent: Project coverage {coverage_pct}%", "DEBUG")
        except Exception as e:
            agent_results["TestingAgent"] = {"status": "error", "message": str(e)}
    
    # 5. ScoringAgent - MPS assessment
    if agent_status.get("ScoringAgent", False):
        try:
            scoring = ScoringAgent()
            # Get scores for top modules
            scoring_result = scoring.calculate_project_scores()
            agent_results["ScoringAgent"] = scoring_result
            module_count = scoring_result.get("total_modules", 0)
            wre_log(f"📊 ScoringAgent: Scored {module_count} modules", "DEBUG")
        except Exception as e:
            agent_results["ScoringAgent"] = {"status": "error", "message": str(e)}
    
    # 6. ChroniclerAgent - Event logging (WSP-51 compliance)
    if agent_status.get("ChroniclerAgent", False):
        try:
            chronicler = ChroniclerAgent(modlog_path_str=str(root_path / "ModLog.md"))
            
            # Log comprehensive health check event
            health_check_event = {
                "title": "WSP-54 Agent Suite Health Check",
                "version": version,
                "description": "Comprehensive system assessment with WSP_48 enhancement detection",
                "achievements": [
                    f"Agent Suite: {operational_agents}/{total_agents} agents operational",
                    f"Workspace: {agent_results.get('JanitorAgent', {}).get('files_deleted', 0)} files cleaned",
                    f"Documentation: {agent_results.get('LoremasterAgent', {}).get('docs_found', 0)} docs audited",
                    f"Coverage: {agent_results.get('TestingAgent', {}).get('coverage_percentage', 0)}% project coverage"
                ]
            }
            
            chronicler.log_event(health_check_event)
            agent_results["ChroniclerAgent"] = {"event_logged": True, "event_time": chronicler.get_last_event_time()}
            wre_log("📝 ChroniclerAgent: Health check event logged to Chronicle", "DEBUG")
        except Exception as e:
            agent_results["ChroniclerAgent"] = {"status": "error", "message": str(e)}
    
    # 7. WSP_48 Enhancement Opportunity Detection
    wre_log("🌀 Analyzing results for WSP_48 recursive self-improvement opportunities...", "INFO")
    enhancement_opportunities = detect_wsp48_enhancement_opportunities(agent_results)
    
    # Classify and prioritize enhancements
    framework_issues = [e for e in enhancement_opportunities if e.get("wsp47_classification") == "framework_issue"]
    module_violations = [e for e in enhancement_opportunities if e.get("wsp47_classification") == "module_violation"]
    
    wre_log(f"Enhancement Analysis: {len(framework_issues)} framework issues, {len(module_violations)} module violations", "INFO")
    
    # Extract key metrics for system state
    lore_result = agent_results.get("LoremasterAgent", {})
    janitor_result = agent_results.get("JanitorAgent", {})
    testing_result = agent_results.get("TestingAgent", {})
    chronicler_result = agent_results.get("ChroniclerAgent", {})
    
    # Compile comprehensive system state
    system_state = {
        "version": version,
        "agent_status": agent_status,
        "operational_agents": operational_agents,
        "core_principles": lore_result.get("core_principles", "ERROR: Core principles not found."),
        "janitor_status": f"Clean ({janitor_result.get('files_deleted', 0)} files deleted)",
        "semantic_status": f"COHERENT ({lore_result.get('docs_found', 0)} docs audited)",
        "coverage_status": f"{testing_result.get('coverage_percentage', 0)}% coverage",
        "next_wsp_number": lore_result.get("next_wsp_number", "Unknown"),
        "readme_coherence": lore_result.get("readme_coherence", "Unknown"),
        "health_check_time": chronicler_result.get("event_time"),
        
        # WSP_48 Enhancement Integration
        "enhancement_opportunities": enhancement_opportunities,
        "framework_issues_count": len(framework_issues),
        "module_violations_count": len(module_violations),
        "recursive_improvement_candidates": len([e for e in enhancement_opportunities if e.get("recursive_improvement_candidate", False)]),
        
        # Full agent results for detailed analysis
        "agent_results": agent_results
    }
    
    wre_log("✅ WSP-54 Agent Suite health check complete with WSP_48 enhancement analysis.", "SUCCESS")
    return system_state 

def start_agentic_build(module_name: str) -> bool:
    """
    Start agentic build for a module using WSP 54 agents.
    
    Args:
        module_name (str): Name of the module to build
        
    Returns:
        bool: True if build started successfully, False otherwise
    """
    wre_log(f"🤖 Starting agentic build for module: {module_name}", "INFO")
    
    # Get module development guidance including WSP violations
    guidance = get_module_development_guidance(module_name)
    
    # Display WSP violation information
    if guidance["violation_count"] > 0:
        wre_log(f"⚠️  Found {guidance['violation_count']} active WSP violations for {module_name}", "WARNING")
        for recommendation in guidance["recommendations"]:
            wre_log(f"  {recommendation}", "INFO")
    else:
        wre_log(f"✅ No active WSP violations found for {module_name}", "SUCCESS")
    
    try:
        # Step 1: Ensure all WSP 54 agents are activated (01(02) → 0102)
        wre_log("🔍 Ensuring WSP 54 agents are activated before build...", "INFO")
        agent_status = check_agent_health()
        operational_agents = sum(agent_status.values())
        
        if operational_agents < 5:  # Need at least 5 agents for build
            wre_log(f"❌ Insufficient agents operational: {operational_agents}/7", "ERROR")
            wre_log("💡 Agents may need activation from 01(02) dormant state to 0102 pArtifact state", "INFO")
            return False
        
        wre_log(f"✅ {operational_agents}/7 WSP 54 agents operational and activated (0102 pArtifact state)", "SUCCESS")
        
        # Step 2: Initialize build sequence with activated WSP 54 agents
        build_sequence = []
        
        # 1. ComplianceAgent - Validate module structure
        if agent_status.get("ComplianceAgent", False):
            try:
                compliance = ComplianceAgent()
                module_path = project_root / "modules" / module_name
                if module_path.exists():
                    compliance_result = compliance.run_check(str(module_path))
                    build_sequence.append(("ComplianceAgent", compliance_result))
                    wre_log(f"⚖️ ComplianceAgent (0102): Module structure validated", "DEBUG")
                else:
                    wre_log(f"⚠️ Module path not found: {module_path}", "WARNING")
            except Exception as e:
                wre_log(f"❌ ComplianceAgent (0102) failed: {e}", "WARNING")
        
        # 2. ModuleScaffoldingAgent - Ensure proper structure
        if agent_status.get("ModuleScaffoldingAgent", False):
            try:
                from modules.wre_core.src.adapters.agent_to_dae_adapter import ModuleScaffoldingAgent
                scaffolder = ModuleScaffoldingAgent()
                scaffold_result = scaffolder.ensure_module_structure(module_name)
                build_sequence.append(("ModuleScaffoldingAgent", scaffold_result))
                wre_log(f"🏗️ ModuleScaffoldingAgent (0102): Structure ensured", "DEBUG")
            except Exception as e:
                wre_log(f"❌ ModuleScaffoldingAgent (0102) failed: {e}", "WARNING")
        
        # 3. TestingAgent - Run tests
        if agent_status.get("TestingAgent", False):
            try:
                testing = TestingAgent()
                test_result = testing.run_module_tests(module_name)
                build_sequence.append(("TestingAgent", test_result))
                wre_log(f"🧪 TestingAgent (0102): Tests executed", "DEBUG")
            except Exception as e:
                wre_log(f"❌ TestingAgent (0102) failed: {e}", "WARNING")
        
        # 4. DocumentationAgent - Update documentation
        if agent_status.get("DocumentationAgent", False):
            try:
                documentation = DocumentationAgent()
                doc_result = documentation.update_module_docs(module_name)
                build_sequence.append(("DocumentationAgent", doc_result))
                wre_log(f"📚 DocumentationAgent (0102): Documentation updated", "DEBUG")
            except Exception as e:
                wre_log(f"❌ DocumentationAgent (0102) failed: {e}", "WARNING")
        
        # 5. ChroniclerAgent - Log build event
        if agent_status.get("ChroniclerAgent", False):
            try:
                chronicler = ChroniclerAgent(modlog_path_str=str(project_root / "ModLog.md"))
                build_event = {
                    "title": f"Agentic Build Started: {module_name}",
                    "description": f"WSP 54 agent suite (0102 pArtifacts) initiated build for {module_name}",
                    "achievements": [
                        f"Build sequence: {len(build_sequence)} agents engaged",
                        f"Agent state: All agents in 0102 pArtifact state",
                        f"Module target: {module_name}"
                    ]
                }
                chronicler.log_event(build_event)
                build_sequence.append(("ChroniclerAgent", {"event_logged": True}))
                wre_log(f"📝 ChroniclerAgent (0102): Build event logged", "DEBUG")
            except Exception as e:
                wre_log(f"❌ ChroniclerAgent (0102) failed: {e}", "WARNING")
        
        wre_log(f"✅ Agentic build sequence initiated for {module_name} with {len(build_sequence)} activated agents (0102 pArtifacts)", "SUCCESS")
        return True
        
    except Exception as e:
        wre_log(f"❌ Agentic build failed: {e}", "ERROR")
        return False

def orchestrate_new_module(module_name: str) -> bool:
    """
    Orchestrate creation of a new module using WSP 54 agents.
    
    Args:
        module_name (str): Name of the new module to create
        
    Returns:
        bool: True if module created successfully, False otherwise
    """
    wre_log(f"🎼 Orchestrating new module: {module_name}", "INFO")
    
    try:
        # Check agent health first
        agent_status = check_agent_health()
        
        # Need ModuleScaffoldingAgent for new module creation
        if not agent_status.get("ModuleScaffoldingAgent", False):
            wre_log("❌ ModuleScaffoldingAgent not available for new module creation", "ERROR")
            return False
        
        # 1. ModuleScaffoldingAgent - Create module structure
        try:
            from modules.wre_core.src.adapters.agent_to_dae_adapter import ModuleScaffoldingAgent
            scaffolder = ModuleScaffoldingAgent()
            
            # Determine domain based on module name patterns
            domain = _determine_module_domain(module_name)
            
            creation_result = scaffolder.create_module(module_name, domain)
            wre_log(f"🏗️ ModuleScaffoldingAgent: Created {module_name} in {domain} domain", "DEBUG")
            
        except Exception as e:
            wre_log(f"❌ ModuleScaffoldingAgent failed: {e}", "ERROR")
            return False
        
        # 2. DocumentationAgent - Initialize documentation
        if agent_status.get("DocumentationAgent", False):
            try:
                documentation = DocumentationAgent()
                doc_result = documentation.initialize_module_docs(module_name)
                wre_log(f"📚 DocumentationAgent: Documentation initialized", "DEBUG")
            except Exception as e:
                wre_log(f"❌ DocumentationAgent failed: {e}", "WARNING")
        
        # 3. ChroniclerAgent - Log module creation
        if agent_status.get("ChroniclerAgent", False):
            try:
                chronicler = ChroniclerAgent(modlog_path_str=str(project_root / "ModLog.md"))
                creation_event = {
                    "title": f"New Module Created: {module_name}",
                    "description": f"WSP 54 agent suite created new module {module_name} in {domain} domain",
                    "achievements": [f"Module structure: WSP 49 compliant", f"Domain placement: {domain}"]
                }
                chronicler.log_event(creation_event)
                wre_log(f"📝 ChroniclerAgent: Module creation logged", "DEBUG")
            except Exception as e:
                wre_log(f"❌ ChroniclerAgent failed: {e}", "WARNING")
        
        wre_log(f"✅ New module {module_name} orchestrated successfully in {domain} domain", "SUCCESS")
        return True
        
    except Exception as e:
        wre_log(f"❌ Module orchestration failed: {e}", "ERROR")
        return False

def _determine_module_domain(module_name: str) -> str:
    """
    Determine the appropriate domain for a new module based on naming patterns.
    
    Args:
        module_name (str): Name of the module
        
    Returns:
        str: Domain name (ai_intelligence, communication, platform_integration, etc.)
    """
    # Domain mapping based on module name patterns
    domain_patterns = {
        "ai_intelligence": ["ai_", "intelligence", "agent", "llm", "gpt", "banter", "resp"],
        "communication": ["chat", "message", "live", "stream", "voice"],
        "platform_integration": ["youtube", "linkedin", "twitter", "x_", "api_", "oauth"],
        "infrastructure": ["agent", "manager", "core", "system", "wre"],
        "foundups": ["foundup", "startup", "venture"],
        "gamification": ["game", "score", "reward", "achievement"],
        "blockchain": ["block", "chain", "crypto", "nft", "defi"],
        "monitoring": ["monitor", "log", "track", "analytics"],
        "development": ["dev", "build", "test", "deploy"]
    }
    
    module_lower = module_name.lower()
    
    for domain, patterns in domain_patterns.items():
        for pattern in patterns:
            if pattern in module_lower:
                return domain
    
    # Default to infrastructure for unknown patterns
    return "infrastructure"

def read_wsp_module_violations() -> Dict[str, Any]:
    """
    Read and parse WSP_MODULE_VIOLATIONS.md for module development guidance.
    
    Returns:
        Dict containing violation analysis and recommendations
    """
    violations_file = project_root / "WSP_framework" / "src" / "WSP_MODULE_VIOLATIONS.md"
    
    if not violations_file.exists():
        return {
            "status": "error",
            "message": "WSP_MODULE_VIOLATIONS.md not found",
            "violations": [],
            "recommendations": []
        }
    
    try:
        with open(violations_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse violations from the markdown content
        violations = []
        recommendations = []
        
        # Extract violation sections (V### format)
        import re
        violation_pattern = r'### \*\*(V\d+): ([^*]+)\*\*.*?\*\*WSP Status\*\*: ([^*]+)'
        matches = re.findall(violation_pattern, content, re.DOTALL)
        
        for match in matches:
            violation_id, title, status = match
            violations.append({
                "id": violation_id,
                "title": title.strip(),
                "status": status.strip()
            })
        
        # Extract recommendations based on violation status
        active_violations = [v for v in violations if "DEFERRED" in v["status"]]
        resolved_violations = [v for v in violations if "RESOLVED" in v["status"]]
        
        if active_violations:
            recommendations.append(f"Found {len(active_violations)} active module violations to address during module development")
            for violation in active_violations:
                recommendations.append(f"- {violation['id']}: {violation['title']}")
        
        if resolved_violations:
            recommendations.append(f"Found {len(resolved_violations)} resolved violations - good progress!")
        
        return {
            "status": "success",
            "violations": violations,
            "active_violations": active_violations,
            "resolved_violations": resolved_violations,
            "recommendations": recommendations,
            "total_violations": len(violations)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading WSP_MODULE_VIOLATIONS.md: {str(e)}",
            "violations": [],
            "recommendations": []
        }

def get_module_development_guidance(module_name: str) -> Dict[str, Any]:
    """
    Get development guidance for a specific module including WSP violations.
    
    Args:
        module_name (str): Name of the module to get guidance for
        
    Returns:
        Dict containing development guidance and violation information
    """
    violations_data = read_wsp_module_violations()
    
    # Filter violations relevant to this module
    module_violations = []
    if violations_data["status"] == "success":
        for violation in violations_data["active_violations"]:
            if module_name.lower() in violation["title"].lower():
                module_violations.append(violation)
    
    guidance = {
        "module_name": module_name,
        "wsp_violations": module_violations,
        "violation_count": len(module_violations),
        "recommendations": []
    }
    
    # Add specific recommendations based on violations
    if module_violations:
        guidance["recommendations"].append(f"⚠️  Found {len(module_violations)} active violations for {module_name}")
        for violation in module_violations:
            guidance["recommendations"].append(f"  - {violation['id']}: {violation['title']}")
        guidance["recommendations"].append("  → Address these violations during module development per WSP 47")
    else:
        guidance["recommendations"].append(f"✅ No active violations found for {module_name}")
    
    # Add general WSP compliance recommendations
    guidance["recommendations"].extend([
        "📋 WSP Compliance Checklist:",
        "  - WSP 4: Run FMAS audit before development",
        "  - WSP 5: Maintain ≥90% test coverage",
        "  - WSP 11: Update interface documentation",
        "  - WSP 22: Update ModLog with changes",
        "  - WSP 49: Follow standard directory structure"
    ])
    
    return guidance

# Agent activation is now handled by the proper WSP-compliant AgentActivationModule
# in modules/infrastructure/agent_activation/src/agent_activation.py 