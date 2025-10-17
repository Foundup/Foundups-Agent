"""
Liberty Alert Memory System
===========================

WSP 60 Module Memory Architecture for Liberty Alert DAE
Stores consciousness state, threat patterns, and community data
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class LibertyAlertMemory:
    """
    Memory system for Liberty Alert DAE consciousness

    WSP 60 compliant module memory architecture storing:
    - Consciousness states and evolution
    - Threat patterns and detection history
    - Community zones and protection data
    - Alert history and response tracking
    """

    def __init__(self, memory_dir: str = "modules/communication/liberty_alert/memory"):
        """
        Initialize memory system

        Args:
            memory_dir: Directory for memory storage
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True, parents=True)

        # Memory files
        self.consciousness_file = self.memory_dir / "consciousness_states.jsonl"
        self.threat_patterns_file = self.memory_dir / "threat_patterns.json"
        self.community_zones_file = self.memory_dir / "community_zones.json"
        self.alert_history_file = self.memory_dir / "alert_history.jsonl"

        # Initialize memory structures
        self._load_memory()

    def _load_memory(self) -> None:
        """Load memory from disk"""
        # Threat patterns
        if self.threat_patterns_file.exists():
            with open(self.threat_patterns_file, 'r', encoding='utf-8') as f:
                self.threat_patterns = json.load(f)
        else:
            self.threat_patterns = {}

        # Community zones
        if self.community_zones_file.exists():
            with open(self.community_zones_file, 'r', encoding='utf-8') as f:
                self.community_zones = json.load(f)
        else:
            self.community_zones = {}

    def save_state(self) -> None:
        """Save current memory state to disk"""
        # Threat patterns
        with open(self.threat_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.threat_patterns, f, indent=2, ensure_ascii=False)

        # Community zones
        with open(self.community_zones_file, 'w', encoding='utf-8') as f:
            json.dump(self.community_zones, f, indent=2, ensure_ascii=False)

    def log_consciousness_state(self, state: Dict[str, Any]) -> None:
        """
        Log consciousness state for monitoring

        Args:
            state: Consciousness state data
        """
        state_entry = {
            "timestamp": datetime.now().isoformat(),
            **state
        }

        with open(self.consciousness_file, 'a', encoding='utf-8') as f:
            json.dump(state_entry, f, ensure_ascii=False)
            f.write('\n')

    def log_alert(self, alert_data: Dict[str, Any]) -> None:
        """
        Log alert for historical tracking

        Args:
            alert_data: Alert information
        """
        alert_entry = {
            "timestamp": datetime.now().isoformat(),
            **alert_data
        }

        with open(self.alert_history_file, 'a', encoding='utf-8') as f:
            json.dump(alert_entry, f, ensure_ascii=False)
            f.write('\n')

    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get recent alerts within time window

        Args:
            hours: Hours to look back

        Returns:
            List of recent alerts
        """
        if not self.alert_history_file.exists():
            return []

        alerts = []
        cutoff_time = datetime.now().timestamp() - (hours * 3600)

        with open(self.alert_history_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    alert = json.loads(line)
                    alert_time = datetime.fromisoformat(alert['timestamp']).timestamp()
                    if alert_time >= cutoff_time:
                        alerts.append(alert)

        return alerts

    def get_consciousness_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent consciousness states

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of consciousness states
        """
        if not self.consciousness_file.exists():
            return []

        states = []
        with open(self.consciousness_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    states.append(json.loads(line))
                    if len(states) >= limit:
                        break

        return states

    def update_threat_pattern(self, threat_type: str, data: Dict[str, Any]) -> None:
        """
        Update threat pattern knowledge

        Args:
            threat_type: Type of threat
            data: Pattern data to store
        """
        if threat_type not in self.threat_patterns:
            self.threat_patterns[threat_type] = {}

        self.threat_patterns[threat_type].update(data)
        self.threat_patterns[threat_type]["last_updated"] = datetime.now().isoformat()

    def add_community_zone(self, zone_id: str, zone_data: Dict[str, Any]) -> None:
        """
        Add or update community protection zone

        Args:
            zone_id: Unique zone identifier
            zone_data: Zone information
        """
        self.community_zones[zone_id] = {
            **zone_data,
            "created": datetime.now().isoformat(),
            "zone_id": zone_id
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics

        Returns:
            Dictionary with memory statistics
        """
        stats = {
            "threat_patterns_count": len(self.threat_patterns),
            "community_zones_count": len(self.community_zones),
            "consciousness_states_count": 0,
            "alert_history_count": 0,
            "memory_size_mb": 0
        }

        # Count consciousness states
        if self.consciousness_file.exists():
            with open(self.consciousness_file, 'r', encoding='utf-8') as f:
                stats["consciousness_states_count"] = sum(1 for _ in f)

        # Count alerts
        if self.alert_history_file.exists():
            with open(self.alert_history_file, 'r', encoding='utf-8') as f:
                stats["alert_history_count"] = sum(1 for _ in f)

        # Calculate memory size
        total_size = 0
        for file_path in [self.consciousness_file, self.threat_patterns_file,
                         self.community_zones_file, self.alert_history_file]:
            if file_path.exists():
                total_size += file_path.stat().st_size

        stats["memory_size_mb"] = round(total_size / (1024 * 1024), 2)

        return stats

    def cleanup_old_data(self, days: int = 30) -> int:
        """
        Clean up old consciousness states and alerts

        Args:
            days: Days to keep data

        Returns:
            Number of entries cleaned up
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        cleaned_count = 0

        # Clean consciousness states
        if self.consciousness_file.exists():
            temp_file = self.consciousness_file.with_suffix('.tmp')
            with open(self.consciousness_file, 'r', encoding='utf-8') as f_in:
                with open(temp_file, 'w', encoding='utf-8') as f_out:
                    for line in f_in:
                        if line.strip():
                            state = json.loads(line)
                            state_time = datetime.fromisoformat(state['timestamp']).timestamp()
                            if state_time >= cutoff_time:
                                f_out.write(line)
                            else:
                                cleaned_count += 1

            temp_file.replace(self.consciousness_file)

        return cleaned_count
