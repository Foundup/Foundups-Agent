# -*- coding: utf-8 -*-
"""
Selenium Run History Mission
Analyzes and summarizes Selenium session data from foundups.db

WSP 77: Agent Coordination Protocol
WSP 90: UTF-8 Enforcement
"""

import sqlite3
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

# Apply WSP 90 UTF-8 enforcement
if sys.platform.startswith('win'):
    import io
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        else:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError, AttributeError):
        pass

logger = logging.getLogger(__name__)


class SeleniumRunHistoryMission:
    """
    Mission to analyze and summarize Selenium session data.

    Connects to foundups.db and aggregates statistics from selenium_sessions table.
    Returns structured data ready for Qwen/Gemma summarization.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize mission with database path

        Args:
            db_path: Path to foundups.db, defaults to holo_index/data/foundups.db
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "foundups.db"
        self.db_path = Path(db_path)

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _get_columns(conn: sqlite3.Connection) -> Set[str]:
        """Retrieve available columns for selenium_sessions table."""
        cursor = conn.execute("PRAGMA table_info(selenium_sessions)")
        return {row[1] for row in cursor.fetchall()}

    def _ensure_table_exists(self, conn: sqlite3.Connection) -> bool:
        """
        Ensure selenium_sessions table exists with proper schema.
        Creates table if it doesn't exist.
        """
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='selenium_sessions'
        """)

        if not cursor.fetchone():
            # Create table with comprehensive schema
            cursor.execute("""
                CREATE TABLE selenium_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT CHECK(status IN ('success', 'failed', 'timeout', 'error')),
                    hash TEXT,
                    duration_seconds INTEGER,
                    user_agent TEXT,
                    browser TEXT DEFAULT 'chrome',
                    session_id TEXT,
                    error_message TEXT,
                    page_title TEXT,
                    screenshot_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            cursor.execute("CREATE INDEX idx_selenium_url ON selenium_sessions(url)")
            cursor.execute("CREATE INDEX idx_selenium_status ON selenium_sessions(status)")
            cursor.execute("CREATE INDEX idx_selenium_start_time ON selenium_sessions(start_time)")

            conn.commit()
            logger.debug("[SeleniumRunHistory] Created selenium_sessions table and indexes at %s", self.db_path)
            return False  # Table was created

        return True  # Table already existed

    def _get_recent_sessions(self, conn: sqlite3.Connection, days: int = 7) -> List[sqlite3.Row]:
        """Get recent selenium sessions within specified days"""
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)

        columns = self._get_columns(conn)

        select_fields = ["id"]

        if "start_time" in columns:
            time_column = "start_time"
            select_fields.append("start_time")
        elif "timestamp" in columns:
            time_column = "timestamp"
            select_fields.append("timestamp AS start_time")
        else:
            time_column = None
            select_fields.append("NULL AS start_time")

        if "status" in columns:
            select_fields.append("status")
        else:
            select_fields.append("NULL AS status")

        if "duration_seconds" in columns:
            select_fields.append("duration_seconds")
        else:
            select_fields.append("NULL AS duration_seconds")

        if "hash" in columns:
            select_fields.append("hash")
        elif "screenshot_hash" in columns:
            select_fields.append("screenshot_hash AS hash")
        else:
            select_fields.append("NULL AS hash")

        if "browser" in columns:
            select_fields.append("browser")
        else:
            select_fields.append("'chrome' AS browser")

        optional_fields = [
            "url",
            "user_agent",
            "session_id",
            "error_message",
            "page_title",
            "screenshot_path"
        ]
        for field in optional_fields:
            if field in columns:
                select_fields.append(field)
            else:
                select_fields.append(f"NULL AS {field}")

        select_clause = ", ".join(select_fields)

        if time_column:
            cursor.execute(
                f"""
                SELECT {select_clause}
                FROM selenium_sessions
                WHERE {time_column} >= ?
                ORDER BY {time_column} DESC
                """,
                (cutoff_date.isoformat(),)
            )
        else:
            cursor.execute(
                f"""
                SELECT {select_clause}
                FROM selenium_sessions
                ORDER BY id DESC
                """
            )

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def _aggregate_by_url(self, sessions: List[sqlite3.Row]) -> Dict[str, Dict[str, Any]]:
        """Aggregate session data by URL"""
        url_stats = {}

        for session in sessions:
            url = session.get('url') or 'unknown'
            if url not in url_stats:
                url_stats[url] = {
                    'total_runs': 0,
                    'success_count': 0,
                    'failed_count': 0,
                    'timeout_count': 0,
                    'error_count': 0,
                    'avg_duration': 0,
                    'total_duration': 0,
                    'last_run': None,
                    'last_hash': None,
                    'unique_hashes': set(),
                    'browsers_used': set(),
                    'success_rate': 0,
                    'recent_runs': []
                }

            stats = url_stats[url]
            stats['total_runs'] += 1

            # Count by status
            status = (session.get('status') or 'success').lower()
            if status == 'success':
                stats['success_count'] += 1
            elif status == 'failed':
                stats['failed_count'] += 1
            elif status == 'timeout':
                stats['timeout_count'] += 1
            elif status == 'error':
                stats['error_count'] += 1

            # Duration tracking
            duration = session.get('duration_seconds') or 0
            stats['total_duration'] += duration

            # Track metadata
            hash_value = session.get('hash')
            if hash_value:
                stats['unique_hashes'].add(hash_value)

            browser = session.get('browser') or 'unknown'
            stats['browsers_used'].add(browser)

            # Track most recent run
            start_time = session.get('start_time')
            if start_time and (stats['last_run'] is None or start_time > stats['last_run']):
                stats['last_run'] = start_time
                stats['last_hash'] = hash_value

            # Keep recent runs (last 10)
            stats['recent_runs'].append({
                'start_time': start_time,
                'status': status,
                'duration': duration,
                'hash': hash_value
            })
            stats['recent_runs'] = stats['recent_runs'][-10:]  # Keep only last 10

        # Calculate averages and finalize
        for url, stats in url_stats.items():
            if stats['total_runs'] > 0:
                stats['avg_duration'] = stats['total_duration'] / stats['total_runs']
                stats['success_rate'] = (stats['success_count'] / stats['total_runs']) * 100

            stats['unique_hashes'] = list(stats['unique_hashes'])
            stats['browsers_used'] = list(stats['browsers_used'])
            stats['recent_runs'].sort(
                key=lambda x: x['start_time'] or "",
                reverse=True
            )

        return url_stats

    def _get_overall_stats(self, sessions: List[sqlite3.Row]) -> Dict[str, Any]:
        """Calculate overall statistics"""
        if not sessions:
            return {
                'total_sessions': 0,
                'success_rate': 0,
                'avg_duration': 0,
                'unique_urls': 0,
                'time_range': None
            }

        total_sessions = len(sessions)
        success_count = sum(1 for s in sessions if (s.get('status') or 'success').lower() == 'success')
        total_duration = sum((s.get('duration_seconds') or 0) for s in sessions)
        unique_urls = len(set(s.get('url') or 'unknown' for s in sessions))

        # Time range
        start_times = [s.get('start_time') for s in sessions if s.get('start_time')]
        if start_times:
            earliest = min(start_times)
            latest = max(start_times)
            time_range = {
                'earliest': earliest,
                'latest': latest,
                'days_span': (datetime.fromisoformat(latest) - datetime.fromisoformat(earliest)).days
            }
        else:
            time_range = None

        return {
            'total_sessions': total_sessions,
            'success_rate': (success_count / total_sessions) * 100 if total_sessions > 0 else 0,
            'avg_duration': total_duration / total_sessions if total_sessions > 0 else 0,
            'unique_urls': unique_urls,
            'time_range': time_range
        }

    def _analyze_jsonl_patterns(self) -> Dict[str, Any]:
        """
        Analyze JSONL telemetry files for behavioral patterns and insights.

        This bridges Pipeline A (JSONL creation) to Pipeline B (insight generation)
        enabling 0102 to observe raw telemetry patterns for recursive improvement.

        Returns:
            Dictionary with pattern analysis results
        """
        jsonl_dir = Path("holo_index/telemetry/vision_dae")
        patterns = {
            'jsonl_files_analyzed': 0,
            'total_events': 0,
            'error_patterns': [],
            'performance_anomalies': [],
            'user_interaction_flows': [],
            'failure_modes': [],
            'behavioral_insights': [],
            'analysis_timestamp': datetime.now().isoformat()
        }

        if not jsonl_dir.exists():
            patterns['error'] = f"JSONL directory not found: {jsonl_dir}"
            return patterns

        try:
            # Find all JSONL files
            jsonl_files = sorted(jsonl_dir.glob("vision_session_*.jsonl"))
            patterns['jsonl_files_analyzed'] = len(jsonl_files)

            events_analyzed = []
            error_sequences = []
            current_error_sequence = []

            for jsonl_file in jsonl_files:
                try:
                    with jsonl_file.open('r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if not line:
                                continue

                            try:
                                event = json.loads(line)
                                events_analyzed.append(event)
                                patterns['total_events'] += 1

                                # Analyze for error patterns
                                if self._is_error_event(event):
                                    current_error_sequence.append({
                                        'event': event,
                                        'file': str(jsonl_file),
                                        'line': line_num
                                    })
                                elif current_error_sequence:
                                    # End of error sequence
                                    if len(current_error_sequence) > 1:
                                        error_sequences.append(current_error_sequence)
                                    current_error_sequence = []

                                # Analyze for performance anomalies
                                if self._is_performance_anomaly(event):
                                    patterns['performance_anomalies'].append({
                                        'event': event,
                                        'file': str(jsonl_file),
                                        'line': line_num,
                                        'anomaly_type': self._detect_anomaly_type(event)
                                    })

                                # Analyze user interaction flows
                                if self._is_user_interaction(event):
                                    patterns['user_interaction_flows'].append({
                                        'event': event,
                                        'timestamp': event.get('timestamp'),
                                        'interaction_type': self._classify_interaction(event)
                                    })

                            except json.JSONDecodeError as e:
                                logger.warning(f"Malformed JSONL line {line_num} in {jsonl_file}: {e}")

                except Exception as e:
                    logger.warning(f"Failed to process JSONL file {jsonl_file}: {e}")

            # Process completed error sequences
            if current_error_sequence:
                error_sequences.append(current_error_sequence)

            # Extract error patterns
            patterns['error_patterns'] = self._extract_error_patterns(error_sequences)

            # Extract failure modes
            patterns['failure_modes'] = self._extract_failure_modes(events_analyzed)

            # Generate behavioral insights
            patterns['behavioral_insights'] = self._generate_behavioral_insights(events_analyzed)

        except Exception as e:
            patterns['error'] = f"JSONL analysis failed: {str(e)}"
            logger.error(f"JSONL pattern analysis failed: {e}")

        return patterns

    def _is_error_event(self, event: Dict) -> bool:
        """Check if event represents an error or failure"""
        event_str = json.dumps(event).lower()
        error_indicators = [
            'error', 'exception', 'failed', 'timeout', 'crash',
            'unable', 'cannot', 'failed', 'error_code'
        ]
        return any(indicator in event_str for indicator in error_indicators)

    def _is_performance_anomaly(self, event: Dict) -> bool:
        """Check if event shows performance anomaly"""
        # Look for timing data that indicates anomalies
        if 'duration' in event and isinstance(event['duration'], (int, float)):
            duration = event['duration']
            # Flag events taking longer than 30 seconds as anomalies
            if duration > 30:
                return True
        return False

    def _detect_anomaly_type(self, event: Dict) -> str:
        """Classify the type of performance anomaly"""
        duration = event.get('duration', 0)
        if duration > 120:
            return 'extreme_delay'
        elif duration > 60:
            return 'significant_delay'
        elif duration > 30:
            return 'moderate_delay'
        return 'unknown'

    def _is_user_interaction(self, event: Dict) -> bool:
        """Check if event represents user interaction"""
        interaction_indicators = [
            'click', 'input', 'type', 'select', 'scroll',
            'hover', 'focus', 'submit', 'navigate'
        ]
        event_str = json.dumps(event).lower()
        return any(indicator in event_str for indicator in interaction_indicators)

    def _classify_interaction(self, event: Dict) -> str:
        """Classify the type of user interaction"""
        event_str = json.dumps(event).lower()
        if 'click' in event_str:
            return 'click'
        elif 'input' in event_str or 'type' in event_str:
            return 'input'
        elif 'select' in event_str:
            return 'selection'
        elif 'scroll' in event_str:
            return 'navigation'
        elif 'submit' in event_str:
            return 'form_submission'
        return 'other'

    def _extract_error_patterns(self, error_sequences: List[List[Dict]]) -> List[Dict]:
        """Extract patterns from error sequences"""
        patterns = []

        for sequence in error_sequences:
            if len(sequence) < 2:
                continue

            pattern = {
                'sequence_length': len(sequence),
                'start_event': sequence[0]['event'],
                'end_event': sequence[-1]['event'],
                'files_involved': list(set(s['file'] for s in sequence)),
                'error_chain': [s['event'] for s in sequence],
                'pattern_type': self._classify_error_pattern(sequence)
            }
            patterns.append(pattern)

        return patterns

    def _classify_error_pattern(self, sequence: List[Dict]) -> str:
        """Classify the type of error pattern"""
        events = [s['event'] for s in sequence]

        # Check for timeout chains
        if all('timeout' in json.dumps(e).lower() for e in events):
            return 'timeout_chain'

        # Check for network errors
        if any('network' in json.dumps(e).lower() for e in events):
            return 'network_failure'

        # Check for element not found patterns
        if any('not found' in json.dumps(e).lower() for e in events):
            return 'element_missing'

        return 'unknown_error_chain'

    def _extract_failure_modes(self, events: List[Dict]) -> List[Dict]:
        """Extract common failure modes from telemetry"""
        failure_modes = []

        # Group events by failure type
        failure_groups = {}
        for event in events:
            if self._is_error_event(event):
                failure_type = self._classify_failure_mode(event)
                if failure_type not in failure_groups:
                    failure_groups[failure_type] = []
                failure_groups[failure_type].append(event)

        # Convert to structured failure modes
        for failure_type, failure_events in failure_groups.items():
            failure_modes.append({
                'failure_type': failure_type,
                'occurrences': len(failure_events),
                'sample_events': failure_events[:3],  # First 3 examples
                'frequency': len(failure_events) / len(events) if events else 0,
                'severity': self._assess_failure_severity(failure_type)
            })

        return sorted(failure_modes, key=lambda x: x['occurrences'], reverse=True)

    def _classify_failure_mode(self, event: Dict) -> str:
        """Classify the type of failure"""
        event_str = json.dumps(event).lower()

        if 'timeout' in event_str:
            return 'timeout'
        elif 'network' in event_str or 'connection' in event_str:
            return 'network_error'
        elif 'not found' in event_str or 'element' in event_str:
            return 'element_not_found'
        elif 'stale' in event_str:
            return 'stale_element'
        elif 'javascript' in event_str:
            return 'javascript_error'
        return 'unknown_failure'

    def _assess_failure_severity(self, failure_type: str) -> str:
        """Assess the severity of a failure type"""
        severity_map = {
            'timeout': 'high',
            'network_error': 'high',
            'javascript_error': 'high',
            'element_not_found': 'medium',
            'stale_element': 'medium',
            'unknown_failure': 'low'
        }
        return severity_map.get(failure_type, 'low')

    def _generate_behavioral_insights(self, events: List[Dict]) -> List[Dict]:
        """Generate behavioral insights from telemetry patterns"""
        insights = []

        if not events:
            return insights

        # Analyze timing patterns
        durations = [e.get('duration', 0) for e in events if isinstance(e.get('duration'), (int, float))]
        if durations:
            avg_duration = sum(durations) / len(durations)
            insights.append({
                'type': 'timing_analysis',
                'insight': f'Average operation duration: {avg_duration:.2f}s',
                'data': {'avg_duration': avg_duration, 'sample_count': len(durations)}
            })

        # Analyze interaction patterns
        interactions = [e for e in events if self._is_user_interaction(e)]
        if interactions:
            interaction_types = {}
            for interaction in interactions:
                itype = self._classify_interaction(interaction)
                interaction_types[itype] = interaction_types.get(itype, 0) + 1

            most_common = max(interaction_types.items(), key=lambda x: x[1])
            insights.append({
                'type': 'interaction_pattern',
                'insight': f'Most common interaction: {most_common[0]} ({most_common[1]} occurrences)',
                'data': interaction_types
            })

        # Analyze error frequency
        error_count = sum(1 for e in events if self._is_error_event(e))
        error_rate = error_count / len(events) if events else 0

        if error_rate > 0.1:  # More than 10% errors
            insights.append({
                'type': 'error_frequency',
                'insight': f'High error rate detected: {error_rate:.1%} ({error_count}/{len(events)})',
                'severity': 'high',
                'data': {'error_rate': error_rate, 'error_count': error_count}
            })

        return insights

    def execute_mission(self, days: int = 7) -> Dict[str, Any]:
        """
        Execute the selenium run history mission

        Args:
            days: Number of days to look back for sessions

        Returns:
            Structured dictionary with session analysis and aggregations
        """
        try:
            with self._get_db_connection() as conn:
                # Ensure table exists
                table_existed = self._ensure_table_exists(conn)

                # Get recent sessions
                sessions = self._get_recent_sessions(conn, days)

                # Aggregate data
                url_stats = self._aggregate_by_url(sessions)
                overall_stats = self._get_overall_stats(sessions)

                # Analyze JSONL telemetry patterns (bridge Pipeline A to Pipeline B)
                jsonl_patterns = self._analyze_jsonl_patterns()

                # Prepare result
                result = {
                    'mission': 'selenium_run_history',
                    'timestamp': datetime.now().isoformat(),
                    'parameters': {
                        'days_analyzed': days,
                        'table_existed': table_existed
                    },
                    'overall_stats': overall_stats,
                    'url_breakdown': url_stats,
                    'jsonl_patterns': jsonl_patterns,
                    'raw_session_count': len(sessions),
                    'summary_ready': True
                }

                # Add sample sessions if any exist
                if sessions:
                    result['sample_sessions'] = [
                        {
                            'url': s['url'],
                            'start_time': s.get('start_time'),
                            'status': s.get('status'),
                            'duration_seconds': s.get('duration_seconds'),
                            'hash': s.get('hash')
                        }
                        for s in sessions[:5]  # First 5 sessions
                    ]

                return result

        except Exception as e:
            return {
                'mission': 'selenium_run_history',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'summary_ready': False
            }


def run_selenium_history_mission(days: int = 7) -> Dict[str, Any]:
    """
    Convenience function to run the selenium history mission

    Args:
        days: Number of days to analyze

    Returns:
        Mission results dictionary
    """
    mission = SeleniumRunHistoryMission()
    return mission.execute_mission(days)


if __name__ == "__main__":
    # CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Selenium Run History Mission")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--db-path", help="Custom database path")

    args = parser.parse_args()

    mission = SeleniumRunHistoryMission(args.db_path)
    result = mission.execute_mission(args.days)

    # Pretty print result
    import json
    print(json.dumps(result, indent=2, default=str))
