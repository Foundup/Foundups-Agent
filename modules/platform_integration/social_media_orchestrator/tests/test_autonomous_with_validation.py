"""
AUTONOMOUS ENGAGEMENT WITH HUMAN VALIDATION LAYER
0102 executes → 012 validates → Pattern Memory learns

WSP 77 Phase 3: Human Supervision
Pattern Memory: Recursive Learning from Validated Outcomes
"""
import asyncio
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
import json

# Set repo_root to O:\Foundups-Agent (4 levels up from this file)
repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType
from modules.infrastructure.foundups_vision.src.action_pattern_learner import get_learner
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def ask_human_validation(action_name: str, expected_result: str) -> tuple:
    """
    Show popup for human validation (012 layer) with comment field

    Args:
        action_name: Action performed (e.g., "HEART")
        expected_result: What should have happened (e.g., "Heart turned RED")

    Returns:
        tuple: (bool: success, str: 012 comment)
    """
    root = tk.Tk()
    root.title(f"012 Validation - {action_name}")
    root.geometry("500x350")
    root.resizable(False, False)

    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (350 // 2)
    root.geometry(f"+{x}+{y}")

    result_var = tk.BooleanVar(value=False)
    submitted = tk.BooleanVar(value=False)

    # Header
    header = tk.Label(
        root,
        text=f"Did the action succeed?",
        font=("Arial", 14, "bold"),
        pady=10
    )
    header.pack()

    # Info frame
    info_frame = tk.Frame(root, padx=20, pady=10)
    info_frame.pack(fill="both")

    tk.Label(info_frame, text="Action:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
    tk.Label(info_frame, text=action_name, font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=10)

    tk.Label(info_frame, text="Expected:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
    expected_label = tk.Label(info_frame, text=expected_result, font=("Arial", 10), wraplength=350, justify="left")
    expected_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    # Comment section
    comment_label = tk.Label(root, text="012 Comments (optional):", font=("Arial", 10, "bold"), pady=10)
    comment_label.pack()

    comment_text = tk.Text(root, height=5, width=55, font=("Arial", 9), wrap="word")
    comment_text.pack(padx=20)
    comment_text.insert("1.0", "e.g., 'Icon did not change color' or 'Action worked perfectly'")
    comment_text.config(fg="gray")

    def on_focus_in(event):
        if comment_text.get("1.0", "end-1c") == "e.g., 'Icon did not change color' or 'Action worked perfectly'":
            comment_text.delete("1.0", "end")
            comment_text.config(fg="black")

    def on_focus_out(event):
        if not comment_text.get("1.0", "end-1c").strip():
            comment_text.insert("1.0", "e.g., 'Icon did not change color' or 'Action worked perfectly'")
            comment_text.config(fg="gray")

    comment_text.bind("<FocusIn>", on_focus_in)
    comment_text.bind("<FocusOut>", on_focus_out)

    # Button frame
    button_frame = tk.Frame(root, pady=15)
    button_frame.pack()

    def on_yes():
        result_var.set(True)
        submitted.set(True)
        root.quit()

    def on_no():
        result_var.set(False)
        submitted.set(True)
        root.quit()

    yes_btn = tk.Button(
        button_frame,
        text="YES - Success",
        command=on_yes,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        height=2
    )
    yes_btn.pack(side="left", padx=10)

    no_btn = tk.Button(
        button_frame,
        text="NO - Failed",
        command=on_no,
        bg="#f44336",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        height=2
    )
    no_btn.pack(side="left", padx=10)

    root.mainloop()

    # Get comment
    comment = comment_text.get("1.0", "end-1c").strip()
    if comment == "e.g., 'Icon did not change color' or 'Action worked perfectly'":
        comment = ""

    root.destroy()

    return (result_var.get(), comment)

async def test_autonomous_with_validation():
    print("\n" + "=" * 80)
    print(" AUTONOMOUS ENGAGEMENT WITH HUMAN VALIDATION")
    print(" 0102 Executes -> 012 Validates -> Pattern Memory Learns")
    print("=" * 80 + "\n")

    # Get pattern learner (singleton)
    learner = get_learner()
    print(f"[MEMORY] Pattern learner initialized with {len(learner._patterns)} learned patterns")

    # Step 1: Connect to existing Chrome on 9222
    print("\n[1] Connecting to existing Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[OK] Connected to Chrome")
        print(f"    Current URL: {driver.current_url}")

        # Find Studio tab
        tabs = driver.window_handles
        print(f"\n[2] Found {len(tabs)} tabs - switching to YouTube Studio...")

        for tab in tabs:
            driver.switch_to.window(tab)
            if "studio.youtube.com" in driver.current_url:
                print(f"[OK] Switched to Studio tab")
                break

    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        sys.exit(1)

    # Step 2: Create ActionRouter with existing driver
    print("\n[3] Creating ActionRouter with pre-connected driver...")
    router = ActionRouter(
        profile="youtube_move2japan",
        selenium_driver=driver,
        fallback_enabled=False
    )
    print("[OK] ActionRouter initialized")

    # Step 3: Define engagement actions
    actions = [
        {
            "name": "LIKE",
            "description": (
                "gray thumbs up icon in the comment action bar, located between the "
                "replies counter and thumbs down icon"
            ),
            "expected": "Thumbs up icon turned BLUE (filled)"
        },
        {
            "name": "HEART",
            "description": (
                "gray outlined heart icon in the comment action bar, located between "
                "thumbs down and three-dot menu"
            ),
            "expected": "Heart icon turned RED (filled)"
        },
        {
            "name": "REPLY",
            "description": "Reply button in the comment action bar",
            "expected": "Reply text box appeared below comment"
        }
    ]

    results = []

    try:
        # Step 4: Execute actions with validation loop
        for i, action in enumerate(actions, start=4):
            print(f"\n[{i}] 0102 EXECUTING: {action['name']}")
            print(f"    Description: {action['description'][:60]}...")

            # LEARNING: Show what we know from history
            learner.display_pre_learning(action['name'], 'youtube')

            # 0102: Execute action autonomously
            start_time = datetime.now()
            result = await router.execute(
                "click_element",
                {"description": action['description']},
                driver=DriverType.VISION,
            )
            execution_time = (datetime.now() - start_time).total_seconds()

            print(f"    Execution Result: {result.success}")
            print(f"    Execution Time: {execution_time:.2f}s")

            # Record success/failure in learner
            if result.success:
                learner.record_success(
                    action=action['name'],
                    platform='youtube',
                    driver='vision',
                    params={"description": action['description']},
                    duration_ms=execution_time * 1000,
                )
            else:
                learner.record_failure(
                    action=action['name'],
                    platform='youtube',
                    driver='vision',
                    params={"description": action['description']},
                )

            # Wait for UI update
            await asyncio.sleep(2)

            # 012: Human validates
            print(f"\n    [012 VALIDATION] Showing popup for human confirmation...")
            human_confirmed, comment_012 = ask_human_validation(action['name'], action['expected'])

            # Record human validation and show learning analysis
            learner.record_human_validation(
                action=action['name'],
                platform='youtube',
                driver='vision',
                params={"description": action['description']},
                human_success=human_confirmed,
                comment_012=comment_012,
            )

            # Display post-action learning (includes statistics)
            learner.display_post_learning(
                action=action['name'],
                platform='youtube',
                ai_success=result.success,
                human_success=human_confirmed,
                comment_012=comment_012,
            )

            # Track result for session summary
            results.append({
                "action": action['name'],
                "ai_success": result.success,
                "human_success": human_confirmed,
                "match": result.success == human_confirmed,
                "comment": comment_012,
            })

            await asyncio.sleep(1)

        # Step 5: Pattern memory is auto-saved by learner
        print(f"\n[{i+1}] Pattern learner auto-saved...")

        # Step 6: Analyze learning
        print("\n" + "=" * 80)
        print("LEARNING ANALYSIS")
        print("=" * 80)

        matches = sum(1 for p in results if p['match'])
        mismatches = len(results) - matches

        print(f"\nSession Results:")
        print(f"  Total Actions: {len(results)}")
        print(f"  AI-Human Agreement: {matches}/{len(results)}")
        print(f"  Mismatches: {mismatches}/{len(results)}")

        if mismatches > 0:
            print(f"\n  Calibration Needed:")
            for p in results:
                if not p['match']:
                    print(f"    - {p['action']}: AI={p['ai_success']}, Human={p['human_success']}")

        # Overall metrics from learner
        metrics = learner.get_metrics()
        print(f"\n  Total Patterns Learned: {metrics['total_patterns']}")
        print(f"  Overall Success Rate: {metrics.get('overall_success_rate', 0.0):.1%}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Autonomous + Validation + Learning Complete!")
        print("=" * 80)

        print(f"\nPattern memory stored in: {learner.storage_path}")
        print("Next session will learn from these validated patterns.")

    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await router.close()

        # Keep browser open for review
        print("\n[BROWSER] Staying open for 10 seconds for review...")
        await asyncio.sleep(10)
        driver.quit()

if __name__ == "__main__":
    asyncio.run(test_autonomous_with_validation())
