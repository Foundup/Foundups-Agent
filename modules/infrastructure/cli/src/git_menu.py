"""
Git Menu - Git operations submenu for FoundUps Agent CLI.

Extracted from main.py per WSP 62 (file size enforcement).
"""


def handle_git_menu(launch_git_push_dae, view_git_post_history) -> None:
    """Handle Git Operations submenu (WSP 91 compliant)."""
    print("\n[MENU] Git Operations")
    print("=" * 60)
    print("1. Push to Git + Post to LinkedIn/X")
    print("2. View Git Post History")
    print("0. Back to Main Menu")
    print("=" * 60)

    git_choice = input("\nSelect Git option: ").strip()

    if git_choice == "1":
        print("[DEBUG-MAIN] Calling launch_git_push_dae()...")
        # Run-once so the interactive menu is not blocked by a long-running daemon.
        launch_git_push_dae(run_once=True)
        print("[DEBUG-MAIN] Returned from launch_git_push_dae()")
    elif git_choice == "2":
        view_git_post_history()
    elif git_choice == "0":
        print("[BACK] Returning to main menu...")
    else:
        print("[ERROR] Invalid choice")
