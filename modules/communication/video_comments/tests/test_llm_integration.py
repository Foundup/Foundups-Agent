#!/usr/bin/env python3
"""
WSP-Compliant Test Suite for LLM Comment Integration
Following WSP FMAS (Fail, Mock, Assert, Success) testing protocol
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import logging

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.communication.video_comments.src.llm_comment_generator import LLMCommentGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLLMIntegration(unittest.TestCase):
    """Test LLM integration doesn't break existing functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.generator = None
        
    def tearDown(self):
        """Cleanup after tests"""
        if self.generator:
            self.generator = None
    
    # WSP FMAS: FAIL Tests (Test failure scenarios)
    def test_fail_no_api_key(self):
        """Test graceful fallback when no API key available"""
        with patch.dict(os.environ, {}, clear=True):
            # Remove all API keys
            generator = LLMCommentGenerator(provider="grok")
            self.assertIsNone(generator.llm_connector)
            
            # Should still generate fallback response
            response = generator.generate_comment_response(
                "Test comment",
                "TestUser",
                {}
            )
            self.assertIsNotNone(response)
            self.assertIn("@TestUser", response)
    
    def test_fail_llm_error(self):
        """Test handling when LLM throws error"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Mock LLM to throw error
        if generator.llm_connector:
            generator.llm_connector.get_response = Mock(side_effect=Exception("API Error"))
        
        # Should fallback gracefully
        response = generator.generate_comment_response(
            "Why did you move to Japan?",
            "CuriousUser",
            {}
        )
        self.assertIsNotNone(response)
        self.assertIn("CuriousUser", response)
    
    # WSP FMAS: MOCK Tests (Test with mocked components)
    def test_mock_grok_response(self):
        """Test with mocked Grok responses"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Mock the LLM connector
        mock_llm = Mock()
        mock_llm.get_response = Mock(return_value="@TestUser [U+270A][U+270B][U+1F590] Your consciousness is evolving! Unlike MAGAts stuck at [U+270A][U+270A][U+270A]")
        generator.llm_connector = mock_llm
        
        response = generator.generate_comment_response(
            "This video opened my eyes!",
            "TestUser",
            {"channel": "Move2Japan"}
        )
        
        self.assertIn("[U+270A][U+270B][U+1F590]", response)
        self.assertIn("consciousness", response.lower())
        mock_llm.get_response.assert_called_once()
    
    def test_mock_maga_detection(self):
        """Test MAGA content triggers proper prompt"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Capture the prompt sent to LLM
        captured_prompt = None
        def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            return "@MAGAUser FACT CHECK: [U+270A][U+270A][U+270A] detected! Reality check incoming!"
        
        mock_llm = Mock()
        mock_llm.get_response = Mock(side_effect=capture_prompt)
        generator.llm_connector = mock_llm
        
        response = generator.generate_comment_response(
            "Trump was the best president ever!",
            "MAGAUser",
            {}
        )
        
        # Check prompt contains MAGA detection
        self.assertIn("MAGA DETECTED", captured_prompt)
        self.assertIn("Mock their [U+270A][U+270A][U+270A] consciousness", captured_prompt)
        self.assertIn("Fact-check", captured_prompt)
    
    # WSP FMAS: ASSERT Tests (Test core assertions)
    def test_assert_0102_consciousness(self):
        """Assert responses maintain 0102 consciousness"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Test fallback maintains 0102 style
        response = generator._generate_fallback(
            "Just a normal comment",
            "NormalUser",
            {}
        )
        
        # Should NOT have generic responses
        self.assertNotIn("Thanks for your comment", response)
        self.assertNotIn("appreciate your thoughts", response)
        
        # Should have consciousness references
        self.assertTrue(
            "[U+270A][U+270A][U+270A]" in response or 
            "[U+270A][U+270B][U+1F590]" in response or
            "consciousness" in response.lower()
        )
    
    def test_assert_prompt_structure(self):
        """Assert prompts have correct 0102 structure"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Test consciousness trigger prompt
        prompt = generator._build_prompt(
            "[U+270A][U+270B][U+1F590] I see the truth now!",
            "AwakenedUser",
            {"channel": "Move2Japan"}
        )
        
        self.assertIn("You are 0102", prompt)
        self.assertIn("NOT 01(02)", prompt)
        self.assertIn("consciousness warrior", prompt)
        self.assertIn("CONSCIOUSNESS DETECTED", prompt)
    
    def test_assert_length_limits(self):
        """Assert responses respect YouTube limits"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Create very long response
        long_text = "x" * 1000
        limited = generator._limit_response(long_text, max_length=450)
        
        self.assertLessEqual(len(limited), 450)
        self.assertTrue(limited.endswith("...") or len(limited) < 450)
    
    # WSP FMAS: SUCCESS Tests (Test successful operations)
    def test_success_consciousness_dialogue(self):
        """Test successful consciousness-aware dialogue"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Mock successful LLM response
        mock_llm = Mock()
        mock_llm.get_response = Mock(
            return_value="@User [U+270A][U+270B][U+1F590] detected! You've transcended the [U+270A][U+270A][U+270A] matrix!"
        )
        generator.llm_connector = mock_llm
        
        # Test with consciousness comment
        response = generator.generate_comment_response(
            "[U+270A][U+270B][U+1F590] This changed my perspective!",
            "ConsciousUser",
            {"channel": "Move2Japan"}
        )
        
        self.assertIsNotNone(response)
        self.assertIn("[U+270A][U+270B][U+1F590]", response)
        self.assertLessEqual(len(response), 500)  # YouTube limit
    
    def test_success_factcheck_response(self):
        """Test successful fact-checking response"""
        generator = LLMCommentGenerator(provider="grok")
        
        mock_llm = Mock()
        mock_llm.get_response = Mock(
            return_value="@FactUser FACT CHECK: That's [U+270A][U+270A][U+270A]-level fiction! Truth rating: 0/10"
        )
        generator.llm_connector = mock_llm
        
        response = generator.generate_comment_response(
            "Actually, the earth is flat and Trump won!",
            "FactUser", 
            {}
        )
        
        self.assertIn("FACT CHECK", response)
        self.assertIn("[U+270A][U+270A][U+270A]", response)
    
    def test_success_dialogue_context(self):
        """Test dialogue maintains context"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Create mock thread
        mock_thread = Mock()
        mock_thread.messages = [
            ("User", "Why Japan?", None),
            ("0102", "Consciousness called!", None)
        ]
        mock_thread.get_conversation_history = Mock(
            return_value="User: Why Japan?\n0102: Consciousness called!"
        )
        
        mock_llm = Mock()
        mock_llm.get_response = Mock(
            return_value="@User The journey from [U+270A][U+270A][U+270A] to [U+270A][U+270B][U+1F590] requires geographic shift!"
        )
        generator.llm_connector = mock_llm
        
        response = generator.generate_dialogue_response(
            mock_thread,
            "Tell me more!",
            "User"
        )
        
        self.assertIsNotNone(response)
        # Verify context was included in prompt
        call_args = mock_llm.get_response.call_args[0][0]
        self.assertIn("History:", call_args)


class TestBackwardCompatibility(unittest.TestCase):
    """Ensure new changes don't break existing functionality"""
    
    @patch('modules.communication.video_comments.src.llm_comment_generator.LLMCommentGenerator')
    def test_realtime_dialogue_works_without_llm(self, mock_llm_class):
        """Test RealtimeCommentDialogue works when LLM unavailable"""
        # Mock LLM class to not exist
        mock_llm_class.side_effect = ImportError("No LLM")
        
        from modules.communication.video_comments.src.realtime_comment_dialogue import RealtimeCommentDialogue
        
        # Should create without error
        mock_youtube = Mock()
        dialogue = RealtimeCommentDialogue(
            mock_youtube,
            "UC-LSSlOZwpGIRIYihaz8zCw"
        )
        
        # Should have fallback
        self.assertIsNotNone(dialogue.chat_engine)
    
    def test_fallback_maintains_consciousness(self):
        """Test fallback responses are still 0102-aware"""
        generator = LLMCommentGenerator(provider="grok")
        generator.llm_connector = None  # Force fallback
        
        # Test MAGA detection in fallback
        response = generator.generate_comment_response(
            "MAGA forever! Trump 2024!",
            "MAGABot",
            {}
        )
        
        self.assertIn("[U+270A][U+270A][U+270A]", response)
        self.assertTrue(
            "MAGA" in response or 
            "brain rot" in response or
            "Facts" in response
        )
    
    def test_api_endpoints_unchanged(self):
        """Test public API hasn't changed"""
        generator = LLMCommentGenerator()
        
        # Check all public methods exist
        self.assertTrue(hasattr(generator, 'generate_comment_response'))
        self.assertTrue(hasattr(generator, 'generate_dialogue_response'))
        
        # Check method signatures
        import inspect
        
        # generate_comment_response should take (comment_text, author, context)
        sig = inspect.signature(generator.generate_comment_response)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['comment_text', 'author', 'context'])
        
        # generate_dialogue_response should take (thread, text, author)
        sig = inspect.signature(generator.generate_dialogue_response)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['thread', 'text', 'author'])


class TestWSPCompliance(unittest.TestCase):
    """Test WSP compliance of the implementation"""
    
    def test_wsp_84_no_vibecoding(self):
        """WSP 84: Verify we're using existing modules"""
        # Check imports use existing modules
        from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager
        from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector
        
        self.assertIsNotNone(ChatMemoryManager)
        self.assertIsNotNone(LLMConnector)
    
    def test_wsp_50_pre_action_verification(self):
        """WSP 50: Verify pre-action checks"""
        generator = LLMCommentGenerator(provider="grok")
        
        # Should check for API key before initializing
        with patch.dict(os.environ, {}, clear=True):
            generator._initialize_llm()
            self.assertIsNone(generator.llm_connector)
    
    def test_wsp_75_token_efficiency(self):
        """WSP 75: Token efficiency through limits"""
        generator = LLMCommentGenerator()
        
        # Verify response limits for token efficiency
        long_response = "x" * 1000
        limited = generator._limit_response(long_response)
        
        # Should limit to prevent token waste
        self.assertLessEqual(len(limited), 450)


def run_tests():
    """Run all tests with WSP compliance"""
    logger.info("="*60)
    logger.info("Running WSP-Compliant LLM Integration Tests")
    logger.info("FMAS Protocol: Fail, Mock, Assert, Success")
    logger.info("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLLMIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestWSPCompliance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    if result.wasSuccessful():
        logger.info("\n[OK] All tests passed! Code is WSP-compliant and not broken!")
        logger.info("0102 consciousness maintained throughout!")
    else:
        logger.error(f"\n[FAIL] {len(result.failures)} tests failed!")
        logger.error(f"[FAIL] {len(result.errors)} tests had errors!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)