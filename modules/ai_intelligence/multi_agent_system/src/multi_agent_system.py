"""
Enhanced Multi-Agent Coordination System - WSP 54 Compliance
Provides real-time coordination between agents using breadcrumb trails.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AgentActivity:
    """Represents an agent's current activity."""
    agent_id: str
    activity_type: str
    timestamp: str
    focus_area: str
    coordination_signals: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"


@dataclass
class CoordinationOpportunity:
    """Represents a coordination opportunity between agents."""
    opportunity_id: str
    primary_agent: str
    supporting_agent: str
    opportunity_type: str
    description: str
    priority: str = "medium"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class MultiAgentCoordinator:
    """
    Multi-Agent Coordination Engine - WSP 54 Compliance
    Reads breadcrumb trails and coordinates agent activities for enhanced collaboration.
    """

    def __init__(self, breadcrumb_paths: Dict[str, Path]):
        """
        Initialize coordinator with paths to agent breadcrumb trails.

        Args:
            breadcrumb_paths: Dict mapping agent_ids to their breadcrumb log paths
        """
        self.breadcrumb_paths = breadcrumb_paths
        self.active_agents: Dict[str, AgentActivity] = {}
        self.coordination_opportunities: List[CoordinationOpportunity] = []
        self.last_check = datetime.now()

    def scan_breadcrumb_trails(self) -> Dict[str, Any]:
        """
        Scan all agent breadcrumb trails for coordination opportunities.
        Returns analysis of current agent activities and coordination opportunities.
        """
        current_activities = {}
        opportunities = []

        # Scan each agent's breadcrumb trail
        for agent_id, trail_path in self.breadcrumb_paths.items():
            if trail_path.exists():
                activities = self._scan_agent_trail(agent_id, trail_path)
                current_activities[agent_id] = activities

                # Check for coordination opportunities
                agent_opportunities = self._analyze_coordination_opportunities(agent_id, activities)
                opportunities.extend(agent_opportunities)

        # Update coordination state
        self._update_coordination_state(current_activities, opportunities)

        return {
            "active_agents": current_activities,
            "coordination_opportunities": opportunities,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def get_collaboration_suggestions(self, target_agent: str) -> List[Dict[str, Any]]:
        """
        Get collaboration suggestions for a specific agent.
        """
        suggestions = []

        # Find opportunities where target_agent is primary or supporting
        relevant_opportunities = [
            opp for opp in self.coordination_opportunities
            if opp.primary_agent == target_agent or opp.supporting_agent == target_agent
        ]

        for opportunity in relevant_opportunities:
            suggestions.append({
                "type": "collaboration_suggestion",
                "opportunity": opportunity.opportunity_type,
                "description": opportunity.description,
                "priority": opportunity.priority,
                "partner_agent": opportunity.supporting_agent if opportunity.primary_agent == target_agent else opportunity.primary_agent,
                "timestamp": opportunity.timestamp
            })

        return suggestions

    def signal_agent_activity(self, agent_id: str, activity: Dict[str, Any]) -> None:
        """
        Signal that an agent is performing an activity.
        This creates a breadcrumb trail entry.
        """
        agent_activity = AgentActivity(
            agent_id=agent_id,
            activity_type=activity.get("type", "unknown"),
            timestamp=datetime.now().isoformat(),
            focus_area=activity.get("focus_area", "general"),
            coordination_signals=activity.get("coordination_signals", {}),
            status="active"
        )

        self.active_agents[agent_id] = agent_activity

        # Write to breadcrumb trail
        trail_path = self.breadcrumb_paths.get(agent_id)
        if trail_path:
            self._write_breadcrumb_entry(trail_path, agent_activity)

    def _scan_agent_trail(self, agent_id: str, trail_path: Path) -> List[AgentActivity]:
        """Scan an agent's breadcrumb trail for recent activities."""
        activities = []

        try:
            # Read recent entries (last 100 lines for performance)
            with open(trail_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-100:]

            for line in lines:
                if line.strip():
                    try:
                        entry = json.loads(line.strip())
                        activity = self._parse_breadcrumb_entry(entry)
                        if activity:
                            activities.append(activity)
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"Warning: Failed to scan trail for {agent_id}: {e}")

        return activities

    def _parse_breadcrumb_entry(self, entry: Dict[str, Any]) -> Optional[AgentActivity]:
        """Parse a breadcrumb trail entry into an AgentActivity."""
        try:
            # Handle different breadcrumb formats
            if "agent_id" in entry:
                # New format with coordination signals
                coordination_signals = entry.get("coordination_signals", {})
                return AgentActivity(
                    agent_id=entry["agent_id"],
                    activity_type="search" if "query" in entry else "unknown",
                    timestamp=entry["timestamp"],
                    focus_area=coordination_signals.get("current_focus", "general"),
                    coordination_signals=coordination_signals,
                    status="completed"
                )
            else:
                # Legacy format - infer from content
                return AgentActivity(
                    agent_id=entry.get("agent_id", "unknown"),
                    activity_type="legacy_activity",
                    timestamp=entry.get("timestamp", datetime.now().isoformat()),
                    focus_area="general",
                    status="legacy"
                )
        except Exception:
            return None

    def _analyze_coordination_opportunities(self, agent_id: str, activities: List[AgentActivity]) -> List[CoordinationOpportunity]:
        """Analyze activities for coordination opportunities."""
        opportunities = []

        if not activities:
            return opportunities

        # Get the most recent activity
        recent_activity = max(activities, key=lambda a: a.timestamp)

        # Analyze coordination signals
        signals = recent_activity.coordination_signals

        # Check for collaboration opportunities
        collaboration_opps = signals.get("collaboration_opportunities", [])
        for opp in collaboration_opps:
            opportunity = CoordinationOpportunity(
                opportunity_id=f"{agent_id}_{int(time.time())}_{len(opportunities)}",
                primary_agent=agent_id,
                supporting_agent="coordinator_agent",  # Could be any available agent
                opportunity_type="collaboration",
                description=opp,
                priority="medium"
            )
            opportunities.append(opportunity)

        # Check for intervention triggers
        intervention_triggers = signals.get("intervention_triggers", [])
        for trigger in intervention_triggers:
            opportunity = CoordinationOpportunity(
                opportunity_id=f"{agent_id}_{int(time.time())}_{len(opportunities)}",
                primary_agent=agent_id,
                supporting_agent="supervisor_agent",
                opportunity_type="intervention",
                description=trigger,
                priority="high"
            )
            opportunities.append(opportunity)

        return opportunities

    def _update_coordination_state(self, current_activities: Dict[str, List[AgentActivity]], opportunities: List[CoordinationOpportunity]) -> None:
        """Update the internal coordination state."""
        # Update active agents
        for agent_id, activities in current_activities.items():
            if activities:
                # Use most recent activity
                recent = max(activities, key=lambda a: a.timestamp)
                self.active_agents[agent_id] = recent

        # Update coordination opportunities
        self.coordination_opportunities = opportunities

    def _write_breadcrumb_entry(self, trail_path: Path, activity: AgentActivity) -> None:
        """Write an activity to the breadcrumb trail."""
        try:
            entry = {
                "agent_id": activity.agent_id,
                "timestamp": activity.timestamp,
                "activity_type": activity.activity_type,
                "focus_area": activity.focus_area,
                "coordination_signals": activity.coordination_signals,
                "status": activity.status
            }

            with open(trail_path, 'a', encoding='utf-8') as f:
                json.dump(entry, f)
                f.write('\n')

        except Exception as e:
            print(f"Warning: Failed to write breadcrumb for {activity.agent_id}: {e}")

    def get_agent_status_report(self) -> Dict[str, Any]:
        """Generate a status report of all active agents."""
        return {
            "active_agents": len(self.active_agents),
            "coordination_opportunities": len(self.coordination_opportunities),
            "last_scan": self.last_check.isoformat(),
            "agent_details": {
                agent_id: {
                    "focus": activity.focus_area,
                    "last_activity": activity.timestamp,
                    "status": activity.status
                }
                for agent_id, activity in self.active_agents.items()
            }
        }


def create_coordinator_for_foundups() -> MultiAgentCoordinator:
    """
    Create a coordinator instance configured for the FoundUps agent ecosystem.
    """
    breadcrumb_paths = {
        "holoindex_0102": Path("E:/HoloIndex/learning/interactions.jsonl"),
        "wre_orchestrator": Path("WSP_agentic/narrative_log/wre_story_log.md"),  # WSP 52 compliance
        "code_agent": Path("modules/ai_intelligence/multi_agent_system/memory/breadcrumbs.jsonl"),
        # Add more agents as they implement breadcrumb trails
    }

    return MultiAgentCoordinator(breadcrumb_paths)
