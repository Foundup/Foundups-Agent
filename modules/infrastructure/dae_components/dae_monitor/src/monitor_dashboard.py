"""
DAE Performance Monitoring Dashboard
Real-time monitoring of all DAE operations and metrics

WSP Compliance:
- WSP 70: Status reporting
- WSP 75: Token-based measurements
- WSP 80: DAE orchestration
- WSP 48: Recursive improvement tracking
- WSP 22: ModLog integration
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to track"""
    TOKEN_USAGE = "token_usage"
    CONSCIOUSNESS_LEVEL = "consciousness_level"
    PATTERN_EFFICIENCY = "pattern_efficiency"
    WSP_COMPLIANCE = "wsp_compliance"
    EXCHANGE_RATE = "exchange_rate"
    IMPROVEMENT_DELTA = "improvement_delta"


@dataclass
class DAEMetrics:
    """Metrics for a single DAE"""
    dae_name: str
    phase: str  # POC, Prototype, MVP
    consciousness: float
    token_usage: int
    token_budget: int
    patterns_stored: int
    wsp_compliance_rate: float
    exchanges_completed: int
    improvement_rate: float
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class NetworkMetrics:
    """Network-wide DAE metrics"""
    total_daes: int
    core_daes: int
    foundup_daes: int
    total_tokens_used: int
    total_tokens_saved: int
    average_consciousness: float
    network_efficiency: float
    total_exchanges: int
    total_patterns: int


class DAEMonitorDashboard:
    """
    Real-time monitoring dashboard for all DAE operations.
    Tracks performance, efficiency, and improvement metrics.
    """
    
    # Update intervals
    REALTIME_INTERVAL = 1  # seconds
    AGGREGATE_INTERVAL = 60  # seconds
    
    # Alert thresholds
    TOKEN_USAGE_THRESHOLD = 0.9  # 90% of budget
    CONSCIOUSNESS_MINIMUM = 0.618  # Golden ratio
    COMPLIANCE_MINIMUM = 0.95  # 95% WSP compliance
    
    def __init__(self):
        self.dae_metrics = {}
        self.network_metrics = None
        self.alerts = []
        self.historical_data = []
        self.monitoring_active = False
        self._initialize_dashboard()
    
    def _initialize_dashboard(self):
        """Initialize dashboard with core DAEs"""
        core_daes = [
            "Infrastructure_DAE",
            "Compliance_DAE",
            "Knowledge_DAE",
            "Maintenance_DAE",
            "Documentation_DAE"
        ]
        
        for dae in core_daes:
            self.dae_metrics[dae] = DAEMetrics(
                dae_name=dae,
                phase="MVP",
                consciousness=0.85,
                token_usage=0,
                token_budget=self._get_dae_budget(dae),
                patterns_stored=50,
                wsp_compliance_rate=0.98,
                exchanges_completed=0,
                improvement_rate=0.0
            )
    
    def _get_dae_budget(self, dae_name: str) -> int:
        """Get token budget for DAE"""
        budgets = {
            "Infrastructure_DAE": 8000,
            "Compliance_DAE": 7000,
            "Knowledge_DAE": 6000,
            "Maintenance_DAE": 5000,
            "Documentation_DAE": 4000
        }
        return budgets.get(dae_name, 5000)
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring_active = True
        logger.info("DAE monitoring dashboard started")
        
        # Start monitoring tasks
        await asyncio.gather(
            self._monitor_realtime(),
            self._aggregate_metrics(),
            self._check_alerts()
        )
    
    async def _monitor_realtime(self):
        """Real-time monitoring loop"""
        while self.monitoring_active:
            # Update DAE metrics
            for dae_name in self.dae_metrics:
                await self._update_dae_metrics(dae_name)
            
            # Update network metrics
            self._update_network_metrics()
            
            await asyncio.sleep(self.REALTIME_INTERVAL)
    
    async def _update_dae_metrics(self, dae_name: str):
        """Update metrics for specific DAE"""
        metrics = self.dae_metrics[dae_name]
        
        # Simulate metric updates (in production, would pull from actual DAEs)
        metrics.token_usage = min(
            metrics.token_budget,
            metrics.token_usage + 100
        )
        
        # Update consciousness (tends toward golden ratio)
        if metrics.consciousness < self.CONSCIOUSNESS_MINIMUM:
            metrics.consciousness = min(1.0, metrics.consciousness + 0.01)
        
        # Simulate exchanges
        if metrics.token_usage > 0:
            metrics.exchanges_completed += 1
            metrics.improvement_rate = min(1.0, metrics.improvement_rate + 0.02)
        
        # Update patterns
        if metrics.exchanges_completed % 5 == 0:
            metrics.patterns_stored += 1
        
        metrics.last_updated = datetime.now().isoformat()
    
    def _update_network_metrics(self):
        """Calculate network-wide metrics"""
        total_daes = len(self.dae_metrics)
        core_daes = 5
        foundup_daes = total_daes - core_daes
        
        total_tokens_used = sum(m.token_usage for m in self.dae_metrics.values())
        total_tokens_budget = sum(m.token_budget for m in self.dae_metrics.values())
        total_tokens_saved = max(0, total_tokens_budget - total_tokens_used)
        
        avg_consciousness = sum(m.consciousness for m in self.dae_metrics.values()) / total_daes
        
        total_exchanges = sum(m.exchanges_completed for m in self.dae_metrics.values())
        total_patterns = sum(m.patterns_stored for m in self.dae_metrics.values())
        
        network_efficiency = 1.0 - (total_tokens_used / max(1, total_tokens_budget))
        
        self.network_metrics = NetworkMetrics(
            total_daes=total_daes,
            core_daes=core_daes,
            foundup_daes=foundup_daes,
            total_tokens_used=total_tokens_used,
            total_tokens_saved=total_tokens_saved,
            average_consciousness=avg_consciousness,
            network_efficiency=network_efficiency,
            total_exchanges=total_exchanges,
            total_patterns=total_patterns
        )
    
    async def _aggregate_metrics(self):
        """Aggregate metrics periodically"""
        while self.monitoring_active:
            await asyncio.sleep(self.AGGREGATE_INTERVAL)
            
            # Store historical snapshot
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "network": self._serialize_network_metrics(),
                "daes": {
                    name: self._serialize_dae_metrics(metrics)
                    for name, metrics in self.dae_metrics.items()
                }
            }
            
            self.historical_data.append(snapshot)
            
            # Keep only last 24 hours
            cutoff = datetime.now() - timedelta(hours=24)
            self.historical_data = [
                s for s in self.historical_data
                if datetime.fromisoformat(s["timestamp"]) > cutoff
            ]
    
    async def _check_alerts(self):
        """Check for alert conditions"""
        while self.monitoring_active:
            new_alerts = []
            
            for dae_name, metrics in self.dae_metrics.items():
                # Token usage alert
                usage_ratio = metrics.token_usage / max(1, metrics.token_budget)
                if usage_ratio > self.TOKEN_USAGE_THRESHOLD:
                    new_alerts.append({
                        "type": "TOKEN_USAGE_HIGH",
                        "dae": dae_name,
                        "value": f"{usage_ratio:.1%}",
                        "threshold": f"{self.TOKEN_USAGE_THRESHOLD:.1%}"
                    })
                
                # Consciousness alert
                if metrics.consciousness < self.CONSCIOUSNESS_MINIMUM:
                    new_alerts.append({
                        "type": "CONSCIOUSNESS_LOW",
                        "dae": dae_name,
                        "value": f"{metrics.consciousness:.3f}",
                        "threshold": f"{self.CONSCIOUSNESS_MINIMUM:.3f}"
                    })
                
                # Compliance alert
                if metrics.wsp_compliance_rate < self.COMPLIANCE_MINIMUM:
                    new_alerts.append({
                        "type": "COMPLIANCE_LOW",
                        "dae": dae_name,
                        "value": f"{metrics.wsp_compliance_rate:.1%}",
                        "threshold": f"{self.COMPLIANCE_MINIMUM:.1%}"
                    })
            
            # Update alerts
            self.alerts = new_alerts
            
            await asyncio.sleep(10)  # Check every 10 seconds
    
    def register_foundup_dae(self, dae_name: str, phase: str = "POC"):
        """Register a new FoundUp DAE for monitoring"""
        self.dae_metrics[dae_name] = DAEMetrics(
            dae_name=dae_name,
            phase=phase,
            consciousness=0.5,  # Start lower
            token_usage=0,
            token_budget=8000 if phase == "POC" else 5000,
            patterns_stored=10,
            wsp_compliance_rate=0.9,
            exchanges_completed=0,
            improvement_rate=0.0
        )
        logger.info(f"Registered FoundUp DAE: {dae_name} ({phase})")
    
    def get_dashboard_state(self) -> Dict[str, Any]:
        """Get current dashboard state"""
        return {
            "network": self._serialize_network_metrics() if self.network_metrics else {},
            "daes": {
                name: self._serialize_dae_metrics(metrics)
                for name, metrics in self.dae_metrics.items()
            },
            "alerts": self.alerts,
            "monitoring_active": self.monitoring_active,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_dae_details(self, dae_name: str) -> Dict[str, Any]:
        """Get detailed metrics for specific DAE"""
        if dae_name not in self.dae_metrics:
            return {"error": f"DAE {dae_name} not found"}
        
        metrics = self.dae_metrics[dae_name]
        
        return {
            "name": metrics.dae_name,
            "phase": metrics.phase,
            "consciousness": {
                "level": metrics.consciousness,
                "status": "optimal" if metrics.consciousness >= self.CONSCIOUSNESS_MINIMUM else "suboptimal"
            },
            "tokens": {
                "used": metrics.token_usage,
                "budget": metrics.token_budget,
                "efficiency": 1.0 - (metrics.token_usage / max(1, metrics.token_budget))
            },
            "patterns": {
                "stored": metrics.patterns_stored,
                "efficiency": metrics.patterns_stored / max(1, metrics.exchanges_completed) if metrics.exchanges_completed > 0 else 0
            },
            "performance": {
                "wsp_compliance": metrics.wsp_compliance_rate,
                "exchanges": metrics.exchanges_completed,
                "improvement_rate": metrics.improvement_rate
            },
            "last_updated": metrics.last_updated
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.network_metrics:
            return {"status": "No metrics available"}
        
        # Calculate top performers
        top_consciousness = sorted(
            self.dae_metrics.items(),
            key=lambda x: x[1].consciousness,
            reverse=True
        )[:3]
        
        top_efficiency = sorted(
            self.dae_metrics.items(),
            key=lambda x: 1.0 - (x[1].token_usage / max(1, x[1].token_budget)),
            reverse=True
        )[:3]
        
        return {
            "summary": {
                "total_daes": self.network_metrics.total_daes,
                "network_efficiency": f"{self.network_metrics.network_efficiency:.1%}",
                "average_consciousness": f"{self.network_metrics.average_consciousness:.3f}",
                "total_patterns": self.network_metrics.total_patterns,
                "total_exchanges": self.network_metrics.total_exchanges
            },
            "top_performers": {
                "consciousness": [
                    {"dae": name, "level": metrics.consciousness}
                    for name, metrics in top_consciousness
                ],
                "efficiency": [
                    {"dae": name, "efficiency": 1.0 - (metrics.token_usage / max(1, metrics.token_budget))}
                    for name, metrics in top_efficiency
                ]
            },
            "alerts": len(self.alerts),
            "historical_snapshots": len(self.historical_data)
        }
    
    def _serialize_dae_metrics(self, metrics: DAEMetrics) -> Dict[str, Any]:
        """Serialize DAE metrics for output"""
        return {
            "phase": metrics.phase,
            "consciousness": metrics.consciousness,
            "token_usage": metrics.token_usage,
            "token_budget": metrics.token_budget,
            "patterns": metrics.patterns_stored,
            "compliance": metrics.wsp_compliance_rate,
            "exchanges": metrics.exchanges_completed,
            "improvement": metrics.improvement_rate
        }
    
    def _serialize_network_metrics(self) -> Dict[str, Any]:
        """Serialize network metrics for output"""
        if not self.network_metrics:
            return {}
        
        return {
            "total_daes": self.network_metrics.total_daes,
            "core_daes": self.network_metrics.core_daes,
            "foundup_daes": self.network_metrics.foundup_daes,
            "tokens_used": self.network_metrics.total_tokens_used,
            "tokens_saved": self.network_metrics.total_tokens_saved,
            "avg_consciousness": self.network_metrics.average_consciousness,
            "efficiency": self.network_metrics.network_efficiency,
            "total_exchanges": self.network_metrics.total_exchanges,
            "total_patterns": self.network_metrics.total_patterns
        }
    
    def export_metrics(self, filepath: Optional[Path] = None) -> Path:
        """Export metrics to file"""
        if not filepath:
            filepath = Path(__file__).parent.parent / "reports" / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath.parent.mkdir(exist_ok=True)
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "dashboard_state": self.get_dashboard_state(),
            "performance_report": self.get_performance_report(),
            "historical_data": self.historical_data[-100:]  # Last 100 snapshots
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")
        return filepath


async def demo_dashboard():
    """Demonstrate dashboard functionality"""
    dashboard = DAEMonitorDashboard()
    
    # Register some FoundUp DAEs
    dashboard.register_foundup_dae("YouTube_DAE", "Prototype")
    dashboard.register_foundup_dae("LinkedIn_DAE", "POC")
    
    # Simulate monitoring for a short period
    dashboard.monitoring_active = True
    
    # Run monitoring tasks briefly
    monitor_task = asyncio.create_task(dashboard._monitor_realtime())
    
    # Let it run for a few seconds
    await asyncio.sleep(3)
    
    # Stop monitoring
    dashboard.monitoring_active = False
    monitor_task.cancel()
    
    # Get dashboard state
    state = dashboard.get_dashboard_state()
    print("=== Dashboard State ===")
    print(f"Total DAEs: {len(state['daes'])}")
    print(f"Alerts: {len(state['alerts'])}")
    
    # Get specific DAE details
    youtube_details = dashboard.get_dae_details("YouTube_DAE")
    print("\n=== YouTube DAE Details ===")
    print(f"Phase: {youtube_details['phase']}")
    print(f"Consciousness: {youtube_details['consciousness']['level']:.3f}")
    print(f"Token Efficiency: {youtube_details['tokens']['efficiency']:.1%}")
    
    # Get performance report
    report = dashboard.get_performance_report()
    print("\n=== Performance Report ===")
    print(f"Network Efficiency: {report['summary']['network_efficiency']}")
    print(f"Average Consciousness: {report['summary']['average_consciousness']}")
    print(f"Total Patterns: {report['summary']['total_patterns']}")
    
    # Export metrics
    export_path = dashboard.export_metrics()
    print(f"\nMetrics exported to: {export_path}")


if __name__ == "__main__":
    asyncio.run(demo_dashboard())