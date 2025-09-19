#!/usr/bin/env python3
"""Trigger X posting for current stream since LinkedIn already posted."""

import os
import sys

# Set up environment
os.chdir(r'O:\Foundups-Agent')
sys.path.insert(0, os.getcwd())

# Import the X poster
from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX

def post_to_x():
    """Post current stream to X."""
    content = """@UnDaoDu going live!

#MORON cult killed Charlie? Why #Trump supporter became a killer usher #policestate? #ICE #chicago

https://www.youtube.com/watch?v=riWxmxOozVA"""

    try:
        print("[X] Starting X/Twitter posting...")
        x_poster = AntiDetectionX()
        result = x_poster.post_to_x(content, video_id='riWxmxOozVA')

        if result:
            print("[OK] Successfully posted to X/Twitter!")

            # Update the history
            import json
            history_file = "memory/orchestrator_posted_streams.json"

            # Load existing history
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = {}

            # Update with X posting
            if 'riWxmxOozVA' not in history:
                history['riWxmxOozVA'] = {
                    'timestamp': '2025-09-16T10:00:00',
                    'title': '#MORON cult killed Charlie? Why #Trump supporter became a killer usher #policestate? #ICE #chicago',
                    'url': 'https://www.youtube.com/watch?v=riWxmxOozVA',
                    'platforms_posted': ['linkedin', 'x_twitter']
                }
            elif 'x_twitter' not in history['riWxmxOozVA']['platforms_posted']:
                history['riWxmxOozVA']['platforms_posted'].append('x_twitter')

            # Save updated history
            os.makedirs("memory", exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)

            print("[OK] Updated posting history")
        else:
            print("[FAIL] X posting failed")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    post_to_x()
