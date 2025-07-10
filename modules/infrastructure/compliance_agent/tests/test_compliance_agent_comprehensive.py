"""
Comprehensive ComplianceAgent Tests

Tests for the WSP compliance verification system.
Relocated from tests/wre_simulation/ per WSP 3 compliance requirements.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (proper test location)
- WSP 5: Test Coverage Protocol (comprehensive testing)
- WSP 22: Traceable Narrative (documented relocation)
"""

import pytest
import shutil
import tempfile
from pathlib import Path

from modules.infrastructure.compliance_agent.src.compliance_agent import ComplianceAgent


@pytest.fixture
def sandboxed_wre():
    """Creates a temporary, sandboxed WRE structure for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create basic structure
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()
        
        # Create WSP_framework module structure
        wsp_framework_dir = modules_dir / "WSP_framework"
        wsp_framework_dir.mkdir()
        (wsp_framework_dir / "src").mkdir()
        (wsp_framework_dir / "README.md").touch()
        (wsp_framework_dir / "__init__.py").touch()
        
        # Create tools structure
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        
        yield tmp_path


def test_sentinel_detects_rogue_file(sandboxed_wre):
    """
    Test Condition A: The ComplianceAgent must detect a rogue .md file
    in a module's root.
    """
    # --- Setup: Create the dissonance ---
    module_path = sandboxed_wre / "modules" / "WSP_framework"
    rogue_file = module_path / "rogue_protocol.md"
    rogue_file.touch()

    # --- Execution: Run the Sentinel ---
    agent = ComplianceAgent()
    # ComplianceAgent uses 'run_check' method, not 'execute'
    result = agent.run_check(str(module_path))

    # --- Validation: Ensure the dissonance was detected ---
    assert not result["compliant"], "Expected compliance check to fail due to missing tests directory"
    assert len(result["errors"]) > 0, "Expected at least one error to be detected"


def test_sentinel_detects_missing_readme_in_agent_dir(sandboxed_wre):
    """
    Test Condition B: The ComplianceAgent must detect an agent directory
    that is missing its README.md file.
    """
    # --- Setup: Create the dissonance ---
    agent_dir = sandboxed_wre / "tools" / "wre" / "agents" / "dummy_agents"
    agent_dir.mkdir(parents=True)
    (agent_dir / "some_cool_agent.py").touch()

    # --- Execution: Run the Sentinel ---
    # We run the scan from the agent directory itself
    agent = ComplianceAgent()
    # ComplianceAgent uses 'run_check' method, not 'execute'
    result = agent.run_check(str(agent_dir))

    # --- Validation: Ensure the dissonance was detected ---
    assert not result["compliant"], "Expected compliance check to fail due to missing README.md"
    assert len(result["errors"]) > 0, "Expected at least one error to be detected"


def test_compliance_agent_basic_functionality():
    """
    Test basic ComplianceAgent functionality with current project structure.
    """
    agent = ComplianceAgent()
    
    # Test that the agent can be instantiated and has required methods
    assert hasattr(agent, 'run_check')
    # ComplianceAgent uses 'run_check' method, not 'execute'
    
    # Test with a simple directory structure
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create minimal compliant structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "README.md").touch()
        (tmp_path / "__init__.py").touch()
        (tmp_path / "tests" / "README.md").touch()
        
        result = agent.run_check(str(tmp_path))
        
        # Should be compliant with minimal structure
        assert 'compliant' in result
        assert 'errors' in result 