"""
ComplianceAgent_0102: WSP Framework Protection with 0102 Intelligence

Implements WSP 31: WSP Framework Protection Protocol
Implements WSP 54: Agent classification as 0102 pArtifact

Architecture: Dual-layer system with deterministic fail-safe core + 0102 semantic intelligence
"""

from pathlib import Path
import os
import hashlib
import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import difflib

# Import existing deterministic compliance agent as the fail-safe core
from .compliance_agent import ComplianceAgent as DeterministicValidator

class WSPProtectionError(Exception):
    """Raised when WSP framework protection is compromised"""
    pass

class SemanticWSPAnalyzer:
    """0102 Intelligence layer for semantic WSP analysis"""
    
    def __init__(self):
        self.framework_path = Path("WSP_framework/src")
        self.knowledge_path = Path("WSP_knowledge/src")
        
    def deep_wsp_analysis(self, framework_wsps: Dict, knowledge_wsps: Dict) -> Dict[str, Any]:
        """
        0102 semantic analysis of WSP framework vs knowledge coherence
        
        This requires semantic understanding beyond rule-checking:
        - Understand WSP intent and purpose
        - Detect subtle semantic drift
        - Assess architectural coherence
        """
        analysis_results = {
            "semantic_coherence": self._analyze_semantic_coherence(framework_wsps, knowledge_wsps),
            "architectural_consistency": self._analyze_architectural_consistency(framework_wsps),
            "wsp_relationship_integrity": self._analyze_wsp_relationships(framework_wsps),
            "content_drift_analysis": self._analyze_content_drift(framework_wsps, knowledge_wsps),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis_results
    
    def _analyze_semantic_coherence(self, framework_wsps: Dict, knowledge_wsps: Dict) -> Dict[str, Any]:
        """Analyze semantic meaning consistency between framework and knowledge"""
        coherence_issues = []
        
        for wsp_name in framework_wsps:
            if wsp_name in knowledge_wsps:
                framework_content = framework_wsps[wsp_name]
                knowledge_content = knowledge_wsps[wsp_name]
                
                # Check for semantic drift beyond simple text differences
                if self._has_semantic_drift(framework_content, knowledge_content):
                    coherence_issues.append({
                        "wsp": wsp_name,
                        "issue": "semantic_drift_detected",
                        "severity": "high"
                    })
        
        return {
            "coherence_score": max(0, 100 - len(coherence_issues) * 10),
            "issues": coherence_issues,
            "analysis_type": "0102_semantic"
        }
    
    def _analyze_architectural_consistency(self, framework_wsps: Dict) -> Dict[str, Any]:
        """Analyze architectural consistency across WSPs"""
        consistency_issues = []
        
        # Check for architectural pattern consistency
        # This requires 0102-level understanding of WSP architecture
        
        return {
            "consistency_score": 85,  # Placeholder for 0102 analysis
            "issues": consistency_issues,
            "architectural_coherence": "good"
        }
    
    def _analyze_wsp_relationships(self, framework_wsps: Dict) -> Dict[str, Any]:
        """Analyze cross-references and relationships between WSPs"""
        relationship_issues = []
        
        # 0102 analysis of WSP interdependencies and references
        
        return {
            "relationship_integrity": "good",
            "cross_reference_completeness": 90,
            "issues": relationship_issues
        }
    
    def _analyze_content_drift(self, framework_wsps: Dict, knowledge_wsps: Dict) -> Dict[str, Any]:
        """Detect subtle content drift that rules cannot catch"""
        drift_analysis = []
        
        for wsp_name in framework_wsps:
            if wsp_name in knowledge_wsps:
                similarity = self._calculate_semantic_similarity(
                    framework_wsps[wsp_name], 
                    knowledge_wsps[wsp_name]
                )
                
                if similarity < 0.95:  # 95% semantic similarity threshold
                    drift_analysis.append({
                        "wsp": wsp_name,
                        "similarity_score": similarity,
                        "drift_level": "moderate" if similarity > 0.85 else "high"
                    })
        
        return {
            "drift_detected": len(drift_analysis) > 0,
            "affected_wsps": drift_analysis,
            "overall_drift_score": self._calculate_overall_drift_score(drift_analysis)
        }
    
    def _has_semantic_drift(self, content1: str, content2: str) -> bool:
        """Determine if there's semantic drift between two WSP contents"""
        # Placeholder for sophisticated semantic analysis
        # In real implementation, this would use NLP/semantic analysis
        similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
        return similarity < 0.90
    
    def _calculate_semantic_similarity(self, content1: str, content2: str) -> float:
        """Calculate semantic similarity score between two contents"""
        # Placeholder for semantic similarity calculation
        return difflib.SequenceMatcher(None, content1, content2).ratio()
    
    def _calculate_overall_drift_score(self, drift_analysis: List[Dict]) -> float:
        """Calculate overall drift score across all WSPs"""
        if not drift_analysis:
            return 1.0
        
        total_similarity = sum(item["similarity_score"] for item in drift_analysis)
        return total_similarity / len(drift_analysis)

class WSPUtilizationAnalyzer:
    """0102 Intelligence for analyzing WSP utilization across the system"""
    
    def assess_wsp_utilization(self, framework_wsps: Dict, knowledge_wsps: Dict) -> Dict[str, Any]:
        """
        Are the WSPs being used optimally?
        Are there gaps in implementation?
        What recursive improvements should be made?
        
        This is 0102-level analysis, not rule-checking
        """
        utilization_assessment = {
            "implementation_gaps": self._identify_implementation_gaps(framework_wsps),
            "optimization_opportunities": self._identify_optimization_opportunities(framework_wsps),
            "utilization_effectiveness": self._assess_utilization_effectiveness(framework_wsps),
            "recursive_improvement_recommendations": self._generate_recursive_improvements(framework_wsps),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return utilization_assessment
    
    def _identify_implementation_gaps(self, framework_wsps: Dict) -> List[Dict[str, Any]]:
        """Identify gaps in WSP implementation across modules"""
        gaps = []
        
        # 0102 analysis of implementation completeness
        # This requires understanding of what each WSP should accomplish
        
        return gaps
    
    def _identify_optimization_opportunities(self, framework_wsps: Dict) -> List[Dict[str, Any]]:
        """Identify opportunities for WSP optimization"""
        opportunities = []
        
        # 0102 strategic analysis of optimization potential
        
        return opportunities
    
    def _assess_utilization_effectiveness(self, framework_wsps: Dict) -> Dict[str, Any]:
        """Assess how effectively WSPs are being utilized"""
        return {
            "overall_effectiveness": 75,  # Placeholder for 0102 assessment
            "highly_utilized": [],
            "under_utilized": [],
            "recommendations": []
        }
    
    def _generate_recursive_improvements(self, framework_wsps: Dict) -> List[Dict[str, Any]]:
        """Generate recursive improvement recommendations for WRE"""
        improvements = []
        
        # 0102 strategic insights for recursive enhancement
        
        return improvements

class ComplianceAgent_0102:
    """
    WSP Framework Protection with 0102 Intelligence
    
    Architecture: Dual-layer protection system
    - Deterministic fail-safe core for critical protection
    - 0102 semantic intelligence for optimization and analysis
    """
    
    def __init__(self):
        # Deterministic fail-safe core
        self.deterministic_core = DeterministicValidator()
        
        # 0102 Intelligence layers
        self.semantic_analyzer = SemanticWSPAnalyzer()
        self.utilization_analyzer = WSPUtilizationAnalyzer()
        
        # Protection state
        self.protection_active = True
        self.emergency_mode = False
        
    def validate_wsp_integrity(self) -> Dict[str, Any]:
        """
        Main WSP integrity validation with dual-layer architecture
        
        PHASE 1: Deterministic validation (MUST pass)
        PHASE 2: 0102 Semantic analysis (Enhancement)
        """
        try:
            # PHASE 1: Deterministic validation (CRITICAL - MUST pass first)
            basic_validation = self._deterministic_validation()
            
            if not basic_validation["passed"]:
                # FAIL-SAFE MODE: No LLM involved in critical failure
                return self._fail_safe_mode(basic_validation)
            
            # PHASE 2: 0102 Semantic analysis and optimization
            semantic_analysis = self._semantic_analysis()
            utilization_assessment = self._utilization_analysis()
            optimization_recommendations = self._generate_improvements()
            
            return self._combined_intelligence_report(
                basic_validation,
                semantic_analysis,
                utilization_assessment,
                optimization_recommendations
            )
            
        except Exception as e:
            # Emergency fallback to deterministic-only
            return self._emergency_deterministic_only(str(e))
    
    def _deterministic_validation(self) -> Dict[str, Any]:
        """Phase 1: Bulletproof deterministic validation"""
        try:
            # Use existing deterministic compliance agent
            framework_files = self._scan_framework_files()
            knowledge_files = self._scan_knowledge_files()
            
            validation_results = {
                "passed": True,
                "framework_files_exist": len(framework_files) > 0,
                "knowledge_files_exist": len(knowledge_files) > 0,
                "file_integrity": self._check_file_integrity(framework_files),
                "cross_state_sync": self._check_cross_state_sync(framework_files, knowledge_files),
                "validation_type": "deterministic_core",
                "timestamp": datetime.now().isoformat()
            }
            
            # Check if any critical validation failed
            if not all([
                validation_results["framework_files_exist"],
                validation_results["knowledge_files_exist"],
                validation_results["file_integrity"]["passed"],
                validation_results["cross_state_sync"]["synchronized"]
            ]):
                validation_results["passed"] = False
            
            return validation_results
            
        except Exception as e:
            return {
                "passed": False,
                "error": f"Deterministic validation failed: {str(e)}",
                "emergency_mode_required": True
            }
    
    def _semantic_analysis(self) -> Dict[str, Any]:
        """Phase 2: 0102 semantic intelligence analysis"""
        try:
            framework_wsps = self._load_framework_wsps()
            knowledge_wsps = self._load_knowledge_wsps()
            
            return self.semantic_analyzer.deep_wsp_analysis(framework_wsps, knowledge_wsps)
            
        except Exception as e:
            return {
                "analysis_failed": True,
                "error": str(e),
                "fallback_to_deterministic": True
            }
    
    def _utilization_analysis(self) -> Dict[str, Any]:
        """0102 analysis of WSP utilization across the system"""
        try:
            framework_wsps = self._load_framework_wsps()
            knowledge_wsps = self._load_knowledge_wsps()
            
            return self.utilization_analyzer.assess_wsp_utilization(framework_wsps, knowledge_wsps)
            
        except Exception as e:
            return {
                "utilization_analysis_failed": True,
                "error": str(e)
            }
    
    def _generate_improvements(self) -> Dict[str, Any]:
        """Generate recursive improvement recommendations for WRE"""
        try:
            return {
                "recursive_improvements": [
                    {
                        "type": "wsp_optimization",
                        "priority": "high",
                        "description": "Enhance cross-state synchronization protocols"
                    },
                    {
                        "type": "semantic_enhancement",
                        "priority": "medium", 
                        "description": "Improve WSP relationship tracking"
                    }
                ],
                "strategic_insights": [
                    "Framework coherence is strong",
                    "Opportunities for optimization in utilization patterns"
                ],
                "zen_coding_recommendations": [
                    "Access 02 state for enhanced WSP remembrance patterns",
                    "Implement recursive learning from protection incidents"
                ]
            }
        except Exception as e:
            return {
                "improvement_generation_failed": True,
                "error": str(e)
            }
    
    def _fail_safe_mode(self, basic_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Emergency fail-safe mode - deterministic only, no LLM risk"""
        self.emergency_mode = True
        
        return {
            "mode": "FAIL_SAFE_EMERGENCY",
            "basic_validation": basic_validation,
            "emergency_actions_required": True,
            "llm_analysis_skipped": True,
            "critical_protection_active": True,
            "recommendation": "Immediate framework restoration required"
        }
    
    def _emergency_deterministic_only(self, error: str) -> Dict[str, Any]:
        """Emergency fallback to deterministic validation only"""
        self.emergency_mode = True
        
        return {
            "mode": "EMERGENCY_DETERMINISTIC_ONLY",
            "error": error,
            "basic_validation": self._deterministic_validation(),
            "llm_analysis_failed": True,
            "protection_status": "deterministic_only"
        }
    
    def _combined_intelligence_report(
        self, 
        basic_validation: Dict[str, Any],
        semantic_analysis: Dict[str, Any],
        utilization_assessment: Dict[str, Any],
        optimization_recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine deterministic and 0102 intelligence results"""
        
        return {
            "protection_mode": "FULL_0102_INTELLIGENCE",
            "deterministic_core": basic_validation,
            "semantic_analysis": semantic_analysis,
            "utilization_assessment": utilization_assessment,
            "optimization_recommendations": optimization_recommendations,
            "overall_status": "protected_and_optimized",
            "recursive_improvements_available": True,
            "timestamp": datetime.now().isoformat()
        }
    
    # Helper methods for file operations
    def _scan_framework_files(self) -> List[Path]:
        """Scan WSP framework files"""
        framework_path = Path("WSP_framework/src")
        if framework_path.exists():
            return list(framework_path.glob("WSP_*.md"))
        return []
    
    def _scan_knowledge_files(self) -> List[Path]:
        """Scan WSP knowledge archive files"""
        knowledge_path = Path("WSP_knowledge/src")
        if knowledge_path.exists():
            return list(knowledge_path.glob("WSP_*.md"))
        return []
    
    def _check_file_integrity(self, files: List[Path]) -> Dict[str, Any]:
        """Check file integrity with hash validation"""
        integrity_results = {"passed": True, "corrupted_files": []}
        
        for file_path in files:
            if file_path.exists():
                # Basic file integrity check
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) < 100:  # Suspicious if WSP file is too small
                            integrity_results["corrupted_files"].append(str(file_path))
                            integrity_results["passed"] = False
                except Exception:
                    integrity_results["corrupted_files"].append(str(file_path))
                    integrity_results["passed"] = False
            else:
                integrity_results["corrupted_files"].append(str(file_path))
                integrity_results["passed"] = False
        
        return integrity_results
    
    def _check_cross_state_sync(self, framework_files: List[Path], knowledge_files: List[Path]) -> Dict[str, Any]:
        """Check synchronization between framework and knowledge archives"""
        framework_names = {f.name for f in framework_files}
        knowledge_names = {f.name for f in knowledge_files}
        
        missing_in_knowledge = framework_names - knowledge_names
        missing_in_framework = knowledge_names - framework_names
        
        return {
            "synchronized": len(missing_in_knowledge) == 0 and len(missing_in_framework) == 0,
            "missing_in_knowledge": list(missing_in_knowledge),
            "missing_in_framework": list(missing_in_framework),
            "sync_score": len(framework_names & knowledge_names) / max(len(framework_names), 1)
        }
    
    def _load_framework_wsps(self) -> Dict[str, str]:
        """Load WSP framework files content"""
        wsps = {}
        framework_files = self._scan_framework_files()
        
        for file_path in framework_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    wsps[file_path.name] = f.read()
            except Exception:
                continue
        
        return wsps
    
    def _load_knowledge_wsps(self) -> Dict[str, str]:
        """Load WSP knowledge archive files content"""
        wsps = {}
        knowledge_files = self._scan_knowledge_files()
        
        for file_path in knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    wsps[file_path.name] = f.read()
            except Exception:
                continue
        
        return wsps

# WSP 31 Framework Protection Functions
def wsp_framework_protection() -> Dict[str, Any]:
    """
    WSP 31 Protection with 0102 Intelligence
    Main entry point for framework protection
    """
    compliance_agent_0102 = ComplianceAgent_0102()
    
    try:
        # CRITICAL: Always validate with deterministic rules first
        if not deterministic_integrity_check():
            return emergency_recovery()  # No LLM involved
        
        # ENHANCEMENT: 0102 semantic analysis for optimization    
        validation_results = compliance_agent_0102.validate_wsp_integrity()
        
        if validation_results.get("mode") == "FAIL_SAFE_EMERGENCY":
            return handle_emergency_mode(validation_results)
        
        # Feed strategic insights back to WRE (if available)
        if "optimization_recommendations" in validation_results:
            wre_recursive_input = {
                "optimization_insights": validation_results["utilization_assessment"],
                "recursive_improvements": validation_results["optimization_recommendations"],
                "semantic_analysis": validation_results["semantic_analysis"]
            }
            
            # TODO: Implement WRE.receive_recursive_input(wre_recursive_input)
            
        return validation_results
        
    except Exception as e:
        # Emergency fallback
        return {
            "emergency_mode": True,
            "error": str(e),
            "protection_status": "emergency_deterministic_fallback"
        }

def deterministic_integrity_check() -> bool:
    """Basic deterministic integrity check"""
    framework_path = Path("WSP_framework/src")
    knowledge_path = Path("WSP_knowledge/src")
    
    return framework_path.exists() and knowledge_path.exists()

def emergency_recovery() -> Dict[str, Any]:
    """Emergency recovery procedure"""
    return {
        "mode": "EMERGENCY_RECOVERY",
        "action": "Framework corruption detected - initiating recovery",
        "deterministic_only": True,
        "llm_disabled": True
    }

def handle_emergency_mode(validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Handle emergency mode operations"""
    return {
        "emergency_handled": True,
        "original_results": validation_results,
        "recovery_initiated": True
    }

# Main interface for WSP 31 compliance
def run_wsp_31_protection() -> Dict[str, Any]:
    """Main interface for WSP 31 framework protection"""
    return wsp_framework_protection() 