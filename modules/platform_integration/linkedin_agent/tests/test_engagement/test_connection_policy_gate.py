"""
LinkedIn Connection Policy Gate Tests

Validates outbound connection restrictions:
- Allow: CxO/founder/architect/blockchain roles
- Deny: business development/marketing/recruiting roles
- Deny: employee-level roles when no allow signal
"""

import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

from modules.platform_integration.linkedin_agent.src.engagement.connection_manager import (  # noqa: E402
    ConnectionStatus,
    LinkedInConnectionManager,
    LinkedInProfile,
)


class TestLinkedInConnectionPolicyGate(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = LinkedInConnectionManager(max_daily_requests=50)

    def _profile(self, headline: str) -> LinkedInProfile:
        return LinkedInProfile(
            profile_id="p1",
            first_name="Test",
            last_name="User",
            headline=headline,
            company="Example Co",
            industry="Technology",
        )

    def test_allows_founder(self):
        profile = self._profile("Founder @ Example Ventures")
        result = self.manager.send_connection_request("p1", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.PENDING)

    def test_allows_cxo(self):
        profile = self._profile("CTO | AI Systems")
        result = self.manager.send_connection_request("p2", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.PENDING)

    def test_allows_architect(self):
        profile = self._profile("Enterprise Architect")
        result = self.manager.send_connection_request("p3", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.PENDING)

    def test_allows_blockchain(self):
        profile = self._profile("Blockchain Engineer")
        result = self.manager.send_connection_request("p4", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.PENDING)

    def test_blocks_business_development(self):
        profile = self._profile("Business Development Director")
        result = self.manager.send_connection_request("p5", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.BLOCKED)

    def test_blocks_marketing(self):
        profile = self._profile("Growth Marketing Lead")
        result = self.manager.send_connection_request("p6", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.BLOCKED)

    def test_blocks_recruiting(self):
        profile = self._profile("Senior Recruiter")
        result = self.manager.send_connection_request("p7", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.BLOCKED)

    def test_blocks_employee_level_when_no_allow(self):
        profile = self._profile("Software Engineer")
        result = self.manager.send_connection_request("p8", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.BLOCKED)

    def test_hard_deny_overrides_allow(self):
        profile = self._profile("Founder and Marketing Advisor")
        result = self.manager.send_connection_request("p9", target_profile=profile)
        self.assertEqual(result.status, ConnectionStatus.BLOCKED)

    def test_blocks_when_profile_metadata_missing(self):
        result = self.manager.send_connection_request("p10")
        self.assertEqual(result.status, ConnectionStatus.BLOCKED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
