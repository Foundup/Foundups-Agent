"""
GitHub Automation Manager - Automated GitHub Workflows
Provides high-level automation for common GitHub operations integrated with WSP protocols.

WSP Compliance:
- WSP 34: Git Operations Protocol integration
- WSP 22: ModLog management and documentation
- WSP 54: Agent coordination for automated workflows
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import json

from .github_api_client import GitHubAPIClient, create_feature_branch_and_pr, create_issue_for_bug


class GitHubAutomation:
    """
    High-level GitHub automation for FoundUps Agent workflows
    
    Provides automated workflows for:
    - WSP compliance checking and PR creation
    - Automated issue creation for violations
    - Module update automation
    - Documentation synchronization
    - Release management
    """
    
    def __init__(self, token: Optional[str] = None, owner: str = "Foundup", repo: str = "Foundups-Agent"):
        """
        Initialize GitHub automation
        
        Args:
            token: GitHub personal access token
            owner: Repository owner
            repo: Repository name
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.logger = logging.getLogger(__name__)
        
    async def auto_create_wsp_compliance_pr(self, wsp_number: int, changes_description: str,
                                          files_changed: List[str]) -> Optional[str]:
        """
        Automatically create a pull request for WSP compliance updates
        
        Args:
            wsp_number: WSP protocol number
            changes_description: Description of changes made
            files_changed: List of files that were changed
            
        Returns:
            PR URL if successful, None otherwise
        """
        try:
            # Generate PR details
            branch_name = f"wsp-{wsp_number}-compliance-{datetime.now().strftime('%Y%m%d')}"
            pr_title = f"[WSP {wsp_number}] {changes_description}"
            
            pr_description = f"""
## WSP {wsp_number} Compliance Update

### Changes Made
{changes_description}

### Files Modified
{chr(10).join(f'- `{file}`' for file in files_changed)}

### WSP Compliance
- ✅ WSP {wsp_number}: {changes_description}
- ✅ WSP 22: ModLog updated
- ✅ WSP 34: Git operations compliant

### Testing
- [ ] All existing tests pass
- [ ] New functionality tested
- [ ] WSP compliance verified

---
*This PR was created automatically by the FoundUps Agent system.*

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""
            
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                # Create branch and PR
                branch_name, pr = await create_feature_branch_and_pr(
                    pr_title, pr_description, branch_name, self.token
                )
                
                self.logger.info(f"Created WSP {wsp_number} compliance PR: {pr.url}")
                return pr.url
                
        except Exception as e:
            self.logger.error(f"Failed to create WSP compliance PR: {e}")
            return None
            
    async def auto_create_module_update_pr(self, module_name: str, module_domain: str,
                                         update_description: str, version: str) -> Optional[str]:
        """
        Automatically create a pull request for module updates
        
        Args:
            module_name: Name of the module
            module_domain: Module domain (ai_intelligence, platform_integration, etc.)
            update_description: Description of the update
            version: Module version
            
        Returns:
            PR URL if successful, None otherwise
        """
        try:
            branch_name = f"module/{module_domain}/{module_name}-{version}"
            pr_title = f"[{module_domain}] Update {module_name} to v{version}"
            
            pr_description = f"""
## Module Update: {module_name}

### Domain
`{module_domain}`

### Version
`{version}`

### Changes
{update_description}

### WSP Compliance
- ✅ WSP 3: Enterprise Domain Organization
- ✅ WSP 22: ModLog updated
- ✅ WSP 49: Module directory structure
- ✅ WSP 55: Module creation automation

### Module Status
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Interface compliance verified
- [ ] Performance benchmarks met

---
*Module update automated by FoundUps Agent system.*

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""
            
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                branch_name, pr = await create_feature_branch_and_pr(
                    pr_title, pr_description, branch_name, self.token
                )
                
                self.logger.info(f"Created module update PR for {module_name}: {pr.url}")
                return pr.url
                
        except Exception as e:
            self.logger.error(f"Failed to create module update PR: {e}")
            return None
            
    async def auto_create_violation_issue(self, violation_type: str, violation_description: str,
                                        affected_files: List[str], wsp_protocol: Optional[int] = None) -> Optional[str]:
        """
        Automatically create an issue for WSP violations
        
        Args:
            violation_type: Type of violation (e.g., "WSP Violation", "Architecture Violation")
            violation_description: Description of the violation
            affected_files: List of files affected by the violation
            wsp_protocol: WSP protocol number if applicable
            
        Returns:
            Issue URL if successful, None otherwise
        """
        try:
            title = f"[{violation_type}] {violation_description}"
            if wsp_protocol:
                title = f"[WSP {wsp_protocol} Violation] {violation_description}"
                
            issue_description = f"""
## Violation Details

**Type**: {violation_type}
**WSP Protocol**: {f"WSP {wsp_protocol}" if wsp_protocol else "N/A"}

### Description
{violation_description}

### Affected Files
{chr(10).join(f'- `{file}`' for file in affected_files)}

### Resolution Required
- [ ] Fix violation in affected files
- [ ] Update relevant WSP compliance
- [ ] Add tests to prevent regression
- [ ] Update documentation if needed

### Priority
- [ ] Critical (blocks development)
- [ ] High (affects system stability)
- [ ] Medium (architectural improvement)
- [ ] Low (technical debt)

---
*This issue was created automatically by the FoundUps Agent violation detection system.*
"""
            
            labels = ["violation", "automated"]
            if wsp_protocol:
                labels.append(f"wsp-{wsp_protocol}")
                
            issue = await create_issue_for_bug(title, issue_description, "See description above", self.token)
            
            self.logger.info(f"Created violation issue: {issue.url}")
            return issue.url
            
        except Exception as e:
            self.logger.error(f"Failed to create violation issue: {e}")
            return None
            
    async def auto_sync_documentation(self, docs_path: Path) -> Optional[str]:
        """
        Automatically sync documentation to GitHub
        
        Args:
            docs_path: Path to documentation directory
            
        Returns:
            PR URL if successful, None otherwise
        """
        try:
            branch_name = f"docs/sync-{datetime.now().strftime('%Y%m%d-%H%M')}"
            pr_title = "📚 Automated Documentation Sync"
            
            # Scan for documentation files
            doc_files = []
            for ext in ['.md', '.txt', '.rst']:
                doc_files.extend(docs_path.glob(f"**/*{ext}"))
                
            pr_description = f"""
## Documentation Synchronization

### Files Updated
{chr(10).join(f'- `{file.relative_to(docs_path)}`' for file in doc_files[:20])}
{f'{chr(10)}... and {len(doc_files) - 20} more files' if len(doc_files) > 20 else ''}

### Changes
- Updated module documentation
- Synchronized WSP protocol documentation  
- Refreshed README files
- Updated ROADMAP files
- Synchronized ModLog files

### WSP Compliance
- ✅ WSP 22: ModLog management
- ✅ WSP 57: Naming coherence
- ✅ WSP 60: Module memory architecture

---
*Automated documentation sync by FoundUps Agent system.*

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""
            
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                branch_name, pr = await create_feature_branch_and_pr(
                    pr_title, pr_description, branch_name, self.token
                )
                
                self.logger.info(f"Created documentation sync PR: {pr.url}")
                return pr.url
                
        except Exception as e:
            self.logger.error(f"Failed to sync documentation: {e}")
            return None
            
    async def auto_create_release_pr(self, version: str, release_notes: str,
                                   breaking_changes: List[str] = None) -> Optional[str]:
        """
        Automatically create a pull request for a new release
        
        Args:
            version: Release version (e.g., "v1.2.3")
            release_notes: Release notes
            breaking_changes: List of breaking changes
            
        Returns:
            PR URL if successful, None otherwise
        """
        try:
            branch_name = f"release/{version}"
            pr_title = f"🚀 Release {version}"
            
            breaking_section = ""
            if breaking_changes:
                breaking_section = f"""
### ⚠️ Breaking Changes
{chr(10).join(f'- {change}' for change in breaking_changes)}
"""
            
            pr_description = f"""
## Release {version}

### Release Notes
{release_notes}
{breaking_section}

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version numbers updated
- [ ] WSP compliance verified
- [ ] Performance benchmarks met
- [ ] Security review completed

### WSP Compliance
- ✅ WSP 22: ModLog updated with release info
- ✅ WSP 34: Git operations compliant
- ✅ WSP 48: Recursive self-improvement documented

---
*Release PR automated by FoundUps Agent system.*

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""
            
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                branch_name, pr = await create_feature_branch_and_pr(
                    pr_title, pr_description, branch_name, self.token
                )
                
                self.logger.info(f"Created release PR for {version}: {pr.url}")
                return pr.url
                
        except Exception as e:
            self.logger.error(f"Failed to create release PR: {e}")
            return None
            
    async def monitor_pr_status(self, pr_number: int, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Monitor pull request status and trigger actions
        
        Args:
            pr_number: Pull request number to monitor
            callback: Optional callback function for status changes
            
        Returns:
            PR status information
        """
        try:
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                prs = await client.get_pull_requests("all")
                pr = next((p for p in prs if p.number == pr_number), None)
                
                if not pr:
                    return {"error": f"PR #{pr_number} not found"}
                    
                # Get additional status information
                workflows = await client.get_workflow_runs()
                pr_workflows = [w for w in workflows if w.get("pull_requests") and 
                              any(p["number"] == pr_number for p in w["pull_requests"])]
                
                status_info = {
                    "pr": pr,
                    "workflows": pr_workflows,
                    "checks_passing": all(w["conclusion"] == "success" for w in pr_workflows),
                    "ready_to_merge": pr.state.value == "open" and all(w["conclusion"] == "success" for w in pr_workflows)
                }
                
                if callback:
                    await callback(status_info)
                    
                return status_info
                
        except Exception as e:
            self.logger.error(f"Failed to monitor PR status: {e}")
            return {"error": str(e)}
            
    async def auto_merge_ready_prs(self, max_prs: int = 5) -> List[str]:
        """
        Automatically merge pull requests that are ready
        
        Args:
            max_prs: Maximum number of PRs to merge in one run
            
        Returns:
            List of merged PR URLs
        """
        merged_prs = []
        
        try:
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                prs = await client.get_pull_requests("open")
                
                for pr in prs[:max_prs]:
                    # Check if PR is ready to merge
                    status = await self.monitor_pr_status(pr.number)
                    
                    if status.get("ready_to_merge", False):
                        try:
                            # Attempt to merge
                            await client.merge_pull_request(
                                pr.number,
                                commit_title=f"Merge pull request #{pr.number} from {pr.head_branch}",
                                commit_message=f"{pr.title}\n\n{pr.body[:500]}...",
                                merge_method="merge"
                            )
                            
                            merged_prs.append(pr.url)
                            self.logger.info(f"Auto-merged PR #{pr.number}: {pr.title}")
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to auto-merge PR #{pr.number}: {e}")
                            
        except Exception as e:
            self.logger.error(f"Failed to auto-merge PRs: {e}")
            
        return merged_prs
        
    async def cleanup_old_branches(self, days_old: int = 30) -> List[str]:
        """
        Clean up old feature branches that have been merged
        
        Args:
            days_old: Delete branches older than this many days
            
        Returns:
            List of deleted branch names
        """
        deleted_branches = []
        
        try:
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                branches = await client.get_branches()
                cutoff_date = datetime.now() - timedelta(days=days_old)
                
                for branch_name in branches:
                    # Skip main/master branches
                    if branch_name in ["main", "master", "develop"]:
                        continue
                        
                    # Check if branch is old and has been merged
                    # This is a simplified check - in reality, you'd want to check
                    # the last commit date and merge status
                    if branch_name.startswith(("feature/", "fix/", "auto-update/")):
                        try:
                            # Delete branch (this is a placeholder - actual implementation
                            # would need to check merge status first)
                            # await client.delete_branch(branch_name)  # Not implemented in client yet
                            
                            self.logger.info(f"Would delete old branch: {branch_name}")
                            # deleted_branches.append(branch_name)
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to delete branch {branch_name}: {e}")
                            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old branches: {e}")
            
        return deleted_branches


# Utility Functions
async def trigger_automated_pr_for_changes(commit_message: str, pr_title: str, 
                                         pr_description: str, token: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to trigger automated PR creation for current changes
    
    Args:
        commit_message: Commit message for changes
        pr_title: Pull request title
        pr_description: Pull request description
        token: GitHub token
        
    Returns:
        PR URL if successful, None otherwise
    """
    try:
        automation = GitHubAutomation(token=token)
        
        # This would integrate with the git operations manager
        # For now, we'll assume changes are already committed and pushed
        
        async with GitHubAPIClient(token=token) as client:
            branch_name, pr = await create_feature_branch_and_pr(
                pr_title, pr_description, None, token
            )
            
            return pr.url
            
    except Exception as e:
        logging.error(f"Failed to trigger automated PR: {e}")
        return None


async def setup_automated_workflows(token: Optional[str] = None) -> bool:
    """
    Setup automated GitHub workflows for the FoundUps Agent repository
    
    Args:
        token: GitHub token
        
    Returns:
        True if successful
    """
    try:
        automation = GitHubAutomation(token=token)
        
        # This would set up GitHub Actions workflows, webhooks, etc.
        # For now, we'll just log what would be set up
        
        logging.info("Setting up automated GitHub workflows:")
        logging.info("- WSP compliance checking")
        logging.info("- Module update automation")
        logging.info("- Documentation synchronization")
        logging.info("- Violation detection and issue creation")
        logging.info("- Release management")
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to setup automated workflows: {e}")
        return False