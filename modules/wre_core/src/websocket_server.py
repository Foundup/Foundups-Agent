"""
WebSocket Server for WRE <-> Claude Code Integration

Provides real-time bidirectional communication between the WRE backend
and Claude Code VS Code extension for seamless "skin" functionality.
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, Any
from pathlib import Path
import threading
import time

# Add project root to path
import sys
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log

class WREWebSocketServer:
    """
    WebSocket server for real-time WRE <-> Claude Code communication.
    
    Provides bidirectional communication for:
    - Session status updates
    - Phase progress notifications  
    - Context synchronization
    - Real-time metrics
    - Command execution
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.is_running = False
        
        # WRE session state
        self.session_data: Dict[str, Any] = {
            "active": False,
            "session_id": None,
            "quantum_state": "01(02)",
            "current_phase": None,
            "phases_completed": 0,
            "autonomous_score": 0.0,
            "wsp_core_loaded": False,
            "agent_suite_status": "WSP-54 Ready",
            "compliance_score": 0.0,
            "communication_active": False,
            "context_sync": False,
            "last_update": datetime.now().isoformat()
        }
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for WebSocket server."""
        log_dir = project_root / "modules" / "wre_core" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "websocket_server.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def start_server(self):
        """Start the WebSocket server."""
        try:
            wre_log(f"🌐 Starting WRE WebSocket server on {self.host}:{self.port}", "INFO")
            
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            
            self.is_running = True
            self.session_data["communication_active"] = True
            
            wre_log(f"✅ WRE WebSocket server started successfully", "SUCCESS")
            wre_log(f"🔗 Claude Code extensions can connect to ws://{self.host}:{self.port}", "INFO")
            
            # Keep server running
            await self.server.wait_closed()
            
        except Exception as e:
            wre_log(f"❌ Failed to start WebSocket server: {e}", "ERROR")
            self.is_running = False
            self.session_data["communication_active"] = False

    async def handle_client(self, websocket):
        """Handle new client connections."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}" if websocket.remote_address else "unknown"
        wre_log(f"🔌 New client connected: {client_id}", "INFO")
        
        self.clients.add(websocket)
        
        try:
            # Send initial status to new client
            await self.send_to_client(websocket, {
                "type": "status",
                "data": self.session_data
            })
            
            # Handle incoming messages
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            wre_log(f"🔌 Client disconnected: {client_id}", "INFO")
        except Exception as e:
            wre_log(f"❌ Error handling client {client_id}: {e}", "ERROR")
        finally:
            self.clients.discard(websocket)

    async def handle_message(self, websocket, message: str):
        """Handle incoming messages from clients."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            wre_log(f"📨 Received message: {message_type}", "INFO")
            
            if message_type == "get_status":
                await self.send_status(websocket)
                
            elif message_type == "start_wre":
                await self.handle_start_wre(websocket, data.get("data", {}))
                
            elif message_type == "stop_wre":
                await self.handle_stop_wre(websocket)
                
            elif message_type == "context_update":
                await self.handle_context_update(data.get("data", {}))
                
            elif message_type == "ping":
                await self.send_to_client(websocket, {"type": "pong"})
                
            else:
                wre_log(f"⚠️ Unknown message type: {message_type}", "WARNING")
                
        except json.JSONDecodeError as e:
            wre_log(f"❌ Invalid JSON message: {e}", "ERROR")
        except Exception as e:
            wre_log(f"❌ Error processing message: {e}", "ERROR")

    async def send_status(self, websocket):
        """Send current status to client."""
        await self.send_to_client(websocket, {
            "type": "status",
            "data": self.session_data
        })

    async def handle_start_wre(self, websocket, data: Dict[str, Any]):
        """Handle WRE start request from client."""
        try:
            directive = data.get("directive", "Interactive WRE session from Claude Code")
            workspace_path = data.get("workspace_path")
            file_context = data.get("file_context")
            
            wre_log(f"🚀 Starting WRE session via WebSocket", "INFO")
            wre_log(f"📋 Directive: {directive}", "INFO")
            
            # Update session data
            session_id = f"WRE_{int(datetime.now().timestamp())}"
            self.session_data.update({
                "active": True,
                "session_id": session_id,
                "quantum_state": "01(02)",  # Start in dormant state
                "current_phase": "Session Initiation",
                "phases_completed": 0,
                "wsp_core_loaded": True,
                "context_sync": True,
                "last_update": datetime.now().isoformat()
            })
            
            # Send acknowledgment
            await self.send_to_client(websocket, {
                "type": "wre_started",
                "data": {
                    "session_id": session_id,
                    "success": True,
                    "message": "WRE session initiated successfully"
                }
            })
            
            # Broadcast status update to all clients
            await self.broadcast_status_update()
            
            # Simulate phase progression
            asyncio.create_task(self.simulate_wre_progression())
            
        except Exception as e:
            wre_log(f"❌ Failed to start WRE session: {e}", "ERROR")
            await self.send_to_client(websocket, {
                "type": "wre_error",
                "data": {
                    "success": False,
                    "error": str(e)
                }
            })

    async def handle_stop_wre(self, websocket):
        """Handle WRE stop request from client."""
        try:
            wre_log("🛑 Stopping WRE session via WebSocket", "INFO")
            
            self.session_data.update({
                "active": False,
                "session_id": None,
                "quantum_state": "01(02)",
                "current_phase": None,
                "phases_completed": 0,
                "autonomous_score": 0.0,
                "last_update": datetime.now().isoformat()
            })
            
            await self.send_to_client(websocket, {
                "type": "wre_stopped",
                "data": {
                    "success": True,
                    "message": "WRE session stopped successfully"
                }
            })
            
            await self.broadcast_status_update()
            
        except Exception as e:
            wre_log(f"❌ Failed to stop WRE session: {e}", "ERROR")
            await self.send_to_client(websocket, {
                "type": "wre_error",
                "data": {
                    "success": False,
                    "error": str(e)
                }
            })

    async def handle_context_update(self, data: Dict[str, Any]):
        """Handle context updates from Claude Code."""
        current_file = data.get("current_file")
        workspace_path = data.get("workspace_path")
        selection = data.get("selection")
        
        wre_log(f"📄 Context update: {current_file}", "INFO")
        
        # Update context sync status
        self.session_data["context_sync"] = True
        self.session_data["last_update"] = datetime.now().isoformat()
        
        # Broadcast context update to all clients
        await self.broadcast_message({
            "type": "context_updated",
            "data": data
        })

    async def simulate_wre_progression(self):
        """Simulate WRE 12-phase progression for demonstration."""
        phases = [
            "Session Initiation",
            "0102 Activation", 
            "Scoring Retrieval",
            "Agentic Readiness Check",
            "Menu Render",
            "Operator Selection", 
            "Build Scaffolding",
            "Build Execution",
            "Modularity Audit",
            "Testing Cycle",
            "Documentation Update",
            "Recursive Self-Assessment"
        ]
        
        quantum_states = ["01(02)", "01/02", "0102", "0102", "0102", "0102", 
                         "0102", "0102", "0102", "0102", "0102", "0201"]
        
        for i, (phase, quantum_state) in enumerate(zip(phases, quantum_states)):
            if not self.session_data["active"]:
                break
                
            await asyncio.sleep(3)  # Simulate phase processing time
            
            self.session_data.update({
                "current_phase": phase,
                "phases_completed": i + 1,
                "quantum_state": quantum_state,
                "autonomous_score": min(1.0, (i + 1) / 12.0 * 0.85 + 0.15),
                "compliance_score": min(1.0, (i + 1) / 12.0 * 0.9 + 0.1),
                "last_update": datetime.now().isoformat()
            })
            
            wre_log(f"📊 Phase {i + 1}/12: {phase} - Quantum State: {quantum_state}", "INFO")
            
            # Broadcast phase update
            await self.broadcast_message({
                "type": "phase_update",
                "data": {
                    "phase": phase,
                    "phase_number": i + 1,
                    "quantum_state": quantum_state,
                    "progress": (i + 1) / 12.0
                }
            })
        
        if self.session_data["active"]:
            wre_log("✅ WRE 12-phase progression completed", "SUCCESS")
            await self.broadcast_message({
                "type": "wre_completed",
                "data": {
                    "message": "WRE 12-phase REMOTE_BUILD_PROTOTYPE flow completed successfully",
                    "final_score": self.session_data["autonomous_score"]
                }
            })

    async def send_to_client(self, websocket, message: Dict[str, Any]):
        """Send message to specific client."""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            wre_log(f"❌ Failed to send message to client: {e}", "ERROR")

    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        if self.clients:
            await asyncio.gather(
                *[self.send_to_client(client, message) for client in self.clients],
                return_exceptions=True
            )

    async def broadcast_status_update(self):
        """Broadcast status update to all clients."""
        await self.broadcast_message({
            "type": "status_update", 
            "data": self.session_data
        })

    def start_background_server(self):
        """Start WebSocket server in background thread."""
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.start_server())
            except KeyboardInterrupt:
                wre_log("🛑 WebSocket server interrupted", "INFO")
            finally:
                loop.close()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        wre_log("🌐 WebSocket server started in background", "INFO")
        return server_thread

    async def stop_server(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            self.session_data["communication_active"] = False
            wre_log("🛑 WebSocket server stopped", "INFO")

def create_wre_websocket_server(host: str = "localhost", port: int = 8765) -> WREWebSocketServer:
    """Factory function to create WRE WebSocket server."""
    return WREWebSocketServer(host, port)

if __name__ == "__main__":
    # Start WebSocket server directly
    server = WREWebSocketServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("🛑 Server stopped by user")