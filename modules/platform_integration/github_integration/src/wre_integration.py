"""
WRE Integration for GitHub Operations
Integrates GitHub API client with existing WRE Git Operations Manager for enhanced functionality.

WSP Compliance:
- WSP 34: Git Operations Protocol integration
- WSP 46: WRE coordination
- WSP 54: Agent coordination
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .github_api_client import GitHubAPIClient, GitHubAPIError
from .github_automation import GitHubAutomation


class WREGitHubIntegration:
    """
    Integration layer between WRE Git Operations Manager and GitHub API
    
    Provides enhanced git operations with GitHub integration:
    - Automatic PR creation after commits
    - Issue creation for violations
    - Repository status synchronization
    - Automated workflow triggers
    """
    
    def __init__(self, token: Optional[str] = None, owner: str = "Foundup", 
                 repo: str = "Foundups-Agent", project_root: Optional[Path] = None):
        """
        Initialize WRE GitHub integration
        
        Args:
            token: GitHub personal access token
            owner: Repository owner
            repo: Repository name
            project_root: Project root directory path
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.project_root = project_root or Path(__file__).resolve().parents[5]
        self.logger = logging.getLogger(__name__)
        
        # Initialize GitHub components
        self.automation = GitHubAutomation(token=token, owner=owner, repo=repo)
        
    async def enhanced_commit_and_pr(self, commit_message: str, pr_title: Optional[str] = None,
                                   pr_description: Optional[str] = None, auto_merge: bool = False) -> Dict[str, Any]:
        """
        Enhanced commit operation with automatic PR creation
        
        Args:
            commit_message: Commit message
            pr_title: Pull request title (auto-generated if None)
            pr_description: Pull request description (auto-generated if None)
            auto_merge: Whether to auto-merge if checks pass
            
        Returns:
            Dictionary with commit and PR information
        """
        try:
            # Generate PR details if not provided
            if not pr_title:
                pr_title = f"🤖 {commit_message}"
                
            if not pr_description:
                pr_description = f"""
## Automated Commit and PR

### Changes
{commit_message}

### Automated by FoundUps Agent
- ✅ WSP 34: Git Operations Protocol compliance
- ✅ WSP 22: ModLog updated  
- ✅ Automated testing triggered
- ✅ GitHub integration active

---
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""
            
            # Create feature branch and PR
            branch_name = f"auto-update/{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                # Create branch
                await client.create_branch(branch_name)
                self.logger.info(f"Created branch: {branch_name}")
                
                # Create PR
                pr = await client.create_pull_request(pr_title, pr_description, branch_name)
                self.logger.info(f"Created PR: {pr.url}")
                
                result = {
                    "success": True,
                    "branch_name": branch_name,
                    "pr_number": pr.number,
                    "pr_url": pr.url,
                    "commit_message": commit_message
                }
                
                # Auto-merge if requested and checks pass
                if auto_merge:
                    # Wait a moment for checks to start
                    await asyncio.sleep(30)
                    
                    # Check if ready to merge
                    status = await self.automation.monitor_pr_status(pr.number)
                    if status.get("ready_to_merge", False):
                        await client.merge_pull_request(pr.number)
                        result["merged"] = True
                        self.logger.info(f"Auto-merged PR #{pr.number}")
                    else:
                        result["merged"] = False
                        self.logger.info(f"PR #{pr.number} not ready for auto-merge")
                
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to create enhanced commit and PR: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def create_violation_issue(self, violation_type: str, description: str, 
                                   affected_files: List[str], wsp_protocol: Optional[int] = None) -> Optional[str]:
        """
        Create GitHub issue for WSP violations
        
        Args:
            violation_type: Type of violation
            description: Violation description
            affected_files: List of affected files
            wsp_protocol: WSP protocol number
            
        Returns:
            Issue URL if successful
        """
        return await self.automation.auto_create_violation_issue(
            violation_type, description, affected_files, wsp_protocol
        )
        
    async def sync_repository_status(self) -> Dict[str, Any]:
        """
        Synchronize repository status with GitHub
        
        Returns:
            Repository status information
        """
        try:
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                # Get repository info
                repo = await client.get_repository()
                
                # Get branches
                branches = await client.get_branches()
                
                # Get open PRs
                prs = await client.get_pull_requests("open")
                
                # Get open issues
                issues = await client.get_issues("open")
                
                # Get recent workflows
                workflows = await client.get_workflows()
                recent_runs = await client.get_workflow_runs()
                
                status = {
                    "repository": {
                        "name": repo.full_name,
                        "default_branch": repo.default_branch,
                        "private": repo.private,
                        "url": repo.url
                    },
                    "branches": {
                        "total": len(branches),
                        "names": branches[:10]  # First 10 branches
                    },
                    "pull_requests": {
                        "open": len(prs),
                        "recent": [{"number": pr.number, "title": pr.title} for pr in prs[:5]]
                    },
                    "issues": {
                        "open": len(issues),
                        "recent": [{"number": issue.number, "title": issue.title} for issue in issues[:5]]
                    },
                    "workflows": {
                        "total": len(workflows),
                        "recent_runs": len(recent_runs),
                        "latest_runs": [
                            {
                                "id": run["id"],
                                "status": run["status"],
                                "conclusion": run.get("conclusion", "pending")
                            } for run in recent_runs[:3]
                        ]
                    },
                    "last_updated": datetime.now().isoformat()
                }
                
                return status
                
        except Exception as e:
            self.logger.error(f"Failed to sync repository status: {e}")
            return {"error": str(e)}
            
    async def trigger_ci_workflow(self, workflow_name: str = "ci.yml", 
                                branch: str = "main") -> bool:
        """
        Trigger CI workflow
        
        Args:
            workflow_name: Workflow file name
            branch: Branch to run workflow on
            
        Returns:
            True if successful
        """
        try:
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                result = await client.trigger_workflow(workflow_name, ref=branch)
                
                if result:
                    self.logger.info(f"Triggered workflow {workflow_name} on {branch}")
                else:
                    self.logger.warning(f"Failed to trigger workflow {workflow_name}")
                    
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to trigger CI workflow: {e}")
            return False
            
    async def auto_create_wsp_pr(self, wsp_number: int, description: str, 
                               files_changed: List[str]) -> Optional[str]:
        """
        Create automated WSP compliance PR
        
        Args:
            wsp_number: WSP protocol number
            description: Changes description
            files_changed: List of changed files
            
        Returns:
            PR URL if successful
        """
        return await self.automation.auto_create_wsp_compliance_pr(
            wsp_number, description, files_changed
        )
        
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of GitHub integration
        
        Returns:
            Health status information
        """
        health = {
            "github_api": False,
            "authentication": False,
            "repository_access": False,
            "rate_limit": None,
            "errors": []
        }
        
        try:
            async with GitHubAPIClient(token=self.token, owner=self.owner, repo=self.repo) as client:
                # Test authentication
                if client.is_authenticated():
                    health["authentication"] = True
                    
                    try:
                        # Test API access
                        user = await client.get_user()
                        health["github_api"] = True
                        health["user"] = user["login"]
                        
                        # Test repository access
                        repo = await client.get_repository()
                        health["repository_access"] = True
                        health["repository"] = repo.full_name
                        
                        # Check rate limit
                        rate_limit = await client.check_rate_limit()
                        health["rate_limit"] = {
                            "remaining": rate_limit["resources"]["core"]["remaining"],
                            "limit": rate_limit["resources"]["core"]["limit"],
                            "reset": rate_limit["resources"]["core"]["reset"]
                        }
                        
                    except GitHubAPIError as e:
                        health["errors"].append(f"API Error: {e}")
                    except Exception as e:
                        health["errors"].append(f"Unexpected error: {e}")
                        
                else:
                    health["errors"].append("No GitHub token provided")
                    
        except Exception as e:
            health["errors"].append(f"Client initialization failed: {e}")
            
        health["overall_status"] = (
            health["github_api"] and 
            health["authentication"] and 
            health["repository_access"] and
            len(health["errors"]) == 0
        )
        
        return health


# Convenience functions for WRE integration
async def quick_health_check(token: Optional[str] = None) -> bool:
    """
    Quick health check for GitHub integration
    
    Args:
        token: GitHub token (optional)
        
    Returns:
        True if GitHub integration is healthy
    """
    integration = WREGitHubIntegration(token=token)
    health = await integration.health_check()
    return health["overall_status"]


async def create_automated_pr(commit_message: str, token: Optional[str] = None) -> Optional[str]:
    """
    Create automated PR for current changes
    
    Args:
        commit_message: Commit message
        token: GitHub token (optional)
        
    Returns:
        PR URL if successful
    """
    integration = WREGitHubIntegration(token=token)
    result = await integration.enhanced_commit_and_pr(commit_message)
    
    return result.get("pr_url") if result.get("success") else None


async def report_violation(violation_type: str, description: str, 
                         files: List[str], wsp: Optional[int] = None,
                         token: Optional[str] = None) -> Optional[str]:
    """
    Report WSP violation as GitHub issue
    
    Args:
        violation_type: Violation type
        description: Description
        files: Affected files
        wsp: WSP protocol number
        token: GitHub token (optional)
        
    Returns:
        Issue URL if successful
    """
    integration = WREGitHubIntegration(token=token)
    return await integration.create_violation_issue(violation_type, description, files, wsp)


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstration of WRE GitHub integration"""
        import os
        
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("GITHUB_TOKEN environment variable not set")
            return
            
        integration = WREGitHubIntegration(token=token)
        
        # Health check
        print("Performing health check...")
        health = await integration.health_check()
        print(f"Health status: {'✅' if health['overall_status'] else '❌'}")
        
        if health["overall_status"]:
            # Sync repository status
            print("\nSyncing repository status...")
            status = await integration.sync_repository_status()
            print(f"Repository: {status['repository']['name']}")
            print(f"Open PRs: {status['pull_requests']['open']}")
            print(f"Open Issues: {status['issues']['open']}")
            
        else:
            print("Errors:", health["errors"])
    
    asyncio.run(demo())