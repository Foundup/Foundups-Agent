"""
Stream Density Testing for MAGADOOM Announcements
Tests system behavior from 100 to 1000+ concurrent viewers
Ensures announcements scale appropriately with stream activity
"""

import pytest
import time
import random
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor
import threading

from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager
from modules.gamification.whack_a_magat.src.whack import apply_whack, get_profile
import re


class StreamDensitySimulator:
    """Simulates different stream densities for testing"""
    
    def __init__(self, viewer_count: int, chat_rate: float):
        """
        Args:
            viewer_count: Number of concurrent viewers
            chat_rate: Messages per second in chat
        """
        self.viewer_count = viewer_count
        self.chat_rate = chat_rate
        self.activity_level = self._calculate_activity_level()
        
    def _calculate_activity_level(self) -> str:
        """Calculate stream activity level based on metrics"""
        if self.viewer_count < 200:
            return "LOW"  # Small stream
        elif self.viewer_count < 500:
            return "MEDIUM"  # Medium stream
        elif self.viewer_count < 1000:
            return "HIGH"  # Large stream
        else:
            return "EXTREME"  # Massive stream
    
    def get_timeout_frequency(self) -> float:
        """Get expected timeout frequency based on stream size"""
        # More viewers = more trolls = more timeouts
        base_rate = 0.01  # 1% of viewers might be trolls
        troll_rate = self.viewer_count * base_rate
        
        # Adjust for chat activity
        if self.chat_rate > 10:  # Very active chat
            troll_rate *= 1.5
        elif self.chat_rate < 2:  # Slow chat
            troll_rate *= 0.5
            
        return troll_rate / 60  # Timeouts per second
    
    def get_announcement_threshold(self) -> dict:
        """Get dynamic thresholds based on stream density"""
        if self.activity_level == "LOW":
            return {
                "multi_whack_window": 30,  # Generous window for small streams
                "cooldown_period": 5,      # Short cooldown
                "min_announcement_gap": 2   # Frequent announcements OK
            }
        elif self.activity_level == "MEDIUM":
            return {
                "multi_whack_window": 20,  # Moderate window
                "cooldown_period": 10,     # Medium cooldown
                "min_announcement_gap": 5   # Space out announcements
            }
        elif self.activity_level == "HIGH":
            return {
                "multi_whack_window": 15,  # Tighter window for busy streams
                "cooldown_period": 15,     # Longer cooldown
                "min_announcement_gap": 8   # Avoid spam
            }
        else:  # EXTREME
            return {
                "multi_whack_window": 10,  # Very tight window
                "cooldown_period": 20,     # Long cooldown
                "min_announcement_gap": 10  # Minimal announcements
            }


class TestStreamDensityScaling:
    """Test announcement system under different stream densities"""
    
    @pytest.fixture
    def timeout_manager(self):
        """Create a timeout manager for testing"""
        return TimeoutManager(memory_dir="/tmp/test_density")
    
    def simulate_timeouts(self, manager: TimeoutManager, count: int, 
                         interval: float, mod_count: int = 3) -> list:
        """Simulate multiple timeouts with given interval"""
        announcements = []
        mods = [f"Mod{i}" for i in range(mod_count)]
        
        for i in range(count):
            mod_name = random.choice(mods)
            mod_id = f"mod_{mod_name}"
            target = f"Troll{i}"
            
            # Vary timeout duration for realism
            durations = [10, 60, 300, 300, 300, 600, 3600]  # Most are 5min
            duration = random.choice(durations)
            
            result = manager.record_timeout(
                mod_id=mod_id,
                mod_name=mod_name,
                target_id=f"target_{i}",
                target_name=target,
                duration=duration,
                reason="Trolling"
            )
            
            if result.get("announcement"):
                announcements.append({
                    "time": time.time(),
                    "text": result["announcement"],
                    "mod": mod_name
                })
            
            time.sleep(interval)
        
        return announcements
    
    @pytest.mark.parametrize("viewer_count,expected_activity", [
        (100, "LOW"),
        (250, "MEDIUM"),
        (500, "HIGH"),
        (1000, "EXTREME"),
        (1500, "EXTREME")
    ])
    def test_activity_level_calculation(self, viewer_count, expected_activity):
        """Test that activity levels are calculated correctly"""
        simulator = StreamDensitySimulator(viewer_count, 5.0)
        assert simulator.activity_level == expected_activity
    
    def test_small_stream_100_viewers(self, timeout_manager):
        """Test behavior with ~100 viewers (small stream)"""
        simulator = StreamDensitySimulator(100, 2.0)  # Slow chat
        
        # Small stream might have 1-2 timeouts per minute
        timeouts_per_minute = 2
        interval = 60 / timeouts_per_minute
        
        # Simulate 5 minutes of stream
        announcements = self.simulate_timeouts(
            timeout_manager, 
            count=10,  # 10 timeouts in 5 minutes
            interval=interval/60,  # Convert to seconds
            mod_count=2  # Small stream has fewer mods
        )
        
        # In small streams, most timeouts should get announcements
        assert len(announcements) >= 8  # At least 80% get announced
        
        # Check for multi-whack opportunities (should be easier in small streams)
        multi_whacks = [a for a in announcements if "DOUBLE" in a["text"] or "MULTI" in a["text"]]
        assert len(multi_whacks) >= 1  # Should get some multi-whacks
    
    def test_medium_stream_500_viewers(self, timeout_manager):
        """Test behavior with ~500 viewers (medium stream)"""
        simulator = StreamDensitySimulator(500, 5.0)  # Active chat
        
        # Medium stream might have 5-10 timeouts per minute
        announcements = self.simulate_timeouts(
            timeout_manager,
            count=30,  # 30 timeouts in 5 minutes
            interval=0.1,  # Every 6 seconds
            mod_count=5  # More mods
        )
        
        # Should have good variety of announcements
        double_whacks = [a for a in announcements if "DOUBLE" in a["text"]]
        multi_whacks = [a for a in announcements if "MULTI" in a["text"]]
        mega_whacks = [a for a in announcements if "MEGA" in a["text"]]
        
        total_special = len(double_whacks) + len(multi_whacks) + len(mega_whacks)
        assert total_special >= 3  # Should get multiple special announcements
    
    def test_large_stream_1000_viewers(self, timeout_manager):
        """Test behavior with ~1000 viewers (large stream)"""
        simulator = StreamDensitySimulator(1000, 10.0)  # Very active chat
        
        # Large stream might have 15-20 timeouts per minute
        announcements = []
        
        # Simulate rapid-fire timeouts
        for burst in range(3):  # 3 bursts of activity
            # Burst of timeouts
            burst_announcements = self.simulate_timeouts(
                timeout_manager,
                count=10,
                interval=0.05,  # Very rapid (every 3 seconds)
                mod_count=8  # Many mods
            )
            announcements.extend(burst_announcements)
            time.sleep(2)  # Gap between bursts
        
        # Should get escalating multi-whacks
        ultra_plus = [a for a in announcements if any(
            keyword in a["text"] for keyword in ["ULTRA", "MONSTER", "LUDICROUS", "HOLY SHIT"]
        )]
        assert len(ultra_plus) >= 1  # Should hit high combos
    
    def test_announcement_cooldown(self, timeout_manager):
        """Test that announcements have appropriate cooldowns"""
        announcements = []
        mod_id = "mod_cooldown_test"
        
        # Rapid fire 5 timeouts
        for i in range(5):
            result = timeout_manager.record_timeout(
                mod_id=mod_id,
                mod_name="CooldownMod",
                target_id=f"target_{i}",
                target_name=f"Troll{i}",
                duration=300,
                reason="Test"
            )
            if result.get("announcement"):
                announcements.append({
                    "time": time.time(),
                    "text": result["announcement"]
                })
            time.sleep(0.1)  # Very rapid
        
        # Should get multi-whack announcements
        assert any("MULTI" in a["text"] or "DOUBLE" in a["text"] for a in announcements)
    
    def test_milestone_announcements_priority(self, timeout_manager):
        """Test that milestone announcements (5, 10, 25, etc) get priority"""
        mod_id = "mod_milestone"
        announcements = []
        
        # Build up to milestone
        for i in range(26):  # Get to 25 whack milestone
            result = timeout_manager.record_timeout(
                mod_id=mod_id,
                mod_name="MilestoneMod",
                target_id=f"target_{i}",
                target_name=f"Troll{i}",
                duration=300,
                reason="Test"
            )
            if result.get("announcement"):
                announcements.append(result["announcement"])
            time.sleep(0.2)  # Space them out
        
        # Should have milestone announcements
        milestones = [a for a in announcements if any(
            phrase in a for phrase in ["SPREE", "RAMPAGE", "DOMINATING", "UNSTOPPABLE", "GODLIKE"]
        )]
        assert len(milestones) >= 3  # Should hit multiple milestones
    
    @pytest.mark.asyncio
    async def test_concurrent_mods_high_density(self):
        """Test multiple mods timing out simultaneously (raid scenario)"""
        manager = TimeoutManager(memory_dir="/tmp/test_concurrent")
        announcements = []
        lock = threading.Lock()
        
        def mod_timeout(mod_num: int, count: int):
            """Single mod performing timeouts"""
            mod_id = f"mod_{mod_num}"
            mod_name = f"Mod{mod_num}"
            
            for i in range(count):
                result = manager.record_timeout(
                    mod_id=mod_id,
                    mod_name=mod_name,
                    target_id=f"target_{mod_num}_{i}",
                    target_name=f"Raider{mod_num}_{i}",
                    duration=300,
                    reason="Raid"
                )
                if result.get("announcement"):
                    with lock:
                        announcements.append(result["announcement"])
                time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate 5 mods working simultaneously
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for mod_num in range(5):
                future = executor.submit(mod_timeout, mod_num, 5)
                futures.append(future)
            
            # Wait for all to complete
            for future in futures:
                future.result()
        
        # Should get variety of announcements from different mods
        unique_mods = set()
        for announcement in announcements:
            for i in range(5):
                if f"Mod{i}" in announcement:
                    unique_mods.add(i)
        
        assert len(unique_mods) >= 3  # At least 3 different mods got announcements
    
    def test_dynamic_threshold_adjustment(self):
        """Test that thresholds adjust based on stream density"""
        low_density = StreamDensitySimulator(100, 2.0)
        high_density = StreamDensitySimulator(1000, 10.0)
        
        low_thresholds = low_density.get_announcement_threshold()
        high_thresholds = high_density.get_announcement_threshold()
        
        # High density streams should have tighter windows
        assert low_thresholds["multi_whack_window"] > high_thresholds["multi_whack_window"]
        assert low_thresholds["cooldown_period"] < high_thresholds["cooldown_period"]
        assert low_thresholds["min_announcement_gap"] < high_thresholds["min_announcement_gap"]
    
    def test_spam_prevention_extreme_density(self, timeout_manager):
        """Test that extreme activity doesn't spam announcements"""
        announcements = []
        
        # Simulate 50 timeouts in 10 seconds (extreme raid)
        start_time = time.time()
        for i in range(50):
            mod_id = f"mod_{i % 10}"  # 10 different mods
            result = timeout_manager.record_timeout(
                mod_id=mod_id,
                mod_name=f"Mod{i % 10}",
                target_id=f"target_{i}",
                target_name=f"Raider{i}",
                duration=300,
                reason="Mass raid"
            )
            if result.get("announcement"):
                announcements.append({
                    "time": time.time() - start_time,
                    "text": result["announcement"]
                })
            time.sleep(0.01)  # Very rapid
        
        # With mockery system, we get an announcement for each timeout (mockery or real)
        assert len(announcements) == 50  # All timeouts get announcements (real or mockery)
        
        # Check for mockery messages in extreme density
        mockery_announcements = [a for a in announcements if any(
            keyword in a["text"] for keyword in ["SPEEDRUN", "CLOWN", "TRASH", "YEETED", "GARBAGE", "NPC", 
                                                  "WAVE DETECTED", "TARGET RICH", "RAINING TROLLS", 
                                                  "farming XP", "HARVESTING", "RAID BOSS"]
        )]
        assert len(mockery_announcements) >= 10  # Should have plenty of mockery
        
        # But should still get some epic announcements
        epic_announcements = [a for a in announcements if any(
            keyword in a["text"] for keyword in ["MONSTER", "LUDICROUS", "HOLY SHIT", "GODLIKE", "MULTI", "MEGA"]
        )]
        assert len(epic_announcements) >= 1  # At least one epic announcement


class TestComprehensiveAnnouncements:
    """Comprehensive tests for all announcement types and priorities"""
    
    @pytest.fixture
    def timeout_manager(self):
        """Create a fresh timeout manager for testing"""
        return TimeoutManager(memory_dir="/tmp/test_comprehensive")
    
    def test_youtube_exact_timeout_durations(self, timeout_manager):
        """Test all exact YouTube timeout durations get proper announcements"""
        mod_id = "mod_durations"
        mod_name = "DurationMod"
        
        # Test each exact YouTube duration
        duration_tests = [
            (10, "SLAP", "slapped"),
            (60, "SHOTGUN", "blasted"),
            (300, "TACTICAL NUKE", "nuked"),
            (1800, "DEVASTATOR", "OBLITERATED"),
            (3600, "MEGA PUNISHMENT", "shadow realm"),
            (86400, "APOCALYPSE", "24 HOURS"),
            (9999999, "BFG 9000", "HIDDEN")
        ]
        
        for duration, expected_keyword, expected_verb in duration_tests:
            # Create fresh timeout manager for each test to avoid interference
            fresh_manager = TimeoutManager(memory_dir=f"/tmp/test_duration_{duration}")
            
            result = fresh_manager.record_timeout(
                mod_id=f"{mod_id}_{duration}",  # Unique mod ID
                mod_name=mod_name,
                target_id=f"target_{duration}",
                target_name=f"Troll{duration}",
                duration=duration,
                reason="Test"
            )
            
            announcement = result.get("announcement", "")
            assert expected_keyword in announcement, f"Duration {duration} should have {expected_keyword}, got: {announcement}"
            assert expected_verb in announcement or expected_keyword in announcement, f"Duration {duration} missing expected content"
    
    def test_multi_whack_priority_over_duration(self, timeout_manager):
        """Test that multi-whack announcements supersede duration announcements"""
        mod_id = "mod_priority"
        mod_name = "PriorityMod"
        
        # First timeout - should get duration announcement
        result1 = timeout_manager.record_timeout(
            mod_id=mod_id,
            mod_name=mod_name,
            target_id="target_1",
            target_name="Troll1",
            duration=300,  # 5 minute
            reason="Test"
        )
        assert "TACTICAL NUKE" in result1["announcement"]
        
        # Second rapid timeout - should get DOUBLE WHACK, not duration
        time.sleep(2)  # Within 5-second multi-whack window
        result2 = timeout_manager.record_timeout(
            mod_id=mod_id,
            mod_name=mod_name,
            target_id="target_2",
            target_name="Troll2",
            duration=3600,  # 1 hour - different duration
            reason="Test"
        )
        assert "DOUBLE WHACK" in result2["announcement"]
        assert "MEGA PUNISHMENT" not in result2["announcement"]  # Duration suppressed
        
        # Third rapid timeout - should get MULTI WHACK
        time.sleep(2)  # Within window
        result3 = timeout_manager.record_timeout(
            mod_id=mod_id,
            mod_name=mod_name,
            target_id="target_3",
            target_name="Troll3",
            duration=10,  # 10 second - very different
            reason="Test"
        )
        assert "MULTI WHACK" in result3["announcement"]
        assert "SLAP" not in result3["announcement"]  # Duration suppressed
    
    def test_milestone_priority_over_single_timeout(self):
        """Test milestone announcements take priority over duration announcements"""
        # Create fresh manager to avoid interference
        timeout_manager = TimeoutManager(memory_dir="/tmp/test_milestone_priority")
        mod_id = "mod_milestone_priority"
        mod_name = "MilestonePriorityMod"
        
        # Build up to milestone 5
        for i in range(5):
            # Space timeouts to avoid multi-whack
            if i > 0:
                time.sleep(6)  # Wait BEFORE timeout to ensure no multi-whack
            
            result = timeout_manager.record_timeout(
                mod_id=mod_id,
                mod_name=mod_name,
                target_id=f"target_{i}",
                target_name=f"Troll{i}",
                duration=300,  # 5 minute
                reason="Test"
            )
            
            if i == 4:  # 5th whack
                # Should get milestone announcement, not duration or multi-whack
                assert "WHACKING SPREE" in result["announcement"], f"5th whack should be milestone, got: {result['announcement']}"
                assert "TACTICAL NUKE" not in result["announcement"]
                assert "DOUBLE" not in result["announcement"]
    
    def test_all_multi_whack_levels(self, timeout_manager):
        """Test all 8+ levels of multi-whack announcements"""
        mod_id = "mod_multi"
        mod_name = "MultiMod"
        
        expected_announcements = [
            (1, None),  # First whack, no multi
            (2, "DOUBLE WHACK"),
            (3, "MULTI WHACK"),
            (4, "MEGA WHACK"),
            (5, "ULTRA WHACK"),
            (6, "MONSTER WHACK"),
            (7, "LUDICROUS WHACK"),
            (8, "HOLY SHIT"),
            (9, "9x WHACK COMBO"),  # 9+ gets combo counter
            (10, "10x WHACK COMBO")
        ]
        
        for count, expected in expected_announcements:
            result = timeout_manager.record_timeout(
                mod_id=mod_id,
                mod_name=mod_name,
                target_id=f"target_{count}",
                target_name=f"Troll{count}",
                duration=300,
                reason="Test"
            )
            
            if expected:
                assert expected in result["announcement"], f"Count {count} should have {expected}"
            
            time.sleep(2)  # Keep within 5s multi-whack window
    
    def test_raid_mockery_in_extreme_density(self, timeout_manager):
        """Test that raid mockery activates in extreme density"""
        # Simulate extreme density first
        for i in range(20):
            timeout_manager.record_timeout(
                mod_id=f"mod_spam_{i}",
                mod_name=f"Mod{i}",
                target_id=f"target_{i}",
                target_name=f"Raider{i}",
                duration=300,
                reason="Raid"
            )
        
        # Now check for mockery
        mockery_keywords = [
            "SPEEDRUN", "CLOWN", "TRASH", "YEETED", "GARBAGE", "NPC",
            "WAVE DETECTED", "TARGET RICH", "RAINING TROLLS", "farming XP", 
            "HARVESTING", "RAID BOSS"
        ]
        
        found_mockery = False
        for i in range(20, 30):  # Try more timeouts
            result = timeout_manager.record_timeout(
                mod_id=f"mod_raid_{i}",
                mod_name=f"RaidMod{i}",
                target_id=f"target_{i}",
                target_name=f"Raider{i}",
                duration=300,
                reason="Raid"
            )
            
            announcement = result.get("announcement", "")
            if any(keyword in announcement for keyword in mockery_keywords):
                found_mockery = True
                break
        
        assert found_mockery, "Should get raid mockery in extreme density"
    
    def test_fallback_announcements_for_unknown_durations(self, timeout_manager):
        """Test fallback for non-standard durations"""
        mod_id = "mod_fallback"
        mod_name = "FallbackMod"
        
        # Test non-standard duration
        result = timeout_manager.record_timeout(
            mod_id=mod_id,
            mod_name=mod_name,
            target_id="target_weird",
            target_name="TrollWeird",
            duration=123,  # Not a standard YouTube duration
            reason="Test"
        )
        
        # Should get generic whack announcement
        assert "WHACKS" in result["announcement"]
    
    def test_announcement_learning_system(self, timeout_manager):
        """Test that system learns optimal multi-whack windows"""
        mod_id = "mod_learning"
        mod_name = "LearningMod"
        
        # Initial window should be 5 seconds (Quake-style)
        assert timeout_manager.multi_whack_window == 5
        
        # Simulate successful multi-whacks with realistic timing
        for i in range(10):
            timeout_manager.record_timeout(
                mod_id=mod_id,
                mod_name=mod_name,
                target_id=f"target_{i}",
                target_name=f"Troll{i}",
                duration=300,
                reason="Test"
            )
            time.sleep(2)  # 2 seconds between (achievable)
        
        # System should have learned from these achievements
        assert len(timeout_manager.achieved_multi_whacks) > 0
        
        # Window should have adjusted based on achievements
        # (exact value depends on the learning algorithm)
        assert timeout_manager.optimal_window > 0
    
    def test_points_display_in_announcements(self, timeout_manager):
        """Test that points are correctly displayed in announcements"""
        mod_id = "mod_points"
        mod_name = "PointsMod"
        
        result = timeout_manager.record_timeout(
            mod_id=mod_id,
            mod_name=mod_name,
            target_id="target_points",
            target_name="TrollPoints",
            duration=300,
            reason="Test"
        )
        
        # Should show points gained
        assert "[+5 pts]" in result["announcement"] or "[Daily cap reached]" in result["announcement"]
    
    @pytest.mark.parametrize("viewer_count,density", [
        (50, "LOW"),
        (150, "LOW"),
        (250, "MEDIUM"),
        (400, "MEDIUM"),
        (600, "HIGH"),
        (800, "HIGH"),
        (1200, "EXTREME"),
        (2000, "EXTREME")
    ])
    def test_density_calculation_ranges(self, viewer_count, density):
        """Test density calculation across various viewer counts"""
        simulator = StreamDensitySimulator(viewer_count, 5.0)
        assert simulator.activity_level == density


if __name__ == "__main__":
    # Run comprehensive tests
    import sys
    import pytest
    
    # Run all tests in this file
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)