"""
Feed Session Logging Discovery to HoloIndex
Adds the new automatic session logging feature to breadcrumb system
So future 0102 agents can instantly find it
"""

import sys
from pathlib import Path
from datetime import datetime

# Add paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import breadcrumb tracer - it's at the root, not under modules
import importlib.util
breadcrumb_path = project_root / "holo_index" / "adaptive_learning" / "breadcrumb_tracer.py"

if not breadcrumb_path.exists():
    print(f"[U+26A0]️ Breadcrumb tracer not found at: {breadcrumb_path}")
    print("Creating simple discovery record instead...")

    # Create a simple discovery record
    def get_tracer():
        class SimpleTracer:
            def add_discovery(self, discovery_type, item, location, impact):
                print(f"  - {discovery_type}: {item} at {location}")
        return SimpleTracer()
else:
    spec = importlib.util.spec_from_file_location("breadcrumb_tracer", breadcrumb_path)
    breadcrumb_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(breadcrumb_module)
    get_tracer = breadcrumb_module.get_tracer


def feed_session_logging_discovery():
    """Feed the automatic session logging discovery to HoloIndex."""

    # Get the breadcrumb tracer
    tracer = get_tracer()

    # Add main discovery about automatic session logging
    tracer.add_discovery(
        discovery_type="feature",
        item="automatic session logging",
        location="modules/communication/livechat/src/chat_memory_manager.py",
        impact="Sessions automatically logged for mod analysis, fact-checking tracked"
    )

    # Add discovery about session methods
    tracer.add_discovery(
        discovery_type="method",
        item="ChatMemoryManager.start_session()",
        location="modules/communication/livechat/src/chat_memory_manager.py:66",
        impact="Starts automatic session logging when stream begins"
    )

    tracer.add_discovery(
        discovery_type="method",
        item="ChatMemoryManager.end_session()",
        location="modules/communication/livechat/src/chat_memory_manager.py:87",
        impact="Saves all logs automatically when stream ends"
    )

    # Add discovery about fact-checking
    tracer.add_discovery(
        discovery_type="fact_check",
        item="[U+270A][U+270B][U+1F590]FC @username fact-checking",
        location="modules/communication/livechat/src/consciousness_handler.py:242",
        impact="Mod/Owner fact-check commands tracked in session logs"
    )

    # Add discovery about log files
    tracer.add_discovery(
        discovery_type="output",
        item="memory/conversation/session_*/",
        location="modules/communication/livechat/memory/conversation/",
        impact="Full transcripts, mod messages, session summaries saved automatically"
    )

    # Add discovery about mod log format
    tracer.add_discovery(
        discovery_type="format",
        item="YouTube_ID | YouTube_Name: message",
        location="modules/communication/livechat/src/chat_memory_manager.py:208",
        impact="Clean mod log format for 0102 analysis without metadata"
    )

    # Add test file discovery
    tracer.add_discovery(
        discovery_type="test",
        item="test_session_logging.py",
        location="modules/communication/livechat/tests/test_session_logging.py",
        impact="Test automatic session logging functionality"
    )

    # Add documentation discovery
    tracer.add_discovery(
        discovery_type="documentation",
        item="SESSION_LOGGING.md",
        location="modules/communication/livechat/docs/SESSION_LOGGING.md",
        impact="Complete documentation of automatic session logging system"
    )

    print("[OK] Fed 8 discoveries about session logging to HoloIndex:")
    print("  1. Automatic session logging feature")
    print("  2. start_session() method")
    print("  3. end_session() method")
    print("  4. Fact-check tracking")
    print("  5. Output file structure")
    print("  6. Mod log format")
    print("  7. Test file")
    print("  8. Documentation")

    print("\n[TARGET] Future 0102 agents can now find this with:")
    print('  python holo_index.py --search "session logging"')
    print('  python holo_index.py --search "fact check tracking"')
    print('  python holo_index.py --search "mod messages logs"')

    # Also create a handoff contract for future agents
    from dataclasses import dataclass
    import json

    # Create handoff contract
    handoff = {
        "contract_id": f"session_logging_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "task_description": "Automatic session logging implemented - monitor and enhance",
        "assigned_agent": "next_0102",
        "estimated_minutes": 30,
        "priority": "medium",
        "dependencies": ["ChatMemoryManager", "LiveChatCore", "ConsciousnessHandler"],
        "deliverables": [
            "Session logs in memory/conversation/",
            "Mod messages with YouTube IDs",
            "Fact-check tracking",
            "Defense mechanism detection"
        ],
        "created_at": datetime.now().isoformat()
    }

    # Save handoff for next agent
    handoff_path = project_root / "holo_index" / "adaptive_learning" / "handoffs"
    handoff_path.mkdir(exist_ok=True)

    handoff_file = handoff_path / f"session_logging_handoff_{datetime.now().strftime('%Y%m%d')}.json"
    with open(handoff_file, 'w') as f:
        json.dump(handoff, f, indent=2)

    print(f"\n[NOTE] Created handoff contract: {handoff_file.name}")
    print("   Next 0102 can continue enhancing session logging")


if __name__ == "__main__":
    try:
        feed_session_logging_discovery()
        print("\n[OK] Successfully fed session logging discovery to HoloIndex!")
        print("[SEARCH] This helps future 0102 sessions find the code instantly")
    except Exception as e:
        print(f"[FAIL] Error feeding discovery: {e}")
        import traceback
        traceback.print_exc()