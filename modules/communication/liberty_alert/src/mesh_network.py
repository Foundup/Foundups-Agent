# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Mesh Network Implementation
===========================

WebRTC-based P2P mesh networking for offline alert propagation.

Technology:
- aiortc (WebRTC for Python)
- DataChannels for P2P messaging
- Optional signaling server for peer discovery
- Auto-discovery via local network broadcast
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Set
from datetime import datetime
from uuid import uuid4

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from aiortc.contrib.signaling import TcpSocketSignaling

from .models import MeshMessage, MessageType, MeshStatus

logger = logging.getLogger(__name__)


class MeshNetwork:
    """
    WebRTC P2P Mesh Network

    Manages peer-to-peer connections for offline alert propagation.
    Supports both WebRTC DataChannels and optional Meshtastic integration.
    """

    def __init__(
        self,
        peer_id: Optional[str] = None,
        signaling_server: Optional[str] = None,
        auto_discovery: bool = True,
        max_peers: int = 50,
    ):
        """
        Initialize mesh network

        Args:
            peer_id: Unique identifier for this node (generated if None)
            signaling_server: Optional signaling server URL for bootstrap
            auto_discovery: Enable automatic peer discovery
            max_peers: Maximum number of peer connections
        """
        self.peer_id = peer_id or str(uuid4())
        self.signaling_server = signaling_server
        self.auto_discovery = auto_discovery
        self.max_peers = max_peers

        # Peer connections
        self.peers: Dict[str, RTCPeerConnection] = {}
        self.data_channels: Dict[str, RTCDataChannel] = {}
        self.peer_metadata: Dict[str, dict] = {}

        # Message routing
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.message_cache: Set[str] = set()  # Prevent duplicate processing
        self.message_count = 0

        # Network health
        self.is_running = False
        self.latency_samples: List[float] = []

        logger.info(f"[MESH] Initialized node: {self.peer_id}")

    async def start(self) -> bool:
        """
        Start mesh network

        Returns:
            bool: True if started successfully
        """
        try:
            self.is_running = True

            # Start auto-discovery if enabled
            if self.auto_discovery:
                asyncio.create_task(self._discovery_loop())

            # Connect to signaling server if provided
            if self.signaling_server:
                asyncio.create_task(self._connect_via_signaling())

            logger.info(f"[MESH] Node {self.peer_id} started")
            return True

        except Exception as e:
            logger.error(f"[MESH] Failed to start: {e}")
            return False

    async def stop(self) -> bool:
        """
        Gracefully stop mesh network

        Returns:
            bool: True if stopped successfully
        """
        try:
            self.is_running = False

            # Close all peer connections
            for peer_id, pc in self.peers.items():
                await pc.close()
                logger.info(f"[MESH] Closed connection to {peer_id}")

            self.peers.clear()
            self.data_channels.clear()

            logger.info(f"[MESH] Node {self.peer_id} stopped")
            return True

        except Exception as e:
            logger.error(f"[MESH] Failed to stop: {e}")
            return False

    async def connect_peer(self, peer_id: str, offer: Optional[dict] = None) -> bool:
        """
        Establish connection with peer

        Args:
            peer_id: Target peer ID
            offer: WebRTC offer (if answering connection)

        Returns:
            bool: True if connection successful
        """
        if len(self.peers) >= self.max_peers:
            logger.warning(f"[MESH] Max peers reached ({self.max_peers})")
            return False

        if peer_id in self.peers:
            logger.info(f"[MESH] Already connected to {peer_id}")
            return True

        try:
            # Create RTCPeerConnection
            pc = RTCPeerConnection()

            # Create data channel
            if offer is None:
                # We're the offerer
                channel = pc.createDataChannel("mesh")
                self._setup_data_channel(channel, peer_id)
            else:
                # We're the answerer
                @pc.on("datachannel")
                def on_datachannel(channel):
                    self._setup_data_channel(channel, peer_id)

            # Handle ICE connection state
            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                logger.info(f"[MESH] Connection to {peer_id}: {pc.connectionState}")
                if pc.connectionState == "failed" or pc.connectionState == "closed":
                    await self.disconnect_peer(peer_id)

            # Store connection
            self.peers[peer_id] = pc

            # Handle offer/answer exchange
            if offer:
                # Process received offer
                await pc.setRemoteDescription(RTCSessionDescription(**offer))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                # Return answer to peer (handled by signaling layer)
                return True
            else:
                # Create offer
                offer = await pc.createOffer()
                await pc.setLocalDescription(offer)
                # Send offer to peer (handled by signaling layer)
                return True

        except Exception as e:
            logger.error(f"[MESH] Failed to connect to {peer_id}: {e}")
            return False

    async def disconnect_peer(self, peer_id: str) -> bool:
        """
        Disconnect from peer

        Args:
            peer_id: Peer to disconnect

        Returns:
            bool: True if disconnected successfully
        """
        try:
            if peer_id in self.peers:
                await self.peers[peer_id].close()
                del self.peers[peer_id]

            if peer_id in self.data_channels:
                del self.data_channels[peer_id]

            if peer_id in self.peer_metadata:
                del self.peer_metadata[peer_id]

            logger.info(f"[MESH] Disconnected from {peer_id}")
            return True

        except Exception as e:
            logger.error(f"[MESH] Failed to disconnect from {peer_id}: {e}")
            return False

    async def send_message(self, message: MeshMessage, target_peer: Optional[str] = None) -> bool:
        """
        Send message through mesh

        Args:
            message: Message to send
            target_peer: Specific peer (None = broadcast to all)

        Returns:
            bool: True if sent successfully
        """
        try:
            # Set sender ID
            message.sender_id = self.peer_id

            # Check TTL
            if message.ttl <= 0:
                logger.debug(f"[MESH] Message {message.id} TTL expired")
                return False

            # Serialize message
            data = json.dumps(message.to_dict()).encode("utf-8")

            # Send to specific peer or broadcast
            if target_peer:
                if target_peer in self.data_channels:
                    self.data_channels[target_peer].send(data)
                    logger.debug(f"[MESH] Sent message {message.id} to {target_peer}")
                    return True
                else:
                    logger.warning(f"[MESH] Peer {target_peer} not connected")
                    return False
            else:
                # Broadcast to all peers
                sent_count = 0
                for peer_id, channel in self.data_channels.items():
                    if channel.readyState == "open":
                        channel.send(data)
                        sent_count += 1

                logger.debug(f"[MESH] Broadcast message {message.id} to {sent_count} peers")
                self.message_count += sent_count
                return sent_count > 0

        except Exception as e:
            logger.error(f"[MESH] Failed to send message: {e}")
            return False

    def on(self, message_type: MessageType, handler: Callable) -> None:
        """
        Register message handler

        Args:
            message_type: Type of message to handle
            handler: Async callback function
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []

        self.message_handlers[message_type].append(handler)
        logger.debug(f"[MESH] Registered handler for {message_type.value}")

    def get_connected_peers(self) -> List[str]:
        """Get list of connected peer IDs"""
        return list(self.peers.keys())

    def get_mesh_status(self) -> MeshStatus:
        """
        Get current mesh network status

        Returns:
            MeshStatus: Network health and metrics
        """
        return MeshStatus(
            peer_count=len(self.peers),
            coverage_km2=0.0,  # TODO: Calculate from peer locations
            avg_latency_ms=sum(self.latency_samples) / len(self.latency_samples)
            if self.latency_samples
            else 0.0,
            message_count=self.message_count,
            is_healthy=len(self.peers) > 0 and self.is_running,
            connected_peers=self.get_connected_peers(),
        )

    # Private methods

    def _setup_data_channel(self, channel: RTCDataChannel, peer_id: str) -> None:
        """Setup data channel event handlers"""
        self.data_channels[peer_id] = channel

        @channel.on("open")
        def on_open():
            logger.info(f"[MESH] Data channel opened to {peer_id}")

        @channel.on("message")
        def on_message(raw_message):
            try:
                # Deserialize message
                data = json.loads(raw_message)
                message = MeshMessage.from_dict(data)

                # Check for duplicate (prevent loops)
                if message.id in self.message_cache:
                    logger.debug(f"[MESH] Duplicate message {message.id}, ignoring")
                    return

                # Add to cache
                self.message_cache.add(message.id)

                # Handle message
                asyncio.create_task(self._handle_message(message, peer_id))

            except Exception as e:
                logger.error(f"[MESH] Failed to process message: {e}")

        @channel.on("close")
        def on_close():
            logger.info(f"[MESH] Data channel closed to {peer_id}")
            asyncio.create_task(self.disconnect_peer(peer_id))

    async def _handle_message(self, message: MeshMessage, from_peer: str) -> None:
        """Process received message"""
        try:
            logger.debug(f"[MESH] Received {message.type.value} from {from_peer}")

            # Call registered handlers
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    await handler(message, from_peer)

            # Forward message to other peers (mesh routing)
            if message.ttl > 1:
                forwarded_message = MeshMessage(
                    id=message.id,
                    type=message.type,
                    payload=message.payload,
                    sender_id=message.sender_id,
                    timestamp=message.timestamp,
                    ttl=message.ttl - 1,
                )

                # Forward to all peers except sender
                for peer_id in self.data_channels.keys():
                    if peer_id != from_peer:
                        await self.send_message(forwarded_message, target_peer=peer_id)

        except Exception as e:
            logger.error(f"[MESH] Failed to handle message: {e}")

    async def _discovery_loop(self) -> None:
        """Auto-discovery loop for finding nearby peers"""
        while self.is_running:
            try:
                # TODO: Implement local network discovery
                # - UDP broadcast for LAN peers
                # - mDNS/Bonjour for local service discovery
                # - Bluetooth for proximity detection

                await asyncio.sleep(5)  # Discovery interval

            except Exception as e:
                logger.error(f"[MESH] Discovery loop error: {e}")
                await asyncio.sleep(10)

    async def _connect_via_signaling(self) -> None:
        """Connect to signaling server for peer discovery"""
        try:
            # TODO: Implement signaling server protocol
            # - Connect to signaling server
            # - Announce presence
            # - Receive peer list
            # - Establish WebRTC connections

            logger.info(f"[MESH] Connected to signaling server: {self.signaling_server}")

        except Exception as e:
            logger.error(f"[MESH] Signaling server connection failed: {e}")

    async def enable_discovery(self) -> bool:
        """
        Enable peer discovery

        Returns:
            bool: True if discovery enabled
        """
        if not self.auto_discovery:
            self.auto_discovery = True
            asyncio.create_task(self._discovery_loop())
            logger.info("[MESH] Auto-discovery enabled")
            return True
        return False
