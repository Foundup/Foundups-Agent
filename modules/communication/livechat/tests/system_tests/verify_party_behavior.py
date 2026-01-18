import asyncio
import logging
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

# Add repo root to sys.path (WSP 50: never assume cwd)
_here = Path(__file__).resolve()
for _parent in [_here] + list(_here.parents):
    if (_parent / "modules").exists() and (_parent / "holo_index.py").exists():
        sys.path.insert(0, str(_parent))
        break

from modules.infrastructure.human_interaction import get_interaction_controller

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def verify_behavior():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Connected to existing Chrome instance on 9222", flush=True)
        
        interaction = get_interaction_controller(driver, platform="youtube_chat")
        
        print("Waiting for chatframe to be available...", flush=True)
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#chatframe")))
            print("Chatframe found!", flush=True)
        except:
            print("Chatframe not found via explicit wait, continuing anyway...", flush=True)

        print("Starting burst of 5 reactions...", flush=True)
        # We can iterate through different ones or just spam the same one
        reactions = ["reaction_100", "reaction_wide_eyes", "reaction_celebrate", "reaction_smiley", "reaction_heart"]
        
        for r in reactions:
            print(f"Spamming {r}...", flush=True)
            await interaction.spam_action(r, count=1)
        
        print("Verification complete!", flush=True)
        
    except Exception as e:
        print(f"Verification failed: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(verify_behavior())
