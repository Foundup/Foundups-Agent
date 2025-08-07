# GitHub Integration Testing Strategy

## Testing Overview

This directory contains comprehensive tests for the GitHub Integration module, covering both unit tests and integration tests with the actual GitHub API.

## Test Structure

### **Unit Tests**
- `test_github_api_client.py` - Core API client functionality
- `test_github_automation.py` - Automation workflow testing
- `test_data_structures.py` - Data structure validation
- `test_error_handling.py` - Error handling and edge cases

### **Integration Tests**
- `test_integration.py` - Real GitHub API integration tests (requires token)
- `test_workflows.py` - GitHub Actions workflow testing
- `test_repository_operations.py` - Live repository operation tests

### **Mock Tests**
- `test_mocked_api.py` - Mocked API responses for reliable unit testing
- `test_rate_limiting.py` - Rate limiting and throttling tests

## Testing Strategy

### **Unit Testing Approach**
- Mock all external GitHub API calls using `aioresponses`
- Test all public methods with various input scenarios
- Validate data structure serialization/deserialization
- Test error handling for API failures and network issues
- Verify async/await patterns and context manager usage

### **Integration Testing Approach**
- Test against real GitHub API using test repository
- Validate end-to-end workflows including PR creation and merging
- Test authentication and authorization flows
- Verify rate limiting and throttling behavior
- Test GitHub Actions workflow triggering

### **Mocking Patterns**
```python
# Example mocking pattern for GitHub API responses
@pytest.fixture
def mock_github_api():
    with aioresponses() as m:
        # Mock repository info
        m.get(
            'https://api.github.com/repos/Foundup/Foundups-Agent',
            payload={
                'name': 'Foundups-Agent',
                'owner': {'login': 'Foundup'},
                'default_branch': 'main',
                # ... more repo data
            }
        )
        yield m
```

## Test Data Management

### **Mock Data**
- Repository information fixtures
- Pull request response fixtures  
- Issue response fixtures
- Workflow run response fixtures
- Error response fixtures

### **Test Configuration**
```python
# Test configuration
TEST_REPO_OWNER = "Foundup"
TEST_REPO_NAME = "Foundups-Agent"
TEST_TOKEN = "test_token_123"  # For unit tests only
```

## Running Tests

### **Unit Tests Only** (No GitHub API calls)
```bash
pytest tests/test_github_api_client.py tests/test_github_automation.py -v
```

### **Integration Tests** (Requires GitHub token)
```bash
GITHUB_TOKEN=your_test_token pytest tests/test_integration.py -v
```

### **All Tests with Coverage**
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
```

### **Specific Test Categories**
```bash
# Mock tests only
pytest tests/test_mocked_api.py -v

# Error handling tests
pytest tests/test_error_handling.py -v

# Automation workflow tests
pytest tests/test_github_automation.py -v
```

## Test Environment Setup

### **GitHub Test Repository**
For integration tests, you'll need:
- A GitHub personal access token with repo access
- A test repository (can be private)
- Proper permissions for creating branches, PRs, and issues

### **Environment Variables**
```bash
export GITHUB_TOKEN=your_test_token
export TEST_GITHUB_OWNER=your_test_org
export TEST_GITHUB_REPO=your_test_repo
```

## Coverage Requirements

- **Minimum Coverage**: 90%
- **Critical Paths**: 100% coverage for authentication, API calls, and error handling
- **Integration Tests**: Cover all major workflow scenarios
- **Edge Cases**: Network failures, rate limiting, authentication errors

## Test Data Fixtures

### **Repository Fixtures**
```python
@pytest.fixture
def sample_repository():
    return GitHubRepository(
        owner="Foundup",
        name="Foundups-Agent",
        full_name="Foundup/Foundups-Agent",
        description="FoundUps Agent Repository",
        private=False,
        default_branch="main",
        url="https://github.com/Foundup/Foundups-Agent"
    )
```

### **Pull Request Fixtures**
```python
@pytest.fixture  
def sample_pull_request():
    return PullRequest(
        number=123,
        title="Test PR",
        body="Test PR body",
        state=PullRequestState.OPEN,
        head_branch="feature/test",
        base_branch="main",
        author="testuser",
        url="https://github.com/Foundup/Foundups-Agent/pull/123",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
```

## Continuous Integration

### **GitHub Actions Integration**
The tests are designed to run in GitHub Actions with:
- Matrix testing across Python versions
- Separate jobs for unit tests vs integration tests
- Test result reporting and coverage upload
- Automatic test execution on PR creation

### **Test Matrix**
- Python 3.8, 3.9, 3.10, 3.11
- Different OS environments (Ubuntu, Windows, macOS)
- Mock tests vs integration tests
- Performance benchmarking tests

## Performance Testing

### **Benchmarks**
- API response time measurements
- Bulk operation performance (100+ items)
- Concurrent request handling
- Memory usage during large operations
- Rate limit compliance testing

### **Load Testing**
```python
@pytest.mark.performance
async def test_bulk_pr_creation_performance():
    # Test creating multiple PRs concurrently
    # Measure response times and resource usage
    pass
```

## Security Testing

### **Authentication Tests**
- Token validation and error handling
- Unauthorized access scenarios
- Token expiration handling
- Rate limit response handling

### **Input Validation Tests**
- SQL injection attempts in PR/issue content
- XSS prevention in markdown content
- Path traversal prevention in file operations
- Input sanitization verification

---

**Testing Strategy**: Comprehensive unit and integration testing with mocking  
**Coverage Target**: 90%+ with 100% critical path coverage  
**CI Integration**: GitHub Actions with matrix testing  
**Security Focus**: Authentication, input validation, and API security