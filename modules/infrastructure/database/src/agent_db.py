#!/usr/bin/env python3
"""
WSP 78: Agent Memory Database
Shared agent memory and state management.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .db_manager import DatabaseManager


class AgentDB:
    """
    Shared agent memory and state (WSP 78).

    Provides:
    - Agent awakening states
    - Shared memory patterns
    - Error learning (WSP 48)
    """

    def __init__(self):
        """Initialize agent database."""
        self.db = DatabaseManager()
        self._init_tables()

    def _init_tables(self) -> None:
        """Create agent database tables."""
        with self.db.get_connection() as conn:
            # Agent awakening states
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_awakening (
                    agent_id TEXT PRIMARY KEY,
                    consciousness_level TEXT,
                    last_koan TEXT,
                    awakening_timestamp DATETIME
                )
            ''')

            # Shared memory patterns
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    pattern_type TEXT,
                    pattern_data JSON,
                    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Error learning (WSP 48)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_hash TEXT UNIQUE,
                    error_type TEXT,
                    solution JSON,
                    occurrences INTEGER DEFAULT 1
                )
            ''')

            # Breadcrumb trails (WSP 54 multi-agent coordination)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_breadcrumbs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action TEXT,
                    agent_id TEXT DEFAULT '0102',
                    query TEXT,
                    results JSON,
                    related_docs JSON,
                    contract_id TEXT,
                    task_id TEXT,
                    data JSON
                )
            ''')

            # Handoff contracts (multi-agent task assignment)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_contracts (
                    contract_id TEXT PRIMARY KEY,
                    task_description TEXT,
                    assigned_agent TEXT,
                    estimated_minutes INTEGER,
                    priority TEXT DEFAULT 'medium',
                    dependencies JSON,
                    deliverables JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deadline DATETIME,
                    completed_at DATETIME,
                    status TEXT DEFAULT 'active'
                )
            ''')

            # Collaboration signals (agent availability)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_collaboration_signals (
                    agent_id TEXT PRIMARY KEY,
                    collaboration_mode TEXT DEFAULT 'active',
                    available_until DATETIME,
                    skills_offered JSON,
                    current_focus TEXT,
                    last_ping DATETIME DEFAULT CURRENT_TIMESTAMP,
                    autonomy_level TEXT DEFAULT 'semi',
                    workload_capacity REAL DEFAULT 1.0
                )
            ''')

            # Coordination events (inter-agent communication)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_coordination_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    initiator_agent TEXT,
                    target_agents JSON,
                    payload JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolution_status TEXT DEFAULT 'pending'
                )
            ''')

            # Autonomous tasks (discovered work items)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents_autonomous_tasks (
                    task_id TEXT PRIMARY KEY,
                    description TEXT,
                    required_skills JSON,
                    estimated_complexity REAL,
                    priority_score REAL,
                    discovered_by TEXT DEFAULT 'autonomous_discovery',
                    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context JSON,
                    assigned_to TEXT,
                    assigned_at DATETIME
                )

            ''')

            # Index refresh tracking
            conn.execute('''
                CREATE TABLE IF NOT EXISTS index_refresh_tracking (
                    index_type TEXT PRIMARY KEY,
                    last_refresh DATETIME DEFAULT CURRENT_TIMESTAMP,
                    refresh_count INTEGER DEFAULT 0,
                    last_refresh_duration REAL,
                    total_entries_indexed INTEGER DEFAULT 0
                )
            ''')

    def record_awakening(self, agent_id: str, consciousness_level: str, koan: str = None) -> None:
        """Record agent awakening state."""
        with self.db.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO agents_awakening
                (agent_id, consciousness_level, last_koan, awakening_timestamp)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, consciousness_level, koan, datetime.now().isoformat()))

    def get_awakening_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get awakening state for agent."""
        result = self.db.execute_query('''
            SELECT * FROM agents_awakening WHERE agent_id = ?
        ''', (agent_id,))

        if result:
            return dict(result[0])
        return None

    def learn_pattern(self, agent_id: str, pattern_type: str, pattern_data: Dict[str, Any]) -> int:
        """Store a learned pattern."""
        return self.db.execute_write('''
            INSERT INTO agents_memory (agent_id, pattern_type, pattern_data)
            VALUES (?, ?, ?)
        ''', (agent_id, pattern_type, json.dumps(pattern_data)))

    def get_patterns(self, agent_id: str = None, pattern_type: str = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve learned patterns."""
        query = "SELECT * FROM agents_memory WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)

        query += " ORDER BY learned_at DESC LIMIT ?"
        params.append(limit)

        return self.db.execute_query(query, tuple(params))

    def record_error(self, error_hash: str, error_type: str, solution: Dict[str, Any]) -> None:
        """Record error learning (WSP 48)."""
        with self.db.get_connection() as conn:
            # Try to update existing error
            updated = conn.execute('''
                UPDATE agents_errors
                SET occurrences = occurrences + 1
                WHERE error_hash = ?
            ''', (error_hash,)).rowcount

            # If no existing error, insert new one
            if updated == 0:
                conn.execute('''
                    INSERT INTO agents_errors
                    (error_hash, error_type, solution, occurrences)
                    VALUES (?, ?, ?, 1)
                ''', (error_hash, error_type, json.dumps(solution)))

    def get_error_solution(self, error_hash: str) -> Optional[Dict[str, Any]]:
        """Get solution for error."""
        result = self.db.execute_query('''
            SELECT * FROM agents_errors WHERE error_hash = ?
        ''', (error_hash,))

        if result:
            row = dict(result[0])
            row['solution'] = json.loads(row['solution'])
            return row
        return None

    # ============================================================================
    # BREADCRUMB TRAILS (WSP 54 Multi-Agent Coordination)
    # ============================================================================

    def add_breadcrumb(self, session_id: str, action: str, agent_id: str = "0102",
                      query: str = None, results: List[Dict] = None,
                      related_docs: List[str] = None, contract_id: str = None,
                      task_id: str = None, data: Dict[str, Any] = None) -> int:
        """Add a breadcrumb to the trail."""
        return self.db.execute_write('''
            INSERT INTO agents_breadcrumbs
            (session_id, action, agent_id, query, results, related_docs, contract_id, task_id, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, action, agent_id, query,
            json.dumps(results) if results else None,
            json.dumps(related_docs) if related_docs else None,
            contract_id, task_id,
            json.dumps(data) if data else None
        ))

    def get_breadcrumbs(self, session_id: str = None, agent_id: str = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Get breadcrumbs with optional filtering."""
        query = "SELECT * FROM agents_breadcrumbs WHERE 1=1"
        params = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        results = self.db.execute_query(query, tuple(params))

        # Parse JSON fields
        for row in results:
            for field in ['results', 'related_docs', 'data']:
                if row[field] and isinstance(row[field], str):
                    try:
                        row[field] = json.loads(row[field])
                    except json.JSONDecodeError:
                        row[field] = None

        return results

    def get_recent_breadcrumb_agents(self, minutes: int = 120, limit: int = 5) -> List[str]:
        """Get distinct breadcrumb agent IDs within the time window."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        rows = self.execute_query(
            """
            SELECT DISTINCT agent_id
            FROM agents_breadcrumbs
            WHERE agent_id IS NOT NULL AND agent_id != '' AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (cutoff.isoformat(), limit)
        )
        return [row['agent_id'] for row in rows]

    # ============================================================================
    # HANDOFF CONTRACTS (Multi-Agent Task Assignment)
    # ============================================================================

    def create_contract(self, contract_id: str, task_description: str, assigned_agent: str,
                       estimated_minutes: int, priority: str = "medium",
                       dependencies: List[str] = None, deliverables: List[str] = None,
                       deadline: str = None) -> bool:
        """Create a new contract."""
        try:
            self.db.execute_write('''
                INSERT INTO agents_contracts
                (contract_id, task_description, assigned_agent, estimated_minutes, priority,
                 dependencies, deliverables, deadline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_id, task_description, assigned_agent, estimated_minutes, priority,
                json.dumps(dependencies) if dependencies else None,
                json.dumps(deliverables) if deliverables else None,
                deadline
            ))
            return True
        except Exception:
            return False

    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by ID."""
        result = self.db.execute_query('''
            SELECT * FROM agents_contracts WHERE contract_id = ?
        ''', (contract_id,))

        if result:
            contract = dict(result[0])
            # Parse JSON fields
            for field in ['dependencies', 'deliverables']:
                if contract[field] and isinstance(contract[field], str):
                    contract[field] = json.loads(contract[field])
            return contract
        return None

    def update_contract(self, contract_id: str, updates: Dict[str, Any]) -> bool:
        """Update contract fields."""
        if not updates:
            return False

        # Build dynamic update query
        set_parts = []
        params = []
        for field, value in updates.items():
            if field in ['dependencies', 'deliverables']:
                value = json.dumps(value)
            set_parts.append(f"{field} = ?")
            params.append(value)

        params.append(contract_id)  # WHERE clause

        query = f"UPDATE agents_contracts SET {', '.join(set_parts)} WHERE contract_id = ?"
        return self.db.execute_write(query, tuple(params)) > 0

    def complete_contract(self, contract_id: str) -> bool:
        """Mark contract as completed."""
        return self.update_contract(contract_id, {
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        })

    def get_active_contracts(self, agent_filter: str = None) -> List[Dict[str, Any]]:
        """Get active contracts, optionally filtered by assigned agent."""
        query = "SELECT * FROM agents_contracts WHERE status = 'active'"
        params = []

        if agent_filter:
            query += " AND assigned_agent = ?"
            params.append(agent_filter)

        query += " ORDER BY created_at DESC"

        results = self.db.execute_query(query, tuple(params))

        # Parse JSON fields
        for row in results:
            for field in ['dependencies', 'deliverables']:
                if row[field] and isinstance(row[field], str):
                    row[field] = json.loads(row[field])

        return results

    # ============================================================================
    # COLLABORATION SIGNALS (Agent Availability)
    # ============================================================================

    def signal_collaboration(self, agent_id: str, collaboration_mode: str = "active",
                           available_until: str = None, skills_offered: List[str] = None,
                           current_focus: str = "general", autonomy_level: str = "semi",
                           workload_capacity: float = 1.0) -> bool:
        """Signal collaboration readiness."""
        try:
            self.db.execute_write('''
                INSERT OR REPLACE INTO agents_collaboration_signals
                (agent_id, collaboration_mode, available_until, skills_offered,
                 current_focus, autonomy_level, workload_capacity, last_ping)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_id, collaboration_mode, available_until,
                json.dumps(skills_offered) if skills_offered else None,
                current_focus, autonomy_level, workload_capacity,
                datetime.now().isoformat()
            ))
            return True
        except Exception:
            return False

    def get_collaborators(self, required_skills: List[str] = None) -> List[Dict[str, Any]]:
        """Get available collaborators, optionally filtered by skills."""
        query = """
            SELECT * FROM agents_collaboration_signals
            WHERE available_until > ?
        """
        params = [datetime.now().isoformat()]

        if required_skills:
            # Complex skill matching query
            skill_conditions = []
            for skill in required_skills:
                skill_conditions.append("skills_offered LIKE ?")
                params.append(f'%"{skill}"%')
            query += f" AND ({' OR '.join(skill_conditions)})"

        query += " ORDER BY workload_capacity DESC, last_ping DESC"

        results = self.db.execute_query(query, tuple(params))

        # Parse JSON fields
        for row in results:
            if row['skills_offered'] and isinstance(row['skills_offered'], str):
                row['skills_offered'] = json.loads(row['skills_offered'])

        return results

    # ============================================================================
    # COORDINATION EVENTS (Inter-Agent Communication)
    # ============================================================================

    def create_coordination_event(self, event_id: str, event_type: str,
                                initiator_agent: str, target_agents: List[str],
                                payload: Dict[str, Any]) -> bool:
        """Create a coordination event."""
        try:
            self.db.execute_write('''
                INSERT INTO agents_coordination_events
                (event_id, event_type, initiator_agent, target_agents, payload)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                event_id, event_type, initiator_agent,
                json.dumps(target_agents), json.dumps(payload)
            ))
            return True
        except Exception:
            return False

    def get_coordination_events(self, status: str = "pending", limit: int = 50) -> List[Dict[str, Any]]:
        """Get coordination events by status."""
        results = self.db.execute_query('''
            SELECT * FROM agents_coordination_events
            WHERE resolution_status = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (status, limit))

        # Parse JSON fields
        for row in results:
            for field in ['target_agents', 'payload']:
                if row[field] and isinstance(row[field], str):
                    row[field] = json.loads(row[field])

        return results

    def resolve_coordination_event(self, event_id: str, status: str = "completed") -> bool:
        """Mark coordination event as resolved."""
        return self.db.execute_write('''
            UPDATE agents_coordination_events
            SET resolution_status = ?
            WHERE event_id = ?
        ''', (status, event_id)) > 0

    # ============================================================================
    # AUTONOMOUS TASKS (Discovered Work Items)
    # ============================================================================

    def create_autonomous_task(self, task_id: str, description: str,
                             required_skills: List[str], estimated_complexity: float,
                             priority_score: float, context: Dict[str, Any] = None) -> bool:
        """Create an autonomous task."""
        try:
            self.db.execute_write('''
                INSERT OR REPLACE INTO agents_autonomous_tasks
                (task_id, description, required_skills, estimated_complexity,
                 priority_score, context)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task_id, description, json.dumps(required_skills),
                estimated_complexity, priority_score,
                json.dumps(context) if context else None
            ))
            return True
        except Exception:
            return False

    def get_autonomous_tasks(self, status: str = "pending", limit: int = 50) -> List[Dict[str, Any]]:
        """Get autonomous tasks by status."""
        results = self.db.execute_query('''
            SELECT * FROM agents_autonomous_tasks
            WHERE status = ?
            ORDER BY priority_score DESC, discovered_at DESC LIMIT ?
        ''', (status, limit))

        # Parse JSON fields
        for row in results:
            for field in ['required_skills', 'context']:
                if row[field] and isinstance(row[field], str):
                    row[field] = json.loads(row[field])

        return results

    def assign_autonomous_task(self, task_id: str, agent_id: str) -> bool:
        """Assign autonomous task to agent."""
        return self.db.execute_write('''
            UPDATE agents_autonomous_tasks
            SET assigned_to = ?, assigned_at = ?, status = 'assigned'
            WHERE task_id = ?
        ''', (agent_id, datetime.now().isoformat(), task_id)) > 0

    def complete_autonomous_task(self, task_id: str) -> bool:
        """Mark autonomous task as completed."""
        return self.db.execute_write('''
            UPDATE agents_autonomous_tasks
            SET completed_at = ?, status = 'completed'
            WHERE task_id = ?
        ''', (datetime.now().isoformat(), task_id)) > 0

    # ============================================================================
    # INDEX REFRESH TRACKING (HoloIndex Automation)
    # ============================================================================

    def record_index_refresh(self, index_type: str, duration: float, entries_count: int) -> None:
        """Record successful index refresh."""
        with self.db.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO index_refresh_tracking
                (index_type, last_refresh, refresh_count, last_refresh_duration, total_entries_indexed)
                VALUES (
                    ?,
                    ?,
                    COALESCE((SELECT refresh_count FROM index_refresh_tracking WHERE index_type = ?), 0) + 1,
                    ?,
                    ?
                )
            ''', (index_type, datetime.now(), index_type, duration, entries_count))

    def get_last_index_refresh(self, index_type: str) -> Optional[datetime]:
        """Get timestamp of last index refresh."""
        result = self.db.execute_query(
            "SELECT last_refresh FROM index_refresh_tracking WHERE index_type = ?",
            (index_type,)
        )
        return result[0]['last_refresh'] if result else None

    def should_refresh_index(self, index_type: str, max_age_hours: int = 24) -> bool:
        """Check if index should be refreshed based on age."""
        last_refresh = self.get_last_index_refresh(index_type)
        if not last_refresh:
            return True  # Never refreshed, should refresh

        # Parse the datetime string
        if isinstance(last_refresh, str):
            last_refresh = datetime.fromisoformat(last_refresh.replace('Z', '+00:00'))

        age = datetime.now() - last_refresh
        return age.total_seconds() > (max_age_hours * 3600)
