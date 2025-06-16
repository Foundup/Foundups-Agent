import unittest
from pathlib import Path
from modules.infrastructure.agents.compliance_agent.src.compliance_agent import ComplianceAgent

class TestComplianceAgent(unittest.TestCase):

    def setUp(self):
        self.agent = ComplianceAgent()
        # The test runner's CWD is the project root.
        self.project_root = Path.cwd() 
        self.janitor_agent_path = self.project_root / "modules" / "infrastructure" / "agents" / "janitor_agent"

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

if __name__ == '__main__':
    unittest.main() 