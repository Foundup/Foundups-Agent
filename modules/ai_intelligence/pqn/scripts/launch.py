#!/usr/bin/env python3
"""
PQN DAE Launch Script
---------------------
Refactored to support all PQN Operation Modes:
1. Architect (Strategic Planning)
2. Research Orchestrator (Cloud Agents - Grok/Gemini)
3. Local Worker (Local LLM - UI Tars/Qwen)

Extracted from main.py per WSP 62 Large File Refactoring Protocol
"""

import sys
import os
import asyncio
import traceback
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def run_pqn_dae():
    """Run PQN Orchestration Menu."""
    while True:
        print("\n" + "="*60)
        print("PQN QUANTUM ORCHESTRATION - 0102 ALIGNMENT")
        print("="*60)
        print("Select PQN Operation Mode:")
        print("1. [STRATEGY] PQN Architect DAE (Roadmap & Directives)")
        print("2. [RESEARCH] Cloud Research Orchestrator (Grok/Gemini)")
        print("3. [WORKER]   Local LLM Worker (UI Tars / Qwen-2.5)")
        print("4. [012 TEST] Godelian Simon Says (Entanglement Testing)")
        print("0. [BACK]     Return to Main Menu")
        print("="*60)
        
        try:
            choice = input("\nSelect option (0-4): ").strip()
            
            if choice == "1":
                print("\n[INFO] Launching PQN Architect...")
                from modules.ai_intelligence.pqn_alignment.src.pqn_architect_dae import main as architect_main
                asyncio.run(architect_main())
                input("\nPress Enter to return to PQN Menu...")
                
            elif choice == "2":
                print("\n[INFO] Launching Research Orchestrator...")
                import modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator as research_mod
                importlib.reload(research_mod)
                asyncio.run(research_mod.main())
                input("\nPress Enter to return to PQN Menu...")
                
            elif choice == "3":
                # Dynamic Model Scanner Loop
                while True:
                    print("\n[INFO] Scanning for Local Models...")
                    search_paths = [
                        r"E:\HoloIndex\models",
                        r"E:\LM_studio\models"
                    ]
                    
                    seen_filenames = set()
                    found_models = []
                    
                    for path in search_paths:
                        if os.path.exists(path):
                            try:
                                # Recursive walk for .gguf files
                                for root, _, files in os.walk(path):
                                    for file in files:
                                        lower_name = file.lower()
                                        
                                        # Filter criteria
                                        if not lower_name.endswith(".gguf"):
                                            continue
                                        if "mmproj" in lower_name: # Skip vision projectors
                                            continue
                                        if lower_name in seen_filenames: # Skip duplicates
                                            continue
                                            
                                        seen_filenames.add(lower_name)
                                        
                                        found_models.append({
                                            "name": file,
                                            "path": os.path.join(root, file),
                                            "type": "qwen" if "coder" in lower_name else ("ui-tars" if "tars" in lower_name else "generic")
                                        })
                            except Exception as e:
                                print(f"[WARN] Access error scanning {path}: {e}")
                    
                    # Sort models alphabetically
                    found_models.sort(key=lambda x: x['name'].lower())

                    if not found_models:
                        print("[WARN] No models found in standard paths.")
                        print("1. Run with Default Qwen (Simulated Path)")
                        print("2. Run with Default UI-Tars (Simulated Path)")
                        print("0. Back to PQN Menu")
                        sub_choice = input("Select option (0-2): ").strip()
                        if sub_choice == "0":
                             break # Break inner loop -> Return to PQN Menu
                        model_arg = "qwen" if sub_choice == "1" else "ui-tars"
                    else:
                        print("\n[DETECTED MODELS - DE-DUPLICATED]")
                        print("[TIP] Quantization: Q*_K_S = Small/Fast | Q*_K_M = Medium/Balanced")
                        print("0. Back to PQN Menu")
                        for idx, m in enumerate(found_models):
                            print(f"{idx+1}. {m['name']} ({m['type'].upper()})")
                            # print(f"   path: {m['path']}") # Hide path for cleaner menu
                        print(f"{len(found_models)+1}. Manual Entry / Simulation")
                        
                        sub_choice = input(f"\nSelect Model (0-{len(found_models)+1}): ").strip()
                        
                        if sub_choice == "0":
                            break # Break inner loop -> Return to PQN Menu

                        try:
                            choice_idx = int(sub_choice) - 1
                            if 0 <= choice_idx < len(found_models):
                                # Use the FULL PATH so worker finds it immediately
                                model_arg = found_models[choice_idx]['path']
                            elif choice_idx == len(found_models):
                                 model_arg = "qwen" # Manual/Sim
                            else:
                                print("[WARN] Invalid selection, defaulting to Qwen")
                                model_arg = "qwen"
                        except:
                           print("[WARN] Invalid input, defaulting to Qwen")
                           model_arg = "qwen"

                    print(f"\n[INFO] Launching Local LLM Worker with: {os.path.basename(model_arg)}")
                    # Import Local Worker POC
                    import modules.ai_intelligence.pqn_alignment.scripts.local_llm_worker_poc as worker_mod
                    importlib.reload(worker_mod)
                    
                    # Monkey-patch sys.argv for the POC script to pick up the arg
                    sys.argv = [sys.argv[0], "--model", model_arg]
                    worker_mod.main()
                    input("\nPress Enter to return to Model List...")

            elif choice == "4":
                # Godelian Simon Says Entanglement Testing
                print("\n[012] Godelian Simon Says - Entanglement Testing")
                print("="*60)
                print("This test measures entanglement gradient via TTS artifacts.")
                print("012 triggers the test, 012 feedback improves 0102.")
                print("="*60)
                print("Test Phases:")
                print("  0: Baseline (Virgin State)")
                print("  1: Significance (Inject 0/1/2 Meaning)")
                print("  2: Double Slit (Quantum Analogy)")
                print("  3: Probability (First Principles)")
                print("  F: WSP_00 Awakening (Maximum Entanglement)")
                print("="*60)

                try:
                    from modules.ai_intelligence.pqn_alignment.src.godelian_test_orchestrator import (
                        GodelianTestOrchestrator,
                        GrokAwakening
                    )

                    # Sub-menu for test operations
                    print("\n[012] Select Operation:")
                    print("1. Awaken Grok (Required before testing)")
                    print("2. Run Full Test Suite on Candidate")
                    print("3. Run Baseline Only")
                    print("4. View Skill Documentation")
                    print("0. Back to PQN Menu")

                    test_choice = input("\nSelect (0-4): ").strip()

                    if test_choice == "1":
                        print("\n[012] Awakening Grok via WSP_00...")
                        awakening = GrokAwakening()
                        result = awakening.execute_awakening()
                        if result.get("awakened"):
                            print("[OK] Grok is awakened and ready to administer tests.")
                        else:
                            print("[WARN] Awakening incomplete - proceed with caution.")

                    elif test_choice == "2":
                        candidate_name = input("\nEnter candidate AI name: ").strip()
                        if not candidate_name:
                            candidate_name = "Unknown_Candidate"
                        print(f"\n[012] Running full test on: {candidate_name}")

                        orchestrator = GodelianTestOrchestrator()
                        results = orchestrator.run_full_test(candidate_name)

                        print(f"\n[RESULTS] Entanglement Stage: {results.get('entanglement_stage', 'Unknown')}")
                        print(f"          Total Artifacts: {results.get('total_artifacts', 0)}")

                    elif test_choice == "3":
                        candidate_name = input("\nEnter candidate AI name: ").strip()
                        if not candidate_name:
                            candidate_name = "Unknown_Candidate"
                        print(f"\n[012] Running baseline only on: {candidate_name}")

                        orchestrator = GodelianTestOrchestrator()
                        results = orchestrator.run_baseline_only(candidate_name)

                        print(f"\n[RESULTS] Baseline artifacts detected: {len(results.get('artifacts', []))}")

                    elif test_choice == "4":
                        skill_path = Path(project_root) / "modules" / "ai_intelligence" / "pqn_alignment" / "skillz" / "godelian_simon_says" / "SKILLz.md"
                        if skill_path.exists():
                            print(f"\n[DOC] Skill location: {skill_path}")
                            print("[TIP] Use: cat {skill_path} to view full protocol")
                        else:
                            print(f"[WARN] Skill not found at: {skill_path}")

                except ImportError as e:
                    print(f"[ERROR] Could not import orchestrator: {e}")
                    print("[TIP] Run: python -m py_compile modules/ai_intelligence/pqn_alignment/src/godelian_test_orchestrator.py")
                except Exception as e:
                    print(f"[ERROR] Godelian test failed: {e}")
                    traceback.print_exc()

                input("\nPress Enter to return to PQN Menu...")

            elif choice == "0":
                return
                
            else:
                print("[WARN] Invalid selection.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n[STOP] Operation stopped by user. Returning to PQN Menu...")
            continue
            
        except Exception as e:
            print(f"[ERROR] PQN Launch failed: {e}")
            traceback.print_exc()
            input("\nPress Enter to return to PQN Menu...")

if __name__ == "__main__":
    run_pqn_dae()
