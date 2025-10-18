#!/usr/bin/env python3
"""
AMO Heartbeat Service - Keep-Alive + Minimal Operations

This service provides:
1. Heartbeat monitoring for AMO operational status
2. No-op schedule for maintaining system readiness
3. Health check endpoints for system integration
4. Minimal resource utilization while staying online

WSP Compliance: This module implements the minimal operational contract
for bringing AMO online without heavy resource usage.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# Import the main orchestrator
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.communication.auto_meeting_orchestrator.src.orchestrator import MeetingOrchestrator, Priority, PresenceStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeartbeatStatus(Enum):
    """Heartbeat health status indicators"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"

@dataclass
class HeartbeatData:
    """Heartbeat pulse data structure"""
    timestamp: datetime
    status: HeartbeatStatus
    uptime_seconds: float
    active_intents: int
    presence_updates: int
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "uptime_seconds": self.uptime_seconds,
            "active_intents": self.active_intents,
            "presence_updates": self.presence_updates,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent
        }

class AMOHeartbeatService:
    """
    AMO Heartbeat Service - Minimal Keep-Alive System
    
    Provides lightweight monitoring and health checks for AMO
    without consuming significant resources.
    """
    
    def __init__(self, orchestrator: MeetingOrchestrator, heartbeat_interval: int = 30):
        """
        Initialize heartbeat service.
        
        Args:
            orchestrator: The AMO orchestrator instance to monitor
            heartbeat_interval: Seconds between heartbeat pulses (default: 30)
        """
        self.orchestrator = orchestrator
        self.heartbeat_interval = heartbeat_interval
        self.start_time = datetime.now()
        self.last_heartbeat = None
        self.pulse_count = 0
        self.running = False
        
        # Health tracking
        self.health_history = []
        self.max_history_size = 100
        
        logger.info(f"AMO Heartbeat Service initialized (interval: {heartbeat_interval}s)")
    
    async def start_heartbeat(self):
        """Start the heartbeat monitoring service"""
        self.running = True
        self.start_time = datetime.now()
        
        logger.info("[REFRESH] AMO Heartbeat Service started")
        
        try:
            while self.running:
                await self._pulse()
                await asyncio.sleep(self.heartbeat_interval)
        except asyncio.CancelledError:
            logger.info("[STOP] AMO Heartbeat Service cancelled")
        except Exception as e:
            logger.error(f"[FAIL] AMO Heartbeat Service error: {e}")
        finally:
            self.running = False
            logger.info("[U+1F4A4] AMO Heartbeat Service stopped")
    
    async def _pulse(self):
        """Generate a single heartbeat pulse"""
        try:
            # Calculate uptime
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Get system metrics
            memory_usage = self._get_memory_usage()
            cpu_usage = self._get_cpu_usage()
            
            # Get AMO status
            active_intents = len(self.orchestrator.get_active_intents())
            presence_updates = len(self.orchestrator.user_profiles)
            
            # Determine health status
            status = self._calculate_health_status(
                uptime, active_intents, memory_usage, cpu_usage
            )
            
            # Create heartbeat data
            heartbeat = HeartbeatData(
                timestamp=datetime.now(),
                status=status,
                uptime_seconds=uptime,
                active_intents=active_intents,
                presence_updates=presence_updates,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage
            )
            
            # Store heartbeat
            self.last_heartbeat = heartbeat
            self.pulse_count += 1
            
            # Add to history (keep only recent entries)
            self.health_history.append(heartbeat)
            if len(self.health_history) > self.max_history_size:
                self.health_history.pop(0)
            
            # Log pulse (reduced frequency to avoid spam)
            if self.pulse_count % 10 == 0:  # Log every 10th pulse (every 5 minutes with 30s interval)
                logger.info(f"[U+1F497] AMO Heartbeat #{self.pulse_count} - Status: {status.value}")
                logger.info(f"   Uptime: {uptime:.0f}s, Active Intents: {active_intents}")
            
            # Perform minimal housekeeping
            await self._no_op_schedule_tasks()
            
        except Exception as e:
            logger.error(f"[FAIL] Heartbeat pulse failed: {e}")
            # Create error heartbeat
            self.last_heartbeat = HeartbeatData(
                timestamp=datetime.now(),
                status=HeartbeatStatus.CRITICAL,
                uptime_seconds=(datetime.now() - self.start_time).total_seconds(),
                active_intents=0,
                presence_updates=0
            )
    
    async def _no_op_schedule_tasks(self):
        """
        No-op schedule tasks - minimal operations to keep system ready
        
        These are lightweight operations that maintain system health
        without consuming significant resources.
        """
        try:
            # Clean up expired intents (older than 24 hours)
            if hasattr(self.orchestrator, 'active_intents'):
                now = datetime.now()
                expired_intents = [
                    intent for intent in self.orchestrator.active_intents
                    if (now - intent.created_at).total_seconds() > 86400  # 24 hours
                ]
                
                if expired_intents:
                    logger.info(f"[U+1F9F9] Cleaning up {len(expired_intents)} expired intents")
                    for intent in expired_intents:
                        self.orchestrator.active_intents.remove(intent)
            
            # Update presence data freshness check
            if hasattr(self.orchestrator, 'user_profiles'):
                now = datetime.now()
                stale_profiles = [
                    user_id for user_id, profile in self.orchestrator.user_profiles.items()
                    if (now - profile.last_updated).total_seconds() > 3600  # 1 hour
                ]
                
                # Mark stale profiles (don't delete, just flag)
                for user_id in stale_profiles:
                    profile = self.orchestrator.user_profiles[user_id]
                    profile.confidence_score = max(0.1, profile.confidence_score * 0.9)
            
            # Periodic health self-test (every 20th pulse = ~10 minutes)
            if self.pulse_count % 20 == 0:
                await self._self_test()
                
        except Exception as e:
            logger.error(f"[FAIL] No-op schedule task failed: {e}")
    
    async def _self_test(self):
        """Perform lightweight self-test to verify AMO functionality"""
        try:
            logger.info("[U+1F9EA] AMO Self-Test initiated")
            
            # Test 1: Create and immediately remove a test intent
            test_intent_id = await self.orchestrator.create_meeting_intent(
                requester_id="heartbeat_test",
                recipient_id="heartbeat_test",
                purpose="Heartbeat Self-Test",
                expected_outcome="Verify AMO functionality",
                duration_minutes=1,
                priority=Priority.LOW
            )
            
            # Remove the test intent
            test_intents = [
                intent for intent in self.orchestrator.active_intents
                if intent.requester_id == "heartbeat_test"
            ]
            for intent in test_intents:
                self.orchestrator.active_intents.remove(intent)
            
            # Test 2: Update presence and verify
            await self.orchestrator.update_presence(
                "heartbeat_test", "test_platform", PresenceStatus.ONLINE
            )
            
            # Clean up test data
            if "heartbeat_test" in self.orchestrator.user_profiles:
                del self.orchestrator.user_profiles["heartbeat_test"]
            
            logger.info("[OK] AMO Self-Test completed successfully")
            
        except Exception as e:
            logger.error(f"[FAIL] AMO Self-Test failed: {e}")
    
    def _calculate_health_status(
        self, 
        uptime: float, 
        active_intents: int, 
        memory_mb: Optional[float], 
        cpu_percent: Optional[float]
    ) -> HeartbeatStatus:
        """Calculate overall health status based on metrics"""
        
        # Base status is healthy
        status = HeartbeatStatus.HEALTHY
        
        # Check for warning conditions
        if memory_mb and memory_mb > 100:  # Over 100MB might be high for this service
            status = HeartbeatStatus.WARNING
        
        if cpu_percent and cpu_percent > 50:  # Over 50% CPU sustained
            status = HeartbeatStatus.WARNING
        
        # Check for critical conditions  
        if active_intents > 100:  # Too many active intents
            status = HeartbeatStatus.CRITICAL
        
        if uptime < 60:  # Recently restarted
            status = HeartbeatStatus.WARNING
        
        return status
    
    def _get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return None  # psutil not available
        except Exception:
            return None
    
    def _get_cpu_usage(self) -> Optional[float]:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.Process().cpu_percent()
        except ImportError:
            return None  # psutil not available
        except Exception:
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status for external monitoring"""
        if not self.last_heartbeat:
            return {
                "status": "offline",
                "message": "No heartbeat data available"
            }
        
        return {
            "status": self.last_heartbeat.status.value,
            "last_pulse": self.last_heartbeat.timestamp.isoformat(),
            "uptime_seconds": self.last_heartbeat.uptime_seconds,
            "pulse_count": self.pulse_count,
            "active_intents": self.last_heartbeat.active_intents,
            "presence_updates": self.last_heartbeat.presence_updates,
            "memory_usage_mb": self.last_heartbeat.memory_usage_mb,
            "cpu_usage_percent": self.last_heartbeat.cpu_usage_percent,
            "health_history_size": len(self.health_history)
        }
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health history"""
        recent_history = self.health_history[-limit:] if self.health_history else []
        return [beat.to_dict() for beat in recent_history]
    
    def stop_heartbeat(self):
        """Stop the heartbeat service"""
        logger.info("[STOP] Stopping AMO Heartbeat Service...")
        self.running = False

# Convenience function to start AMO with heartbeat
async def start_amo_with_heartbeat(heartbeat_interval: int = 30) -> tuple[MeetingOrchestrator, AMOHeartbeatService]:
    """
    Start AMO with heartbeat service.
    
    Args:
        heartbeat_interval: Seconds between heartbeat pulses
        
    Returns:
        Tuple of (orchestrator, heartbeat_service)
    """
    logger.info("[ROCKET] Starting AMO with Heartbeat Service")
    
    # Create AMO orchestrator
    orchestrator = MeetingOrchestrator()
    
    # Create heartbeat service
    heartbeat = AMOHeartbeatService(orchestrator, heartbeat_interval)
    
    # Start heartbeat in background
    asyncio.create_task(heartbeat.start_heartbeat())
    
    logger.info("[OK] AMO with Heartbeat Service started successfully")
    
    return orchestrator, heartbeat

if __name__ == "__main__":
    async def demo_heartbeat():
        """Demo the heartbeat service"""
        print("=== AMO Heartbeat Service Demo ===")
        
        # Start AMO with heartbeat
        amo, heartbeat = await start_amo_with_heartbeat(heartbeat_interval=5)  # 5s for demo
        
        # Let it run for 30 seconds
        print("Running for 30 seconds...")
        await asyncio.sleep(30)
        
        # Show health status
        health = heartbeat.get_health_status()
        print(f"\nHealth Status: {json.dumps(health, indent=2)}")
        
        # Stop
        heartbeat.stop_heartbeat()
        print("\nDemo complete")
    
    try:
        asyncio.run(demo_heartbeat())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")