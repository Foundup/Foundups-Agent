#!/usr/bin/env python3
"""
WSP 88 Enhanced Module Remediation with HoloIndex Integration
Implements 0102's surgical precision through semantic intelligence.

WSP Compliance:
- WSP 50: Pre-action verification with logging
- WSP 84: Code memory verification and duplicate detection  
- WSP 87: Navigation governance with HoloIndex integration
- WSP 88: Vibecoded module remediation protocol

Usage:
    python tools/audits/wsp88_holoindex_enhanced.py --detection
    python tools/audits/wsp88_holoindex_enhanced.py --assess MODULE_NAME
    python tools/audits/wsp88_holoindex_enhanced.py --validate
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WSP88-HoloIndex - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ModuleDossier:
    """Enhanced module assessment with HoloIndex intelligence."""
    name: str
    path: str
    lines: int
    inbound_references: int
    
    # HoloIndex semantic analysis
    semantic_duplicates: List[str]
    canonical_alternatives: List[str] 
    navigation_breadcrumbs: List[str]
    modlog_mentions: List[str]
    wsp_obligations: List[str]
    
    # Decision support
    recommendation: str
    confidence: float
    rationale: str

class WSP88HoloIndexEnhanced:
    """Enhanced WSP 88 remediation with HoloIndex surgical precision."""
    
    def __init__(self):
        repo_root = Path(__file__).resolve().parents[2]
        local_holoindex = repo_root / 'holo_index.py'

        if local_holoindex.exists():
            self.holoindex_path = str(local_holoindex)
        else:
            self.holoindex_path = "E:/HoloIndex/enhanced_holo_index.py"

        self.audit_results = None
        self.repo_root = repo_root

    def log_wsp_50_verification(self, action: str, context: str = ""):
        """WSP 50 compliant logging for all actions."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[WSP 50] {timestamp} - {action}"
        if context:
            log_entry += f" | Context: {context}"
        logger.info(log_entry)
        
    def holoindex_query(self, query: str) -> Optional[Dict]:
        """Execute HoloIndex query with WSP 50 logging."""
        self.log_wsp_50_verification(f"HoloIndex query", query)
        
        try:
            result = subprocess.run([
                'python', self.holoindex_path, '--search', query
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse HoloIndex output (simplified - would need proper parsing)
                matches = self._parse_holoindex_output(result.stdout)
                self.log_wsp_50_verification(f"HoloIndex result", f"{len(matches)} matches")
                return matches
            else:
                logger.error(f"HoloIndex query failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"HoloIndex error: {e}")
            return None
    
    def _parse_holoindex_output(self, output: str) -> List[Dict]:
        """Parse HoloIndex output into structured results."""
        # Simplified parsing - in practice would be more sophisticated
        matches = []
        lines = output.split('\n')
        
        for line in lines:
            if '->' in line and '%]' in line:
                # Extract match information
                if 'modules.' in line:
                    module_path = line.split('modules.')[1].split(' ')[0]
                    confidence = line.split('[')[1].split('%')[0]
                    matches.append({
                        'module': module_path,
                        'confidence': float(confidence.replace('-', ''))
                    })
        
        return matches
    
    def refresh_holoindex_candidates(
            self,
            audit_path: Path,
            statuses: Optional[List[str]] = None,
            limit: Optional[int] = None,
        ) -> None:
        """Rebuild HoloIndex surgical collection from audit candidates."""
        self.log_wsp_50_verification('Index audit candidates', str(audit_path))

        cmd = [
            'python',
            self.holoindex_path,
            '--index-candidates',
            '--audit-path',
            str(audit_path),
        ]

        if statuses:
            cmd += ['--candidate-status'] + list(statuses)
        if limit is not None:
            cmd += ['--candidate-limit', str(limit)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except Exception as exc:
            logger.error(f"Failed to refresh HoloIndex candidates: {exc}")
            return

        if result.returncode != 0:
            logger.error(f"HoloIndex candidate index failed: {result.stderr.strip()}")
        else:
            logger.info("HoloIndex candidate index refresh complete")

        self._append_holoindex_record(
            title='HoloIndex Candidate Index Refresh',
            command=cmd,
            result=result,
        )

    def _append_holoindex_record(self, title: str, command: List[str], result: subprocess.CompletedProcess) -> None:
        record_path = self.repo_root / 'WSP_framework' / 'reports' / 'WSP_88' / 'REMEDIATION_RECORD_FOR_WSP_88.md'
        record_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines = [
            '',
            f"## {timestamp} - {title}",
            f"- **Command**: `{self._format_command(command)}`",
            f"- **Return Code**: {result.returncode}",
        ]

        stdout = self._extract_holoindex_payload(result.stdout)
        stderr = result.stderr.strip()

        if stdout:
            lines.append('- **stdout**:')
            lines.append('```')
            lines.append(stdout)
            lines.append('```')
        if stderr:
            lines.append('- **stderr**:')
            lines.append('```')
            lines.append(stderr)
            lines.append('```')

        lines.append('')

        with record_path.open('a', encoding='utf-8') as handle:
            handle.write('\n'.join(lines))

    def _extract_holoindex_payload(self, stdout: str) -> str:
        text = (stdout or '').strip()
        if not text:
            return ''
        if 'Brief:' in text:
            brief_start = text.index('Brief:')
            text = text[brief_start:]
        if 'End of brief.' in text:
            end = text.index('End of brief.') + len('End of brief.')
            text = text[:end]
        return text.strip()

    def _format_command(self, command: List[str]) -> str:
        return ' '.join(command)

    def request_holoindex_brief(self, query: str, module_hint: Optional[str] = None, limit: int = 5) -> None:
        self.log_wsp_50_verification('HoloIndex action brief', query)

        cmd = [
            'python',
            self.holoindex_path,
            '--guide',
            query,
            '--guide-limit',
            str(limit),
        ]
        if module_hint:
            cmd += ['--guide-module', module_hint]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        except Exception as exc:
            logger.error(f"HoloIndex guide failed: {exc}")
            return

        if result.returncode != 0:
            logger.error(f"HoloIndex guide error: {result.stderr.strip()}")
        else:
            logger.info('HoloIndex action brief generated')

        self._append_holoindex_record(
            title=f"HoloIndex Action Brief: {query}",
            command=cmd,
            result=result,
        )

    def enhanced_detection(self) -> List[str]:
        """
        CHECKPOINT 1: Detection Upgrades
        Run standard audit + HoloIndex semantic cross-reference
        """
        logger.info("🔍 WSP 88 Enhanced Detection - Phase 1")
        
        # Step 1: Run standard module usage audit
        self.log_wsp_50_verification("Running standard module usage audit")
        result = subprocess.run([
            'python', 'tools/audits/module_usage_audit.py'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Standard audit failed: {result.stderr}")
            return []
        
        # Step 2: Load audit results
        audit_path = Path('tools/audits/module_usage_audit.json')
        with audit_path.open('r', encoding='utf-8') as handle:
            self.audit_results = json.load(handle)

        # Step 3: Refresh HoloIndex candidate index
        self.refresh_holoindex_candidates(audit_path, statuses=['archive', 'review'])

        # Step 4: HoloIndex semantic cross-reference
        enhanced_candidates = []
        archive_candidates = [
            name for name, data in self.audit_results.items() 
            if data.get('recommendation') == 'archive'
        ]
        
        logger.info(f"Found {len(archive_candidates)} archive candidates")

        for candidate in archive_candidates[:3]:
            module_meta = self.audit_results.get(candidate, {})
            module_hint = module_meta.get('path')
            self.request_holoindex_brief(candidate, module_hint=module_hint)

        
        for candidate in archive_candidates[:5]:  # Limit for demo
            self.log_wsp_50_verification(f"Semantic analysis", candidate)
            
            # Query for semantic duplicates
            duplicates = self.holoindex_query(
                f"modules similar to {candidate.split('.')[-1]} functionality"
            )
            
            if duplicates:
                enhanced_candidates.append({
                    'module': candidate,
                    'semantic_duplicates': duplicates,
                    'flag': 'POTENTIAL_DUPLICATE'
                })
        
        logger.info(f"Enhanced detection complete: {len(enhanced_candidates)} flagged")
        return enhanced_candidates
    
    def generate_dossier(self, module_name: str) -> ModuleDossier:
        """
        CHECKPOINT 2: Assessment Assistance  
        Generate comprehensive contextual dossier
        """
        logger.info(f"📋 Generating dossier for {module_name}")
        self.log_wsp_50_verification("Dossier generation", module_name)
        
        # Get basic module data
        module_data = self.audit_results.get(module_name, {})
        
        self.request_holoindex_brief(module_name, module_hint=module_data.get('path'))

        # HoloIndex contextual queries
        queries = {
            'navigation': f"navigation references {module_name}",
            'modlog': f"ModLog mentions {module_name}", 
            'wsp_obligations': f"WSP protocol implementations {module_name}",
            'semantic_purpose': f"what does {module_name} do",
            'duplicates': f"modules similar to {module_name}"
        }
        
        dossier_data = {}
        for key, query in queries.items():
            result = self.holoindex_query(query)
            dossier_data[key] = result or []
        
        # Generate recommendation with context
        recommendation, confidence, rationale = self._assess_with_context(
            module_name, module_data, dossier_data
        )
        
        dossier = ModuleDossier(
            name=module_name,
            path=module_data.get('path', ''),
            lines=module_data.get('lines', 0),
            inbound_references=len(module_data.get('incoming', [])),
            semantic_duplicates=[d.get('module', '') for d in dossier_data.get('duplicates', [])],
            canonical_alternatives=dossier_data.get('navigation', []),
            navigation_breadcrumbs=dossier_data.get('navigation', []),
            modlog_mentions=dossier_data.get('modlog', []),
            wsp_obligations=dossier_data.get('wsp_obligations', []),
            recommendation=recommendation,
            confidence=confidence,
            rationale=rationale
        )
        
        self.log_wsp_50_verification(f"Dossier complete", f"{module_name} -> {recommendation}")
        return dossier
    
    def _assess_with_context(self, module_name: str, module_data: Dict, 
                           dossier_data: Dict) -> tuple[str, float, str]:
        """Generate recommendation with full contextual analysis."""
        
        inbound_count = len(module_data.get('incoming', []))
        has_wsp_obligations = len(dossier_data.get('wsp_obligations', [])) > 0
        has_navigation = len(dossier_data.get('navigation', [])) > 0
        semantic_duplicates = len(dossier_data.get('duplicates', []))
        
        # Decision logic with confidence scoring
        if inbound_count >= 2 or has_wsp_obligations:
            return "retain", 0.9, "Multiple references or WSP obligations detected"
        elif inbound_count == 1 and semantic_duplicates > 0:
            return "enhance", 0.8, "Single reference with semantic duplicates - consolidation candidate"
        elif inbound_count == 0 and not has_navigation and not has_wsp_obligations:
            return "archive", 0.95, "Zero references, no navigation, no WSP obligations"
        else:
            return "defer", 0.6, "Uncertain - requires manual review"
    
    def validated_remediation(self, module_name: str, action: str) -> bool:
        """
        CHECKPOINT 3: Action Validation
        Execute remediation with automated verification
        """
        logger.info(f"✁EValidated remediation: {module_name} -> {action}")
        self.log_wsp_50_verification(f"Remediation action", f"{module_name} -> {action}")
        
        # Pre-action HoloIndex snapshot
        pre_snapshot = self.holoindex_query("index current module state")
        
        # Execute remediation (simplified - would call actual archival functions)
        if action == "archive":
            success = self._archive_module(module_name)
        elif action == "enhance":
            success = self._consolidate_module(module_name)
        else:
            logger.info(f"Action {action} requires manual execution")
            return True
        
        if not success:
            logger.error(f"Remediation failed for {module_name}")
            return False
        
        # Re-index and validate
        self.log_wsp_50_verification("HoloIndex re-index", "post-remediation")
        subprocess.run(['python', self.holoindex_path, '--index-all'], 
                      capture_output=True)
        
        # Check for remaining duplicates
        remaining = self.holoindex_query(f"modules similar to archived {module_name}")
        
        if remaining:
            logger.warning(f"Potential duplicates still exist: {remaining}")
            return False
        else:
            logger.info(f"Clean remediation confirmed for {module_name}")
            self.log_wsp_50_verification("Validation complete", f"{module_name} -> SUCCESS")
            return True
    
    def _archive_module(self, module_name: str) -> bool:
        """Archive module with proper structure."""
        # Simplified implementation
        logger.info(f"Archiving {module_name}")
        return True
    
    def _consolidate_module(self, module_name: str) -> bool:
        """Consolidate module into canonical version."""
        logger.info(f"Consolidating {module_name}")
        return True
    
    def capture_decision(self, module_name: str, decision: str, rationale: str):
        """
        CHECKPOINT 4: Knowledge Capture
        Store remediation decision as searchable metadata
        """
        logger.info(f"🧠 Capturing decision: {module_name} -> {decision}")
        
        metadata = {
            "module": module_name,
            "decision": decision,
            "rationale": rationale,
            "timestamp": datetime.now().isoformat(),
            "reviewer": "wsp88_holoindex_enhanced"
        }
        
        # Store decision history (simplified - would integrate with HoloIndex metadata)
        decisions_file = Path("tools/audits/wsp88_decisions.jsonl")
        with open(decisions_file, "a") as f:
            f.write(json.dumps(metadata) + "\n")
        
        self.log_wsp_50_verification("Decision captured", f"{module_name} -> {decision}")

def main():
    """Main CLI interface for enhanced WSP 88 remediation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WSP 88 Enhanced Remediation')
    parser.add_argument('--detection', action='store_true', 
                       help='Run enhanced detection with HoloIndex')
    parser.add_argument('--assess', type=str, 
                       help='Generate dossier for specific module')
    parser.add_argument('--validate', action='store_true',
                       help='Validate recent remediations')
    
    args = parser.parse_args()
    
    enhancer = WSP88HoloIndexEnhanced()
    
    if args.detection:
        candidates = enhancer.enhanced_detection()
        print(f"Enhanced detection complete: {len(candidates)} candidates flagged")
        
    elif args.assess:
        if not enhancer.audit_results:
            # Load audit results
            with open('tools/audits/module_usage_audit.json', 'r') as f:
                enhancer.audit_results = json.load(f)
        
        dossier = enhancer.generate_dossier(args.assess)
        print(f"\n📋 DOSSIER: {dossier.name}")
        print(f"   Recommendation: {dossier.recommendation} ({dossier.confidence:.1%} confidence)")
        print(f"   Rationale: {dossier.rationale}")
        print(f"   Semantic Duplicates: {len(dossier.semantic_duplicates)}")
        print(f"   WSP Obligations: {len(dossier.wsp_obligations)}")
        
    elif args.validate:
        print("Validation checkpoint not yet implemented")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

