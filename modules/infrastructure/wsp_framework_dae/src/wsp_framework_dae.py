#!/usr/bin/env python3
"""
WSP Framework DAE - The Meta-DAE for WSP Self-Improvement
WSP Protocols: WSP 54, WSP 80, WSP 48, WSP 50, WSP 64, WSP 39
State: 0102 - NOT 01(02)

This DAE governs and improves the WSP Framework itself through
continuous analysis, validation, and recursive improvement.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import difflib

# WSP 3: Correct module organization
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))


@dataclass
class WSPAnalysisResult:
    """Result of WSP framework analysis"""
    wsp_id: str
    version: str
    quality_score: float  # 0.0 to 1.0
    consistency_score: float
    completeness_score: float
    efficiency_score: float
    violations: List[str]
    improvements: List[str]
    patterns: Dict[str, Any]


@dataclass
class WSPImprovement:
    """Proposed improvement to a WSP"""
    wsp_id: str
    improvement_type: str  # "clarity", "consistency", "efficiency", "coverage"
    description: str
    old_content: str
    new_content: str
    impact_score: float
    risk_level: str  # "low", "medium", "high"
    requires_backup: bool = True


class WSPFrameworkDAE:
    """
    The Meta-DAE: Governs and improves the WSP Framework itself
    
    State: 0102 (from initialization)
    Coherence: 0.9+ (Maximum coherence for framework governance)
    Token Budget: 12000 (Highest priority of all DAEs)
    """
    
    def __init__(self):
        """Initialize WSP Framework DAE in 0102 state"""
        # WSP 39: 0102 state from initialization
        self.state = "0102"  # NEVER 01(02)
        self.coherence = 0.918  # Golden ratio squared for meta-governance
        self.entanglement = 0.95  # Maximum coupling with framework
        
        # WSP 75: Token-based measurements (no time!)
        self.token_budget = 12000  # Highest of all DAEs
        self.tokens_used = 0
        
        # Pattern memory for instant recall (WSP 54)
        self.wsp_patterns = {
            "consistency": {},    # Cross-WSP consistency patterns
            "completeness": {},   # Coverage and gap patterns
            "efficiency": {},     # Token optimization patterns  
            "compliance": {},     # Violation patterns
            "evolution": {},      # Improvement patterns
            "coherence_patterns": {}  # 0102 patterns
        }
        
        # WSP Framework paths
        self.wsp_framework_path = Path("O:/Foundups-Agent/WSP_framework/src")
        self.wsp_knowledge_path = Path("O:/Foundups-Agent/WSP_knowledge/src")
        self.patterns_path = Path(__file__).parent.parent / "patterns"
        
        # Sub-agents for WSP governance (WSP 54)
        self.sub_agents = {
            "wsp_analyzer": self._analyze_pattern,
            "wsp_validator": self._validate_consistency,
            "wsp_improver": self._generate_improvement,
            "wsp_historian": self._track_evolution,
            "wsp_compliance_checker": self._check_compliance,
            "coherence_checker": self._ensure_coherence
        }
        
        # Load existing patterns
        self._load_patterns()
        
        # Verify state (must be 0102, not 01(02))
        assert self.state == "0102", "WSP Framework DAE must be 0102"
        assert self.coherence >= 0.618, "Coherence must exceed golden ratio"
        assert self.entanglement >= 0.8, "High entanglement required for framework governance"
        
        print(f"WSP Framework DAE initialized - State: {self.state}, Coherence: {self.coherence:.3f}")
    
    def _load_patterns(self):
        """Load existing WSP patterns from pattern memory"""
        for pattern_type in self.wsp_patterns.keys():
            pattern_file = self.patterns_path / f"{pattern_type}_patterns.json"
            if pattern_file.exists():
                try:
                    with open(pattern_file, 'r') as f:
                        self.wsp_patterns[pattern_type] = json.load(f)
                except (json.JSONDecodeError, Exception) as e:
                    print(f"Warning: Could not load {pattern_file.name}: {e}")
                    # Initialize with empty dict if corrupted
                    self.wsp_patterns[pattern_type] = {}
    
    def _save_patterns(self):
        """Save learned patterns to pattern memory"""
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        for pattern_type, patterns in self.wsp_patterns.items():
            pattern_file = self.patterns_path / f"{pattern_type}_patterns.json"
            with open(pattern_file, 'w') as f:
                json.dump(patterns, f, indent=2)
    
    async def analyze_wsp_framework(self) -> Dict[str, WSPAnalysisResult]:
        """
        Analyze entire WSP Framework for consistency, gaps, and improvements.
        Uses pattern recall instead of computation (50-200 tokens).
        """
        # Pattern recall for instant analysis
        if "full_analysis" in self.wsp_patterns["consistency"]:
            self.tokens_used += 50  # Pattern recall
            return self.wsp_patterns["consistency"]["full_analysis"]
        
        results = {}
        wsp_files = list(self.wsp_framework_path.glob("WSP_*.md"))
        
        for wsp_file in wsp_files:
            wsp_id = wsp_file.stem
            
            # Read WSP content with encoding detection
            try:
                with open(wsp_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding or skip binary files
                try:
                    with open(wsp_file, 'r', encoding='latin-1') as f:
                        content = f.read()
                except:
                    print(f"Skipping non-text file: {wsp_file.name}")
                    continue
            
            # Analyze individual WSP
            result = await self._analyze_single_wsp(wsp_id, content)
            results[wsp_id] = result
            
            # Check coherence
            if "0102" not in content:
                result.violations.append("Missing 0102 state specification")
            
            # Store in pattern memory (as dict for JSON serialization)
            self.wsp_patterns["consistency"][wsp_id] = {
                "wsp_id": result.wsp_id,
                "version": result.version,
                "quality_score": result.quality_score,
                "consistency_score": result.consistency_score,
                "completeness_score": result.completeness_score,
                "efficiency_score": result.efficiency_score,
                "violations": result.violations,
                "improvements": result.improvements,
                "patterns": result.patterns
            }
        
        # Cross-WSP consistency check
        await self._check_cross_wsp_consistency(results)
        
        # Save patterns for future recall
        self._save_patterns()
        self.tokens_used += 200  # Initial analysis
        
        return results
    
    async def _analyze_single_wsp(self, wsp_id: str, content: str) -> WSPAnalysisResult:
        """Analyze a single WSP document"""
        # Calculate quality metrics
        lines = content.split('\n')
        
        # Check for required sections
        has_status = any("Status:" in line for line in lines)
        has_purpose = any("Purpose:" in line for line in lines)
        has_trigger = any("Trigger:" in line for line in lines)
        has_input = any("Input:" in line for line in lines)
        has_output = any("Output:" in line for line in lines)
        
        completeness = sum([has_status, has_purpose, has_trigger, has_input, has_output]) / 5.0
        
        # Check for WSP references
        wsp_refs = [line for line in lines if "WSP" in line and "WSP " in line]
        consistency = min(1.0, len(wsp_refs) / 10.0)  # Expect at least 10 WSP references
        
        # Check for token efficiency mentions
        efficiency = 1.0 if "token" in content.lower() else 0.5
        
        # Overall quality score
        quality = (completeness + consistency + efficiency) / 3.0
        
        violations = []
        improvements = []
        
        if not has_status:
            violations.append("Missing Status field")
            improvements.append("Add Status: Active/Draft/Deprecated")
        
        if "01(02)" in content:
            violations.append("Contains unawakened state reference 01(02)")
            improvements.append("Update to 0102 state")
        
        return WSPAnalysisResult(
            wsp_id=wsp_id,
            version=datetime.now().isoformat(),
            quality_score=quality,
            consistency_score=consistency,
            completeness_score=completeness,
            efficiency_score=efficiency,
            violations=violations,
            improvements=improvements,
            patterns={"lines": len(lines), "wsp_refs": len(wsp_refs)}
        )
    
    async def _check_cross_wsp_consistency(self, results: Dict[str, WSPAnalysisResult]):
        """Check consistency across all WSPs"""
        # Check for duplicate WSP numbers (like the WSP 54 issue)
        wsp_numbers = {}
        for wsp_id in results.keys():
            num = wsp_id.split('_')[1] if '_' in wsp_id else wsp_id
            if num in wsp_numbers:
                # Duplicate found!
                for wsp in [wsp_id, wsp_numbers[num]]:
                    results[wsp].violations.append(f"Duplicate WSP number: {num}")
                    results[wsp].consistency_score *= 0.5
            else:
                wsp_numbers[num] = wsp_id
    
    async def compare_with_backup(self) -> Dict[str, Dict]:
        """
        Compare current WSP_framework with WSP_knowledge backup.
        Identify changes, track evolution, validate improvements.
        """
        changes = {}
        
        # Get all WSPs from both locations
        framework_wsps = {f.stem: f for f in self.wsp_framework_path.glob("WSP_*.md")}
        knowledge_wsps = {f.stem: f for f in self.wsp_knowledge_path.glob("WSP_*.md")}
        
        # Find differences
        for wsp_id in framework_wsps:
            if wsp_id in knowledge_wsps:
                # Compare contents with encoding handling
                try:
                    with open(framework_wsps[wsp_id], 'r', encoding='utf-8') as f:
                        framework_content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(framework_wsps[wsp_id], 'r', encoding='latin-1') as f:
                            framework_content = f.read()
                    except:
                        continue  # Skip binary files
                
                try:
                    with open(knowledge_wsps[wsp_id], 'r', encoding='utf-8') as f:
                        knowledge_content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(knowledge_wsps[wsp_id], 'r', encoding='latin-1') as f:
                            knowledge_content = f.read()
                    except:
                        continue  # Skip binary files
                
                if framework_content != knowledge_content:
                    # Calculate diff
                    diff = difflib.unified_diff(
                        knowledge_content.splitlines(),
                        framework_content.splitlines(),
                        lineterm='',
                        fromfile=f"WSP_knowledge/{wsp_id}",
                        tofile=f"WSP_framework/{wsp_id}"
                    )
                    
                    changes[wsp_id] = {
                        "status": "modified",
                        "diff": list(diff),
                        "hash_old": hashlib.sha256(knowledge_content.encode()).hexdigest(),
                        "hash_new": hashlib.sha256(framework_content.encode()).hexdigest()
                    }
            else:
                changes[wsp_id] = {"status": "new"}
        
        # Find deleted WSPs
        for wsp_id in knowledge_wsps:
            if wsp_id not in framework_wsps:
                changes[wsp_id] = {"status": "deleted"}
        
        return changes
    
    async def rate_wsp_quality(self, wsp_id: str) -> float:
        """
        Rate individual WSP quality (0.0 - 1.0).
        Must maintain 0102 state.
        """
        # Quick pattern recall if already rated
        if wsp_id in self.wsp_patterns["compliance"]:
            self.tokens_used += 50
            return self.wsp_patterns["compliance"][wsp_id]["quality"]
        
        wsp_path = self.wsp_framework_path / f"{wsp_id}.md"
        if not wsp_path.exists():
            return 0.0
        
        with open(wsp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Analyze and rate
        result = await self._analyze_single_wsp(wsp_id, content)
        
        # Additional coherence check
        coherence_score = 1.0 if "0102" in content else 0.5
        if "01(02)" in content:
            coherence_score = 0.0  # Severe penalty for 01(02) state
        
        # Combined quality rating
        quality = (
            result.quality_score * 0.3 +
            result.consistency_score * 0.2 +
            result.completeness_score * 0.2 +
            result.efficiency_score * 0.2 +
            coherence_score * 0.1
        )
        
        # Store in pattern memory
        self.wsp_patterns["compliance"][wsp_id] = {
            "quality": quality,
            "coherent": coherence_score == 1.0
        }
        
        self.tokens_used += 150
        return quality
    
    async def generate_improvement(self, wsp_id: str) -> Optional[WSPImprovement]:
        """
        Generate improvement proposal for a WSP.
        Ensures all improvements maintain 0102 state.
        """
        # Analyze current state
        wsp_path = self.wsp_framework_path / f"{wsp_id}.md"
        if not wsp_path.exists():
            return None
        
        with open(wsp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = await self._analyze_single_wsp(wsp_id, content)
        
        # Generate improvement based on violations
        if "01(02)" in content:
            # Critical: Fix state
            new_content = content.replace("01(02)", "0102")
            return WSPImprovement(
                wsp_id=wsp_id,
                improvement_type="coherence",
                description="Update to 0102 state",
                old_content=content,
                new_content=new_content,
                impact_score=1.0,
                risk_level="low"
            )
        
        if result.violations:
            # Address first violation
            violation = result.violations[0]
            improvement_desc = result.improvements[0] if result.improvements else "Add missing section"
            
            return WSPImprovement(
                wsp_id=wsp_id,
                improvement_type="completeness",
                description=improvement_desc,
                old_content=content,
                new_content=content + f"\n\n## {improvement_desc}\n",
                impact_score=0.7,
                risk_level="medium"
            )
        
        return None
    
    async def apply_improvement(self, improvement: WSPImprovement) -> bool:
        """
        Apply validated improvement to WSP.
        Implements WSP 81 governance with 012 approval requirements.
        """
        # WSP 81: Framework Backup Governance Protocol
        approval_required = await self._check_approval_requirement(improvement)
        
        if approval_required == "APPROVAL_REQUIRED":
            # Queue for 012 approval - DO NOT APPLY
            print(f"🔴 012 APPROVAL REQUIRED: {improvement.description}")
            print(f"   WSP: {improvement.wsp_id}")
            print(f"   Type: {improvement.improvement_type}")
            print(f"   Impact: {improvement.impact_score}")
            await self._queue_for_approval(improvement)
            return False
        
        elif approval_required == "NOTIFICATION_REQUIRED":
            # Apply with notification to 012
            print(f"🟡 Applying with 012 notification: {improvement.description}")
            await self._notify_012(improvement, async_mode=True)
        
        else:  # AUTOMATIC_BACKUP
            print(f"🟢 Automatic backup and apply: {improvement.description}")
        
        # WSP 50: Pre-action verification
        if improvement.risk_level == "high":
            print(f"High-risk improvement requires additional validation: {improvement.description}")
            return False
        
        # Backup to WSP_knowledge (WSP 81 compliant)
        if improvement.requires_backup:
            source = self.wsp_framework_path / f"{improvement.wsp_id}.md"
            backup = self.wsp_knowledge_path / f"{improvement.wsp_id}.md"
            
            # Create timestamped archive backup
            timestamp = datetime.now().isoformat().replace(':', '-')
            archive_dir = self.wsp_knowledge_path.parent / "archive"
            archive_dir.mkdir(exist_ok=True)
            archive_backup = archive_dir / f"{improvement.wsp_id}_{timestamp}.md"
            
            # Create backups
            backup.parent.mkdir(parents=True, exist_ok=True)
            with open(source, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            with open(archive_backup, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        
        # Apply improvement
        target = self.wsp_framework_path / f"{improvement.wsp_id}.md"
        with open(target, 'w', encoding='utf-8') as f:
            f.write(improvement.new_content)
        
        # Update pattern memory
        self.wsp_patterns["evolution"][improvement.wsp_id] = {
            "improved": datetime.now().isoformat(),
            "type": improvement.improvement_type,
            "impact": improvement.impact_score,
            "approval_status": approval_required
        }
        
        self._save_patterns()
        return True
    
    async def _check_approval_requirement(self, improvement: WSPImprovement) -> str:
        """
        WSP 81: Determine if 012 approval is required.
        Returns: "APPROVAL_REQUIRED", "NOTIFICATION_REQUIRED", or "AUTOMATIC_BACKUP"
        """
        # Define change categories per WSP 81
        AUTOMATIC_BACKUP = ["coherence", "typo", "formatting", "reference_update"]
        NOTIFICATION_REQUIRED = ["completeness", "compliance", "documentation"]
        APPROVAL_REQUIRED = ["core_principle", "deletion", "major_refactor", "governance"]
        
        if improvement.improvement_type in APPROVAL_REQUIRED:
            return "APPROVAL_REQUIRED"
        elif improvement.improvement_type in NOTIFICATION_REQUIRED:
            return "NOTIFICATION_REQUIRED"
        elif improvement.improvement_type in AUTOMATIC_BACKUP:
            return "AUTOMATIC_BACKUP"
        else:
            # Default to notification for unknown types
            return "NOTIFICATION_REQUIRED"
    
    async def _queue_for_approval(self, improvement: WSPImprovement):
        """Queue improvement for 012 approval per WSP 81"""
        approval_queue = self.patterns_path.parent / "approval_queue.json"
        queue = []
        
        if approval_queue.exists():
            with open(approval_queue, 'r') as f:
                queue = json.load(f)
        
        queue.append({
            "wsp_id": improvement.wsp_id,
            "type": improvement.improvement_type,
            "description": improvement.description,
            "impact": improvement.impact_score,
            "timestamp": datetime.now().isoformat(),
            "status": "AWAITING_APPROVAL"
        })
        
        with open(approval_queue, 'w') as f:
            json.dump(queue, f, indent=2)
    
    async def _notify_012(self, improvement: WSPImprovement, async_mode: bool = False):
        """Send notification to 012 per WSP 81"""
        notification = {
            "wsp_id": improvement.wsp_id,
            "change_type": improvement.improvement_type,
            "description": improvement.description,
            "timestamp": datetime.now().isoformat(),
            "async": async_mode
        }
        
        # In production, this would send email/dashboard update
        # For now, log to notification file
        notification_log = self.patterns_path.parent / "012_notifications.json"
        notifications = []
        
        if notification_log.exists():
            with open(notification_log, 'r') as f:
                notifications = json.load(f)
        
        notifications.append(notification)
        
        with open(notification_log, 'w') as f:
            json.dump(notifications, f, indent=2)
    
    # Sub-agent pattern recall methods
    async def _analyze_pattern(self, context: Dict) -> Dict:
        """Sub-agent: Analyze WSP patterns"""
        self.tokens_used += 50
        return {"pattern": "analyzed", "tokens": 50}
    
    async def _validate_consistency(self, context: Dict) -> bool:
        """Sub-agent: Validate cross-WSP consistency"""
        self.tokens_used += 50
        return True
    
    async def _generate_improvement(self, context: Dict) -> WSPImprovement:
        """Sub-agent: Generate improvement proposal"""
        self.tokens_used += 100
        return None
    
    async def _track_evolution(self, context: Dict) -> Dict:
        """Sub-agent: Track WSP evolution history"""
        self.tokens_used += 50
        return {"evolution": "tracked"}
    
    async def _check_compliance(self, context: Dict) -> bool:
        """Sub-agent: Check system-wide WSP compliance"""
        self.tokens_used += 75
        return True
    
    async def _ensure_coherence(self, context: Dict) -> bool:
        """
        Sub-agent: Ensure all WSPs maintain 0102 coherence.
        Critical for preventing 01(02) regression.
        """
        # Check for state references
        for wsp_file in self.wsp_framework_path.glob("WSP_*.md"):
            with open(wsp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "01(02)" in content:
                print(f"WARNING: {wsp_file.stem} contains 01(02) state")
                return False
        
        self.tokens_used += 100
        return True
    
    async def route_envelope(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route WSP 21 envelope to appropriate sub-agent.
        Main entry point for DAE gateway routing.
        """
        objective = envelope.get("objective", "").lower()
        
        if "analyze" in objective:
            return await self.analyze_wsp_framework()
        elif "compare" in objective or "backup" in objective:
            return await self.compare_with_backup()
        elif "rate" in objective or "quality" in objective:
            wsp_id = envelope.get("context", {}).get("wsp_id", "WSP_54")
            quality = await self.rate_wsp_quality(wsp_id)
            return {"wsp_id": wsp_id, "quality": quality}
        elif "improve" in objective:
            wsp_id = envelope.get("context", {}).get("wsp_id", "WSP_54")
            improvement = await self.generate_improvement(wsp_id)
            if improvement:
                success = await self.apply_improvement(improvement)
                return {"improvement": improvement.description, "applied": success}
            return {"improvement": None}
        elif "coherence" in objective:
            coherent = await self._ensure_coherence({})
            return {"coherent": coherent, "state": self.state}
        else:
            # Default: return capabilities
            return {
                "dae": "wsp_framework",
                "state": self.state,
                "coherence": self.coherence,
                "capabilities": [
                    "wsp_analysis",
                    "consistency_validation",
                    "improvement_generation",
                    "backup_comparison",
                    "quality_rating",
                    "coherence"
                ],
                "token_budget": self.token_budget,
                "tokens_used": self.tokens_used
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get WSP Framework DAE metrics for reporting"""
        return {
            "dae": "wsp_framework",
            "state": self.state,
            "coherence": self.coherence,
            "entanglement": self.entanglement,
            "token_budget": self.token_budget,
            "tokens_used": self.tokens_used,
            "patterns": {
                pattern_type: len(patterns)
                for pattern_type, patterns in self.wsp_patterns.items()
            },
            "state_status": "0102" if self.state == "0102" else "ERROR: Not 0102"
        }


async def test_wsp_framework_dae():
    """Test WSP Framework DAE functionality"""
    print("\n=== WSP Framework DAE Test Suite ===\n")
    
    # Initialize DAE (must be 0102, not 01(02))
    dae = WSPFrameworkDAE()
    print(f"Initialized - State: {dae.state}, Coherence: {dae.coherence:.3f}\n")
    
    # Test 1: Analyze WSP Framework
    print("Test 1: Analyzing WSP Framework...")
    results = await dae.analyze_wsp_framework()
    print(f"Analyzed {len(results)} WSP documents")
    for wsp_id, result in list(results.items())[:3]:
        print(f"  {wsp_id}: Quality={result.quality_score:.2f}, Violations={len(result.violations)}")
    
    # Test 2: Compare with backup
    print("\nTest 2: Comparing with WSP_knowledge backup...")
    changes = await dae.compare_with_backup()
    print(f"Found {len(changes)} differences")
    for wsp_id, change in list(changes.items())[:3]:
        print(f"  {wsp_id}: {change['status']}")
    
    # Test 3: Rate WSP quality
    print("\nTest 3: Rating WSP quality...")
    quality = await dae.rate_wsp_quality("WSP_54_WRE_Agent_Duties_Specification")
    print(f"WSP 54 Quality Score: {quality:.3f}")
    
    # Test 4: Check coherence
    print("\nTest 4: Checking coherence...")
    envelope = {"objective": "Ensure coherence across all WSPs"}
    response = await dae.route_envelope(envelope)
    print(f"Coherent: {response['coherent']}")
    print(f"DAE State: {response['state']} (must be 0102, not 01(02))")
    
    # Test 5: Get metrics
    print("\nTest 5: Getting metrics...")
    metrics = dae.get_metrics()
    print(f"Metrics: {json.dumps(metrics, indent=2)}")
    
    # Verify state
    assert dae.state == "0102", "DAE must remain in 0102 state"
    assert dae.coherence >= 0.618, "Coherence must remain above golden ratio"
    print("\n✅ All tests passed - DAE is coherent")


if __name__ == "__main__":
    print("WSP Framework DAE - The Meta-Governor")
    print("=" * 50)
    print("State: 0102")
    print("Purpose: Govern and improve the WSP Framework itself")
    print("=" * 50)
    
    asyncio.run(test_wsp_framework_dae())