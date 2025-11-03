# -*- coding: utf-8 -*-
"""
Agent Permission Manager - Graduated Autonomy System
Manages agent permissions with confidence-based escalation

WSP Compliance:
- WSP 77 (Agent Coordination): Permission escalation based on proven ability
- WSP 50 (Pre-Action Verification): Verify permissions before operations
- WSP 91 (Observability): Permission events logged to JSONL

Integration:
- skills_registry.json: Single source of truth for skills + permissions
- ConfidenceTracker: Confidence scoring with decay
- PatchExecutor: Allowlist validation patterns
"""

import json
import hashlib
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

from .confidence_tracker import ConfidenceTracker


logger = logging.getLogger(__name__)


# Permission escalation thresholds (from design doc Upgrade 2)
PROMOTION_THRESHOLDS = {
    'metrics_write': {
        'confidence_required': 0.75,
        'successful_executions': 10,
        'human_validations': 5,
        'trial_period_days': 7
    },
    'edit_access_tests': {
        'confidence_required': 0.85,
        'successful_executions': 25,
        'human_validations': 10,
        'trial_period_days': 14,
        'allowlist': ['modules/**/tests/**/*.py', 'modules/**/docs/**/*.md']
    },
    'edit_access_src': {
        'confidence_required': 0.95,
        'successful_executions': 100,
        'human_validations': 50,
        'trial_period_days': 30,
        'allowlist': ['modules/**/*.py'],
        'forbidlist': ['main.py', 'modules/**/*_dae.py', '.env']
    }
}

# Downgrade thresholds (lower than promotion)
DOWNGRADE_THRESHOLDS = {
    'edit_access_src': 0.90,
    'edit_access_tests': 0.80,
    'metrics_write': 0.70
}


@dataclass
class PermissionCheckResult:
    """Result of permission check"""
    allowed: bool
    reason: str
    permission_level: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class PermissionRecord:
    """Permission record for an agent"""
    agent_id: str
    permission_level: str
    granted_at: datetime
    granted_by: str
    expires_at: datetime
    confidence_at_grant: float
    allowlist_patterns: List[str]
    forbidlist_patterns: List[str]
    justification: str
    approval_signature: str


class AgentPermissionManager:
    """
    Manage agent permissions with confidence-based escalation

    Features:
    - Unified skills_registry.json (single source of truth)
    - Permission events JSONL audit trail
    - Automatic downgrade on confidence drop
    - Allowlist/forbidlist validation
    """

    def __init__(self, repo_root: Path):
        """
        Initialize permission manager

        Args:
            repo_root: Repository root directory
        """
        self.repo_root = Path(repo_root)

        # Paths
        self.skills_registry_path = self.repo_root / ".claude" / "skills" / "skills_registry.json"
        self.db_path = self.repo_root / "data" / "foundup.db"

        # Ensure directories exist
        self.skills_registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Load skills registry
        self.skills_registry = self._load_skills_registry()

        # Initialize confidence tracker
        self.confidence_tracker = ConfidenceTracker(repo_root=repo_root)

    def _load_skills_registry(self) -> Dict[str, Any]:
        """Load skills registry from .claude/skills/skills_registry.json"""
        if not self.skills_registry_path.exists():
            return {'skills': [], 'version': '1.0.0'}

        try:
            with open(self.skills_registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load skills registry: {e}")
            return {'skills': [], 'version': '1.0.0'}

    def _save_skills_registry(self) -> None:
        """Save skills registry (atomic write)"""
        try:
            temp_path = self.skills_registry_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(self.skills_registry, f, indent=2)
            temp_path.replace(self.skills_registry_path)
            logger.info("[REGISTRY] Skills registry saved")
        except Exception as e:
            logger.error(f"Failed to save skills registry: {e}")

    def _find_skill(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Find skill in registry by agent_id"""
        for skill in self.skills_registry.get('skills', []):
            if skill.get('name') == agent_id or skill.get('agent') == agent_id:
                return skill
        return None

    def _append_permission_event(self, event: Dict[str, Any]) -> None:
        """Append permission event to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO permission_events (
                    agent_id, event_type, permission_level, granted_at,
                    granted_by, confidence, justification, approval_signature,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('agent_id'),
                event.get('event_type'),
                event.get('permission'),
                event.get('granted_at'),
                event.get('granted_by'),
                event.get('confidence_at_grant'),
                event.get('justification'),
                event.get('approval_signature'),
                json.dumps(event.get('metadata', {}))
            ))
            conn.commit()
            conn.close()
            logger.debug(f"[PERMISSION_EVENT] {event['event_type']} for {event['agent_id']}")
        except Exception as e:
            logger.error(f"Failed to append permission event: {e}")

    def _generate_approval_signature(
        self,
        agent_id: str,
        permission: str,
        granted_by: str,
        timestamp: datetime
    ) -> str:
        """
        Generate cryptographic signature for permission grant
        Enables WSP 50 audit verification
        """
        approval_data = {
            'agent_id': agent_id,
            'permission': permission,
            'granted_by': granted_by,
            'timestamp': timestamp.isoformat()
        }

        signature_string = json.dumps(approval_data, sort_keys=True)
        return f"sha256:{hashlib.sha256(signature_string.encode()).hexdigest()}"

    def _file_matches_patterns(
        self,
        file_path: str,
        patterns: List[str],
        is_forbid: bool = False
    ) -> bool:
        """
        Check if file matches patterns (allowlist or forbidlist)

        Args:
            file_path: File path to check
            patterns: List of glob patterns
            is_forbid: True if checking forbidlist (any match = forbidden)

        Returns:
            True if matches (allowed or forbidden based on is_forbid)
        """
        from pathlib import PurePosixPath

        # Normalize to POSIX path
        path = PurePosixPath(file_path.replace('\\', '/'))

        for pattern in patterns:
            # Handle ** recursive glob
            if '**' in pattern:
                parts = pattern.split('**/')
                if len(parts) == 2:
                    prefix, suffix = parts
                    path_str = str(path)

                    if prefix and not path_str.startswith(prefix.rstrip('/')):
                        continue

                    if prefix:
                        remaining = path_str[len(prefix.rstrip('/')):]
                        if remaining.startswith('/'):
                            remaining = remaining[1:]
                    else:
                        remaining = path_str

                    if PurePosixPath(remaining).match(suffix):
                        return True
            else:
                if path.match(pattern):
                    return True

        return False

    def check_permission(
        self,
        agent_id: str,
        operation: str,
        file_path: Optional[str] = None
    ) -> PermissionCheckResult:
        """
        Check if agent has permission for operation

        Args:
            agent_id: Agent identifier
            operation: Operation type ('read', 'metrics_write', 'edit', 'write')
            file_path: Optional file path for edit/write operations

        Returns:
            PermissionCheckResult with allow/deny decision
        """
        # Find skill in registry
        skill = self._find_skill(agent_id)

        if not skill:
            return PermissionCheckResult(
                allowed=False,
                reason=f"Agent {agent_id} not registered in skills_registry.json"
            )

        # Check expiration
        expires_at_str = skill.get('permission_expires_at')
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now() > expires_at:
                    return PermissionCheckResult(
                        allowed=False,
                        reason=f"Permission expired on {expires_at}"
                    )
            except ValueError:
                pass

        # Get permission level
        permission_level = skill.get('permission_level', 'read_only')

        # Operation permission mapping
        operation_permissions = {
            'read': ['read_only', 'metrics_write', 'edit_access_tests', 'edit_access_src'],
            'metrics_write': ['metrics_write', 'edit_access_tests', 'edit_access_src'],
            'edit': ['edit_access_tests', 'edit_access_src'],
            'write': ['edit_access_tests', 'edit_access_src']
        }

        allowed_permissions = operation_permissions.get(operation, [])
        if permission_level not in allowed_permissions:
            return PermissionCheckResult(
                allowed=False,
                reason=f"Permission level '{permission_level}' insufficient for operation '{operation}'"
            )

        # Check file path for edit/write operations
        if file_path and operation in ['edit', 'write']:
            # Get allowlist/forbidlist from promotion history
            promotion_history = skill.get('promotion_history', [])
            if promotion_history:
                latest = promotion_history[-1]
                allowlist = latest.get('allowlist_patterns', [])
                forbidlist = latest.get('forbidlist_patterns', [])

                # Check forbidlist first (any match = forbidden)
                if forbidlist and self._file_matches_patterns(file_path, forbidlist, is_forbid=True):
                    return PermissionCheckResult(
                        allowed=False,
                        reason=f"File {file_path} in forbidlist"
                    )

                # Check allowlist
                if allowlist and not self._file_matches_patterns(file_path, allowlist):
                    return PermissionCheckResult(
                        allowed=False,
                        reason=f"File {file_path} not in allowlist"
                    )

        # Check confidence (must remain above downgrade threshold)
        current_confidence = self.confidence_tracker.get_confidence(agent_id)
        downgrade_threshold = DOWNGRADE_THRESHOLDS.get(permission_level, 0.0)

        if current_confidence < downgrade_threshold:
            logger.warning(
                f"[PERMISSION-DENIED] {agent_id}: Confidence {current_confidence:.2f} "
                f"below downgrade threshold {downgrade_threshold}"
            )
            return PermissionCheckResult(
                allowed=False,
                reason=f"Confidence {current_confidence:.2f} below threshold {downgrade_threshold}"
            )

        return PermissionCheckResult(
            allowed=True,
            reason="Permission granted",
            permission_level=permission_level,
            confidence=current_confidence
        )

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        description: str,
        permission_level: str = "read_only"
    ) -> bool:
        """
        Register a new agent with initial permissions

        Convenience method that wraps grant_permission() for agent creation.

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (e.g., 'detection', 'investigation', 'execution')
            description: Human-readable description
            permission_level: Initial permission level (default: read_only)

        Returns:
            True if registration successful
        """
        try:
            self.grant_permission(
                agent_id=agent_id,
                permission_type=permission_level,
                granted_by="system",
                duration_days=365,  # Long duration for initial registration
                justification=f"Agent registration: {description}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False

    def grant_permission(
        self,
        agent_id: str,
        permission_type: str,
        granted_by: str,
        duration_days: int = 30,
        allowlist_patterns: Optional[List[str]] = None,
        forbidlist_patterns: Optional[List[str]] = None,
        justification: Optional[str] = None
    ) -> PermissionRecord:
        """
        Grant permission and update skills registry

        Args:
            agent_id: Agent identifier
            permission_type: Permission level to grant
            granted_by: Who granted ('0102', '012', 'system_automatic')
            duration_days: Permission validity duration
            allowlist_patterns: File patterns allowed
            forbidlist_patterns: File patterns forbidden
            justification: Reason for granting

        Returns:
            PermissionRecord
        """
        # Find or create skill
        skill = self._find_skill(agent_id)
        if not skill:
            skill = {
                'name': agent_id,
                'agent': agent_id.split('_')[0] if '_' in agent_id else 'unknown',
                'status': 'prototype',
                'permission_level': 'read_only',
                'promotion_history': []
            }
            self.skills_registry.setdefault('skills', []).append(skill)

        # Create permission record
        granted_at = datetime.now()
        expires_at = granted_at + timedelta(days=duration_days)

        # Use defaults from PROMOTION_THRESHOLDS if not provided
        if allowlist_patterns is None:
            threshold_config = PROMOTION_THRESHOLDS.get(permission_type, {})
            allowlist_patterns = threshold_config.get('allowlist', [])

        if forbidlist_patterns is None:
            threshold_config = PROMOTION_THRESHOLDS.get(permission_type, {})
            forbidlist_patterns = threshold_config.get('forbidlist', [])

        confidence_at_grant = self.confidence_tracker.get_confidence(agent_id)
        approval_signature = self._generate_approval_signature(
            agent_id, permission_type, granted_by, granted_at
        )

        # Update skill in registry
        old_permission = skill.get('permission_level', 'read_only')
        skill['permission_level'] = permission_type
        skill['permission_granted_at'] = granted_at.isoformat()
        skill['permission_granted_by'] = granted_by
        skill['permission_expires_at'] = expires_at.isoformat()
        skill['confidence_score'] = confidence_at_grant

        # Add to promotion history
        skill.setdefault('promotion_history', []).append({
            'from': old_permission,
            'to': permission_type,
            'date': granted_at.isoformat(),
            'reason': justification or f"Permission escalation to {permission_type}",
            'confidence': confidence_at_grant,
            'approval_signature': approval_signature,
            'allowlist_patterns': allowlist_patterns,
            'forbidlist_patterns': forbidlist_patterns
        })

        # Save registry
        self._save_skills_registry()

        # Append to audit trail
        self._append_permission_event({
            'event_id': f"perm_{int(granted_at.timestamp())}",
            'event_type': 'PERMISSION_GRANTED',
            'agent_id': agent_id,
            'permission': permission_type,
            'granted_by': granted_by,
            'granted_at': granted_at.isoformat(),
            'expires_at': expires_at.isoformat(),
            'confidence_at_grant': confidence_at_grant,
            'justification': justification,
            'approval_signature': approval_signature
        })

        logger.info(
            f"[PERMISSION-GRANTED] {agent_id}: {old_permission} → {permission_type} "
            f"(granted by {granted_by}, confidence: {confidence_at_grant:.2f})"
        )

        return PermissionRecord(
            agent_id=agent_id,
            permission_level=permission_type,
            granted_at=granted_at,
            granted_by=granted_by,
            expires_at=expires_at,
            confidence_at_grant=confidence_at_grant,
            allowlist_patterns=allowlist_patterns,
            forbidlist_patterns=forbidlist_patterns,
            justification=justification or "",
            approval_signature=approval_signature
        )

    def downgrade_permission(
        self,
        agent_id: str,
        reason: str,
        requires_reapproval: bool = True
    ) -> bool:
        """
        Automatically downgrade agent permissions

        Args:
            agent_id: Agent identifier
            reason: Reason for downgrade
            requires_reapproval: Require human re-approval before escalation

        Returns:
            True if downgrade successful
        """
        skill = self._find_skill(agent_id)
        if not skill:
            logger.warning(f"[DOWNGRADE] Agent {agent_id} not found")
            return False

        current_permission = skill.get('permission_level', 'read_only')

        # Permission ladder (order matters)
        permission_ladder = ['read_only', 'metrics_write', 'edit_access_tests', 'edit_access_src']

        try:
            current_idx = permission_ladder.index(current_permission)
        except ValueError:
            logger.warning(f"[DOWNGRADE] Unknown permission level: {current_permission}")
            return False

        # One level down
        new_permission = permission_ladder[max(0, current_idx - 1)]

        if new_permission == current_permission:
            logger.info(f"[DOWNGRADE] {agent_id} already at lowest permission")
            return True

        # Update skill
        skill['permission_level'] = new_permission
        skill['permission_downgraded_at'] = datetime.now().isoformat()
        skill['permission_downgrade_reason'] = reason
        skill['requires_reapproval'] = requires_reapproval

        # Save registry
        self._save_skills_registry()

        # Append to audit trail
        self._append_permission_event({
            'event_id': f"perm_{int(datetime.now().timestamp())}",
            'event_type': 'PERMISSION_DOWNGRADE',
            'agent_id': agent_id,
            'permission_before': current_permission,
            'permission_after': new_permission,
            'reason': reason,
            'downgraded_by': 'system_automatic',
            'requires_reapproval': requires_reapproval,
            'timestamp': datetime.now().isoformat()
        })

        logger.warning(
            f"[PERMISSION-DOWNGRADE] {agent_id}: {current_permission} → {new_permission} "
            f"(reason: {reason})"
        )

        return True

    def get_permission_level(self, agent_id: str) -> str:
        """Get current permission level for agent"""
        skill = self._find_skill(agent_id)
        if skill:
            return skill.get('permission_level', 'read_only')
        return 'read_only'
