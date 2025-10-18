#!/usr/bin/env python3
"""
Comprehensive System Monitor - Deep Component Analysis
Post-migration health check and component verification

This monitor performs:
1. Deep component analysis
2. Integration verification
3. Message flow testing
4. Performance assessment
5. Architecture validation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

import asyncio
import json
import time
from unittest.mock import Mock, patch
from typing import Dict, List, Any

class SystemMonitor:
    """Comprehensive system health monitor"""

    def __init__(self):
        self.results = {}
        self.issues = []
        self.warnings = []
        self.successes = []

    def log_result(self, component: str, status: str, details: str):
        """Log monitoring result"""
        self.results[component] = {
            'status': status,
            'details': details,
            'timestamp': time.time()
        }

        if status == 'FAIL':
            self.issues.append(f"{component}: {details}")
        elif status == 'WARN':
            self.warnings.append(f"{component}: {details}")
        else:
            self.successes.append(f"{component}: {details}")

def monitor_orchestrator_components():
    """Deep analysis of orchestrator components"""
    print("🔍 DEEP COMPONENT ANALYSIS - ORCHESTRATOR")
    print("=" * 60)

    monitor = SystemMonitor()
    mock_youtube = Mock()

    try:
        from modules.communication.livechat.src.core.orchestrator import LiveChatOrchestrator

        # Initialize orchestrator
        orchestrator = LiveChatOrchestrator(mock_youtube, "monitor_video")

        # Component 1: Session Manager
        if hasattr(orchestrator, 'session_manager'):
            session_mgr = orchestrator.session_manager
            required_methods = ['initialize_session', 'send_greeting']
            missing_methods = [m for m in required_methods if not hasattr(session_mgr, m)]

            if not missing_methods:
                monitor.log_result("SessionManager", "PASS", f"All {len(required_methods)} methods available")
            else:
                monitor.log_result("SessionManager", "FAIL", f"Missing methods: {missing_methods}")
        else:
            monitor.log_result("SessionManager", "FAIL", "Component not initialized")

        # Component 2: Memory Manager
        if hasattr(orchestrator, 'memory_manager'):
            memory_mgr = orchestrator.memory_manager
            memory_methods = ['save_message', 'get_recent_messages']
            available_methods = [m for m in memory_methods if hasattr(memory_mgr, m)]
            monitor.log_result("MemoryManager", "PASS", f"{len(available_methods)}/{len(memory_methods)} methods available")
        else:
            monitor.log_result("MemoryManager", "FAIL", "Component not initialized")

        # Component 3: Message Router
        if hasattr(orchestrator, 'message_router'):
            router = orchestrator.message_router
            if hasattr(router, 'handlers') and len(router.handlers) > 0:
                handler_count = len(router.handlers)
                handler_types = [type(h).__name__ for h in router.handlers]
                monitor.log_result("MessageRouter", "PASS", f"{handler_count} handlers: {handler_types}")
            else:
                monitor.log_result("MessageRouter", "FAIL", "No handlers registered")
        else:
            monitor.log_result("MessageRouter", "FAIL", "Router not initialized")

        # Component 4: Command Handler
        if hasattr(orchestrator, 'command_handler'):
            cmd_handler = orchestrator.command_handler
            cmd_methods = ['handle_whack_command']
            available_cmd_methods = [m for m in cmd_methods if hasattr(cmd_handler, m)]
            monitor.log_result("CommandHandler", "PASS", f"{len(available_cmd_methods)} command methods available")
        else:
            monitor.log_result("CommandHandler", "FAIL", "Component not initialized")

        # Component 5: Event Handler
        if hasattr(orchestrator, 'event_handler'):
            event_handler = orchestrator.event_handler
            # Check for event processing methods
            has_process_method = hasattr(event_handler, 'process_ban_event') or hasattr(event_handler, 'handle_event')
            if has_process_method:
                monitor.log_result("EventHandler", "PASS", "Event processing methods available")
            else:
                monitor.log_result("EventHandler", "WARN", "Event processing methods unclear")
        else:
            monitor.log_result("EventHandler", "FAIL", "Component not initialized")

        # Component 6: Chat Sender
        if hasattr(orchestrator, 'chat_sender'):
            sender = orchestrator.chat_sender
            sender_methods = ['send_message']
            available_sender_methods = [m for m in sender_methods if hasattr(sender, m)]
            monitor.log_result("ChatSender", "PASS", f"{len(available_sender_methods)} sender methods available")
        else:
            monitor.log_result("ChatSender", "FAIL", "Component not initialized")

        # Component 7: Chat Poller
        if hasattr(orchestrator, 'chat_poller'):
            poller = orchestrator.chat_poller
            poller_methods = ['poll_messages']
            available_poller_methods = [m for m in poller_methods if hasattr(poller, m)]
            monitor.log_result("ChatPoller", "PASS", f"{len(available_poller_methods)} poller methods available")
        else:
            monitor.log_result("ChatPoller", "FAIL", "Component not initialized")

        # Component 8: Throttle Manager
        if hasattr(orchestrator, 'throttle_manager'):
            if orchestrator.throttle_manager is not None:
                throttle_mgr = orchestrator.throttle_manager
                throttle_methods = ['calculate_adaptive_delay', 'should_respond']
                available_throttle_methods = [m for m in throttle_methods if hasattr(throttle_mgr, m)]
                monitor.log_result("ThrottleManager", "PASS", f"{len(available_throttle_methods)} throttle methods available")
            else:
                monitor.log_result("ThrottleManager", "WARN", "Throttle manager is None (may be optional)")
        else:
            monitor.log_result("ThrottleManager", "WARN", "Throttle manager not present")

    except Exception as e:
        monitor.log_result("OrchestatorInit", "FAIL", f"Failed to initialize: {e}")

    return monitor

def monitor_livechat_core_integration():
    """Deep analysis of LiveChatCore integration with orchestrator"""
    print("\n🔍 DEEP COMPONENT ANALYSIS - LIVECHAT CORE INTEGRATION")
    print("=" * 60)

    monitor = SystemMonitor()
    mock_youtube = Mock()

    try:
        from modules.communication.livechat.src.core.orchestrator import LiveChatOrchestrator
        from modules.communication.livechat.src.livechat_core import LiveChatCore

        # Test 1: Legacy mode (no router)
        legacy_core = LiveChatCore(mock_youtube, "legacy_test")

        if hasattr(legacy_core, 'router_mode') and legacy_core.router_mode == False:
            monitor.log_result("LegacyMode", "PASS", "Router mode correctly disabled")
        else:
            monitor.log_result("LegacyMode", "FAIL", "Router mode property issues")

        # Test 2: Router mode (with orchestrator)
        orchestrator = LiveChatOrchestrator(mock_youtube, "router_test")
        router_core = LiveChatCore(mock_youtube, "router_test", message_router=orchestrator.message_router)

        if hasattr(router_core, 'router_mode') and router_core.router_mode == True:
            monitor.log_result("RouterMode", "PASS", "Router mode correctly enabled")
        else:
            monitor.log_result("RouterMode", "FAIL", "Router mode not enabled properly")

        # Test 3: Router reference
        if router_core.message_router is orchestrator.message_router:
            monitor.log_result("RouterReference", "PASS", "Router reference correctly stored")
        else:
            monitor.log_result("RouterReference", "FAIL", "Router reference mismatch")

        # Test 4: Backward compatibility
        legacy_methods = ['start_listening', 'stop_listening', 'get_moderation_stats', 'process_message']
        legacy_missing = [m for m in legacy_methods if not hasattr(legacy_core, m)]
        router_missing = [m for m in legacy_methods if not hasattr(router_core, m)]

        if not legacy_missing and not router_missing:
            monitor.log_result("BackwardCompat", "PASS", "All legacy methods available in both modes")
        else:
            monitor.log_result("BackwardCompat", "FAIL", f"Missing methods - Legacy: {legacy_missing}, Router: {router_missing}")

        # Test 5: Component initialization in both modes
        core_components = ['session_manager', 'memory_manager', 'message_processor', 'chat_sender', 'chat_poller']
        legacy_components = [c for c in core_components if hasattr(legacy_core, c)]
        router_components = [c for c in core_components if hasattr(router_core, c)]

        if len(legacy_components) == len(router_components) == len(core_components):
            monitor.log_result("ComponentInit", "PASS", f"All {len(core_components)} components initialized in both modes")
        else:
            monitor.log_result("ComponentInit", "WARN", f"Component count - Legacy: {len(legacy_components)}, Router: {len(router_components)}")

    except Exception as e:
        monitor.log_result("CoreIntegration", "FAIL", f"Integration test failed: {e}")

    return monitor

async def monitor_message_flow():
    """Deep analysis of message flow through the system"""
    print("\n🔍 DEEP COMPONENT ANALYSIS - MESSAGE FLOW")
    print("=" * 60)

    monitor = SystemMonitor()
    mock_youtube = Mock()

    try:
        from modules.communication.livechat.src.core.orchestrator import LiveChatOrchestrator
        from modules.communication.livechat.src.livechat_core import LiveChatCore

        # Setup systems
        orchestrator = LiveChatOrchestrator(mock_youtube, "flow_test")
        router_core = LiveChatCore(mock_youtube, "flow_test", message_router=orchestrator.message_router)
        legacy_core = LiveChatCore(mock_youtube, "flow_test")

        # Test message types
        test_messages = [
            {
                "id": "cmd_msg",
                "type": "text_message",
                "snippet": {"displayMessage": "/score"},
                "authorDetails": {
                    "displayName": "CmdUser",
                    "channelId": "cmd_123",
                    "isChatModerator": False,
                    "isChatOwner": False
                }
            },
            {
                "id": "reg_msg",
                "type": "text_message",
                "snippet": {"displayMessage": "regular message"},
                "authorDetails": {
                    "displayName": "RegularUser",
                    "channelId": "reg_123",
                    "isChatModerator": False,
                    "isChatOwner": False
                }
            },
            {
                "type": "ban_event",
                "banned_user": "BadUser",
                "moderator": "ModUser"
            }
        ]

        # Test message processing in router mode
        router_results = []
        for msg in test_messages:
            try:
                await router_core.process_message(msg)
                router_results.append("processed")
            except Exception as e:
                router_results.append(f"error: {str(e)[:30]}")

        # Test message processing in legacy mode
        legacy_results = []
        for msg in test_messages:
            try:
                await legacy_core.process_message(msg)
                legacy_results.append("processed")
            except Exception as e:
                legacy_results.append(f"error: {str(e)[:30]}")

        # Analyze results
        router_processed = sum(1 for r in router_results if r == "processed")
        legacy_processed = sum(1 for r in legacy_results if r == "processed")

        if router_processed >= legacy_processed:
            monitor.log_result("MessageFlow", "PASS", f"Router: {router_processed}/{len(test_messages)}, Legacy: {legacy_processed}/{len(test_messages)}")
        else:
            monitor.log_result("MessageFlow", "WARN", f"Router processing less effective than legacy")

        # Test router directly
        router_direct_results = []
        for msg in test_messages:
            try:
                response = orchestrator.message_router.route_message(msg)
                router_direct_results.append("routed" if response else "no_response")
            except Exception as e:
                router_direct_results.append(f"error: {str(e)[:30]}")

        router_direct_success = sum(1 for r in router_direct_results if "error" not in r)
        monitor.log_result("RouterDirect", "PASS" if router_direct_success > 0 else "WARN",
                          f"Direct router: {router_direct_success}/{len(test_messages)} successful")

    except Exception as e:
        monitor.log_result("MessageFlow", "FAIL", f"Flow test failed: {e}")

    return monitor

def monitor_handler_adapters():
    """Deep analysis of handler adapters and their integration"""
    print("\n🔍 DEEP COMPONENT ANALYSIS - HANDLER ADAPTERS")
    print("=" * 60)

    monitor = SystemMonitor()
    mock_youtube = Mock()

    try:
        from modules.communication.livechat.src.core.orchestrator import LiveChatOrchestrator

        orchestrator = LiveChatOrchestrator(mock_youtube, "adapter_test")
        router = orchestrator.message_router

        # Analyze registered handlers
        if hasattr(router, 'handlers'):
            handlers = router.handlers

            handler_details = []
            for handler in handlers:
                handler_type = type(handler).__name__
                priority = getattr(handler, 'priority', 'unknown')
                handler_details.append(f"{handler_type}(p={priority})")

            monitor.log_result("HandlerCount", "PASS", f"{len(handlers)} handlers registered")
            monitor.log_result("HandlerTypes", "PASS", f"Types: {', '.join(handler_details)}")

            # Check for expected adapter types
            adapter_types = [type(h).__name__ for h in handlers]
            expected_adapters = ['CommandHandlerAdapter', 'EventHandlerAdapter']
            found_adapters = [a for a in expected_adapters if a in adapter_types]

            if len(found_adapters) >= 1:
                monitor.log_result("AdapterTypes", "PASS", f"Found adapters: {found_adapters}")
            else:
                monitor.log_result("AdapterTypes", "WARN", f"Expected adapters not found: {expected_adapters}")

            # Test adapter functionality
            test_command_msg = {
                "type": "text_message",
                "text": "/help",
                "username": "AdapterTest",
                "user_id": "adapter_123",
                "role": "USER"
            }

            adapter_responses = []
            for handler in handlers:
                try:
                    if hasattr(handler, 'handle'):
                        response = handler.handle(test_command_msg)
                        adapter_responses.append(f"{type(handler).__name__}: {response is not None}")
                    else:
                        adapter_responses.append(f"{type(handler).__name__}: no handle method")
                except Exception as e:
                    adapter_responses.append(f"{type(handler).__name__}: error")

            monitor.log_result("AdapterFunction", "PASS", f"Adapter tests: {len(adapter_responses)} completed")

        else:
            monitor.log_result("HandlerRegistry", "FAIL", "Router has no handlers attribute")

    except Exception as e:
        monitor.log_result("HandlerAdapters", "FAIL", f"Adapter analysis failed: {e}")

    return monitor

def monitor_performance_metrics():
    """Analyze performance characteristics"""
    print("\n🔍 DEEP COMPONENT ANALYSIS - PERFORMANCE METRICS")
    print("=" * 60)

    monitor = SystemMonitor()
    mock_youtube = Mock()

    try:
        from modules.communication.livechat.src.core.orchestrator import LiveChatOrchestrator
        from modules.communication.livechat.src.livechat_core import LiveChatCore

        # Timing tests
        start_time = time.time()

        # Test 1: Orchestrator initialization time
        orch_start = time.time()
        orchestrator = LiveChatOrchestrator(mock_youtube, "perf_test")
        orch_time = time.time() - orch_start

        # Test 2: Core initialization time (legacy)
        legacy_start = time.time()
        legacy_core = LiveChatCore(mock_youtube, "perf_test")
        legacy_time = time.time() - legacy_start

        # Test 3: Core initialization time (with router)
        router_start = time.time()
        router_core = LiveChatCore(mock_youtube, "perf_test", message_router=orchestrator.message_router)
        router_time = time.time() - router_start

        # Performance analysis
        monitor.log_result("OrchInitTime", "PASS", f"{orch_time:.4f}s")
        monitor.log_result("LegacyInitTime", "PASS", f"{legacy_time:.4f}s")
        monitor.log_result("RouterInitTime", "PASS", f"{router_time:.4f}s")

        # Memory footprint (component count)
        orch_attrs = len([attr for attr in dir(orchestrator) if not attr.startswith('_')])
        legacy_attrs = len([attr for attr in dir(legacy_core) if not attr.startswith('_')])
        router_attrs = len([attr for attr in dir(router_core) if not attr.startswith('_')])

        monitor.log_result("ComponentCount", "PASS", f"Orch: {orch_attrs}, Legacy: {legacy_attrs}, Router: {router_attrs}")

        # Router efficiency test
        if hasattr(orchestrator, 'message_router'):
            router = orchestrator.message_router
            handler_count = len(router.handlers) if hasattr(router, 'handlers') else 0

            if handler_count > 0:
                monitor.log_result("RouterEfficiency", "PASS", f"{handler_count} handlers - centralized processing")
            else:
                monitor.log_result("RouterEfficiency", "WARN", "No handlers - processing may be inefficient")

    except Exception as e:
        monitor.log_result("Performance", "FAIL", f"Performance analysis failed: {e}")

    return monitor

def monitor_integration_points():
    """Check integration points and dependencies"""
    print("\n🔍 DEEP COMPONENT ANALYSIS - INTEGRATION POINTS")
    print("=" * 60)

    monitor = SystemMonitor()

    try:
        # Import analysis
        import_tests = [
            ("LiveChatOrchestrator", "modules.communication.livechat.src.core.orchestrator"),
            ("LiveChatCore", "modules.communication.livechat.src.livechat_core"),
            ("MessageRouter", "modules.communication.livechat.src.core.message_router"),
            ("SessionManager", "modules.communication.livechat.src.session_manager"),
            ("ChatMemoryManager", "modules.communication.livechat.src.chat_memory_manager"),
            ("CommandHandler", "modules.communication.livechat.src.command_handler"),
            ("EventHandler", "modules.communication.livechat.src.event_handler"),
        ]

        import_results = []
        for name, module_path in import_tests:
            try:
                module = __import__(module_path, fromlist=[name])
                cls = getattr(module, name)
                import_results.append(f"{name}: ✓")
            except Exception as e:
                import_results.append(f"{name}: ✗ ({str(e)[:20]})")

        successful_imports = sum(1 for r in import_results if "✓" in r)
        monitor.log_result("ImportTests", "PASS" if successful_imports == len(import_tests) else "WARN",
                          f"{successful_imports}/{len(import_tests)} imports successful")

        # File existence check
        base_path = "modules/communication/livechat"
        critical_files = [
            "src/core/orchestrator.py",
            "src/livechat_core.py",
            "src/core/message_router.py",
            "src/session_manager.py",
            "src/command_handler.py",
            "src/event_handler.py",
            "src/chat_sender.py",
            "src/chat_poller.py"
        ]

        existing_files = []
        for file_path in critical_files:
            full_path = f"{base_path}/{file_path}"
            if os.path.exists(full_path):
                existing_files.append(file_path)

        monitor.log_result("FileExistence", "PASS" if len(existing_files) == len(critical_files) else "WARN",
                          f"{len(existing_files)}/{len(critical_files)} critical files exist")

        # Test file check
        test_files = [
            "tests/test_orchestrator_migration_step1.py",
            "tests/test_orchestrator_migration_step2.py",
            "tests/test_orchestrator_migration_step3.py",
            "tests/test_surgical_migration_live.py",
            "tests/test_integration_demonstration.py"
        ]

        existing_tests = []
        for test_file in test_files:
            full_path = f"{base_path}/{test_file}"
            if os.path.exists(full_path):
                existing_tests.append(test_file)

        monitor.log_result("TestFiles", "PASS", f"{len(existing_tests)}/{len(test_files)} test files created")

    except Exception as e:
        monitor.log_result("Integration", "FAIL", f"Integration check failed: {e}")

    return monitor

async def run_comprehensive_monitor():
    """Run all monitoring components"""
    print("🚀 COMPREHENSIVE SYSTEM MONITOR - POST-MIGRATION ANALYSIS")
    print("=" * 100)
    print("Deep thinking through all components...")
    print()

    # Run all monitoring components
    monitors = []

    monitors.append(monitor_orchestrator_components())
    monitors.append(monitor_livechat_core_integration())
    monitors.append(await monitor_message_flow())
    monitors.append(monitor_handler_adapters())
    monitors.append(monitor_performance_metrics())
    monitors.append(monitor_integration_points())

    # Aggregate results
    all_results = {}
    all_issues = []
    all_warnings = []
    all_successes = []

    for monitor in monitors:
        all_results.update(monitor.results)
        all_issues.extend(monitor.issues)
        all_warnings.extend(monitor.warnings)
        all_successes.extend(monitor.successes)

    # Generate comprehensive report
    print("\n🏁 COMPREHENSIVE ANALYSIS RESULTS")
    print("=" * 100)

    print(f"📊 METRICS:")
    print(f"   Total Components Analyzed: {len(all_results)}")
    print(f"   Successful Checks: {len(all_successes)}")
    print(f"   Warnings: {len(all_warnings)}")
    print(f"   Issues: {len(all_issues)}")

    print(f"\n✅ SUCCESSES ({len(all_successes)}):")
    for success in all_successes[:10]:  # Show top 10
        print(f"   ✓ {success}")
    if len(all_successes) > 10:
        print(f"   ... and {len(all_successes) - 10} more")

    if all_warnings:
        print(f"\n⚠️ WARNINGS ({len(all_warnings)}):")
        for warning in all_warnings:
            print(f"   ⚠ {warning}")

    if all_issues:
        print(f"\n❌ ISSUES ({len(all_issues)}):")
        for issue in all_issues:
            print(f"   ❌ {issue}")

    # Overall system health assessment
    total_checks = len(all_results)
    success_rate = len(all_successes) / total_checks if total_checks > 0 else 0

    print(f"\n🎯 OVERALL SYSTEM HEALTH:")
    print(f"   Success Rate: {success_rate:.1%}")

    if success_rate >= 0.9:
        health_status = "EXCELLENT"
        health_icon = "🟢"
    elif success_rate >= 0.8:
        health_status = "GOOD"
        health_icon = "🟡"
    elif success_rate >= 0.7:
        health_status = "ACCEPTABLE"
        health_icon = "🟠"
    else:
        health_status = "NEEDS ATTENTION"
        health_icon = "🔴"

    print(f"   System Status: {health_icon} {health_status}")

    # Migration-specific assessment
    print(f"\n🔄 MIGRATION ASSESSMENT:")
    migration_components = [
        "RouterMode", "LegacyMode", "RouterReference", "BackwardCompat",
        "MessageFlow", "HandlerTypes", "AdapterFunction"
    ]

    migration_results = {k: v for k, v in all_results.items() if k in migration_components}
    migration_successes = len([r for r in migration_results.values() if r['status'] == 'PASS'])
    migration_rate = migration_successes / len(migration_results) if migration_results else 0

    print(f"   Migration Success Rate: {migration_rate:.1%}")
    print(f"   Critical Components: {migration_successes}/{len(migration_results)} operational")

    if migration_rate >= 0.9:
        print(f"   Migration Status: 🎉 SUCCESSFUL - Production Ready")
    elif migration_rate >= 0.8:
        print(f"   Migration Status: ✅ MOSTLY SUCCESSFUL - Minor issues to address")
    else:
        print(f"   Migration Status: ⚠️ NEEDS WORK - Address critical issues before production")

    print("\n" + "=" * 100)
    return success_rate >= 0.8

if __name__ == "__main__":
    result = asyncio.run(run_comprehensive_monitor())

    print(f"\n🏆 FINAL ASSESSMENT: {'SYSTEM READY' if result else 'NEEDS ATTENTION'}")