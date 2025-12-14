"""
Browser Health Check - Diagnostic tool for detecting multiple browser instances

Detects:
- Multiple Chrome/Edge processes with same profile
- Orphaned browser instances
- BrowserManager singleton usage violations
- Browser lifecycle issues

WSP Compliance:
    - WSP 91: Observability and monitoring
    - WSP 77: AI Overseer integration

Usage:
    python browser_health_check.py
    python browser_health_check.py --profile youtube_move2japan
    python browser_health_check.py --kill-orphans
"""

import argparse
import logging
import os
import psutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class BrowserHealthCheck:
    """Health check for browser instances."""

    def __init__(self):
        """Initialize health check."""
        self.issues_found = []
        self.chrome_processes = []
        self.edge_processes = []

    def scan_browser_processes(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Scan for Chrome and Edge browser processes.

        Returns:
            Tuple of (chrome_processes, edge_processes)
        """
        chrome_procs = []
        edge_procs = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                name = proc.info['name'].lower()
                cmdline = proc.info['cmdline'] or []

                if 'chrome.exe' in name:
                    chrome_procs.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(cmdline),
                        'created': datetime.fromtimestamp(proc.info['create_time']),
                        'profile': self._extract_profile_from_cmdline(cmdline),
                        'remote_debugging': self._extract_remote_debugging_port(cmdline),
                    })
                elif 'msedge.exe' in name:
                    edge_procs.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(cmdline),
                        'created': datetime.fromtimestamp(proc.info['create_time']),
                        'profile': self._extract_profile_from_cmdline(cmdline),
                        'remote_debugging': self._extract_remote_debugging_port(cmdline),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        self.chrome_processes = chrome_procs
        self.edge_processes = edge_procs

        return chrome_procs, edge_procs

    def _extract_profile_from_cmdline(self, cmdline: List[str]) -> str:
        """Extract profile directory from command line arguments."""
        for arg in cmdline:
            if '--user-data-dir=' in arg:
                return arg.split('=', 1)[1]
        return 'default'

    def _extract_remote_debugging_port(self, cmdline: List[str]) -> int:
        """Extract remote debugging port from command line."""
        for arg in cmdline:
            if '--remote-debugging-port=' in arg:
                try:
                    return int(arg.split('=', 1)[1])
                except ValueError:
                    pass
        return None

    def check_duplicate_profiles(self) -> List[Dict]:
        """
        Check for multiple browser instances with same profile.

        Returns:
            List of duplicate profile violations
        """
        violations = []

        # Group Chrome processes by profile
        chrome_by_profile = defaultdict(list)
        for proc in self.chrome_processes:
            chrome_by_profile[proc['profile']].append(proc)

        # Group Edge processes by profile
        edge_by_profile = defaultdict(list)
        for proc in self.edge_processes:
            edge_by_profile[proc['profile']].append(proc)

        # Check for duplicates
        for profile, procs in chrome_by_profile.items():
            if len(procs) > 1:
                violations.append({
                    'browser': 'Chrome',
                    'profile': profile,
                    'count': len(procs),
                    'pids': [p['pid'] for p in procs],
                    'created_times': [p['created'] for p in procs],
                })
                self.issues_found.append(f"[WARN] Multiple Chrome instances for profile: {profile} (PIDs: {', '.join(str(p['pid']) for p in procs)})")

        for profile, procs in edge_by_profile.items():
            if len(procs) > 1:
                violations.append({
                    'browser': 'Edge',
                    'profile': profile,
                    'count': len(procs),
                    'pids': [p['pid'] for p in procs],
                    'created_times': [p['created'] for p in procs],
                })
                self.issues_found.append(f"[WARN] Multiple Edge instances for profile: {profile} (PIDs: {', '.join(str(p['pid']) for p in procs)})")

        return violations

    def check_orphaned_browsers(self) -> List[Dict]:
        """
        Check for orphaned browser instances (no parent Python process).

        Returns:
            List of orphaned browser processes
        """
        orphaned = []

        all_browsers = self.chrome_processes + self.edge_processes

        for browser in all_browsers:
            try:
                proc = psutil.Process(browser['pid'])
                parent = proc.parent()

                # Check if parent is a Python process
                if parent:
                    parent_name = parent.name().lower()
                    if 'python' not in parent_name:
                        orphaned.append({
                            'browser': browser['name'],
                            'pid': browser['pid'],
                            'profile': browser['profile'],
                            'parent_pid': parent.pid,
                            'parent_name': parent.name(),
                        })
                        self.issues_found.append(f"[INFO] Potentially orphaned browser: {browser['name']} PID={browser['pid']}, parent={parent.name()}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return orphaned

    def check_remote_debugging_conflicts(self) -> List[Dict]:
        """
        Check for multiple browsers on same remote debugging port.

        Returns:
            List of port conflicts
        """
        conflicts = []
        port_usage = defaultdict(list)

        # Group browsers by port
        for proc in self.chrome_processes + self.edge_processes:
            port = proc.get('remote_debugging')
            if port:
                port_usage[port].append(proc)

        # Check for conflicts
        for port, procs in port_usage.items():
            if len(procs) > 1:
                conflicts.append({
                    'port': port,
                    'count': len(procs),
                    'processes': procs,
                })
                proc_list = ', '.join(f"{p['name']}({p['pid']})" for p in procs)
                self.issues_found.append(f"[ERROR] Multiple browsers on port {port}: {proc_list}")

        return conflicts

    def generate_report(self, profile_filter: str = None) -> str:
        """
        Generate health check report.

        Args:
            profile_filter: Optional profile name to filter by

        Returns:
            Report string
        """
        report = []
        report.append("=" * 80)
        report.append("BROWSER HEALTH CHECK REPORT")
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("=" * 80)

        # Summary
        chrome_count = len(self.chrome_processes)
        edge_count = len(self.edge_processes)

        if profile_filter:
            chrome_count = sum(1 for p in self.chrome_processes if profile_filter in p['profile'])
            edge_count = sum(1 for p in self.edge_processes if profile_filter in p['profile'])
            report.append(f"\nFilter: profile={profile_filter}")

        report.append(f"\nBrowser Instances:")
        report.append(f"  Chrome: {chrome_count}")
        report.append(f"  Edge:   {edge_count}")
        report.append(f"  Total:  {chrome_count + edge_count}")

        # List processes
        report.append(f"\nChrome Processes:")
        for proc in self.chrome_processes:
            if profile_filter and profile_filter not in proc['profile']:
                continue
            port_str = f" (debug port: {proc['remote_debugging']})" if proc['remote_debugging'] else ""
            report.append(f"  PID {proc['pid']}: {proc['profile']}{port_str}")
            report.append(f"           Created: {proc['created']}")

        report.append(f"\nEdge Processes:")
        for proc in self.edge_processes:
            if profile_filter and profile_filter not in proc['profile']:
                continue
            port_str = f" (debug port: {proc['remote_debugging']})" if proc['remote_debugging'] else ""
            report.append(f"  PID {proc['pid']}: {proc['profile']}{port_str}")
            report.append(f"           Created: {proc['created']}")

        # Issues
        if self.issues_found:
            report.append(f"\nISSUES DETECTED ({len(self.issues_found)}):")
            for issue in self.issues_found:
                report.append(f"  {issue}")
        else:
            report.append(f"\n[OK] No issues detected")

        # Recommendations
        report.append(f"\nRECOMMENDATIONS:")
        duplicate_violations = self.check_duplicate_profiles()
        if duplicate_violations:
            report.append(f"  1. Multiple browser instances detected for same profile - use BrowserManager singleton")
            report.append(f"     from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager")
            report.append(f"     browser_manager = get_browser_manager()")
            report.append(f"     browser = browser_manager.get_browser('chrome', 'profile_name')")

        port_conflicts = self.check_remote_debugging_conflicts()
        if port_conflicts:
            report.append(f"  2. Remote debugging port conflicts detected - each browser needs unique port")

        orphaned = self.check_orphaned_browsers()
        if orphaned:
            report.append(f"  3. Orphaned browsers detected - use browser_manager.close_all_browsers() or kill manually")

        report.append("=" * 80)

        return "\n".join(report)

    def kill_orphaned_browsers(self, dry_run: bool = True) -> List[int]:
        """
        Kill orphaned browser processes.

        Args:
            dry_run: If True, only simulate killing (don't actually kill)

        Returns:
            List of killed PIDs
        """
        orphaned = self.check_orphaned_browsers()
        killed_pids = []

        for orphan in orphaned:
            pid = orphan['pid']
            if dry_run:
                logger.info(f"[DRY-RUN] Would kill {orphan['browser']} PID={pid}")
            else:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    killed_pids.append(pid)
                    logger.info(f"[KILLED] {orphan['browser']} PID={pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"[FAILED] Could not kill PID={pid}: {e}")

        return killed_pids


def main():
    """Run browser health check."""
    parser = argparse.ArgumentParser(description="Browser Health Check Tool")
    parser.add_argument('--profile', help="Filter by profile name")
    parser.add_argument('--kill-orphans', action='store_true', help="Kill orphaned browser processes")
    parser.add_argument('--dry-run', action='store_true', help="Dry run (don't kill processes)")
    args = parser.parse_args()

    checker = BrowserHealthCheck()
    checker.scan_browser_processes()

    # Run health checks
    checker.check_duplicate_profiles()
    checker.check_orphaned_browsers()
    checker.check_remote_debugging_conflicts()

    # Generate report
    report = checker.generate_report(profile_filter=args.profile)
    print(report)

    # Kill orphaned browsers if requested
    if args.kill_orphans:
        if args.dry_run:
            print("\n[DRY-RUN MODE] - No processes will be killed")
        killed = checker.kill_orphaned_browsers(dry_run=args.dry_run)
        if killed:
            print(f"\nKilled {len(killed)} orphaned browsers")

    # Exit code
    sys.exit(1 if checker.issues_found else 0)


if __name__ == "__main__":
    main()
