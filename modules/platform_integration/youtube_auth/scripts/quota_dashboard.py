#!/usr/bin/env python3
"""
Quota Dashboard - Interactive Quota Monitoring Tool
WSP-Compliant: Real-time quota monitoring and management

Usage:
    python quota_dashboard.py
    python quota_dashboard.py --summary
    python quota_dashboard.py --reset-emergency
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.quota_monitor import QuotaMonitor
from src.quota_intelligence import QuotaIntelligence


def print_banner():
    """Print dashboard banner."""
    print("\n" + "="*80)
    print("[TARGET] YOUTUBE API QUOTA INTELLIGENCE DASHBOARD")
    print("="*80)


def print_quota_summary(dashboard):
    """Print main quota summary."""
    print(f"\n[DATA] SYSTEM STATUS: {dashboard['overall_status']}")
    print(f"⏰ Time until reset: {dashboard['time_until_reset']}")
    print(f"[U+1F550] Last updated: {datetime.fromisoformat(dashboard['timestamp']).strftime('%I:%M %p')}")
    
    print(f"\n{'='*60}")
    print("CREDENTIAL SET STATUS")
    print(f"{'='*60}")
    
    for set_num, set_info in dashboard['credential_sets'].items():
        status_emoji = {
            'HEALTHY': '[OK]',
            'MODERATE': '[U+26A0]️', 
            'WARNING': '[ALERT]',
            'CRITICAL': '[U+1F480]',
            'DISABLED': '[FAIL]'
        }.get(set_info['status'], '[U+2753]')
        
        print(f"\n[U+1F511] SET {set_num} ({set_info['status']}) {status_emoji}")
        print(f"   [UP] Usage: {set_info['used']:,}/{set_info['limit']:,} units ({set_info['usage_percent']:.1f}%)")
        print(f"   [U+1F4B0] Available: {set_info['available']:,} units")
        print(f"   [U+1F6E1]️ Safe available: {set_info['safe_available']:,} units (after emergency reserve)")
        print(f"   [TARGET] Can handle expensive ops: {'Yes' if set_info['can_handle_expensive_ops'] else 'No'}")
        print(f"   [IDEA] Recommended for: {', '.join(set_info['recommended_for'])}")


def print_recommendations(dashboard):
    """Print system recommendations."""
    if dashboard['recommendations']:
        print(f"\n{'='*60}")
        print("INTELLIGENT RECOMMENDATIONS")
        print(f"{'='*60}")
        for rec in dashboard['recommendations']:
            print(f"   {rec}")


def print_emergency_reserves(dashboard):
    """Print emergency reserve status."""
    print(f"\n{'='*60}")
    print("EMERGENCY RESERVE STATUS")
    print(f"{'='*60}")
    
    for set_num, reserve_info in dashboard['emergency_reserves'].items():
        reserve_emoji = '[ALERT]' if reserve_info['in_reserve'] else '[U+1F6E1]️'
        print(f"   SET {set_num}: {reserve_emoji} Reserve: {reserve_info['reserve_amount']} units | "
              f"In Reserve: {'YES' if reserve_info['in_reserve'] else 'NO'}")


def print_detailed_costs():
    """Print operation costs reference."""
    quota_monitor = QuotaMonitor()
    
    print(f"\n{'='*60}")
    print("OPERATION COSTS REFERENCE")
    print(f"{'='*60}")
    
    # Group by cost level
    costs = quota_monitor.QUOTA_COSTS
    low_cost = {k: v for k, v in costs.items() if v <= 5}
    med_cost = {k: v for k, v in costs.items() if 5 < v <= 50}
    high_cost = {k: v for k, v in costs.items() if v > 50}
    
    print("\n[U+1F49A] LOW COST ([U+2264]5 units):")
    for op, cost in sorted(low_cost.items()):
        print(f"   {op}: {cost} units")
    
    print("\n[U+1F49B] MEDIUM COST (6-50 units):")
    for op, cost in sorted(med_cost.items()):
        print(f"   {op}: {cost} units")
    
    print("\n[U+1F4A5] HIGH COST (>50 units):")
    for op, cost in sorted(high_cost.items()):
        print(f"   {op}: {cost} units")


def interactive_menu():
    """Interactive dashboard menu."""
    quota_monitor = QuotaMonitor()
    quota_intelligence = QuotaIntelligence(quota_monitor)
    
    while True:
        print_banner()
        dashboard = quota_intelligence.get_quota_dashboard()
        print_quota_summary(dashboard)
        print_recommendations(dashboard)
        
        print(f"\n{'='*60}")
        print("DASHBOARD MENU")
        print(f"{'='*60}")
        print("1. Refresh Status")
        print("2. Show Emergency Reserves")
        print("3. Show Operation Costs")
        print("4. Test Operation (Check if allowed)")
        print("5. Plan Operation Batch")
        print("6. Export Data (JSON)")
        print("9. Exit")
        
        try:
            choice = input("\nSelect option (1-6, 9): ").strip()
            
            if choice == '1':
                continue  # Refresh
            elif choice == '2':
                print_emergency_reserves(dashboard)
                input("\nPress Enter to continue...")
            elif choice == '3':
                print_detailed_costs()
                input("\nPress Enter to continue...")
            elif choice == '4':
                test_operation_interactive(quota_intelligence)
            elif choice == '5':
                plan_batch_interactive(quota_intelligence)
            elif choice == '6':
                export_data(dashboard)
            elif choice == '9':
                print("\n[U+1F44B] Goodbye!")
                break
            else:
                print("[FAIL] Invalid choice. Please select 1-6 or 9.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n[U+1F44B] Goodbye!")
            break
        except Exception as e:
            print(f"\n[FAIL] Error: {e}")
            input("Press Enter to continue...")


def test_operation_interactive(quota_intelligence):
    """Interactive operation testing."""
    print(f"\n{'='*60}")
    print("TEST OPERATION")
    print(f"{'='*60}")
    
    # Show available operations
    print("\nCommon operations:")
    print("  channels.list, videos.list, liveChatMessages.list")
    print("  liveChatMessages.insert, search.list")
    
    try:
        operation = input("\nEnter operation (e.g., 'liveChatMessages.list'): ").strip()
        credential_set = int(input("Enter credential set (1 or 10): ").strip())
        count = int(input("Enter count (default 1): ").strip() or "1")
        
        result = quota_intelligence.can_perform_operation(operation, credential_set, count)
        
        print(f"\n[CLIPBOARD] OPERATION TEST RESULT:")
        print(f"   Operation: {operation}")
        print(f"   Credential Set: {credential_set}")
        print(f"   Count: {count}")
        print(f"   Cost: {result['cost']} units")
        print(f"   Allowed: {'[OK] YES' if result['allowed'] else '[FAIL] NO'}")
        print(f"   Reason: {result['reason']}")
        
        if result.get('suggestion'):
            print(f"   [IDEA] Suggestion: {result['suggestion']}")
        
        if result.get('warning'):
            print(f"   [U+26A0]️ Warning: {result['warning']}")
            
        if result.get('alternative'):
            print(f"   [REFRESH] Alternatives available: {len(result['alternative'])} options")
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
    
    input("\nPress Enter to continue...")


def plan_batch_interactive(quota_intelligence):
    """Interactive batch planning."""
    print(f"\n{'='*60}")
    print("PLAN OPERATION BATCH")
    print(f"{'='*60}")
    
    try:
        credential_set = int(input("Enter credential set (1 or 10): ").strip())
        operations = []
        
        print("\nEnter operations (press Enter with empty operation to finish):")
        while True:
            operation = input("  Operation: ").strip()
            if not operation:
                break
            count = int(input("  Count: ").strip() or "1")
            operations.append({'operation': operation, 'count': count})
        
        if not operations:
            print("No operations specified.")
            input("Press Enter to continue...")
            return
        
        plan = quota_intelligence.plan_operation_batch(operations, credential_set)
        
        print(f"\n[CLIPBOARD] BATCH EXECUTION PLAN:")
        print(f"   Total Cost: {plan['total_cost']} units")
        
        print(f"\n[OK] EXECUTABLE ({len(plan['executable'])} operations):")
        for op in plan['executable']:
            print(f"   • {op['operation']} x{op['count']} (cost: {op['cost']}, priority: {op['priority']})")
        
        if plan['deferred']:
            print(f"\n⏸️ DEFERRED ({len(plan['deferred'])} operations):")
            for op in plan['deferred']:
                print(f"   • {op['operation']} x{op.get('count', 1)}")
        
        if plan['blocked']:
            print(f"\n[FAIL] BLOCKED ({len(plan['blocked'])} operations):")
            for op in plan['blocked']:
                print(f"   • {op['operation']} x{op.get('count', 1)} - {op['reason']}")
        
        if plan['warnings']:
            print(f"\n[U+26A0]️ WARNINGS:")
            for warning in plan['warnings']:
                print(f"   • {warning}")
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
    
    input("\nPress Enter to continue...")


def export_data(dashboard):
    """Export dashboard data to JSON."""
    try:
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quota_dashboard_{timestamp}.json"
        
        with open(filename, 'w', encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2)
        
        print(f"\n[U+1F4BE] Data exported to: {filename}")
        
    except Exception as e:
        print(f"[FAIL] Export error: {e}")
    
    input("Press Enter to continue...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="YouTube API Quota Intelligence Dashboard")
    parser.add_argument('--summary', action='store_true', help='Show summary and exit')
    parser.add_argument('--costs', action='store_true', help='Show operation costs and exit')
    
    args = parser.parse_args()
    
    try:
        quota_monitor = QuotaMonitor()
        quota_intelligence = QuotaIntelligence(quota_monitor)
        dashboard = quota_intelligence.get_quota_dashboard()
        
        if args.summary:
            print_banner()
            print_quota_summary(dashboard)
            print_recommendations(dashboard)
            return
        
        if args.costs:
            print_banner()
            print_detailed_costs()
            return
        
        # Interactive mode
        interactive_menu()
        
    except KeyboardInterrupt:
        print("\n\n[U+1F44B] Goodbye!")
    except Exception as e:
        print(f"[FAIL] Dashboard error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()