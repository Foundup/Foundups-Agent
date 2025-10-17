#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server Configuration Setup for Claude Code
================================================

Automatically configures all 5 MCP servers in Claude Code:
- 4 FoundUps custom servers (HoloIndex, CodeIndex, WSP Governance, YouTube DAE)
- 1 Official Playwright server (browser automation)

Usage:
    python setup_mcp_servers.py

WSP Compliance:
    - WSP 96: MCP Governance and Consensus Protocol
    - WSP 22: Traceable Narrative Protocol
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===

import json
import os
from pathlib import Path
import shutil

def get_claude_config_path():
    """Get the Claude Code configuration file path"""
    if sys.platform.startswith('win'):
        # Windows: %APPDATA%\Claude\claude_desktop_config.json
        appdata = os.environ.get('APPDATA')
        if not appdata:
            raise RuntimeError("APPDATA environment variable not found")
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        # Linux: ~/.config/Claude/claude_desktop_config.json
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def backup_config(config_path: Path) -> Path:
    """Create backup of existing config"""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print(f"[BACKUP] Created backup: {backup_path}")
        return backup_path
    return None


def get_repo_root() -> Path:
    """Get repository root directory"""
    return Path(__file__).parent.parent.resolve()


def get_python_executable() -> Path:
    """Get the Python executable from foundups-mcp-env"""
    repo_root = get_repo_root()
    if sys.platform.startswith('win'):
        python_exe = repo_root / "foundups-mcp-p1" / "foundups-mcp-env" / "Scripts" / "python.exe"
    else:
        python_exe = repo_root / "foundups-mcp-p1" / "foundups-mcp-env" / "bin" / "python"

    if not python_exe.exists():
        raise RuntimeError(f"Python executable not found: {python_exe}")

    return python_exe


def create_mcp_config() -> dict:
    """Create MCP server configuration"""
    repo_root = get_repo_root()
    python_exe = str(get_python_executable())

    # Convert Windows paths to forward slashes for JSON
    repo_root_str = str(repo_root).replace('\\', '/')
    python_exe = python_exe.replace('\\', '/')

    config = {
        "mcpServers": {
            "holo_index": {
                "command": python_exe,
                "args": [
                    f"{repo_root_str}/foundups-mcp-p1/servers/holo_index/server.py"
                ],
                "env": {
                    "REPO_ROOT": repo_root_str,
                    "HOLO_INDEX_PATH": "E:/HoloIndex"
                }
            },
            "codeindex": {
                "command": python_exe,
                "args": [
                    f"{repo_root_str}/foundups-mcp-p1/servers/codeindex/server.py"
                ],
                "env": {
                    "REPO_ROOT": repo_root_str
                }
            },
            "wsp_governance": {
                "command": python_exe,
                "args": [
                    f"{repo_root_str}/foundups-mcp-p1/servers/wsp_governance/server.py"
                ],
                "env": {
                    "REPO_ROOT": repo_root_str,
                    "WSP_FRAMEWORK_PATH": f"{repo_root_str}/WSP_framework"
                }
            },
            "youtube_dae_gemma": {
                "command": python_exe,
                "args": [
                    f"{repo_root_str}/foundups-mcp-p1/servers/youtube_dae_gemma/server.py"
                ],
                "env": {
                    "REPO_ROOT": repo_root_str
                }
            },
            "playwright": {
                "command": "npx",
                "args": [
                    "-y",
                    "@playwright/mcp-server"
                ],
                "env": {}
            }
        }
    }

    return config


def merge_configs(existing: dict, new: dict) -> dict:
    """Merge existing config with new MCP servers"""
    # Start with existing config
    merged = existing.copy()

    # Add or update mcpServers section
    if "mcpServers" not in merged:
        merged["mcpServers"] = {}

    # Merge MCP servers
    merged["mcpServers"].update(new["mcpServers"])

    return merged


def setup_mcp_servers():
    """Main setup function"""
    print("=" * 60)
    print("FoundUps MCP Server Configuration Setup")
    print("=" * 60)
    print()

    try:
        # Get Claude config path
        config_path = get_claude_config_path()
        print(f"[CONFIG] Claude config path: {config_path}")

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new
        if config_path.exists():
            print(f"[FOUND] Existing config found")
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

            # Backup existing config
            backup_path = backup_config(config_path)
        else:
            print(f"[NEW] Creating new config")
            existing_config = {}

        # Create MCP server config
        print()
        print("[GENERATE] Generating MCP server configuration...")
        mcp_config = create_mcp_config()

        # Merge configurations
        final_config = merge_configs(existing_config, mcp_config)

        # Write config
        print(f"[WRITE] Writing configuration to: {config_path}")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(final_config, f, indent=2)

        print()
        print("[SUCCESS] MCP servers configured successfully!")
        print()
        print("Configured servers:")
        for server_name in mcp_config["mcpServers"].keys():
            print(f"  - {server_name}")

        print()
        print("[NEXT STEPS]")
        print("1. Restart Claude Code completely")
        print("2. Check 'Manage MCP Servers' - you should see 5 servers running")
        print("3. Test with: /mcp")
        print()
        print("[0102 AUTONOMOUS BROWSER OPTIONS]")
        print("  Selenium Tools (via holo_index):")
        print("    - post_to_linkedin_via_selenium (with Gemini vision)")
        print("    - post_to_x_via_selenium (with training data)")
        print("  Playwright Tools (via playwright):")
        print("    - mcp__playwright__navigate (fast navigation)")
        print("    - mcp__playwright__screenshot (lightweight)")
        print("    - mcp__playwright__click (precise interaction)")
        print("  → 0102 can now choose based on task requirements!")
        print()

        # Show config preview
        print("[CONFIG PREVIEW]")
        print(json.dumps(mcp_config, indent=2))

    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(setup_mcp_servers())
