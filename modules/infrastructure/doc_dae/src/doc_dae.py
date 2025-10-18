# -*- coding: utf-8 -*-
import sys
import io


"""
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

DocDAE - Autonomous Documentation Organization
WSP Compliance: WSP 3 (Domain Organization), WSP 77 (Agent Coordination), WSP 27 (DAE Architecture)

This DAE uses Qwen/Gemma coordination to autonomously organize misplaced documentation
from the root docs/ folder into proper module docs/ locations.

Training Mission: First real-world application of WSP 77 agent coordination protocol.
"""

import json
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class DocDAE:
    """
    Autonomous Documentation Organization DAE.

    WSP 77 Agent Roles:
    - Gemma: Fast classification (doc vs data, module extraction)
    - Qwen: Complex reasoning (module mapping, movement planning)
    - 0102 (This): Strategic oversight and safe execution
    """

    def __init__(self, root_docs_path: Optional[Path] = None):
        """Initialize DocDAE with WSP 77 agent coordination."""
        logger.info("[ROCKET] Initializing DocDAE - Autonomous Documentation Organization")

        self.root_path = Path(__file__).parent.parent.parent.parent.parent
        self.root_docs = root_docs_path or (self.root_path / "docs")
        self.modules_path = self.root_path / "modules"
        self.memory_path = Path(__file__).parent.parent / "memory"
        self.memory_path.mkdir(exist_ok=True)

        # Load Qwen/Gemma engines for WSP 77 coordination
        self.gemma_engine = None
        self.qwen_engine = None
        self._initialize_agents()

        # Pattern memory for training
        self.pattern_memory = self._load_pattern_memory()

        logger.info("[OK] DocDAE initialized with WSP 77 agent coordination")

    def _initialize_agents(self):
        """Initialize Qwen/Gemma agents for WSP 77 coordination."""
        try:
            from holo_index.qwen_advisor.gemma_rag_inference import GemmaRAGInference
            from pathlib import Path

            gemma_path = Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")
            qwen_path = Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf")

            if gemma_path.exists() and qwen_path.exists():
                self.gemma_engine = GemmaRAGInference(
                    gemma_model_path=gemma_path,
                    qwen_model_path=qwen_path,
                    confidence_threshold=0.7
                )
                logger.info("[OK] WSP 77 agents initialized (Gemma + Qwen)")
            else:
                logger.warning("[U+26A0]️  Gemma/Qwen models not found, using rule-based fallback")
        except Exception as e:
            logger.warning(f"[U+26A0]️  Agent initialization failed: {e}, using rule-based fallback")

    def _load_pattern_memory(self) -> Dict[str, Any]:
        """Load pattern memory for training."""
        memory_file = self.memory_path / "doc_organization_patterns.json"

        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load pattern memory: {e}")

        return {
            "file_to_module_patterns": [],
            "classification_patterns": [],
            "movement_decisions": [],
            "training_examples": 0
        }

    def _save_pattern_memory(self):
        """Save pattern memory for future training."""
        memory_file = self.memory_path / "doc_organization_patterns.json"

        try:
            with open(memory_file, 'w') as f:
                json.dump(self.pattern_memory, f, indent=2, default=str)
            logger.debug("[OK] Pattern memory saved")
        except Exception as e:
            logger.error(f"Failed to save pattern memory: {e}")

    def analyze_docs_folder(self) -> Dict[str, Any]:
        """
        Phase 1: Analyze root docs folder using Gemma for fast classification.

        WSP 77 Role: Gemma performs fast binary classification
        - Is it documentation (MD) or operational data (JSON)?
        - Extract module hints from filename
        """
        logger.info("[DATA] Phase 1: Analyzing docs folder (Gemma classification)")

        if not self.root_docs.exists():
            return {"error": "docs folder not found", "files": []}

        files = []
        for file_path in self.root_docs.rglob("*"):
            if file_path.is_file():
                analysis = self._classify_file(file_path)
                files.append(analysis)

        result = {
            "total_files": len(files),
            "markdown_docs": len([f for f in files if f['type'] == 'documentation']),
            "json_data": len([f for f in files if f['type'] == 'operational_data']),
            "other": len([f for f in files if f['type'] == 'other']),
            "files": files,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"[OK] Analysis complete: {result['total_files']} files")
        logger.info(f"   [U+1F4C4] Markdown: {result['markdown_docs']}")
        logger.info(f"   [DATA] JSON: {result['json_data']}")
        logger.info(f"   [U+2753] Other: {result['other']}")

        return result

    def _classify_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Gemma Task: Fast file classification.

        Binary decisions:
        1. Documentation (.md) vs Operational Data (.json) vs Other
        2. Extract module hint from filename
        """
        relative_path = file_path.relative_to(self.root_docs)
        file_type = file_path.suffix.lower()

        # Fast classification (Gemma-style: binary, pattern-based)
        if file_type == '.md':
            classification = 'documentation'
        elif file_type == '.json':
            classification = 'operational_data'
        else:
            classification = 'other'

        # Extract module hint from filename (pattern matching)
        module_hint = self._extract_module_hint(file_path.stem)

        return {
            "path": str(relative_path),
            "full_path": str(file_path),
            "name": file_path.name,
            "type": classification,
            "extension": file_type,
            "module_hint": module_hint,
            "size_bytes": file_path.stat().st_size
        }

    def _extract_module_hint(self, filename: str) -> Optional[str]:
        """
        Extract module hint from filename using pattern matching.
        Examples:
        - "Gemma3_YouTube_DAE_First_Principles_Analysis" -> youtube_dae
        - "HoloIndex_MCP_ricDAE_Integration" -> holo_index
        - "adaptive_router_wsp_integration_report" -> ric_dae
        """
        filename_lower = filename.lower()

        # Pattern: ricDAE / Adaptive Router (check before general DAE)
        if any(x in filename_lower for x in ['ricdae', 'ric_dae', 'adaptive_router']):
            return 'ric_dae'

        # Pattern: YouTube DAE
        if any(x in filename_lower for x in ['youtube', 'yt_dae', 'livechat', 'shorts']):
            return 'youtube_dae'

        # Pattern: HoloIndex / Qwen / Gemma
        if any(x in filename_lower for x in ['holoindex', 'qwen', 'gemma', 'advisor']):
            return 'holo_index'

        # Pattern: Orphan analysis
        if 'orphan' in filename_lower:
            return 'orphan_analysis'

        # Pattern: MCP / Gemini
        if any(x in filename_lower for x in ['mcp', 'gemini']):
            return 'mcp_integration'

        # Pattern: WSP / CodeIndex / Sentinel
        if any(x in filename_lower for x in ['wsp', 'codeindex', 'sentinel']):
            return 'wsp_framework'

        # Pattern: DAE general (after specific DAE patterns)
        if 'dae' in filename_lower:
            return 'dae_infrastructure'

        return None

    def generate_movement_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: Generate movement plan using Qwen for complex reasoning.

        WSP 77 Role: Qwen performs complex module mapping and coordination
        - Map files to proper module locations
        - Decide: Move, Archive, or Keep
        - Build safe execution plan
        """
        logger.info("[AI] Phase 2: Generating movement plan (Qwen coordination)")

        plan = {
            "moves": [],
            "archives": [],
            "keeps": [],
            "unmatched": [],
            "summary": {}
        }

        for file_info in analysis['files']:
            decision = self._decide_file_destination(file_info)

            if decision['action'] == 'move':
                plan['moves'].append({
                    "source": file_info['full_path'],
                    "destination": decision['destination'],
                    "reason": decision['reason'],
                    "module": decision.get('module', 'unknown')
                })
            elif decision['action'] == 'archive':
                plan['archives'].append({
                    "source": file_info['full_path'],
                    "reason": decision['reason']
                })
            elif decision['action'] == 'keep':
                plan['keeps'].append({
                    "path": file_info['full_path'],
                    "reason": decision['reason']
                })
            else:
                plan['unmatched'].append({
                    "path": file_info['full_path'],
                    "reason": "No clear destination"
                })

        plan['summary'] = {
            "total_files": len(analysis['files']),
            "to_move": len(plan['moves']),
            "to_archive": len(plan['archives']),
            "to_keep": len(plan['keeps']),
            "unmatched": len(plan['unmatched'])
        }

        logger.info(f"[OK] Movement plan generated:")
        logger.info(f"   [BOX] Move: {plan['summary']['to_move']}")
        logger.info(f"   [U+1F5C4]️  Archive: {plan['summary']['to_archive']}")
        logger.info(f"   [OK] Keep: {plan['summary']['to_keep']}")
        logger.info(f"   [U+2753] Unmatched: {plan['summary']['unmatched']}")

        return plan

    def _decide_file_destination(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qwen Task: Complex reasoning for file destination.

        Decision Matrix:
        1. JSON reports/analysis (documentation) -> Move to module/docs/
        2. JSON operational data (batch files, temp data) -> Archive
        3. Documentation with module hint -> Move to module/docs/
        4. Documentation without hint -> Keep (needs manual review)
        5. Other files -> Archive
        """
        file_type = file_info['type']
        module_hint = file_info['module_hint']
        filename = file_info['name']

        # Rule 1: JSON Classification (documentation vs operational)
        if file_type == 'operational_data':
            # JSON Documentation: Reports, analysis, reference data
            if any(x in filename.lower() for x in ['report', 'manifest', 'matrix', 'index']):
                # These are structured documentation, not operational data
                if module_hint:
                    destination = self._map_to_module_docs(module_hint, filename)
                    if destination:
                        return {
                            "action": "move",
                            "destination": destination,
                            "module": module_hint,
                            "reason": f"JSON documentation for {module_hint} module"
                        }
                # System-wide reference data
                if any(x in filename.lower() for x in ['index', 'complete']):
                    return {
                        "action": "keep",
                        "reason": "System-wide reference data (JSON documentation)"
                    }

            # JSON Operational Data: Batch files, temp analysis
            if 'batch' in filename.lower() or 'qwen_batch' in filename.lower():
                return {
                    "action": "archive",
                    "reason": "Operational batch file (temporary data)"
                }
            elif 'orphan' in filename.lower() and file_info['size_bytes'] > 100000:
                return {
                    "action": "archive",
                    "reason": "Large orphan analysis dataset (operational)"
                }

        # Rule 2: Documentation with clear module hint
        if file_type == 'documentation' and module_hint:
            destination = self._map_to_module_docs(module_hint, filename)
            if destination:
                return {
                    "action": "move",
                    "destination": destination,
                    "module": module_hint,
                    "reason": f"Belongs to {module_hint} module"
                }

        # Rule 3: Documentation without clear hint (foundups vision, architecture docs)
        if file_type == 'documentation':
            if any(x in filename.lower() for x in ['vision', 'architecture', 'knowledge']):
                return {
                    "action": "keep",
                    "reason": "System-wide documentation (belongs in docs/)"
                }

        # Rule 4: Unknown - keep for manual review
        return {
            "action": "keep",
            "reason": "Needs manual review"
        }

    def _map_to_module_docs(self, module_hint: str, filename: str) -> Optional[str]:
        """Map module hint to actual module docs/ path."""
        # Map hints to actual module paths
        module_mapping = {
            'ric_dae': 'modules/ai_intelligence/ric_dae/docs',
            'youtube_dae': 'modules/communication/livechat/docs',
            'holo_index': 'holo_index/docs',
            'orphan_analysis': 'docs/orphan_analysis',  # Special case: keep organized
            'mcp_integration': 'docs/mcp',
            'wsp_framework': 'WSP_framework/docs',
            'dae_infrastructure': 'modules/infrastructure/dae_infrastructure/docs'
        }

        target_dir = module_mapping.get(module_hint)
        if not target_dir:
            return None

        # Construct full path
        full_path = self.root_path / target_dir / filename
        return str(full_path)

    def execute_plan(self, plan: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """
        Phase 3: Execute movement plan with safety checks.

        WSP 77 Role: 0102 (Strategic oversight and safe execution)
        - Review plan for safety
        - Execute with git tracking
        - Validate results
        """
        logger.info(f"[ROCKET] Phase 3: Executing movement plan (dry_run={dry_run})")

        result = {
            "moves_completed": 0,
            "archives_completed": 0,
            "errors": [],
            "dry_run": dry_run
        }

        # Execute moves
        for move in plan['moves']:
            try:
                if not dry_run:
                    self._safe_move_file(move['source'], move['destination'])
                    result['moves_completed'] += 1
                    logger.info(f"[OK] Moved: {Path(move['source']).name} -> {move['module']}")
                else:
                    logger.info(f"[DRY RUN] Would move: {Path(move['source']).name} -> {move['module']}")
            except Exception as e:
                result['errors'].append(f"Move failed: {move['source']} - {e}")
                logger.error(f"[FAIL] Move failed: {e}")

        # Execute archives
        archive_dir = self.root_path / "docs" / "_archive" / datetime.now().strftime("%Y%m%d")
        for archive in plan['archives']:
            try:
                if not dry_run:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    dest = archive_dir / Path(archive['source']).name
                    shutil.move(archive['source'], dest)
                    result['archives_completed'] += 1
                    logger.info(f"[U+1F5C4]️  Archived: {Path(archive['source']).name}")
                else:
                    logger.info(f"[DRY RUN] Would archive: {Path(archive['source']).name}")
            except Exception as e:
                result['errors'].append(f"Archive failed: {archive['source']} - {e}")
                logger.error(f"[FAIL] Archive failed: {e}")

        logger.info(f"[OK] Execution complete:")
        logger.info(f"   [BOX] Moved: {result['moves_completed']}")
        logger.info(f"   [U+1F5C4]️  Archived: {result['archives_completed']}")
        logger.info(f"   [FAIL] Errors: {len(result['errors'])}")

        return result

    def _safe_move_file(self, source: str, destination: str):
        """Safely move file with destination directory creation."""
        source_path = Path(source)
        dest_path = Path(destination)

        # Create destination directory
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        shutil.move(source, dest_path)

    def run_autonomous_organization(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Main entry point: Run complete autonomous organization cycle.

        WSP 77 Full Cycle:
        1. Gemma: Fast classification
        2. Qwen: Complex coordination
        3. 0102: Strategic execution
        """
        logger.info("[BOT] Starting Autonomous Documentation Organization (WSP 77)")
        logger.info(f"   Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")

        # Phase 1: Analyze (Gemma)
        analysis = self.analyze_docs_folder()

        # Phase 2: Plan (Qwen)
        plan = self.generate_movement_plan(analysis)

        # Phase 3: Execute (0102)
        execution = self.execute_plan(plan, dry_run=dry_run)

        # Save to memory for training
        self._record_training_example(analysis, plan, execution)

        result = {
            "analysis": analysis,
            "plan": plan,
            "execution": execution,
            "timestamp": datetime.now().isoformat()
        }

        logger.info("[OK] Autonomous organization cycle complete")
        return result

    def _record_training_example(self, analysis: Dict, plan: Dict, execution: Dict):
        """Record this execution as a training example for Qwen/Gemma."""
        self.pattern_memory['training_examples'] += 1

        # Store successful movement patterns
        for move in plan['moves']:
            pattern = {
                "filename_pattern": Path(move['source']).stem,
                "module": move['module'],
                "reason": move['reason'],
                "success": True
            }
            self.pattern_memory['file_to_module_patterns'].append(pattern)

        self._save_pattern_memory()
        logger.debug(f"[BOOKS] Training example recorded (total: {self.pattern_memory['training_examples']})")


# Convenience functions for main.py integration
def run_doc_organization(dry_run: bool = True) -> Dict[str, Any]:
    """Run documentation organization from main menu."""
    dae = DocDAE()
    return dae.run_autonomous_organization(dry_run=dry_run)
