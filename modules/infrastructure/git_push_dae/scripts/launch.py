#!/usr/bin/env python3
"""
Git Push DAE Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch GitPushDAE daemon with WSP 91 full observability
Domain: infrastructure
Module: git_push_dae
"""

import sys
import time
import traceback


def launch_git_push_dae():
    """
    Launch GitPushDAE daemon with WSP 91 full observability.
    Transforms git push from human-triggered action to autonomous DAE.
    """
    print("\n" + "="*60)
    print("[MENU] GIT PUSH DAE - AUTONOMOUS DEVELOPMENT")
    print("="*60)
    print("WSP 91 DAEMON: Fully autonomous git push with observability")
    print("No human decision required - agentic parameters drive decisions")
    print("="*60)

    try:
        # Import and launch the GitPushDAE
        print("[DEBUG-MAIN] About to import GitPushDAE module...")
        from modules.infrastructure.git_push_dae.src.git_push_dae import GitPushDAE
        print("[DEBUG-MAIN] GitPushDAE module imported successfully")

        # Create and start the daemon
        print("[DEBUG-MAIN] Creating GitPushDAE instance...")
        dae = GitPushDAE(domain="foundups_development", check_interval=300)  # 5-minute checks
        print("[DEBUG-MAIN] GitPushDAE instance created, starting daemon...")
        dae.start()
        print("[DEBUG-MAIN] GitPushDAE daemon started")

        print("\n[INFO]GitPushDAE launched successfully!")
        print("[INFO] Monitor logs at: logs/git_push_dae.log")
        print("[INFO] Press Ctrl+C to stop the daemon")

        try:
            # Keep running until interrupted
            while dae.active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Stopping GitPushDAE...")
            dae.stop()

    except ImportError as e:
        print(f"[ERROR]Failed to import GitPushDAE: {e}")
        print("GitPushDAE module not available")
        traceback.print_exc()

    except Exception as e:
        print(f"[ERROR]GitPushDAE failed: {e}")
        traceback.print_exc()
        input("\nPress Enter to continue...")

    finally:
        # Flush stdout/stderr to prevent "lost sys.stderr" errors
        # when returning to menu (WSP 90 UTF-8 enforcement cleanup)
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except:
            pass


if __name__ == "__main__":
    launch_git_push_dae()
