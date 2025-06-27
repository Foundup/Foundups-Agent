import sys
import json
from pathlib import Path
from typing import Dict, List

# Add project root to resolve imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.infrastructure.agents.janitor_agent.src.janitor_agent import JanitorAgent
from modules.infrastructure.agents.loremaster_agent.src.loremaster_agent import LoremasterAgent
from modules.infrastructure.agents.chronicler_agent.src.chronicler_agent import ChroniclerAgent
from modules.infrastructure.agents.compliance_agent.src.compliance_agent import ComplianceAgent
from modules.infrastructure.agents.testing_agent.src.testing_agent import TestingAgent
from modules.infrastructure.agents.scoring_agent.src.scoring_agent import ScoringAgent
from modules.infrastructure.agents.documentation_agent.src.documentation_agent import DocumentationAgent

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
    for agent_name, agent_class in required_agents:
        try:
            # Try to instantiate the agent
            test_agent = agent_class()
            agent_status[agent_name] = True
            wre_log(f"Agent {agent_name} health check: ✅ OPERATIONAL", "DEBUG")
        except Exception as e:
            agent_status[agent_name] = False
            wre_log(f"Agent {agent_name} health check: ❌ FAILED - {e}", "WARNING")
    
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