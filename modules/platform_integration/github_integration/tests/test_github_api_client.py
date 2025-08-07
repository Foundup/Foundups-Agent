"""
Tests for GitHub API Client
Comprehensive testing of all GitHub API client functionality with mocked responses.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from aioresponses import aioresponses

from modules.platform_integration.github_integration.src.github_api_client import (
    GitHubAPIClient,
    GitHubAPIError,
    GitHubRepository,
    PullRequest,
    Issue,
    PullRequestState,
    IssueState
)


@pytest.fixture
def github_client():
    """Create GitHub API client for testing"""
    return GitHubAPIClient(token="test_token", owner="TestOwner", repo="TestRepo")


@pytest.fixture
def mock_repository_response():
    """Mock repository API response"""
    return {
        "name": "TestRepo",
        "owner": {"login": "TestOwner"},
        "full_name": "TestOwner/TestRepo", 
        "description": "Test repository",
        "private": False,
        "default_branch": "main",
        "html_url": "https://github.com/TestOwner/TestRepo"
    }


@pytest.fixture
def mock_pull_request_response():
    """Mock pull request API response"""
    return {
        "number": 123,
        "title": "Test PR",
        "body": "Test PR body",
        "state": "open",
        "head": {"ref": "feature/test"},
        "base": {"ref": "main"},
        "user": {"login": "testuser"},
        "html_url": "https://github.com/TestOwner/TestRepo/pull/123",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_issue_response():
    """Mock issue API response"""
    return {
        "number": 456,
        "title": "Test Issue",
        "body": "Test issue body",
        "state": "open",
        "user": {"login": "testuser"},
        "labels": [{"name": "bug"}, {"name": "high-priority"}],
        "html_url": "https://github.com/TestOwner/TestRepo/issues/456",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


class TestGitHubAPIClientInit:
    """Test GitHub API client initialization"""
    
    def test_init_with_token(self):
        client = GitHubAPIClient(token="test_token", owner="TestOwner", repo="TestRepo")
        assert client.token == "test_token"
        assert client.owner == "TestOwner"
        assert client.repo == "TestRepo"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "token test_token"
    
    def test_init_without_token(self):
        with patch.dict('os.environ', {}, clear=True):
            client = GitHubAPIClient(owner="TestOwner", repo="TestRepo")
            assert client.token is None
            assert "Authorization" not in client.headers
    
    def test_init_with_env_token(self):
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'env_token'}):
            client = GitHubAPIClient(owner="TestOwner", repo="TestRepo")
            assert client.token == "env_token"


class TestGitHubAPIClientRepositoryOperations:
    """Test repository operations"""
    
    @pytest.mark.asyncio
    async def test_get_repository_success(self, github_client, mock_repository_response):
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo',
                payload=mock_repository_response
            )
            
            async with github_client as client:
                repo = await client.get_repository()
                
            assert isinstance(repo, GitHubRepository)
            assert repo.name == "TestRepo"
            assert repo.owner == "TestOwner"
            assert repo.full_name == "TestOwner/TestRepo"
            assert repo.description == "Test repository"
            assert repo.private is False
            assert repo.default_branch == "main"
    
    @pytest.mark.asyncio
    async def test_get_repository_api_error(self, github_client):
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo',
                status=404,
                payload={"message": "Not Found"}
            )
            
            async with github_client as client:
                with pytest.raises(GitHubAPIError, match="GitHub API error: Not Found"):
                    await client.get_repository()
    
    @pytest.mark.asyncio
    async def test_get_branches_success(self, github_client):
        branches_response = [
            {"name": "main"},
            {"name": "develop"},
            {"name": "feature/test"}
        ]
        
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo/branches',
                payload=branches_response
            )
            
            async with github_client as client:
                branches = await client.get_branches()
                
            assert branches == ["main", "develop", "feature/test"]
    
    @pytest.mark.asyncio
    async def test_create_branch_success(self, github_client):
        # Mock getting source branch SHA
        source_ref_response = {
            "object": {"sha": "abc123"}
        }
        
        # Mock creating new branch
        create_ref_response = {
            "ref": "refs/heads/feature/new-feature",
            "object": {"sha": "abc123"}
        }
        
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo/git/refs/heads/main',
                payload=source_ref_response
            )
            m.post(
                'https://api.github.com/repos/TestOwner/TestRepo/git/refs',
                payload=create_ref_response
            )
            
            async with github_client as client:
                result = await client.create_branch("feature/new-feature")
                
            assert result is True


class TestGitHubAPIClientPullRequestOperations:
    """Test pull request operations"""
    
    @pytest.mark.asyncio
    async def test_create_pull_request_success(self, github_client, mock_pull_request_response):
        with aioresponses() as m:
            m.post(
                'https://api.github.com/repos/TestOwner/TestRepo/pulls',
                payload=mock_pull_request_response
            )
            
            async with github_client as client:
                pr = await client.create_pull_request(
                    title="Test PR",
                    body="Test PR body",
                    head_branch="feature/test"
                )
                
            assert isinstance(pr, PullRequest)
            assert pr.number == 123
            assert pr.title == "Test PR"
            assert pr.body == "Test PR body"
            assert pr.state == PullRequestState.OPEN
            assert pr.head_branch == "feature/test"
            assert pr.base_branch == "main"
    
    @pytest.mark.asyncio
    async def test_get_pull_requests_success(self, github_client, mock_pull_request_response):
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo/pulls?state=open',
                payload=[mock_pull_request_response]
            )
            
            async with github_client as client:
                prs = await client.get_pull_requests()
                
            assert len(prs) == 1
            assert isinstance(prs[0], PullRequest)
            assert prs[0].number == 123
    
    @pytest.mark.asyncio
    async def test_merge_pull_request_success(self, github_client):
        merge_response = {
            "sha": "merged_sha",
            "merged": True,
            "message": "Pull Request successfully merged"
        }
        
        with aioresponses() as m:
            m.put(
                'https://api.github.com/repos/TestOwner/TestRepo/pulls/123/merge',
                payload=merge_response
            )
            
            async with github_client as client:
                result = await client.merge_pull_request(123)
                
            assert result is True


class TestGitHubAPIClientIssueOperations:
    """Test issue operations"""
    
    @pytest.mark.asyncio
    async def test_create_issue_success(self, github_client, mock_issue_response):
        with aioresponses() as m:
            m.post(
                'https://api.github.com/repos/TestOwner/TestRepo/issues',
                payload=mock_issue_response
            )
            
            async with github_client as client:
                issue = await client.create_issue(
                    title="Test Issue",
                    body="Test issue body",
                    labels=["bug", "high-priority"]
                )
                
            assert isinstance(issue, Issue)
            assert issue.number == 456
            assert issue.title == "Test Issue"
            assert issue.body == "Test issue body"
            assert issue.state == IssueState.OPEN
            assert issue.labels == ["bug", "high-priority"]
    
    @pytest.mark.asyncio
    async def test_get_issues_success(self, github_client, mock_issue_response):
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo/issues?state=open',
                payload=[mock_issue_response]
            )
            
            async with github_client as client:
                issues = await client.get_issues()
                
            assert len(issues) == 1
            assert isinstance(issues[0], Issue)
            assert issues[0].number == 456
    
    @pytest.mark.asyncio
    async def test_close_issue_success(self, github_client):
        close_response = {
            "state": "closed"
        }
        
        with aioresponses() as m:
            m.patch(
                'https://api.github.com/repos/TestOwner/TestRepo/issues/456',
                payload=close_response
            )
            
            async with github_client as client:
                result = await client.close_issue(456)
                
            assert result is True


class TestGitHubAPIClientFileOperations:
    """Test file operations"""
    
    @pytest.mark.asyncio
    async def test_get_file_content_success(self, github_client):
        import base64
        
        file_content = "# Test File\nThis is a test file."
        encoded_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
        
        file_response = {
            "content": encoded_content,
            "sha": "file_sha_123"
        }
        
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo/contents/test.md?ref=main',
                payload=file_response
            )
            
            async with github_client as client:
                content, sha = await client.get_file_content("test.md")
                
            assert content == file_content
            assert sha == "file_sha_123"
    
    @pytest.mark.asyncio
    async def test_create_or_update_file_success(self, github_client):
        file_response = {
            "commit": {
                "sha": "commit_sha_123"
            }
        }
        
        with aioresponses() as m:
            m.put(
                'https://api.github.com/repos/TestOwner/TestRepo/contents/test.md',
                payload=file_response
            )
            
            async with github_client as client:
                result = await client.create_or_update_file(
                    file_path="test.md",
                    content="# Updated Test File",
                    commit_message="Update test file"
                )
                
            assert result is True


class TestGitHubAPIClientWorkflowOperations:
    """Test workflow operations"""
    
    @pytest.mark.asyncio
    async def test_get_workflows_success(self, github_client):
        workflows_response = {
            "workflows": [
                {
                    "id": 123,
                    "name": "CI",
                    "path": ".github/workflows/ci.yml"
                }
            ]
        }
        
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/TestOwner/TestRepo/actions/workflows',
                payload=workflows_response
            )
            
            async with github_client as client:
                workflows = await client.get_workflows()
                
            assert len(workflows) == 1
            assert workflows[0]["name"] == "CI"
    
    @pytest.mark.asyncio
    async def test_trigger_workflow_success(self, github_client):
        with aioresponses() as m:
            m.post(
                'https://api.github.com/repos/TestOwner/TestRepo/actions/workflows/ci.yml/dispatches',
                status=204
            )
            
            async with github_client as client:
                result = await client.trigger_workflow("ci.yml", ref="main")
                
            assert result is True


class TestGitHubAPIClientUtilityMethods:
    """Test utility methods"""
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, github_client):
        rate_limit_response = {
            "resources": {
                "core": {
                    "limit": 5000,
                    "remaining": 4999,
                    "reset": 1640995200
                }
            }
        }
        
        with aioresponses() as m:
            m.get(
                'https://api.github.com/rate_limit',
                payload=rate_limit_response
            )
            
            async with github_client as client:
                rate_limit = await client.check_rate_limit()
                
            assert rate_limit["resources"]["core"]["limit"] == 5000
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, github_client):
        user_response = {
            "login": "testuser",
            "id": 123,
            "name": "Test User"
        }
        
        with aioresponses() as m:
            m.get(
                'https://api.github.com/user',
                payload=user_response
            )
            
            async with github_client as client:
                user = await client.get_user()
                
            assert user["login"] == "testuser"
    
    def test_is_authenticated_with_token(self):
        client = GitHubAPIClient(token="test_token")
        assert client.is_authenticated() is True
    
    def test_is_authenticated_without_token(self):
        client = GitHubAPIClient(token=None)
        assert client.is_authenticated() is False


class TestGitHubAPIClientErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_request_without_session(self, github_client):
        with pytest.raises(GitHubAPIError, match="Client not initialized"):
            await github_client._make_request("GET", "repos/test/test")
    
    @pytest.mark.asyncio
    async def test_unsupported_http_method(self, github_client):
        with aioresponses():
            async with github_client as client:
                with pytest.raises(GitHubAPIError, match="Unsupported HTTP method"):
                    await client._make_request("PATCH", "repos/test/test")
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, github_client):
        with aioresponses() as m:
            m.get('https://api.github.com/repos/TestOwner/TestRepo', exception=Exception("Network error"))
            
            async with github_client as client:
                with pytest.raises(GitHubAPIError, match="Request failed"):
                    await client.get_repository()


class TestGitHubAPIClientContextManager:
    """Test async context manager"""
    
    @pytest.mark.asyncio
    async def test_context_manager_creates_session(self, github_client):
        assert github_client.session is None
        
        async with github_client as client:
            assert client.session is not None
            
        assert github_client.session is None or github_client.session.closed
    
    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self, github_client):
        async with github_client as client:
            session = client.session
            assert not session.closed
            
        assert session.closed