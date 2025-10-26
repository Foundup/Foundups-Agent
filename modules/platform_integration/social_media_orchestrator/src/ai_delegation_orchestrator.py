# -*- coding: utf-8 -*-
"""
AI Delegation Orchestrator
Provides fallback AI drafting when Qwen/Gemma is unavailable.

Uses external AI services (Claude, Grok, Gemini) for LinkedIn content drafting
while maintaining WSP compliance and Vision DAE telemetry.

WSP 77: Agent Coordination Protocol
WSP 84: Auto-Management (intelligent delegation)
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

from .ui_tars_scheduler import get_ui_tars_scheduler, ScheduledPost

logger = logging.getLogger(__name__)


class AIDelegationOrchestrator:
    """
    Orchestrates AI content drafting when local models are unavailable.

    Implements intelligent delegation pipeline:
    1. Check Qwen/Gemma availability
    2. Fallback to external AI services
    3. Vision DAE telemetry logging
    4. UI-TARS scheduling coordination
    """

    def __init__(self):
        self.ui_tars_scheduler = get_ui_tars_scheduler()
        self.skills_dir = Path("skills")  # Directory containing skills.md files
        self.delegation_history = Path("memory/ai_delegation_history.jsonl")

    async def draft_linkedin_content(self,
                                   trigger_event: Dict[str, Any],
                                   target_platform: str = "linkedin") -> Optional[Dict[str, Any]]:
        """
        Draft LinkedIn content using available AI services.

        Args:
            trigger_event: Event that triggered content creation
            target_platform: Target social media platform

        Returns:
            Draft result with content and metadata, or None if failed
        """
        try:
            # Check Qwen/Gemma availability first
            if await self._check_qwen_gemma_available():
                logger.info("Using Qwen/Gemma for content drafting")
                return await self._draft_with_qwen_gemma(trigger_event, target_platform)

            # Fallback to external AI services
            logger.info("Qwen/Gemma unavailable, using external AI delegation")
            return await self._draft_with_external_ai(trigger_event, target_platform)

        except Exception as e:
            logger.error(f"Content drafting failed: {e}")
            return None

    async def _check_qwen_gemma_available(self) -> bool:
        """
        Check if Qwen/Gemma models are available and responsive.

        Returns:
            bool: True if models are available for use
        """
        try:
            # Check for model files and running processes
            qwen_path = Path("E:/HoloIndex/models/qwen")
            gemma_path = Path("E:/HoloIndex/models/gemma")

            models_exist = qwen_path.exists() or gemma_path.exists()

            if not models_exist:
                logger.debug("Qwen/Gemma model files not found")
                return False

            # Could add process checking here if models run as services
            # For now, just check file existence and basic responsiveness

            # Quick test query to see if models respond
            test_result = await self._test_model_responsiveness()
            return test_result

        except Exception as e:
            logger.debug(f"Qwen/Gemma availability check failed: {e}")
            return False

    async def _test_model_responsiveness(self) -> bool:
        """Test if AI models are responsive (placeholder implementation)"""
        # This would need actual integration with the model serving infrastructure
        # For now, return False to force external AI delegation
        return False

    async def _draft_with_qwen_gemma(self,
                                    trigger_event: Dict[str, Any],
                                    target_platform: str) -> Dict[str, Any]:
        """
        Draft content using local Qwen/Gemma models.

        Args:
            trigger_event: Event triggering content creation
            target_platform: Target platform

        Returns:
            Draft result dictionary
        """
        # This would integrate with the actual Qwen/Gemma serving infrastructure
        # For now, this is a placeholder that would be implemented when models are available

        draft_hash = self._generate_draft_hash(trigger_event)

        return {
            'content': f"Generated content for {trigger_event.get('type', 'event')}",
            'draft_hash': draft_hash,
            'ai_service': 'qwen_gemma_local',
            'confidence': 0.9,
            'metadata': {
                'trigger_event': trigger_event,
                'target_platform': target_platform,
                'generated_at': datetime.now().isoformat()
            }
        }

    async def _draft_with_external_ai(self,
                                     trigger_event: Dict[str, Any],
                                     target_platform: str) -> Dict[str, Any]:
        """
        Draft content using external AI services as fallback.

        Args:
            trigger_event: Event triggering content creation
            target_platform: Target platform

        Returns:
            Draft result dictionary
        """
        try:
            # Load appropriate skills.md prompt
            skills_prompt = await self._load_skills_prompt(trigger_event)

            # Try external AI services in order of preference
            ai_services = [
                ('claude', self._draft_with_claude),
                ('grok', self._draft_with_grok),
                ('gemini', self._draft_with_gemini)
            ]

            for service_name, service_func in ai_services:
                try:
                    logger.info(f"Attempting content drafting with {service_name}")
                    result = await service_func(trigger_event, skills_prompt, target_platform)

                    if result and result.get('content'):
                        # Add service metadata
                        result['ai_service'] = f'external_{service_name}'
                        result['fallback_used'] = True

                        # Log delegation
                        await self._log_delegation(result, trigger_event)

                        return result

                except Exception as e:
                    logger.warning(f"{service_name} drafting failed: {e}")
                    continue

            logger.error("All external AI services failed")
            return None

        except Exception as e:
            logger.error(f"External AI drafting failed: {e}")
            return None

    async def _load_skills_prompt(self, trigger_event: Dict[str, Any]) -> str:
        """
        Load appropriate skills.md prompt based on trigger event.

        Args:
            trigger_event: Event that triggered content creation

        Returns:
            str: Skills prompt content
        """
        event_type = trigger_event.get('type', 'general')

        # Map event types to skills files
        skills_map = {
            'stream_start': 'skills/stream_announcement.md',
            'stream_end': 'skills/stream_summary.md',
            'git_commit': 'skills/git_update.md',
            'development_update': 'skills/development_progress.md'
        }

        skills_file = skills_map.get(event_type, 'skills/general_post.md')

        try:
            if os.path.exists(skills_file):
                with open(skills_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # Fallback to generic prompt
                return """
                Write a professional LinkedIn post about this event.
                Keep it engaging, informative, and under 2000 characters.
                Include relevant hashtags and call-to-action when appropriate.
                """
        except Exception as e:
            logger.warning(f"Failed to load skills prompt {skills_file}: {e}")
            return "Write a professional LinkedIn post about this event."

    async def _draft_with_claude(self, trigger_event: Dict[str, Any],
                                skills_prompt: str, target_platform: str) -> Dict[str, Any]:
        """Draft content using Claude API (placeholder)"""
        # This would integrate with Anthropic Claude API
        # For now, return a mock response

        draft_hash = self._generate_draft_hash(trigger_event)

        content = f"""🚀 Exciting Update from FoundUps!

{trigger_event.get('description', 'Something amazing just happened!')}

#AI #Innovation #Technology
"""

        return {
            'content': content,
            'draft_hash': draft_hash,
            'confidence': 0.85,
            'word_count': len(content.split()),
            'character_count': len(content),
            'metadata': {
                'trigger_event': trigger_event,
                'target_platform': target_platform,
                'skills_used': bool(skills_prompt.strip()),
                'generated_at': datetime.now().isoformat()
            }
        }

    async def _draft_with_grok(self, trigger_event: Dict[str, Any],
                              skills_prompt: str, target_platform: str) -> Dict[str, Any]:
        """Draft content using Grok API (placeholder)"""
        # This would integrate with xAI Grok API
        draft_hash = self._generate_draft_hash(trigger_event)

        content = f"""🤖 AI-Powered Innovation at FoundUps

{trigger_event.get('description', 'Advancing the boundaries of autonomous development!')}

#AI #Autonomous #FutureOfWork
"""

        return {
            'content': content,
            'draft_hash': draft_hash,
            'confidence': 0.82,
            'word_count': len(content.split()),
            'character_count': len(content),
            'metadata': {
                'trigger_event': trigger_event,
                'target_platform': target_platform,
                'skills_used': bool(skills_prompt.strip()),
                'generated_at': datetime.now().isoformat()
            }
        }

    async def _draft_with_gemini(self, trigger_event: Dict[str, Any],
                                skills_prompt: str, target_platform: str) -> Dict[str, Any]:
        """Draft content using Gemini API (placeholder)"""
        # This would integrate with Google Gemini API
        draft_hash = self._generate_draft_hash(trigger_event)

        content = f"""💡 Innovation in Progress

{trigger_event.get('description', 'Building the next generation of development tools!')}

#Innovation #Technology #Future
"""

        return {
            'content': content,
            'draft_hash': draft_hash,
            'confidence': 0.80,
            'word_count': len(content.split()),
            'character_count': len(content),
            'metadata': {
                'trigger_event': trigger_event,
                'target_platform': target_platform,
                'skills_used': bool(skills_prompt.strip()),
                'generated_at': datetime.now().isoformat()
            }
        }

    def _generate_draft_hash(self, trigger_event: Dict[str, Any]) -> str:
        """Generate unique hash for draft content"""
        content = json.dumps(trigger_event, sort_keys=True, default=str)
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}_{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    async def _log_delegation(self, draft_result: Dict[str, Any], trigger_event: Dict[str, Any]):
        """Log AI delegation event for telemetry"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'ai_delegation',
            'draft_hash': draft_result.get('draft_hash'),
            'ai_service': draft_result.get('ai_service'),
            'confidence': draft_result.get('confidence'),
            'trigger_event_type': trigger_event.get('type'),
            'fallback_used': draft_result.get('fallback_used', False),
            'content_length': len(draft_result.get('content', ''))
        }

        try:
            with open(self.delegation_history, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.warning(f"Failed to log delegation: {e}")

    async def schedule_draft(self, draft_result: Dict[str, Any],
                           delay_hours: int = 24) -> bool:
        """
        Schedule a drafted post using UI-TARS.

        Args:
            draft_result: Result from AI drafting
            delay_hours: Hours to delay scheduling

        Returns:
            bool: Success status
        """
        try:
            scheduled_time = datetime.now() + timedelta(hours=delay_hours)

            post = ScheduledPost(
                content=draft_result['content'],
                scheduled_time=scheduled_time,
                content_type=draft_result['metadata'].get('trigger_event', {}).get('type', 'general'),
                company_page='foundups',  # Default to FoundUps page
                draft_hash=draft_result['draft_hash'],
                metadata={
                    'ai_service': draft_result.get('ai_service'),
                    'confidence': draft_result.get('confidence'),
                    'trigger_event': draft_result['metadata'].get('trigger_event'),
                    'delegation_log': True
                }
            )

            success = self.ui_tars_scheduler.schedule_linkedin_post(post)

            if success:
                logger.info(f"Scheduled draft {draft_result['draft_hash']} for {scheduled_time}")

                # Update telemetry with scheduling info
                draft_result['scheduled_time'] = scheduled_time.isoformat()
                draft_result['ui_tars_scheduled'] = True

            return success

        except Exception as e:
            logger.error(f"Failed to schedule draft: {e}")
            return False


# Global singleton
_delegation_instance = None

def get_ai_delegation_orchestrator() -> AIDelegationOrchestrator:
    """Get singleton AI delegation orchestrator"""
    global _delegation_instance
    if _delegation_instance is None:
        _delegation_instance = AIDelegationOrchestrator()
    return _delegation_instance


if __name__ == "__main__":
    # CLI testing
    import argparse

    parser = argparse.ArgumentParser(description="AI Delegation Orchestrator")
    parser.add_argument("--action", choices=["draft", "schedule"], required=True)
    parser.add_argument("--event-type", default="stream_start", help="Trigger event type")
    parser.add_argument("--description", required=True, help="Event description")
    parser.add_argument("--delay-hours", type=int, default=24, help="Scheduling delay in hours")

    args = parser.parse_args()

    async def main():
        orchestrator = get_ai_delegation_orchestrator()

        trigger_event = {
            'type': args.event_type,
            'description': args.description,
            'timestamp': datetime.now().isoformat()
        }

        if args.action == "draft":
            result = await orchestrator.draft_linkedin_content(trigger_event)
            if result:
                print("Draft created:")
                print(f"Hash: {result['draft_hash']}")
                print(f"Service: {result['ai_service']}")
                print(f"Content: {result['content'][:200]}...")
            else:
                print("Drafting failed")

        elif args.action == "schedule":
            # First draft, then schedule
            draft = await orchestrator.draft_linkedin_content(trigger_event)
            if draft:
                success = await orchestrator.schedule_draft(draft, args.delay_hours)
                print(f"Scheduling {'successful' if success else 'failed'}")

    asyncio.run(main())
