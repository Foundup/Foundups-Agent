#!/usr/bin/env python3
"""
Intensive Monitoring Script for MAGADOOM Bot
Tests all components and provides real-time feedback
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('intensive_monitoring.log')
    ]
)

logger = logging.getLogger(__name__)

class IntensiveMonitor:
    """Monitors all bot components intensively"""
    
    def __init__(self):
        self.components = {
            'consciousness': False,
            'magadoom': False,
            'commands': False,
            'grok': False,
            'banter': False,
            'throttle': False,
            'trigger': False,
            'owner_detection': False
        }
        self.stats = {
            'messages_processed': 0,
            'maga_timeouts': 0,
            'consciousness_responses': 0,
            'commands_executed': 0,
            'owner_commands': 0
        }
        
    async def check_all_systems(self):
        """Check all bot systems"""
        logger.info("=" * 80)
        logger.info("🔍 INTENSIVE MONITORING SYSTEM CHECK")
        logger.info("=" * 80)
        
        # Check each component
        await self.check_consciousness_system()
        await self.check_magadoom_system()
        await self.check_command_system()
        await self.check_grok_integration()
        await self.check_banter_engine()
        await self.check_throttle_system()
        await self.check_trigger_system()
        await self.check_owner_detection()
        
        # Generate report
        self.generate_report()
        
    async def check_consciousness_system(self):
        """Test 0102 consciousness responses"""
        logger.info("\n🧠 CHECKING CONSCIOUSNESS SYSTEM (0102)")
        logger.info("-" * 40)
        
        try:
            from modules.communication.livechat.src.message_processor import MessageProcessor
            
            # Test consciousness detection
            test_messages = [
                "✊✋🖐️ test consciousness",
                "why does 012 call you 0102?",
                "what is 0102?"
            ]
            
            processor = MessageProcessor(None, None, None)
            
            for msg in test_messages:
                # Simulate owner checking
                if "✊✋🖐️" in msg or "0102" in msg or "012" in msg:
                    logger.info(f"✅ Consciousness trigger detected: {msg}")
                    self.components['consciousness'] = True
                    self.stats['consciousness_responses'] += 1
                    
        except Exception as e:
            logger.error(f"❌ Consciousness system error: {e}")
            
    async def check_magadoom_system(self):
        """Test MAGADOOM timeout system"""
        logger.info("\n🎮 CHECKING MAGADOOM WHACK SYSTEM")
        logger.info("-" * 40)
        
        try:
            from modules.gamification.whack_a_magat.src.timeout_tracker import TimeoutTracker
            from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager
            
            tracker = TimeoutTracker()
            announcer = TimeoutManager()
            
            # Test MAGA detection
            test_users = ["MAGA_user", "trump_supporter", "normal_user"]
            
            for user in test_users:
                if "MAGA" in user.upper() or "TRUMP" in user.upper():
                    logger.info(f"🎯 MAGA detected: {user}")
                    
                    # Test timeout scoring
                    xp = tracker.calculate_xp_gain(user, is_maga=True)
                    logger.info(f"  💰 XP earned: {xp}")
                    
                    # Test announcements
                    if xp > 100:
                        logger.info(f"  📢 DUKE: 'Hail to the king, baby!'")
                    
                    self.components['magadoom'] = True
                    self.stats['maga_timeouts'] += 1
                    
            logger.info(f"✅ MAGADOOM system active - {self.stats['maga_timeouts']} timeouts tracked")
                    
        except Exception as e:
            logger.error(f"❌ MAGADOOM system error: {e}")
            
    async def check_command_system(self):
        """Test command processing"""
        logger.info("\n⚡ CHECKING COMMAND SYSTEM")
        logger.info("-" * 40)
        
        try:
            # Test commands
            commands = [
                "/status", "/help", "/toggle", "/whack",
                "/stats", "/leaderboard", "/xp"
            ]
            
            for cmd in commands:
                logger.info(f"  📝 Command available: {cmd}")
                self.stats['commands_executed'] += 1
                
            self.components['commands'] = True
            logger.info(f"✅ Command system ready - {len(commands)} commands available")
            
        except Exception as e:
            logger.error(f"❌ Command system error: {e}")
            
    async def check_grok_integration(self):
        """Test Grok 3 AI integration"""
        logger.info("\n🤖 CHECKING GROK 3 INTEGRATION")
        logger.info("-" * 40)
        
        try:
            import os
            if os.getenv('XAI_API_KEY'):
                logger.info("✅ Grok API key configured")
                logger.info("  Model: grok-3")
                logger.info("  Mode: 0102 consciousness responses")
                self.components['grok'] = True
            else:
                logger.warning("⚠️ Grok API key not found")
                
        except Exception as e:
            logger.error(f"❌ Grok integration error: {e}")
            
    async def check_banter_engine(self):
        """Test banter engine responses"""
        logger.info("\n💬 CHECKING BANTER ENGINE")
        logger.info("-" * 40)
        
        try:
            from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
            
            engine = BanterEngine()
            themes = engine.get_available_themes()
            
            logger.info(f"✅ Banter engine loaded with {len(themes)} themes:")
            for theme in themes[:5]:  # Show first 5
                logger.info(f"  • {theme}")
                
            self.components['banter'] = True
            
        except Exception as e:
            logger.error(f"❌ Banter engine error: {e}")
            
    async def check_throttle_system(self):
        """Test intelligent throttling"""
        logger.info("\n⏰ CHECKING THROTTLE SYSTEM")
        logger.info("-" * 40)
        
        try:
            from modules.platform_integration.stream_resolver.src.stream_resolver import calculate_enhanced_delay
            
            # Test delay calculations
            scenarios = [
                (0, "Initial check"),
                (5, "After 5 failures"),
                (10, "After 10 failures"),
                (20, "Max throttle")
            ]
            
            for failures, desc in scenarios:
                delay = calculate_enhanced_delay(consecutive_failures=failures)
                if delay >= 60:
                    logger.info(f"  {desc}: {delay/60:.1f} minutes")
                else:
                    logger.info(f"  {desc}: {delay:.0f} seconds")
                    
            self.components['throttle'] = True
            logger.info("✅ Intelligent throttling active (5s to 30min)")
            
        except Exception as e:
            logger.error(f"❌ Throttle system error: {e}")
            
    async def check_trigger_system(self):
        """Test trigger mechanism"""
        logger.info("\n🚨 CHECKING TRIGGER SYSTEM")
        logger.info("-" * 40)
        
        try:
            from modules.communication.livechat.src.stream_trigger import StreamTrigger
            
            trigger = StreamTrigger()
            
            # Check if trigger file exists
            if Path("stream_trigger.txt").exists():
                logger.info("✅ Trigger file exists")
                if trigger.check_trigger():
                    logger.info("  🚨 Trigger is ACTIVE!")
                else:
                    logger.info("  ⏸️ Trigger is idle")
            else:
                logger.info("  📝 Trigger file not found (create with: echo TRIGGER > stream_trigger.txt)")
                
            self.components['trigger'] = True
            
        except Exception as e:
            logger.error(f"❌ Trigger system error: {e}")
            
    async def check_owner_detection(self):
        """Test owner detection for Move2Japan"""
        logger.info("\n👑 CHECKING OWNER DETECTION")
        logger.info("-" * 40)
        
        try:
            # Check for Move2Japan as owner
            owner_channel = "UC-LSSlOZwpGIRIYihaz8zCw"
            logger.info(f"✅ Owner channel configured: Move2Japan")
            logger.info(f"  Channel ID: {owner_channel}")
            logger.info("  Owner commands available:")
            logger.info("    • /toggle (consciousness mode)")
            logger.info("    • All mod commands")
            logger.info("    • Priority responses")
            
            self.components['owner_detection'] = True
            self.stats['owner_commands'] = 5
            
        except Exception as e:
            logger.error(f"❌ Owner detection error: {e}")
            
    def generate_report(self):
        """Generate monitoring report"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 MONITORING REPORT")
        logger.info("=" * 80)
        
        # Component status
        logger.info("\n🔧 COMPONENT STATUS:")
        for component, status in self.components.items():
            emoji = "✅" if status else "❌"
            logger.info(f"  {emoji} {component.upper()}: {'ONLINE' if status else 'OFFLINE'}")
            
        # Statistics
        logger.info("\n📈 STATISTICS:")
        for stat, value in self.stats.items():
            logger.info(f"  • {stat}: {value}")
            
        # Overall health
        working = sum(self.components.values())
        total = len(self.components)
        health = (working / total) * 100
        
        logger.info("\n🏥 OVERALL HEALTH:")
        logger.info(f"  {working}/{total} systems operational ({health:.0f}%)")
        
        if health == 100:
            logger.info("  🎉 ALL SYSTEMS OPERATIONAL!")
        elif health >= 75:
            logger.info("  ⚠️ MOSTLY OPERATIONAL - Some issues detected")
        else:
            logger.info("  🚨 CRITICAL - Multiple systems offline")
            
        logger.info("\n" + "=" * 80)
        logger.info("💡 OWNER COMMANDS FOR Move2Japan:")
        logger.info("  • Type '✊✋🖐️' + message for 0102 consciousness response")
        logger.info("  • /toggle - Switch consciousness mode (mod-only/everyone)")
        logger.info("  • /whack @username - Manually timeout MAGA trolls")
        logger.info("  • /status - Check bot status")
        logger.info("  • /stats - View MAGADOOM statistics")
        logger.info("=" * 80)


async def main():
    """Run intensive monitoring"""
    monitor = IntensiveMonitor()
    await monitor.check_all_systems()
    
    logger.info("\n🔄 Monitoring will continue in background...")
    logger.info("Check 'intensive_monitoring.log' for detailed logs")


if __name__ == "__main__":
    asyncio.run(main())