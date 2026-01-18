import asyncio
import os
import sys
from pathlib import Path

# Add repo root to sys.path (WSP 50: never assume cwd)
repo_root = Path(__file__).resolve()
for parent in [repo_root] + list(repo_root.parents):
    if (parent / "modules").exists() and (parent / "holo_index.py").exists():
        sys.path.insert(0, str(parent))
        break

# Set environment variables for testing
os.environ["YT_AUTOMATION_ENABLED"] = "true"
os.environ["YT_LIVECHAT_UI_ACTIONS_ENABLED"] = "true"
os.environ["YT_PARTY_REACTIONS_ENABLED"] = "true"
os.environ["PARTY_TRAINING_ENABLED"] = "false" # Disable training for test run

from modules.communication.livechat.src.party_reactor import trigger_party

async def main():
    print("Triggering hardened !party mode...")
    result = await trigger_party(total_clicks=15)
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())
