"""
ComplianceAgent Tests

Main test suite for the WSP compliance verification system.
Updated to include comprehensive testing capabilities.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (proper test location)
- WSP 5: Test Coverage Protocol (comprehensive testing)
- WSP 22: Traceable Narrative (test organization)
"""

import unittest
import pytest
from pathlib import Path
from modules.infrastructure.compliance_agent.src.compliance_agent import ComplianceAgent


class TestComplianceAgent(unittest.TestCase):
    """
    Basic ComplianceAgent tests using unittest framework.
    For comprehensive tests, see test_compliance_agent_comprehensive.py
    """

    def setUp(self):
        self.agent = ComplianceAgent()
        # The test runner's CWD is the project root.
        self.project_root = Path.cwd() 
        self.janitor_agent_path = self.project_root / "modules" / "infrastructure" / "janitor_agent"

    def test_janitor_agent_is_now_compliant(self):
        """
        Tests that the janitor_agent module is now fully compliant
        after adding its corresponding test file.
        """
        print(f"\n--- Verifying final compliance of: {self.janitor_agent_path} ---")
        result = self.agent.run_check(str(self.janitor_agent_path))
        
        # We now expect the janitor agent to be compliant
        self.assertTrue(result["compliant"], f"Expected JanitorAgent to be compliant, but got errors: {result['errors']}")
        
        print("--- JanitorAgent is now WSP Compliant ---")

    def test_compliance_agent_instantiation(self):
        """Test that ComplianceAgent can be instantiated properly."""
        agent = ComplianceAgent()
        self.assertIsNotNone(agent)
        self.assertTrue(hasattr(agent, 'run_check'))
        # ComplianceAgent uses 'run_check' method, not 'execute'


def test_compliance_agent_pytest_integration():
    """
    Pytest-style integration test for ComplianceAgent.
    Bridges unittest and pytest frameworks.
    """
    agent = ComplianceAgent()
    
    # Test basic functionality
    assert agent is not None
    assert hasattr(agent, 'run_check')
    # ComplianceAgent uses 'run_check' method, not 'execute'
    
    # Test with project structure
    project_root = Path.cwd()
    if (project_root / "modules" / "infrastructure" / "janitor_agent").exists():
        result = agent.run_check(str(project_root / "modules" / "infrastructure" / "janitor_agent"))
        assert 'compliant' in result
        assert 'errors' in result


if __name__ == '__main__':
    unittest.main() 