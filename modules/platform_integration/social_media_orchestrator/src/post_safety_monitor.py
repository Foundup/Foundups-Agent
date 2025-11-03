#!/usr/bin/env python3
"""
Post Safety Monitor - Detects and prevents duplicate posting attempts
WSP Compliant: Monitors for user interventions and auto-corrects the system

This module detects when posts are cancelled or fail, indicating a duplicate
attempt was made, and automatically updates the database to prevent future attempts.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PostSafetyMonitor:
    """
    Monitors posting attempts and detects user interventions.

    When a user cancels a post or a post fails with "window closed" error,
    it indicates the system tried to post something already posted.
    This class tracks these events and auto-corrects the database.
    """

    def __init__(self):
        """Initialize the safety monitor"""
        self.monitor_file = Path("memory/post_safety_monitor.json")
        self.duplicate_attempts_file = Path("memory/duplicate_attempts.json")
        self.monitor_file.parent.mkdir(exist_ok=True)

        # Load existing monitoring data
        self.monitoring_data = self._load_monitoring_data()
        self.duplicate_attempts = self._load_duplicate_attempts()

    def _load_monitoring_data(self) -> Dict:
        """Load existing monitoring data"""
        if self.monitor_file.exists():
            try:
                with open(self.monitor_file, 'r', encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading monitor data: {e}")

        return {
            'manual_interventions': [],
            'auto_corrections': [],
            'last_check': datetime.now().isoformat()
        }

    def _save_monitoring_data(self):
        """Save monitoring data"""
        try:
            with open(self.monitor_file, 'w', encoding="utf-8") as f:
                json.dump(self.monitoring_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving monitor data: {e}")

    def _load_duplicate_attempts(self) -> List[Dict]:
        """Load duplicate attempt history"""
        if self.duplicate_attempts_file.exists():
            try:
                with open(self.duplicate_attempts_file, 'r', encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading duplicate attempts: {e}")
        return []

    def _save_duplicate_attempts(self):
        """Save duplicate attempts history"""
        try:
            # Keep only last 100 attempts
            if len(self.duplicate_attempts) > 100:
                self.duplicate_attempts = self.duplicate_attempts[-100:]

            with open(self.duplicate_attempts_file, 'w', encoding="utf-8") as f:
                json.dump(self.duplicate_attempts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving duplicate attempts: {e}")

    def detect_user_cancellation(self, video_id: str, platform: str, error_msg: str = None) -> bool:
        """
        Detect if a user cancelled a post or if it failed suspiciously.

        Args:
            video_id: YouTube video ID
            platform: Platform that failed (linkedin/x_twitter)
            error_msg: Error message if available

        Returns:
            True if this appears to be a duplicate attempt
        """
        # Common indicators of user cancellation or duplicate attempt
        duplicate_indicators = [
            "window already closed",
            "target window already closed",
            "web view not found",
            "no such window",
            "session not created",
            "user cancelled",
            "manually closed"
        ]

        is_duplicate = False

        if error_msg:
            error_lower = error_msg.lower()
            for indicator in duplicate_indicators:
                if indicator in error_lower:
                    is_duplicate = True
                    break

        if is_duplicate:
            logger.warning("="*60)
            logger.warning("[ALERT] DUPLICATE POSTING ATTEMPT DETECTED!")
            logger.warning(f"   Video: {video_id}")
            logger.warning(f"   Platform: {platform}")
            logger.warning(f"   Error: {error_msg[:100] if error_msg else 'User cancelled'}")
            logger.warning("="*60)

            # Record the duplicate attempt
            attempt = {
                'timestamp': datetime.now().isoformat(),
                'video_id': video_id,
                'platform': platform,
                'error': error_msg,
                'auto_corrected': False
            }

            self.duplicate_attempts.append(attempt)
            self._save_duplicate_attempts()

            # Record as manual intervention
            intervention = {
                'timestamp': datetime.now().isoformat(),
                'video_id': video_id,
                'platform': platform,
                'type': 'user_cancellation',
                'error': error_msg
            }

            self.monitoring_data['manual_interventions'].append(intervention)
            self._save_monitoring_data()

        return is_duplicate

    def auto_mark_as_posted(self, video_id: str, platform: str, title: str = None) -> bool:
        """
        Automatically mark a video as posted when duplicate attempt is detected.

        This prevents future duplicate attempts by updating the database.

        Args:
            video_id: YouTube video ID to mark as posted
            platform: Platform to mark as posted
            title: Optional video title

        Returns:
            True if successfully marked
        """
        try:
            # Import the orchestrator to update its database
            from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import orchestrator

            # Force-add to posted history
            if video_id not in orchestrator.posted_streams:
                orchestrator.posted_streams[video_id] = {
                    'timestamp': datetime.now().isoformat(),
                    'title': title or 'Auto-corrected duplicate',
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'platforms_posted': []
                }

            # Add platform if not already there
            if platform not in orchestrator.posted_streams[video_id]['platforms_posted']:
                orchestrator.posted_streams[video_id]['platforms_posted'].append(platform)
                orchestrator._save_posted_history()

                logger.info("="*60)
                logger.info("[OK] AUTO-CORRECTION APPLIED")
                logger.info(f"   Video {video_id} marked as posted to {platform}")
                logger.info("   Future duplicate attempts will be prevented")
                logger.info("="*60)

                # Record the auto-correction
                correction = {
                    'timestamp': datetime.now().isoformat(),
                    'video_id': video_id,
                    'platform': platform,
                    'action': 'marked_as_posted'
                }

                self.monitoring_data['auto_corrections'].append(correction)
                self._save_monitoring_data()

                # Mark the duplicate attempt as corrected
                for attempt in self.duplicate_attempts:
                    if attempt['video_id'] == video_id and attempt['platform'] == platform:
                        attempt['auto_corrected'] = True
                self._save_duplicate_attempts()

                return True
            else:
                logger.info(f"Video {video_id} already marked as posted to {platform}")
                return True

        except Exception as e:
            logger.error(f"Failed to auto-mark as posted: {e}")
            return False

    def get_duplicate_attempt_report(self) -> str:
        """Generate a report of duplicate posting attempts"""
        report = []
        report.append("="*60)
        report.append("DUPLICATE POSTING ATTEMPTS REPORT")
        report.append("="*60)

        if not self.duplicate_attempts:
            report.append("No duplicate attempts recorded")
        else:
            # Group by video_id
            by_video = {}
            for attempt in self.duplicate_attempts:
                vid = attempt['video_id']
                if vid not in by_video:
                    by_video[vid] = []
                by_video[vid].append(attempt)

            for video_id, attempts in by_video.items():
                report.append(f"\nVideo: {video_id}")
                report.append(f"  Duplicate attempts: {len(attempts)}")

                for attempt in attempts[-3:]:  # Show last 3 attempts
                    report.append(f"    - {attempt['timestamp']}: {attempt['platform']}")
                    if attempt.get('auto_corrected'):
                        report.append(f"      [OK] Auto-corrected")
                    else:
                        report.append(f"      [U+26A0]️ Not corrected")

        # Show recent interventions
        if self.monitoring_data['manual_interventions']:
            report.append("\n" + "-"*40)
            report.append("RECENT USER INTERVENTIONS (Last 5)")
            report.append("-"*40)

            for intervention in self.monitoring_data['manual_interventions'][-5:]:
                report.append(f"{intervention['timestamp']}: {intervention['type']} on {intervention['platform']}")

        report.append("="*60)
        return "\n".join(report)

    def check_and_fix_current_stream(self, video_id: str = "vAkosSG-zp0") -> bool:
        """
        Check if the current stream has duplicate attempts and fix them.

        This is a convenience method to fix the current known issue.
        """
        logger.info(f"Checking for duplicate attempts on video {video_id}...")

        # Check if there were any duplicate attempts for this video
        has_duplicates = False
        for attempt in self.duplicate_attempts:
            if attempt['video_id'] == video_id and not attempt.get('auto_corrected'):
                has_duplicates = True
                platform = attempt['platform']
                logger.info(f"Found uncorrected duplicate attempt for {platform}")

                # Auto-correct it
                if self.auto_mark_as_posted(video_id, platform):
                    logger.info(f"[OK] Fixed duplicate issue for {platform}")
                else:
                    logger.error(f"[FAIL] Failed to fix duplicate issue for {platform}")

        if not has_duplicates:
            logger.info("No uncorrected duplicate attempts found")

        return True


# Singleton instance
safety_monitor = PostSafetyMonitor()


def detect_and_fix_duplicate(video_id: str, platform: str, error_msg: str = None) -> bool:
    """
    Detect duplicate posting attempt and auto-fix if needed.

    Call this when a post fails with suspicious errors.
    """
    if safety_monitor.detect_user_cancellation(video_id, platform, error_msg):
        return safety_monitor.auto_mark_as_posted(video_id, platform)
    return False


def fix_current_stream_duplicates():
    """Fix any duplicate issues with the current stream"""
    return safety_monitor.check_and_fix_current_stream()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Generate report
    print(safety_monitor.get_duplicate_attempt_report())

    # Fix current stream issues
    fix_current_stream_duplicates()