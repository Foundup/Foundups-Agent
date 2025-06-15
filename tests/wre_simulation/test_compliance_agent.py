import pytest
import shutil
import tempfile
from pathlib import Path

# This is a bit of a hack to make sure we can import from the project root
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.wre.agents.compliance_agent import ComplianceAgent

@pytest.fixture
def sandboxed_wre():
    """Creates a temporary, sandboxed WRE structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a dummy module structure
        module_path = root / "modules" / "WSP_framework"
        module_path.mkdir(parents=True, exist_ok=True)
        (module_path / "src").mkdir()
        (module_path / "tests").mkdir()
        (module_path / "__init__.py").touch()
        (module_path / "README.md").touch()
        
        # Create a dummy agent directory structure
        agent_dir_path = root / "tools" / "wre" / "agents" / "dummy_agents"
        agent_dir_path.mkdir(parents=True, exist_ok=True)

        yield root

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
    task_payload = {'path': str(module_path)}
    result = agent.execute(task_payload)

    # --- Assertion: The Sentinel must see the failure ---
    assert result['status'] == 'SUCCESS'
    assert len(result['findings']) == 1
    assert "rogue_protocol.md" in result['findings'][0]

def test_sentinel_detects_missing_readme_in_agent_dir(sandboxed_wre):
    """
    Test Condition B: The ComplianceAgent must detect an agent directory
    that is missing its README.md file.
    """
    # --- Setup: Create the dissonance ---
    agent_dir = sandboxed_wre / "tools" / "wre" / "agents" / "dummy_agents"
    (agent_dir / "some_cool_agent.py").touch()
    
    # --- Execution: Run the Sentinel ---
    # We run the scan from the root of the tools dir to test recursion
    scan_path = sandboxed_wre / "tools"
    agent = ComplianceAgent()
    task_payload = {'path': str(scan_path)}
    result = agent.execute(task_payload)
    
    # --- Assertion: The Sentinel must see the failure ---
    assert result['status'] == 'SUCCESS'
    assert len(result['findings']) == 1
    assert str(agent_dir) in result['findings'][0]
    assert "missing a README.md" in result['findings'][0] 