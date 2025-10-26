# -*- coding: utf-8 -*-
"""
Audit LinkedIn Scheduling Queue Mission
Comprehensive audit of all LinkedIn scheduling queues and pending approvals.

WSP 77: Agent Coordination Protocol
WSP 60: Memory Compliance
WSP 50: Pre-Action Verification
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

# Apply WSP 90 UTF-8 enforcement
if __name__ == '__main__':
    import sys
    import io
    if sys.platform.startswith('win'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except (OSError, ValueError):
            pass

logger = logging.getLogger(__name__)


class AuditLinkedInSchedulingQueueMission:
    """
    Mission to audit all LinkedIn scheduling queues and identify issues.

    Inventories active queue entries across:
    - UI-TARS Scheduler
    - Unified LinkedIn Interface
    - Simple Posting Orchestrator
    - Vision DAE dispatches

    WSP 77: Agent Coordination
    WSP 60: Memory Compliance
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.memory_dir = self.project_root / "memory"
        self.session_summaries_dir = self.memory_dir / "session_summaries"
        self.ui_tars_dispatches_dir = self.memory_dir / "ui_tars_dispatches"

        # Queue sources to audit
        self.queue_sources = {
            'ui_tars_scheduler': self._audit_ui_tars_scheduler,
            'unified_linkedin_interface': self._audit_unified_linkedin_interface,
            'simple_posting_orchestrator': self._audit_simple_posting_orchestrator,
            'vision_dae_dispatches': self._audit_vision_dae_dispatches,
            'memory_compliance': self._audit_memory_compliance
        }

    def execute_mission(self) -> Dict[str, Any]:
        """
        Execute the LinkedIn scheduling queue audit mission.

        Returns:
            Comprehensive audit results with queue status, issues, and cleanup recommendations
        """
        logger.info("[AUDIT MISSION] Starting LinkedIn scheduling queue audit")

        audit_results = {
            'mission': 'audit_linkedin_scheduling_queue',
            'timestamp': datetime.now().isoformat(),
            'wsp_compliance': {
                'wsp_50_pre_action_verification': True,
                'wsp_77_agent_coordination': True,
                'wsp_60_memory_compliance': True
            },
            'queue_inventory': {},
            'issues_found': [],
            'cleanup_recommendations': [],
            'summary_stats': {}
        }

        # Audit each queue source
        for source_name, audit_func in self.queue_sources.items():
            try:
                logger.info(f"[AUDIT MISSION] Auditing {source_name}")
                result = audit_func()
                audit_results['queue_inventory'][source_name] = result

                # Collect issues and recommendations
                if 'issues' in result:
                    audit_results['issues_found'].extend(result['issues'])
                if 'cleanup_recommendations' in result:
                    audit_results['cleanup_recommendations'].extend(result['cleanup_recommendations'])

            except Exception as e:
                logger.error(f"[AUDIT MISSION] Failed to audit {source_name}: {e}")
                audit_results['queue_inventory'][source_name] = {
                    'status': 'error',
                    'error': str(e)
                }

        # Calculate summary statistics
        audit_results['summary_stats'] = self._calculate_summary_stats(audit_results)

        # Log to ModLog
        self._log_audit_results(audit_results)

        logger.info(f"[AUDIT MISSION] Audit complete - {len(audit_results['issues_found'])} issues found")
        return audit_results

    def _audit_ui_tars_scheduler(self) -> Dict[str, Any]:
        """Audit UI-TARS scheduler queue"""
        try:
            # Check UI-TARS inbox
            ui_tars_inbox = Path("E:/HoloIndex/models/ui-tars-1.5/telemetry")
            scheduled_posts_file = ui_tars_inbox / "scheduled_posts.json"

            if not scheduled_posts_file.exists():
                return {
                    'status': 'empty',
                    'queue_size': 0,
                    'scheduled_posts': [],
                    'issues': ['UI-TARS inbox not found'],
                    'cleanup_recommendations': []
                }

            with open(scheduled_posts_file, 'r', encoding='utf-8') as f:
                scheduled_posts = json.load(f)

            # Analyze posts
            issues = []
            cleanup_recommendations = []
            old_posts = []

            for post in scheduled_posts:
                scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                age_days = (datetime.now() - scheduled_time).days

                if age_days > 30:
                    old_posts.append(post)
                    cleanup_recommendations.append(
                        f"Remove old scheduled post: {post['draft_hash'][:8]}... "
                        f"(scheduled {age_days} days ago)"
                    )

            return {
                'status': 'active',
                'queue_size': len(scheduled_posts),
                'scheduled_posts': scheduled_posts,
                'old_posts_count': len(old_posts),
                'issues': issues,
                'cleanup_recommendations': cleanup_recommendations
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'issues': [f'UI-TARS scheduler audit failed: {str(e)}'],
                'cleanup_recommendations': []
            }

    def _audit_unified_linkedin_interface(self) -> Dict[str, Any]:
        """Audit Unified LinkedIn Interface history"""
        try:
            history_file = self.memory_dir / "unified_linkedin_history.json"

            if not history_file.exists():
                return {
                    'status': 'empty',
                    'history_size': 0,
                    'recent_posts': [],
                    'issues': ['Unified LinkedIn history not found'],
                    'cleanup_recommendations': []
                }

            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # Analyze recent activity
            recent_posts = []
            issues = []
            cleanup_recommendations = []

            # Check for very old entries (placeholder - would need date parsing)
            if len(history) > 1000:  # Arbitrary large number
                cleanup_recommendations.append(
                    f"Consider archiving old history: {len(history)} entries"
                )

            return {
                'status': 'active',
                'history_size': len(history),
                'recent_posts': recent_posts,
                'issues': issues,
                'cleanup_recommendations': cleanup_recommendations
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'issues': [f'Unified LinkedIn interface audit failed: {str(e)}'],
                'cleanup_recommendations': []
            }

    def _audit_simple_posting_orchestrator(self) -> Dict[str, Any]:
        """Audit Simple Posting Orchestrator state"""
        try:
            posted_history_file = self.memory_dir / "posted_streams.json"

            if not posted_history_file.exists():
                return {
                    'status': 'empty',
                    'posted_count': 0,
                    'issues': ['Posted streams history not found'],
                    'cleanup_recommendations': []
                }

            with open(posted_history_file, 'r', encoding='utf-8') as f:
                posted_history = json.load(f)

            # Analyze posting history
            issues = []
            cleanup_recommendations = []

            posted_count = 0
            old_entries = []

            if isinstance(posted_history, list):
                # Handle array format
                posted_count = len(posted_history)
                # Arrays don't have timestamps, so we can't check for old entries
                cleanup_recommendations.append(
                    f"Consider migrating posted_streams.json from array to dict format with timestamps"
                )
            elif isinstance(posted_history, dict):
                # Handle dict format
                posted_count = len(posted_history)

                # Check for old entries
                cutoff_date = datetime.now() - timedelta(days=90)

                for stream_id, data in posted_history.items():
                    if isinstance(data, dict) and 'timestamp' in data:
                        try:
                            post_date = datetime.fromisoformat(data['timestamp'])
                            if post_date < cutoff_date:
                                old_entries.append(stream_id)
                        except:
                            pass

                if old_entries:
                    cleanup_recommendations.append(
                        f"Archive {len(old_entries)} old stream entries (>90 days)"
                    )

            return {
                'status': 'active',
                'posted_count': posted_count,
                'old_entries_count': len(old_entries),
                'data_format': 'array' if isinstance(posted_history, list) else 'dict',
                'issues': issues,
                'cleanup_recommendations': cleanup_recommendations
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'issues': [f'Simple posting orchestrator audit failed: {str(e)}'],
                'cleanup_recommendations': []
            }

    def _audit_vision_dae_dispatches(self) -> Dict[str, Any]:
        """Audit Vision DAE UI-TARS dispatches"""
        try:
            ui_tars_inbox = Path("E:/HoloIndex/models/ui-tars-1.5/telemetry")
            dispatch_files = list(ui_tars_inbox.glob("vision_summary_*.json"))

            # Also check local dispatches
            local_dispatches = list(self.ui_tars_dispatches_dir.glob("*.json")) if self.ui_tars_dispatches_dir.exists() else []

            total_dispatches = len(dispatch_files) + len(local_dispatches)

            # Analyze dispatch files
            issues = []
            cleanup_recommendations = []

            # Check for old dispatch files
            old_files = []
            cutoff_date = datetime.now() - timedelta(days=30)

            for dispatch_file in dispatch_files + local_dispatches:
                try:
                    # Extract timestamp from filename
                    filename = dispatch_file.name
                    if 'vision_summary_' in filename:
                        # Parse timestamp from filename
                        timestamp_str = filename.replace('vision_summary_', '').replace('.json', '')
                        file_date = datetime.fromisoformat(timestamp_str.replace('_', 'T'))

                        if file_date < cutoff_date:
                            old_files.append(dispatch_file)
                except:
                    pass

            if old_files:
                cleanup_recommendations.append(
                    f"Archive {len(old_files)} old Vision DAE dispatch files (>30 days)"
                )

            return {
                'status': 'active' if total_dispatches > 0 else 'empty',
                'total_dispatches': total_dispatches,
                'ui_tars_dispatches': len(dispatch_files),
                'local_dispatches': len(local_dispatches),
                'old_files_count': len(old_files),
                'issues': issues,
                'cleanup_recommendations': cleanup_recommendations
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'issues': [f'Vision DAE dispatches audit failed: {str(e)}'],
                'cleanup_recommendations': []
            }

    def _audit_memory_compliance(self) -> Dict[str, Any]:
        """Audit WSP 60 Memory Compliance"""
        issues = []
        cleanup_recommendations = []

        # Check session_summaries directory
        if not self.session_summaries_dir.exists():
            issues.append("WSP 60 VIOLATION: memory/session_summaries directory missing")
            cleanup_recommendations.append("Create memory/session_summaries directory")
        else:
            summary_files = list(self.session_summaries_dir.glob("*.json"))
            if not summary_files:
                issues.append("WSP 60 WARNING: memory/session_summaries directory empty")
            else:
                # Check for old files
                old_files = []
                for summary_file in summary_files:
                    try:
                        # Check file modification time
                        mtime = datetime.fromtimestamp(summary_file.stat().st_mtime)
                        if mtime < datetime.now() - timedelta(days=30):
                            old_files.append(summary_file)
                    except:
                        pass

                if old_files:
                    cleanup_recommendations.append(
                        f"Archive {len(old_files)} old session summaries (>30 days)"
                    )

        # Check ui_tars_dispatches directory
        if not self.ui_tars_dispatches_dir.exists():
            issues.append("WSP 60 VIOLATION: memory/ui_tars_dispatches directory missing")
            cleanup_recommendations.append("Create memory/ui_tars_dispatches directory")
        else:
            dispatch_files = list(self.ui_tars_dispatches_dir.glob("*.json"))
            if not dispatch_files:
                issues.append("WSP 60 WARNING: memory/ui_tars_dispatches directory empty")

        return {
            'status': 'compliant' if not issues else 'non_compliant',
            'session_summaries_dir_exists': self.session_summaries_dir.exists(),
            'ui_tars_dispatches_dir_exists': self.ui_tars_dispatches_dir.exists(),
            'issues': issues,
            'cleanup_recommendations': cleanup_recommendations
        }

    def _calculate_summary_stats(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics across all queues"""
        total_queue_size = 0
        total_issues = len(audit_results['issues_found'])
        total_recommendations = len(audit_results['cleanup_recommendations'])

        # Aggregate queue sizes
        for source_name, source_data in audit_results['queue_inventory'].items():
            if isinstance(source_data, dict):
                total_queue_size += source_data.get('queue_size', 0)
                total_queue_size += source_data.get('posted_count', 0)
                total_queue_size += source_data.get('total_dispatches', 0)

        # Find scheduled times
        scheduled_times = []
        for source_name, source_data in audit_results['queue_inventory'].items():
            if source_name == 'ui_tars_scheduler' and 'scheduled_posts' in source_data:
                for post in source_data['scheduled_posts']:
                    try:
                        scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                        scheduled_times.append({
                            'time': scheduled_time.isoformat(),
                            'draft_hash': post['draft_hash'],
                            'content_preview': post['content'][:50] + '...'
                        })
                    except:
                        pass

        return {
            'total_queue_size': total_queue_size,
            'total_issues': total_issues,
            'total_cleanup_recommendations': total_recommendations,
            'scheduled_times': sorted(scheduled_times, key=lambda x: x['time']),
            'memory_compliance': audit_results['queue_inventory'].get('memory_compliance', {}).get('status', 'unknown')
        }

    def _log_audit_results(self, audit_results: Dict[str, Any]):
        """Log audit results to ModLog.md"""
        try:
            modlog_file = self.project_root / "ModLog.md"

            # Read existing ModLog
            existing_content = ""
            if modlog_file.exists():
                with open(modlog_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

            # Create audit log entry
            audit_entry = f"""
## LinkedIn Scheduling Queue Audit - {datetime.now().strftime('%Y-%m-%d')}

**WSP Compliance**: WSP 50 (Pre-Action), WSP 77 (Agent Coordination), WSP 60 (Memory)

### Audit Summary
- **Total Queue Size**: {audit_results['summary_stats']['total_queue_size']}
- **Issues Found**: {audit_results['summary_stats']['total_issues']}
- **Cleanup Recommendations**: {audit_results['summary_stats']['total_cleanup_recommendations']}
- **Memory Compliance**: {audit_results['summary_stats']['memory_compliance']}

### Queue Inventory
{json.dumps(audit_results['queue_inventory'], indent=2, default=str)}

### Scheduled Posts
{json.dumps(audit_results['summary_stats']['scheduled_times'], indent=2, default=str)}

### Issues Identified
{chr(10).join(f"- {issue}" for issue in audit_results['issues_found'])}

### Cleanup Recommendations
{chr(10).join(f"- {rec}" for rec in audit_results['cleanup_recommendations'])}
"""

            # Append to ModLog
            with open(modlog_file, 'a', encoding='utf-8') as f:
                f.write(audit_entry)

            logger.info(f"[AUDIT MISSION] Results logged to {modlog_file}")

        except Exception as e:
            logger.error(f"[AUDIT MISSION] Failed to log results: {e}")


def run_audit_linkedin_scheduling_queue() -> Dict[str, Any]:
    """
    Convenience function to run the LinkedIn scheduling queue audit mission.

    Returns:
        Audit results dictionary
    """
    mission = AuditLinkedInSchedulingQueueMission()
    return mission.execute_mission()


if __name__ == "__main__":
    # CLI interface
    import argparse

    parser = argparse.ArgumentParser(description="Audit LinkedIn Scheduling Queue Mission")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                       help="Output format")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress verbose output")

    args = parser.parse_args()

    # Run the audit
    mission = AuditLinkedInSchedulingQueueMission()
    results = mission.execute_mission()

    if args.format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        # Text summary
        print("=" * 80)
        print("LINKEDIN SCHEDULING QUEUE AUDIT RESULTS")
        print("=" * 80)

        stats = results['summary_stats']
        print(f"Total Queue Size: {stats['total_queue_size']}")
        print(f"Issues Found: {stats['total_issues']}")
        print(f"Cleanup Recommendations: {stats['total_cleanup_recommendations']}")
        print(f"Memory Compliance: {stats['memory_compliance']}")
        print()

        if stats['scheduled_times']:
            print("Scheduled Posts:")
            for post in stats['scheduled_times'][:5]:  # Show first 5
                print(f"  {post['time']}: {post['content_preview']}")
            if len(stats['scheduled_times']) > 5:
                print(f"  ... and {len(stats['scheduled_times']) - 5} more")
            print()

        if results['issues_found']:
            print("Issues Found:")
            for issue in results['issues_found']:
                print(f"  ❌ {issue}")
            print()

        if results['cleanup_recommendations']:
            print("Cleanup Recommendations:")
            for rec in results['cleanup_recommendations']:
                print(f"  🧹 {rec}")
            print()

        print("=" * 80)
