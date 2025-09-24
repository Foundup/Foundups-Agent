#!/usr/bin/env python3
"""
Test script for LLM integration in HoloIndex Qwen Advisor.

This script tests the LLM integration without requiring the actual model to be loaded,
verifying that the code structure and imports work correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all LLM-related imports work."""
    print("Testing LLM integration imports...")

    try:
        from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
        print("✓ QwenInferenceEngine import successful")
    except ImportError as e:
        print(f"✗ QwenInferenceEngine import failed: {e}")
        return False

    try:
        from holo_index.qwen_advisor.config import QwenAdvisorConfig
        print("✓ QwenAdvisorConfig import successful")
    except ImportError as e:
        print(f"✗ QwenAdvisorConfig import failed: {e}")
        return False

    try:
        from holo_index.qwen_advisor.advisor import QwenAdvisor
        print("✓ QwenAdvisor import successful")
    except ImportError as e:
        print(f"✗ QwenAdvisor import failed: {e}")
        return False

    return True

def test_llm_engine_initialization():
    """Test LLM engine initialization without loading model."""
    print("\nTesting LLM engine initialization...")

    try:
        from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
        from holo_index.qwen_advisor.config import QwenAdvisorConfig

        config = QwenAdvisorConfig.from_env()
        print(f"✓ Config loaded: model_path={config.model_path}")

        # Test engine creation (won't load model without llama-cpp-python)
        engine = QwenInferenceEngine(
            model_path=config.model_path,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        print("✓ QwenInferenceEngine created successfully")

        # Test model info (should show not initialized)
        info = engine.get_model_info()
        print(f"✓ Model info: {info}")

        return True

    except Exception as e:
        print(f"✗ LLM engine initialization failed: {e}")
        return False

def test_advisor_integration():
    """Test that advisor integrates LLM engine."""
    print("\nTesting advisor LLM integration...")

    try:
        from holo_index.qwen_advisor.advisor import QwenAdvisor, AdvisorContext
        from holo_index.qwen_advisor.config import QwenAdvisorConfig

        # Create advisor (should initialize LLM engine)
        config = QwenAdvisorConfig.from_env()
        advisor = QwenAdvisor(config=config)
        print("✓ QwenAdvisor created with LLM engine")

        # Check that LLM engine is attached
        if hasattr(advisor, 'llm_engine'):
            print("✓ LLM engine attached to advisor")
        else:
            print("✗ LLM engine not attached to advisor")
            return False

        # Test model info through advisor
        model_info = advisor.llm_engine.get_model_info()
        print(f"✓ Advisor LLM model info: {model_info}")

        return True

    except Exception as e:
        print(f"✗ Advisor integration test failed: {e}")
        return False

def test_llm_dependencies():
    """Test that LLM dependencies are available."""
    print("\nTesting LLM dependencies...")

    try:
        import llama_cpp
        print("✓ llama-cpp-python is available")
        return True
    except ImportError:
        print("✗ llama-cpp-python not installed (this is expected in test environment)")
        print("  Run: pip install llama-cpp-python==0.2.69")
        return False

def main():
    """Run all tests."""
    print("🔍 HoloIndex LLM Integration Test Suite")
    print("=" * 50)

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test LLM engine
    results.append(("LLM Engine", test_llm_engine_initialization()))

    # Test advisor integration
    results.append(("Advisor Integration", test_advisor_integration()))

    # Test dependencies (optional)
    dep_result = test_llm_dependencies()
    results.append(("Dependencies", dep_result))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed >= 3:  # Core functionality works
        print("🎉 Core LLM integration is structurally sound!")
        if not dep_result:
            print("⚠️  Note: Install llama-cpp-python to enable actual LLM inference")
    else:
        print("💥 Critical issues found in LLM integration")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
