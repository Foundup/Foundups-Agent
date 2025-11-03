"""
MCP Server for Whack-a-MAGAT Gaming System
WSP-Compliant: WSP 48 (Recursive Improvement), WSP 80 (Cube DAE), WSP 17 (Pattern Registry)

Real-time timeout tracking, leaderboards, and combo multipliers via MCP.
Provides instant updates to all connected clients without buffering delays.

WSP 17 Pattern Registry: Gaming MCP Server Pattern
- Real-time game state synchronization
- Instant leaderboard updates
- Combo tracking across platforms
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from collections import deque
from pathlib import Path
import time

# MCP Server interfaces (placeholder until MCP package installed)
try:
    from mcp import Server, Tool, Resource
except ImportError:
    class Server:
        def __init__(self, name: str):
            self.name = name
            self.tools = {}
            self.resources = {}
    
    class Tool:
        def __init__(self, name: str, description: str, parameters: Dict):
            self.name = name
            self.description = description
            self.parameters = parameters
    
    class Resource:
        def __init__(self, name: str, uri: str, description: str):
            self.name = name
            self.uri = uri
            self.description = description

logger = logging.getLogger(__name__)


@dataclass
class WhackEvent:
    """Real-time whack event for MCP broadcast"""
    timestamp: float
    moderator_name: str
    moderator_id: str
    target_name: str
    target_id: str
    points: int
    combo_multiplier: int = 1
    is_multi_whack: bool = False
    total_whacks: int = 1


@dataclass
class LeaderboardEntry:
    """Leaderboard entry for MCP transmission"""
    user_id: str
    user_name: str
    total_points: int
    total_whacks: int
    best_combo: int
    rank: int
    last_whack: Optional[float] = None


@dataclass
class ComboStatus:
    """Active combo tracking"""
    moderator_id: str
    streak: int = 0
    multiplier: int = 1
    last_target: Optional[str] = None
    last_timestamp: float = field(default_factory=time.time)
    different_targets: Set[str] = field(default_factory=set)


class MCPWhackServer(Server):
    """
    MCP Server for Whack-a-MAGAT Real-time Gaming
    
    Eliminates buffering issues by providing instant updates via MCP.
    Tracks combos, multi-whacks, and leaderboards in real-time.
    
    WSP 48: Enhanced with modern gaming integration
    WSP 80: Spawns gaming DAEs for distributed tracking
    """
    
    def __init__(self, memory_dir: str = "memory/whack"):
        """Initialize MCP Whack Server"""
        super().__init__("whack-a-magat-mcp")
        
        # Game state
        self.leaderboard: Dict[str, Dict] = {}
        self.recent_whacks: deque = deque(maxlen=100)
        self.active_combos: Dict[str, ComboStatus] = {}
        
        # Multi-whack detection
        self.whack_window = 10.0  # 10 second window
        self.recent_timeouts: deque = deque(maxlen=50)
        
        # Connected clients (for real-time updates)
        self.connected_clients: Set[str] = set()
        self.event_subscribers: Dict[str, List[str]] = {
            "whack": [],
            "combo": [],
            "leaderboard": [],
            "magadoom": []
        }
        
        # Persistence
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._load_state()
        
        # Register MCP tools and resources
        self._register_tools()
        self._register_resources()
        
        # Background tasks
        self.tasks = []
        
        logger.info(f"[GAME] MCP Whack Server initialized: {self.name}")
    
    def _register_tools(self):
        """Register MCP tools for whack operations"""
        
        # Tool: Record a whack (timeout)
        self.tools["record_whack"] = Tool(
            name="record_whack",
            description="Record a timeout/whack event in real-time",
            parameters={
                "type": "object",
                "properties": {
                    "moderator_name": {"type": "string"},
                    "moderator_id": {"type": "string"},
                    "target_name": {"type": "string"},
                    "target_id": {"type": "string"},
                    "timestamp": {"type": "number", "description": "Event timestamp"},
                    "duration": {"type": "integer", "description": "Timeout duration in seconds"}
                },
                "required": ["moderator_name", "moderator_id", "target_name", "target_id"]
            }
        )
        
        # Tool: Get live leaderboard
        self.tools["get_leaderboard"] = Tool(
            name="get_leaderboard",
            description="Get real-time leaderboard",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of entries (default 10)"}
                }
            }
        )
        
        # Tool: Get user stats
        self.tools["get_user_stats"] = Tool(
            name="get_user_stats",
            description="Get specific user's whack statistics",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to lookup"}
                },
                "required": ["user_id"]
            }
        )
        
        # Tool: Check combo status
        self.tools["check_combo"] = Tool(
            name="check_combo",
            description="Check active combo for a moderator",
            parameters={
                "type": "object",
                "properties": {
                    "moderator_id": {"type": "string"}
                },
                "required": ["moderator_id"]
            }
        )
        
        # Tool: Subscribe to events
        self.tools["subscribe_events"] = Tool(
            name="subscribe_events",
            description="Subscribe to real-time whack events",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "events": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event types: whack, combo, leaderboard, magadoom"
                    }
                },
                "required": ["client_id", "events"]
            }
        )
        
        # Tool: Announce MAGADOOM
        self.tools["announce_magadoom"] = Tool(
            name="announce_magadoom",
            description="Trigger MAGADOOM announcement",
            parameters={
                "type": "object",
                "properties": {
                    "moderator_name": {"type": "string"},
                    "whack_count": {"type": "integer"},
                    "combo_multiplier": {"type": "integer"}
                },
                "required": ["moderator_name", "whack_count"]
            }
        )
    
    def _register_resources(self):
        """Register MCP resources for game data access"""
        
        self.resources["leaderboard_live"] = Resource(
            name="leaderboard_live",
            uri="whack://leaderboard/live",
            description="Live leaderboard updates"
        )
        
        self.resources["combo_tracker"] = Resource(
            name="combo_tracker",
            uri="whack://combos/active",
            description="Active combo tracking"
        )
        
        self.resources["recent_whacks"] = Resource(
            name="recent_whacks",
            uri="whack://events/recent",
            description="Recent whack events stream"
        )
        
        self.resources["stats_dashboard"] = Resource(
            name="stats_dashboard",
            uri="whack://stats/dashboard",
            description="Complete gaming statistics"
        )
    
    async def handle_tool_call(self, tool_name: str, parameters: Dict) -> Dict:
        """Handle MCP tool calls"""
        try:
            if tool_name == "record_whack":
                return await self._handle_record_whack(parameters)
            elif tool_name == "get_leaderboard":
                return await self._handle_get_leaderboard(parameters)
            elif tool_name == "get_user_stats":
                return await self._handle_get_user_stats(parameters)
            elif tool_name == "check_combo":
                return await self._handle_check_combo(parameters)
            elif tool_name == "subscribe_events":
                return await self._handle_subscribe_events(parameters)
            elif tool_name == "announce_magadoom":
                return await self._handle_announce_magadoom(parameters)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"MCP tool error: {e}")
            return {"error": str(e)}
    
    async def _handle_record_whack(self, params: Dict) -> Dict:
        """Record a whack event and calculate points/combos"""
        timestamp = params.get("timestamp", time.time())
        moderator_id = params["moderator_id"]
        target_id = params["target_id"]
        
        # Check for multi-whack
        is_multi_whack, whack_count = self._detect_multi_whack(
            moderator_id, timestamp
        )
        
        # Check for combo
        combo_multiplier = self._calculate_combo(
            moderator_id, target_id, timestamp
        )
        
        # Calculate points
        base_points = 10
        points = base_points * combo_multiplier
        if is_multi_whack:
            points += (whack_count - 1) * 50  # Bonus for multi-whack
        
        # Create event
        event = WhackEvent(
            timestamp=timestamp,
            moderator_name=params["moderator_name"],
            moderator_id=moderator_id,
            target_name=params["target_name"],
            target_id=target_id,
            points=points,
            combo_multiplier=combo_multiplier,
            is_multi_whack=is_multi_whack,
            total_whacks=whack_count if is_multi_whack else 1
        )
        
        # Update leaderboard
        self._update_leaderboard(event)
        
        # Store event
        self.recent_whacks.append(event)
        self.recent_timeouts.append({
            "moderator_id": moderator_id,
            "target_id": target_id,
            "timestamp": timestamp
        })
        
        # Broadcast to subscribers (INSTANT, no buffering!)
        await self._broadcast_event("whack", asdict(event))
        
        # Check for MAGADOOM
        if is_multi_whack and whack_count >= 3:
            await self._trigger_magadoom(event, whack_count)
        
        # Save state
        self._save_state()
        
        return {
            "success": True,
            "points": points,
            "combo_multiplier": combo_multiplier,
            "is_multi_whack": is_multi_whack,
            "total_whacks": whack_count if is_multi_whack else 1,
            "leaderboard_rank": self._get_user_rank(moderator_id)
        }
    
    def _detect_multi_whack(self, moderator_id: str, timestamp: float) -> tuple[bool, int]:
        """Detect multi-whack within window"""
        window_start = timestamp - self.whack_window
        
        # Count timeouts by this moderator in window
        # BUT exclude same target (anti-gaming)
        recent_targets = set()
        whack_count = 1  # Current whack
        
        for timeout in reversed(self.recent_timeouts):
            if timeout["timestamp"] < window_start:
                break
            if timeout["moderator_id"] == moderator_id:
                # Only count different targets
                if timeout["target_id"] not in recent_targets:
                    recent_targets.add(timeout["target_id"])
                    whack_count += 1
        
        is_multi = whack_count >= 2
        return is_multi, whack_count
    
    def _calculate_combo(self, moderator_id: str, target_id: str, timestamp: float) -> int:
        """Calculate combo multiplier for consecutive different targets"""
        
        # Get or create combo status
        if moderator_id not in self.active_combos:
            self.active_combos[moderator_id] = ComboStatus(moderator_id=moderator_id)
        
        combo = self.active_combos[moderator_id]
        
        # Check if combo expired (30 seconds)
        if timestamp - combo.last_timestamp > 30:
            # Reset combo
            combo.streak = 0
            combo.different_targets.clear()
            combo.multiplier = 1
        
        # Check if different target (required for combo)
        if target_id != combo.last_target:
            combo.different_targets.add(target_id)
            combo.streak += 1
            
            # Calculate multiplier (x2, x3, x4, x5 max)
            if combo.streak >= 5:
                combo.multiplier = 5
            elif combo.streak >= 4:
                combo.multiplier = 4
            elif combo.streak >= 3:
                combo.multiplier = 3
            elif combo.streak >= 2:
                combo.multiplier = 2
            else:
                combo.multiplier = 1
        else:
            # Same target, no combo bonus (anti-gaming)
            combo.multiplier = 1
        
        # Update combo state
        combo.last_target = target_id
        combo.last_timestamp = timestamp
        
        return combo.multiplier
    
    def _update_leaderboard(self, event: WhackEvent):
        """Update leaderboard with new whack"""
        user_id = event.moderator_id
        
        if user_id not in self.leaderboard:
            self.leaderboard[user_id] = {
                "user_name": event.moderator_name,
                "total_points": 0,
                "total_whacks": 0,
                "best_combo": 0,
                "last_whack": None
            }
        
        entry = self.leaderboard[user_id]
        entry["total_points"] += event.points
        entry["total_whacks"] += event.total_whacks
        entry["best_combo"] = max(entry["best_combo"], event.combo_multiplier)
        entry["last_whack"] = event.timestamp
        entry["user_name"] = event.moderator_name  # Update name in case it changed
    
    def _get_user_rank(self, user_id: str) -> int:
        """Get user's current rank"""
        if user_id not in self.leaderboard:
            return -1
        
        sorted_users = sorted(
            self.leaderboard.items(),
            key=lambda x: x[1]["total_points"],
            reverse=True
        )
        
        for rank, (uid, _) in enumerate(sorted_users, 1):
            if uid == user_id:
                return rank
        
        return -1
    
    async def _handle_get_leaderboard(self, params: Dict) -> Dict:
        """Get current leaderboard"""
        limit = params.get("limit", 10)
        
        sorted_users = sorted(
            self.leaderboard.items(),
            key=lambda x: x[1]["total_points"],
            reverse=True
        )[:limit]
        
        entries = []
        for rank, (user_id, data) in enumerate(sorted_users, 1):
            entry = LeaderboardEntry(
                user_id=user_id,
                user_name=data["user_name"],
                total_points=data["total_points"],
                total_whacks=data["total_whacks"],
                best_combo=data["best_combo"],
                rank=rank,
                last_whack=data["last_whack"]
            )
            entries.append(asdict(entry))
        
        return {
            "leaderboard": entries,
            "total_players": len(self.leaderboard)
        }
    
    async def _handle_get_user_stats(self, params: Dict) -> Dict:
        """Get specific user statistics"""
        user_id = params["user_id"]
        
        if user_id not in self.leaderboard:
            return {"error": "User not found"}
        
        data = self.leaderboard[user_id]
        rank = self._get_user_rank(user_id)
        
        return {
            "user_id": user_id,
            "user_name": data["user_name"],
            "total_points": data["total_points"],
            "total_whacks": data["total_whacks"],
            "best_combo": data["best_combo"],
            "rank": rank,
            "last_whack": data["last_whack"],
            "average_points": data["total_points"] / max(data["total_whacks"], 1)
        }
    
    async def _handle_check_combo(self, params: Dict) -> Dict:
        """Check active combo status"""
        moderator_id = params["moderator_id"]
        
        if moderator_id not in self.active_combos:
            return {
                "active": False,
                "streak": 0,
                "multiplier": 1
            }
        
        combo = self.active_combos[moderator_id]
        now = time.time()
        
        # Check if expired
        if now - combo.last_timestamp > 30:
            return {
                "active": False,
                "streak": 0,
                "multiplier": 1,
                "expired": True
            }
        
        return {
            "active": True,
            "streak": combo.streak,
            "multiplier": combo.multiplier,
            "different_targets": len(combo.different_targets),
            "time_remaining": 30 - (now - combo.last_timestamp)
        }
    
    async def _handle_subscribe_events(self, params: Dict) -> Dict:
        """Subscribe client to event streams"""
        client_id = params["client_id"]
        events = params["events"]
        
        self.connected_clients.add(client_id)
        
        for event_type in events:
            if event_type in self.event_subscribers:
                if client_id not in self.event_subscribers[event_type]:
                    self.event_subscribers[event_type].append(client_id)
        
        return {
            "subscribed": True,
            "client_id": client_id,
            "events": events,
            "message": f"Subscribed to {len(events)} event types"
        }
    
    async def _handle_announce_magadoom(self, params: Dict) -> Dict:
        """Trigger MAGADOOM announcement"""
        announcement = {
            "type": "MAGADOOM",
            "moderator_name": params["moderator_name"],
            "whack_count": params["whack_count"],
            "combo_multiplier": params.get("combo_multiplier", 1),
            "timestamp": time.time(),
            "message": f"[U+1F525] MAGADOOM! {params['moderator_name']} just whacked {params['whack_count']} MAGAts!"
        }
        
        # Broadcast immediately (no buffering!)
        await self._broadcast_event("magadoom", announcement)
        
        return {
            "announced": True,
            "broadcast_to": len(self.event_subscribers["magadoom"])
        }
    
    async def _trigger_magadoom(self, event: WhackEvent, whack_count: int):
        """Auto-trigger MAGADOOM for multi-whacks"""
        await self._handle_announce_magadoom({
            "moderator_name": event.moderator_name,
            "whack_count": whack_count,
            "combo_multiplier": event.combo_multiplier
        })
    
    async def _broadcast_event(self, event_type: str, data: Dict):
        """
        Broadcast event to all subscribers INSTANTLY
        No buffering, no delays - real-time via MCP
        """
        subscribers = self.event_subscribers.get(event_type, [])
        
        for client_id in subscribers:
            # In real MCP, this would push to client immediately
            logger.info(f"[U+1F4E2] MCP Broadcast [{event_type}] to {client_id}: {data.get('message', 'Event')}")
            
            # WSP 21: Create envelope for DAE communication
            envelope = {
                "version": "WSP21-1.0",
                "timestamp": datetime.now().isoformat(),
                "source": "MCP-WhackServer",
                "target": client_id,
                "protocol": f"whack-{event_type}",
                "data": data,
                "coherence": 0.618
            }
            
            # Here we would send via MCP connection
            # For now, just log the instant delivery
    
    async def handle_resource_read(self, resource_name: str) -> Any:
        """Handle MCP resource read requests"""
        if resource_name == "leaderboard_live":
            return await self._handle_get_leaderboard({"limit": 10})
        
        elif resource_name == "combo_tracker":
            active = []
            for mod_id, combo in self.active_combos.items():
                if time.time() - combo.last_timestamp < 30:
                    active.append({
                        "moderator_id": mod_id,
                        "streak": combo.streak,
                        "multiplier": combo.multiplier
                    })
            return {"active_combos": active}
        
        elif resource_name == "recent_whacks":
            return {"events": [asdict(e) for e in list(self.recent_whacks)[-20:]]}
        
        elif resource_name == "stats_dashboard":
            return {
                "total_whacks": sum(u["total_whacks"] for u in self.leaderboard.values()),
                "total_points": sum(u["total_points"] for u in self.leaderboard.values()),
                "active_players": len(self.leaderboard),
                "active_combos": len([c for c in self.active_combos.values() 
                                     if time.time() - c.last_timestamp < 30])
            }
        
        else:
            return {"error": f"Unknown resource: {resource_name}"}
    
    def _save_state(self):
        """Save game state to disk"""
        state_file = self.memory_dir / "whack_state.json"
        state = {
            "leaderboard": self.leaderboard,
            "recent_whacks": [asdict(w) for w in list(self.recent_whacks)[-50:]],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _load_state(self):
        """Load game state from disk"""
        state_file = self.memory_dir / "whack_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.leaderboard = state.get("leaderboard", {})
                    logger.info(f"[U+1F4C2] Loaded state with {len(self.leaderboard)} players")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
    
    def get_server_info(self) -> Dict:
        """Get MCP server information"""
        return {
            "name": self.name,
            "version": "1.0.0",
            "protocol": "MCP-1.0",
            "wsp_compliance": ["WSP 48", "WSP 80", "WSP 17"],
            "features": [
                "Real-time whack tracking",
                "Instant MAGADOOM announcements",
                "Live leaderboard updates",
                "Combo multiplier tracking",
                "Anti-gaming protection"
            ],
            "tools": list(self.tools.keys()),
            "resources": list(self.resources.keys()),
            "connected_clients": len(self.connected_clients),
            "active_players": len(self.leaderboard),
            "status": "operational"
        }


async def main():
    """Run MCP Whack Server standalone for testing"""
    server = MCPWhackServer()
    
    logger.info(f"[GAME] MCP Whack Server started: {server.get_server_info()}")
    
    # Simulate some events for testing
    test_events = [
        {
            "moderator_name": "UnDaoDu",
            "moderator_id": "mod_1",
            "target_name": "MAGA_Troll_1",
            "target_id": "target_1"
        },
        {
            "moderator_name": "UnDaoDu",
            "moderator_id": "mod_1",
            "target_name": "MAGA_Troll_2",
            "target_id": "target_2"
        },
        {
            "moderator_name": "UnDaoDu",
            "moderator_id": "mod_1",
            "target_name": "MAGA_Troll_3",
            "target_id": "target_3"
        }
    ]
    
    # Subscribe a test client
    await server.handle_tool_call("subscribe_events", {
        "client_id": "test_client",
        "events": ["whack", "combo", "magadoom"]
    })
    
    # Process test events
    for i, event in enumerate(test_events):
        event["timestamp"] = time.time() + i * 2
        result = await server.handle_tool_call("record_whack", event)
        print(f"Whack result: {result}")
        await asyncio.sleep(1)
    
    # Get leaderboard
    leaderboard = await server.handle_tool_call("get_leaderboard", {"limit": 5})
    print(f"\nLeaderboard: {json.dumps(leaderboard, indent=2)}")
    
    print("\n[GAME] MCP Whack Server running - press Ctrl+C to stop")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down MCP Whack Server")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())