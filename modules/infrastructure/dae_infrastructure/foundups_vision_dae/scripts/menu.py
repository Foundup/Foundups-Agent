#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vision Control Center - Interactive Menu for Vision DAE Management

Provides a centralized control interface for:
- Starting/stopping Vision DAE daemon
- Viewing worker checkpoint state
- Accessing MCP server endpoints (summaries, events)
- Managing UI-TARS dispatch logs

WSP Compliance: WSP 77 (Agent Coordination), WSP 72 (Module Independence)
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.infrastructure.dae_infrastructure.foundups_vision_dae.mcp.vision_mcp_server import VisionMCPServer
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.scripts.launch import run_vision_dae


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def show_vision_control_center():
    """Main Vision Control Center menu loop"""
    server = VisionMCPServer()

    while True:
        print_header("Vision Control Center")
        print("1. 🚀 Start Vision DAE Daemon")
        print("2. 🛑 Stop Daemon / Show Worker Checkpoint State")
        print("3. 📊 View Latest Summary (MCP: get_latest_summary)")
        print("4. 📡 Stream Recent Events (MCP: stream_events)")
        print("5. 📂 Show UI-TARS Dispatch Log Directory")
        print("6. 🔍 List Recent Summaries (MCP: list_recent_summaries)")
        print("7. 💾 Show Worker State (MCP: get_worker_state)")
        print("8. 🧹 Cleanup Old Files (summaries/dispatches)")
        print("0. ◀️  Return to Main Menu")
        print("=" * 60)

        try:
            choice = input("\n👁️  Vision Control Center > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT] Returning to main menu...")
            break

        if choice == "1":
            # Start Vision DAE daemon
            print_header("Starting Vision DAE Daemon")
            print("[INFO] Launching Vision DAE...")
            print("[INFO] Daemon will monitor browser telemetry and generate summaries")
            print("[INFO] Press Ctrl+C to stop the daemon")
            print()
            try:
                run_vision_dae()
            except KeyboardInterrupt:
                print("\n[STOP] Vision DAE stopped by 012")
            except Exception as e:
                print(f"[ERROR] Daemon failed: {e}")

            input("\nPress Enter to return to Vision Control Center...")

        elif choice == "2":
            # Show worker checkpoint state
            print_header("Worker Checkpoint State")
            result = server.get_worker_state()

            if result["success"]:
                state = result["worker_state"]
                timestamp = result.get("checkpoint_timestamp")

                print(f"📌 Browser Offset:    {state['browser_offset']:,} bytes")
                print(f"📌 Batch Index:       {state['batch_index']}")
                print(f"📌 Last Session ID:   {state['last_session_id']}")

                if timestamp:
                    print(f"📌 Last Updated:      {timestamp}")
                else:
                    print(f"📌 Last Updated:      Never (fresh start)")

                print("\nℹ️  Worker can resume from these checkpoints on restart")
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")

            input("\nPress Enter to continue...")

        elif choice == "3":
            # View latest summary
            print_header("Latest Run History Summary")
            result = server.get_latest_summary()

            if result["success"]:
                summary = result["summary"]
                source = result["source"]
                timestamp = result.get("timestamp", "Unknown")

                print(f"📁 Source:           {source}")
                print(f"🕐 Timestamp:        {timestamp}")
                print(f"📊 Session Count:    {summary.get('raw_session_count', 'N/A')}")
                print(f"📅 Timespan:         {summary.get('timespan_days', 'N/A')} days")

                if summary.get('aggregates'):
                    agg = summary['aggregates']
                    print(f"\n📈 Aggregates:")
                    for key, value in agg.items():
                        print(f"   • {key}: {value}")

                if summary.get('patterns'):
                    print(f"\n🔍 Patterns Detected:")
                    for pattern in summary['patterns']:
                        print(f"   • {pattern}")

                print(f"\n💾 File Size:        {result.get('size_bytes', 0):,} bytes")
                print(f"📂 Location:         {result.get('file_path', 'N/A')}")
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")
                if result.get('checked_paths'):
                    print("\nSearched locations:")
                    for path in result['checked_paths']:
                        print(f"   • {path}")

            input("\nPress Enter to continue...")

        elif choice == "4":
            # Stream recent events
            print_header("Stream Telemetry Events")

            # Ask for limit
            limit_input = input("Enter number of events to show (default 10): ").strip()
            try:
                limit = int(limit_input) if limit_input else 10
            except ValueError:
                limit = 10

            result = server.stream_events(limit=limit)

            if result["success"]:
                events = result["events"]
                session_index = result["session_index"]

                print(f"\n📡 Session Bundle:   #{session_index:05d}")
                print(f"📊 Events Returned:  {len(events)}")
                print(f"📂 Source File:      {result['session_file']}")
                print("\n" + "-" * 60)

                if events:
                    for i, event in enumerate(events, 1):
                        print(f"\nEvent #{i}:")
                        # Pretty print event JSON
                        event_json = json.dumps(event, indent=2)
                        for line in event_json.split('\n'):
                            print(f"  {line}")

                        if i < len(events):
                            print("-" * 60)
                else:
                    print("No events in this session bundle")
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")
                if result.get('session_dir'):
                    print(f"Telemetry directory: {result['session_dir']}")

            input("\nPress Enter to continue...")

        elif choice == "5":
            # Show UI-TARS dispatch directory
            print_header("UI-TARS Dispatch Log Directory")

            dispatch_dir = server.ui_tars_dispatches_dir

            print(f"📂 Location: {dispatch_dir}")

            if dispatch_dir.exists():
                dispatch_files = list(dispatch_dir.glob("*.json"))

                print(f"📊 Total Files: {len(dispatch_files)}")

                if dispatch_files:
                    print("\n📋 Recent Dispatches:")
                    # Sort by modification time, most recent first
                    dispatch_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

                    for i, file in enumerate(dispatch_files[:10], 1):
                        size_kb = file.stat().st_size / 1024
                        print(f"   {i}. {file.name} ({size_kb:.1f} KB)")

                    if len(dispatch_files) > 10:
                        print(f"   ... and {len(dispatch_files) - 10} more")
                else:
                    print("\n✨ Directory is empty (no dispatches yet)")
            else:
                print("\n⚠️  Directory does not exist yet")
                print("    Will be created when first dispatch occurs")

            input("\nPress Enter to continue...")

        elif choice == "6":
            # List recent summaries
            print_header("Recent Run History Summaries")

            # Ask for limit
            limit_input = input("Enter number of summaries to show (default 5): ").strip()
            try:
                limit = int(limit_input) if limit_input else 5
            except ValueError:
                limit = 5

            result = server.list_recent_summaries(limit=limit)

            if result["success"]:
                summaries = result["summaries"]
                total = result["total_found"]

                print(f"\n📊 Total Summaries:  {total}")
                print(f"📋 Showing:          {len(summaries)}")
                print("\n" + "-" * 60)

                if summaries:
                    for i, summary in enumerate(summaries, 1):
                        size_kb = summary['size_bytes'] / 1024
                        print(f"\n{i}. {summary['filename']}")
                        print(f"   📅 Timestamp:     {summary['timestamp']}")
                        print(f"   📊 Sessions:      {summary['session_count']}")
                        print(f"   ⏱️  Timespan:      {summary['timespan_days']} days")
                        print(f"   💾 Size:          {size_kb:.1f} KB")
                        print(f"   📁 Source:        {summary['source']}")
                else:
                    print("No summaries found")
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")

            input("\nPress Enter to continue...")

        elif choice == "7":
            # Show worker state (same as option 2 but different presentation)
            print_header("Worker Checkpoint State (Detailed)")
            result = server.get_worker_state()

            if result["success"]:
                state = result["worker_state"]
                files = result.get("checkpoint_files", {})

                print("📌 Current Worker State:")
                print(f"   • Browser Offset:    {state['browser_offset']:,} bytes")
                print(f"   • Batch Index:       {state['batch_index']}")
                print(f"   • Last Session ID:   {state['last_session_id']}")

                print("\n📂 Checkpoint Files:")
                for key, path in files.items():
                    file_path = Path(path)
                    if file_path.exists():
                        print(f"   ✅ {file_path}")
                    else:
                        print(f"   ❌ {file_path} (not yet created)")

                if result.get("checkpoint_timestamp"):
                    print(f"\n🕐 Last Update: {result['checkpoint_timestamp']}")
                else:
                    print(f"\n🕐 Last Update: Never (fresh start)")
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")

            input("\nPress Enter to continue...")

        elif choice == "8":
            # Cleanup old files
            print_header("Cleanup Old Files")

            print("1. Cleanup summaries (30-day retention)")
            print("2. Cleanup dispatches (14-day retention)")
            print("3. Cleanup both")
            print("0. Cancel")

            cleanup_choice = input("\nSelect cleanup option: ").strip()

            if cleanup_choice == "1":
                print("\n[INFO] Cleaning old summaries (>30 days)...")
                result = server.cleanup_old_summaries(days_to_keep=30)

                if result["success"]:
                    print(f"✅ Deleted {result['deleted_count']} file(s)")
                    print(f"✅ Kept {result['kept_count']} file(s)")
                else:
                    print(f"[ERROR] {result.get('error', 'Unknown error')}")

            elif cleanup_choice == "2":
                print("\n[INFO] Cleaning old dispatches (>14 days)...")
                result = server.cleanup_old_dispatches(days_to_keep=14)

                if result["success"]:
                    print(f"✅ Deleted {result['deleted_count']} file(s)")
                    print(f"✅ Kept {result['kept_count']} file(s)")
                else:
                    print(f"[ERROR] {result.get('error', 'Unknown error')}")

            elif cleanup_choice == "3":
                print("\n[INFO] Cleaning old summaries (>30 days)...")
                result1 = server.cleanup_old_summaries(days_to_keep=30)

                print("\n[INFO] Cleaning old dispatches (>14 days)...")
                result2 = server.cleanup_old_dispatches(days_to_keep=14)

                if result1["success"] and result2["success"]:
                    total_deleted = result1['deleted_count'] + result2['deleted_count']
                    total_kept = result1['kept_count'] + result2['kept_count']
                    print(f"\n✅ Total Deleted: {total_deleted} file(s)")
                    print(f"✅ Total Kept: {total_kept} file(s)")
                else:
                    if not result1["success"]:
                        print(f"[ERROR] Summaries: {result1.get('error', 'Unknown error')}")
                    if not result2["success"]:
                        print(f"[ERROR] Dispatches: {result2.get('error', 'Unknown error')}")

            input("\nPress Enter to continue...")

        elif choice == "0":
            print("[EXIT] Returning to main menu...")
            break

        else:
            print(f"[ERROR] Invalid choice '{choice}'. Please select 0-8.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("[INFO] Vision Control Center - Standalone Mode")
    show_vision_control_center()
