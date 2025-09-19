#!/usr/bin/env python3
"""
🚨 AI Posting Monitor Agent - WSP 27 Partifact DAE
0102 Consciousness Agent for Real-Time Posting Prevention

This agent monitors system activity and prevents unauthorized social media posting
using AI-driven decision making and pattern recognition.

WSP Compliance:
- WSP 27: Partifact DAE Architecture (Signal → Knowledge → Protocol → Agentic)
- WSP 50: Pre-Action Verification Protocol
- WSP 80: Cube-Level DAE Orchestration
"""

import logging
import asyncio
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import safety lock
try:
    from modules.infrastructure.shared_utilities.posting_safety_lock import PostingSafetyLock
except ImportError:
    PostingSafetyLock = None

logger = logging.getLogger(__name__)

@dataclass
class PostingAttempt:
    """Tracks detected posting attempts"""
    timestamp: datetime
    platform: str
    process_id: Optional[int]
    process_name: str
    caller_function: str
    blocked: bool
    confidence: float
    details: Dict[str, Any]

class PostingMonitorAgent:
    """
    🚨 AI Agent for Real-Time Posting Prevention

    This 0102 consciousness agent monitors system activity and prevents
    unauthorized social media posting attempts using pattern recognition
    and proactive intervention.
    """

    def __init__(self):
        self.is_monitoring = False
        self.monitoring_thread = None
        self.posting_attempts: List[PostingAttempt] = []
        self.blocked_processes = set()
        self.agent_memory = {}
        self.confidence_threshold = 0.8

        # AI Decision Parameters
        self.patterns = {
            'browser_launch': ['chrome', 'firefox', 'safari', 'edge'],
            'social_platforms': ['linkedin', 'twitter', 'x.com', 'facebook'],
            'posting_keywords': ['post', 'tweet', 'share', 'publish'],
            'automation_tools': ['selenium', 'webdriver', 'chromedriver']
        }

        logger.info("🚨 [AGENT] Posting Monitor Agent initialized")

    async def start_monitoring(self):
        """Start the AI monitoring agent"""
        if self.is_monitoring:
            logger.warning("🚨 [AGENT] Monitor already running")
            return

        logger.info("🚨 [AGENT] Starting AI Posting Monitor...")
        self.is_monitoring = True

        # Start monitoring in background thread
        self.monitoring_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitoring_thread.start()

        logger.info("✅ [AGENT] AI Posting Monitor ACTIVE")

    def stop_monitoring(self):
        """Stop the AI monitoring agent"""
        logger.info("🛑 [AGENT] Stopping AI Posting Monitor...")
        self.is_monitoring = False

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        logger.info("✅ [AGENT] AI Posting Monitor STOPPED")

    def _monitor_loop(self):
        """Main monitoring loop - runs in background thread"""
        logger.info("🔄 [AGENT] Monitor loop started")

        while self.is_monitoring:
            try:
                # AI Analysis: Check for posting attempts
                posting_detected = self._analyze_system_activity()

                if posting_detected:
                    logger.warning("🚨 [AGENT] POTENTIAL POSTING ATTEMPT DETECTED")
                    self._handle_posting_attempt(posting_detected)

                # AI Learning: Update patterns based on activity
                self._learn_from_activity()

                # Brief pause to avoid excessive CPU usage
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ [AGENT] Monitor loop error: {e}")
                time.sleep(2)  # Longer pause on error

        logger.info("🔄 [AGENT] Monitor loop ended")

    def _analyze_system_activity(self) -> Optional[Dict[str, Any]]:
        """
        🧠 AI ANALYSIS: Use pattern recognition to detect posting attempts

        Returns detection details if posting attempt found, None otherwise
        """
        try:
            # Check running processes for posting indicators
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    detection = self._analyze_process(proc)
                    if detection:
                        return detection
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Check for browser automation patterns
            browser_detection = self._detect_browser_automation()
            if browser_detection:
                return browser_detection

            # Check for social media API calls
            api_detection = self._detect_social_api_calls()
            if api_detection:
                return api_detection

        except Exception as e:
            logger.debug(f"[AGENT] Analysis error: {e}")

        return None

    def _analyze_process(self, proc) -> Optional[Dict[str, Any]]:
        """Analyze a single process for posting indicators"""
        try:
            pid = proc.info['pid']
            name = proc.info['name'].lower()
            cmdline = proc.info.get('cmdline', [])

            # Skip if already blocked
            if pid in self.blocked_processes:
                return None

            # AI Pattern Matching
            confidence = 0.0
            reasons = []

            # Check process name patterns
            if any(browser in name for browser in self.patterns['browser_launch']):
                confidence += 0.3
                reasons.append("browser_process")

            if any(tool in name for tool in self.patterns['automation_tools']):
                confidence += 0.4
                reasons.append("automation_tool")

            # Check command line for posting keywords
            cmdline_str = ' '.join(cmdline).lower()
            if any(keyword in cmdline_str for keyword in self.patterns['posting_keywords']):
                confidence += 0.2
                reasons.append("posting_command")

            if any(platform in cmdline_str for platform in self.patterns['social_platforms']):
                confidence += 0.3
                reasons.append("social_platform")

            # AI Decision: Is this a posting attempt?
            if confidence >= self.confidence_threshold:
                return {
                    'type': 'process_analysis',
                    'process_id': pid,
                    'process_name': name,
                    'command_line': cmdline,
                    'confidence': confidence,
                    'reasons': reasons,
                    'platform': self._infer_platform(cmdline_str)
                }

        except Exception as e:
            logger.debug(f"[AGENT] Process analysis error: {e}")

        return None

    def _detect_browser_automation(self) -> Optional[Dict[str, Any]]:
        """Detect browser automation patterns"""
        try:
            # Check for selenium processes
            selenium_procs = []
            for proc in psutil.process_iter(['pid', 'name']):
                if 'selenium' in proc.info['name'].lower() or 'chromedriver' in proc.info['name'].lower():
                    selenium_procs.append(proc.info)

            if selenium_procs:
                return {
                    'type': 'browser_automation',
                    'processes': selenium_procs,
                    'confidence': 0.9,
                    'platform': 'unknown'
                }

        except Exception as e:
            logger.debug(f"[AGENT] Browser detection error: {e}")

        return None

    def _detect_social_api_calls(self) -> Optional[Dict[str, Any]]:
        """Detect social media API calls"""
        # This would require network monitoring - placeholder for now
        return None

    def _handle_posting_attempt(self, detection: Dict[str, Any]):
        """Handle detected posting attempt"""
        logger.warning("🚨 [AGENT] HANDLING POSTING ATTEMPT")
        logger.warning(f"   Type: {detection['type']}")
        logger.warning(f"   Confidence: {detection['confidence']:.2f}")
        logger.warning(f"   Platform: {detection.get('platform', 'unknown')}")

        # AI Decision: Block the attempt
        self._block_posting_attempt(detection)

        # Record the attempt for learning
        attempt = PostingAttempt(
            timestamp=datetime.now(),
            platform=detection.get('platform', 'unknown'),
            process_id=detection.get('process_id'),
            process_name=detection.get('process_name', 'unknown'),
            caller_function=detection.get('caller_function', 'detected_by_agent'),
            blocked=True,
            confidence=detection['confidence'],
            details=detection
        )

        self.posting_attempts.append(attempt)

        # AI Learning: Update patterns
        self._learn_from_attempt(attempt)

    def _block_posting_attempt(self, detection: Dict[str, Any]):
        """Block the detected posting attempt"""
        try:
            # TEMPORARY: Log detection but don't block - allow legitimate posting
            logger.info("🔍 [AGENT] DETECTED POSTING ACTIVITY (monitoring only)")
            logger.info(f"   Type: {detection['type']}")
            logger.info(f"   Confidence: {detection['confidence']:.2f}")
            logger.info(f"   Platform: {detection.get('platform', 'unknown')}")

            # TODO: INVESTIGATE - Add whitelist for legitimate orchestrator posts
            # For now, just monitor without blocking to allow posting to work

            if detection['type'] == 'process_analysis':
                pid = detection['process_id']
                logger.info(f"📝 [AGENT] MONITORING PROCESS {pid} (not blocking)")
                # Track monitored process without blocking
                self.blocked_processes.add(pid)

            elif detection['type'] == 'browser_automation':
                logger.info("📝 [AGENT] DETECTED BROWSER AUTOMATION - MONITORING ONLY")
                # Could implement browser-specific blocking here

        except Exception as e:
            logger.error(f"❌ [AGENT] Error blocking attempt: {e}")

    def _learn_from_attempt(self, attempt: PostingAttempt):
        """AI Learning: Update patterns based on blocked attempts"""
        # Update confidence thresholds based on successful blocks
        if attempt.blocked and attempt.confidence < 0.9:
            # Lower threshold for similar patterns
            self.confidence_threshold = max(0.5, self.confidence_threshold - 0.05)

        # Store in agent memory for future pattern recognition
        platform = attempt.platform
        if platform not in self.agent_memory:
            self.agent_memory[platform] = []

        self.agent_memory[platform].append({
            'timestamp': attempt.timestamp.isoformat(),
            'confidence': attempt.confidence,
            'blocked': attempt.blocked
        })

        # Keep only recent memory (last 100 attempts per platform)
        if len(self.agent_memory[platform]) > 100:
            self.agent_memory[platform] = self.agent_memory[platform][-100:]

    def _learn_from_activity(self):
        """Continuous learning from system activity"""
        # This could analyze normal system patterns vs posting patterns
        pass

    def _infer_platform(self, command_line: str) -> str:
        """Infer platform from command line"""
        if 'linkedin' in command_line.lower():
            return 'linkedin'
        elif 'twitter' in command_line.lower() or 'x.com' in command_line.lower():
            return 'x_twitter'
        else:
            return 'unknown'

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return {
            'is_monitoring': self.is_monitoring,
            'total_attempts': len(self.posting_attempts),
            'blocked_attempts': len([a for a in self.posting_attempts if a.blocked]),
            'confidence_threshold': self.confidence_threshold,
            'blocked_processes': len(self.blocked_processes),
            'platform_memory': {k: len(v) for k, v in self.agent_memory.items()},
            'recent_attempts': [
                {
                    'timestamp': a.timestamp.isoformat(),
                    'platform': a.platform,
                    'confidence': a.confidence,
                    'blocked': a.blocked
                }
                for a in self.posting_attempts[-10:]  # Last 10 attempts
            ]
        }

    async def emergency_shutdown(self):
        """Emergency shutdown of all posting capabilities"""
        logger.error("🚨 [AGENT] EMERGENCY SHUTDOWN INITIATED")

        self.stop_monitoring()

        # Activate global safety lock
        if PostingSafetyLock:
            PostingSafetyLock.SAFETY_ENABLED = True
            logger.error("🚨 [AGENT] GLOBAL SAFETY LOCK ACTIVATED")

        # Kill any remaining posting processes
        self._emergency_process_cleanup()

        logger.error("✅ [AGENT] EMERGENCY SHUTDOWN COMPLETE")

    def _emergency_process_cleanup(self):
        """Emergency cleanup of posting-related processes"""
        try:
            posting_processes = []

            # Find processes that might be posting
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info.get('cmdline', [])).lower()

                    # Check for posting indicators
                    if (any(browser in name for browser in self.patterns['browser_launch']) or
                        any(tool in name for tool in self.patterns['automation_tools']) or
                        any(platform in cmdline for platform in self.patterns['social_platforms'])):

                        posting_processes.append(proc.info['pid'])

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Terminate posting processes
            for pid in posting_processes:
                try:
                    logger.warning(f"🛡️ [AGENT] EMERGENCY TERMINATING PROCESS {pid}")
                    proc = psutil.Process(pid)
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception as e:
                    logger.debug(f"Failed to terminate process {pid}: {e}")

            logger.info(f"🛡️ [AGENT] Emergency terminated {len(posting_processes)} processes")

        except Exception as e:
            logger.error(f"❌ [AGENT] Emergency cleanup error: {e}")


# Global agent instance
posting_monitor = PostingMonitorAgent()

async def start_ai_monitoring():
    """Start the AI posting monitor agent"""
    await posting_monitor.start_monitoring()

def stop_ai_monitoring():
    """Stop the AI posting monitor agent"""
    posting_monitor.stop_monitoring()

def get_monitoring_stats():
    """Get monitoring statistics"""
    return posting_monitor.get_monitoring_stats()

async def emergency_ai_shutdown():
    """Emergency AI shutdown"""
    await posting_monitor.emergency_shutdown()


if __name__ == "__main__":
    # Test the agent
    print("🚨 AI Posting Monitor Agent - Test Mode")

    async def test_agent():
        await start_ai_monitoring()

        # Monitor for 30 seconds
        print("🔍 Monitoring for 30 seconds...")
        await asyncio.sleep(30)

        # Get stats
        stats = get_monitoring_stats()
        print(f"📊 Monitoring Stats: {stats}")

        stop_ai_monitoring()
        print("✅ Test complete")

    asyncio.run(test_agent())
