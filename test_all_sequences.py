#!/usr/bin/env python3
"""
Comprehensive Emoji Sequence Detection Test
Following WSP Guidelines

This script tests ALL possible emoji sequences to understand current coverage
and identify gaps for improving the emoji-guided LLM response system.
"""

import sys
import os

# Add the module path to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), 'modules', 'ai_intelligence', 'banter_engine', 'banter_engine'))

try:
    from src.banter_engine import BanterEngine
    
    def test_all_emoji_sequences():
        """Test all possible 3-emoji sequences comprehensively."""
        print("🎯 COMPREHENSIVE EMOJI SEQUENCE DETECTION TEST")
        print("=" * 80)
        print("Testing all 27 possible emoji sequences (0-0-0 through 2-2-2)")
        print("Following WSP guidelines for emoji-guided LLM response system")
        print("=" * 80)
        
        # Initialize banter engine
        banter_engine = BanterEngine()
        
        # All possible 3-emoji sequences with detailed descriptions
        all_sequences = [
            ("✊✊✊", (0, 0, 0), "Pure confrontational energy - aggressive, challenging"),
            ("✊✊✋", (0, 0, 1), "Confrontational to peaceful shift - backing down"),
            ("✊✊🖐️", (0, 0, 2), "Confrontational to open shift - sudden openness"),
            ("✊✋✊", (0, 1, 0), "Confrontational with peaceful pause - hesitation"),
            ("✊✋✋", (0, 1, 1), "Confrontational to peaceful transition - calming"),
            ("✊✋🖐️", (0, 1, 2), "Full transformational sequence - breakthrough"),
            ("✊🖐️✊", (0, 2, 0), "Confrontational with open pause - complex emotion"),
            ("✊🖐️✋", (0, 2, 1), "Complex transition pattern - mixed signals"),
            ("✊🖐️🖐️", (0, 2, 2), "Confrontational to open progression - evolution"),
            ("✋✊✊", (1, 0, 0), "Peaceful to confrontational shift - escalation"),
            ("✋✊✋", (1, 0, 1), "Peaceful-confrontational oscillation - uncertainty"),
            ("✋✊🖐️", (1, 0, 2), "Mixed energy progression - complex journey"),
            ("✋✋✊", (1, 1, 0), "Peaceful to confrontational - sudden anger"),
            ("✋✋✋", (1, 1, 1), "Pure peaceful energy - calm, centered, balanced"),
            ("✋✋🖐️", (1, 1, 2), "Peaceful to open progression - gentle expansion"),
            ("✋🖐️✊", (1, 2, 0), "Complex to confrontational - defensive reaction"),
            ("✋🖐️✋", (1, 2, 1), "Complex peaceful pattern - nuanced calm"),
            ("✋🖐️🖐️", (1, 2, 2), "Progressive opening sequence - gradual expansion"),
            ("🖐️✊✊", (2, 0, 0), "Open to confrontational shift - defensive closure"),
            ("🖐️✊✋", (2, 0, 1), "Open to mixed energy - emotional complexity"),
            ("🖐️✊🖐️", (2, 0, 2), "Open-confrontational oscillation - internal conflict"),
            ("🖐️✋✊", (2, 1, 0), "Open to confrontational via peaceful - complex path"),
            ("🖐️✋✋", (2, 1, 1), "Open to peaceful progression - settling down"),
            ("🖐️✋🖐️", (2, 1, 2), "Open progression via peaceful - gentle flow"),
            ("🖐️🖐️✊", (2, 2, 0), "Open to confrontational - sudden defensiveness"),
            ("🖐️🖐️✋", (2, 2, 1), "Open to peaceful - transcendent calm"),
            ("🖐️🖐️🖐️", (2, 2, 2), "Pure transcendent energy - unity, elevated consciousness"),
        ]
        
        # Track results
        detected_sequences = []
        undetected_sequences = []
        responses_generated = []
        llm_guidance_available = []
        
        print(f"\n📊 TESTING {len(all_sequences)} SEQUENCES:")
        print("-" * 80)
        
        for i, (emoji_seq, expected_tuple, description) in enumerate(all_sequences, 1):
            print(f"\n{i:2d}. Testing: {emoji_seq} -> {expected_tuple}")
            print(f"    Description: {description}")
            
            # Test banter engine detection
            state_info, response = banter_engine.process_input(emoji_seq)
            
            if "No sequence detected" not in state_info:
                detected_sequences.append((emoji_seq, expected_tuple, description, state_info, response))
                print(f"    ✅ DETECTED: {state_info}")
                
                # Check for LLM guidance
                state_lower = state_info.lower()
                has_guidance = any(keyword in state_lower for keyword in [
                    "state:", "tone:", "confrontational", "peaceful", "transcendent",
                    "conscious", "unconscious", "entanglement", "mode", "energy"
                ])
                
                if has_guidance:
                    llm_guidance_available.append((emoji_seq, state_info))
                    print(f"    🧠 LLM GUIDANCE: Available")
                else:
                    print(f"    ⚠️  LLM GUIDANCE: Limited")
                
                if response and isinstance(response, str) and response.strip():
                    responses_generated.append((emoji_seq, response))
                    print(f"    📝 RESPONSE: {response}")
                else:
                    print(f"    ❌ RESPONSE: None generated")
            else:
                undetected_sequences.append((emoji_seq, expected_tuple, description))
                print(f"    ❌ NOT DETECTED")
        
        # Comprehensive analysis
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE ANALYSIS RESULTS")
        print(f"{'='*80}")
        
        total_sequences = len(all_sequences)
        detected_count = len(detected_sequences)
        response_count = len(responses_generated)
        guidance_count = len(llm_guidance_available)
        
        print(f"📈 DETECTION STATISTICS:")
        print(f"  Total sequences tested: {total_sequences}")
        print(f"  Sequences detected: {detected_count} ({detected_count/total_sequences*100:.1f}%)")
        print(f"  Responses generated: {response_count} ({response_count/detected_count*100:.1f}% of detected)")
        print(f"  LLM guidance available: {guidance_count} ({guidance_count/detected_count*100:.1f}% of detected)")
        
        # Detailed breakdown by pattern
        print(f"\n🔍 PATTERN ANALYSIS:")
        
        # Group by first emoji
        first_emoji_groups = {"✊": [], "✋": [], "🖐️": []}
        for seq, tuple_val, desc, state, resp in detected_sequences:
            first_emoji = seq[0]
            if first_emoji in first_emoji_groups:
                first_emoji_groups[first_emoji].append((seq, tuple_val))
        
        for emoji, sequences in first_emoji_groups.items():
            emoji_name = {"✊": "Confrontational", "✋": "Peaceful", "🖐️": "Open"}[emoji]
            print(f"  {emoji} ({emoji_name}) starting sequences: {len(sequences)}")
            for seq, tuple_val in sequences:
                print(f"    {seq} -> {tuple_val}")
        
        # Show undetected sequences for improvement
        if undetected_sequences:
            print(f"\n❌ UNDETECTED SEQUENCES ({len(undetected_sequences)}):")
            print("These sequences need to be added to improve LLM guidance coverage:")
            for emoji_seq, expected_tuple, description in undetected_sequences:
                print(f"  {emoji_seq} -> {expected_tuple}: {description}")
        
        # Show detected sequences with responses
        if detected_sequences:
            print(f"\n✅ DETECTED SEQUENCES WITH RESPONSES ({len(responses_generated)}):")
            for emoji_seq, response in responses_generated:
                print(f"  {emoji_seq}: \"{response}\"")
        
        # LLM guidance analysis
        if llm_guidance_available:
            print(f"\n🧠 LLM GUIDANCE ANALYSIS ({len(llm_guidance_available)}):")
            for emoji_seq, state_info in llm_guidance_available:
                print(f"  {emoji_seq}: {state_info}")
        
        # Performance statistics
        stats = banter_engine.get_performance_stats()
        print(f"\n⚡ PERFORMANCE STATISTICS:")
        print(f"  Total requests: {stats.get('total_requests', 0)}")
        print(f"  Success rate: {stats.get('success_rate_percent', 0):.1f}%")
        print(f"  Cache hit rate: {stats.get('cache_hit_rate_percent', 0):.1f}%")
        print(f"  Cache size: {stats.get('cache_size', 0)}")
        
        # WSP Compliance Assessment
        print(f"\n📋 WSP COMPLIANCE ASSESSMENT:")
        detection_grade = "A" if detected_count >= 24 else "B" if detected_count >= 20 else "C" if detected_count >= 15 else "D"
        response_grade = "A" if response_count >= detected_count * 0.9 else "B" if response_count >= detected_count * 0.8 else "C"
        guidance_grade = "A" if guidance_count >= detected_count * 0.9 else "B" if guidance_count >= detected_count * 0.7 else "C"
        
        print(f"  Detection Coverage: {detection_grade} ({detected_count}/{total_sequences})")
        print(f"  Response Generation: {response_grade} ({response_count}/{detected_count})")
        print(f"  LLM Guidance Quality: {guidance_grade} ({guidance_count}/{detected_count})")
        
        overall_grade = min(detection_grade, response_grade, guidance_grade)
        print(f"  Overall WSP Grade: {overall_grade}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS FOR IMPROVEMENT:")
        if detected_count < 20:
            print("  🔧 CRITICAL: Add support for missing emoji sequences")
            print("     - Focus on sequences starting with ✋ and 🖐️")
            print("     - Implement fallback pattern matching")
        
        if response_count < detected_count * 0.8:
            print("  📝 IMPORTANT: Improve response generation rate")
            print("     - Add more themed responses")
            print("     - Enhance fallback response system")
        
        if guidance_count < detected_count * 0.7:
            print("  🧠 IMPORTANT: Enhance LLM guidance extraction")
            print("     - Add more descriptive state information")
            print("     - Include emotional tone keywords")
        
        print(f"\n🎯 NEXT STEPS FOR LLM INTEGRATION:")
        print("  1. Expand sequence detection to cover all 27 patterns")
        print("  2. Enhance state descriptions with LLM-friendly keywords")
        print("  3. Add contextual response generation based on detected patterns")
        print("  4. Implement dynamic LLM prompt generation from emoji guidance")
        
        return {
            "total_sequences": total_sequences,
            "detected_count": detected_count,
            "response_count": response_count,
            "guidance_count": guidance_count,
            "detected_sequences": detected_sequences,
            "undetected_sequences": undetected_sequences,
            "overall_grade": overall_grade
        }

    if __name__ == "__main__":
        results = test_all_emoji_sequences()
        
        # Exit with appropriate code for CI/CD
        if results["overall_grade"] in ["A", "B"]:
            print(f"\n🎉 SUCCESS: Emoji detection system is performing well!")
            sys.exit(0)
        else:
            print(f"\n⚠️  WARNING: Emoji detection system needs improvement")
            sys.exit(1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all modules are properly installed and paths are correct.")
    sys.exit(1) 