#!/usr/bin/env python3
"""
Setup Suno Lyrics Extension - Automated Installation

Installs the get-suno-lyric Chrome extension for batch LRC downloads.

Usage:
    # Full setup (clone, install, build):
    python setup_suno_extension.py install

    # Open Chrome with extension loaded:
    python setup_suno_extension.py launch

    # Check status:
    python setup_suno_extension.py status

    # Uninstall:
    python setup_suno_extension.py uninstall
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Extension paths
DATA_DIR = Path(__file__).parent.parent / "data"
EXTENSION_DIR = DATA_DIR / "suno_extension"
EXTENSION_REPO = "https://github.com/zh30/get-suno-lyric.git"
LRC_OUTPUT_DIR = DATA_DIR / "lrc_downloads"


def check_dependencies() -> dict:
    """Check if required tools are installed."""
    deps = {
        "git": False,
        "node": False,
        "pnpm": False,
        "npm": False,
        "chrome": False,
    }

    # Check git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        deps["git"] = result.returncode == 0
    except FileNotFoundError:
        pass

    # Check node
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        deps["node"] = result.returncode == 0
    except FileNotFoundError:
        pass

    # Check pnpm
    try:
        result = subprocess.run(["pnpm", "--version"], capture_output=True, text=True)
        deps["pnpm"] = result.returncode == 0
    except FileNotFoundError:
        pass

    # Check npm (fallback)
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        deps["npm"] = result.returncode == 0
    except FileNotFoundError:
        pass

    # Check Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
    ]
    for path in chrome_paths:
        if Path(path).exists():
            deps["chrome"] = True
            break

    return deps


def install_pnpm():
    """Install pnpm via npm."""
    logger.info("[SETUP] Installing pnpm...")
    try:
        subprocess.run(["npm", "install", "-g", "pnpm"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[SETUP] Failed to install pnpm: {e}")
        return False


def clone_extension():
    """Clone the extension repository."""
    if EXTENSION_DIR.exists():
        logger.info(f"[SETUP] Extension already exists at: {EXTENSION_DIR}")
        return True

    logger.info(f"[SETUP] Cloning {EXTENSION_REPO}...")
    EXTENSION_DIR.parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["git", "clone", EXTENSION_REPO, str(EXTENSION_DIR)],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[SETUP] Clone failed: {e}")
        return False


def install_dependencies():
    """Install extension dependencies."""
    if not EXTENSION_DIR.exists():
        logger.error("[SETUP] Extension not cloned yet")
        return False

    logger.info("[SETUP] Installing dependencies...")

    # Try pnpm first, fallback to npm
    package_manager = "pnpm" if shutil.which("pnpm") else "npm"

    try:
        subprocess.run(
            [package_manager, "install"],
            cwd=str(EXTENSION_DIR),
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[SETUP] Install failed: {e}")
        return False


def build_extension():
    """Build the extension."""
    if not EXTENSION_DIR.exists():
        logger.error("[SETUP] Extension not cloned yet")
        return False

    logger.info("[SETUP] Building extension...")

    package_manager = "pnpm" if shutil.which("pnpm") else "npm"

    try:
        subprocess.run(
            [package_manager, "run", "build"],
            cwd=str(EXTENSION_DIR),
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[SETUP] Build failed: {e}")
        return False


def get_extension_dist_path() -> Path:
    """Get path to built extension."""
    dist_path = EXTENSION_DIR / "dist"
    if dist_path.exists():
        return dist_path
    # Some builds output to 'build' folder
    build_path = EXTENSION_DIR / "build"
    if build_path.exists():
        return build_path
    return dist_path


def launch_chrome_with_extension():
    """Launch Chrome with extension loaded."""
    dist_path = get_extension_dist_path()

    if not dist_path.exists():
        logger.error(f"[LAUNCH] Extension not built. Run: python setup_suno_extension.py install")
        return False

    # Find Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
    ]

    chrome_exe = None
    for path in chrome_paths:
        if Path(path).exists():
            chrome_exe = path
            break

    if not chrome_exe:
        logger.error("[LAUNCH] Chrome not found. Please install Chrome.")
        return False

    # Create output directory for downloads
    LRC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"[LAUNCH] Starting Chrome with extension from: {dist_path}")
    logger.info(f"[LAUNCH] LRC files will be saved to: {LRC_OUTPUT_DIR}")

    # Launch Chrome with extension
    cmd = [
        chrome_exe,
        f"--load-extension={dist_path}",
        f"--user-data-dir={DATA_DIR / 'chrome_profile'}",  # Separate profile
        "--no-first-run",
        "--no-default-browser-check",
        "https://suno.com/playlist/3adb1878-12f8-4c1c-a815-bde3d7d320ed"  # 012's playlist
    ]

    try:
        subprocess.Popen(cmd)
        logger.info("[LAUNCH] Chrome started. Look for download button on song pages.")
        return True
    except Exception as e:
        logger.error(f"[LAUNCH] Failed to start Chrome: {e}")
        return False


def get_status() -> dict:
    """Get installation status."""
    deps = check_dependencies()

    status = {
        "dependencies": deps,
        "extension_cloned": EXTENSION_DIR.exists(),
        "extension_built": get_extension_dist_path().exists(),
        "lrc_output_dir": str(LRC_OUTPUT_DIR),
        "lrc_files_count": len(list(LRC_OUTPUT_DIR.glob("*.lrc"))) if LRC_OUTPUT_DIR.exists() else 0,
    }

    return status


def uninstall():
    """Remove extension and data."""
    if EXTENSION_DIR.exists():
        logger.info(f"[UNINSTALL] Removing: {EXTENSION_DIR}")
        shutil.rmtree(EXTENSION_DIR)

    chrome_profile = DATA_DIR / "chrome_profile"
    if chrome_profile.exists():
        logger.info(f"[UNINSTALL] Removing Chrome profile: {chrome_profile}")
        shutil.rmtree(chrome_profile)

    logger.info("[UNINSTALL] Complete. LRC files preserved in: {LRC_OUTPUT_DIR}")


def full_install():
    """Run full installation."""
    print("=" * 60)
    print("[SUNO EXTENSION SETUP]")
    print("=" * 60)

    # Check dependencies
    print("\n[1/5] Checking dependencies...")
    deps = check_dependencies()

    if not deps["git"]:
        print("  [ERROR] Git not found. Install from: https://git-scm.com/")
        return False

    if not deps["node"]:
        print("  [ERROR] Node.js not found. Install from: https://nodejs.org/")
        return False

    print(f"  Git:   {'OK' if deps['git'] else 'MISSING'}")
    print(f"  Node:  {'OK' if deps['node'] else 'MISSING'}")
    print(f"  pnpm:  {'OK' if deps['pnpm'] else 'will install'}")
    print(f"  Chrome: {'OK' if deps['chrome'] else 'MISSING'}")

    # Install pnpm if needed
    if not deps["pnpm"] and deps["npm"]:
        print("\n[2/5] Installing pnpm...")
        if not install_pnpm():
            print("  [WARN] Using npm instead")

    # Clone
    print("\n[3/5] Cloning extension...")
    if not clone_extension():
        return False
    print(f"  Cloned to: {EXTENSION_DIR}")

    # Install deps
    print("\n[4/5] Installing node modules...")
    if not install_dependencies():
        return False
    print("  Dependencies installed")

    # Build
    print("\n[5/5] Building extension...")
    if not build_extension():
        return False
    print(f"  Built to: {get_extension_dist_path()}")

    print("\n" + "=" * 60)
    print("[SETUP COMPLETE]")
    print("=" * 60)
    print(f"\nExtension ready at: {get_extension_dist_path()}")
    print("\nNext steps:")
    print("  1. Run: python setup_suno_extension.py launch")
    print("  2. Browse to Suno songs")
    print("  3. Click LRC download button on each song")
    print(f"  4. Files save to: {LRC_OUTPUT_DIR}")
    print("  5. Import: python ffcpln_lyrics_library.py bulk-import --folder", LRC_OUTPUT_DIR)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Setup Suno Lyrics Extension",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  install   - Clone, install dependencies, and build extension
  launch    - Open Chrome with extension loaded
  status    - Check installation status
  uninstall - Remove extension (preserves LRC files)

Examples:
  python setup_suno_extension.py install
  python setup_suno_extension.py launch
  python setup_suno_extension.py status
        """
    )

    parser.add_argument("command", nargs="?", default="status",
                        choices=["install", "launch", "status", "uninstall"],
                        help="Command to run")

    args = parser.parse_args()

    if args.command == "install":
        full_install()

    elif args.command == "launch":
        if not get_extension_dist_path().exists():
            print("[ERROR] Extension not installed. Run: python setup_suno_extension.py install")
            return
        launch_chrome_with_extension()

    elif args.command == "status":
        status = get_status()
        print("\n[SUNO EXTENSION STATUS]")
        print("-" * 40)
        print("Dependencies:")
        for dep, ok in status["dependencies"].items():
            print(f"  {dep:10} {'OK' if ok else 'MISSING'}")
        print(f"\nExtension cloned: {'Yes' if status['extension_cloned'] else 'No'}")
        print(f"Extension built:  {'Yes' if status['extension_built'] else 'No'}")
        print(f"LRC output dir:   {status['lrc_output_dir']}")
        print(f"LRC files:        {status['lrc_files_count']}")

        if not status["extension_built"]:
            print("\n[TIP] Run: python setup_suno_extension.py install")

    elif args.command == "uninstall":
        uninstall()


if __name__ == "__main__":
    main()
