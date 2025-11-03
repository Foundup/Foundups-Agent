"""
Stream Trigger Utilities
Manual trigger and intelligent delay helpers for stream monitoring

NAVIGATION: Handles manual trigger workflows and delay tuning.
-> Called by: auto_moderator_dae.py when restarting streams
-> Delegates to: create_intelligent_delay, StreamTrigger
-> Related: NAVIGATION.py -> NEED_TO["trigger stream handshake"]
-> Quick ref: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["stream_detection_flow"]
"""

import os
import time
import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class StreamTrigger:
    """Manages trigger mechanisms for immediate stream checking"""
    
    def __init__(self, trigger_file: str = None):
        """
        Initialize trigger manager.
        
        Args:
            trigger_file: Path to trigger file (defaults to memory/stream_trigger.txt)
        """
        if trigger_file is None:
            # Use memory directory for trigger file
            memory_dir = Path("memory")
            memory_dir.mkdir(exist_ok=True)
            trigger_file = memory_dir / "stream_trigger.txt"
        self.trigger_file = Path(trigger_file)
        self.last_trigger_time = 0
        self.triggered = False
        
    def check_trigger(self) -> bool:
        """
        Check if a trigger has been activated.
        
        Returns:
            True if triggered, False otherwise
        """
        # Check file trigger
        if self._check_file_trigger():
            return True
            
        # Future: Check API endpoint
        # if self._check_api_trigger():
        #     return True
            
        # Future: Check webhook
        # if self._check_webhook_trigger():
        #     return True
            
        return False
    
    def _check_file_trigger(self) -> bool:
        """
        Check if trigger file exists or has been modified.
        
        The trigger activates if:
        - File is created
        - File is modified (touch command)
        - File contains "TRIGGER" text
        """
        try:
            if not self.trigger_file.exists():
                return False
                
            # Check modification time
            mtime = self.trigger_file.stat().st_mtime
            
            # If file is newer than last trigger
            if mtime > self.last_trigger_time:
                self.last_trigger_time = mtime
                
                # Check content for explicit trigger
                content = self.trigger_file.read_text().strip()
                if "TRIGGER" in content.upper():
                    logger.info("[ALERT] Stream trigger activated via file!")
                    # Clear the file after reading
                    self.trigger_file.write_text("")
                    return True
                    
                # Any modification counts as trigger
                logger.info("[NOTE] Trigger file modified - checking for stream")
                return True
                
        except Exception as e:
            logger.debug(f"Error checking trigger file: {e}")
            
        return False
    
    def reset(self):
        """Reset trigger state"""
        self.triggered = False
        
    def create_trigger_instructions(self):
        """Create instructions file for how to use triggers"""
        # Don't create instructions file - violates WSP
        # Instructions already exist in docs/TRIGGER_INSTRUCTIONS.md
        logger.debug("Trigger instructions available in docs/TRIGGER_INSTRUCTIONS.md")


def create_intelligent_delay(
    consecutive_failures: int,
    previous_delay: float = None,
    has_trigger: bool = False,
    min_delay: float = 30.0,
    max_delay: float = 1800.0  # 30 minutes
) -> float:
    """
    Create intelligent delay with trigger support.
    
    Args:
        consecutive_failures: Number of consecutive stream check failures
        previous_delay: Previous delay used
        has_trigger: Whether a trigger is available
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds (30 minutes)
        
    Returns:
        Delay in seconds
    """
    if has_trigger:
        # With trigger available, can use longer delays
        if consecutive_failures == 0:
            return min_delay
        elif consecutive_failures <= 3:
            # Quick ramp: 5s -> 30s -> 60s -> 120s
            return min(min_delay * (2 ** consecutive_failures), 120)
        elif consecutive_failures <= 6:
            # Medium ramp: 3min -> 5min -> 10min
            return min(180 * (consecutive_failures - 2), 600)
        else:
            # Max out at 30 minutes since we have trigger
            return max_delay
    else:
        # Without trigger, use more aggressive checking
        if consecutive_failures == 0:
            return min_delay
        elif consecutive_failures <= 5:
            # Moderate ramp: 5s -> 10s -> 20s -> 40s -> 80s -> 160s
            return min(min_delay * (2 ** (consecutive_failures * 0.7)), 160)
        elif consecutive_failures <= 10:
            # Slower ramp: up to 5 minutes
            return min(160 + (30 * (consecutive_failures - 5)), 300)
        else:
            # Max at 10 minutes without trigger
            return min(300 + (60 * (consecutive_failures - 10)), 600)


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create trigger manager
    trigger = StreamTrigger()
    trigger.create_trigger_instructions()
    
    print("[TARGET] Stream Trigger Test")
    print("=" * 60)
    
    # Test trigger checking
    for i in range(5):
        if trigger.check_trigger():
            print(f"[OK] Trigger activated at iteration {i}!")
            trigger.reset()
        else:
            print(f"⏳ No trigger at iteration {i}")
        time.sleep(2)
    
    print("\n[DATA] Intelligent Delay Examples:")
    print("=" * 60)
    
    # Show delay progression
    for failures in [0, 1, 3, 5, 10, 15, 20]:
        with_trigger = create_intelligent_delay(failures, has_trigger=True)
        without_trigger = create_intelligent_delay(failures, has_trigger=False)
        
        print(f"Failures: {failures:2d} | With Trigger: {with_trigger:6.0f}s ({with_trigger/60:4.1f}m) | "
              f"Without: {without_trigger:6.0f}s ({without_trigger/60:4.1f}m)")