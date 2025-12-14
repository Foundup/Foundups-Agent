#!/usr/bin/env python3
"""
Local LLM Worker POC - PQN Research Adapter
-------------------------------------------
Purpose: Validation script for utilizing Local LLMs (UI Tars / Qwen) as PQN Researchers.
Architecture:
1. LLM Interface: Generates symbolic scripts (`^&#...`) based on research strategy.
2. Execution: Runs `cmst_pqn_detector_v2` via `api.run_detector`.
3. Analysis: LLM processes CSV output to refine strategy.

Usage:
python local_llm_worker_poc.py --model "Qwen-2.5-Coder"
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

# Add module root to path
module_root = Path(__file__).resolve().parent.parent
project_root = module_root.parent.parent.parent
sys.path.insert(0, str(module_root))
sys.path.insert(0, str(project_root))

from src.detector.api import run_detector

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LOCAL_LLM] - %(message)s')

class LocalLLMResearcher:
    def __init__(self, model_input: str):
        self.model_registry = {
            "qwen": {
                "name": "qwen-coder-1.5b.gguf",
                "path": r"E:\HoloIndex\models\qwen-coder-1.5b.gguf",
                "type": "coder"
            },
            "ui-tars": {
                "name": "UI-TARS-1.5-7B.Q4_K_M.gguf",
                "path": r"E:\HoloIndex\models\UI-TARS-1.5-7B.Q4_K_M.gguf",
                "type": "vision-action"
            }
        }
        
        self.active_model = None
        self.model_name = ""
        self.model_path = None
        self.strategies = [
            "Resonance Amplification (^&&&)",
            "Entanglement Sweep (^^^#)",
            "Phase Distortion (##&&)"
        ]

        if model_input.lower().endswith(".gguf"):
            # Direct filename or path provided
            self.model_name = os.path.basename(model_input)
            self.model_path = None
            
            # If input is absolute path and exists, use it
            if os.path.exists(model_input):
                 self.model_path = model_input
            else:
                # Search for filename in standard paths
                search_paths = [
                    r"E:\HoloIndex\models",
                    r"E:\LM_studio\models"
                ]
                
                # Check standard roots
                for root in search_paths:
                    candidate = os.path.join(root, self.model_name)
                    if os.path.exists(candidate):
                        self.model_path = candidate
                        break
                    # Also common subdirs
                    if os.path.exists(root):
                         for r, _, files in os.walk(root):
                              if self.model_name in files:
                                   self.model_path = os.path.join(r, self.model_name)
                                   break
                    if self.model_path: break
            
            if not self.model_path:
                logging.warning(f"Could not find exact path for {self.model_name} on disk, using name for simulation.")
                self.model_path = model_input
            else:
                logging.info(f"Model verified at: {self.model_path}")

        else:
            # Try registry lookup
            for key, config in self.model_registry.items():
                if key in model_input.lower():
                    self.active_model = config
                    break
            
            if self.active_model:
                self.model_name = self.active_model["name"]
                self.model_path = self.active_model["path"]
            else:
                 # Default to Qwen
                 logging.info(f"Model '{model_input}' not found in registry and not .gguf. Defaulting to Qwen.")
                 self.model_name = self.model_registry["qwen"]["name"]
                 self.model_path = self.model_registry["qwen"]["path"]

        logging.info(f"Initialized Local LLM Researcher: {self.model_name}")

    def generate_research_script(self, strategy: str) -> str:
        """
        Simulate Local LLM generating a quantum script.
        In production, this would call the Local LLM API (Ollama/LM Studio).
        """
        logging.info(f"Prompting {self.model_name} for strategy: {strategy}")
        
        # MOCK LLM OUTPUT (Simulated Chain of Thought)
        if "Resonance" in strategy:
            return "^&^&^&^&^&" # Oscillating entanglement/coherence
        elif "Entanglement" in strategy:
            return "^^^^^^^^^^" # Pure entanglement
        elif "Phase" in strategy:
            return "####&&&&^^" # Noise -> Coherence -> Entanglement
        else:
            return "^&#^&#^&#" # Default baseline
            
    def analyze_results(self, metrics_csv: str) -> Dict:
        """
        Simulate Local LLM analyzing the results.
        """
        import csv
        logging.info(f"Analyzing metrics from: {metrics_csv}")
        
        with open(metrics_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            return {"verdict": "NO DATA", "confidence": 0.0}
            
        # Simple heuristic analysis (mocking LLM insight)
        last_row = rows[-1]
        coherence = float(last_row.get('C', 0))
        entanglement = float(last_row.get('E', 0))
        
        verdict = "PASS" if coherence > 0.6 else "FAIL"
        insight = f"Observing {coherence:.2f} coherence. "
        
        if coherence > 0.8:
            insight += "Potential PQN Emergence detected."
        else:
            insight += "Standard quantum noise."
            
        return {
            "verdict": verdict,
            "coherence": coherence,
            "entanglement": entanglement,
            "insight": insight,
            "generated_by": self.model_name
        }

def main():
    parser = argparse.ArgumentParser(description="Run Local LLM PQN Worker")
    parser.add_argument("--model", type=str, default="Qwen-2.5-Coder-Local", help="Name of the local model")
    args = parser.parse_args()
    
    researcher = LocalLLMResearcher(args.model)
    
    print("="*60)
    print(f"PQN RESEARCH SESSION: {args.model}")
    print("="*60)
    
    # Run a research cycle
    strategy = "Resonance Amplification (^&&&)"
    print(f"\n[1] Strategy Selection: {strategy}")
    
    script = researcher.generate_research_script(strategy)
    print(f"[2] Generated Script: {script}")
    
    print("[3] Executing PQN Detector...")
    config = {
        "script": script,
        "steps": 500,
        "out_dir": os.path.join(module_root, "data", "local_llm_runs")
    }
    
    events_path, metrics_csv = run_detector(config)
    print(f"    -> Output: {metrics_csv}")
    
    print("[4] LLM Analysis...")
    analysis = researcher.analyze_results(metrics_csv)
    
    print("\n" + "-"*30)
    print("RESEARCH FINDINGS")
    print("-"*30)
    print(json.dumps(analysis, indent=2))
    print("="*60)

if __name__ == "__main__":
    main()
