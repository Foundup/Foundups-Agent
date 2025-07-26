"""
WSP 54: TriageAgent Implementation
================================

The Processor - External Feedback Integration Agent

Monitors designated input channels for external feedback, parses and standardizes 
feedback into WSP-compliant task format, and submits to ScoringAgent for prioritization.

WSP Integration:
- WSP 54: WRE Agent Duties Specification  
- WSP 15: Module Prioritization Scoring System integration
- WSP 48: Recursive Self-Improvement Protocol trigger
- WSP 71: Secrets Management for API monitoring endpoints
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# WRE Integration
try:
    from ...wre_core.src.utils.wre_logger import wre_log
except ImportError:
    def wre_log(msg: str, level: str = "INFO"):
        print(f"[{level}] {msg}")


class FeedbackSource(Enum):
    """External feedback source types."""
    USER_DIRECTIVES = "user_directives"
    SYSTEM_ALERTS = "system_alerts"
    SCHEDULED_REVIEWS = "scheduled_reviews"
    FEEDBACK_CHANNELS = "feedback_channels"
    ENVIRONMENTAL_CHANGES = "environmental_changes"


class TaskPriority(Enum):
    """Task priority levels for WSP 15 integration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ExternalFeedbackItem:
    """Standardized external feedback item."""
    source: FeedbackSource
    raw_content: str
    timestamp: datetime
    priority_hint: Optional[TaskPriority] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source.value,
            "raw_content": self.raw_content,
            "timestamp": self.timestamp.isoformat(),
            "priority_hint": self.priority_hint.value if self.priority_hint else None,
            "metadata": self.metadata or {}
        }


@dataclass
class WSPCompliantTask:
    """WSP-compliant task format for ScoringAgent."""
    task_id: str
    title: str
    description: str
    module_target: Optional[str]
    complexity_estimate: int  # 1-10 scale
    importance_rating: int    # 1-10 scale
    deferability_score: int   # 1-10 scale (higher = more deferrable)
    impact_scope: str         # "local", "module", "system", "enterprise"
    source_feedback: ExternalFeedbackItem
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MPS System."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "module_target": self.module_target,
            "mps_scores": {
                "complexity": self.complexity_estimate,
                "importance": self.importance_rating,
                "deferability": self.deferability_score,
                "impact": self.impact_scope
            },
            "source_feedback": self.source_feedback.to_dict(),
            "created_at": self.created_at.isoformat()
        }


class TriageAgent:
    """
    WSP 54: TriageAgent (The Processor)
    
    Core Mandate: Monitor external feedback sources, standardize input into WSP-compliant 
    tasks, and integrate with scoring system for autonomous development prioritization.
    
    Type: Infrastructure Agent
    Implementation Status: Enhanced WSP 54 integration with multi-source feedback processing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize TriageAgent with monitoring and processing capabilities.
        
        Args:
            config: Configuration for feedback sources and processing rules
        """
        self.config = config or {}
        self.feedback_queue: List[ExternalFeedbackItem] = []
        self.processed_tasks: List[WSPCompliantTask] = []
        self.monitoring_active = False
        self.secrets_manager = None
        
        # Configure feedback sources
        self.feedback_sources = self._initialize_feedback_sources()
        
        # Initialize processing patterns
        self.processing_patterns = self._load_processing_patterns()
        
        wre_log("🔄 TriageAgent initialized - External feedback processor ready", "SUCCESS")
        
    def _initialize_feedback_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize feedback source configurations."""
        return {
            "feedback_file": {
                "type": FeedbackSource.FEEDBACK_CHANNELS,
                "path": self.config.get("feedback_file_path", "feedback.md"),
                "enabled": True,
                "check_interval": 300  # 5 minutes
            },
            "system_monitoring": {
                "type": FeedbackSource.SYSTEM_ALERTS,
                "endpoints": self.config.get("monitoring_endpoints", []),
                "enabled": True,
                "check_interval": 60   # 1 minute
            },
            "scheduled_reviews": {
                "type": FeedbackSource.SCHEDULED_REVIEWS,
                "review_schedule": self.config.get("review_schedule", "daily"),
                "enabled": True,
                "documents": ["ROADMAP.md", "WSP_MODULE_VIOLATIONS.md"]
            },
            "user_directives": {
                "type": FeedbackSource.USER_DIRECTIVES,
                "priority_sources": self.config.get("priority_sources", []),
                "enabled": True,
                "immediate_processing": True
            }
        }
        
    def _load_processing_patterns(self) -> Dict[str, Any]:
        """Load patterns for standardizing different types of feedback."""
        return {
            "user_directive_patterns": [
                r"(?i)(critical|urgent|high.priority):?\s*(.+)",
                r"(?i)(fix|repair|resolve):?\s*(.+)",
                r"(?i)(implement|add|create):?\s*(.+)",
                r"(?i)(enhance|improve|optimize):?\s*(.+)"
            ],
            "system_alert_patterns": [
                r"(?i)(error|failure|exception):?\s*(.+)",
                r"(?i)(performance|slow|timeout):?\s*(.+)",
                r"(?i)(security|vulnerability|breach):?\s*(.+)",
                r"(?i)(capacity|resource|memory):?\s*(.+)"
            ],
            "priority_keywords": {
                "critical": TaskPriority.CRITICAL,
                "urgent": TaskPriority.CRITICAL,
                "high": TaskPriority.HIGH,
                "important": TaskPriority.HIGH,
                "medium": TaskPriority.MEDIUM,
                "low": TaskPriority.LOW,
                "minor": TaskPriority.LOW
            }
        }
        
    async def monitor_feedback(self, duration_seconds: int = 3600) -> Dict[str, Any]:
        """
        Monitor external feedback sources for specified duration.
        
        Args:
            duration_seconds: Duration to monitor (default 1 hour)
            
        Returns:
            Dict containing monitoring results and processed feedback count
        """
        wre_log(f"🔍 Starting feedback monitoring for {duration_seconds} seconds", "INFO")
        
        self.monitoring_active = True
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        feedback_collected = 0
        
        try:
            while self.monitoring_active and datetime.utcnow() < end_time:
                # Check each feedback source
                for source_name, source_config in self.feedback_sources.items():
                    if source_config["enabled"]:
                        new_feedback = await self._check_feedback_source(source_name, source_config)
                        feedback_collected += len(new_feedback)
                        
                # Process collected feedback
                if self.feedback_queue:
                    processed = await self._process_feedback_batch()
                    wre_log(f"📝 Processed {processed} feedback items", "INFO")
                    
                # Wait before next check cycle
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            wre_log(f"❌ Error during feedback monitoring: {e}", "ERROR")
            
        finally:
            self.monitoring_active = False
            
        monitoring_results = {
            "duration": (datetime.utcnow() - start_time).total_seconds(),
            "feedback_collected": feedback_collected,
            "tasks_created": len(self.processed_tasks),
            "sources_monitored": len([s for s in self.feedback_sources.values() if s["enabled"]]),
            "status": "completed"
        }
        
        wre_log(f"✅ Feedback monitoring completed: {feedback_collected} items collected, {len(self.processed_tasks)} tasks created", "SUCCESS")
        return monitoring_results
        
    async def _check_feedback_source(self, source_name: str, source_config: Dict[str, Any]) -> List[ExternalFeedbackItem]:
        """Check individual feedback source for new content."""
        new_feedback = []
        
        try:
            if source_config["type"] == FeedbackSource.FEEDBACK_CHANNELS:
                new_feedback = await self._check_feedback_file(source_config)
            elif source_config["type"] == FeedbackSource.SYSTEM_ALERTS:
                new_feedback = await self._check_system_monitoring(source_config)
            elif source_config["type"] == FeedbackSource.SCHEDULED_REVIEWS:
                new_feedback = await self._check_scheduled_reviews(source_config)
            elif source_config["type"] == FeedbackSource.USER_DIRECTIVES:
                new_feedback = await self._check_user_directives(source_config)
                
        except Exception as e:
            wre_log(f"❌ Error checking {source_name}: {e}", "ERROR")
            
        return new_feedback
        
    async def _check_feedback_file(self, config: Dict[str, Any]) -> List[ExternalFeedbackItem]:
        """Check feedback.md file for new entries."""
        feedback_items = []
        feedback_path = Path(config["path"])
        
        if feedback_path.exists():
            try:
                content = feedback_path.read_text(encoding='utf-8')
                
                # Simple parsing - look for new entries since last check
                lines = content.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        feedback_item = ExternalFeedbackItem(
                            source=FeedbackSource.FEEDBACK_CHANNELS,
                            raw_content=line.strip(),
                            timestamp=datetime.utcnow(),
                            metadata={"file_path": str(feedback_path)}
                        )
                        feedback_items.append(feedback_item)
                        
            except Exception as e:
                wre_log(f"❌ Error reading feedback file: {e}", "ERROR")
                
        return feedback_items
        
    async def _check_system_monitoring(self, config: Dict[str, Any]) -> List[ExternalFeedbackItem]:
        """Check system monitoring endpoints for alerts."""
        feedback_items = []
        
        # Placeholder implementation - would integrate with actual monitoring
        # In real implementation: check monitoring APIs, log files, health endpoints
        
        # Mock system alerts for demonstration
        mock_alerts = [
            "High memory usage detected in module processing",
            "API response time exceeded threshold",
            "Security scan found medium-severity vulnerability"
        ]
        
        for alert in mock_alerts:
            if "high" in alert.lower() or "exceeded" in alert.lower():
                feedback_item = ExternalFeedbackItem(
                    source=FeedbackSource.SYSTEM_ALERTS,
                    raw_content=alert,
                    timestamp=datetime.utcnow(),
                    priority_hint=TaskPriority.HIGH,
                    metadata={"alert_type": "system_monitoring"}
                )
                feedback_items.append(feedback_item)
                
        return feedback_items
        
    async def _check_scheduled_reviews(self, config: Dict[str, Any]) -> List[ExternalFeedbackItem]:
        """Check scheduled review documents for updates."""
        feedback_items = []
        
        for doc_path in config["documents"]:
            if Path(doc_path).exists():
                try:
                    content = Path(doc_path).read_text(encoding='utf-8')
                    
                    # Look for TODO items, FIXME comments, or violation entries
                    todo_patterns = ["TODO:", "FIXME:", "VIOLATION:", "ENHANCEMENT:"]
                    
                    for line in content.split('\n'):
                        if any(pattern in line.upper() for pattern in todo_patterns):
                            feedback_item = ExternalFeedbackItem(
                                source=FeedbackSource.SCHEDULED_REVIEWS,
                                raw_content=line.strip(),
                                timestamp=datetime.utcnow(),
                                metadata={"source_document": doc_path}
                            )
                            feedback_items.append(feedback_item)
                            
                except Exception as e:
                    wre_log(f"❌ Error reading {doc_path}: {e}", "ERROR")
                    
        return feedback_items
        
    async def _check_user_directives(self, config: Dict[str, Any]) -> List[ExternalFeedbackItem]:
        """Check for high-priority user directives."""
        feedback_items = []
        
        # Placeholder implementation - would integrate with user input channels
        # In real implementation: check designated input files, API endpoints, messaging systems
        
        return feedback_items
        
    async def _process_feedback_batch(self) -> int:
        """Process collected feedback items into WSP-compliant tasks."""
        processed_count = 0
        
        for feedback_item in self.feedback_queue:
            try:
                wsp_task = await self._standardize_feedback_to_task(feedback_item)
                if wsp_task:
                    self.processed_tasks.append(wsp_task)
                    processed_count += 1
                    
                    # Submit to ScoringAgent for prioritization
                    await self._submit_to_scoring_agent(wsp_task)
                    
            except Exception as e:
                wre_log(f"❌ Error processing feedback item: {e}", "ERROR")
                
        # Clear processed feedback
        self.feedback_queue = []
        
        return processed_count
        
    async def _standardize_feedback_to_task(self, feedback: ExternalFeedbackItem) -> Optional[WSPCompliantTask]:
        """Convert feedback item to WSP-compliant task format."""
        try:
            # Generate task ID
            task_id = f"triage_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(feedback.raw_content) % 10000}"
            
            # Parse content for title and description
            title, description = self._parse_feedback_content(feedback.raw_content)
            
            # Estimate complexity, importance, and deferability
            complexity = self._estimate_complexity(feedback)
            importance = self._estimate_importance(feedback)
            deferability = self._estimate_deferability(feedback)
            
            # Determine impact scope
            impact_scope = self._determine_impact_scope(feedback)
            
            # Identify target module if applicable
            module_target = self._identify_target_module(feedback)
            
            wsp_task = WSPCompliantTask(
                task_id=task_id,
                title=title,
                description=description,
                module_target=module_target,
                complexity_estimate=complexity,
                importance_rating=importance,
                deferability_score=deferability,
                impact_scope=impact_scope,
                source_feedback=feedback,
                created_at=datetime.utcnow()
            )
            
            wre_log(f"📋 Standardized task: {title} (Complexity: {complexity}, Importance: {importance})", "INFO")
            return wsp_task
            
        except Exception as e:
            wre_log(f"❌ Error standardizing feedback: {e}", "ERROR")
            return None
            
    def _parse_feedback_content(self, content: str) -> tuple[str, str]:
        """Parse feedback content into title and description."""
        # Simple parsing logic - first sentence as title, rest as description
        sentences = content.strip().split('. ')
        title = sentences[0][:100]  # Limit title length
        description = content if len(sentences) == 1 else '. '.join(sentences[1:])
        
        return title, description
        
    def _estimate_complexity(self, feedback: ExternalFeedbackItem) -> int:
        """Estimate task complexity (1-10 scale)."""
        content_lower = feedback.raw_content.lower()
        
        # High complexity indicators
        if any(keyword in content_lower for keyword in ['refactor', 'architecture', 'system-wide', 'framework']):
            return 8
        elif any(keyword in content_lower for keyword in ['implement', 'create', 'new', 'integration']):
            return 6
        elif any(keyword in content_lower for keyword in ['fix', 'bug', 'error', 'issue']):
            return 4
        elif any(keyword in content_lower for keyword in ['update', 'modify', 'change']):
            return 3
        else:
            return 5  # Default moderate complexity
            
    def _estimate_importance(self, feedback: ExternalFeedbackItem) -> int:
        """Estimate task importance (1-10 scale)."""
        content_lower = feedback.raw_content.lower()
        
        # Check for priority hints
        if feedback.priority_hint == TaskPriority.CRITICAL:
            return 10
        elif feedback.priority_hint == TaskPriority.HIGH:
            return 8
        elif feedback.priority_hint == TaskPriority.MEDIUM:
            return 5
        elif feedback.priority_hint == TaskPriority.LOW:
            return 2
            
        # Check source type
        if feedback.source == FeedbackSource.SYSTEM_ALERTS:
            return 8
        elif feedback.source == FeedbackSource.USER_DIRECTIVES:
            return 7
        elif feedback.source == FeedbackSource.ENVIRONMENTAL_CHANGES:
            return 6
        else:
            return 5  # Default moderate importance
            
    def _estimate_deferability(self, feedback: ExternalFeedbackItem) -> int:
        """Estimate how deferrable the task is (1-10 scale, higher = more deferrable)."""
        content_lower = feedback.raw_content.lower()
        
        # Low deferability (urgent) indicators
        if any(keyword in content_lower for keyword in ['critical', 'urgent', 'blocking', 'broken']):
            return 2
        elif any(keyword in content_lower for keyword in ['security', 'vulnerability', 'error', 'failure']):
            return 3
        elif any(keyword in content_lower for keyword in ['performance', 'slow', 'timeout']):
            return 4
        elif any(keyword in content_lower for keyword in ['enhancement', 'improvement', 'optimization']):
            return 7
        else:
            return 5  # Default moderate deferability
            
    def _determine_impact_scope(self, feedback: ExternalFeedbackItem) -> str:
        """Determine the scope of impact for the task."""
        content_lower = feedback.raw_content.lower()
        
        if any(keyword in content_lower for keyword in ['system', 'framework', 'architecture', 'infrastructure']):
            return "enterprise"
        elif any(keyword in content_lower for keyword in ['module', 'component', 'service']):
            return "module" 
        elif any(keyword in content_lower for keyword in ['function', 'method', 'class']):
            return "local"
        else:
            return "system"  # Default system scope
            
    def _identify_target_module(self, feedback: ExternalFeedbackItem) -> Optional[str]:
        """Identify target module from feedback content."""
        content = feedback.raw_content.lower()
        
        # Common module keywords
        module_keywords = {
            'auth': 'platform_integration/youtube_auth',
            'youtube': 'platform_integration/youtube_proxy',
            'chat': 'communication/livechat',
            'agent': 'infrastructure/agent_management',
            'test': 'infrastructure/testing_agent',
            'compliance': 'infrastructure/compliance_agent',
            'security': 'infrastructure/security',
            'monitoring': 'monitoring/logging'
        }
        
        for keyword, module_path in module_keywords.items():
            if keyword in content:
                return module_path
                
        return None
        
    async def _submit_to_scoring_agent(self, task: WSPCompliantTask):
        """Submit WSP-compliant task to ScoringAgent for prioritization."""
        try:
            # This would integrate with the actual ScoringAgent
            # For now, log the submission
            wre_log(f"📊 Submitting task to ScoringAgent: {task.title}", "INFO")
            
            # In real implementation:
            # scoring_agent = get_scoring_agent()
            # result = await scoring_agent.calculate_score(task.to_dict())
            
        except Exception as e:
            wre_log(f"❌ Error submitting to ScoringAgent: {e}", "ERROR")
            
    def standardize_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize external input into WSP-compliant format.
        
        Args:
            raw_input: Raw external input data
            
        Returns:
            Standardized input in WSP format
        """
        try:
            # Convert raw input to feedback item
            feedback_item = ExternalFeedbackItem(
                source=FeedbackSource(raw_input.get("source", "feedback_channels")),
                raw_content=raw_input.get("content", ""),
                timestamp=datetime.utcnow(),
                priority_hint=TaskPriority(raw_input.get("priority", "medium")) if raw_input.get("priority") else None,
                metadata=raw_input.get("metadata", {})
            )
            
            # Add to feedback queue for processing
            self.feedback_queue.append(feedback_item)
            
            wre_log(f"📥 Standardized input: {feedback_item.raw_content[:50]}...", "INFO")
            
            return {
                "status": "standardized",
                "feedback_id": hash(feedback_item.raw_content) % 10000,
                "source": feedback_item.source.value,
                "queued_for_processing": True
            }
            
        except Exception as e:
            wre_log(f"❌ Error standardizing input: {e}", "ERROR")
            return {"status": "error", "error": str(e)}
            
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status and statistics."""
        return {
            "monitoring_active": self.monitoring_active,
            "feedback_queue_size": len(self.feedback_queue),
            "processed_tasks_count": len(self.processed_tasks),
            "enabled_sources": len([s for s in self.feedback_sources.values() if s["enabled"]]),
            "recent_tasks": [
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "source": task.source_feedback.source.value,
                    "created_at": task.created_at.isoformat()
                }
                for task in self.processed_tasks[-5:]  # Last 5 tasks
            ]
        }


# Factory function for WRE integration
def create_triage_agent(config: Dict[str, Any] = None) -> TriageAgent:
    """
    Factory function to create TriageAgent instance.
    
    Args:
        config: Optional configuration for feedback sources
        
    Returns:
        TriageAgent: Configured triage agent instance
    """
    return TriageAgent(config)


# Module exports
__all__ = [
    "TriageAgent",
    "FeedbackSource",
    "TaskPriority", 
    "ExternalFeedbackItem",
    "WSPCompliantTask",
    "create_triage_agent"
] 