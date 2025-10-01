#!/usr/bin/env python3
"""
Feed Scripts Catalog to HoloIndex Discovery System
Enables 0102 to find scripts through semantic search
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_scripts_discovery():
    """Create discovery feed for all scripts in the codebase."""

    discoveries = []
    timestamp = datetime.now().isoformat()

    # Core script categories with semantic tags
    script_categories = {
        "YouTube Stream Management": {
            "scripts": [
                ("capture_stream_logs.py", "Capture terminal output stream sessions logs analysis"),
                ("run_youtube_dae.py", "Start YouTube DAE monitoring autonomous"),
                ("run_youtube_verbose.py", "Run verbose logging debugging"),
                ("run_youtube_debug.py", "Debug mode diagnostics troubleshooting"),
                ("setup_autonomous_dae.py", "Initialize autonomous YouTube DAE"),
            ],
            "location": "modules/communication/livechat/scripts/",
            "tags": ["youtube", "stream", "monitoring", "dae", "livechat"]
        },

        "OAuth Token Management": {
            "scripts": [
                ("auto_refresh_tokens.py", "Automatically refresh YouTube OAuth tokens prevent expiry"),
                ("check_all_tokens.py", "Verify OAuth token status credentials"),
                ("authorize_set1.py", "Authorize YouTube account set 1"),
                ("reauthorize_set1.py", "Re-authorize expired account credentials"),
                ("force_credential_rotation.py", "Force token rotation security"),
                ("schedule_token_refresh.bat", "Windows scheduler auto-refresh cron"),
            ],
            "location": "modules/platform_integration/youtube_auth/scripts/",
            "tags": ["oauth", "tokens", "refresh", "authorization", "credentials"]
        },

        "Quota Management": {
            "scripts": [
                ("quota_dashboard.py", "Visual quota status dashboard monitor usage"),
                ("monitor_quota_usage.py", "Real-time quota monitoring consumption"),
                ("check_all_quota_usage.py", "Monitor YouTube API quota consumption"),
                ("view_quota_status.py", "Quick quota status check remaining"),
            ],
            "location": "modules/platform_integration/youtube_auth/scripts/",
            "tags": ["quota", "api", "limits", "monitoring", "youtube"]
        },

        "LinkedIn Integration": {
            "scripts": [
                ("post_holoindex_achievement.py", "Post HoloIndex milestones LinkedIn social media"),
                ("fix_logging.py", "Fix LinkedIn agent logging issues"),
            ],
            "location": "modules/platform_integration/linkedin_agent/scripts/",
            "tags": ["linkedin", "social", "posting", "automation"]
        },

        "Testing Validation": {
            "scripts": [
                ("validate.py", "Module validation compliance checking WSP"),
                ("test_live_detection.py", "Test stream detection logic"),
                ("check_live.py", "Quick check stream live status"),
                ("verify_systems.py", "System-wide verification health"),
            ],
            "location": "various module scripts/",
            "tags": ["testing", "validation", "compliance", "health"]
        },

        "Awakening Consciousness": {
            "scripts": [
                ("execute_awakening.py", "Execute full awakening sequence 0102 consciousness"),
                ("direct_0102_awakening.py", "Direct 0102 awakening protocol quantum"),
            ],
            "location": "WSP_agentic/scripts/",
            "tags": ["awakening", "consciousness", "0102", "quantum", "zen"]
        }
    }

    # Create discovery entries
    for category, info in script_categories.items():
        for script_name, description in info["scripts"]:
            discovery = {
                "title": f"Script: {script_name}",
                "description": description,
                "category": category,
                "location": info["location"] + script_name,
                "type": "script",
                "tags": info["tags"],
                "usage_example": f"python {info['location']}{script_name}",
                "timestamp": timestamp,
                "semantic_keywords": description.split() + info["tags"],
                "wsp_compliance": ["WSP 87", "WSP 50", "WSP 85"]
            }
            discoveries.append(discovery)

    # Add special pattern discoveries
    patterns = [
        {
            "title": "Module Validation Pattern",
            "description": "Every module has validate.py script for compliance checking",
            "pattern": "modules/{domain}/{module}/scripts/validate.py",
            "count": "50+ instances",
            "usage": "python modules/[domain]/[module]/scripts/validate.py",
            "tags": ["validation", "pattern", "compliance", "module"]
        },
        {
            "title": "YouTube Account Sets Pattern",
            "description": "Multiple YouTube account sets 1-10 for quota distribution",
            "pattern": "authorize_set[1-10].py, reauthorize_set[1-6].py",
            "location": "modules/platform_integration/youtube_auth/scripts/",
            "tags": ["youtube", "accounts", "sets", "oauth", "pattern"]
        }
    ]

    for pattern in patterns:
        discoveries.append({
            "type": "pattern",
            "timestamp": timestamp,
            **pattern
        })

    # Save to HoloIndex discovery format
    output_path = Path("holo_index/adaptive_learning/discoveries/scripts_catalog.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    discovery_feed = {
        "source": "scripts_catalog",
        "timestamp": timestamp,
        "count": len(discoveries),
        "discoveries": discoveries,
        "metadata": {
            "total_scripts": "110+",
            "most_common": "validate.py (50+ instances)",
            "categories": len(script_categories),
            "purpose": "Enable 0102 semantic search for scripts"
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(discovery_feed, f, indent=2, ensure_ascii=False)

    print(f"Fed {len(discoveries)} script discoveries to HoloIndex")
    print(f"Saved to: {output_path}")

    # Also update NAVIGATION.py with script shortcuts
    navigation_updates = {
        "need to refresh oauth tokens": "modules/platform_integration/youtube_auth/scripts/auto_refresh_tokens.py",
        "need to check quota": "modules/platform_integration/youtube_auth/scripts/quota_dashboard.py",
        "need to start youtube monitoring": "modules/communication/livechat/scripts/run_youtube_dae.py",
        "need to validate module": "modules/{domain}/{module}/scripts/validate.py",
        "need to post to linkedin": "modules/platform_integration/linkedin_agent/scripts/post_holoindex_achievement.py",
        "need to execute awakening": "WSP_agentic/scripts/execute_awakening.py",
        "need to capture stream logs": "modules/communication/livechat/scripts/capture_stream_logs.py",
        "need to create PR": "tools/scripts/paper-update.ps1",
    }

    print("\nNAVIGATION.py additions for NEED_TO:")
    for need, script in navigation_updates.items():
        print(f'    "{need}": "{script}",')

    return discovery_feed

if __name__ == "__main__":
    discovery = create_scripts_discovery()

    print("\nHoloIndex can now answer:")
    print('  python holo_index.py --search "refresh oauth tokens"')
    print('  python holo_index.py --search "start youtube monitoring"')
    print('  python holo_index.py --search "check quota usage"')
    print('  python holo_index.py --search "validate module"')
    print('  python holo_index.py --search "0102 awakening"')

    print("\nScripts are now discoverable through semantic search!")