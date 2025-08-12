#!/usr/bin/env python3
"""
WSP-Compliant Agent Monitor
Efficient, cost-sensitive monitoring for all agents
Follows WSP 48 (Recursive Self-Improvement) and WSP 60 (Memory Architecture)
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import deque
import threading

class AgentMonitor:
    """
    Lightweight agent monitoring with NDJSON journaling
    Design: Write-once, read-many pattern for cost efficiency
    """
    
    def __init__(self):
        self.journal_dir = Path("O:/Foundups-Agent/WSP_agentic/agentic_journals")
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        
        # Activity log for all agents
        self.activity_log = self.journal_dir / "agent_activity.ndjson"
        
        # Health metrics (in-memory for speed)
        self.health_metrics = {}
        
        # Cost tracking
        self.cost_tracker = {
            "total_tool_calls": 0,
            "total_tokens": 0,
            "sessions": {}
        }
        
        # Circular buffer for recent events (memory efficient)
        self.recent_events = deque(maxlen=100)
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def log_event(self, agent_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Log agent event to NDJSON (single write, no reads)"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "event_type": event_type,
            "data": data
        }
        
        with self.lock:
            # Write to journal (append-only)
            with open(self.activity_log, 'a') as f:
                f.write(json.dumps(event) + '\n')
            
            # Update in-memory metrics
            self.recent_events.append(event)
            self._update_health_metrics(agent_id, event_type, data)
    
    def _update_health_metrics(self, agent_id: str, event_type: str, data: Dict) -> None:
        """Update in-memory health metrics (no disk I/O)"""
        if agent_id not in self.health_metrics:
            self.health_metrics[agent_id] = {
                "start_time": time.time(),
                "events": 0,
                "errors": 0,
                "tool_calls": 0,
                "last_active": time.time()
            }
        
        metrics = self.health_metrics[agent_id]
        metrics["events"] += 1
        metrics["last_active"] = time.time()
        
        if event_type == "error":
            metrics["errors"] += 1
        elif event_type == "tool_call":
            metrics["tool_calls"] += 1
            self.cost_tracker["total_tool_calls"] += 1
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get agent dashboard (memory-only, no disk reads)"""
        with self.lock:
            active_agents = []
            for agent_id, metrics in self.health_metrics.items():
                uptime = time.time() - metrics["start_time"]
                idle_time = time.time() - metrics["last_active"]
                
                active_agents.append({
                    "agent_id": agent_id,
                    "status": "active" if idle_time < 60 else "idle",
                    "uptime_seconds": int(uptime),
                    "events": metrics["events"],
                    "errors": metrics["errors"],
                    "tool_calls": metrics["tool_calls"],
                    "efficiency": self._calculate_efficiency(metrics)
                })
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "active_agents": len(active_agents),
                "total_tool_calls": self.cost_tracker["total_tool_calls"],
                "agents": active_agents,
                "recent_events": list(self.recent_events)[-10:]  # Last 10 events
            }
    
    def _calculate_efficiency(self, metrics: Dict) -> float:
        """Calculate agent efficiency score (0-100)"""
        if metrics["events"] == 0:
            return 100.0
        
        error_rate = metrics["errors"] / metrics["events"]
        tool_efficiency = min(1.0, 5.0 / max(1, metrics["tool_calls"]))  # Optimal: <=5 tools
        
        # Weighted score
        efficiency = (1 - error_rate) * 0.7 + tool_efficiency * 0.3
        return round(efficiency * 100, 1)
    
    def get_agent_report(self, agent_id: str) -> Optional[Dict]:
        """Get specific agent report"""
        with self.lock:
            if agent_id not in self.health_metrics:
                return None
            
            metrics = self.health_metrics[agent_id]
            recent_events = [e for e in self.recent_events if e["agent_id"] == agent_id]
            
            return {
                "agent_id": agent_id,
                "metrics": metrics,
                "efficiency": self._calculate_efficiency(metrics),
                "recent_events": recent_events[-5:],
                "recommendations": self._get_recommendations(metrics)
            }
    
    def _get_recommendations(self, metrics: Dict) -> List[str]:
        """WSP 48: Recursive improvement recommendations"""
        recommendations = []
        
        if metrics["errors"] > metrics["events"] * 0.1:
            recommendations.append("High error rate - review error patterns")
        
        if metrics["tool_calls"] > metrics["events"] * 5:
            recommendations.append("Excessive tool usage - optimize to <=5 per task")
        
        idle_time = time.time() - metrics["last_active"]
        if idle_time > 300:
            recommendations.append("Agent idle >5min - consider deactivation")
        
        return recommendations
    
    def export_session_report(self) -> str:
        """Export session report for cost analysis"""
        report = {
            "session_end": datetime.utcnow().isoformat(),
            "cost_metrics": self.cost_tracker,
            "agent_performance": {}
        }
        
        for agent_id, metrics in self.health_metrics.items():
            report["agent_performance"][agent_id] = {
                "efficiency": self._calculate_efficiency(metrics),
                "tool_calls": metrics["tool_calls"],
                "error_rate": metrics["errors"] / max(1, metrics["events"])
            }
        
        # Save to journal
        report_file = self.journal_dir / f"session_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)


# Global monitor instance (singleton pattern for efficiency)
_monitor_instance = None

def get_monitor() -> AgentMonitor:
    """Get singleton monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = AgentMonitor()
    return _monitor_instance