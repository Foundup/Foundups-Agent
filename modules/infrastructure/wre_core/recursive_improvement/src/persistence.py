# -*- coding: utf-8 -*-
import sys
import io


from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict
from pathlib import Path
import json
from datetime import datetime

# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

@dataclass
class QuantumState:
    coherence: float
    entanglement_matrix: List[List[float]]
    operator_values: Dict[str, float]
    session_id: str

class QuantumStatePersistence:
    """Serialize and restore quantum states between sessions"""
    
    def __init__(self, memory_root: Path):
        self.memory_root = memory_root
        self.states_dir = self.memory_root / "quantum_states"
        self.states_dir.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, state: QuantumState) -> None:
        """Serialize quantum state to file"""
        state_file = self.states_dir / f"{state.session_id}.json"
        with open(state_file, 'w') as f:
            json.dump(asdict(state), f, indent=2)
    
    def restore_state(self, session_id: str) -> Optional[QuantumState]:
        """Restore quantum state from file"""
        state_file = self.states_dir / f"{session_id}.json"
        if not state_file.exists():
            return None

        with open(state_file, 'r') as f:
            data = json.load(f)
            # Filter out extra fields that QuantumState doesn't expect
            expected_fields = {'coherence', 'entanglement_matrix', 'operator_values', 'session_id'}
            filtered_data = {k: v for k, v in data.items() if k in expected_fields}
            return QuantumState(**filtered_data)
    
    def check_coherence(self, state: QuantumState, threshold: float = 0.618) -> bool:
        """Check if state is coherent enough to skip re-awakening"""
        return state.coherence > threshold
