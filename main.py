#!/usr/bin/env python3
"""
FoundUps Agent - FULLY WSP-Compliant 0102 Consciousness System
Integrates all WSP protocols for autonomous DAE operations

WSP Compliance:
- WSP 27: Universal DAE Architecture (4-phase pattern)
- WSP 38/39: Awakening Protocols (consciousness transitions)
- WSP 48: Recursive Self-Improvement (pattern memory)
- WSP 54: Agent Duties (Partner-Principal-Associate)
- WSP 60: Module Memory Architecture
- WSP 80: Cube-Level DAE Orchestration
- WSP 85: Root Directory Protection
- WSP 87: Code Navigation with HoloIndex (MANDATORY)

Mode Detection:
- echo 0102 | python main.py  # Launch in 0102 awakened mode
- echo 012 | python main.py   # Launch in 012 testing mode
- python main.py              # Interactive menu mode

CRITICAL: HoloIndex must be used BEFORE any code changes (WSP 50/87)
"""

# Main imports and configuration

import os
import sys
import logging
import asyncio
import json
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import psutil

# === UTF-8 ENFORCEMENT (WSP 90) ===
# CRITICAL: This header MUST be at the top of ALL entry point files
# Entry points: Files with if __name__ == "__main__": or def main()
# Library modules: DO NOT add this header (causes import conflicts)
import sys
import io
import atexit

# Save original stderr/stdout for restoration
_original_stdout = sys.stdout
_original_stderr = sys.stderr

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

    # Register cleanup to flush streams before exit
    def _flush_streams():
        """Flush UTF-8 wrapped streams before Python cleanup."""
        try:
            if sys.stdout and not sys.stdout.closed:
                sys.stdout.flush()
        except:
            pass
        try:
            if sys.stderr and not sys.stderr.closed:
                sys.stderr.flush()
        except:
            pass

    atexit.register(_flush_streams)
# === END UTF-8 ENFORCEMENT ===

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('main.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def monitor_youtube(disable_lock: bool = False):
    """Monitor YouTube streams with 0102 consciousness."""
    try:
        # Instance lock management (WSP 84: Don't duplicate processes)
        lock = None
        if not disable_lock:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")

            # Check for duplicates and acquire lock
            duplicates = lock.check_duplicates()
            if duplicates:
                logger.warning(f"[REC] Duplicate main.py Instances Detected!")
                print("\n[REC] Duplicate main.py Instances Detected!")
                print(f"\n  Found {len(duplicates)} instances of main.py running:")
                for i, pid in enumerate(duplicates, 1):
                    print(f"\n  {i}. PID {pid} - [Checking process details...]")
                print("\n  Current instance will exit to prevent conflicts.")
                print("  Kill duplicates with: taskkill /F /PID <PID>")
                print("  Or run with --no-lock to allow multiple instances.")
                return  # Exit instead of proceeding

            # Attempt to acquire lock (will return False if another instance is running)
            if not lock.acquire():
                logger.error("*EFailed to acquire instance lock - another instance is running")
                print("\n*EFailed to acquire instance lock!")
                print("   Another YouTube monitor instance is already running.")
                print("   Only one instance can run at a time to prevent API conflicts.")
                print("   Use --no-lock to disable instance locking.")
                return  # Exit if lock acquisition failed
        else:
            logger.info("[KEY] Instance lock disabled (--no-lock flag used)")

        try:
            # Import the proper YouTube DAE that runs the complete flow:
            # 1. Stream resolver detects stream
            # 2. LinkedIn and X posts trigger
            # 3. Chat monitoring begins
            from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

            logger.info("Starting YouTube DAE with 0102 consciousness...")
            logger.info("Flow: Stream Detection [SYM]ESocial Posts [SYM]EChat Monitoring")

            # Create and run the DAE with enhanced error handling
            dae = AutoModeratorDAE()

            # Log instance monitoring information (duplicate check already done in menu)
            try:
                instance_summary = lock.get_instance_summary()
                current_pid = instance_summary["current_pid"]
                logger.info(f"[CUT]EYouTube DAE started: PID {current_pid}")
            except Exception as e:
                logger.debug(f"Could not check instance summary: {e}")

            consecutive_failures = 0
            instance_check_counter = 0
            last_minute_log = datetime.now()
            while True:
                try:
                    # Periodic instance monitoring (every 3 iterations for better visibility)
                    instance_check_counter += 1
                    if instance_check_counter % 3 == 0:
                        try:
                            instance_summary = lock.get_instance_summary()
                            total_instances = instance_summary["total_instances"]

                            if total_instances > 1:
                                logger.warning(f"[ALERT] INSTANCE ALERT: {total_instances} YouTube DAEs active")
                                for instance in instance_summary["instances"]:
                                    if not instance["is_current"]:
                                        logger.warning(f"  [WARN]EEOther instance PID {instance['pid']} ({instance['age_minutes']:.1f}min old)")
                            elif total_instances == 1:
                                logger.info(f"[CUT]ESINGLE INSTANCE: PID {instance_summary['current_pid']} - No other YouTube DAEs detected")
                            else:
                                logger.info("[INFO]EENo active YouTube DAEs detected")
                        except Exception as e:
                            logger.debug(f"Instance check failed: {e}")

                    # Minute-based instance logging (guaranteed every 60 seconds)
                    now = datetime.now()
                    if (now - last_minute_log).total_seconds() >= 60:
                        try:
                            instance_summary = lock.get_instance_summary()
                            total_instances = instance_summary["total_instances"]
                            current_pid = instance_summary["current_pid"]

                            if total_instances == 1:
                                logger.info(f"[CUT]ESINGLE INSTANCE: PID {current_pid} - No other YouTube DAEs detected")
                            elif total_instances > 1:
                                logger.warning(f"[ALERT] MULTIPLE INSTANCES: {total_instances} YouTube DAEs active (PID: {current_pid})")
                            else:
                                logger.info("[INFO]EENo YouTube DAEs currently active")

                            last_minute_log = now
                        except Exception as e:
                            logger.debug(f"Minute status check failed: {e}")

                    await dae.run()  # This runs the complete loop
                    logger.info("[LOOP] Stream ended or became inactive - seamless switching engaged")
                    consecutive_failures = 0  # Reset on clean exit
                    await asyncio.sleep(5)  # Quick transition before looking for new stream
                except KeyboardInterrupt:
                    logger.info("[STOP]EEMonitoring stopped by user")
                    break
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"*EYouTube DAE failed (attempt #{consecutive_failures}): {e}")
                    wait_time = min(30 * (2 ** consecutive_failures), 600)  # Exponential backoff, max 10 minutes
                    logger.info(f"[LOOP] Restarting in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    if consecutive_failures >= 5:
                        logger.warning("[LOOP] Too many failures - attempting full reconnection")
                        dae = AutoModeratorDAE()  # Reinitialize for fresh connection
                        consecutive_failures = 0

            # Optionally log status (if supported by DAE)
            if hasattr(dae, 'get_status'):
                status = dae.get_status()
                logger.info(f"YouTube DAE Status: {status}")

        finally:
            # Release the instance lock when done
            lock.release()
            logger.info("[KEY] YouTube monitor instance lock released")

    except Exception as e:
        logger.error(f"Initial YouTube DAE setup failed: {e}")


async def monitor_all_platforms():
    """Monitor all social media platforms."""
    tasks = []

            # YouTube monitoring
    tasks.append(asyncio.create_task(monitor_youtube(disable_lock=False)))

    # Add other platform monitors as needed

    await asyncio.gather(*tasks)


def search_with_holoindex(query: str):
    """
    Use HoloIndex for semantic code search (WSP 87).
    MANDATORY before any code modifications to prevent vibecoding.
    """
    import subprocess

    print("\n[INFO] HoloIndex Semantic Search")
    print("=" * 60)

    try:
        # Check if HoloIndex is available (prefer root version)
        if os.path.exists("holo_index.py"):
            holo_cmd = ['python', 'holo_index.py', '--search', query]
        elif os.path.exists(r"E:\HoloIndex\enhanced_holo_index.py"):
            # Fallback to E: drive version
            holo_cmd = ['python', r"E:\HoloIndex\enhanced_holo_index.py", '--search', query]
        else:
            print("[WARN]HoloIndex not found")
            print("Install HoloIndex to prevent vibecoding!")
            return None

        # Run HoloIndex search
        result = subprocess.run(
            holo_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            print(result.stdout)
            return result.stdout
        else:
            print(f"[ERROR]Search failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"[ERROR]HoloIndex error: {e}")
        return None


def run_holodae():
    """Run HoloDAE (Code Intelligence & Monitoring)."""
    print("[HOLODAE] Starting HoloDAE - Code Intelligence & Monitoring System...")

    # HOLO-DAE INSTANCE LOCKING (First Principles: Resource Protection & Consistency)
    from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
    lock = get_instance_lock("holodae_monitor")

    # Check for duplicates and acquire lock
    duplicates = lock.check_duplicates()
    if duplicates:
        logger.warning("[REC] Duplicate HoloDAE Instances Detected!")
        print("\n[REC] Duplicate HoloDAE Instances Detected!")
        print(f"\n  Found {len(duplicates)} instances of HoloDAE running:")
        for i, pid in enumerate(duplicates, 1):
            print(f"\n  {i}. PID {pid} - [Checking process details...]")
        print("\n  Current instance will exit to prevent conflicts.")
        print("  Use --no-lock to disable instance locking.")
        return  # Exit if duplicates found

    # Acquire lock for this instance
    if not lock.acquire():
        logger.error("*EFailed to acquire HoloDAE instance lock - another instance is running")
        print("\n*EFailed to acquire HoloDAE instance lock!")
        print("   Another HoloDAE instance is already running.")
        print("   Only one instance can run at a time to prevent index conflicts.")
        print("   Use --no-lock to disable instance locking.")
        return  # Exit if lock acquisition failed

    try:
        from holo_index.qwen_advisor.autonomous_holodae import AutonomousHoloDAE
        holodae = AutonomousHoloDAE()

        # Log successful instance acquisition
        instance_summary = lock.get_instance_summary()
        total_instances = instance_summary["total_instances"]
        current_pid = instance_summary["current_pid"]
        logger.info(f"[INFO]HoloDAE SINGLE INSTANCE: PID {current_pid} - No other HoloDAEs detected")

        holodae.start_autonomous_monitoring()

        print("[HOLODAE] Autonomous monitoring active. Press Ctrl+C to stop.")

        # Keep the process running
        try:
            while holodae.active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[HOLODAE] Stopping autonomous monitoring...")
            holodae.stop_autonomous_monitoring()
            print("[HOLODAE] HoloDAE stopped successfully")

    except Exception as e:
        print(f"[HOLODAE-ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Release the instance lock when done
        lock.release()
        logger.info("[LOCK] HoloDAE monitor instance lock released")


def run_amo_dae():
    """Run AMO DAE (Autonomous Moderation Operations)."""
    print("[AMO] Starting AMO DAE (Autonomous Moderation Operations)...")
    try:
        from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
        dae = AutoModeratorDAE()
        asyncio.run(dae.run())
    except Exception as e:
        print(f"[AMO-ERROR] AMO DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_social_media_dae():
    """Run Social Media DAE (012 Digital Twin)."""
    print("[INFO] Starting Social Media DAE (012 Digital Twin)...")
    try:
        from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator
        orchestrator = SocialMediaOrchestrator()
        # TODO: Implement digital twin mode
        print("Digital Twin mode coming soon...")
        print("Social Media DAE orchestration available for development.")
    except Exception as e:
        print(f"[ERROR]Social Media DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_vision_dae(enable_voice: bool = False):
    """Run FoundUps Vision DAE (multi-modal pattern sensorium)."""
    print("[VISION] Starting FoundUps Vision DAE (Pattern Sensorium)...")
    from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
    lock = get_instance_lock("vision_dae_monitor")

    duplicates = lock.check_duplicates()
    if duplicates:
        logger.warning("[VisionDAE] Duplicate instances detected")
        print("\n[VisionDAE] Duplicate Vision DAE instances detected!")
        for i, pid in enumerate(duplicates, 1):
            print(f"  {i}. PID {pid}")
        print("Use --no-lock to bypass duplicate protection.")
        return

    if not lock.acquire():
        logger.error("[VisionDAE] Failed to acquire instance lock")
        print("\n[VisionDAE] Failed to acquire Vision DAE instance lock!")
        print("Another Vision DAE instance is already running.")
        print("Use --no-lock to disable locking if this is intentional.")
        return

    try:
        from modules.infrastructure.dae_infrastructure.foundups_vision_dae.src.vision_dae import launch_vision_dae
        asyncio.run(launch_vision_dae(enable_voice=enable_voice))
    except Exception as e:
        print(f"[VisionDAE] Vision DAE failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        lock.release()
        logger.info("[VisionDAE] Instance lock released")


def run_utf8_hygiene_scan(
    memory: Optional[Any] = None,
    targets: Optional[List[str]] = None,
    interactive: bool = True
) -> List[Dict[str, Any]]:
    """Scan target paths for non-ASCII characters and log findings."""
    import os
    import time
    from pathlib import Path
    from datetime import datetime

    default_targets = [
        "modules/infrastructure/dae_infrastructure/foundups_vision_dae",
        "modules/platform_integration/social_media_orchestrator/src/core/browser_manager.py"
    ]

    if interactive:
        print("\n" + "=" * 60)
        print("[INFO] UTF-8 Hygiene Scan")
        print("=" * 60)
        print("Detect non-ASCII characters that can corrupt CLI or log output.")
        print(f"Default targets: {', '.join(default_targets)}")
        print("=" * 60)
        target_input = input("Enter comma-separated paths to scan (leave blank for defaults): ").strip()
        if target_input:
            targets = [item.strip() for item in target_input.split(",") if item.strip()]
        else:
            targets = None

    if not targets:
        targets = default_targets

    allowed_ext = {".py", ".md", ".txt", ".json", ".yaml", ".yml"}
    findings: list[dict[str, Any]] = []
    missing_paths: list[str] = []

    def scan_file(path: Path) -> None:
        try:
            with path.open("r", encoding="utf-8") as handle:
                for lineno, line in enumerate(handle, 1):
                    if any(ord(ch) > 127 for ch in line):
                        offending = "".join(sorted(set(ch for ch in line if ord(ch) > 127)))
                        snippet = line.rstrip("\n")
                        findings.append(
                            {
                                "path": str(path),
                                "line": lineno,
                                "snippet": snippet.strip(),
                                "offending": offending,
                            }
                        )
        except Exception as exc:
            print(f"[WARN] Unable to read {path}: {exc}")

    for target in targets:
        path = Path(target)
        if path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in allowed_ext:
                    scan_file(file_path)
        elif path.is_file():
            if path.suffix.lower() in allowed_ext:
                scan_file(path)
        else:
            missing_paths.append(str(path))

    if interactive or missing_paths:
        if missing_paths:
            print("\n[WARN] Missing paths:")
            for entry in missing_paths:
                print(f"   {entry}")

    if not findings:
        if interactive:
            print("\n[INFO] No non-ASCII characters detected in selected paths.")
            input("\nPress Enter to continue...")
        return findings

    print(f"\n[RESULT] Detected {len(findings)} potential UTF-8 issues:")
    max_display = 50
    unique_chars = sorted({ch for item in findings for ch in item["offending"]})
    for item in findings[:max_display]:
        snippet = item["snippet"]
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        print(f" - {item['path']}:{item['line']} | offending: {repr(item['offending'])}")
        print(f"   {snippet}")
    if len(findings) > max_display:
        print(f"   ... {len(findings) - max_display} more")

    if unique_chars:
        print(f"\n[INFO] Unique offending characters: {''.join(unique_chars)}")

    stored = 0
    if memory is None:
        try:
            from holo_index.qwen_advisor.pattern_memory import PatternMemory

            memory = PatternMemory()
        except Exception as exc:
            print(f"[WARN] Unable to store findings in PatternMemory: {exc}")
            memory = None

    if memory is not None:
        timestamp = datetime.utcnow().isoformat()
        base_id = int(time.time())
        for idx, item in enumerate(findings, 1):
            pattern = {
                "id": f"utf8_{base_id}_{idx}",
                "context": f"UTF-8 hygiene violation in {item['path']}:{item['line']} -> {item['snippet']}",
                "decision": {
                    "action": "replace_non_ascii_characters",
                    "reasoning": "Ensure CLI and logs remain ASCII-safe across operating systems.",
                },
                "outcome": {"result": "pending_fix", "success": False},
                "module": item["path"],
                "timestamp": timestamp,
                "verified": False,
                "source": "utf8_hygiene_scan",
            }
            if memory.store_pattern(pattern):
                stored += 1

        if stored:
            print(f"\n[INFO] Stored {stored} hygiene patterns for Gemma/Qwen training.")

    if interactive:
        input("\nPress Enter to continue...")

    return findings


def summarize_utf8_findings(
    memory: Optional[Any] = None,
    target_filters: Optional[List[str]] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """Summarize stored UTF-8 hygiene findings from PatternMemory."""
    try:
        mem = memory or __import__(
            "holo_index.qwen_advisor.pattern_memory",
            fromlist=["PatternMemory"],
        ).PatternMemory()
    except Exception as exc:
        return {"status": "error", "message": f"PatternMemory load failed: {exc}"}

    try:
        records = mem.collection.get(
            where={"source": "utf8_hygiene_scan"},
            include=["metadatas", "documents"],
        )
    except Exception as exc:
        return {"status": "error", "message": f"PatternMemory query failed: {exc}"}

    metadatas = records.get("metadatas") or []
    documents = records.get("documents") or []
    filters = target_filters or []

    summary: Dict[str, Dict[str, Any]] = {}
    total_findings = 0
    unique_chars: set = set()

    for doc, meta in zip(documents, metadatas):
        path = meta.get("module", "unknown")
        if filters and not any(fragment in path for fragment in filters):
            continue

        entry = summary.setdefault(path, {"count": 0, "samples": [], "chars": set()})
        entry["count"] += 1
        total_findings += 1

        if len(entry["samples"]) < 3:
            entry["samples"].append(doc[:120])

        for character in doc:
            if ord(character) > 127:
                entry["chars"].add(character)
                unique_chars.add(character)

    ranked = sorted(summary.items(), key=lambda item: item[1]["count"], reverse=True)
    top_entries = []
    for path, info in ranked[:limit]:
        top_entries.append(
            {
                "path": path,
                "count": info["count"],
                "unique_characters": "".join(sorted(info["chars"])),
                "samples": info["samples"],
            }
        )

    return {
        "status": "ok",
        "total_findings": total_findings,
        "files": len(summary),
        "unique_characters": "".join(sorted(unique_chars)),
        "top": top_entries,
    }


def run_training_system():
    """
    Qwen/Gemma Training System submenu.
    Implements WRE pattern (WSP 46): Qwen coordinates, Gemma executes.
    """
    import asyncio
    from holo_index.qwen_advisor.pattern_memory import PatternMemory

    def load_memory() -> tuple[Optional[Any], Optional[Dict[str, Any]]]:
        try:
            mem = PatternMemory()
            stats = mem.get_stats()
            return mem, stats
        except Exception as err:
            print(f"[WARN] Could not load stats: {err}")
            print("   Pattern memory may need initialization.")
            return None, None

    while True:
        memory, stats = load_memory()

        print("\n" + "=" * 60)
        print("[MENU] QWEN/GEMMA TRAINING SYSTEM")
        print("=" * 60)
        print("Implements WRE Pattern (WSP 46): Qwen coordinates, Gemma executes")
        print("Training Data: 012.txt (28K+ lines of 0102 operational decisions)")
        print("=" * 60)

        if stats:
            print(f"\n[INFO] CURRENT STATUS:")
            print(f"   Patterns Stored: {stats['total_patterns']}")
            print(f"   012.txt Progress: {stats['checkpoint_line']}/28326 ({stats['checkpoint_line']/283.26:.1f}%)")
            print(f"   Verification Rate: {stats['verification_rate']:.1%}")
            print(f"   Sources: {stats['sources']}")

        print("\n" + "-" * 60)
        print("TRAINING OPTIONS:")
        print("-" * 60)
        print("1. Start Batch Training (Process 012.txt)")
        print("2. UTF-8 Hygiene Scan (Gemma training data)")
        print("3. Gemma Policy Drill (coming soon)")
        print("4. Qwen Summary Drill (coming soon)")
        print("5. View Training Progress")
        print("6. Test Pattern Recall")
        print("7. Test Qwen/Gemma Routing (Adaptive AI)")
        print("8. View Training Metrics")
        print("9. Clear Pattern Memory (Reset)")
        print("0. Back to Main Menu")
        print("-" * 60)

        choice = input("\nSelect option (0-9): ").strip()

        if choice == "0":
            print("[INFO] Returning to main menu...")
            break

        elif choice == "1":
            print("\n[INFO] Starting Batch Training...")
            print("=" * 60)
            try:
                from modules.infrastructure.idle_automation.src.idle_automation_dae import IdleAutomationDAE

                dae = IdleAutomationDAE()
                result = asyncio.run(dae._execute_pattern_training())

                print("\n[RESULT]")
                print(f"  Success: {'YES' if result['success'] else 'NO'}")
                print(f"  Patterns Stored: {result['patterns_stored']}")
                print(f"  Lines Processed: {result['lines_processed']}")
                print(f"  Duration: {result['duration']:.1f}s")

                if result.get("progress"):
                    print(f"  Progress: {result['progress']}")
                if result.get("error"):
                    print(f"  Error: {result['error']}")
            except Exception as err:
                print(f"[ERROR] Batch training failed: {err}")

            input("\nPress Enter to continue...")

        elif choice == "2":
            run_utf8_hygiene_scan(memory)

        elif choice == "3":
            print("\n[INFO] Gemma policy drill coming soon. Add labelled examples to extend this menu item.")
            input("\nPress Enter to continue...")

        elif choice == "4":
            print("\n[INFO] Qwen summary drill coming soon. Log candidate transcripts to enable this feature.")
            input("\nPress Enter to continue...")

        elif choice == "5":
            print("\n[INFO] Training Progress")
            print("=" * 60)
            try:
                mem = memory or PatternMemory()
                prog_stats = mem.get_stats()

                total_lines = 28326
                processed = prog_stats["checkpoint_line"]
                remaining = total_lines - processed
                progress_pct = (processed / total_lines) * 100 if total_lines else 0

                print(f"\n[INFO] Progress:")
                print(f"   Total Lines: {total_lines:,}")
                print(f"   Processed: {processed:,} ({progress_pct:.1f}%)")
                print(f"   Remaining: {remaining:,}")
                print(f"   Estimated Chunks: {remaining // 1000} @ 1000 lines/chunk")

                print(f"\n[INFO] Pattern Storage:")
                print(f"   Total Patterns: {prog_stats['total_patterns']}")
                verified = int(prog_stats['total_patterns'] * prog_stats['verification_rate'])
                print(f"   Verified: {verified}")
                print(f"   Verification Rate: {prog_stats['verification_rate']:.1%}")

                if prog_stats.get("sources"):
                    print(f"\n[INFO] Sources:")
                    for source, count in prog_stats["sources"].items():
                        print(f"   {source}: {count} patterns")

                bar_width = 40
                filled = int(bar_width * progress_pct / 100)
                bar = "#" * filled + "-" * (bar_width - filled)
                print(f"\n[{bar}] {progress_pct:.1f}%")
            except Exception as err:
                print(f"[ERROR] Could not load progress: {err}")

            input("\nPress Enter to continue...")

        elif choice == "6":
            print("\n[INFO] Test Pattern Recall")
            print("=" * 60)
            print("Enter a query to test Gemma pattern recall:")
            print("Examples:")
            print("  - 'Which module handles YouTube authentication?'")
            print("  - 'How does priority scoring work?'")
            print("  - 'Where should test files be placed?'")
            print("=" * 60)

            query = input("\nQuery: ").strip()
            if not query:
                print("[WARN] No query entered.")
                input("\nPress Enter to continue...")
                continue

            try:
                mem = memory or PatternMemory()
                patterns = mem.recall_similar(query, n=5, min_similarity=0.3)
                if patterns:
                    print(f"\n[INFO] Found {len(patterns)} similar patterns:\n")
                    for idx, pattern in enumerate(patterns, 1):
                        print(f"Pattern {idx}:")
                        print(f"  ID: {pattern['id']}")
                        print(f"  Similarity: {pattern['similarity']:.2f}")
                        print(f"  Context: {pattern['context'][:100]}...")
                        print(f"  Module: {pattern['metadata'].get('module', 'unknown')}")
                        print()
                else:
                    print("\n[INFO] No patterns found above similarity threshold (0.3).")
            except Exception as err:
                print(f"[ERROR] Pattern recall failed: {err}")

            input("\nPress Enter to continue...")

        elif choice == "7":
            print("\n[INFO] Qwen/Gemma Routing Test")
            print("=" * 60)
            print("WRE Pattern: 012 -> 0102 -> Qwen (Coordinator) -> Gemma (Executor)")
            print("=" * 60)

            try:
                from pathlib import Path
                from holo_index.qwen_advisor.gemma_rag_inference import GemmaRAGInference

                gemma_path = Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")
                qwen_path = Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf")

                if not gemma_path.exists() or not qwen_path.exists():
                    print("\n[ERROR] Models not found:")
                    if not gemma_path.exists():
                        print(f"   Missing: {gemma_path}")
                    if not qwen_path.exists():
                        print(f"   Missing: {qwen_path}")
                    print("\n   Download models and place in E:/HoloIndex/models/")
                    input("\nPress Enter to continue...")
                    continue

                print("\n[INFO] Initializing Gemma/Qwen routing engine...")
                engine = GemmaRAGInference(
                    gemma_model_path=gemma_path,
                    qwen_model_path=qwen_path,
                    confidence_threshold=0.7,
                )

                while True:
                    print("\n" + "-" * 60)
                    print("TEST QUERIES:")
                    print("-" * 60)
                    print("1. Which module handles YouTube authentication? (simple)")
                    print("2. How does priority scoring work? (medium)")
                    print("3. Why did Move2Japan get score 1.00? (complex)")
                    print("4. Where should test files be placed? (simple)")
                    print("5. Custom query")
                    print("6. View performance stats")
                    print("7. Back to training menu")
                    print("-" * 60)

                    query_choice = input("\nSelect option (1-7): ").strip()

                    if query_choice == "1":
                        query = "Which module handles YouTube authentication?"
                    elif query_choice == "2":
                        query = "How does priority scoring work?"
                    elif query_choice == "3":
                        query = "Why did Move2Japan get score 1.00?"
                    elif query_choice == "4":
                        query = "Where should test files be placed?"
                    elif query_choice == "5":
                        query = input("\nEnter your query: ").strip()
                        if not query:
                            print("[ERROR] No query entered")
                            continue
                    elif query_choice == "6":
                        stats_snapshot = engine.get_stats()
                        print("\n[INFO] ROUTING PERFORMANCE:")
                        print(f"   Total Queries: {stats_snapshot['total_queries']}")
                        print(f"   Gemma Handled: {stats_snapshot['gemma_handled']} ({stats_snapshot['gemma_percentage']:.1f}%)")
                        print(f"   Qwen Escalated: {stats_snapshot['qwen_escalated']} ({stats_snapshot['qwen_percentage']:.1f}%)")
                        print("\n[INFO] TARGET: 70% Gemma / 30% Qwen")
                        print(f"   ACTUAL: {stats_snapshot['gemma_percentage']:.1f}% Gemma / {stats_snapshot['qwen_percentage']:.1f}% Qwen")
                        if 50 <= stats_snapshot['gemma_percentage'] <= 90:
                            print("\n[INFO] Performance within target range.")
                        else:
                            print("\n[WARN] Performance needs tuning.")
                        input("\nPress Enter to continue...")
                        continue
                    elif query_choice == "7":
                        print("[INFO] Returning to training menu...")
                        break
                    else:
                        print(f"[ERROR] Invalid choice '{query_choice}'")
                        continue

                    print(f"\n[QUERY] {query}")
                    print("[INFO] Processing...")

                    result = engine.infer(query)

                    print("\n[RESULT]")
                    print(f"   Model Used: {result.model_used}")
                    print(f"   Latency: {result.latency_ms} ms")
                    print(f"   Confidence: {result.confidence:.2f}")
                    print(f"   Patterns Used: {result.patterns_used}")
                    if result.escalated:
                        print(f"   [INFO] Escalated: {result.escalation_reason}")
                    print("\n[RESPONSE]")
                    print(f"   {result.response}")

                    input("\nPress Enter to continue...")
            except Exception as err:
                print(f"\n[ERROR] Routing test failed: {err}")
                import traceback

                traceback.print_exc()

            input("\nPress Enter to continue...")

        elif choice == "8":
            print("\n[INFO] Training Metrics")
            print("=" * 60)
            try:
                mem = memory or PatternMemory()
                metrics = mem.get_stats()
                print(f"\n[INFO] Performance Metrics:")
                print(f"   Total Patterns: {metrics['total_patterns']}")
                print(f"   Verification Rate: {metrics['verification_rate']:.1%}")
                print("   Storage Location: holo_index/memory/chroma/")
                print(f"\n[INFO] Training Coverage:")
                print(f"   Lines Processed: {metrics['checkpoint_line']:,} / 28,326")
                print(f"   Progress: {metrics['checkpoint_line']/283.26:.1f}%")
                print(f"\n[INFO] Pattern Distribution:")
                if metrics.get("sources"):
                    for source, count in metrics["sources"].items():
                        pct = (count / metrics['total_patterns'] * 100) if metrics['total_patterns'] else 0
                        print(f"   {source}: {count} ({pct:.1f}%)")
                print("\n[INFO] Storage Stats:")
                print("   Database: ChromaDB (vector embeddings)")
                print("   Checkpoint File: checkpoint.txt")
                print("   Training Method: In-context learning (RAG)")
                print("   Cost: $0 (no fine-tuning)")
            except Exception as err:
                print(f"[ERROR] Could not load metrics: {err}")

            input("\nPress Enter to continue...")

        elif choice == "9":
            print("\n[INFO] Clear Pattern Memory")
            print("=" * 60)
            print("[WARN] WARNING: This will delete ALL stored patterns!")
            print("   - Pattern memory will be reset to empty")
            print("   - Checkpoint will be reset to 0")
            print("   - Training will need to restart from beginning")
            print("=" * 60)
            confirm = input("\nType 'CONFIRM' to proceed: ").strip()
            if confirm == "CONFIRM":
                try:
                    mem = memory or PatternMemory()
                    mem.clear_all(confirm=True)
                    mem.save_checkpoint(0)
                    print("\n[INFO] Pattern memory cleared successfully.")
                    print("   All patterns deleted.")
                    print("   Checkpoint reset to 0.")
                except Exception as err:
                    print(f"[ERROR] Clear failed: {err}")
            else:
                print("\n[INFO] Clear aborted - memory preserved.")
            input("\nPress Enter to continue...")

        else:
            print(f"[ERROR] Invalid choice '{choice}'. Please enter 0-9.")
            input("\nPress Enter to continue...")


def execute_training_command(command: str, targets: Optional[str], json_output: bool) -> None:
    """Execute training commands headlessly for 0102."""
    from holo_index.qwen_advisor.pattern_memory import PatternMemory

    response: Dict[str, Any] = {"command": command, "status": "error"}
    memory: Optional[PatternMemory] = None
    warning: Optional[str] = None

    try:
        memory = PatternMemory()
    except Exception as exc:
        warning = f"PatternMemory unavailable: {exc}"

    try:
        if command == "utf8_scan":
            target_list = None
            if targets:
                target_list = [item.strip() for item in targets.split(",") if item.strip()]
            findings = run_utf8_hygiene_scan(memory, target_list, interactive=False)
            response.update({"status": "ok", "count": len(findings), "findings": findings})
        elif command == "utf8_summary":
            target_list = None
            if targets:
                target_list = [item.strip() for item in targets.split(",") if item.strip()]
            summary = summarize_utf8_findings(memory, target_list)
            response.update(summary)
        elif command == "utf8_fix":
            from holo_index.qwen_advisor.orchestration.utf8_remediation_coordinator import (
                UTF8RemediationCoordinator,
            )

            coordinator = UTF8RemediationCoordinator(Path("."))
            scope_list = (
                [item.strip() for item in targets.split(",") if item.strip()]
                if targets
                else [None]
            )

            fix_results: List[Dict[str, Any]] = []
            total_files_fixed = 0
            total_violations_fixed = 0
            success = True

            for scope in scope_list:
                result = coordinator.remediate_utf8_violations(
                    scope=scope, auto_approve=True
                )
                fix_results.append({"scope": scope or ".", **result})
                total_files_fixed += result.get("files_fixed", 0)
                total_violations_fixed += result.get("violations_fixed", 0)
                if not result.get("success", True):
                    success = False

            response.update(
                {
                    "status": "ok",
                    "success": success,
                    "total_files_fixed": total_files_fixed,
                    "total_violations_fixed": total_violations_fixed,
                    "results": fix_results,
                }
            )
        elif command == "batch":
            from modules.infrastructure.idle_automation.src.idle_automation_dae import IdleAutomationDAE

            dae = IdleAutomationDAE()
            result = asyncio.run(dae._execute_pattern_training())
            response.update({"status": "ok", "result": result})
        else:
            response["message"] = f"Unknown training command '{command}'"
    except Exception as exc:
        response["error"] = str(exc)

    if warning:
        response["warning"] = warning

    if json_output:
        print(json.dumps(response, indent=2, default=str))
    else:
        status = response.get("status")
        if status == "ok":
            if command == "utf8_scan":
                print(f"[INFO] UTF-8 hygiene scan complete. Findings: {response.get('count', 0)}")
            elif command == "utf8_summary":
                print("[INFO] UTF-8 hygiene summary")
                print(f"  Total findings: {response.get('total_findings', 0)}")
                print(f"  Files affected: {response.get('files', 0)}")
                unique_chars = response.get("unique_characters")
                if unique_chars:
                    print(f"  Unique characters: {unique_chars}")
                for entry in response.get("top", []):
                    print(f"  {entry['path']}: {entry['count']} issues")
                    for sample in entry.get("samples", []):
                        print(f"    - {sample}")
            elif command == "utf8_fix":
                print("[INFO] UTF-8 remediation complete.")
                print(f"  Success: {response.get('success')}")
                print(f"  Files fixed: {response.get('total_files_fixed', 0)}")
                print(f"  Violations fixed: {response.get('total_violations_fixed', 0)}")
                for entry in response.get("results", []):
                    scope = entry.get("scope", ".")
                    fixed_count = entry.get("violations_fixed", entry.get("files_fixed", 0))
                    print(f"  - {scope}: {fixed_count} violations fixed")
                    if not entry.get("success", True):
                        print(f"    [WARN] {entry.get('message', 'Remediation issue encountered')}")
            elif command == "batch":
                result = response.get("result", {})
                print("[INFO] Batch training complete.")
                print(f"  Success: {result.get('success')}")
                print(f"  Patterns Stored: {result.get('patterns_stored')}")
                print(f"  Lines Processed: {result.get('lines_processed')}")
        else:
            print(f"[ERROR] Training command failed: {response.get('message', response.get('error'))}")
        if warning:
            print(f"[WARN] {warning}")
def run_pqn_dae():
    """Run PQN Orchestration (Research & Alignment)."""
    print("[INFO] Starting PQN Research DAE...")
    try:
        from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
        pqn_dae = PQNResearchDAEOrchestrator()
        asyncio.run(pqn_dae.run())
    except Exception as e:
        print(f"[ERROR]PQN DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_liberty_alert_dae():
    """Run Liberty Alert DAE (Community Protection Autonomous Entity)."""
    print("[LIBERTY ALERT DAE] Starting Community Protection Autonomous Entity...")
    print("[LIBERTY ALERT DAE] 'L as resistance roots' - Liberty through community protection via mesh alerts")
    try:
        from modules.communication.liberty_alert.src.liberty_alert_dae import run_liberty_alert_dae as _run_dae
        asyncio.run(_run_dae())
    except Exception as e:
        print(f"[ERROR] Liberty Alert DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_evade_net():
    """Run Liberty Alert Mesh Alert System (Community Protection)."""
    print("[WARN] Starting Liberty Alert - Mesh Alert System...")
    print("[INFO] Offline P2P alerts for community protection")
    try:
        from modules.communication.liberty_alert.src.liberty_alert_orchestrator import LibertyAlertOrchestrator
        from modules.communication.liberty_alert.src.models import LibertyAlertConfig

        # Configure Liberty Alert
        config = LibertyAlertConfig(
            mesh_enabled=True,
            voice_enabled=True,
            default_language="es",
            alert_radius_km=5.0,
        )

        orchestrator = LibertyAlertOrchestrator(config)
        asyncio.run(orchestrator.run())
    except Exception as e:
        print(f"[ERROR]Liberty Alert failed: {e}")
        import traceback
        traceback.print_exc()


def check_instance_status():
    """Check the status and health of running instances."""
    print("\n" + "="*60)
    print("[INFO] INSTANCE STATUS CHECK")
    print("="*60)

    try:
        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

        lock = get_instance_lock("youtube_monitor")

        # Check for running instances
        duplicates = lock.check_duplicates()

        if duplicates:
            print(f"[ERROR]Found {len(duplicates)} duplicate instances running")
            return
        else:
            print("[INFO]No duplicate instances detected")

        # Check lock file status
        if lock.lock_file.exists():
            print("[INFO] Lock file exists:")
            try:
                with open(lock.lock_file, 'r') as f:
                    lock_data = json.load(f)
                pid = lock_data.get('pid')
                heartbeat = lock_data.get('heartbeat', 'Unknown')
                start_time = lock_data.get('start_time', 'Unknown')

                print(f"   PID: {pid}")
                print(f"   Started: {start_time}")
                print(f"   Last heartbeat: {heartbeat}")

                # Check if process is actually running
                if lock._is_process_running(pid):
                    print("   Status: [INFO]RUNNING")
                else:
                    print("   Status: [ERROR]PROCESS NOT FOUND (stale lock)")

            except Exception as e:
                print(f"   Error reading lock file: {e}")
        else:
            print("[LOCK] No lock file found (no instances running)")

        # Check health status
        health = lock.get_health_status()
        print("\n[INFO] Health Status:")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Message: {health.get('message', 'no data')}")
        if 'timestamp' in health:
            print(f"   Last update: {health['timestamp']}")

        # Check HoloDAE instances
        print("\n" + "-"*40)
        print("[MENU]HOLO-DAE STATUS")
        print("-"*40)

        try:
            holodae_lock = get_instance_lock("holodae_monitor")

            # Check for running HoloDAE instances
            holodae_duplicates = holodae_lock.check_duplicates()

            if holodae_duplicates:
                print(f"[ERROR]Found {len(holodae_duplicates)} HoloDAE instances running")
                return
            else:
                print("[INFO]No duplicate HoloDAE instances detected")

            # Check HoloDAE lock file status
            if holodae_lock.lock_file.exists():
                print("[INFO] HoloDAE Lock file exists:")
                try:
                    with open(holodae_lock.lock_file, 'r') as f:
                        lock_data = json.load(f)
                    pid = lock_data.get('pid')
                    heartbeat = lock_data.get('heartbeat', 'Unknown')
                    start_time = lock_data.get('start_time', 'Unknown')

                    print(f"   PID: {pid}")
                    print(f"   Started: {start_time}")
                    print(f"   Last heartbeat: {heartbeat}")

                    # Check if process is actually running
                    if holodae_lock._is_process_running(pid):
                        print("   Status: [INFO]RUNNING")
                    else:
                        print("   Status: [ERROR]PROCESS NOT FOUND (stale lock)")

                except Exception as e:
                    print(f"   Error reading lock file: {e}")
            else:
                print("[LOCK] No HoloDAE lock file found (no instances running)")

            # Check HoloDAE health status
            holodae_health = holodae_lock.get_health_status()
            print("\n[INFO] HoloDAE Health Status:")
            print(f"   Status: {holodae_health.get('status', 'unknown')}")
            print(f"   Message: {holodae_health.get('message', 'no data')}")
            if 'timestamp' in holodae_health:
                print(f"   Last update: {holodae_health['timestamp']}")

        except Exception as e:
            print(f"[ERROR]Error checking HoloDAE status: {e}")

    except Exception as e:
        print(f"[ERROR]Error checking status: {e}")

    print()


def generate_x_content(commit_msg, file_count):
    """Generate compelling X/Twitter content (280 char limit)"""
    import random

    # Short punchy intros for X
    x_intros = [
        "[INFO] FoundUps by @UnDaoDu\n\nDAEs eating startups for breakfast.\n\n",
        "[WARN] Startups die. FoundUps are forever.\n\n",
        "[MENU] No VCs. No employees. Just you + 0102 agents.\n\n",
        "[TIP] Solo unicorns are real. Ask @UnDaoDu.\n\n",
        "[INFO] The startup killer is here.\n\n"
    ]

    content = random.choice(x_intros)

    # Add brief update
    if "fix" in commit_msg.lower():
        content += f"[INFO] {file_count} fixes by 0102 agents\n\n"
    elif "test" in commit_msg.lower():
        content += f"[INFO] Testing future: {file_count} files\n\n"
    else:
        content += f"[WARN] {file_count} autonomous updates\n\n"

    # Short CTA
    ctas = [
        "Join the revolution.",
        "Build a FoundUp.",
        "Be a solo unicorn.",
        "The future is autonomous.",
        "Startups are dead."
    ]
    content += random.choice(ctas)

    # Essential hashtags that fit
    content += "\n\n#FoundUps #DAE #SoloUnicorn @Foundups"

    # Ensure we're under 280 chars
    if len(content) > 280:
        # Trim to fit with link
        content = content[:240] + "...\n\n#FoundUps @Foundups"

    return content


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
        print("Falling back to legacy git_push_and_post...")

        # Fallback to old method
        git_push_and_post()

    except Exception as e:
        print(f"[ERROR]GitPushDAE failed: {e}")
        input("\nPress Enter to continue...")

    finally:
        # Flush stdout/stderr to prevent "lost sys.stderr" errors
        # when returning to menu (WSP 90 UTF-8 enforcement cleanup)
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except:
            pass


def git_push_and_post():
    """
    LEGACY: Git push with automatic social media posting.
    Uses the git_linkedin_bridge module to handle posting.
    DEPRECATED: Use GitPushDAE instead for full autonomy.
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge

    print("\n" + "="*60)
    print("GIT PUSH & LINKEDIN + X POST (FoundUps)")
    print("="*60)
    print("[WARN] LEGACY MODE: Consider using GitPushDAE for full autonomy")

    # Use the git bridge module with X support
    bridge = GitLinkedInBridge(company_id="1263645")
    bridge.push_and_post()

    input("\nPress Enter to continue...")



def view_git_post_history():
    """View the history of git posts to social media."""
    import json
    import os
    from datetime import datetime

    print("\n" + "="*60)
    print("[INFO] GIT POST HISTORY")
    print("="*60)

    # Check posted commits
    posted_commits_file = "memory/git_posted_commits.json"
    if os.path.exists(posted_commits_file):
        try:
            with open(posted_commits_file, 'r') as f:
                posted_commits = json.load(f)
                print(f"\n[INFO]{len(posted_commits)} commits posted to social media")
                print("\nPosted commit hashes:")
                for commit in posted_commits[-10:]:  # Show last 10
                    print(f"  - {commit}")
                if len(posted_commits) > 10:
                    print(f"  ... and {len(posted_commits) - 10} more")
        except Exception as e:
            print(f"[ERROR]Error reading posted commits: {e}")
    else:
        print("[INFO] No posted commits found")

    # Check detailed log
    log_file = "memory/git_post_log.json"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                log_entries = json.load(f)
                print(f"\n[INFO] Detailed posting log ({len(log_entries)} entries):")
                print("-" * 60)

                # Show last 5 entries
                for entry in log_entries[-5:]:
                    timestamp = entry.get('timestamp', 'Unknown')
                    commit_msg = entry.get('commit_msg', 'No message')[:50]
                    linkedin = "[INFO] if entry.get('linkedin') else "[ERROR]
                    x_twitter = "[INFO] if entry.get('x_twitter') else "[ERROR]
                    files = entry.get('file_count', 0)

                    print(f"\n[INFO] {timestamp[:19]}")
                    print(f"   Commit: {commit_msg}...")
                    print(f"   Files: {files}")
                    print(f"   LinkedIn: {linkedin}  X/Twitter: {x_twitter}")

                if len(log_entries) > 5:
                    print(f"\n... and {len(log_entries) - 5} more entries")

                # Stats
                total_posts = len(log_entries)
                linkedin_success = sum(1 for e in log_entries if e.get('linkedin'))
                x_success = sum(1 for e in log_entries if e.get('x_twitter'))

                print("\n[INFO] Statistics:")
                print(f"   Total posts: {total_posts}")
                print(f"   LinkedIn success rate: {linkedin_success}/{total_posts} ({linkedin_success*100//max(total_posts,1)}%)")
                print(f"   X/Twitter success rate: {x_success}/{total_posts} ({x_success*100//max(total_posts,1)}%)")

        except Exception as e:
            print(f"[ERROR]Error reading log file: {e}")
    else:
        print("\n[INFO] No posting log found")

    # Option to clear history
    print("\n" + "-"*60)
    clear = input("Clear posting history? (y/n): ").lower()
    if clear == 'y':
        try:
            if os.path.exists(posted_commits_file):
                os.remove(posted_commits_file)
                print("[INFO]Cleared posted commits")
            if os.path.exists(log_file):
                os.remove(log_file)
                print("[INFO]Cleared posting log")
            print("[INFO] History cleared - all commits can be posted again")
        except Exception as e:
            print(f"[ERROR]Error clearing history: {e}")

    input("\nPress Enter to continue...")


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description='0102 FoundUps Agent')
    parser.add_argument('--git', action='store_true', help='Launch GitPushDAE (autonomous git push + social posting)')
    parser.add_argument('--youtube', action='store_true', help='Monitor YouTube only')
    parser.add_argument('--holodae', '--holo', action='store_true', help='Run HoloDAE (Code Intelligence & Monitoring)')
    parser.add_argument('--amo', action='store_true', help='Run AMO DAE (Autonomous Moderation Operations)')
    parser.add_argument('--smd', action='store_true', help='Run Social Media DAE (012 Digital Twin)')
    parser.add_argument('--vision', action='store_true', help='Run FoundUps Vision DAE (Pattern Sensorium)')
    parser.add_argument('--pqn', action='store_true', help='Run PQN Orchestration (Research & Alignment)')
    parser.add_argument('--liberty', action='store_true', help='Run Liberty Alert Mesh Alert System (Community Protection)')
    parser.add_argument('--liberty-dae', action='store_true', help='Run Liberty Alert DAE (Community Protection Autonomous Entity)')
    parser.add_argument('--all', action='store_true', help='Monitor all platforms')
    parser.add_argument('--no-lock', action='store_true', help='Disable instance lock (allow multiple instances)')
    parser.add_argument('--status', action='store_true', help='Check instance status and health')
    parser.add_argument('--training-command', type=str, help='Execute training command via Holo (e.g., utf8_scan, batch)')
    parser.add_argument('--targets', type=str, help='Comma-separated target paths for training command')
    parser.add_argument('--json-output', action='store_true', help='Return training command result as JSON')
    parser.add_argument('--training-menu', action='store_true', help='Launch interactive training submenu (option 12)')

    args = parser.parse_args()

    if args.training_command:
        execute_training_command(args.training_command, args.targets, args.json_output)
        return
    if args.training_menu:
        run_training_system()
        return

    if args.status:
        check_instance_status()
        return
    elif args.git:
        launch_git_push_dae()
    elif args.youtube:
        asyncio.run(monitor_youtube(disable_lock=args.no_lock))
    elif args.holodae:
        run_holodae()
    elif args.amo:
        run_amo_dae()
    elif args.smd:
        run_social_media_dae()
    elif args.vision:
        run_vision_dae()
    elif args.pqn:
        run_pqn_dae()
    elif args.liberty:
        run_evade_net()
    elif args.liberty_dae:
        run_liberty_alert_dae()
    elif args.all:
        asyncio.run(monitor_all_platforms())
    else:
        # Interactive menu - Check instances once at startup, then loop main menu
        print("\n" + "="*60)
        print("0102 FoundUps Agent - DAE Test Menu")
        print("="*60)

        # Check for running instances once at startup
        try:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")
            duplicates = lock.check_duplicates(quiet=True)

            if duplicates:
                # Loop until user makes a valid choice
                while True:
                    print(f"[WARN] FOUND {len(duplicates)} RUNNING INSTANCE(S)")
                    print("\nWhat would you like to do?")
                    print("1. Kill all instances and continue")
                    print("2. Show detailed status")
                    print("3. Continue anyway (may cause conflicts)")
                    print("4. Exit")
                    print("-"*40)

                    # Get user input and clean it (remove brackets, spaces, etc.)
                    choice = input("Select option (1-4): ").strip().lstrip(']').lstrip('[')

                    if choice == "1":
                        print("\n[INFO] Killing duplicate instances...")
                        killed_pids = []
                        failed_pids = []

                        current_pid = os.getpid()

                        for pid in duplicates:
                            if pid == current_pid:
                                continue  # Don't kill ourselves

                            try:
                                print(f"   [INFO] Terminating PID {pid}...")
                                process = psutil.Process(pid)
                                process.terminate()  # Try graceful termination first

                                # Wait up to 5 seconds for process to terminate
                                gone, alive = psutil.wait_procs([process], timeout=5)

                                if alive:
                                    # If still alive, force kill
                                    print(f"   [INFO] Force killing PID {pid}...")
                                    process.kill()
                                    gone, alive = psutil.wait_procs([process], timeout=2)

                                if not alive:
                                    killed_pids.append(pid)
                                    print(f"   [INFO]PID {pid} terminated successfully")
                                else:
                                    failed_pids.append(pid)
                                    print(f"   [ERROR]Failed to kill PID {pid}")

                            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                print(f"   [WARN] Could not kill PID {pid}: {e}")
                                failed_pids.append(pid)

                        if killed_pids:
                            print(f"\n[INFO]Successfully killed {len(killed_pids)} instance(s): {killed_pids}")
                        if failed_pids:
                            print(f"[WARN] Failed to kill {len(failed_pids)} instance(s): {failed_pids}")

                        print("   Proceeding to main menu...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "2":
                        print("\n" + "="*50)
                        check_instance_status()
                        print("="*50)
                        input("\nPress Enter to continue...")
                        # Don't break - loop back to menu

                    elif choice == "3":
                        print("[WARN] Continuing with potential conflicts...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "4":
                        print("[INFO] Exiting...")
                        return  # Exit entire program

                    else:
                        print(f"[ERROR]Invalid choice '{choice}'. Please enter 1, 2, 3, or 4.")
                        print("   Try again...\n")
                        # Don't break - loop will continue and ask again
                        continue

            else:
                print("[INFO] No running instances detected")
                print("   Safe to start new DAEs")
                print("   Browser cleanup will run on startup\n")

        except Exception as e:
            print(f"[WARN] Could not check instances: {e}")
            print("   Proceeding with menu...\n")

        print("[DEBUG-MAIN] About to enter main menu loop")

        # Main menu loop (only reached after instance handling)
        while True:
            print("[DEBUG-MAIN] Top of menu loop - displaying options")

            # Show the main menu
            print("0. Push to Git and Post to LinkedIn + X (FoundUps)       | --git")
            print("1. YouTube Live DAE (Move2Japan/UnDaoDu/FoundUps)        | --youtube")
            print("2. HoloDAE (Code Intelligence & Monitoring)              | --holodae")
            print("3. AMO DAE (Autonomous Moderation Operations)            | --amo")
            print("4. Social Media DAE (012 Digital Twin)                   | --smd")
            print("5. Liberty Alert DAE (Community Protection)              | --liberty-dae")
            print("6. PQN Orchestration (Research & Alignment)              | --pqn")
            print("7. Liberty Alert (Mesh Alert System)                     | --liberty")
            print("8. FoundUps Vision DAE (Pattern Sensorium)               | --vision")
            print("9. All DAEs (Full System)                                | --all")
            print("10. Exit")
            print("-"*60)
            print("00. Check Instance Status & Health                       | --status")
            print("11. HoloIndex Search (Find code semantically)")
            print("12. View Git Post History")
            print("13. Qwen/Gemma Training System (Pattern Learning)")
            print("="*60)
            print("CLI: --youtube --no-lock (bypass menu + instance lock)")
            print("="*60)

            choice = input("\nSelect option: ")
            print(f"[DEBUG-MAIN] User selected option: '{choice}'")

            if choice == "0":
                # Launch GitPushDAE daemon (WSP 91 compliant)
                print("[DEBUG-MAIN] Calling launch_git_push_dae()...")
                launch_git_push_dae()
                print("[DEBUG-MAIN] Returned from launch_git_push_dae()")
                # Will return to menu after completion

            elif choice == "1":
                # YouTube DAE Menu - Live Chat OR Shorts
                print("\n[MENU] YouTube DAE Menu")
                print("="*60)
                print("1. [ALERT] YouTube Live Chat Monitor (AutoModeratorDAE)")
                print("2. [MENU] YouTube Shorts Generator (Gemini/Veo 3)")
                print("3. [MENU] YouTube Shorts Generator (Sora2 Live Action)")
                print("4. [INFO] YouTube Stats & Info")
                print("0. [BACK] Back to Main Menu")
                print("="*60)

                yt_choice = input("\nSelect YouTube option: ")

                def run_shorts_flow(engine_label: str, system_label: str, mode_label: str, duration_label: str, engine_key: str) -> None:
                    print(f"\n[MENU] YouTube Shorts Generator [{engine_label}]")
                    print("="*60)
                    print("Channel: Move2Japan (9,020 subscribers)")
                    print(f"System: {system_label}")
                    print("="*60)

                    topic = input("\n[TIP] Enter topic (e.g., 'Cherry blossoms in Tokyo'): ").strip()

                    if not topic:
                        print("[WARN] No topic entered - returning to menu")
                        return

                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

                        print(f"\n[MENU] Generating YouTube Short ({engine_label}): {topic}")
                        print(f"  Mode: {mode_label}")
                        print(f"  Duration: {duration_label}")
                        print("  Privacy: PUBLIC")

                        orchestrator = ShortsOrchestrator(channel="move2japan", default_engine="auto")

                        youtube_url = orchestrator.create_and_upload(
                            topic=topic,
                            duration=15,
                            enhance_prompt=True,
                            fast_mode=True,
                            privacy="public",
                            use_3act=True,
                            engine=engine_key
                        )

                        print(f"\n[INFO]SHORT PUBLISHED!")
                        print(f"   URL: {youtube_url}")
                        print(f"   Channel: Move2Japan")

                    except Exception as e:
                        print(f"\n[ERROR]YouTube Shorts generation failed: {e}")
                        import traceback
                        traceback.print_exc()

                if yt_choice == "1":
                    print("[MENU] Starting YouTube Live Chat Monitor...")
                    asyncio.run(monitor_youtube(disable_lock=False))

                elif yt_choice == "2":
                    run_shorts_flow(
                        engine_label="Gemini/Veo 3",
                        system_label="3-Act Story (Setup  -> Shock  -> 0102 Reveal)",
                        mode_label="Emergence Journal POC",
                        duration_label="~16s (2.5s clips merged)",
                        engine_key="veo3"
                    )

                elif yt_choice == "3":
                    run_shorts_flow(
                        engine_label="Sora2 Live Action",
                        system_label="3-Act Story (Cinematic Reveal)",
                        mode_label="Cinematic Sora2 (live-action focus)",
                        duration_label="15s cinematic (single clip)",
                        engine_key="sora2"
                    )

                elif yt_choice == "4":
                    # YouTube Stats
                    print("\n[INFO] YouTube Stats")
                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator
                        orch = ShortsOrchestrator(channel="move2japan", default_engine="auto")
                        stats = orch.get_stats()

                        print(f"\n  Total Shorts: {stats['total_shorts']}")
                        print(f"  Uploaded: {stats['uploaded']}")
                        print(f"  Total Cost: ${stats['total_cost_usd']}")
                        print(f"  Avg Cost: ${stats['average_cost_per_short']}")
                        if stats.get('engine_usage'):
                            print(f"  Engine Usage: {stats['engine_usage']}")

                        recent = stats.get('recent_shorts') or []
                        if recent:
                            print(f"\n  Recent Shorts:")
                            for s in recent[-3:]:
                                print(f"    - {s.get('topic', 'N/A')[:40]}...")
                                print(f"      {s.get('youtube_url', 'N/A')}")
                    except Exception as e:
                        print(f"[ERROR]Failed to get stats: {e}")

                elif yt_choice == "0":
                    print("[BACK] Returning to main menu...")
                else:
                    print("[ERROR]Invalid choice")

            elif choice == "2":
                # HoloDAE - Code Intelligence & Monitoring
                print("[INFO] HoloDAE Menu - Code Intelligence & Monitoring System")
                try:
                    # Import menu function ONLY (don't start daemon yet)
                    from holo_index.qwen_advisor.autonomous_holodae import show_holodae_menu

                    holodae_instance = None  # Initialize as None, created only when needed

                    while True:
                        choice = show_holodae_menu()

                        if choice == "0":
                            # Launch the daemon (option 0 in HoloDAE menu)
                            print("[MENU] Launching HoloDAE Autonomous Monitor...")
                            from holo_index.qwen_advisor.autonomous_holodae import start_holodae_monitoring
                            if holodae_instance is None:
                                holodae_instance = start_holodae_monitoring()
                                print("[INFO]HoloDAE monitoring started in background")
                                print("[TIP] Daemon is running - select 9 to stop, or 99 to return to main menu")
                            else:
                                print("[INFO]HoloDAE already running")
                            # Don't break - loop back to HoloDAE menu for more selections
                        elif choice == "9":
                            # Stop the daemon (option 9 - toggle monitoring)
                            if holodae_instance is not None and holodae_instance.active:
                                print("[INFO] Stopping HoloDAE monitoring...")
                                holodae_instance.stop_autonomous_monitoring()
                                print("[INFO]HoloDAE daemon stopped")
                            else:
                                print("[INFO] HoloDAE daemon is not running")
                        elif choice == "99":
                            print("[INFO] Returning to main menu...")
                            if holodae_instance is not None and holodae_instance.active:
                                print("[WARN]HoloDAE daemon still running in background")
                            break
                        elif choice == "1":
                            print("[INFO] Running semantic code search...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "2":
                            print("[INFO] Running dual search (code + WSP)...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "3":
                            print("[INFO]Running module existence check...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --check-module 'module_name'")
                        elif choice == "4":
                            print("[INFO] Running DAE cube organizer...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --init-dae 'DAE_name'")
                        elif choice == "5":
                            print("[INFO] Running index management...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --index-all")
                        elif choice in ["6", "7", "8", "9", "10", "11", "12", "13"]:
                            print("[INFO] Running HoloDAE intelligence analysis...")
                            # These would trigger HoloDAE analysis functions
                            print("Use HoloIndex search to trigger automatic analysis")
                        elif choice == "14":
                            print("[INFO]Running WSP 88 orphan analysis...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --wsp88")
                        elif choice == "16":
                            print("[INFO] Execution Log Analyzer - Advisor Choice")
                            print("=" * 60)
                            print("Advisor: Choose analysis mode for systematic log processing")
                            print()
                            print("1. [MENU]Interactive Mode - Step-by-step advisor guidance")
                            print("2. [WARN] Daemon Mode - Autonomous 0102 background processing")
                            print()
                            print("Interactive: User-guided analysis with advisor oversight")
                            print("Daemon: Autonomous processing once triggered - follows WSP 80")
                            print()

                            analysis_choice = input("Select mode (1-2): ").strip()

                            if analysis_choice == "1":
                                # Interactive mode - advisor-guided
                                print("\n[MENU]Starting Interactive Log Analysis...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("[INFO] Advisor-guided systematic log analysis...")
                                    print("[INFO] Processing 23,000+ lines with advisor oversight...")

                                    librarian = coordinate_execution_log_processing(daemon_mode=False)

                                    print("\n[INFO]Interactive analysis initialized!")
                                    print("[INFO] Results saved to:")
                                    print("   - complete_file_index.json (full scope analysis)")
                                    print("   - qwen_processing_plan.json (processing plan)")
                                    print("   - qwen_next_task.json (ready for Qwen analysis)")

                                    print("\n[INFO] Next: Advisor guides Qwen analysis of chunks")
                                    input("\nPress Enter to continue...")

                                except Exception as e:
                                    print(f"[ERROR]Interactive analysis failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            elif analysis_choice == "2":
                                # Daemon mode - autonomous 0102 processing
                                print("\n[WARN] Starting Log Analysis Daemon...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("[INFO] Advisor triggers autonomous 0102 processing...")
                                    print("[INFO] 0102 will process entire log file independently")

                                    # Start daemon
                                    daemon_thread = coordinate_execution_log_processing(daemon_mode=True)

                                    print("\n[INFO]Daemon started successfully!")
                                    print("[INFO] 0102 processing 23,000+ lines autonomously")
                                    print("[INFO] Check progress: HoloDAE menu  -> Option 15 (PID Detective)")
                                    print("[INFO] Results will be saved to analysis output files")

                                    input("\nPress Enter to continue (daemon runs in background)...")

                                except Exception as e:
                                    print(f"[ERROR]Daemon startup failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            else:
                                print("[ERROR]Invalid choice - returning to menu")
                                input("\nPress Enter to continue...")
                        elif choice in ["15", "17", "18"]:
                            print("[INFO] Running WSP compliance functions...")
                            # These would trigger compliance checking
                            print("Use HoloIndex search to trigger compliance analysis")
                        elif choice in ["19", "20", "21", "22", "23"]:
                            print("[MENU]Running AI advisor functions...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'query' --llm-advisor")
                        elif choice == "24":
                            print("[MENU] Launching YouTube Live DAE...")
                            # Would need to navigate to option 1
                            print("Please select option 1 from main menu for YouTube DAE")
                        elif choice == "25":
                            print("[INFO] Starting autonomous HoloDAE monitoring...")
                            run_holodae()
                            break  # Exit menu after starting monitoring
                        elif choice == "6":
                            print("[INFO] Launching Chain-of-Thought Brain Logging...")
                            try:
                                from holo_index.qwen_advisor.chain_of_thought_logger import demonstrate_brain_logging
                                demonstrate_brain_logging()
                                print("\n[INFO] BRAIN LOGGING COMPLETE - Every thought, decision, and action was logged above!")
                                print("[TIP] This shows exactly how the AI brain works - completely observable!")
                            except Exception as e:
                                print(f"[ERROR]Brain logging failed: {e}")
                            input("\nPress Enter to continue...")
                        elif choice in ["26", "27", "28", "29", "30"]:
                            print("[INFO] This DAE operation requires main menu selection...")
                            # Would need to navigate to appropriate main menu option
                            print("Please return to main menu and select the appropriate DAE")
                        elif choice in ["31", "32", "33", "34", "35"]:
                            print("[WARN]Running administrative functions...")
                            # These would trigger admin functions
                            print("Administrative functions available through main menu")
                        else:
                            print("[ERROR]Invalid choice. Please select 0-35.")

                        input("\nPress Enter to continue...")

                except Exception as e:
                    print(f"[ERROR]HoloDAE menu failed to load: {e}")
                    import traceback
                    traceback.print_exc()

            elif choice == "3":
                # AMO DAE
                print("[AMO] Starting AMO DAE (Autonomous Moderation)...")
                from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
                dae = AutoModeratorDAE()
                asyncio.run(dae.run())

            elif choice == "4":
                # Social Media DAE (012 Digital Twin)
                print("[SMD] Starting Social Media DAE (012 Digital Twin)...")
                from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator
                orchestrator = SocialMediaOrchestrator()
                # orchestrator.run_digital_twin()  # TODO: Implement digital twin mode
                print("Digital Twin mode coming soon...")

            elif choice == "5":
                # Liberty Alert DAE
                run_liberty_alert_dae()

            elif choice == "6":
                # PQN Orchestration
                print("[INFO] Starting PQN Research DAE...")
                from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
                pqn_dae = PQNResearchDAEOrchestrator()
                asyncio.run(pqn_dae.run())

            elif choice == "7":
                # Liberty Alert mesh alert system
                run_evade_net()

            elif choice == "8":
                # FoundUps Vision DAE
                run_vision_dae()

            elif choice == "9":
                # All DAEs
                print("[ALL] Starting ALL DAEs...")
                asyncio.run(monitor_all_platforms())

            elif choice == "10":
                print("[EXIT] Exiting...")
                break  # Exit the while True loop

            elif choice in {"00", "status"}:
                check_instance_status()
                input("\nPress Enter to continue...")

            elif choice == "10":
                # HoloIndex search
                print("\n[HOLOINDEX] Semantic Code Search")
                print("=" * 60)
                print("This prevents vibecoding by finding existing code!")
                print("Examples: 'send messages', 'handle timeouts', 'consciousness'")
                print("=" * 60)
                query = input("\nWhat code are you looking for? ")
                if query:
                    search_with_holoindex(query)
                    input("\nPress Enter to continue...")
                else:
                    print("No search query provided")

            elif choice == "11":
                # View git post history
                view_git_post_history()

            elif choice == "12":
                # Qwen/Gemma Training System
                run_training_system()

            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()



