"""
Tests for Move2Japan Command Handler (WSP 34)
===============================================

Covers: trigger detection, urgency classification, passport classification,
intent bucket redirect, emotional tone handling, routing matrix, state machine,
BC0 re-engagement.
"""

import os
import tempfile
import pytest

from modules.communication.livechat.src.m2j_handler import Move2JapanHandler
from modules.foundups.move2japan.src.m2j_stakeholder_db import M2JStakeholderDB


@pytest.fixture
def handler():
    """Create handler with a temp DB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_stakeholders.db")
        h = Move2JapanHandler()
        h.db = M2JStakeholderDB(db_path=db_path)
        yield h


class TestTriggerDetection:
    """Test that _check_m2j_command detects the right triggers."""

    def test_move2japan_trigger(self):
        from modules.communication.livechat.src.message_processor import MessageProcessor
        mp = MessageProcessor.__new__(MessageProcessor)
        assert mp._check_m2j_command("!move2japan") is True

    def test_m2j_trigger(self):
        mp = MessageProcessor.__new__(MessageProcessor)
        assert mp._check_m2j_command("!m2j") is True

    def test_japan_trigger(self):
        mp = MessageProcessor.__new__(MessageProcessor)
        assert mp._check_m2j_command("!japan") is True

    def test_m2j_with_args(self):
        mp = MessageProcessor.__new__(MessageProcessor)
        assert mp._check_m2j_command("!m2j 3") is True

    def test_no_trigger(self):
        mp = MessageProcessor.__new__(MessageProcessor)
        assert mp._check_m2j_command("hello world") is False

    def test_shorts_not_m2j(self):
        mp = MessageProcessor.__new__(MessageProcessor)
        assert mp._check_m2j_command("!createshort topic") is False


# Need to re-import since the class reference above was in a test-only scope
from modules.communication.livechat.src.message_processor import MessageProcessor


class TestUrgencyClassification:

    def test_parse_urgency_1(self, handler):
        assert handler._parse_urgency("1") == "1"

    def test_parse_urgency_5(self, handler):
        assert handler._parse_urgency("5") == "5"

    def test_parse_urgency_from_command(self, handler):
        assert handler._parse_urgency("!m2j 3") == "3"

    def test_parse_urgency_no_match(self, handler):
        assert handler._parse_urgency("hello") is None

    def test_parse_urgency_out_of_range(self, handler):
        assert handler._parse_urgency("9") is None


class TestPassportClassification:

    def test_yes(self, handler):
        assert handler._parse_passport("yes") == "yes"

    def test_yeah(self, handler):
        assert handler._parse_passport("yeah I do") == "yes"

    def test_no(self, handler):
        assert handler._parse_passport("no") == "no"

    def test_nope(self, handler):
        assert handler._parse_passport("nope") == "no"

    def test_expired(self, handler):
        assert handler._parse_passport("mine expired") == "expired"

    def test_in_progress(self, handler):
        assert handler._parse_passport("I'm applying now") == "in_progress"

    def test_ambiguous(self, handler):
        assert handler._parse_passport("maybe idk") is None


class TestIntentBucketDetection:

    def test_jobs(self, handler):
        assert handler._classify_intent_bucket("how do I get a job in Japan") == "jobs"

    def test_visa(self, handler):
        assert handler._classify_intent_bucket("what visa do I need") == "visa"

    def test_housing(self, handler):
        assert handler._classify_intent_bucket("how expensive is rent") == "housing"

    def test_cost(self, handler):
        assert handler._classify_intent_bucket("is it expensive to live there") == "cost"

    def test_no_bucket(self, handler):
        assert handler._classify_intent_bucket("!move2japan") is None


class TestEmotionalToneHandling:

    def test_emotional_detected(self, handler):
        assert handler._is_emotional("I need to get out of here I'm scared") is True

    def test_normal_not_emotional(self, handler):
        assert handler._is_emotional("!move2japan 3") is False


class TestBC0StateMachine:

    def test_initial_welcome(self, handler):
        response = handler.handle_command("!move2japan", "TestUser", "UC_001", "USER")
        assert response is not None
        assert "@TestUser" in response
        assert "1️⃣" in response or "exploring" in response.lower()

    def test_urgency_then_passport(self, handler):
        # Step 1: Trigger
        handler.handle_command("!move2japan", "TestUser", "UC_002", "USER")
        # Step 2: Pick urgency
        response = handler.handle_command("!m2j 3", "TestUser", "UC_002", "USER")
        assert response is not None
        assert "passport" in response.lower()

    def test_full_flow_yes_passport(self, handler):
        handler.handle_command("!move2japan", "TestUser", "UC_003", "USER")
        handler.handle_command("!m2j 3", "TestUser", "UC_003", "USER")
        response = handler.handle_command("!m2j yes", "TestUser", "UC_003", "USER")
        assert response is not None
        # Should get the "yes_passport" route
        assert "gate" in response.lower() or "foundups.com" in response.lower() or "path" in response.lower()

    def test_full_flow_no_passport(self, handler):
        handler.handle_command("!move2japan", "TestUser", "UC_004", "USER")
        handler.handle_command("!m2j 2", "TestUser", "UC_004", "USER")
        response = handler.handle_command("!m2j no", "TestUser", "UC_004", "USER")
        assert response is not None
        # Should get the "no_passport" route
        assert "passport" in response.lower()

    def test_re_engagement(self, handler):
        # Complete the flow first
        handler.handle_command("!move2japan", "TestUser", "UC_005", "USER")
        handler.handle_command("!m2j 4", "TestUser", "UC_005", "USER")
        handler.handle_command("!m2j yes", "TestUser", "UC_005", "USER")
        # Re-engage
        response = handler.handle_command("!move2japan", "TestUser", "UC_005", "USER")
        assert response is not None
        assert "Welcome back" in response


class TestRoutingMatrix:

    def test_exploring_no_route(self, handler):
        handler.handle_command("!move2japan", "TestUser", "UC_R1", "USER")
        handler.handle_command("!m2j 1", "TestUser", "UC_R1", "USER")
        response = handler.handle_command("!m2j no", "TestUser", "UC_R1", "USER")
        assert "passport" in response.lower()

    def test_urgent_yes_route(self, handler):
        handler.handle_command("!move2japan", "TestUser", "UC_R2", "USER")
        handler.handle_command("!m2j 5", "TestUser", "UC_R2", "USER")
        response = handler.handle_command("!m2j yes", "TestUser", "UC_R2", "USER")
        # Urgent + passport should get fast-track
        assert "gate" in response.lower() or "roadmap" in response.lower() or "foundups" in response.lower()


class TestInfoCommands:

    def test_status_command(self, handler):
        handler.handle_command("!move2japan", "TestUser", "UC_I1", "USER")
        handler.handle_command("!m2j 3", "TestUser", "UC_I1", "USER")
        response = handler.handle_info_command("!m2j status", "TestUser", "UC_I1")
        assert response is not None
        assert "serious" in response.lower() or "stage" in response.lower()

    def test_reset_command(self, handler):
        handler.handle_command("!move2japan", "TestUser", "UC_I2", "USER")
        response = handler.handle_info_command("!m2j reset", "TestUser", "UC_I2")
        assert response is not None
        assert "reset" in response.lower()


class TestStakeholderPersistence:

    def test_write_and_read_back(self, handler):
        handler.handle_command("!move2japan", "PersistUser", "UC_P1", "USER")
        handler.handle_command("!m2j 4", "PersistUser", "UC_P1", "USER")
        # Check DB directly
        record = handler.db.get_stakeholder("UC_P1")
        assert record is not None
        assert record["urgency_level"] == "imminent"
        assert record["bc0_state"] == "BC0.4"
