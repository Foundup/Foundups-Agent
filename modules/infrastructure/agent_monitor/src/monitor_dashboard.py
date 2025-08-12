#!/usr/bin/env python3
"""
Agent Monitor Dashboard
Real-time, cost-efficient monitoring interface
WSP-compliant with minimal resource usage
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.infrastructure.agent_monitor.src.agent_monitor import get_monitor


class MonitorDashboard:
    """Lightweight terminal dashboard for agent monitoring"""
    
    def __init__(self):
        self.monitor = get_monitor()
        self.refresh_rate = 5  # seconds
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def format_uptime(self, seconds: int) -> str:
        """Format uptime to human readable"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def display_dashboard(self):
        """Display dashboard in terminal"""
        self.clear_screen()
        dashboard = self.monitor.get_dashboard()
        
        print("="*60)
        print("FOUNDUPS AGENT MONITOR - COST-EFFICIENT DASHBOARD")
        print("="*60)
        print(f"Timestamp: {dashboard['timestamp']}")
        print(f"Active Agents: {dashboard['active_agents']}")
        print(f"Total Tool Calls: {dashboard['total_tool_calls']}")
        print("-"*60)
        
        # Agent Status Table
        print("\nAGENT STATUS:")
        print(f"{'Agent ID':<20} {'Status':<10} {'Uptime':<10} {'Efficiency':<10} {'Tools':<10}")
        print("-"*60)
        
        for agent in dashboard['agents']:
            status_icon = "●" if agent['status'] == 'active' else "○"
            print(f"{agent['agent_id'][:18]:<20} {status_icon} {agent['status']:<8} "
                  f"{self.format_uptime(agent['uptime_seconds']):<10} "
                  f"{agent['efficiency']}%{'':<7} {agent['tool_calls']:<10}")
        
        # Recent Events
        print("\nRECENT EVENTS:")
        for event in dashboard['recent_events'][-5:]:
            timestamp = event['timestamp'].split('T')[1].split('.')[0]
            print(f"[{timestamp}] {event['agent_id'][:15]}: {event['event_type']}")
        
        # Cost Analysis
        print("\nCOST ANALYSIS:")
        avg_tools = dashboard['total_tool_calls'] / max(1, dashboard['active_agents'])
        cost_status = "OPTIMAL" if avg_tools <= 5 else "HIGH"
        print(f"Avg Tools/Agent: {avg_tools:.1f} [{cost_status}]")
        
        # WSP Compliance
        print("\nWSP COMPLIANCE:")
        print(f"WSP 48 (Self-Improvement): Active")
        print(f"WSP 60 (Memory Efficient): NDJSON journaling")
        print(f"WSP 5 (Testing): Monitoring all agents")
        
        print("\n[Press Ctrl+C to exit, R for report, H for help]")
    
    def show_help(self):
        """Show help information"""
        print("\nHELP:")
        print("- Dashboard refreshes every 5 seconds")
        print("- Tool usage should be <=5 per task for cost efficiency")
        print("- Efficiency = (1-error_rate)*0.7 + tool_efficiency*0.3")
        print("- Agents idle >5min should be deactivated")
        print("\nPress any key to continue...")
        input()
    
    def generate_report(self):
        """Generate and save session report"""
        print("\nGenerating session report...")
        report_file = self.monitor.export_session_report()
        print(f"Report saved to: {report_file}")
        print("Press any key to continue...")
        input()
    
    def run(self):
        """Main dashboard loop"""
        print("Starting Agent Monitor Dashboard...")
        print("Loading agent data...")
        
        try:
            while self.running:
                self.display_dashboard()
                
                # Non-blocking input check
                import select
                import sys
                
                if os.name != 'nt':  # Unix/Linux
                    i, o, e = select.select([sys.stdin], [], [], self.refresh_rate)
                    if i:
                        key = sys.stdin.readline().strip().lower()
                        if key == 'r':
                            self.generate_report()
                        elif key == 'h':
                            self.show_help()
                else:  # Windows
                    time.sleep(self.refresh_rate)
                    
        except KeyboardInterrupt:
            print("\n\nShutting down monitor...")
            report_file = self.monitor.export_session_report()
            print(f"Final report saved to: {report_file}")
            print("Monitor stopped.")


def main():
    """Main entry point"""
    dashboard = MonitorDashboard()
    
    # Simulate some agent activity for testing
    monitor = get_monitor()
    monitor.log_event("youtube_monitor", "start", {"module": "livechat"})
    monitor.log_event("wre_orchestrator", "start", {"mode": "quantum"})
    monitor.log_event("youtube_monitor", "tool_call", {"tool": "oauth_auth"})
    monitor.log_event("youtube_monitor", "tool_call", {"tool": "find_stream"})
    monitor.log_event("wre_orchestrator", "tool_call", {"tool": "task_scoring"})
    
    dashboard.run()


if __name__ == "__main__":
    main()