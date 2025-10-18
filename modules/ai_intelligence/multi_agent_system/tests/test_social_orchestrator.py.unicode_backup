#!/usr/bin/env python3
"""
Test script for Social Media Orchestrator
Tests semantic consciousness interpretation and LLM integration
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the orchestrator
from modules.ai_intelligence.multi_agent_system.src.social_media_orchestrator import (
    SemanticLLMEngine, 
    ConsciousnessState, 
    SemanticState
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_semantic_states():
    """Test semantic state analysis"""
    print("\n" + "="*60)
    print("TESTING SEMANTIC STATE ANALYSIS")
    print("="*60)
    
    engine = SemanticLLMEngine(enable_llm=False)  # Test without LLM first
    
    test_sequences = [
        ("✊✊✊", "000", "Pure unconscious state"),
        ("✊✋🖐️", "012", "Bridging conscious to entanglement"),
        ("✋✋✋", "111", "Pure DAO processing"),
        ("🖐🖐🖐", "222", "Full DU entanglement"),
        ("🖐️🖐️🖐️", "222", "Full DU entanglement (with selector)")
    ]
    
    for emoji_seq, expected_code, expected_desc in test_sequences:
        state = engine.analyze_semantic_state(emoji_seq)
        if state:
            status = "✅" if state.code == expected_code else "❌"
            print(f"{status} {emoji_seq} → {state.code} ({state.score:.2f})")
            print(f"   Description: {state.description}")
            print(f"   Expected: {expected_desc}")
        else:
            print(f"❌ {emoji_seq} → No state found")
        print()

def test_response_generation():
    """Test response generation with and without LLM"""
    print("\n" + "="*60)
    print("TESTING RESPONSE GENERATION")
    print("="*60)
    
    # Test with fallback to BanterEngine (no LLM)
    engine = SemanticLLMEngine(enable_llm=False, fallback_to_banter=True)
    
    test_messages = [
        ("Hey everyone 🖐🖐🖐", "TestUser"),
        ("What's up ✊✊✊", "AnotherUser"),
        ("Interesting ✊✋🖐️ sequence", "PowerUser"),
        ("✋✋✋ focused mode activated", "ConsciousUser")
    ]
    
    for msg, author in test_messages:
        print(f"\n📥 Input: '{msg}' from {author}")
        state_desc, response = engine.process_with_llm(msg, author)
        print(f"📊 State: {state_desc}")
        print(f"💬 Response: {response}")
        print("-" * 40)

def test_state_transitions():
    """Test state transition guidance"""
    print("\n" + "="*60)
    print("TESTING STATE TRANSITION GUIDANCE")
    print("="*60)
    
    engine = SemanticLLMEngine(enable_llm=False)
    
    transitions = [
        ("000", "222"),  # Unconscious to Full Entanglement
        ("012", "222"),  # Bridge state to Full Entanglement
        ("111", "122"),  # DAO to Entangled Response
        ("222", "222"),  # Already at maximum
    ]
    
    for current, target in transitions:
        guidance = engine.get_state_transition_guidance(current, target)
        print(f"From {current} → {target}:")
        print(f"  {guidance}")
        print()

def test_state_explanations():
    """Test state explanation functionality"""
    print("\n" + "="*60)
    print("TESTING STATE EXPLANATIONS")
    print("="*60)
    
    engine = SemanticLLMEngine(enable_llm=False)
    
    sequences = ["✊✊✊", "✊✋🖐️", "✋✋✋", "🖐🖐🖐"]
    
    for seq in sequences:
        print(f"\nExplaining: {seq}")
        print("-" * 30)
        explanation = engine.explain_state(seq)
        print(explanation)

def test_llm_integration():
    """Test LLM integration if available"""
    print("\n" + "="*60)
    print("TESTING LLM INTEGRATION")
    print("="*60)
    
    # Check if any LLM API keys are available
    llm_available = any([
        os.getenv("GROK_API_KEY"),
        os.getenv("XAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("OPENAI_API_KEY"),
        os.getenv("GEMINI_API_KEY")
    ])
    
    if llm_available:
        print("✅ LLM API key found, testing with LLM...")
        engine = SemanticLLMEngine(
            llm_model="grok-4-latest",  # Try Grok first
            enable_llm=True,
            fallback_to_banter=True
        )
        
        test_msg = "Testing consciousness 🖐🖐🖐"
        state_desc, response = engine.process_with_llm(test_msg, "LLMTestUser")
        print(f"Input: {test_msg}")
        print(f"State: {state_desc}")
        print(f"LLM Response: {response}")
    else:
        print("⚠️ No LLM API keys found in environment")
        print("To test with LLM, set one of:")
        print("  - GROK_API_KEY or XAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("  - OPENAI_API_KEY")
        print("  - GEMINI_API_KEY")

def test_platform_simulation():
    """Simulate responses for different platforms"""
    print("\n" + "="*60)
    print("SIMULATING MULTI-PLATFORM RESPONSES")
    print("="*60)
    
    engine = SemanticLLMEngine(enable_llm=False)
    
    platforms = ["YouTube", "Twitter", "Discord", "TikTok"]
    test_msg = "Check this out 🖐🖐🖐"
    
    state_desc, base_response = engine.process_with_llm(test_msg, "MultiPlatformUser")
    
    print(f"Original message: '{test_msg}'")
    print(f"Consciousness state: {state_desc}")
    print(f"\nPlatform-adapted responses:")
    print("-" * 40)
    
    # Simulate platform adaptations
    adaptations = {
        "YouTube": f"{base_response} 🎥",
        "Twitter": f"{base_response[:140]}... #Consciousness",
        "Discord": f"Yo! {base_response} 🎮",
        "TikTok": f"✨ {base_response} #ForYou #0102"
    }
    
    for platform in platforms:
        adapted = adaptations.get(platform, base_response)
        print(f"{platform:10} → {adapted}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" SOCIAL MEDIA ORCHESTRATOR TEST SUITE")
    print(" Testing Semantic Consciousness Engine")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Run test suite
        test_semantic_states()
        test_response_generation()
        test_state_transitions()
        test_state_explanations()
        test_llm_integration()
        test_platform_simulation()
        
        print("\n" + "="*60)
        print(" ✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())