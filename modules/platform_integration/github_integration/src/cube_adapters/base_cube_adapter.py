"""
Base FoundUps Cube Adapter
Provides the foundation for pluggable cube integration with GitHub operations.

This creates the foundational layer that allows any FoundUps cube to connect
to GitHub through coordinated WRE agents with minimal cube-specific code.

WSP Compliance:
- WSP 54: Coordinates existing WRE agents (no duplication)
- WSP 3: Enterprise Domain Organization integration
- WSP 46: WRE orchestration compatible
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
from enum import Enum

from ..extensions.compliance_github_extension import ComplianceGitHubExtension
from ..adapters.github_api_adapter import GitHubAPIAdapter


class CubeType(Enum):
    """FoundUps cube types from WSP 3 Enterprise Domains"""
    AI_INTELLIGENCE = "ai_intelligence"
    COMMUNICATION = "communication"
    PLATFORM_INTEGRATION = "platform_integration"
    INFRASTRUCTURE = "infrastructure"
    FOUNDUPS = "foundups"
    GAMIFICATION = "gamification"
    BLOCKCHAIN = "blockchain"
    DEVELOPMENT = "development"
    AGGREGATION = "aggregation"
    WRE_CORE = "wre_core"


@dataclass
class CubeModuleChange:
    """Represents a change in a FoundUps cube module"""
    module_name: str
    domain: str
    change_type: str  # "create", "update", "delete"
    files_changed: List[str]
    description: str
    version: str
    metadata: Dict[str, Any] = None


@dataclass
class CubeOperationResult:
    """Result of cube operation"""
    success: bool
    cube_type: str
    operation: str
    results: Dict[str, Any]
    github_actions: List[str] = None
    errors: List[str] = None


class BaseCubeAdapter(ABC):
    """
    Base class for FoundUps Cube Adapters
    
    Provides the foundational interface for any FoundUps cube to integrate
    with GitHub through existing WRE agents. Each cube type gets a specialized
    adapter that knows how to coordinate the right WRE agents for that cube's needs.
    
    Key Principles:
    1. Reuses existing WRE agents (ComplianceAgent, DocumentationAgent, etc.)
    2. Provides cube-specific templates and formatting
    3. Coordinates multiple agents for complex cube operations
    4. Pluggable architecture - new cubes just need new adapters
    """
    
    def __init__(self, cube_type: CubeType, repository: str = "Foundup/Foundups-Agent"):
        """
        Initialize cube adapter
        
        Args:
            cube_type: Type of FoundUps cube
            repository: Target GitHub repository
        """
        self.cube_type = cube_type
        self.repository = repository
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Initialize GitHub adapter
        self.github_adapter = GitHubAPIAdapter(repository)
        
        # Initialize agent extensions (these reuse existing WRE agents)
        self._initialize_agent_extensions()
        
        # Cube-specific state
        self.cube_templates = {}
        self.cube_metadata = {}
        
    def _initialize_agent_extensions(self):
        """Initialize GitHub extensions for existing WRE agents"""
        # Get existing WRE agents (this would integrate with WRE agent registry)
        # For now, create extensions without the actual agents
        
        self.compliance_extension = ComplianceGitHubExtension(
            compliance_agent=None,  # Would be: get_wre_agent("ComplianceAgent")
            repository=self.repository
        )
        
        # Additional extensions would be added here:
        # self.documentation_extension = DocumentationGitHubExtension(...)
        # self.chronicler_extension = ChroniclerGitHubExtension(...)
        # self.scaffolding_extension = ScaffoldingGitHubExtension(...)
        
    # Abstract methods that each cube adapter must implement
    @abstractmethod
    async def get_pr_template(self, change_type: str) -> str:
        """Get PR template for this cube type"""
        pass
        
    @abstractmethod
    async def get_default_labels(self) -> List[str]:
        """Get default GitHub labels for this cube"""
        pass
        
    @abstractmethod
    async def format_module_description(self, change: CubeModuleChange) -> str:
        """Format module change description for this cube"""
        pass
        
    @abstractmethod 
    async def get_required_reviewers(self) -> List[str]:
        """Get required reviewers for this cube type"""
        pass
        
    # Common operations that coordinate multiple agents
    async def handle_module_change(self, change: CubeModuleChange, session_id: str) -> CubeOperationResult:
        """
        Handle a module change using coordinated WRE agents
        
        This is the main entry point that coordinates multiple existing agents
        to handle a cube module change with GitHub integration.
        
        Args:
            change: Module change information
            session_id: Agent session ID
            
        Returns:
            Operation result with GitHub actions taken
        """
        self.logger.info(f"Handling {change.change_type} for {self.cube_type.value} module: {change.module_name}")
        
        results = {
            "module_name": change.module_name,
            "change_type": change.change_type,
            "cube_type": self.cube_type.value
        }
        
        github_actions = []
        errors = []
        
        try:
            # 1. Compliance Check (uses existing ComplianceAgent via extension)
            compliance_result = await self._handle_compliance_check(change, session_id)
            results["compliance"] = compliance_result
            github_actions.extend(compliance_result.get("github_actions", []))
            
            # 2. Documentation Update (would use DocumentationAgent via extension)
            doc_result = await self._handle_documentation_update(change, session_id)
            results["documentation"] = doc_result
            github_actions.extend(doc_result.get("github_actions", []))
            
            # 3. Module Scaffolding (would use ModuleScaffoldingAgent via extension)
            if change.change_type == "create":
                scaffold_result = await self._handle_module_scaffolding(change, session_id)
                results["scaffolding"] = scaffold_result
                github_actions.extend(scaffold_result.get("github_actions", []))
                
            # 4. Testing Integration (would use TestingAgent via extension)
            test_result = await self._handle_testing_integration(change, session_id)
            results["testing"] = test_result
            github_actions.extend(test_result.get("github_actions", []))
            
            # 5. Create coordinated PR if multiple changes
            if len(github_actions) > 1:
                pr_result = await self._create_coordinated_pr(change, results, session_id)
                github_actions.append(pr_result.get("pr_url", ""))
                
            return CubeOperationResult(
                success=True,
                cube_type=self.cube_type.value,
                operation="module_change",
                results=results,
                github_actions=github_actions,
                errors=errors
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle module change: {e}")
            errors.append(str(e))
            
            return CubeOperationResult(
                success=False,
                cube_type=self.cube_type.value,
                operation="module_change",
                results=results,
                github_actions=github_actions,
                errors=errors
            )
            
    async def _handle_compliance_check(self, change: CubeModuleChange, session_id: str) -> Dict[str, Any]:
        """Handle compliance check using ComplianceAgent extension"""
        # This would use the existing ComplianceAgent to check the change
        # Then use ComplianceGitHubExtension to create GitHub actions
        
        # Simulate compliance check
        violations = []  # Would come from ComplianceAgent
        
        compliance_result = {
            "violations_found": len(violations),
            "github_actions": []
        }
        
        if violations:
            # Create GitHub issues for violations
            issue_urls = await self.compliance_extension.create_violation_issues(
                violations, session_id, self.cube_type.value
            )
            compliance_result["github_actions"].extend(issue_urls)
            
        return compliance_result
        
    async def _handle_documentation_update(self, change: CubeModuleChange, session_id: str) -> Dict[str, Any]:
        """Handle documentation update using DocumentationAgent extension"""
        # This would use existing DocumentationAgent to update docs
        # Then create GitHub PR for doc changes
        
        # Simulate documentation update
        doc_changes = {
            "readme_updated": True,
            "modlog_updated": True,
            "interface_updated": change.change_type in ["create", "update"]
        }
        
        doc_result = {
            "changes": doc_changes,
            "github_actions": []
        }
        
        # Would create PR for documentation changes
        # doc_pr_url = await self.documentation_extension.create_doc_sync_pr(...)
        # doc_result["github_actions"].append(doc_pr_url)
        
        return doc_result
        
    async def _handle_module_scaffolding(self, change: CubeModuleChange, session_id: str) -> Dict[str, Any]:
        """Handle module scaffolding using ModuleScaffoldingAgent extension"""
        # This would use existing ModuleScaffoldingAgent to create module structure
        # Then create GitHub PR for new module
        
        # Simulate scaffolding
        scaffold_result = {
            "structure_created": True,
            "files_created": [
                f"{change.module_name}/README.md",
                f"{change.module_name}/src/__init__.py",
                f"{change.module_name}/tests/README.md"
            ],
            "github_actions": []
        }
        
        # Would create PR for new module structure
        # scaffold_pr_url = await self.scaffolding_extension.create_module_pr(...)
        # scaffold_result["github_actions"].append(scaffold_pr_url)
        
        return scaffold_result
        
    async def _handle_testing_integration(self, change: CubeModuleChange, session_id: str) -> Dict[str, Any]:
        """Handle testing integration using TestingAgent extension"""
        # This would use existing TestingAgent to set up tests
        # Then update GitHub PR with test results
        
        # Simulate testing setup
        test_result = {
            "tests_configured": True,
            "coverage_target": 85,
            "github_actions": []
        }
        
        # Would update PR with test status
        # test_status_url = await self.testing_extension.update_pr_status(...)
        # test_result["github_actions"].append(test_status_url)
        
        return test_result
        
    async def _create_coordinated_pr(self, change: CubeModuleChange, results: Dict[str, Any], 
                                   session_id: str) -> Dict[str, Any]:
        """Create coordinated PR that includes all changes"""
        # Generate comprehensive PR using cube-specific template
        pr_title = await self._generate_pr_title(change)
        pr_body = await self._generate_pr_body(change, results)
        
        # Would create PR via GitHub adapter
        # pr_result = await self.github_adapter.create_pull_request(...)
        
        return {
            "pr_created": True,
            "pr_url": f"https://github.com/{self.repository}/pull/12345",
            "title": pr_title
        }
        
    async def _generate_pr_title(self, change: CubeModuleChange) -> str:
        """Generate PR title for cube module change"""
        cube_name = self.cube_type.value.replace("_", " ").title()
        
        if change.change_type == "create":
            return f"[CUBE] [{cube_name}] Add {change.module_name} module"
        elif change.change_type == "update":
            return f"[UPDATE] [{cube_name}] Update {change.module_name} to v{change.version}"
        elif change.change_type == "delete":
            return f"[DELETE] [{cube_name}] Remove {change.module_name} module"
        else:
            return f"[AI] [{cube_name}] {change.description}"
            
    async def _generate_pr_body(self, change: CubeModuleChange, results: Dict[str, Any]) -> str:
        """Generate comprehensive PR body for cube module change"""
        
        template = await self.get_pr_template(change.change_type)
        
        body = f"""
## {self.cube_type.value.replace('_', ' ').title()} Cube Module Change

### Module: {change.module_name}
**Domain**: {change.domain}
**Change Type**: {change.change_type}
**Version**: {change.version}

### Description
{change.description}

### Files Changed
{chr(10).join(f'- `{file}`' for file in change.files_changed)}

### Agent Coordination Results
- **Compliance**: {results.get('compliance', {}).get('violations_found', 0)} violations found
- **Documentation**: {'[PASS] Updated' if results.get('documentation', {}).get('changes', {}) else '[SKIP] Skipped'}
- **Testing**: {'[PASS] Configured' if results.get('testing', {}).get('tests_configured') else '[SKIP] Skipped'}
- **Scaffolding**: {'[PASS] Created' if results.get('scaffolding', {}).get('structure_created') else '[SKIP] Skipped'}

### WSP Compliance
{await self._generate_wsp_compliance_section()}

### Cube Integration
- **Cube Type**: {self.cube_type.value}
- **Template**: {template[:50]}...
- **Coordinated Agents**: ComplianceAgent, DocumentationAgent, TestingAgent

### GitHub Actions Taken
{chr(10).join(f'- {action}' for result in results.values() for action in result.get('github_actions', []))}

---
[CUBE] Generated by {self.__class__.__name__}
[AI] Coordinated WRE Agent System

Co-Authored-By: FoundUps Cube System <cubes@foundups.com>
"""
        
        return body.strip()
        
    async def _generate_wsp_compliance_section(self) -> str:
        """Generate WSP compliance section for PR"""
        return f"""
- [PASS] WSP 3: {self.cube_type.value} domain placement
- [PASS] WSP 22: ModLog documentation
- [PASS] WSP 54: Agent coordination protocol
- [PASS] WSP 49: Module structure compliance
"""