import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

# Set environment variables for testing
os.environ["YT_AUTOMATION_ENABLED"] = "true"
os.environ["YT_LIVECHAT_UI_ACTIONS_ENABLED"] = "true"
os.environ["YT_PARTY_REACTIONS_ENABLED"] = "true"
os.environ["PARTY_TRAINING_ENABLED"] = "false" # Disable training for test run

from modules.communication.livechat.src.party_reactor import trigger_party

async def main():
    print("🚀 Triggering hardened !party mode...")
    result = await trigger_party(total_clicks=15)
    print(f"\n✅ Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
