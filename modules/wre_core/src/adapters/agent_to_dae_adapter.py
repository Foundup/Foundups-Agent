"""
Agent to DAE Adapter Layer
Provides backward compatibility during WRE migration to DAE architecture.
Each adapter maintains the old agent interface while using DAE pattern memory.

This is a temporary bridge - will be removed after full migration.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import DAE cubes
from modules.infrastructure.infrastructure_orchestration_dae.src.infrastructure_dae import InfrastructureOrchestrationDAE
from modules.infrastructure.compliance_quality_dae.src.compliance_dae import ComplianceQualityDAE
from modules.infrastructure.knowledge_learning_dae.src.knowledge_dae import KnowledgeLearningDAE
from modules.infrastructure.maintenance_operations_dae.src.maintenance_dae import MaintenanceOperationsDAE
from modules.infrastructure.documentation_registry_dae.src.documentation_dae import DocumentationRegistryDAE


class JanitorAgent:
    """Adapter: JanitorAgent interface → Maintenance DAE patterns"""
    
    def __init__(self):
        self.dae = MaintenanceOperationsDAE()
        logger.info("JanitorAgent adapter initialized with Maintenance DAE")
    
    def clean_workspace(self) -> Dict[str, Any]:
        """Clean workspace using DAE cleanup patterns."""
        return self.dae.recall_pattern("cleanup_automation", {
            "action": "clean_workspace",
            "target": "temporary_files"
        })


class LoremasterAgent:
    """Adapter: LoremasterAgent interface → Knowledge DAE patterns"""
    
    def __init__(self):
        self.dae = KnowledgeLearningDAE()
        logger.info("LoremasterAgent adapter initialized with Knowledge DAE")
    
    def run_audit(self, root_path: Path) -> Dict[str, Any]:
        """Run documentation audit using DAE knowledge patterns."""
        return self.dae.recall_pattern("documentation_audit", {
            "action": "audit",
            "path": str(root_path)
        })
    
    def get_next_wsp_number(self) -> int:
        """Get next WSP number from pattern memory."""
        result = self.dae.recall_pattern("wsp_knowledge", {
            "query": "next_wsp_number"
        })
        return result.get("next_number", 81)


class ChroniclerAgent:
    """Adapter: ChroniclerAgent interface → Infrastructure DAE patterns"""
    
    def __init__(self, modlog_path_str: str = None):
        self.dae = InfrastructureOrchestrationDAE()
        self.modlog_path = modlog_path_str
        logger.info("ChroniclerAgent adapter initialized with Infrastructure DAE")
    
    def log_event(self, event: Dict[str, Any]) -> bool:
        """Log event using DAE event logging patterns."""
        return self.dae.recall_pattern("event_logging", {
            "event": event,
            "modlog_path": self.modlog_path
        })
    
    def get_last_event_time(self) -> str:
        """Get last event timestamp from pattern memory."""
        result = self.dae.recall_pattern("event_logging", {
            "query": "last_event_time"
        })
        return result.get("timestamp", "")


class ComplianceAgent:
    """Adapter: ComplianceAgent interface → Compliance DAE patterns"""
    
    def __init__(self):
        self.dae = ComplianceQualityDAE()
        logger.info("ComplianceAgent adapter initialized with Compliance DAE")
    
    def run_check(self, module_path: str) -> Dict[str, Any]:
        """Run compliance check using DAE validation patterns."""
        return self.dae.recall_pattern("wsp_validation", {
            "action": "check",
            "module_path": module_path
        })


class TestingAgent:
    """Adapter: TestingAgent interface → Compliance DAE patterns"""
    
    def __init__(self):
        self.dae = ComplianceQualityDAE()
        logger.info("TestingAgent adapter initialized with Compliance DAE")
    
    def check_coverage(self) -> Dict[str, Any]:
        """Check test coverage using DAE test patterns."""
        return self.dae.recall_pattern("test_execution", {
            "action": "coverage_check"
        })
    
    def run_module_tests(self, module_name: str) -> Dict[str, Any]:
        """Run module tests using DAE test patterns."""
        return self.dae.recall_pattern("test_execution", {
            "action": "run_tests",
            "module": module_name
        })


class ScoringAgent:
    """Adapter: ScoringAgent interface → Knowledge DAE patterns"""
    
    def __init__(self):
        self.dae = KnowledgeLearningDAE()
        logger.info("ScoringAgent adapter initialized with Knowledge DAE")
    
    def calculate_project_scores(self) -> Dict[str, Any]:
        """Calculate project scores using DAE scoring patterns."""
        return self.dae.recall_pattern("scoring_algorithms", {
            "action": "calculate_mps",
            "scope": "project"
        })


class DocumentationAgent:
    """Adapter: DocumentationAgent interface → Documentation DAE patterns"""
    
    def __init__(self):
        self.dae = DocumentationRegistryDAE()
        logger.info("DocumentationAgent adapter initialized with Documentation DAE")
    
    def update_module_docs(self, module_name: str) -> Dict[str, Any]:
        """Update module documentation using DAE template patterns."""
        return self.dae.recall_pattern("template_generation", {
            "action": "update_docs",
            "module": module_name
        })
    
    def initialize_module_docs(self, module_name: str) -> Dict[str, Any]:
        """Initialize module documentation using DAE template patterns."""
        return self.dae.recall_pattern("template_generation", {
            "action": "init_docs",
            "module": module_name
        })


class ModuleScaffoldingAgent:
    """Adapter: ModuleScaffoldingAgent interface → Infrastructure DAE patterns"""
    
    def __init__(self):
        self.dae = InfrastructureOrchestrationDAE()
        logger.info("ModuleScaffoldingAgent adapter initialized with Infrastructure DAE")
    
    def ensure_module_structure(self, module_name: str) -> Dict[str, Any]:
        """Ensure module structure using DAE scaffolding patterns."""
        return self.dae.recall_pattern("module_scaffolding", {
            "action": "ensure_structure",
            "module": module_name
        })
    
    def create_module(self, module_name: str, domain: str) -> Dict[str, Any]:
        """Create new module using DAE scaffolding patterns."""
        return self.dae.recall_pattern("module_scaffolding", {
            "action": "create",
            "module": module_name,
            "domain": domain
        })


class AgentActivationModule:
    """
    Adapter: AgentActivationModule interface → DAE (always active)
    DAEs don't need activation - they're always in pattern memory mode.
    """
    
    def __init__(self):
        logger.info("AgentActivationModule adapter - DAEs are always active")
    
    def activate_wsp54_agents(self, dormant_agents: List) -> Dict[str, bool]:
        """
        DAEs are always active - return success for all.
        This maintains compatibility while WRE expects activation.
        """
        return {agent[0]: True for agent in dormant_agents}


# Utility function for gradual migration
def get_adapter_for_agent(agent_name: str):
    """
    Get the appropriate adapter for a legacy agent name.
    This helps with incremental migration.
    """
    adapters = {
        "JanitorAgent": JanitorAgent,
        "LoremasterAgent": LoremasterAgent,
        "ChroniclerAgent": ChroniclerAgent,
        "ComplianceAgent": ComplianceAgent,
        "TestingAgent": TestingAgent,
        "ScoringAgent": ScoringAgent,
        "DocumentationAgent": DocumentationAgent,
        "ModuleScaffoldingAgent": ModuleScaffoldingAgent,
        "AgentActivationModule": AgentActivationModule
    }
    
    adapter_class = adapters.get(agent_name)
    if adapter_class:
        return adapter_class()
    else:
        raise ValueError(f"No adapter found for agent: {agent_name}")


logger.info("Agent to DAE adapter layer loaded - Ready for WRE migration")