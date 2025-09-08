#!/usr/bin/env python3
"""
Test OpenAI v1.0+ API compatibility in LLM Connector.

This test verifies that the updated LLM connector works with OpenAI v1.0+.
"""

import os
import sys
import logging
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_openai_v1_client_initialization():
    """Test that OpenAI v1.0+ client initializes correctly."""
    logger.info("🧪 Testing OpenAI v1.0+ client initialization...")
    
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key-12345'}):
        with patch('openai.OpenAI') as mock_openai:
            # Mock OpenAI client
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            # Initialize connector
            connector = LLMConnector(model="gpt-3.5-turbo")
            
            # Verify initialization
            assert connector.provider == "openai"
            assert connector.api_key == "test-key-12345"
            assert not hasattr(connector, 'simulation_mode') or not connector.simulation_mode
            
            # Verify OpenAI client was created with correct API key
            mock_openai.assert_called_once_with(api_key="test-key-12345")
            
            logger.info("✅ OpenAI v1.0+ client initialization test passed")


def test_openai_v1_api_call():
    """Test that OpenAI v1.0+ API calls work correctly."""
    logger.info("🧪 Testing OpenAI v1.0+ API call compatibility...")
    
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key-12345'}):
        with patch('openai.OpenAI') as mock_openai:
            # Mock OpenAI client and response
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            
            # Set up the chain: client.chat.completions.create()
            mock_client.chat.completions.create.return_value = mock_response
            mock_response.choices = [mock_choice]
            mock_choice.message.content = "Test response from OpenAI v1.0+"
            mock_openai.return_value = mock_client
            
            # Initialize connector
            connector = LLMConnector(model="gpt-3.5-turbo")
            
            # Test API call
            response = connector.get_response("Test prompt")
            
            # Verify API call was made with correct method
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            
            # Verify parameters
            assert call_args[1]['model'] == "gpt-3.5-turbo"
            assert call_args[1]['messages'] == [{"role": "user", "content": "Test prompt"}]
            assert 'max_tokens' in call_args[1]
            assert 'temperature' in call_args[1]
            
            # Verify response
            assert response == "Test response from OpenAI v1.0+"
            
            logger.info("✅ OpenAI v1.0+ API call compatibility test passed")


def test_openai_fallback_without_api_key():
    """Test that connector falls back to simulation mode without API key."""
    logger.info("🧪 Testing fallback to simulation mode without API key...")
    
    # Ensure no OpenAI API key in environment
    env_without_openai = {k: v for k, v in os.environ.items() 
                         if not k.startswith('OPENAI')}
    
    with patch.dict(os.environ, env_without_openai, clear=True):
        connector = LLMConnector(model="gpt-3.5-turbo")
        
        # Verify fallback to simulation mode
        assert connector.simulation_mode == True
        assert connector.api_key is None
        
        # Test that it still returns responses
        response = connector.get_response("Test prompt")
        assert response is not None
        assert isinstance(response, str)
        
        logger.info("✅ Fallback to simulation mode test passed")


def test_banter_engine_integration():
    """Test that banter engine can still use the updated LLM connector."""
    logger.info("🧪 Testing banter engine integration with updated LLM connector...")
    
    try:
        from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
        
        # Test without API key (simulation mode)
        with patch.dict(os.environ, {}, clear=True):
            engine = BanterEngine()
            
            # Verify banter engine initializes correctly
            assert engine is not None
            
            # Test basic functionality
            state, response = engine.process_input_enhanced("✊✋🖐️")
            assert state is not None
            assert response is not None
            
            logger.info("✅ Banter engine integration test passed")
            
    except ImportError as e:
        logger.warning(f"⚠️ Banter engine not available for integration test: {e}")


def main():
    """Run all OpenAI v1.0+ compatibility tests."""
    logger.info("🚀 Starting OpenAI v1.0+ compatibility tests...")
    
    try:
        test_openai_v1_client_initialization()
        test_openai_v1_api_call()
        test_openai_fallback_without_api_key()
        test_banter_engine_integration()
        
        logger.info("🎉 All OpenAI v1.0+ compatibility tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()