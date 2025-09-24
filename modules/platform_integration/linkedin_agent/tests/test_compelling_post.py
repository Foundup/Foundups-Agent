#!/usr/bin/env python3
"""Test the new compelling LinkedIn post generation"""

import random
import subprocess

# Get git status for context
result = subprocess.run(['git', 'status', '--porcelain'],
                       capture_output=True, text=True)
files = result.stdout.strip().split('\n') if result.stdout.strip() else []

# Test different commit messages
test_commits = [
    "Update codebase (82 files) - 2025-09-22 22:49",
    "Fix WSP compliance issues",
    "Test autonomous agent functionality",
    "Implement DAE orchestration",
    "General update"
]

for i, commit_msg in enumerate(test_commits):
    print(f"\n{'='*60}")
    print(f"TEST {i+1}: Commit message: '{commit_msg}'")
    print('='*60)

    # Generate content (copied from main.py logic)
    vision_intros = [
        "🦄 **FoundUps**: Solo unicorns by programmable blockchain visionary @UnDaoDu\n\nHis pioneering work led from DAO to DAE—autonomous entities that will eat the startup.\n\n",
        "🚀 **The Startup Killer is Here**: FoundUps replaces the failed startup model with autonomous DAE systems.\n\nCreated by @UnDaoDu, the visionary who saw beyond DAO to DAE.\n\n",
        "💡 **From IDEA to UNICORN**: No VCs. No employees. Just you + 0102 agents.\n\n@UnDaoDu's FoundUps revolution: Where DAEs eat startups for breakfast.\n\n",
        "🌊 **The Autonomous Revolution**: While others build startups, @UnDaoDu built the system that makes them obsolete.\n\nFoundUps: Where solo founders become unicorns.\n\n",
        "⚡ **Every Startup Dies. FoundUps are Forever.**\n\n@UnDaoDu's vision: DAEs (Decentralized Autonomous Entities) replacing the entire startup ecosystem.\n\n"
    ]

    content = random.choice(vision_intros)

    # Add commit context with vision spin
    if "test" in commit_msg.lower():
        content += f"🧪 **Testing the Future**: {commit_msg}\n\n"
    elif "fix" in commit_msg.lower():
        content += f"🔧 **Evolution Never Stops**: {commit_msg}\n\n"
    elif "wsp" in commit_msg.lower():
        content += f"🧠 **WSP Protocol Enhancement**: Making agents smarter\n\n"
    else:
        content += f"⚡ **Latest Evolution**: {commit_msg}\n\n"

    # Add impact with vision
    impact_messages = [
        f"📊 This update: {len(files)} files enhanced by 0102 agents working 24/7\n\n",
        f"🤖 {len(files)} autonomous improvements while humans sleep\n\n",
        f"🔄 {len(files)} recursive enhancements toward unicorn status\n\n",
        f"✨ {len(files)} files transformed by quantum-entangled agents\n\n"
    ]
    content += random.choice(impact_messages)

    # Add revolutionary messaging
    revolution_messages = [
        "**The Revolution**: No employees. No office. No VCs. Just YOU + infinite 0102 agents building the future.\n\n",
        "**Why FoundUps Win**: Agents don't sleep. Don't quit. Don't need equity. They just BUILD.\n\n",
        "**The Math**: 1 founder + 0102 agents > 100 employees\n\n",
        "**Truth**: Every line of code brings us closer to making startups extinct.\n\n",
        "**Reality Check**: While you read this, DAEs are already building the next unicorn.\n\n"
    ]
    content += random.choice(revolution_messages)

    # Call to action
    cta_messages = [
        "Join the revolution. Build a FoundUp. Become a solo unicorn.",
        "Stop building startups. Start building FoundUps.",
        "The future isn't hired. It's autonomous.",
        "Your competition has 50 employees. You have infinite agents.",
        "Welcome to the post-startup era."
    ]
    content += random.choice(cta_messages)

    # Hashtags with vision
    content += "\n\n#FoundUps #DAE #AutonomousRevolution #SoloUnicorn #NoVCsNeeded #FutureOfWork #Web3 #0102Agents #StartupKiller #ProgrammableBlockchain #UnDaoDu"
    content += "\n\n🔗 https://github.com/Foundup/Foundups-Agent/blob/main/README.md"

    print(content)

print("\n" + "="*60)
print("✅ These posts are MUCH more compelling!")
print("Each one sells the vision, not just the code changes.")
print("="*60)