"""
FoundUps Ecosystem Menu - pAVS control panel.

WSP 50 (deploy confirmations), WSP 62 (separate file), WSP 72 (lazy imports).
"""

import logging
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[4]
SIMULATOR_DIR = REPO_ROOT / "modules" / "foundups" / "simulator"

_sse_process: Optional[subprocess.Popen] = None


def handle_fam_menu() -> bool:
    """FoundUps Ecosystem menu. Returns True to exit to main menu."""
    print("\n  FoundUps Ecosystem (pAVS)")
    print("  " + "-" * 40)
    print("  1. Start Simulator")
    print("  2. Deploy")
    print("  3. CABR Dashboard")
    print("  4. Investor Model")
    print("  5. FAM Status")
    print("  6. OpenClaw (012 Twin)")
    print("  0. Back")
    print()

    try:
        choice = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return True

    actions = {
        "0": lambda: True,
        "1": _start_simulator,
        "2": _deploy,
        "3": _cabr_dashboard,
        "4": _investor_model,
        "5": _fam_status,
        "6": _openclaw,
    }

    action = actions.get(choice)
    if action:
        result = action()
        if result is True and choice == "0":
            return True
    else:
        print("  Invalid choice")

    return False


# --- Simulator ---


def _is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _start_simulator() -> None:
    """Start SSE server with Mesa simulator."""
    global _sse_process

    print("\n  Simulator Mode:")
    print("  1. Live (Mesa model + SSE)  [default]")
    print("  2. Simulated events only")
    print("  3. Terminal only (no SSE)")
    try:
        mode = input("  > ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        return

    if mode == "3":
        _run_terminal_simulator()
        return

    port = int(os.getenv("SSE_PORT", "8080"))

    # Already running?
    if _sse_process and _sse_process.poll() is None:
        print(f"  Already running (PID {_sse_process.pid})")
        if input("  Restart? (y/N): ").strip().lower() != "y":
            return
        _sse_process.terminate()
        try:
            _sse_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _sse_process.kill()

    # Port taken?
    if _is_port_in_use(port):
        print(f"  Port {port} in use.")
        print(f"  Find it: netstat -ano | findstr :{port}")
        if input(f"  Try {port + 1}? (Y/n): ").strip().lower() == "n":
            return
        port += 1
        if _is_port_in_use(port):
            print(f"  Port {port} also taken. Free a port and retry.")
            return

    sse_script = SIMULATOR_DIR / "sse_server.py"
    if not sse_script.exists():
        print(f"  Not found: {sse_script}")
        return

    cmd = [sys.executable, str(sse_script)]
    if mode == "2":
        cmd.append("--simulate")
    else:
        cmd.extend(["--run-simulator", "--founders", "3", "--users", "10", "--speed", "2.0"])
    cmd.extend(["--port", str(port)])

    label = "SIMULATED" if mode == "2" else "LIVE"
    print(f"\n  Starting {label} on :{port}...")

    try:
        _sse_process = subprocess.Popen(cmd, cwd=str(REPO_ROOT))
        print(f"  PID {_sse_process.pid}")
        print(f"\n  Health:  http://localhost:{port}/api/health")
        print(f"  Stream:  http://localhost:{port}/api/sim-events")
        print(f"  Cube:    foundups.com/?sim=1  (or localhost:5000/?sim=1)")
    except Exception as e:
        print(f"  Failed: {e}")

    input("\n  Enter to continue...")


def _run_terminal_simulator() -> None:
    """Run Mesa model in terminal (blocking, no SSE)."""
    run_script = SIMULATOR_DIR / "run.py"
    if not run_script.exists():
        print(f"  Not found: {run_script}")
        return

    founders = input("  Founders [3]: ").strip() or "3"
    users = input("  Users [10]: ").strip() or "10"
    speed = input("  Speed Hz [2.0]: ").strip() or "2.0"

    cmd = [sys.executable, str(run_script),
           "--founders", founders, "--users", users, "--speed", speed]

    print("  Ctrl+C to stop\n")
    try:
        subprocess.run(cmd, cwd=str(REPO_ROOT))
    except KeyboardInterrupt:
        print("\n  Stopped")
    except Exception as e:
        print(f"  Failed: {e}")

    input("\n  Enter to continue...")


# --- Deploy ---


def _deploy() -> None:
    """Deploy to Cloud Run or Firebase (WSP 50: type YES)."""
    print("\n  Deploy Target:")
    print("  1. Cloud Run (SSE server)")
    print("  2. Firebase Hosting (foundups.com)")
    try:
        choice = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    if choice == "1":
        _deploy_cloud_run()
    elif choice == "2":
        _deploy_firebase()


def _deploy_cloud_run() -> None:
    if not shutil.which("gcloud"):
        print("  gcloud not found. Install: cloud.google.com/sdk/docs/install")
        return

    print("  Target: sse-foundups / us-central1 / 256Mi")
    if input("  Deploy to PRODUCTION? (type YES): ").strip() != "YES":
        print("  Cancelled")
        return

    if sys.platform == "win32":
        cmd = [
            "gcloud", "run", "deploy", "sse-foundups",
            "--source", str(SIMULATOR_DIR),
            "--project", "gen-lang-client-0061781628",
            "--region", "us-central1", "--platform", "managed",
            "--allow-unauthenticated", "--port", "8080",
            "--memory", "256Mi", "--min-instances", "0",
            "--max-instances", "2", "--timeout", "300s",
            "--set-env-vars", "PYTHONUNBUFFERED=1",
        ]
    else:
        cmd = ["bash", str(SIMULATOR_DIR / "deploy-sse.sh")]

    print("  Deploying...")
    try:
        result = subprocess.run(cmd, cwd=str(SIMULATOR_DIR))
        if result.returncode == 0:
            print("  Done! SSE at: sse-foundups-*.run.app/api/sim-events")
        else:
            print(f"  Failed (exit {result.returncode})")
    except KeyboardInterrupt:
        print("  Interrupted")
    except Exception as e:
        print(f"  Failed: {e}")

    input("\n  Enter to continue...")


def _deploy_firebase() -> None:
    if not shutil.which("firebase"):
        print("  firebase not found. Install: npm install -g firebase-tools")
        return

    print("  Target: foundupscom / public/ / /api/** -> Cloud Run")
    if input("  Deploy to PRODUCTION? (type YES): ").strip() != "YES":
        print("  Cancelled")
        return

    print("  Deploying...")
    try:
        result = subprocess.run(
            ["firebase", "deploy", "--only", "hosting"],
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            print("  Done! Site: foundups.com")
        else:
            print(f"  Failed (exit {result.returncode})")
    except KeyboardInterrupt:
        print("  Interrupted")
    except Exception as e:
        print(f"  Failed: {e}")

    input("\n  Enter to continue...")


# --- CABR ---


def _cabr_dashboard() -> None:
    """CABR scoring table for sample FoundUps."""
    try:
        from modules.foundups.simulator.ai.cabr_estimator import (
            CABREstimator, CABR_THRESHOLD, FoundUpIdea,
        )
    except ImportError as e:
        print(f"  Not available: {e}")
        input("\n  Enter to continue...")
        return

    estimator = CABREstimator(use_ai=False)

    ideas = [
        FoundUpIdea("FoundUps", "FUPS", "No framework for autonomous ventures",
                    "Open platform for pAVS ecosystem", "infrastructure", 10, 21_000_000,
                    {"treasury": 0.2, "team": 0.1, "community": 0.7}),
        FoundUpIdea("Move2Japan", "M2J", "Foreigners struggle relocating to Japan",
                    "AI-guided relocation assistance", "social", 5, 21_000_000,
                    {"treasury": 0.2, "team": 0.1, "community": 0.7}),
        FoundUpIdea("GotJunk_Pro", "JUNK", "Junk removal is expensive and wasteful",
                    "Reuse-first junk removal marketplace", "waste", 8, 21_000_000,
                    {"treasury": 0.2, "team": 0.1, "community": 0.7}),
        FoundUpIdea("GreenEnergy", "GRNE", "Fossil fuel dependence",
                    "Community renewable energy grid", "energy", 6, 21_000_000,
                    {"treasury": 0.2, "team": 0.1, "community": 0.7}),
        FoundUpIdea("EduLearn", "EDUX", "Education inaccessible to many",
                    "Open education with token incentives", "education", 4, 21_000_000,
                    {"treasury": 0.2, "team": 0.1, "community": 0.7}),
        FoundUpIdea("CloudKitchen", "CKXN", "Restaurant startup costs too high",
                    "Shared kitchen marketplace", "food", 5, 21_000_000,
                    {"treasury": 0.2, "team": 0.1, "community": 0.7}),
    ]

    print(f"\n  {'FoundUp':<14} {'ENV':>5} {'SOC':>5} {'PART':>5} {'TOTAL':>6} {'':>4}")
    print("  " + "-" * 44)

    for idea in ideas:
        score = estimator.estimate_idea_cabr(idea)
        meets = estimator.meets_threshold(score)
        mark = "OK" if meets else "--"
        print(f"  {idea.name:<14} {score.env_score:>5.2f} {score.soc_score:>5.2f} "
              f"{score.part_score:>5.2f} {score.total:>6.3f}  {mark}")

    print("  " + "-" * 44)
    print(f"  Threshold: {CABR_THRESHOLD} (golden ratio)")
    print(f"  PART starts at 0 - rises with agent activity")

    input("\n  Enter to continue...")


# --- Investor Model ---


def _investor_model() -> None:
    """Bonding curve returns and underwriting scenarios."""
    print("\n  Investor Model:")
    print("  1. Bonding Curve Returns (10x/100x)")
    print("  2. Underwriting Matrix")
    try:
        choice = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    try:
        if choice == "1":
            from modules.foundups.simulator.economics import demonstrate_10x_100x_returns
            demonstrate_10x_100x_returns()
        elif choice == "2":
            from modules.foundups.simulator.economics import run_underwriting_matrix
            run_underwriting_matrix()
        else:
            return
    except ImportError as e:
        print(f"  Not available: {e}")
    except Exception as e:
        print(f"  Error: {e}")

    input("\n  Enter to continue...")


# --- FAM Status ---


def _fam_status() -> None:
    """FAM DAEmon health check."""
    try:
        from modules.foundups.agent_market.src.fam_daemon import get_fam_daemon
    except ImportError as e:
        print(f"  Not available: {e}")
        input("\n  Enter to continue...")
        return

    daemon = get_fam_daemon(auto_start=False)
    health = daemon.get_health()

    running = "YES" if health.running else "NO"
    parity = "OK" if health.parity_ok else "FAIL"
    stats = health.event_store_stats

    print(f"\n  Running:    {running}")
    print(f"  Uptime:     {health.uptime_seconds:.0f}s")
    print(f"  Heartbeats: {health.heartbeat_count}")
    print(f"  Parity:     {parity}")
    print(f"  Events:     {stats.get('total_events', 0)}")

    by_type = stats.get("events_by_type", {})
    if by_type:
        print()
        for etype, count in sorted(by_type.items()):
            print(f"    {etype:<28} {count:>4}")

    if health.errors:
        print(f"\n  Errors ({len(health.errors)}):")
        for err in health.errors[-3:]:
            print(f"    {err}")

    if not health.running:
        if input("\n  Start DAEmon? (y/N): ").strip().lower() == "y":
            get_fam_daemon(auto_start=True)
            print("  Started!")

    input("\n  Enter to continue...")


# --- OpenClaw ---


def _openclaw() -> None:
    """OpenClaw submenu -- all ways to talk to 0102."""
    from modules.infrastructure.cli.src.openclaw_menu import handle_openclaw_menu
    while True:
        if handle_openclaw_menu():
            break
