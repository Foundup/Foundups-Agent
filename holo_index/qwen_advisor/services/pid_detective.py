# -*- coding: utf-8 -*-
"""
PID Detective - HoloDAE Process Detection and Management

Extracted from holodae_coordinator.py per WSP 62 remediation.
Sprint H1: First extraction (lowest coupling).

WSP Compliance:
- WSP 62: Modularity Enforcement (<500 lines)
- WSP 91: Structured logging for observability
- WSP 49: Module structure compliance

Usage:
    from holo_index.qwen_advisor.services.pid_detective import PIDDetective
    
    detective = PIDDetective()
    issues = detective.check_pid_health()
    detective.show_pid_detective()
"""

from datetime import datetime
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class PIDDetective:
    """
    Detect and manage HoloDAE daemon processes.
    
    Provides:
    - Process health checks
    - Instance type identification
    - Orphan detection
    - Interactive process management
    """

    def check_pid_health(self) -> List[str]:
        """
        Quick health check for HoloDAE processes.
        
        Returns:
            List of health issues with PID identification.
        """
        issues = []

        try:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("holodae_daemon")

            instance_summary = lock.get_instance_summary()
            total_instances = instance_summary["total_instances"]
            instances = instance_summary.get("instances", [])
            current_pid = instance_summary["current_pid"]

            active_instances = []
            orphan_instances = []
            duplicate_launches = []

            for instance in instances:
                pid = instance.get('pid')
                if not pid:
                    continue

                try:
                    import psutil
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        cmdline = ' '.join(proc.cmdline()) if proc.cmdline() else 'unknown'
                        name = proc.name()

                        instance_type = self._identify_holodae_instance_type(cmdline, name, pid)

                        active_instances.append({
                            'pid': pid,
                            'type': instance_type,
                            'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                            'cpu_percent': proc.cpu_percent(),
                            'memory_mb': proc.memory_info().rss / 1024 / 1024 if proc.memory_info() else 0
                        })

                        if 'main.py' in cmdline and pid != current_pid:
                            duplicate_launches.append(pid)
                    else:
                        orphan_instances.append(pid)

                except ImportError:
                    if pid == current_pid:
                        active_instances.append({'pid': pid, 'type': 'current_session', 'cmdline': 'current'})
                    else:
                        orphan_instances.append(pid)
                except Exception:
                    orphan_instances.append(pid)

            # Generate health report
            if duplicate_launches:
                issues.append(f"[ALERT] DUPLICATE LAUNCHES: {len(duplicate_launches)} extra main.py sessions")
                issues.append(f"   PIDs: {', '.join(map(str, duplicate_launches))}")

            if orphan_instances:
                issues.append(f"ORPHAN PROCESSES: {len(orphan_instances)} dead locks")
                issues.append(f"   PIDs: {', '.join(map(str, orphan_instances))}")

            if len(active_instances) > 1:
                necessary_count = sum(1 for inst in active_instances 
                                     if inst['type'] in ['current_session', 'daemon_monitor', 'specialized_analysis'])
                duplicate_count = len(active_instances) - necessary_count

                if duplicate_count > 0:
                    issues.append(f"POTENTIAL DUPLICATES: {duplicate_count} unnecessary instances")

            total_memory = sum(inst.get('memory_mb', 0) for inst in active_instances)
            if total_memory > 1000:
                issues.append(f"HIGH MEMORY: {total_memory:.1f}MB total")

            if not issues:
                if total_instances == 0:
                    issues.append("[OK] CLEAN: No HoloDAE processes running")
                elif total_instances == 1:
                    issues.append("[OK] CLEAN: Single HoloDAE session running")
                else:
                    issues.append(f"[OK] CLEAN: {total_instances} HoloDAE processes running normally")

        except Exception as e:
            issues.append(f"[FAIL] PID health check failed: {e}")

        return issues

    def _identify_holodae_instance_type(self, cmdline: str, name: str, pid: int) -> str:
        """Identify what type of HoloDAE process this is."""
        cmdline_lower = cmdline.lower()

        if 'main.py' in cmdline_lower and 'python' in name.lower():
            return 'main_menu_session'
        if 'holodae' in cmdline_lower and 'monitor' in cmdline_lower:
            return 'daemon_monitor'
        if 'mcp' in cmdline_lower or 'research' in cmdline_lower:
            return 'mcp_service'
        if 'analysis' in cmdline_lower or 'intelligence' in cmdline_lower:
            return 'analysis_worker'
        if 'pqn' in cmdline_lower:
            return 'pqn_analysis'
        if 'youtube' in cmdline_lower:
            return 'youtube_analysis'
        if 'social' in cmdline_lower:
            return 'social_analysis'
        if 'holodae' in cmdline_lower:
            return 'holodae_daemon'

        return 'unknown_holodae'

    def get_process_details(self, pid: int) -> Dict[str, Any]:
        """Get detailed information about a specific process."""
        details = {'type': 'unknown', 'cmdline': '', 'cpu_percent': None, 'memory_mb': None}

        try:
            import psutil
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                cmdline = ' '.join(proc.cmdline()) if proc.cmdline() else 'unknown'
                name = proc.name()

                details.update({
                    'type': self._identify_holodae_instance_type(cmdline, name, pid),
                    'cmdline': cmdline[:150] + '...' if len(cmdline) > 150 else cmdline,
                    'cpu_percent': proc.cpu_percent(),
                    'memory_mb': proc.memory_info().rss / 1024 / 1024 if proc.memory_info() else 0
                })
        except ImportError:
            details['type'] = 'basic_info_unavailable'
        except Exception as e:
            details['error'] = str(e)

        return details

    def show_pid_detective(self) -> None:
        """Detect and manage HoloDAE daemon processes for clean operation."""
        print('\n[TOOL] PID Detective — HoloDAE Process Management')
        print('=' * 60)

        try:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("holodae_daemon")

            instance_summary = lock.get_instance_summary()
            total_instances = instance_summary["total_instances"]
            current_pid = instance_summary["current_pid"]
            instances = instance_summary.get("instances", [])

            print(f"Current Process PID: {current_pid}")
            print(f"Total HoloDAE Instances: {total_instances}")
            print()

            if total_instances <= 1:
                print("[OK] Clean state: Single HoloDAE instance detected")
                return

            print("[ALERT] Multiple HoloDAE instances detected!")
            print()

            # Detect orphans
            orphans = []
            for instance in instances:
                pid = instance.get('pid')
                if pid and pid != current_pid:
                    try:
                        import psutil
                        if not psutil.pid_exists(pid):
                            orphans.append(pid)
                    except ImportError:
                        orphans.append(pid)

            if orphans:
                print(f"Orphan PIDs: {', '.join(map(str, orphans))}")

            print()
            print("Options: 1=Clean orphans, 0=Return")

            try:
                choice = input("Select: ").strip()
                if choice == "1":
                    for orphan_pid in orphans:
                        try:
                            lock.release_orphan_lock(orphan_pid)
                            print(f"[OK] Cleaned PID {orphan_pid}")
                        except Exception as e:
                            print(f"[FAIL] PID {orphan_pid}: {e}")
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled")

        except Exception as e:
            print(f"[FAIL] PID Detective failed: {e}")
            logger.exception("PID Detective error")
