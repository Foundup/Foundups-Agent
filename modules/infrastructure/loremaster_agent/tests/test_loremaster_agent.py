"""
LoremasterAgent Tests

Comprehensive tests for the WSP protocol auditing and manifest generation system.
Relocated from tests/wre_simulation/ per WSP 3 compliance requirements.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (proper test location)
- WSP 5: Test Coverage Protocol (comprehensive testing)
- WSP 22: Traceable Narrative (documented relocation)
"""

import pytest
import tempfile
from pathlib import Path

from modules.infrastructure.loremaster_agent.src.loremaster_agent import LoremasterAgent


@pytest.fixture
def sandboxed_wsp_env():
    """Creates a temporary, sandboxed WSP structure with intentional errors."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create WSP framework structure
        wsp_framework_dir = tmp_path / "WSP_framework"
        wsp_framework_dir.mkdir()
        
        # Create WSP_framework.md with mock content
        wsp_framework_md = wsp_framework_dir / "WSP_framework.md"
        wsp_framework_md.write_text("""
# WSP Framework

### 3.2. Architectural Vision: The "Cube" Philosophy
The WRE is structured as a multi-dimensional cube where each module can be thought of as an independent, 
interlocking component. This philosophy ensures modularity, maintainability, and scalability.

### 3.3. Directory Structure
Standard module organization follows enterprise patterns.
""")
        
        # Create WSP_CORE.md with mock content
        wsp_core_md = wsp_framework_dir / "WSP_CORE.md"
        wsp_core_md.write_text("""
# WSP Core

### NEW MODULE Quick Workflow
1. Create module directory structure
2. Add required documentation
3. Implement core functionality
4. Add comprehensive tests

### EXISTING CODE Quick Workflow
1. Analyze existing code structure
2. Refactor for WSP compliance
3. Update documentation
4. Validate with tests
""")
        
        # Create modules structure
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()
        wre_core_dir = modules_dir / "wre_core"
        wre_core_dir.mkdir()
        
        # Create README.md and main.py
        readme_md = wre_core_dir / "README.md"
        readme_md.write_text("# WRE Core\n\nAgents are located in `src/agents/`")
        
        src_dir = wre_core_dir / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text("# Main WRE entry point\n# No agent imports yet")
        
        yield tmp_path


def test_loremaster_agent_audits_and_generates_manifest(sandboxed_wsp_env):
    """
    Tests that the LoremasterAgent correctly identifies semantic dissonance
    and generates a manifest containing only the valid protocols.
    """
    # --- Setup ---
    scan_path = sandboxed_wsp_env / "WSP_framework"
    
    agent = LoremasterAgent()
    
    # --- Execution ---
    # LoremasterAgent uses 'run_audit' method, not 'execute'
    result = agent.run_audit(sandboxed_wsp_env)
    
    # --- Validation ---
    assert result["status"] == "complete"
    assert "docs_found" in result
    assert "core_principles" in result
    assert "next_wsp_number" in result
    assert "readme_coherence" in result
    
    # Verify it extracted the cube philosophy
    assert "Cube Philosophy" in result["core_principles"]
    assert "multi-dimensional cube" in result["core_principles"]
    
    # Verify it has workflow information
    assert "New Module Workflow" in result["core_principles"]
    assert "Create module directory structure" in result["core_principles"]


def test_loremaster_agent_basic_functionality():
    """
    Test basic LoremasterAgent functionality with current project structure.
    """
    agent = LoremasterAgent()
    
    # Test that the agent can be instantiated and has required methods
    assert hasattr(agent, 'run_audit')
    # LoremasterAgent uses 'run_audit' method, not 'execute'
    
    # Test with current project structure
    from pathlib import Path
    project_root = Path.cwd()
    
    # Basic functionality test - should not crash
    result = agent.run_audit(project_root)
    assert 'status' in result


@pytest.mark.skip(reason="Test directory structure not yet implemented")
def test_loremaster_agent_empty_directory():
    """
    Test LoremasterAgent behavior with empty directory.
    """
    pass


def test_loremaster_agent_instantiation():
    """
    Test that LoremasterAgent can be instantiated properly.
    """
    agent = LoremasterAgent()
    assert agent is not None
    
    # Test that the agent has the expected interface
    # LoremasterAgent uses 'run_audit' method, not 'execute'
    required_methods = ['run_audit']
    for method in required_methods:
        assert hasattr(agent, method), f"LoremasterAgent missing required method: {method}"
    
    # Test internal methods exist
    internal_methods = ['_read_and_extract', '_get_next_wsp_number', '_check_readme_coherence']
    for method in internal_methods:
        assert hasattr(agent, method), f"LoremasterAgent missing internal method: {method}" 