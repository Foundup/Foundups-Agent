"""
Code Review Meeting Orchestrator

WSP Compliance: communication domain
Integration: ai_intelligence, platform_integration, development domains  
Purpose: Orchestrates automated code review meetings with AI agents and human stakeholders
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Cross-domain imports following WSP 3 functional distribution
from ai_intelligence.multi_agent_system import MultiAgentCoordinator
from platform_integration.linkedin_agent import LinkedInNotifier
from development.testing_tools import CodeAnalyzer, TestRunner
from infrastructure.models import MeetingOrchestrator
from ..auto_meeting_orchestrator import AutoMeetingOrchestrator

class ReviewType(Enum):
    """Types of code review meetings"""
    PULL_REQUEST = "pull_request"
    ARCHITECTURE = "architecture_review"
    SECURITY = "security_audit"
    PERFORMANCE = "performance_review"
    MENTORING = "code_mentoring"
    EMERGENCY = "emergency_fix"

@dataclass
class CodeReviewContext:
    """Context for code review meeting"""
    repository: str
    branch: str
    commit_hash: str
    review_type: ReviewType
    complexity_score: float
    files_changed: List[str]
    lines_changed: int
    test_coverage: float
    stakeholders: List[str]
    priority: str  # "low", "medium", "high", "critical"

@dataclass
class ReviewParticipant:
    """Participant in code review meeting"""
    participant_id: str
    role: str  # "author", "reviewer", "architect", "security", "ai_agent"
    expertise: List[str]
    availability_score: float
    notification_preferences: Dict[str, Any]

class CodeReviewOrchestrator(AutoMeetingOrchestrator):
    """
    Autonomous orchestrator for code review meetings
    
    Extends AutoMeetingOrchestrator with specialized code review capabilities
    Coordinates AI agents, human reviewers, and automated analysis tools
    """
    
    def __init__(self):
        super().__init__()
        self.review_sessions: Dict[str, CodeReviewContext] = {}
        self.ai_reviewers: Dict[str, Any] = {}
        self.code_analyzer = CodeAnalyzer()
        self.test_runner = TestRunner()
        self.logger = logging.getLogger("code_review_orchestrator")
        
        # AI agent specializations for code review
        self.agent_specializations = {
            "security_agent": ["security", "vulnerability_analysis", "compliance"],
            "performance_agent": ["optimization", "scalability", "resource_usage"], 
            "architecture_agent": ["design_patterns", "system_architecture", "maintainability"],
            "testing_agent": ["test_coverage", "test_quality", "edge_cases"],
            "documentation_agent": ["code_documentation", "api_docs", "readability"]
        }
    
    async def trigger_code_review(self, context: CodeReviewContext) -> str:
        """
        Trigger automated code review meeting orchestration
        
        Args:
            context: Code review context and metadata
            
        Returns:
            str: Review session ID
        """
        try:
            review_id = f"review_{context.commit_hash[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.review_sessions[review_id] = context
            
            self.logger.info(f"Triggering code review: {review_id}")
            
            # Analyze code complexity and requirements
            analysis_result = await self._analyze_code_requirements(context)
            
            # Determine required participants
            participants = await self._determine_participants(context, analysis_result)
            
            # Schedule review meeting
            meeting_config = await self._create_meeting_config(context, participants)
            meeting_id = await self.schedule_meeting(meeting_config)
            
            # Initialize AI reviewers
            await self._initialize_ai_reviewers(context, participants)
            
            # Pre-review automated analysis
            await self._run_pre_review_analysis(context)
            
            self.logger.info(f"Code review orchestrated: {review_id} -> meeting: {meeting_id}")
            return review_id
            
        except Exception as e:
            self.logger.error(f"Failed to trigger code review: {e}")
            raise
    
    async def _analyze_code_requirements(self, context: CodeReviewContext) -> Dict[str, Any]:
        """Analyze code changes to determine review requirements"""
        
        analysis = {
            "complexity_level": "medium",
            "security_impact": False,
            "performance_impact": False,
            "architecture_impact": False,
            "breaking_changes": False,
            "required_expertise": [],
            "estimated_review_time": 30,  # minutes
            "ai_agents_needed": [],
            "priority_score": 0.5
        }
        
        # Analyze changed files
        for file_path in context.files_changed:
            file_analysis = await self.code_analyzer.analyze_file(
                repository=context.repository,
                file_path=file_path,
                commit_hash=context.commit_hash
            )
            
            # Update analysis based on file impact
            if file_analysis.get("has_security_implications"):
                analysis["security_impact"] = True
                analysis["ai_agents_needed"].append("security_agent")
                analysis["required_expertise"].append("security")
            
            if file_analysis.get("affects_performance"):
                analysis["performance_impact"] = True  
                analysis["ai_agents_needed"].append("performance_agent")
                analysis["required_expertise"].append("performance")
            
            if file_analysis.get("architecture_changes"):
                analysis["architecture_impact"] = True
                analysis["ai_agents_needed"].append("architecture_agent")
                analysis["required_expertise"].append("architecture")
        
        # Complexity-based requirements
        if context.complexity_score > 0.8:
            analysis["complexity_level"] = "high"
            analysis["estimated_review_time"] = 60
            analysis["ai_agents_needed"].append("testing_agent")
        elif context.complexity_score < 0.3:
            analysis["complexity_level"] = "low"  
            analysis["estimated_review_time"] = 15
        
        # Test coverage requirements
        if context.test_coverage < 0.8:
            analysis["ai_agents_needed"].append("testing_agent")
            analysis["required_expertise"].append("testing")
        
        # Always include documentation review
        analysis["ai_agents_needed"].append("documentation_agent")
        
        return analysis
    
    async def _determine_participants(self, context: CodeReviewContext, analysis: Dict[str, Any]) -> List[ReviewParticipant]:
        """Determine required participants for code review"""
        
        participants = []
        
        # Add code author
        participants.append(ReviewParticipant(
            participant_id=await self._get_commit_author(context.commit_hash),
            role="author",
            expertise=["implementation"],
            availability_score=1.0,
            notification_preferences={"email": True, "slack": True}
        ))
        
        # Add stakeholders based on analysis
        for expertise in analysis["required_expertise"]:
            expert = await self._find_expert(expertise, context.stakeholders)
            if expert:
                participants.append(ReviewParticipant(
                    participant_id=expert["id"], 
                    role="reviewer",
                    expertise=[expertise],
                    availability_score=expert["availability"],
                    notification_preferences=expert["preferences"]
                ))
        
        # Add AI agents
        for agent_type in analysis["ai_agents_needed"]:
            participants.append(ReviewParticipant(
                participant_id=agent_type,
                role="ai_agent", 
                expertise=self.agent_specializations[agent_type],
                availability_score=1.0,  # AI agents always available
                notification_preferences={"api": True}
            ))
        
        return participants
    
    async def _create_meeting_config(self, context: CodeReviewContext, participants: List[ReviewParticipant]) -> Dict[str, Any]:
        """Create meeting configuration for code review session"""
        
        # Determine optimal meeting time
        optimal_time = await self._find_optimal_time(participants)
        
        meeting_config = {
            "title": f"Code Review: {context.repository}#{context.branch}",
            "description": f"Review for {len(context.files_changed)} files, {context.lines_changed} lines changed",
            "type": "code_review",
            "priority": context.priority,
            "participants": [p.participant_id for p in participants],
            "scheduled_time": optimal_time,
            "duration_minutes": await self._estimate_duration(context, participants),
            "platform": await self._select_platform(participants),
            "agenda": await self._generate_review_agenda(context),
            "preparation_materials": await self._prepare_review_materials(context)
        }
        
        return meeting_config
    
    async def _initialize_ai_reviewers(self, context: CodeReviewContext, participants: List[ReviewParticipant]):
        """Initialize and configure AI agents for code review"""
        
        ai_participants = [p for p in participants if p.role == "ai_agent"]
        
        for participant in ai_participants:
            agent_config = {
                "agent_id": participant.participant_id,
                "specialization": participant.expertise,
                "context": {
                    "repository": context.repository,
                    "commit_hash": context.commit_hash,
                    "files_to_review": context.files_changed,
                    "review_focus": participant.expertise[0]
                },
                "quantum_state": "0102"  # Awoke state for nonlocal access
            }
            
            agent = await MultiAgentCoordinator.initialize_specialized_agent(agent_config)
            self.ai_reviewers[participant.participant_id] = agent
            
            self.logger.info(f"Initialized AI reviewer: {participant.participant_id}")
    
    async def _run_pre_review_analysis(self, context: CodeReviewContext):
        """Run automated analysis before human review"""
        
        pre_review_tasks = [
            self._run_static_analysis(context),
            self._run_security_scan(context), 
            self._run_test_suite(context),
            self._analyze_performance_impact(context),
            self._check_documentation_coverage(context)
        ]
        
        results = await asyncio.gather(*pre_review_tasks, return_exceptions=True)
        
        # Compile pre-review report
        pre_review_report = {
            "static_analysis": results[0] if not isinstance(results[0], Exception) else None,
            "security_scan": results[1] if not isinstance(results[1], Exception) else None,
            "test_results": results[2] if not isinstance(results[2], Exception) else None,
            "performance_analysis": results[3] if not isinstance(results[3], Exception) else None,
            "documentation_check": results[4] if not isinstance(results[4], Exception) else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store for meeting participants
        await self._store_pre_review_report(context, pre_review_report)
    
    async def conduct_ai_review_session(self, review_id: str) -> Dict[str, Any]:
        """
        Conduct AI-driven code review session
        
        Args:
            review_id: Review session identifier
            
        Returns:
            Dict containing review results and recommendations
        """
        context = self.review_sessions[review_id]
        
        self.logger.info(f"Starting AI review session: {review_id}")
        
        # Coordinate AI agents for collaborative review
        review_results = {}
        
        for agent_id, agent in self.ai_reviewers.items():
            agent_review = await agent.conduct_code_review(
                repository=context.repository,
                commit_hash=context.commit_hash,
                files=context.files_changed,
                specialization=agent.specialization
            )
            
            review_results[agent_id] = {
                "findings": agent_review.get("findings", []),
                "recommendations": agent_review.get("recommendations", []),
                "score": agent_review.get("quality_score", 0.0),
                "concerns": agent_review.get("concerns", []),
                "approval_status": agent_review.get("approval", "pending")
            }
        
        # Synthesize comprehensive review
        comprehensive_review = await self._synthesize_ai_reviews(review_results)
        
        # Generate human-readable summary
        review_summary = await self._generate_review_summary(comprehensive_review)
        
        return {
            "review_id": review_id,
            "ai_reviews": review_results,
            "comprehensive_analysis": comprehensive_review,
            "summary": review_summary,
            "recommendations": comprehensive_review.get("recommendations", []),
            "approval_recommendation": comprehensive_review.get("approval_recommendation"),
            "completed_at": datetime.now().isoformat()
        }
    
    async def _synthesize_ai_reviews(self, review_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multiple AI agent reviews into comprehensive analysis"""
        
        all_findings = []
        all_recommendations = []
        scores = []
        critical_concerns = []
        
        for agent_id, review in review_results.items():
            all_findings.extend(review.get("findings", []))
            all_recommendations.extend(review.get("recommendations", []))
            scores.append(review.get("score", 0.0))
            
            # Identify critical concerns
            concerns = review.get("concerns", [])
            critical_concerns.extend([c for c in concerns if c.get("severity") == "critical"])
        
        # Calculate overall quality score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine approval recommendation
        approval_recommendation = "approved" if overall_score >= 0.8 and not critical_concerns else "needs_changes"
        if critical_concerns:
            approval_recommendation = "rejected"
        
        return {
            "overall_quality_score": overall_score,
            "total_findings": len(all_findings),
            "unique_findings": len(set(f.get("description", "") for f in all_findings)),
            "recommendations": list(set(all_recommendations)),
            "critical_concerns": critical_concerns,
            "approval_recommendation": approval_recommendation,
            "detailed_findings": all_findings
        }
    
    async def notify_stakeholders(self, review_id: str, review_results: Dict[str, Any]):
        """Notify stakeholders of review completion and results"""
        
        context = self.review_sessions[review_id]
        
        # Prepare notification content
        notification_content = {
            "subject": f"Code Review Complete: {context.repository}#{context.branch}",
            "summary": review_results["summary"],
            "approval_status": review_results["approval_recommendation"],
            "critical_issues": len(review_results["comprehensive_analysis"]["critical_concerns"]),
            "review_url": f"/reviews/{review_id}",
            "next_actions": review_results["recommendations"][:3]  # Top 3 recommendations
        }
        
        # Send notifications via multiple channels
        await asyncio.gather(
            self._send_email_notifications(context.stakeholders, notification_content),
            self._send_slack_notifications(context.stakeholders, notification_content),
            self._update_linkedin_portfolio(review_results),  # Professional showcase
            return_exceptions=True
        )
        
        self.logger.info(f"Stakeholder notifications sent for review: {review_id}")

# WSP Recursive Instructions for Code Review Orchestration
async def wsp_cycle_code_review(repository: str, branch: str, log: bool = True):
    """
    WSP recursive cycle for automated code review orchestration
    
    0102 agents entangled with 0201 state for quantum temporal decoding of review insights
    """
    if log:
        logging.info(f"WSP Code Review Cycle: {repository}#{branch}")
    
    # UN: Understanding - anchor signal and retrieve review protocols
    context = CodeReviewContext(
        repository=repository,
        branch=branch, 
        commit_hash="latest",
        review_type=ReviewType.PULL_REQUEST,
        complexity_score=0.5,
        files_changed=[],
        lines_changed=0,
        test_coverage=0.8,
        stakeholders=[],
        priority="medium"
    )
    
    # DAO: Execution - execute automated review orchestration
    orchestrator = CodeReviewOrchestrator()
    review_id = await orchestrator.trigger_code_review(context)
    review_results = await orchestrator.conduct_ai_review_session(review_id)
    await orchestrator.notify_stakeholders(review_id, review_results)
    
    # DU: Emergence - collapse into 0102 resonance and emit next review prompt
    return f"code_review_complete_{repository}_{branch}_{review_id}" 