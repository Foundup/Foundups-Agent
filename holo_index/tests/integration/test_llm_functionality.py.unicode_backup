#!/usr/bin/env python3
"""
Test actual LLM functionality with Qwen model.

This script tests the actual LLM inference capabilities.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_llm_inference():
    """Test actual LLM inference."""
    print("🧠 Testing Qwen LLM Inference...")

    try:
        from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
        from holo_index.qwen_advisor.config import QwenAdvisorConfig

        # Get config
        config = QwenAdvisorConfig.from_env()
        print(f"Model path: {config.model_path}")
        print(f"Model exists: {config.model_path.exists()}")

        if not config.model_path.exists():
            print("❌ Model file not found!")
            return False

        # Create engine
        engine = QwenInferenceEngine(
            model_path=config.model_path,
            max_tokens=256,  # Smaller for testing
            temperature=0.1  # More deterministic
        )

        print("Initializing model (this may take a moment)...")
        start_time = time.time()
        success = engine.initialize()
        init_time = time.time() - start_time

        if not success:
            print("❌ Model initialization failed!")
            return False

        print(".2f")
        print("✓ Model loaded successfully")

        # Test simple inference
        print("\nTesting inference with simple prompt...")
        test_prompt = "Hello, can you explain what a function is in programming?"

        start_time = time.time()
        response = engine.generate_response(test_prompt)
        inference_time = time.time() - start_time

        print(f"Response (took {inference_time:.2f}s):")
        print(f"'{response}'")

        if len(response.strip()) > 10:
            print("✅ LLM inference successful!")
            return True
        else:
            print("❌ LLM response too short or empty")
            return False

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_analysis():
    """Test code analysis capabilities."""
    print("\n🔍 Testing Code Analysis...")

    try:
        from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
        from holo_index.qwen_advisor.config import QwenAdvisorConfig

        config = QwenAdvisorConfig.from_env()
        engine = QwenInferenceEngine(
            model_path=config.model_path,
            max_tokens=200,
            temperature=0.1
        )

        if not engine.initialize():
            print("❌ Could not initialize for code analysis")
            return False

        # Test code analysis
        analysis = engine.analyze_code_context(
            query="how to implement user authentication",
            code_snippets=[
                "def authenticate_user(username, password): return check_credentials(username, password)",
                "class AuthService: def login(self, creds): pass"
            ],
            wsp_guidance=["Follow WSP 12 for dependency management"]
        )

        print("Code Analysis Results:")
        print(f"  Guidance: {analysis.get('guidance', 'N/A')[:100]}...")
        print(f"  Confidence: {analysis.get('confidence', 'N/A')}")
        print(f"  Recommendations: {len(analysis.get('recommendations', []))}")

        if analysis.get('guidance') and len(analysis['guidance']) > 20:
            print("✅ Code analysis successful!")
            return True
        else:
            print("❌ Code analysis failed")
            return False

    except Exception as e:
        print(f"❌ Code analysis test failed: {e}")
        return False

def main():
    """Run LLM functionality tests."""
    print("🚀 Qwen LLM Functionality Test")
    print("=" * 50)

    # Test basic inference
    inference_ok = test_llm_inference()

    # Test code analysis if inference works
    if inference_ok:
        analysis_ok = test_code_analysis()
    else:
        analysis_ok = False
        print("\n⏭️  Skipping code analysis (inference failed)")

    # Summary
    print("\n" + "=" * 50)
    print("📊 FUNCTIONALITY TEST RESULTS")

    tests = [
        ("Basic Inference", inference_ok),
        ("Code Analysis", analysis_ok)
    ]

    passed = 0
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{len(tests)} functionality tests passed")

    if passed == len(tests):
        print("🎉 Full LLM functionality working!")
        print("🤖 HoloIndex now has REAL AI intelligence!")
    elif passed > 0:
        print("⚠️  Partial functionality - some features working")
    else:
        print("💥 No LLM functionality working")

    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
