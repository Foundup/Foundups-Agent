#!/usr/bin/env python3
"""
PoC Test Script for Real-time Comment Dialogue
Tests the concept before full integration
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.communication.video_comments.src.realtime_comment_dialogue import RealtimeCommentDialogue
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommentDialoguePOC:
    """Proof of Concept for real-time comment dialogue"""
    
    def __init__(self):
        self.youtube_service = None
        self.dialogue_system = None
        
        # Move2Japan channel ID (from studio URL)
        self.MOVE2JAPAN_CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"  # Move2Japan actual channel
    
    async def initialize(self):
        """Initialize YouTube service and dialogue system"""
        logger.info("="*60)
        logger.info("🚀 COMMENT DIALOGUE POC STARTING")
        logger.info("="*60)
        
        # Get YouTube service
        logger.info("Authenticating with YouTube...")
        self.youtube_service = get_authenticated_service()
        
        if not self.youtube_service:
            logger.error("Failed to authenticate")
            return False
        
        # Create dialogue system
        logger.info(f"Creating dialogue system for channel: {self.MOVE2JAPAN_CHANNEL_ID}")
        self.dialogue_system = RealtimeCommentDialogue(
            self.youtube_service,
            self.MOVE2JAPAN_CHANNEL_ID
        )
        
        return True
    
    async def run_poc(self):
        """Run the PoC test"""
        if not await self.initialize():
            return
        
        logger.info("="*60)
        logger.info("🔴 STARTING REAL-TIME COMMENT MONITORING")
        logger.info("="*60)
        logger.info("Features being tested:")
        logger.info("  ✅ Detect new comments within 15 seconds")
        logger.info("  ✅ Auto-reply to questions and mentions")
        logger.info("  ✅ Maintain conversation threads")
        logger.info("  ✅ Real-time back-and-forth dialogue")
        logger.info("="*60)
        
        # Create monitoring task
        monitor_task = asyncio.create_task(self.dialogue_system.start())
        
        # Create status display task
        status_task = asyncio.create_task(self.display_status())
        
        try:
            # Run for PoC duration
            await asyncio.gather(monitor_task, status_task)
        except KeyboardInterrupt:
            logger.info("\n⏹️ Stopping PoC test...")
            self.dialogue_system.stop()
    
    async def display_status(self):
        """Display status every 30 seconds"""
        while True:
            await asyncio.sleep(30)
            
            status = self.dialogue_system.get_status()
            
            logger.info("="*60)
            logger.info("📊 STATUS UPDATE")
            logger.info(f"  Running: {status['running']}")
            logger.info(f"  Active Threads: {status['active_threads']}")
            logger.info(f"  Comments Processed: {status['processed_comments']}")
            logger.info(f"  Current Video: {status['current_video']}")
            
            if status['threads']:
                logger.info("  Active Conversations:")
                for thread in status['threads']:
                    logger.info(f"    - {thread['author']}: {thread['messages']} messages")
            
            logger.info("="*60)
    
    async def test_specific_video(self, video_id: str):
        """Test with a specific video ID"""
        logger.info(f"Testing with video: {video_id}")
        
        # Override the dialogue system to use specific video
        self.dialogue_system.current_video_id = video_id
        
        # Run monitoring
        await self.dialogue_system.monitor_new_comments()


async def main():
    """Main entry point for PoC"""
    poc = CommentDialoguePOC()
    
    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--video":
            # Test specific video
            video_id = sys.argv[2] if len(sys.argv) > 2 else None
            if video_id:
                await poc.initialize()
                await poc.test_specific_video(video_id)
            else:
                print("Usage: python test_poc_dialogue.py --video VIDEO_ID")
        else:
            print("Usage: python test_poc_dialogue.py [--video VIDEO_ID]")
    else:
        # Run full PoC
        await poc.run_poc()


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║     YOUTUBE COMMENT DIALOGUE POC - REAL-TIME TEST     ║
    ╠════════════════════════════════════════════════════════╣
    ║  This will monitor YouTube comments in real-time and  ║
    ║  engage in dialogue with commenters automatically.    ║
    ║                                                        ║
    ║  Test Actions:                                        ║
    ║  1. Post a comment with a question                   ║
    ║  2. Reply to the bot's response                      ║
    ║  3. Watch the conversation continue!                 ║
    ║                                                        ║
    ║  Press Ctrl+C to stop                                ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPoC test stopped.")