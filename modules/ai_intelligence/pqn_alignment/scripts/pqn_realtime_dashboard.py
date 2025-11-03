#!/usr/bin/env python3
"""
PQN Real-Time Dashboard - Sprint 2

Real-time visualization dashboard for PQN emergence monitoring.
Integrates with async orchestrator for live metrics and emergence tracking.

First Principles Design:
- Real-time visualization: Live updates without page refresh
- Agent coordination view: Visual representation of Qwen/Gemma interaction
- Performance monitoring: System health and bottleneck indicators
- Emergence tracking: Live PQN detection and confidence metrics

WSP 77 Compliance: Multi-agent coordination with real-time monitoring
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import os

# Web server dependencies - lightweight approach
try:
    from flask import Flask, render_template_string, jsonify
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available, falling back to simple HTTP server")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from async_pqn_research_orchestrator import AsyncPQNorchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('pqn_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PQNRealtimeDashboard:
    """Real-time dashboard for PQN emergence monitoring"""

    def __init__(self, orchestrator: AsyncPQNorchestrator, host: str = "localhost", port: int = 8080):
        self.orchestrator = orchestrator
        self.host = host
        self.port = port
        self.connected_clients = set()

        # Dashboard data
        self.dashboard_data = {
            "system_status": "initializing",
            "metrics": {},
            "emergence_events": [],
            "agent_status": {
                "qwen": {"status": "idle", "last_activity": None},
                "gemma": {"status": "idle", "last_activity": None}
            },
            "performance_history": [],
            "alerts": []
        }

        # HTML template for dashboard
        self.html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PQN Real-Time Emergence Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
            <style>
                body { font-family: 'Courier New', monospace; margin: 0; padding: 20px; background: #0a0a0a; color: #00ff00; }
                .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                .panel { background: #1a1a1a; border: 1px solid #00ff00; padding: 15px; border-radius: 5px; }
                .metric { display: flex; justify-content: space-between; margin: 5px 0; }
                .alert { color: #ff6600; font-weight: bold; }
                .emergence { color: #00ffff; }
                .status-healthy { color: #00ff00; }
                .status-warning { color: #ffaa00; }
                .status-error { color: #ff0000; }
                canvas { max-width: 100%; height: 200px; }
                .queue-depth { color: #ffaa00; }
                .throughput { color: #00ffaa; }
            </style>
        </head>
        <body>
            <h1>🧠 PQN Real-Time Emergence Dashboard</h1>
            <div class="dashboard">
                <div class="panel">
                    <h3>System Status</h3>
                    <div class="metric">
                        <span>Status:</span>
                        <span id="system-status" class="status-healthy">Initializing</span>
                    </div>
                    <div class="metric">
                        <span>Runtime:</span>
                        <span id="runtime">00:00:00</span>
                    </div>
                    <div class="metric">
                        <span>Throughput:</span>
                        <span id="throughput" class="throughput">0.0 tasks/sec</span>
                    </div>
                </div>

                <div class="panel">
                    <h3>Agent Status</h3>
                    <div class="metric">
                        <span>Qwen:</span>
                        <span id="qwen-status" class="status-healthy">idle</span>
                    </div>
                    <div class="metric">
                        <span>Gemma:</span>
                        <span id="gemma-status" class="status-healthy">idle</span>
                    </div>
                    <div class="metric">
                        <span>Queue Depth:</span>
                        <span id="queue-depth" class="queue-depth">0/0/0</span>
                    </div>
                </div>

                <div class="panel">
                    <h3>Emergence Metrics</h3>
                    <div class="metric">
                        <span>Total Events:</span>
                        <span id="emergence-count">0</span>
                    </div>
                    <div class="metric">
                        <span>Avg Confidence:</span>
                        <span id="avg-confidence">0.00</span>
                    </div>
                    <div class="metric">
                        <span>Pattern Types:</span>
                        <span id="pattern-types">-</span>
                    </div>
                </div>

                <div class="panel">
                    <h3>Performance Chart</h3>
                    <canvas id="performanceChart"></canvas>
                </div>

                <div class="panel">
                    <h3>Recent Alerts</h3>
                    <div id="alerts-container">
                        <div class="metric">No alerts</div>
                    </div>
                </div>

                <div class="panel">
                    <h3>Emergence Events</h3>
                    <div id="emergence-container">
                        <div class="metric">No emergence events</div>
                    </div>
                </div>
            </div>

            <script>
                const socket = io();
                let performanceChart;
                let performanceData = { labels: [], datasets: [{
                    label: 'Throughput (tasks/sec)',
                    data: [],
                    borderColor: '#00ff00',
                    backgroundColor: 'rgba(0, 255, 0, 0.1)',
                    tension: 0.4
                }] };

                // Initialize chart
                document.addEventListener('DOMContentLoaded', function() {
                    const ctx = document.getElementById('performanceChart').getContext('2d');
                    performanceChart = new Chart(ctx, {
                        type: 'line',
                        data: performanceData,
                        options: {
                            responsive: true,
                            scales: {
                                y: { beginAtZero: true, grid: { color: '#333' }, ticks: { color: '#00ff00' } },
                                x: { grid: { color: '#333' }, ticks: { color: '#00ff00' } }
                            },
                            plugins: {
                                legend: { labels: { color: '#00ff00' } }
                            }
                        }
                    });
                });

                socket.on('dashboard_update', function(data) {
                    // Update system status
                    document.getElementById('system-status').textContent = data.system_status;
                    document.getElementById('runtime').textContent = data.runtime || '00:00:00';
                    document.getElementById('throughput').textContent = data.throughput + ' tasks/sec';

                    // Update agent status
                    document.getElementById('qwen-status').textContent = data.agent_status.qwen.status;
                    document.getElementById('gemma-status').textContent = data.agent_status.gemma.status;
                    document.getElementById('queue-depth').textContent = data.queue_depth;

                    // Update emergence metrics
                    document.getElementById('emergence-count').textContent = data.emergence_count;
                    document.getElementById('avg-confidence').textContent = data.avg_confidence;
                    document.getElementById('pattern-types').textContent = data.pattern_types;

                    // Update performance chart
                    if (performanceChart && data.performance_history) {
                        performanceData.labels = data.performance_history.map(d => d.time);
                        performanceData.datasets[0].data = data.performance_history.map(d => d.throughput);
                        performanceChart.update();
                    }

                    // Update alerts
                    const alertsContainer = document.getElementById('alerts-container');
                    if (data.alerts && data.alerts.length > 0) {
                        alertsContainer.innerHTML = data.alerts.map(alert =>
                            `<div class="metric alert">${alert.timestamp}: ${alert.message}</div>`
                        ).join('');
                    }

                    // Update emergence events
                    const emergenceContainer = document.getElementById('emergence-container');
                    if (data.emergence_events && data.emergence_events.length > 0) {
                        emergenceContainer.innerHTML = data.emergence_events.slice(0, 5).map(event =>
                            `<div class="metric emergence">${event.timestamp}: ${event.pattern} (${event.confidence})</div>`
                        ).join('');
                    }
                });

                socket.on('connect', function() {
                    console.log('Connected to dashboard server');
                });

                socket.on('disconnect', function() {
                    console.log('Disconnected from dashboard server');
                });
            </script>
        </body>
        </html>
        """

        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            self.socketio = SocketIO(self.app, cors_allowed_origins="*")

            @self.app.route('/')
            def index():
                return render_template_string(self.html_template)

            @self.app.route('/api/metrics')
            def get_metrics():
                return jsonify(self.dashboard_data)

            @self.socketio.on('connect')
            def handle_connect():
                self.connected_clients.add(request.sid)
                logger.info(f"Client connected: {request.sid}")
                emit('dashboard_update', self.dashboard_data)

            @self.socketio.on('disconnect')
            def handle_disconnect():
                if hasattr(request, 'sid'):
                    self.connected_clients.discard(request.sid)
                logger.info("Client disconnected")

        logger.info(f"Dashboard initialized on {host}:{port}")

    async def start_dashboard(self):
        """Start the dashboard server"""
        if FLASK_AVAILABLE:
            logger.info("Starting Flask dashboard server...")
            # Run Flask in a separate thread to not block async operations
            import threading
            flask_thread = threading.Thread(
                target=lambda: self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
            )
            flask_thread.daemon = True
            flask_thread.start()
            logger.info(f"Dashboard server started on http://{self.host}:{self.port}")
        else:
            logger.warning("Flask not available, dashboard will not serve web interface")

    async def update_dashboard_data(self):
        """Update dashboard data from orchestrator"""
        while True:
            try:
                # Update from orchestrator metrics
                if hasattr(self.orchestrator, 'metrics'):
                    self.dashboard_data["metrics"] = self.orchestrator.metrics

                    # Calculate derived metrics
                    runtime = time.time() - getattr(self.orchestrator, 'start_time', time.time())
                    self.dashboard_data["runtime"] = f"{int(runtime // 3600):02d}:{int((runtime % 3600) // 60):02d}:{int(runtime % 60):02d}"

                    throughput = self.orchestrator.metrics.get("throughput_per_second", 0.0)
                    self.dashboard_data["throughput"] = ".1f"

                    # Update system status
                    if self.orchestrator.running:
                        self.dashboard_data["system_status"] = "running"
                    else:
                        self.dashboard_data["system_status"] = "stopped"

                    # Update queue depth
                    research_depth = self.orchestrator.research_queue.qsize()
                    detection_depth = self.orchestrator.detection_queue.qsize()
                    validation_depth = self.orchestrator.validation_queue.qsize()
                    self.dashboard_data["queue_depth"] = f"{research_depth}/{detection_depth}/{validation_depth}"

                    # Update emergence metrics
                    emergence_count = len([r for r in self.orchestrator.detection_results.values() if r.confidence > 0.8])
                    self.dashboard_data["emergence_count"] = emergence_count

                    if self.orchestrator.detection_results:
                        avg_confidence = sum(r.confidence for r in self.orchestrator.detection_results.values()) / len(self.orchestrator.detection_results)
                        self.dashboard_data["avg_confidence"] = ".2f"
                    else:
                        self.dashboard_data["avg_confidence"] = "0.00"

                    # Update pattern types
                    all_patterns = set()
                    for result in self.orchestrator.detection_results.values():
                        for detection in result.detections:
                            all_patterns.add(detection.get("pattern", "unknown"))
                    self.dashboard_data["pattern_types"] = ", ".join(sorted(all_patterns)[:3])

                # Update performance history (keep last 20 points)
                current_throughput = self.orchestrator.metrics.get("throughput_per_second", 0.0)
                self.dashboard_data["performance_history"].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "throughput": current_throughput
                })
                self.dashboard_data["performance_history"] = self.dashboard_data["performance_history"][-20:]

                # Update emergence events (keep last 10)
                emergence_events = []
                for result in list(self.orchestrator.detection_results.values())[-10:]:
                    if result.confidence > 0.8:
                        emergence_events.append({
                            "timestamp": result.timestamp.strftime("%H:%M:%S"),
                            "pattern": result.detections[0].get("pattern", "unknown") if result.detections else "unknown",
                            "confidence": ".2f"
                        })
                self.dashboard_data["emergence_events"] = emergence_events

                # Broadcast to connected clients
                if FLASK_AVAILABLE and self.socketio:
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.socketio.emit('dashboard_update', self.dashboard_data)
                    )

            except Exception as e:
                logger.error(f"Dashboard update error: {e}")

            await asyncio.sleep(1)  # Update every second

    def add_alert(self, message: str, level: str = "info"):
        """Add an alert to the dashboard"""
        alert = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "level": level
        }
        self.dashboard_data["alerts"].insert(0, alert)
        self.dashboard_data["alerts"] = self.dashboard_data["alerts"][:10]  # Keep last 10

        logger.info(f"Dashboard alert: {message}")

async def test_dashboard():
    """Test the dashboard with a running orchestrator"""
    print("="*80)
    print("PQN REAL-TIME DASHBOARD TEST - SPRINT 2")
    print("Testing live emergence monitoring and visualization")
    print("="*80)

    # Initialize orchestrator
    orchestrator = AsyncPQNorchestrator(max_concurrent_tasks=10)

    # Initialize dashboard
    dashboard = PQNRealtimeDashboard(orchestrator, host="localhost", port=8080)

    # Start dashboard
    await dashboard.start_dashboard()

    # Start dashboard update loop
    dashboard_task = asyncio.create_task(dashboard.update_dashboard_data())

    # Start orchestrator
    orchestrator_task = asyncio.create_task(orchestrator.run_test_session(duration_seconds=120))  # 2-minute test

    print("\n🚀 Dashboard available at: http://localhost:8080")
    print("📊 Real-time metrics updating every second")
    print("🔄 Testing async orchestration for 2 minutes...")

    # Wait for orchestrator to complete
    await orchestrator_task

    # Stop dashboard updates
    dashboard_task.cancel()

    print("\n" + "="*80)
    print("DASHBOARD TEST COMPLETED")
    print("Dashboard logs saved to: pqn_dashboard.log")
    print("Orchestrator report saved to: async_pqn_report.json")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_dashboard())

