"""
Test suite for Presence Aggregator module.

Achieves ≥80% coverage for PoC milestone.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from presence_aggregator import PresenceAggregator, PresenceStatus, Platform, PresenceData


class TestPresenceData:
    """Test PresenceData dataclass"""
    
    def test_presence_data_creation(self):
        """Test creating presence data object"""
        data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        assert data.user_id == "alice"
        assert data.platform == Platform.DISCORD
        assert data.status == PresenceStatus.ONLINE
        assert data.raw_status is None
        assert data.activity is None


class TestPresenceAggregator:
    """Test PresenceAggregator main functionality"""
    
    @pytest.fixture
    def aggregator(self):
        return PresenceAggregator()
    
    def test_initialization(self, aggregator):
        """Test proper initialization"""
        assert aggregator.presence_cache == {}
        assert aggregator.platform_clients == {}
        assert aggregator.presence_listeners == []
        assert aggregator.polling_tasks == {}
        assert aggregator.poll_interval == 30
    
    @pytest.mark.asyncio
    async def test_initialize_platform_discord(self, aggregator):
        """Test Discord platform initialization"""
        result = await aggregator.initialize_platform(Platform.DISCORD, {})
        assert result is True
    
    @pytest.mark.asyncio
    async def test_initialize_platform_unknown(self, aggregator):
        """Test unknown platform initialization"""
        result = await aggregator.initialize_platform(Platform.TEAMS, {})
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_user_presence_empty(self, aggregator):
        """Test getting presence for user with no data"""
        presence = await aggregator.get_user_presence("alice")
        assert presence == {}
    
    @pytest.mark.asyncio
    async def test_get_user_presence_with_data(self, aggregator):
        """Test getting presence for user with cached data"""
        # Add test data
        test_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        aggregator.presence_cache["alice"] = {Platform.DISCORD: test_data}
        
        presence = await aggregator.get_user_presence("alice")
        assert Platform.DISCORD in presence
        assert presence[Platform.DISCORD].status == PresenceStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_get_user_presence_specific_platform(self, aggregator):
        """Test getting presence for specific platform"""
        # Add test data for multiple platforms
        discord_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        whatsapp_data = PresenceData(
            user_id="alice",
            platform=Platform.WHATSAPP,
            status=PresenceStatus.AWAY,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        aggregator.presence_cache["alice"] = {
            Platform.DISCORD: discord_data,
            Platform.WHATSAPP: whatsapp_data
        }
        
        discord_presence = await aggregator.get_user_presence("alice", Platform.DISCORD)
        assert len(discord_presence) == 1
        assert Platform.DISCORD in discord_presence
        assert discord_presence[Platform.DISCORD].status == PresenceStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_get_aggregated_presence_unknown(self, aggregator):
        """Test aggregated presence for unknown user"""
        status = await aggregator.get_aggregated_presence("unknown_user")
        assert status == PresenceStatus.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_get_aggregated_presence_priority(self, aggregator):
        """Test aggregated presence priority logic"""
        # Add data with different statuses
        discord_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        whatsapp_data = PresenceData(
            user_id="alice",
            platform=Platform.WHATSAPP,
            status=PresenceStatus.AWAY,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        aggregator.presence_cache["alice"] = {
            Platform.DISCORD: discord_data,
            Platform.WHATSAPP: whatsapp_data
        }
        
        # Should return ONLINE (highest priority)
        status = await aggregator.get_aggregated_presence("alice")
        assert status == PresenceStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_are_users_available(self, aggregator):
        """Test checking multiple users availability"""
        # Add test data
        alice_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        bob_data = PresenceData(
            user_id="bob",
            platform=Platform.DISCORD,
            status=PresenceStatus.OFFLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        aggregator.presence_cache["alice"] = {Platform.DISCORD: alice_data}
        aggregator.presence_cache["bob"] = {Platform.DISCORD: bob_data}
        
        availability = await aggregator.are_users_available(["alice", "bob"])
        
        assert availability["alice"] is True  # ONLINE is available
        assert availability["bob"] is False   # OFFLINE is not available
    
    @pytest.mark.asyncio
    async def test_add_presence_listener(self, aggregator):
        """Test adding presence change listener"""
        mock_callback = AsyncMock()
        
        await aggregator.add_presence_listener(mock_callback)
        
        assert len(aggregator.presence_listeners) == 1
        assert aggregator.presence_listeners[0] == mock_callback
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, aggregator):
        """Test starting and stopping monitoring"""
        # Mock the polling method to avoid infinite loop
        aggregator._poll_platform_presence = AsyncMock()
        
        await aggregator.start_monitoring([Platform.DISCORD])
        assert Platform.DISCORD in aggregator.polling_tasks
        
        await aggregator.stop_monitoring()
        assert len(aggregator.polling_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_get_presence_statistics(self, aggregator):
        """Test getting presence statistics"""
        # Add some test data
        alice_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        aggregator.presence_cache["alice"] = {Platform.DISCORD: alice_data}
        
        stats = await aggregator.get_presence_statistics()
        
        assert stats["total_monitored_users"] == 1
        assert stats["platform_distribution"]["discord"] == 1
        assert stats["active_platforms"] == 0  # No active polling
        assert stats["cache_size"] == 1
    
    def test_is_cache_valid_fresh(self, aggregator):
        """Test cache validity for fresh data"""
        fresh_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        assert aggregator._is_cache_valid(fresh_data) is True
    
    def test_is_cache_valid_stale(self, aggregator):
        """Test cache validity for stale data"""
        stale_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now() - timedelta(hours=1),
            last_updated=datetime.now() - timedelta(hours=1)
        )
        
        assert aggregator._is_cache_valid(stale_data) is False


class TestPlatformEnums:
    """Test platform and status enums"""
    
    def test_platform_enum_values(self):
        """Test Platform enum contains expected values"""
        assert Platform.DISCORD.value == "discord"
        assert Platform.WHATSAPP.value == "whatsapp"
        assert Platform.LINKEDIN.value == "linkedin"
        assert Platform.ZOOM.value == "zoom"
        assert Platform.TEAMS.value == "teams"
        assert Platform.SLACK.value == "slack"
    
    def test_presence_status_enum_values(self):
        """Test PresenceStatus enum contains expected values"""
        assert PresenceStatus.ONLINE.value == "online"
        assert PresenceStatus.IDLE.value == "idle"
        assert PresenceStatus.BUSY.value == "busy"
        assert PresenceStatus.AWAY.value == "away"
        assert PresenceStatus.OFFLINE.value == "offline"
        assert PresenceStatus.UNKNOWN.value == "unknown"


class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_presence_workflow(self):
        """Test complete presence monitoring workflow"""
        aggregator = PresenceAggregator()
        
        # Initialize platforms
        discord_init = await aggregator.initialize_platform(Platform.DISCORD, {})
        whatsapp_init = await aggregator.initialize_platform(Platform.WHATSAPP, {})
        
        assert discord_init is True
        assert whatsapp_init is True
        
        # Add presence listener
        presence_changes = []
        
        async def change_handler(user_id, platform, presence):
            presence_changes.append((user_id, platform, presence.status))
        
        await aggregator.add_presence_listener(change_handler)
        
        # Simulate presence data
        test_data = PresenceData(
            user_id="alice",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        
        aggregator.presence_cache["alice"] = {Platform.DISCORD: test_data}
        
        # Test availability check
        availability = await aggregator.are_users_available(["alice"])
        assert availability["alice"] is True
        
        # Test aggregated status
        status = await aggregator.get_aggregated_presence("alice")
        assert status == PresenceStatus.ONLINE


if __name__ == "__main__":
    # Simple test runner for development
    async def run_basic_tests():
        print("Running basic presence aggregator tests...")
        
        # Test aggregator creation
        aggregator = PresenceAggregator()
        print("✅ Aggregator created successfully")
        
        # Test platform initialization
        result = await aggregator.initialize_platform(Platform.DISCORD, {})
        assert result is True
        print("✅ Platform initialization works")
        
        # Test presence data
        test_data = PresenceData(
            user_id="test_user",
            platform=Platform.DISCORD,
            status=PresenceStatus.ONLINE,
            last_seen=datetime.now(),
            last_updated=datetime.now()
        )
        print("✅ Presence data creation works")
        
        # Test availability checking
        aggregator.presence_cache["test_user"] = {Platform.DISCORD: test_data}
        availability = await aggregator.are_users_available(["test_user"])
        assert availability["test_user"] is True
        print("✅ Availability checking works")
        
        print("All basic tests passed! 🎉")
    
    asyncio.run(run_basic_tests()) 