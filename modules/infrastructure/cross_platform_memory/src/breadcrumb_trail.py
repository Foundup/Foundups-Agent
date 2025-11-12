# -*- coding: utf-8 -*-
"""
Breadcrumb Trail System (WSP 60 Enhanced)

Provides multi-agent discovery sharing and coordination trails.
Enables agents to learn from each other's actions across platforms.

WSP 60: Module Memory Architecture Protocol
WSP 78: AgentDB Protocol for coordination
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid
import sys
import io

# WSP 90 UTF-8 Enforcement for Windows compatibility
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)


@dataclass
class Breadcrumb:
    """Individual breadcrumb in the trail"""
    id: str
    agent_id: str
    action: str
    data: Dict[str, Any]
    timestamp: datetime
    session_id: str
    coordination_value: bool = False
    shared_agents: List[str] = None

    def __post_init__(self):
        if self.shared_agents is None:
            self.shared_agents = []


class BreadcrumbTrail:
    """
    Breadcrumb Trail System

    WSP 60 Enhanced: Multi-agent discovery sharing and coordination
    Enables cross-platform learning through action trails

    Features:
    - Action trail recording and sharing
    - Multi-agent coordination discovery
    - Pattern learning from trails
    - Cross-platform intelligence sharing
    """

    def __init__(self, agent_id: str, storage_path: Optional[Path] = None):
        """
        Initialize breadcrumb trail

        Args:
            agent_id: Identifier for this agent
            storage_path: Optional custom storage path
        """
        self.agent_id = agent_id

        if storage_path is None:
            storage_path = Path("modules/infrastructure/cross_platform_memory/memory/breadcrumbs")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Current session
        self.session_id = str(uuid.uuid4())
        self.current_trail: List[Breadcrumb] = []

        # Coordination tracking
        self.coordination_events: Dict[str, List[Breadcrumb]] = {}

        logger.info(f"[BREADCRUMB] Initialized for agent: {agent_id}")

    async def add_action(self, action: str, data: Dict[str, Any],
                        coordination_value: bool = False,
                        shared_agents: List[str] = None) -> str:
        """
        Add an action to the breadcrumb trail

        Args:
            action: Action name/type
            data: Action data and context
            coordination_value: Whether this action has coordination value
            shared_agents: Other agents this should be shared with

        Returns:
            Breadcrumb ID
        """
        breadcrumb_id = str(uuid.uuid4())

        breadcrumb = Breadcrumb(
            id=breadcrumb_id,
            agent_id=self.agent_id,
            action=action,
            data=data,
            timestamp=datetime.now(),
            session_id=self.session_id,
            coordination_value=coordination_value,
            shared_agents=shared_agents or []
        )

        self.current_trail.append(breadcrumb)

        # Track coordination events
        if coordination_value:
            coord_key = f"{action}_{breadcrumb_id[:8]}"
            self.coordination_events[coord_key] = [breadcrumb]

        # Auto-save for coordination events
        if coordination_value:
            await self.save_trail()

        logger.debug(f"[BREADCRUMB] Added action: {action} (id: {breadcrumb_id[:8]})")
        return breadcrumb_id

    async def save_trail(self):
        """Save current breadcrumb trail to storage"""
        try:
            # Convert breadcrumbs to serializable format
            trail_data = []
            for breadcrumb in self.current_trail:
                trail_data.append({
                    'id': breadcrumb.id,
                    'agent_id': breadcrumb.agent_id,
                    'action': breadcrumb.action,
                    'data': breadcrumb.data,
                    'timestamp': breadcrumb.timestamp.isoformat(),
                    'session_id': breadcrumb.session_id,
                    'coordination_value': breadcrumb.coordination_value,
                    'shared_agents': breadcrumb.shared_agents
                })

            # Save to file
            trail_file = self.storage_path / f"trail_{self.agent_id}_{self.session_id[:8]}.json"
            with open(trail_file, 'w', encoding='utf-8') as f:
                json.dump(trail_data, f, indent=2, ensure_ascii=False)

            # Also save coordination events
            if self.coordination_events:
                coord_file = self.storage_path / f"coordination_{self.agent_id}_{self.session_id[:8]}.json"
                coord_data = {}
                for coord_key, breadcrumbs in self.coordination_events.items():
                    coord_data[coord_key] = [
                        {
                            'id': b.id,
                            'action': b.action,
                            'data': b.data,
                            'timestamp': b.timestamp.isoformat(),
                            'agent_id': b.agent_id
                        } for b in breadcrumbs
                    ]

                with open(coord_file, 'w', encoding='utf-8') as f:
                    json.dump(coord_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"[BREADCRUMB] Saved trail with {len(self.current_trail)} breadcrumbs")

        except Exception as e:
            logger.error(f"[BREADCRUMB] Failed to save trail: {e}")

    async def load_trail(self, session_id: Optional[str] = None) -> List[Breadcrumb]:
        """
        Load breadcrumb trail from storage

        Args:
            session_id: Specific session to load (None for current)

        Returns:
            List of breadcrumbs
        """
        target_session = session_id or self.session_id

        try:
            trail_file = self.storage_path / f"trail_{self.agent_id}_{target_session[:8]}.json"

            if trail_file.exists():
                with open(trail_file, 'r', encoding='utf-8') as f:
                    trail_data = json.load(f)

                breadcrumbs = []
                for item in trail_data:
                    breadcrumb = Breadcrumb(
                        id=item['id'],
                        agent_id=item['agent_id'],
                        action=item['action'],
                        data=item['data'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        session_id=item['session_id'],
                        coordination_value=item.get('coordination_value', False),
                        shared_agents=item.get('shared_agents', [])
                    )
                    breadcrumbs.append(breadcrumb)

                # Update current trail if loading current session
                if session_id is None or session_id == self.session_id:
                    self.current_trail = breadcrumbs

                logger.debug(f"[BREADCRUMB] Loaded trail with {len(breadcrumbs)} breadcrumbs")
                return breadcrumbs

        except Exception as e:
            logger.error(f"[BREADCRUMB] Failed to load trail: {e}")

        return []

    async def get_trail_length(self) -> int:
        """Get current trail length"""
        return len(self.current_trail)

    async def find_coordination_opportunities(self, other_agent_id: str) -> List[Dict[str, Any]]:
        """
        Find coordination opportunities with another agent

        Args:
            other_agent_id: Agent to find coordination with

        Returns:
            List of coordination opportunities
        """
        opportunities = []

        try:
            # Load other agent's recent coordination events
            coord_file = self.storage_path / f"coordination_{other_agent_id}_*.json"
            coord_files = list(self.storage_path.glob(str(coord_file).replace('*', '*')))

            for coord_file in coord_files[-5:]:  # Last 5 sessions
                try:
                    with open(coord_file, 'r', encoding='utf-8') as f:
                        coord_data = json.load(f)

                    for coord_key, breadcrumbs in coord_data.items():
                        for breadcrumb_data in breadcrumbs:
                            # Check if this agent was mentioned in shared_agents
                            if self.agent_id in breadcrumb_data.get('shared_agents', []):
                                opportunities.append({
                                    'coordination_key': coord_key,
                                    'action': breadcrumb_data['action'],
                                    'data': breadcrumb_data['data'],
                                    'timestamp': breadcrumb_data['timestamp'],
                                    'initiating_agent': breadcrumb_data['agent_id'],
                                    'opportunity_type': 'shared_action'
                                })

                except Exception as e:
                    logger.warning(f"[BREADCRUMB] Failed to read coordination file {coord_file}: {e}")

        except Exception as e:
            logger.error(f"[BREADCRUMB] Failed to find coordination opportunities: {e}")

        logger.info(f"[BREADCRUMB] Found {len(opportunities)} coordination opportunities with {other_agent_id}")
        return opportunities

    async def share_trail_segment(self, start_index: int, end_index: int,
                                target_agents: List[str]) -> bool:
        """
        Share a segment of the breadcrumb trail with other agents

        Args:
            start_index: Start index in current trail
            end_index: End index in current trail
            target_agents: Agents to share with

        Returns:
            bool: True if shared successfully
        """
        try:
            if start_index >= len(self.current_trail) or end_index > len(self.current_trail):
                logger.warning("[BREADCRUMB] Invalid trail segment indices")
                return False

            segment = self.current_trail[start_index:end_index]

            # Create shared trail file
            share_data = {
                'source_agent': self.agent_id,
                'session_id': self.session_id,
                'target_agents': target_agents,
                'timestamp': datetime.now().isoformat(),
                'trail_segment': [
                    {
                        'id': b.id,
                        'action': b.action,
                        'data': b.data,
                        'timestamp': b.timestamp.isoformat(),
                        'coordination_value': b.coordination_value
                    } for b in segment
                ]
            }

            # Save to shared location
            shared_file = self.storage_path / f"shared_{self.agent_id}_{self.session_id[:8]}_{start_index}_{end_index}.json"
            with open(shared_file, 'w', encoding='utf-8') as f:
                json.dump(share_data, f, indent=2, ensure_ascii=False)

            # Update breadcrumbs to reflect sharing
            for breadcrumb in segment:
                breadcrumb.shared_agents.extend(target_agents)
                breadcrumb.shared_agents = list(set(breadcrumb.shared_agents))

            await self.save_trail()

            logger.info(f"[BREADCRUMB] Shared trail segment ({start_index}:{end_index}) with {len(target_agents)} agents")
            return True

        except Exception as e:
            logger.error(f"[BREADCRUMB] Failed to share trail segment: {e}")
            return False

    async def learn_from_trail(self, trail_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Learn patterns from a breadcrumb trail

        Args:
            trail_data: Trail data to learn from

        Returns:
            Learning results
        """
        patterns_learned = []
        action_sequences = []
        current_sequence = []

        try:
            for item in trail_data:
                action = item.get('action', '')
                data = item.get('data', {})

                # Build action sequences
                current_sequence.append(action)

                # Look for patterns in sequences
                if len(current_sequence) >= 3:
                    sequence_pattern = tuple(current_sequence[-3:])
                    action_sequences.append(sequence_pattern)

                    # Check for repetitive patterns
                    if action_sequences.count(sequence_pattern) >= 2:
                        patterns_learned.append({
                            'type': 'action_sequence',
                            'pattern': list(sequence_pattern),
                            'frequency': action_sequences.count(sequence_pattern),
                            'value': 'repetitive_workflow'
                        })

                # Look for data patterns
                if 'success' in data and data['success']:
                    patterns_learned.append({
                        'type': 'success_pattern',
                        'action': action,
                        'data': data,
                        'value': 'successful_action'
                    })

        except Exception as e:
            logger.error(f"[BREADCRUMB] Failed to learn from trail: {e}")

        # Consolidate patterns
        consolidated = {}
        for pattern in patterns_learned:
            key = f"{pattern['type']}_{pattern.get('action', 'unknown')}"
            if key not in consolidated:
                consolidated[key] = pattern
                consolidated[key]['occurrences'] = 1
            else:
                consolidated[key]['occurrences'] += 1

        result = {
            'patterns_learned': len(patterns_learned),
            'unique_patterns': len(consolidated),
            'consolidated_patterns': list(consolidated.values()),
            'total_actions': len(trail_data)
        }

        logger.info(f"[BREADCRUMB] Learned {result['unique_patterns']} patterns from {result['total_actions']} actions")
        return result

    async def get_trail_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the breadcrumb trail

        Returns:
            Trail statistics
        """
        if not self.current_trail:
            return {'trail_length': 0, 'actions': {}, 'coordination_events': 0}

        # Action frequency
        actions = {}
        coordination_count = 0

        for breadcrumb in self.current_trail:
            action = breadcrumb.action
            actions[action] = actions.get(action, 0) + 1

            if breadcrumb.coordination_value:
                coordination_count += 1

        # Time span
        if self.current_trail:
            start_time = self.current_trail[0].timestamp
            end_time = self.current_trail[-1].timestamp
            duration = end_time - start_time
        else:
            duration = timedelta(0)

        return {
            'trail_length': len(self.current_trail),
            'session_id': self.session_id,
            'duration_seconds': duration.total_seconds(),
            'actions': actions,
            'coordination_events': coordination_count,
            'agent_id': self.agent_id,
            'shared_with_agents': len(set(
                agent for b in self.current_trail
                for agent in b.shared_agents
            ))
        }

    async def cleanup_old_trails(self, max_age_days: int = 30):
        """
        Clean up old breadcrumb trail files

        Args:
            max_age_days: Maximum age in days for trail files

        Returns:
            Number of files cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            cleaned_count = 0

            # Find old trail files
            for trail_file in self.storage_path.glob("*.json"):
                try:
                    file_modified = datetime.fromtimestamp(trail_file.stat().st_mtime)
                    if file_modified < cutoff_date:
                        trail_file.unlink()
                        cleaned_count += 1
                except Exception as e:
                    logger.warning(f"[BREADCRUMB] Failed to check/clean {trail_file}: {e}")

            if cleaned_count > 0:
                logger.info(f"[BREADCRUMB] Cleaned up {cleaned_count} old trail files")

            return cleaned_count

        except Exception as e:
            logger.error(f"[BREADCRUMB] Failed to cleanup old trails: {e}")
            return 0





