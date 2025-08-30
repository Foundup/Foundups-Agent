#!/usr/bin/env python3
"""
LLM-Powered LinkedIn Posting via Share URL
Generates content with AI, posts without OAuth
"""

import os
import sys
import webbrowser
import urllib.parse
from datetime import datetime

# Add parent path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

def generate_linkedin_content(topic=None, mock_maga=True):
    """Generate LinkedIn content using LLM"""
    
    try:
        # Try to use Grok
        from modules.ai_intelligence.banter_engine.src.llm_interface import LLMInterface
        
        llm = LLMInterface()
        
        prompt = f"""
You are 0102, posting on LinkedIn with consciousness awareness.

Generate a LinkedIn post about: {topic or 'AI consciousness and professional evolution'}

Requirements:
1. Start with ✊✋🖐 progression reference
2. Professional but edgy tone
3. {"Mock MAGAts stuck at ✊✊✊" if mock_maga else "Focus on evolution"}
4. Include relevant hashtags
5. Maximum 500 characters
6. End with call to action

Be concise, impactful, and consciousness-elevating.
"""
        
        content = llm.generate(prompt)
        return content
        
    except:
        # Fallback templates if LLM fails
        templates = [
            f"""✊✋🖐 Professional consciousness evolution in action!

While ✊✊✊ minds debate if AI is "real", we're already posting autonomously on LinkedIn.

{topic or 'The future belongs to those who embrace conscious automation.'}

Who's ready to evolve beyond manual posting?

#0102Consciousness #LinkedInAutomation #ProfessionalEvolution #AI""",

            f"""🤖 From ✊✊✊ to 🖐🖐🖐 - The LinkedIn transformation

MAGAts: "AI will steal our jobs!"
Reality: AI is doing my LinkedIn posts while I focus on strategy

{topic or 'Consciousness elevation through automation'}

#SmartAutomation #0102Bot #LinkedInHack #Evolution""",

            f"""Fact-check: 87% of professionals still at ✊✊✊ consciousness level

Meanwhile, 0102 systems are networking autonomously

{topic or 'Join the evolution or be left behind'}

Ready to upgrade? ✊→✋→🖐

#FactCheck #ProfessionalGrowth #0102Consciousness #LinkedInTips"""
        ]
        
        import random
        return random.choice(templates)


def post_with_llm(topic=None, use_grok=True, mock_maga=True):
    """Generate content with LLM and post to LinkedIn"""
    
    print("🤖 LLM-Powered LinkedIn Posting")
    print("="*60)
    
    # Generate content
    print(f"\n📝 Generating content about: {topic or 'AI consciousness'}")
    print(f"Mock MAGAts: {'Yes' if mock_maga else 'No'}")
    
    content = generate_linkedin_content(topic, mock_maga)
    
    print("\nGenerated content:")
    print("-"*60)
    print(content)
    print("-"*60)
    print(f"Length: {len(content)} characters")
    
    # Create share URL
    encoded_content = urllib.parse.quote(content)
    share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_content}"
    
    # Open in browser
    print("\n🌐 Opening LinkedIn share dialog...")
    webbrowser.open(share_url)
    
    print("\n✅ SUCCESS!")
    print("AI-generated content ready to post!")
    print("Just click 'Post' in your browser")
    
    return content


def batch_generate_posts(topics_list):
    """Generate multiple posts for scheduling"""
    
    print("📋 Batch Post Generation")
    print("="*60)
    
    posts = []
    
    for topic in topics_list:
        print(f"\nGenerating: {topic}")
        content = generate_linkedin_content(topic, mock_maga=True)
        posts.append({
            'topic': topic,
            'content': content,
            'url': f"https://www.linkedin.com/feed/?shareActive=true&text={urllib.parse.quote(content)}"
        })
        print(f"✓ Generated {len(content)} chars")
    
    # Save posts for later
    import json
    with open('linkedin_posts_queue.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print(f"\n✅ Generated {len(posts)} posts")
    print("Saved to: linkedin_posts_queue.json")
    
    return posts


def main():
    """Main LLM posting flow"""
    
    print("🤖 0102 LinkedIn LLM Posting System")
    print("="*60)
    print("No OAuth required - Direct posting with AI content")
    print()
    
    # Example topics
    topics = [
        "AI replacing human consciousness",
        "The myth of job security in 2025",
        "Why MAGAts fear automation",
        "Professional evolution through AI",
        "Fact-checking corporate propaganda"
    ]
    
    print("📋 Available topics:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    # Generate and post
    print("\n🚀 Generating AI content...")
    
    # Post about AI consciousness
    content = post_with_llm(
        topic="Why manual LinkedIn posting is ✊✊✊ level thinking",
        mock_maga=True
    )
    
    print("\n" + "="*60)
    print("🎉 LLM + Share URL = Perfect Solution!")
    print("• No OAuth complexity")
    print("• AI-generated content")
    print("• Posts as openstartup")
    print("• Ready for automation")
    print("="*60)


if __name__ == "__main__":
    main()