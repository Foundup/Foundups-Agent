import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.wre.agents.loremaster_agent import LoremasterAgent

@pytest.fixture
def sandboxed_wsp_env():
    """Creates a temporary, sandboxed WSP structure with intentional errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        wsp_framework_path = root / "WSP_framework" / "src"
        wsp_framework_path.mkdir(parents=True, exist_ok=True)

        # --- Create Dissonance ---
        # 1. A valid protocol
        (wsp_framework_path / "WSP_40_valid.md").write_text("# WSP 40: A Valid Protocol")
        
        # 2. Another valid protocol to test sorting and gaps
        (wsp_framework_path / "WSP_50_valid.md").write_text("# WSP 50: Another Valid Protocol (AVP)")

        # 3. A protocol with a duplicate number
        (wsp_framework_path / "WSP_40_duplicate.md").write_text("# WSP 40: A Duplicate Protocol")

        # 4. A protocol with a malformed header
        (wsp_framework_path / "WSP_malformed.md").write_text("This is not a valid WSP file.")

        yield root

def test_loremaster_agent_audits_and_generates_manifest(sandboxed_wsp_env):
    """
    Tests that the LoremasterAgent correctly identifies semantic dissonance
    and generates a manifest containing only the valid protocols.
    """
    # --- Setup ---
    scan_path = sandboxed_wsp_env / "WSP_framework"
    manifest_path = sandboxed_wsp_env / "WSP_framework" / "src" / "WSP_MANIFEST.md"
    
    agent = LoremasterAgent()
    payload = {
        'scan_paths': [str(scan_path)],
        'manifest_path': str(manifest_path)
    }

    # --- Execution ---
    result = agent.execute(payload)

    # --- Assertion: Agent Report ---
    assert result['status'] == 'SUCCESS'
    assert result['protocols_found'] == 3 # Should find the 3 that look like protocols
    
    findings = result['findings']
    assert len(findings) == 3 # Duplicate, Malformed, and Gap
    
    assert any("CRITICAL: Duplicate WSP number found: 40" in f for f in findings)
    assert any("CRITICAL: Malformed header" in f and "WSP_malformed.md" in f for f in findings)
    assert any("WARNING: Large gap detected" in f and "between 40 and 50" in f for f in findings)
    
    # --- Assertion: Manifest Content ---
    assert manifest_path.exists()
    manifest_content = manifest_path.read_text()
    
    # Manifest should contain WSP 50, but NOT the ambiguous WSP 40s
    assert "Another Valid Protocol" in manifest_content
    assert "A Valid Protocol" not in manifest_content
    assert "A Duplicate Protocol" not in manifest_content
    assert "WSP_malformed.md" not in manifest_content 