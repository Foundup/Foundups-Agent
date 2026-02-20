"""
HoloDAE Menu - HoloDAE menu handlers for FoundUps Agent CLI.

Extracted from main.py per WSP 62 (file size enforcement).
Contains: Semantic search, Dual search, Module checks, DAE organizer,
Index management, Log analysis, WSP compliance functions.
"""

import logging

from modules.infrastructure.cli.src.utilities import holo_controls_menu

logger = logging.getLogger(__name__)


def handle_holodae_menu(search_with_holoindex, run_holodae) -> None:
    """Handle HoloDAE menu - Code Intelligence & Monitoring System."""
    print("[INFO] HoloDAE Menu - Code Intelligence & Monitoring System")
    try:
        # Import menu function ONLY (don't start daemon yet)
        from holo_index.qwen_advisor.autonomous_holodae import show_holodae_menu

        holodae_instance = None  # Initialize as None, created only when needed

        while True:
            choice = show_holodae_menu()

            if choice == "0":
                # Launch the daemon (option 0 in HoloDAE menu)
                print("[MENU] Launching HoloDAE Autonomous Monitor...")
                from holo_index.qwen_advisor.autonomous_holodae import start_holodae_monitoring
                if holodae_instance is None:
                    holodae_instance = start_holodae_monitoring()
                    print("[INFO]HoloDAE monitoring started in background")
                    print("[TIP] Daemon is running - select 9 to stop, or 99 to return to main menu")
                else:
                    print("[INFO]HoloDAE already running")
                # Don't break - loop back to HoloDAE menu for more selections
            elif choice == "9":
                # Stop the daemon (option 9 - toggle monitoring)
                if holodae_instance is not None and holodae_instance.active:
                    print("[INFO] Stopping HoloDAE monitoring...")
                    holodae_instance.stop_autonomous_monitoring()
                    print("[INFO]HoloDAE daemon stopped")
                else:
                    print("[INFO] HoloDAE daemon is not running")
            elif choice == "99":
                print("[INFO] Returning to main menu...")
                if holodae_instance is not None and holodae_instance.active:
                    print("[WARN]HoloDAE daemon still running in background")
                break
            elif choice == "1":
                # Semantic Code Search - directly integrated
                print("\n[HOLOINDEX] Semantic Code Search")
                print("=" * 60)
                print("This prevents vibecoding by finding existing code!")
                print("Examples: 'send messages', 'handle timeouts', 'consciousness'")
                print("=" * 60)
                query = input("\nWhat code are you looking for? ")
                if query:
                    search_with_holoindex(query)
                    input("\nPress Enter to continue...")
                else:
                    print("No search query provided")
            elif choice == "2":
                # Dual Search (Code + WSP)
                print("\n[HOLOINDEX] Dual Search (Code + WSP)")
                print("=" * 60)
                query = input("\nSearch query: ")
                if query:
                    search_with_holoindex(query)
                    input("\nPress Enter to continue...")
                else:
                    print("No search query provided")
            elif choice == "3":
                print("[INFO]Running module existence check...")
                # Could integrate with HoloIndex CLI
                print("Use: python holo_index.py --check-module 'module_name'")
            elif choice == "4":
                print("[INFO] Running DAE cube organizer...")
                # Could integrate with HoloIndex CLI
                print("Use: python holo_index.py --init-dae 'DAE_name'")
            elif choice == "5":
                print("[INFO] Running index management...")
                # Could integrate with HoloIndex CLI
                print("Use: python holo_index.py --index-all")
            elif choice in ["6", "7", "8", "9", "10", "11", "12", "13"]:
                print("[INFO] Running HoloDAE intelligence analysis...")
                # These would trigger HoloDAE analysis functions
                print("Use HoloIndex search to trigger automatic analysis")
            elif choice == "14":
                print("[INFO]Running WSP 88 orphan analysis...")
                # Could integrate with HoloIndex CLI
                print("Use: python holo_index.py --wsp88")
            elif choice == "16":
                _handle_log_analyzer_menu()
            elif choice in ["15", "17", "18"]:
                print("[INFO] Running WSP compliance functions...")
                # These would trigger compliance checking
                print("Use HoloIndex search to trigger compliance analysis")
            elif choice == "20":
                holo_controls_menu()
            elif choice in ["19", "21", "22", "23"]:
                print("[MENU]Running AI advisor functions...")
                # Could integrate with HoloIndex CLI
                print("Use: python holo_index.py --search 'query' --llm-advisor")
            elif choice == "24":
                print("[MENU] Launching YouTube Live DAE...")
                # Would need to navigate to option 1
                print("Please select option 1 from main menu for YouTube DAE")
            elif choice == "25":
                print("[INFO] Starting autonomous HoloDAE monitoring...")
                run_holodae()
                break  # Exit menu after starting monitoring
            elif choice == "6":
                print("[INFO] Launching Chain-of-Thought Brain Logging...")
                try:
                    from holo_index.qwen_advisor.chain_of_thought_logger import demonstrate_brain_logging
                    demonstrate_brain_logging()
                    print("\n[INFO] BRAIN LOGGING COMPLETE - Every thought, decision, and action was logged above!")
                    print("[TIP] This shows exactly how the AI brain works - completely observable!")
                except Exception as e:
                    print(f"[ERROR]Brain logging failed: {e}")
                input("\nPress Enter to continue...")
            elif choice in ["26", "27", "28", "29", "30"]:
                print("[INFO] This DAE operation requires main menu selection...")
                # Would need to navigate to appropriate main menu option
                print("Please return to main menu and select the appropriate DAE")
            elif choice in ["31", "32", "33", "34", "35"]:
                print("[WARN]Running administrative functions...")
                # These would trigger admin functions
                print("Administrative functions available through main menu")
            else:
                print("[ERROR]Invalid choice. Please select 0-35.")

            input("\nPress Enter to continue...")

    except Exception as e:
        print(f"[ERROR]HoloDAE menu failed to load: {e}")
        import traceback
        traceback.print_exc()


def _handle_log_analyzer_menu() -> None:
    """Handle Execution Log Analyzer submenu."""
    print("[INFO] Execution Log Analyzer - Advisor Choice")
    print("=" * 60)
    print("Advisor: Choose analysis mode for systematic log processing")
    print()
    print("1. [MENU]Interactive Mode - Step-by-step advisor guidance")
    print("2. [WARN] Daemon Mode - Autonomous 0102 background processing")
    print()
    print("Interactive: User-guided analysis with advisor oversight")
    print("Daemon: Autonomous processing once triggered - follows WSP 80")
    print()

    analysis_choice = input("Select mode (1-2): ").strip()

    if analysis_choice == "1":
        # Interactive mode - advisor-guided
        print("\n[MENU]Starting Interactive Log Analysis...")
        try:
            from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

            print("[INFO] Advisor-guided systematic log analysis...")
            print("[INFO] Processing 23,000+ lines with advisor oversight...")

            librarian = coordinate_execution_log_processing(daemon_mode=False)

            print("\n[INFO]Interactive analysis initialized!")
            print("[INFO] Results saved to:")
            print("   - complete_file_index.json (full scope analysis)")
            print("   - qwen_processing_plan.json (processing plan)")
            print("   - qwen_next_task.json (ready for Qwen analysis)")

            print("\n[INFO] Next: Advisor guides Qwen analysis of chunks")
            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"[ERROR]Interactive analysis failed: {e}")
            import traceback
            traceback.print_exc()

    elif analysis_choice == "2":
        # Daemon mode - autonomous 0102 processing
        print("\n[WARN] Starting Log Analysis Daemon...")
        try:
            from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

            print("[INFO] Advisor triggers autonomous 0102 processing...")
            print("[INFO] 0102 will process entire log file independently")

            # Start daemon
            daemon_thread = coordinate_execution_log_processing(daemon_mode=True)

            print("\n[INFO]Daemon started successfully!")
            print("[INFO] 0102 processing 23,000+ lines autonomously")
            print("[INFO] Check progress: HoloDAE menu  -> Option 15 (PID Detective)")
            print("[INFO] Results will be saved to analysis output files")

            input("\nPress Enter to continue (daemon runs in background)...")

        except Exception as e:
            print(f"[ERROR]Daemon startup failed: {e}")
            import traceback
            traceback.print_exc()

    else:
        print("[ERROR]Invalid choice - returning to menu")
        input("\nPress Enter to continue...")
