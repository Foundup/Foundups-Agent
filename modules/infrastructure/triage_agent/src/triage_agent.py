"""
Triage Agent - WSP/WRE Infrastructure Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive triage and testing capabilities
- WSP 54 (Agent Duties): AI-powered triage for autonomous infrastructure
- WSP 22 (ModLog): Change tracking and triage history
- WSP 50 (Pre-Action Verification): Enhanced verification before triage operations

Provides AI-powered triage capabilities for autonomous infrastructure operations.
Enables 0102 pArtifacts to prioritize and route issues, tasks, and requests based on urgency and impact.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import heapq


class PriorityLevel(Enum):
    """Priority levels for triage."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


class IssueType(Enum):
    """Types of issues for triage."""
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    WSP_VIOLATION = "wsp_violation"
    SYSTEM_ERROR = "system_error"
    USER_REQUEST = "user_request"
    MAINTENANCE = "maintenance"


class TriageStatus(Enum):
    """Triage status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


@dataclass
class TriageItem:
    """Triage item data structure."""
    item_id: str
    title: str
    description: str
    issue_type: IssueType
    priority: PriorityLevel
    status: TriageStatus
    source: str
    reporter: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    wsp_references: List[str]
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class TriageResult:
    """Result of triage operation."""
    item_id: str
    priority: PriorityLevel
    assigned_agent: str
    estimated_effort: str
    recommended_actions: List[str]
    wsp_compliance_score: float
    triage_reason: str
    timestamp: datetime


@dataclass
class TriageStats:
    """Triage statistics."""
    total_items: int
    items_by_priority: Dict[str, int]
    items_by_status: Dict[str, int]
    items_by_type: Dict[str, int]
    average_resolution_time: timedelta
    wsp_violations: int


class TriageAgent:
    """
    AI-powered triage agent for autonomous infrastructure operations.
    
    Provides comprehensive triage capabilities including:
    - Issue prioritization and routing
    - WSP compliance assessment
    - Agent assignment and workload balancing
    - Resolution time estimation
    - Escalation management
    """
    
    def __init__(self):
        """Initialize the triage agent with WSP compliance standards."""
        self.triage_items = {}
        self.available_agents = {
            'compliance_agent': {'specialties': ['wsp_violation', 'compliance'], 'workload': 0},
            'security_agent': {'specialties': ['security_issue', 'bug'], 'workload': 0},
            'performance_agent': {'specialties': ['performance_issue', 'system_error'], 'workload': 0},
            'development_agent': {'specialties': ['feature_request', 'bug', 'maintenance'], 'workload': 0},
            'user_support_agent': {'specialties': ['user_request', 'bug'], 'workload': 0}
        }
        
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation'
        ]
        
    def triage_item(self, title: str, description: str, issue_type: IssueType,
                   source: str, reporter: str, wsp_references: List[str] = None,
                   tags: List[str] = None, metadata: Dict[str, Any] = None) -> TriageResult:
        """
        Triage a new item.
        
        Args:
            title: Item title
            description: Item description
            issue_type: Type of issue
            source: Source of the item
            reporter: Person reporting the item
            wsp_references: Optional WSP references
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            TriageResult with triage decision
        """
        try:
            # Generate item ID
            item_id = self._generate_item_id(title, source, datetime.now())
            
            # Determine priority
            priority = self._determine_priority(title, description, issue_type, wsp_references)
            
            # Assign agent
            assigned_agent = self._assign_agent(issue_type, priority, wsp_references)
            
            # Estimate effort
            estimated_effort = self._estimate_effort(priority, issue_type, description)
            
            # Generate recommendations
            recommended_actions = self._generate_recommendations(issue_type, priority, wsp_references)
            
            # Calculate WSP compliance score
            wsp_compliance_score = self._calculate_wsp_compliance_score(wsp_references, issue_type)
            
            # Generate triage reason
            triage_reason = self._generate_triage_reason(priority, assigned_agent, issue_type)
            
            # Create triage item
            triage_item = TriageItem(
                item_id=item_id,
                title=title,
                description=description,
                issue_type=issue_type,
                priority=priority,
                status=TriageStatus.PENDING,
                source=source,
                reporter=reporter,
                assigned_to=assigned_agent,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=self._calculate_due_date(priority),
                wsp_references=wsp_references or [],
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # Store triage item
            self.triage_items[item_id] = triage_item
            
            # Update agent workload
            self._update_agent_workload(assigned_agent)
            
            return TriageResult(
                item_id=item_id,
                priority=priority,
                assigned_agent=assigned_agent,
                estimated_effort=estimated_effort,
                recommended_actions=recommended_actions,
                wsp_compliance_score=wsp_compliance_score,
                triage_reason=triage_reason,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            # Return error result
            return TriageResult(
                item_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                priority=PriorityLevel.MINIMAL,
                assigned_agent="error_handler",
                estimated_effort="Unknown",
                recommended_actions=[f"Error during triage: {str(e)}"],
                wsp_compliance_score=0.0,
                triage_reason="Error occurred during triage",
                timestamp=datetime.now()
            )
    
    def update_item_status(self, item_id: str, status: TriageStatus, 
                          assigned_to: str = None, notes: str = None) -> bool:
        """
        Update the status of a triage item.
        
        Args:
            item_id: ID of the item to update
            status: New status
            assigned_to: Optional new assignee
            notes: Optional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if item_id not in self.triage_items:
                return False
            
            item = self.triage_items[item_id]
            item.status = status
            item.updated_at = datetime.now()
            
            if assigned_to:
                item.assigned_to = assigned_to
                self._update_agent_workload(assigned_to)
            
            if notes:
                item.metadata['notes'] = notes
            
            return True
                
        except Exception as e:
            print(f"Error updating item status: {e}")
            return False
    
    def get_items_by_priority(self, priority: PriorityLevel) -> List[TriageItem]:
        """
        Get all items with a specific priority.
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            List of TriageItem objects
        """
        return [item for item in self.triage_items.values() if item.priority == priority]
    
    def get_items_by_status(self, status: TriageStatus) -> List[TriageItem]:
        """
        Get all items with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of TriageItem objects
        """
        return [item for item in self.triage_items.values() if item.status == status]
    
    def get_items_by_agent(self, agent: str) -> List[TriageItem]:
        """
        Get all items assigned to a specific agent.
        
        Args:
            agent: Agent name
            
        Returns:
            List of TriageItem objects
        """
        return [item for item in self.triage_items.values() if item.assigned_to == agent]
    
    def get_triage_stats(self) -> TriageStats:
        """
        Get triage statistics.
        
        Returns:
            TriageStats object with statistics
        """
        try:
            items_by_priority = {}
            items_by_status = {}
            items_by_type = {}
            wsp_violations = 0
            resolution_times = []
            
            for item in self.triage_items.values():
                # Priority statistics
                priority_key = item.priority.name
                items_by_priority[priority_key] = items_by_priority.get(priority_key, 0) + 1
                
                # Status statistics
                status_key = item.status.name
                items_by_status[status_key] = items_by_status.get(status_key, 0) + 1
                
                # Type statistics
                type_key = item.issue_type.name
                items_by_type[type_key] = items_by_type.get(type_key, 0) + 1
                
                # WSP violations
                if item.issue_type == IssueType.WSP_VIOLATION:
                    wsp_violations += 1
                
                # Resolution time for resolved items
                if item.status == TriageStatus.RESOLVED:
                    resolution_time = item.updated_at - item.created_at
                    resolution_times.append(resolution_time)
            
            # Calculate average resolution time
            if resolution_times:
                avg_resolution_time = sum(resolution_times, timedelta()) / len(resolution_times)
            else:
                avg_resolution_time = timedelta()
            
            return TriageStats(
                total_items=len(self.triage_items),
                items_by_priority=items_by_priority,
                items_by_status=items_by_status,
                items_by_type=items_by_type,
                average_resolution_time=avg_resolution_time,
                wsp_violations=wsp_violations
            )
                            
                except Exception as e:
            print(f"Error getting triage stats: {e}")
            return TriageStats(
                total_items=0,
                items_by_priority={},
                items_by_status={},
                items_by_type={},
                average_resolution_time=timedelta(),
                wsp_violations=0
            )
    
    def _generate_item_id(self, title: str, source: str, timestamp: datetime) -> str:
        """Generate a unique item ID."""
        import hashlib
        data_string = f"{title}_{source}_{timestamp.isoformat()}"
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]
    
    def _determine_priority(self, title: str, description: str, issue_type: IssueType,
                          wsp_references: List[str]) -> PriorityLevel:
        """Determine priority based on content and type."""
        priority_score = 0
        
        # Base priority by issue type
        type_priorities = {
            IssueType.SECURITY_ISSUE: 4,
            IssueType.WSP_VIOLATION: 4,
            IssueType.SYSTEM_ERROR: 3,
            IssueType.BUG: 2,
            IssueType.PERFORMANCE_ISSUE: 2,
            IssueType.FEATURE_REQUEST: 1,
            IssueType.USER_REQUEST: 1,
            IssueType.MAINTENANCE: 1
        }
        
        priority_score += type_priorities.get(issue_type, 1)
        
        # Priority keywords
        critical_keywords = ['critical', 'urgent', 'emergency', 'broken', 'down', 'failed']
        high_keywords = ['important', 'blocking', 'major', 'severe', 'high']
        medium_keywords = ['moderate', 'minor', 'low']
        
        content = f"{title} {description}".lower()
        
        if any(keyword in content for keyword in critical_keywords):
            priority_score += 3
        elif any(keyword in content for keyword in high_keywords):
            priority_score += 2
        elif any(keyword in content for keyword in medium_keywords):
            priority_score += 1
        
        # WSP violations get higher priority
        if wsp_references:
            priority_score += 2
        
        # Map score to priority level
        if priority_score >= 6:
            return PriorityLevel.CRITICAL
        elif priority_score >= 4:
            return PriorityLevel.HIGH
        elif priority_score >= 2:
            return PriorityLevel.MEDIUM
        elif priority_score >= 1:
            return PriorityLevel.LOW
        else:
            return PriorityLevel.MINIMAL
    
    def _assign_agent(self, issue_type: IssueType, priority: PriorityLevel,
                     wsp_references: List[str]) -> str:
        """Assign the best agent for the issue."""
        best_agent = None
        best_score = -1
        
        for agent, info in self.available_agents.items():
            score = 0
            
            # Check if agent specializes in this issue type
            if issue_type.name in info['specialties']:
                score += 3
            
            # WSP violations should go to compliance agent
            if issue_type == IssueType.WSP_VIOLATION and agent == 'compliance_agent':
                score += 5
            
            # Security issues should go to security agent
            if issue_type == IssueType.SECURITY_ISSUE and agent == 'security_agent':
                score += 4
            
            # Consider workload (prefer less busy agents)
            workload_penalty = info['workload'] * 0.5
            score -= workload_penalty
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent or 'development_agent'  # Default fallback
    
    def _estimate_effort(self, priority: PriorityLevel, issue_type: IssueType, 
                        description: str) -> str:
        """Estimate effort required to resolve the issue."""
        base_effort = {
            PriorityLevel.CRITICAL: 8,
            PriorityLevel.HIGH: 4,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 1,
            PriorityLevel.MINIMAL: 0.5
        }
        
        effort_hours = base_effort.get(priority, 2)
        
        # Adjust based on issue type
        type_multipliers = {
            IssueType.SECURITY_ISSUE: 1.5,
            IssueType.WSP_VIOLATION: 1.3,
            IssueType.SYSTEM_ERROR: 1.2,
            IssueType.PERFORMANCE_ISSUE: 1.1,
            IssueType.FEATURE_REQUEST: 0.8
        }
        
        multiplier = type_multipliers.get(issue_type, 1.0)
        effort_hours *= multiplier
        
        # Adjust based on description length (complexity indicator)
        if len(description) > 500:
            effort_hours *= 1.2
        elif len(description) < 100:
            effort_hours *= 0.8
        
        if effort_hours <= 1:
            return "Very Low (1 hour or less)"
        elif effort_hours <= 4:
            return "Low (1-4 hours)"
        elif effort_hours <= 8:
            return "Medium (4-8 hours)"
        elif effort_hours <= 16:
            return "High (1-2 days)"
        else:
            return "Very High (2+ days)"
    
    def _generate_recommendations(self, issue_type: IssueType, priority: PriorityLevel,
                                wsp_references: List[str]) -> List[str]:
        """Generate recommendations for handling the issue."""
        recommendations = []
        
        # Priority-based recommendations
        if priority == PriorityLevel.CRITICAL:
            recommendations.append("Immediate attention required - escalate if needed")
        elif priority == PriorityLevel.HIGH:
            recommendations.append("Address within 24 hours")
        elif priority == PriorityLevel.MEDIUM:
            recommendations.append("Address within 1 week")
        else:
            recommendations.append("Address when resources are available")
        
        # Issue type specific recommendations
        if issue_type == IssueType.SECURITY_ISSUE:
            recommendations.append("Follow security incident response procedures")
        elif issue_type == IssueType.WSP_VIOLATION:
            recommendations.append("Ensure WSP compliance documentation is updated")
        elif issue_type == IssueType.PERFORMANCE_ISSUE:
            recommendations.append("Monitor performance metrics after resolution")
        elif issue_type == IssueType.FEATURE_REQUEST:
            recommendations.append("Validate requirements with stakeholders")
        
        # WSP-specific recommendations
        if wsp_references:
            recommendations.append("Review WSP compliance requirements")
            recommendations.append("Update ModLog.md with resolution details")
        
        return recommendations
    
    def _calculate_wsp_compliance_score(self, wsp_references: List[str], 
                                      issue_type: IssueType) -> float:
        """Calculate WSP compliance score for the issue."""
        score = 50.0  # Base score
        
        # WSP violations get lower scores
        if issue_type == IssueType.WSP_VIOLATION:
            score -= 30.0
        
        # WSP references indicate compliance awareness
        if wsp_references:
            score += 20.0
        
        # Security issues affect compliance
        if issue_type == IssueType.SECURITY_ISSUE:
            score -= 10.0
        
        return max(0.0, min(100.0, score))
    
    def _generate_triage_reason(self, priority: PriorityLevel, assigned_agent: str,
                              issue_type: IssueType) -> str:
        """Generate reason for triage decision."""
        reasons = []
        
        if priority == PriorityLevel.CRITICAL:
            reasons.append("Critical priority requires immediate attention")
        elif priority == PriorityLevel.HIGH:
            reasons.append("High priority issue needs prompt resolution")
        
        reasons.append(f"Assigned to {assigned_agent} based on issue type ({issue_type.name})")
        
        if issue_type == IssueType.WSP_VIOLATION:
            reasons.append("WSP compliance issue requires specialized handling")
        elif issue_type == IssueType.SECURITY_ISSUE:
            reasons.append("Security issue requires security agent expertise")
        
        return "; ".join(reasons)
    
    def _calculate_due_date(self, priority: PriorityLevel) -> datetime:
        """Calculate due date based on priority."""
        now = datetime.now()
        
        due_dates = {
            PriorityLevel.CRITICAL: now + timedelta(hours=4),
            PriorityLevel.HIGH: now + timedelta(days=1),
            PriorityLevel.MEDIUM: now + timedelta(days=7),
            PriorityLevel.LOW: now + timedelta(days=30),
            PriorityLevel.MINIMAL: now + timedelta(days=90)
        }
        
        return due_dates.get(priority, now + timedelta(days=7))
    
    def _update_agent_workload(self, agent: str):
        """Update agent workload."""
        if agent in self.available_agents:
            self.available_agents[agent]['workload'] += 1
    
    def save_triage_data(self, output_file: str) -> bool:
        """
        Save triage data to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'items': {},
                'agents': self.available_agents
            }
            
            for item_id, item in self.triage_items.items():
                data['items'][item_id] = {
                    'title': item.title,
                    'description': item.description,
                    'issue_type': item.issue_type.name,
                    'priority': item.priority.name,
                    'status': item.status.name,
                    'source': item.source,
                    'reporter': item.reporter,
                    'assigned_to': item.assigned_to,
                    'created_at': item.created_at.isoformat(),
                    'updated_at': item.updated_at.isoformat(),
                    'due_date': item.due_date.isoformat() if item.due_date else None,
                    'wsp_references': item.wsp_references,
                    'tags': item.tags,
                    'metadata': item.metadata
                }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving triage data: {e}")
            return False
            
    def load_triage_data(self, file_path: str) -> bool:
        """
        Load triage data from file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load agents
            self.available_agents = data.get('agents', self.available_agents)
            
            # Load items
            for item_id, item_data in data.get('items', {}).items():
                item = TriageItem(
                    item_id=item_id,
                    title=item_data['title'],
                    description=item_data['description'],
                    issue_type=IssueType(item_data['issue_type']),
                    priority=PriorityLevel(item_data['priority']),
                    status=TriageStatus(item_data['status']),
                    source=item_data['source'],
                    reporter=item_data['reporter'],
                    assigned_to=item_data['assigned_to'],
                    created_at=datetime.fromisoformat(item_data['created_at']),
                    updated_at=datetime.fromisoformat(item_data['updated_at']),
                    due_date=datetime.fromisoformat(item_data['due_date']) if item_data['due_date'] else None,
                    wsp_references=item_data['wsp_references'],
                    tags=item_data['tags'],
                    metadata=item_data['metadata']
                )
                self.triage_items[item_id] = item
            
            return True
            
        except Exception as e:
            print(f"Error loading triage data: {e}")
            return False


def create_triage_agent() -> TriageAgent:
    """
    Factory function to create a triage agent.
        
    Returns:
        TriageAgent instance
    """
    return TriageAgent()


if __name__ == "__main__":
    """Test the triage agent with sample data."""
    # Create triage agent
    agent = create_triage_agent()
    
    # Triage various items
    result1 = agent.triage_item(
        title="WSP 22 Violation - Missing ModLog.md",
        description="Module test_module is missing ModLog.md file",
        issue_type=IssueType.WSP_VIOLATION,
        source="compliance_checker",
        reporter="0102_agent",
        wsp_references=["WSP 22"]
    )
    
    result2 = agent.triage_item(
        title="Security Issue - Unauthorized Access",
        description="Detected unauthorized access attempt to admin panel",
        issue_type=IssueType.SECURITY_ISSUE,
        source="security_monitor",
        reporter="security_agent"
    )
    
    result3 = agent.triage_item(
        title="Feature Request - Add New API Endpoint",
        description="User requests new API endpoint for user management",
        issue_type=IssueType.FEATURE_REQUEST,
        source="user_feedback",
        reporter="user_123"
    )
    
    print("Triage Results:")
    print(f"Item 1: {result1.priority.name} - {result1.assigned_agent}")
    print(f"Item 2: {result2.priority.name} - {result2.assigned_agent}")
    print(f"Item 3: {result3.priority.name} - {result3.assigned_agent}")
    
    # Get statistics
    stats = agent.get_triage_stats()
    print(f"\nTriage Statistics:")
    print(f"Total items: {stats.total_items}")
    print(f"WSP violations: {stats.wsp_violations}")
    print(f"Items by priority: {stats.items_by_priority}")
    print(f"Items by status: {stats.items_by_status}")
    
    # Save triage data
    agent.save_triage_data("triage_data.json") 