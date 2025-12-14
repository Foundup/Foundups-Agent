"""
COPILOT VALIDATION - Pre-Action Human Confirmation
Agent shows intent → 012 confirms → Agent executes

Every agent step validated BEFORE execution
"""
import asyncio
import sys
import tkinter as tk
from pathlib import Path
from datetime import datetime
import json

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Validation log
VALIDATION_LOG = repo_root / "data" / "copilot_validation_log.json"

def load_validation_log():
    """Load validation history"""
    if VALIDATION_LOG.exists():
        with open(VALIDATION_LOG, 'r') as f:
            return json.load(f)
    return {"validations": []}

def save_validation_log(log):
    """Save validation history"""
    VALIDATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(VALIDATION_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def ask_012_confirmation(step_description: str, context: str = "") -> tuple:
    """
    Ask 012 to confirm agent intent BEFORE execution

    Args:
        step_description: What agent is about to do
        context: Additional context (optional)

    Returns:
        tuple: (str: action, str: comment)
                action: "approve", "reject", or "demonstrate"
    """
    root = tk.Tk()
    root.title("012 Copilot Confirmation")
    root.geometry("550x400")
    root.resizable(False, False)

    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (550 // 2)
    y = (root.winfo_screenheight() // 2) - (400 // 2)
    root.geometry(f"+{x}+{y}")

    action_var = tk.StringVar(value="reject")  # approve, reject, or demonstrate

    # Header
    header = tk.Label(
        root,
        text="Agent Ready to Execute",
        font=("Arial", 16, "bold"),
        fg="#1976D2",
        pady=15
    )
    header.pack()

    # Agent intent box
    intent_frame = tk.Frame(root, bg="#E3F2FD", padx=20, pady=15)
    intent_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(
        intent_frame,
        text="Agent Intent:",
        font=("Arial", 11, "bold"),
        bg="#E3F2FD"
    ).pack(anchor="w")

    intent_label = tk.Label(
        intent_frame,
        text=step_description,
        font=("Arial", 10),
        bg="#E3F2FD",
        wraplength=480,
        justify="left",
        pady=5
    )
    intent_label.pack(anchor="w")

    if context:
        tk.Label(
            intent_frame,
            text=f"Context: {context}",
            font=("Arial", 9, "italic"),
            bg="#E3F2FD",
            fg="#555"
        ).pack(anchor="w", pady=(5, 0))

    # Question
    question = tk.Label(
        root,
        text="Is browser showing the correct element?",
        font=("Arial", 12, "bold"),
        pady=10
    )
    question.pack()

    # Comment section
    comment_label = tk.Label(
        root,
        text="012 Comments (optional):",
        font=("Arial", 10, "bold"),
        pady=5
    )
    comment_label.pack()

    comment_text = tk.Text(root, height=4, width=60, font=("Arial", 9), wrap="word")
    comment_text.pack(padx=20, pady=5)
    comment_text.insert("1.0", "e.g., 'Wrong element highlighted' or 'Looks good'")
    comment_text.config(fg="gray")

    def on_focus_in(event):
        if comment_text.get("1.0", "end-1c") == "e.g., 'Wrong element highlighted' or 'Looks good'":
            comment_text.delete("1.0", "end")
            comment_text.config(fg="black")

    def on_focus_out(event):
        if not comment_text.get("1.0", "end-1c").strip():
            comment_text.insert("1.0", "e.g., 'Wrong element highlighted' or 'Looks good'")
            comment_text.config(fg="gray")

    comment_text.bind("<FocusIn>", on_focus_in)
    comment_text.bind("<FocusOut>", on_focus_out)

    # Button frame
    button_frame = tk.Frame(root, pady=15)
    button_frame.pack()

    def on_approve():
        action_var.set("approve")
        root.quit()

    def on_reject():
        action_var.set("reject")
        root.quit()

    def on_demonstrate():
        action_var.set("demonstrate")
        root.quit()

    approve_btn = tk.Button(
        button_frame,
        text="YES - Proceed",
        command=on_approve,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15,
        height=2
    )
    approve_btn.pack(side="left", padx=10)

    reject_btn = tk.Button(
        button_frame,
        text="NO - Stop",
        command=on_reject,
        bg="#FF9800",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15,
        height=2
    )
    reject_btn.pack(side="left", padx=10)

    demo_btn = tk.Button(
        button_frame,
        text="Let me show you",
        command=on_demonstrate,
        bg="#2196F3",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15,
        height=2
    )
    demo_btn.pack(side="left", padx=10)

    root.mainloop()

    # Get comment
    comment = comment_text.get("1.0", "end-1c").strip()
    if comment == "e.g., 'Wrong element highlighted' or 'Looks good'":
        comment = ""

    action = action_var.get()
    root.destroy()

    return (action, comment)

async def test_copilot_validation():
    print("\n" + "=" * 80)
    print(" COPILOT VALIDATION - Pre-Action Human Confirmation")
    print(" Agent Intent -> 012 Confirms -> Agent Executes")
    print("=" * 80 + "\n")

    # Load validation log
    log = load_validation_log()
    print(f"[LOG] Loaded {len(log['validations'])} previous validations")

    # Step 1: Connect to existing Chrome
    print("\n[1] Connecting to existing Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[OK] Connected to Chrome")

        # Find Studio tab
        tabs = driver.window_handles
        for tab in tabs:
            driver.switch_to.window(tab)
            if "studio.youtube.com" in driver.current_url:
                print(f"[OK] Switched to Studio tab")
                break

    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        sys.exit(1)

    # Step 2: Create ActionRouter
    print("\n[2] Creating ActionRouter...")
    router = ActionRouter(
        profile="youtube_move2japan",
        selenium_driver=driver,
        fallback_enabled=False
    )
    print("[OK] ActionRouter initialized")

    # Step 3: Define actions with copilot validation
    actions = [
        {
            "name": "LIKE",
            "description": (
                "gray thumbs up icon in the comment action bar, located between the "
                "replies counter and thumbs down icon"
            ),
            "intent": "Click LIKE button (thumbs up icon, 3rd from left)"
        },
        {
            "name": "HEART",
            "description": (
                "gray outlined heart icon in the comment action bar, located between "
                "thumbs down and three-dot menu"
            ),
            "intent": "Click HEART button (heart icon, between thumbs down and menu)"
        },
        {
            "name": "REPLY",
            "description": "Reply button in the comment action bar",
            "intent": "Click REPLY button to open reply text box"
        }
    ]

    validations = []

    try:
        # Step 4: Execute with copilot validation
        for i, action in enumerate(actions, start=4):
            print(f"\n[{i}] AGENT STEP: {action['name']}")
            print(f"    Intent: {action['intent']}")

            # PRE-ACTION: Ask 012 for confirmation
            print(f"\n    [COPILOT] Asking 012 to confirm agent intent...")
            action_012, comment_012 = ask_012_confirmation(
                action['intent'],
                f"Looking for: {action['description'][:80]}..."
            )

            # Log validation
            validation_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action['name'],
                "intent": action['intent'],
                "action_012": action_012,
                "comment_012": comment_012
            }

            if action_012 == "reject":
                print(f"    [STOP] 012 rejected - skipping action")
                if comment_012:
                    print(f"    [012 NOTE] {comment_012}")
                validation_entry["executed"] = False
                validation_entry["reason"] = "012 rejected"
                log['validations'].append(validation_entry)
                validations.append(validation_entry)
                continue

            elif action_012 == "demonstrate":
                print(f"    [LEARN] 012 will demonstrate correct action")
                print(f"    [INSTRUCTION] Manually click the correct element in the browser")
                print(f"    [INSTRUCTION] Press Enter in this console when done...")
                if comment_012:
                    print(f"    [012 NOTE] {comment_012}")
                validation_entry["executed"] = False
                validation_entry["reason"] = "012 demonstrated - pattern learned"
                log['validations'].append(validation_entry)
                validations.append(validation_entry)
                input("    Press Enter after manual demonstration...")
                print(f"    [OK] Demonstration complete - pattern saved")
                continue

            print(f"    [APPROVED] 012 confirmed - executing action...")
            if comment_012:
                print(f"    [012 NOTE] {comment_012}")

            # Execute ONLY if approved
            start_time = datetime.now()
            result = await router.execute(
                "click_element",
                {"description": action['description']},
                driver=DriverType.VISION,
            )
            execution_time = (datetime.now() - start_time).total_seconds()

            print(f"    [RESULT] Execution: {result.success} ({execution_time:.2f}s)")

            validation_entry["executed"] = True
            validation_entry["execution_success"] = result.success
            validation_entry["execution_time_seconds"] = execution_time

            log['validations'].append(validation_entry)
            validations.append(validation_entry)

            await asyncio.sleep(2)

        # Step 5: Save validation log
        print(f"\n[{i+1}] Saving validation log...")
        save_validation_log(log)
        print(f"[OK] Saved {len(log['validations'])} total validations")

        # Step 6: Summary
        print("\n" + "=" * 80)
        print("COPILOT SESSION SUMMARY")
        print("=" * 80)

        approved_count = sum(1 for v in validations if v['approved_012'])
        rejected_count = sum(1 for v in validations if not v['approved_012'])
        executed_count = sum(1 for v in validations if v.get('executed', False))
        success_count = sum(1 for v in validations if v.get('execution_success', False))

        print(f"\nValidations:")
        print(f"  Total Steps: {len(validations)}")
        print(f"  Approved by 012: {approved_count}/{len(validations)}")
        print(f"  Rejected by 012: {rejected_count}/{len(validations)}")
        print(f"  Executed: {executed_count}/{len(validations)}")
        print(f"  Successful: {success_count}/{executed_count if executed_count > 0 else 0}")

        if rejected_count > 0:
            print(f"\n  Rejected Actions:")
            for v in validations:
                if not v['approved_012']:
                    reason = v.get('comment_012', 'No comment')
                    print(f"    - {v['action']}: {reason}")

        print("\n" + "=" * 80)
        print("[SUCCESS] Copilot validation session complete!")
        print("=" * 80)

        print(f"\nValidation log saved to: {VALIDATION_LOG}")
        print("Next session will build on this validation history.")

    except Exception as e:
        print(f"\n[ERROR] Session failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await router.close()

        # Keep browser open for review
        print("\n[BROWSER] Staying open for 10 seconds for review...")
        await asyncio.sleep(10)
        driver.quit()

if __name__ == "__main__":
    asyncio.run(test_copilot_validation())
