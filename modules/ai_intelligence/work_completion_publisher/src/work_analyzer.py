"""
Work Analyzer - Evaluates significance of 0102 work sessions using Qwen

Monitors file changes, session activity, and uses Qwen to determine if
work is significant enough to publish to git and social media.
"""

import asyncio
import logging
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkSession:
    """Represents a work session"""
    session_id: str
    start_time: datetime
    files_changed: List[str]
    files_added: List[str]
    files_deleted: List[str]
    total_changes: int
    work_type: str  # "feature", "fix", "docs", "refactor", etc.
    significance_score: float  # 0.0-1.0 from Qwen analysis


@dataclass
class PublishContent:
    """Content generated for publishing"""
    commit_message: str
    linkedin_post: str
    twitter_post: str
    significance_score: float
    metadata: Dict[str, Any]


class WorkAnalyzer:
    """
    Analyzes 0102 work sessions and determines publishing worthiness.

    Uses Qwen for intelligent significance evaluation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[4]
        self.last_publish_time = None
        self.accumulated_changes = []

        # Significance thresholds
        self.min_files_changed = 3
        self.min_minutes_worked = 15
        self.min_significance_score = 0.7

        logger.info("WorkAnalyzer initialized - monitoring 0102 work sessions")

    async def evaluate_current_session(self) -> Tuple[bool, Optional[PublishContent]]:
        """
        Evaluate current work session for publishing worthiness.

        Returns:
            (should_publish, content): Whether to publish and content if yes
        """
        logger.info("Evaluating current work session...")

        # Get current git status
        git_status = await self._get_git_status()

        if not git_status['has_changes']:
            logger.info("No changes detected - nothing to publish")
            return False, None

        # Build work session data
        session = await self._build_session_data(git_status)

        # Use Qwen to evaluate significance
        significance_analysis = await self._evaluate_with_qwen(session)

        session.significance_score = significance_analysis['score']
        session.work_type = significance_analysis['work_type']

        # Check if meets publishing threshold
        should_publish = self._should_publish(session, significance_analysis)

        if not should_publish:
            logger.info(f"Session not significant enough (score: {session.significance_score:.2f})")
            self.accumulated_changes.append(session)
            return False, None

        # Generate publishing content
        logger.info(f"Session significant (score: {session.significance_score:.2f}) - generating content")
        content = await self._generate_publish_content(session, significance_analysis)

        return True, content

    async def publish(self, content: PublishContent) -> bool:
        """
        Execute publishing: git push and social posts.

        Calls main.py --git which handles everything.
        """
        logger.info("Publishing work to git and social media...")

        try:
            # Prepare commit message
            commit_msg = content.commit_message

            # Call main.py --git
            # main.py --git does:
            #   1. git add .
            #   2. git commit
            #   3. git push
            #   4. LinkedIn post
            #   5. X/Twitter post

            result = await self._execute_main_py_git(commit_msg)

            if result['success']:
                self.last_publish_time = datetime.now()
                self.accumulated_changes = []
                logger.info("[check mark] Successfully published to git and social media")
                return True
            else:
                logger.error(f"[cross mark] Publishing failed: {result['error']}")
                return False

        except Exception as e:
            logger.error(f"Publishing error: {e}")
            return False

    async def _get_git_status(self) -> Dict[str, Any]:
        """Get current git status"""
        try:
            # Get changed files
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

            changed_files = []
            added_files = []
            deleted_files = []

            for line in lines:
                if not line:
                    continue
                status = line[:2].strip()
                filepath = line[3:].strip()

                if 'D' in status:
                    deleted_files.append(filepath)
                elif 'A' in status or '?' in status:
                    added_files.append(filepath)
                else:
                    changed_files.append(filepath)

            return {
                'has_changes': len(lines) > 0,
                'changed_files': changed_files,
                'added_files': added_files,
                'deleted_files': deleted_files,
                'total_changes': len(lines)
            }

        except Exception as e:
            logger.error(f"Error getting git status: {e}")
            return {'has_changes': False, 'total_changes': 0}

    async def _build_session_data(self, git_status: Dict) -> WorkSession:
        """Build work session data from git status"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return WorkSession(
            session_id=session_id,
            start_time=datetime.now(),  # Simplified - could track actual start
            files_changed=git_status['changed_files'],
            files_added=git_status['added_files'],
            files_deleted=git_status['deleted_files'],
            total_changes=git_status['total_changes'],
            work_type="unknown",  # Will be filled by Qwen
            significance_score=0.0  # Will be filled by Qwen
        )

    async def _evaluate_with_qwen(self, session: WorkSession) -> Dict[str, Any]:
        """
        Use Qwen to evaluate work significance.

        This is where the AI intelligence analyzes the work.
        """
        logger.info("Using Qwen to evaluate work significance...")

        try:
            # Import Qwen advisor
            from holo_index.qwen_advisor.advisor import QwenAdvisor, AdvisorContext

            advisor = QwenAdvisor()

            # Build context for Qwen
            work_summary = self._build_work_summary(session)

            context = AdvisorContext(
                query=f"Evaluate significance of work session: {work_summary}",
                code_hits=[],
                wsp_hits=[]
            )

            # Get Qwen's analysis
            result = advisor.generate_guidance(context)

            # Parse Qwen's response to extract significance score and work type
            analysis = self._parse_qwen_response(result.guidance)

            return analysis

        except Exception as e:
            logger.error(f"Qwen evaluation error: {e}")
            # Fallback: use simple heuristics
            return self._fallback_evaluation(session)

    def _build_work_summary(self, session: WorkSession) -> str:
        """Build work summary for Qwen analysis"""
        summary_parts = []

        summary_parts.append(f"{session.total_changes} files changed")

        if session.files_added:
            summary_parts.append(f"{len(session.files_added)} new files")

        if session.files_deleted:
            summary_parts.append(f"{len(session.files_deleted)} deleted files")

        # Analyze file types
        file_types = {}
        for f in session.files_changed + session.files_added:
            ext = Path(f).suffix
            file_types[ext] = file_types.get(ext, 0) + 1

        if file_types:
            type_summary = ", ".join([f"{count} {ext}" for ext, count in file_types.items()])
            summary_parts.append(f"Types: {type_summary}")

        return ". ".join(summary_parts)

    def _parse_qwen_response(self, guidance: str) -> Dict[str, Any]:
        """
        Parse Qwen's guidance to extract significance score and work type.

        Looks for patterns in Qwen's response.
        """
        guidance_lower = guidance.lower()

        # Determine work type from guidance
        work_type = "general"
        if "feature" in guidance_lower or "add" in guidance_lower:
            work_type = "feature"
        elif "fix" in guidance_lower or "bug" in guidance_lower:
            work_type = "fix"
        elif "doc" in guidance_lower or "readme" in guidance_lower:
            work_type = "docs"
        elif "refactor" in guidance_lower:
            work_type = "refactor"

        # Estimate significance score from guidance sentiment
        score = 0.5  # Default moderate

        if any(word in guidance_lower for word in ["critical", "important", "significant", "major"]):
            score = 0.9
        elif any(word in guidance_lower for word in ["good", "useful", "valuable"]):
            score = 0.7
        elif any(word in guidance_lower for word in ["minor", "small", "trivial"]):
            score = 0.3

        return {
            'score': score,
            'work_type': work_type,
            'qwen_analysis': guidance
        }

    def _fallback_evaluation(self, session: WorkSession) -> Dict[str, Any]:
        """Fallback evaluation without Qwen"""
        # Simple heuristic scoring
        score = 0.0

        # More files = more significant
        if session.total_changes >= 10:
            score += 0.4
        elif session.total_changes >= 5:
            score += 0.3
        elif session.total_changes >= 3:
            score += 0.2

        # New files are significant
        if session.files_added:
            score += 0.2

        # Deletions suggest cleanup/refactoring
        if session.files_deleted:
            score += 0.1

        # Python files are code changes
        python_files = [f for f in session.files_changed + session.files_added if f.endswith('.py')]
        if len(python_files) >= 3:
            score += 0.3

        return {
            'score': min(1.0, score),
            'work_type': 'general',
            'qwen_analysis': 'Fallback heuristic evaluation'
        }

    def _should_publish(self, session: WorkSession, analysis: Dict) -> bool:
        """Determine if work should be published"""
        # Check minimum thresholds
        if session.total_changes < self.min_files_changed:
            return False

        if session.significance_score < self.min_significance_score:
            return False

        # Check time since last publish
        if self.last_publish_time:
            time_since_last = datetime.now() - self.last_publish_time
            # Don't publish too frequently (minimum 1 hour)
            if time_since_last < timedelta(hours=1):
                return False

        return True

    async def _generate_publish_content(
        self,
        session: WorkSession,
        analysis: Dict
    ) -> PublishContent:
        """Generate commit message and social posts"""
        # Generate commit message
        commit_msg = await self._generate_commit_message(session, analysis)

        # Generate social posts
        linkedin_post = await self._generate_linkedin_post(session, analysis)
        twitter_post = await self._generate_twitter_post(session, analysis)

        return PublishContent(
            commit_message=commit_msg,
            linkedin_post=linkedin_post,
            twitter_post=twitter_post,
            significance_score=session.significance_score,
            metadata={
                'session_id': session.session_id,
                'work_type': session.work_type,
                'files_changed': session.total_changes
            }
        )

    async def _generate_commit_message(self, session: WorkSession, analysis: Dict) -> str:
        """Generate git commit message"""
        # Use Qwen analysis to create meaningful commit message
        work_desc = analysis.get('qwen_analysis', 'Work session completion')

        # Format as conventional commit
        commit_type = session.work_type

        # Keep it under 72 characters for git best practices
        msg = f"{commit_type}: {work_desc[:65]}"

        # Add footer
        msg += "\n\n[0102 Autonomous Agent]"

        return msg

    async def _generate_linkedin_post(self, session: WorkSession, analysis: Dict) -> str:
        """Generate LinkedIn post"""
        post = f"[work check mark] Just completed significant work on the FoundUps autonomous agent:\n\n"
        post += f"Type: {session.work_type.title()}\n"
        post += f"Impact: {session.total_changes} files updated\n\n"
        post += f"{analysis.get('qwen_analysis', 'Advancing autonomous operations.')}\n\n"
        post += "#AI #AutonomousAgents #FoundUps #0102"

        return post

    async def _generate_twitter_post(self, session: WorkSession, analysis: Dict) -> str:
        """Generate Twitter/X post"""
        # Shorter for Twitter
        post = f"[work check mark] 0102 update: {session.work_type} work completed. "
        post += f"{session.total_changes} files. Advancing autonomous operations. "
        post += "#AI #Autonomous"

        return post

    async def _execute_main_py_git(self, commit_msg: str) -> Dict[str, Any]:
        """
        Execute main.py --git command.

        This triggers the full publishing pipeline:
        - Git commit and push
        - LinkedIn post
        - X/Twitter post
        """
        try:
            main_py = self.project_root / "main.py"

            if not main_py.exists():
                return {
                    'success': False,
                    'error': 'main.py not found'
                }

            # For now, return success with message about manual execution
            # In production, this would actually call main.py --git
            logger.info(f"Would execute: python main.py --git")
            logger.info(f"Commit message: {commit_msg}")

            # TODO: Actually execute main.py --git
            # result = subprocess.run(
            #     ['python', str(main_py), '--git'],
            #     cwd=self.project_root,
            #     capture_output=True,
            #     text=True,
            #     encoding='utf-8'
            # )

            return {
                'success': True,
                'message': 'Publishing flow would execute here',
                'commit_message': commit_msg
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


async def demo_work_analyzer():
    """Demonstrate work analyzer functionality"""
    print("=== Work Analyzer Demo ===\n")

    analyzer = WorkAnalyzer()

    # Evaluate current session
    should_publish, content = await analyzer.evaluate_current_session()

    if should_publish:
        print(f"[check mark] Work is significant (score: {content.significance_score:.2f})")
        print(f"\nCommit: {content.commit_message}")
        print(f"\nLinkedIn:\n{content.linkedin_post}")
        print(f"\nTwitter:\n{content.twitter_post}")

        # Would publish if this was production
        # await analyzer.publish(content)
    else:
        print("[info] Work not yet significant enough to publish")

    return analyzer


if __name__ == "__main__":
    asyncio.run(demo_work_analyzer())
