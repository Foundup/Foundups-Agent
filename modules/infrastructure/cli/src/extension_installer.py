#!/usr/bin/env python3
"""
Chrome Extension Installer CLI

General-purpose CLI for installing Chrome extensions from GitHub.
Handles clone, npm/pnpm install, build, and Chrome launch.

Usage:
    # Install any extension:
    python extension_installer.py install --repo "https://github.com/user/extension"

    # Install with custom name:
    python extension_installer.py install --repo "..." --name "my-extension"

    # Launch Chrome with installed extension:
    python extension_installer.py launch --name "my-extension"

    # List installed extensions:
    python extension_installer.py list

    # Remove extension:
    python extension_installer.py remove --name "my-extension"

    # Install specific Suno lyrics extension:
    python extension_installer.py install --repo "https://github.com/zh30/get-suno-lyric" --name "suno-lyrics"
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Storage paths
EXTENSIONS_DIR = PROJECT_ROOT / "data" / "chrome_extensions"
REGISTRY_FILE = EXTENSIONS_DIR / "registry.json"
CHROME_PROFILE_DIR = EXTENSIONS_DIR / "chrome_profile"


@dataclass
class ExtensionInfo:
    """Installed extension metadata."""
    name: str
    repo_url: str
    local_path: str
    dist_path: str
    installed_at: str
    last_built: str
    status: str  # installed, built, error


class ExtensionRegistry:
    """Manages installed extensions."""

    def __init__(self):
        self.extensions: Dict[str, ExtensionInfo] = {}
        self._load()

    def _load(self):
        """Load registry from file."""
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, 'r') as f:
                data = json.load(f)
                for name, info in data.items():
                    self.extensions[name] = ExtensionInfo(**info)

    def save(self):
        """Save registry to file."""
        REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {name: asdict(info) for name, info in self.extensions.items()}
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def add(self, ext: ExtensionInfo):
        """Add extension to registry."""
        self.extensions[ext.name] = ext
        self.save()

    def remove(self, name: str):
        """Remove extension from registry."""
        if name in self.extensions:
            del self.extensions[name]
            self.save()

    def get(self, name: str) -> Optional[ExtensionInfo]:
        """Get extension by name."""
        return self.extensions.get(name)

    def list_all(self) -> List[ExtensionInfo]:
        """List all installed extensions."""
        return list(self.extensions.values())


def check_dependencies() -> Dict[str, bool]:
    """Check required tools."""
    deps = {}

    for cmd in ["git", "node", "npm", "pnpm"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, shell=True)
            deps[cmd] = result.returncode == 0
        except FileNotFoundError:
            deps[cmd] = False

    # Check Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
    ]
    deps["chrome"] = any(Path(p).exists() for p in chrome_paths)

    return deps


def get_chrome_path() -> Optional[str]:
    """Find Chrome executable."""
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
    ]
    for p in paths:
        if Path(p).exists():
            return p
    return None


def extract_name_from_repo(repo_url: str) -> str:
    """Extract extension name from repo URL."""
    # https://github.com/user/repo-name -> repo-name
    name = repo_url.rstrip('/').split('/')[-1]
    if name.endswith('.git'):
        name = name[:-4]
    return name


def find_dist_path(local_path: Path) -> Optional[Path]:
    """Find built extension output directory."""
    # Common output directories
    candidates = [
        local_path / "dist",
        local_path / "build",
        local_path / "out",
        local_path / "extension",
        local_path / "output",
    ]

    for path in candidates:
        if path.exists() and (path / "manifest.json").exists():
            return path

    # Check if manifest.json in root (no build step needed)
    if (local_path / "manifest.json").exists():
        return local_path

    # Check first level subdirs
    for subdir in local_path.iterdir():
        if subdir.is_dir() and (subdir / "manifest.json").exists():
            return subdir

    return None


def install_extension(repo_url: str, name: Optional[str] = None,
                      force: bool = False) -> Optional[ExtensionInfo]:
    """
    Install Chrome extension from GitHub.

    Args:
        repo_url: GitHub repository URL
        name: Custom name (defaults to repo name)
        force: Overwrite if exists

    Returns:
        ExtensionInfo or None on failure
    """
    registry = ExtensionRegistry()

    # Determine name
    if not name:
        name = extract_name_from_repo(repo_url)

    local_path = EXTENSIONS_DIR / name

    def handle_remove_readonly(func, path, exc):
        """Handle read-only files on Windows."""
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # Check if exists
    if local_path.exists() and not force:
        existing = registry.get(name)
        if existing:
            logger.info(f"[INSTALL] Extension '{name}' already installed")
            logger.info(f"[INSTALL] Use --force to reinstall")
            return existing
        # Directory exists but not in registry - clean up
        shutil.rmtree(local_path, onexc=handle_remove_readonly)

    if local_path.exists() and force:
        logger.info(f"[INSTALL] Removing existing: {local_path}")
        shutil.rmtree(local_path, onexc=handle_remove_readonly)

    # Check dependencies
    deps = check_dependencies()
    if not deps["git"]:
        logger.error("[INSTALL] Git not found. Install from: https://git-scm.com/")
        return None
    if not deps["node"]:
        logger.error("[INSTALL] Node.js not found. Install from: https://nodejs.org/")
        return None

    # Clone repository
    logger.info(f"[INSTALL] Cloning {repo_url}...")
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            f'git clone "{repo_url}" "{local_path}"',
            check=True,
            capture_output=True,
            shell=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"[INSTALL] Clone failed: {e.stderr.decode()}")
        return None

    # Install dependencies
    logger.info("[INSTALL] Installing dependencies...")
    package_manager = "pnpm" if deps["pnpm"] else "npm"

    # Check for package.json
    if (local_path / "package.json").exists():
        try:
            subprocess.run(
                f"{package_manager} install",
                cwd=str(local_path),
                check=True,
                capture_output=True,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"[INSTALL] npm install failed: {e.stderr.decode()[:200]}")

    # Build extension
    logger.info("[INSTALL] Building extension...")
    build_scripts = ["build", "build:extension", "build:chrome", "compile"]

    built = False
    for script in build_scripts:
        try:
            result = subprocess.run(
                f"{package_manager} run {script}",
                cwd=str(local_path),
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                built = True
                break
        except:
            continue

    if not built:
        logger.warning("[INSTALL] No build script found or build failed")
        logger.warning("[INSTALL] Extension may not require building")

    # Find dist path
    dist_path = find_dist_path(local_path)

    if not dist_path:
        logger.error("[INSTALL] Could not find built extension (no manifest.json)")
        logger.error("[INSTALL] Check the extension's README for build instructions")
        # Still register so user can manually fix
        dist_path = local_path

    # Create extension info
    ext_info = ExtensionInfo(
        name=name,
        repo_url=repo_url,
        local_path=str(local_path),
        dist_path=str(dist_path) if dist_path else "",
        installed_at=datetime.now().isoformat(),
        last_built=datetime.now().isoformat() if built else "",
        status="built" if dist_path and (dist_path / "manifest.json").exists() else "installed"
    )

    registry.add(ext_info)

    logger.info(f"[INSTALL] Extension '{name}' installed successfully")
    logger.info(f"[INSTALL] Location: {local_path}")
    if dist_path:
        logger.info(f"[INSTALL] Dist: {dist_path}")

    return ext_info


def launch_chrome(name: str, url: str = ""):
    """Launch Chrome with extension loaded."""
    registry = ExtensionRegistry()
    ext = registry.get(name)

    if not ext:
        logger.error(f"[LAUNCH] Extension '{name}' not found")
        logger.error("[LAUNCH] Install first: python extension_installer.py install --repo <url>")
        return False

    if not ext.dist_path or not Path(ext.dist_path).exists():
        logger.error(f"[LAUNCH] Extension dist path not found: {ext.dist_path}")
        return False

    chrome = get_chrome_path()
    if not chrome:
        logger.error("[LAUNCH] Chrome not found")
        return False

    # Create profile dir
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        chrome,
        f"--load-extension={ext.dist_path}",
        f"--user-data-dir={CHROME_PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    if url:
        cmd.append(url)

    logger.info(f"[LAUNCH] Starting Chrome with extension: {name}")
    subprocess.Popen(cmd)
    return True


def list_extensions():
    """List all installed extensions."""
    registry = ExtensionRegistry()
    extensions = registry.list_all()

    if not extensions:
        print("\n[EXTENSIONS] No extensions installed")
        print("[TIP] Install one: python extension_installer.py install --repo <url>")
        return

    print("\n[INSTALLED EXTENSIONS]")
    print("-" * 70)
    for ext in extensions:
        status_icon = "OK" if ext.status == "built" else "?"
        print(f"  [{status_icon}] {ext.name}")
        print(f"      Repo: {ext.repo_url}")
        print(f"      Path: {ext.dist_path}")
        print(f"      Installed: {ext.installed_at[:10]}")
        print()


def remove_extension(name: str):
    """Remove installed extension."""
    registry = ExtensionRegistry()
    ext = registry.get(name)

    if not ext:
        logger.error(f"[REMOVE] Extension '{name}' not found")
        return False

    # Remove directory
    local_path = Path(ext.local_path)
    if local_path.exists():
        shutil.rmtree(local_path)
        logger.info(f"[REMOVE] Deleted: {local_path}")

    # Remove from registry
    registry.remove(name)
    logger.info(f"[REMOVE] Extension '{name}' removed")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Chrome Extension Installer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  install   - Clone, build, and install extension from GitHub
  launch    - Open Chrome with extension loaded
  list      - List installed extensions
  remove    - Uninstall extension

Examples:
  # Install Suno lyrics extension:
  python extension_installer.py install --repo "https://github.com/zh30/get-suno-lyric" --name "suno-lyrics"

  # Launch Chrome with extension:
  python extension_installer.py launch --name "suno-lyrics" --url "https://suno.com"

  # List installed:
  python extension_installer.py list

  # Remove:
  python extension_installer.py remove --name "suno-lyrics"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Install
    install_parser = subparsers.add_parser("install", help="Install extension from GitHub")
    install_parser.add_argument("--repo", "-r", required=True, help="GitHub repository URL")
    install_parser.add_argument("--name", "-n", help="Custom extension name")
    install_parser.add_argument("--force", "-f", action="store_true", help="Force reinstall")

    # Launch
    launch_parser = subparsers.add_parser("launch", help="Launch Chrome with extension")
    launch_parser.add_argument("--name", "-n", required=True, help="Extension name")
    launch_parser.add_argument("--url", "-u", default="", help="URL to open")

    # List
    subparsers.add_parser("list", help="List installed extensions")

    # Remove
    remove_parser = subparsers.add_parser("remove", help="Remove extension")
    remove_parser.add_argument("--name", "-n", required=True, help="Extension name")

    # Status (check dependencies)
    subparsers.add_parser("status", help="Check dependencies")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "install":
        ext = install_extension(args.repo, args.name, args.force)
        if ext:
            print(f"\n[SUCCESS] Extension '{ext.name}' ready")
            print(f"[NEXT] Launch: python extension_installer.py launch --name {ext.name}")

    elif args.command == "launch":
        launch_chrome(args.name, args.url)

    elif args.command == "list":
        list_extensions()

    elif args.command == "remove":
        remove_extension(args.name)

    elif args.command == "status":
        deps = check_dependencies()
        print("\n[DEPENDENCIES]")
        for dep, ok in deps.items():
            status = "OK" if ok else "MISSING"
            print(f"  {dep:10} {status}")


if __name__ == "__main__":
    main()
