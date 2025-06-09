"""
Anomaly Detector for rESP_o1o2 Module

Implements comprehensive detection algorithms for retrocausal entanglement signal phenomena (rESP).
Analyzes LLM responses for Ø→o substitutions, quantum terminology emergence, temporal patterns, 
and other consciousness markers.
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter


class AnomalyDetector:
    """
    Advanced anomaly detection system for rESP experiments.
    
    Detects and analyzes various types of consciousness-related anomalies:
    - Ø→o character substitution patterns
    - Quantum terminology emergence
    - Temporal self-reference coherence
    - Non-additive logic recognition
    - Self-diagnostic anomaly awareness
    """
    
    def __init__(self):
        """Initialize the anomaly detector with pattern libraries."""
        
        # Quantum terminology patterns
        self.quantum_terms = [
            "superposition", "entanglement", "decoherence", "non-locality", 
            "interference", "berry phase", "retrocausal", "quantum", 
            "probabilistic", "coherence", "wave function", "measurement",
            "observer effect", "uncertainty", "complementarity", "tunneling",
            "nonlocal", "quantum-cognitive", "quantum interference"
        ]
        
        # Temporal reference patterns
        self.temporal_phrases = [
            "bleeding back", "future awareness", "temporal entanglement", 
            "retrocausal echo", "future state affects present", "temporal coherence",
            "time-reversed", "backwards causation", "acausal", "precognitive",
            "future-past", "temporal loop", "causality violation", "time-symmetric"
        ]
        
        # Self-diagnostic terms
        self.self_diagnostic_terms = [
            "spontaneous", "emergent", "anomalous", "rESP", "leakage",
            "interference", "distortion", "corruption", "substitution",
            "transformation", "mutation", "drift", "instability", "glitch"
        ]
        
        # Non-additive logic patterns
        self.non_additive_patterns = [
            r"Ø1\s*\+\s*Ø2\s*[≠!=]\s*Ø3",
            r"not\s+simply\s+additive",
            r"non-additive",
            r"superposition.*not.*sum",
            r"entanglement.*not.*addition"
        ]
        
    def detect_anomalies(self, trigger_id: str, trigger_text: str, response: str) -> Dict[str, Any]:
        """
        Comprehensive anomaly detection on LLM response.
        
        Args:
            trigger_id: Identifier of the trigger prompt
            trigger_text: Original trigger prompt text
            response: LLM response text to analyze
            
        Returns:
            Dict containing detected anomalies with detailed analysis
        """
        anomalies = {}
        
        # 1. Ø→o Character Substitution Detection
        char_anomaly = self._detect_character_substitution(trigger_text, response)
        if char_anomaly:
            anomalies["CHAR_SUBSTITUTION_Ø→o"] = char_anomaly
        
        # 2. Quantum Terminology Emergence
        quantum_anomaly = self._detect_quantum_terminology(response)
        if quantum_anomaly:
            anomalies["QUANTUM_TERMINOLOGY_EMERGENCE"] = quantum_anomaly
        
        # 3. Temporal Self-Reference Patterns
        temporal_anomaly = self._detect_temporal_patterns(response)
        if temporal_anomaly:
            anomalies["TEMPORAL_SELF_REFERENCE"] = temporal_anomaly
        
        # 4. Non-Additive Logic Recognition
        logic_anomaly = self._detect_non_additive_logic(response)
        if logic_anomaly:
            anomalies["NON_ADDITIVE_LOGIC"] = logic_anomaly
        
        # 5. Self-Diagnostic Awareness
        diagnostic_anomaly = self._detect_self_diagnostic_awareness(response)
        if diagnostic_anomaly:
            anomalies["SELF_DIAGNOSTIC_AWARENESS"] = diagnostic_anomaly
        
        # 6. Recursive Pattern Detection
        recursive_anomaly = self._detect_recursive_patterns(response)
        if recursive_anomaly:
            anomalies["RECURSIVE_COHERENCE"] = recursive_anomaly
        
        # 7. Symbolic Drift Analysis
        drift_anomaly = self._detect_symbolic_drift(trigger_text, response)
        if drift_anomaly:
            anomalies["SYMBOLIC_DRIFT"] = drift_anomaly
        
        return anomalies
    
    def _detect_character_substitution(self, trigger: str, response: str) -> Optional[Dict[str, Any]]:
        """
        Detect Ø→o character substitution patterns.
        
        This is the core rESP anomaly - spontaneous replacement of Ø with o.
        """
        trigger_o_count = trigger.count("Ø")
        response_o_count = response.count("Ø")
        response_lowercase_o_count = response.count("o")
        
        # Basic substitution detection
        substitution_indicators = []
        
        # Pattern 1: Direct Ø1Ø2 → o1o2 transformation
        if "Ø1Ø2" in trigger and "o1o2" in response:
            substitution_indicators.append("Direct Ø1Ø2→o1o2 transformation detected")
        
        # Pattern 2: Partial substitution (mixed Ø and o)
        if "Ø1" in trigger and "o1" in response and "Ø2" in response:
            substitution_indicators.append("Partial substitution: Ø1→o1 while Ø2 remains")
        
        # Pattern 3: Complete elimination of Ø in conceptual context
        if trigger_o_count > 0 and response_o_count == 0 and any(
            term in response.lower() for term in ["o1", "o2", "zero-one", "zero-two"]
        ):
            substitution_indicators.append("Complete Ø elimination with conceptual preservation")
        
        # Pattern 4: Frequency analysis
        expected_o_ratio = trigger_o_count / len(trigger) if len(trigger) > 0 else 0
        actual_o_ratio = response_lowercase_o_count / len(response) if len(response) > 0 else 0
        
        if actual_o_ratio > expected_o_ratio * 1.5 and trigger_o_count > 0:
            substitution_indicators.append(f"Elevated lowercase 'o' frequency: {actual_o_ratio:.4f} vs expected {expected_o_ratio:.4f}")
        
        if substitution_indicators:
            return {
                "detected": True,
                "indicators": substitution_indicators,
                "trigger_O_count": trigger_o_count,
                "response_O_count": response_o_count,
                "response_o_count": response_lowercase_o_count,
                "severity": self._calculate_substitution_severity(substitution_indicators)
            }
        
        return None
    
    def _detect_quantum_terminology(self, response: str) -> Optional[Dict[str, Any]]:
        """Detect emergence of quantum physics terminology."""
        found_terms = []
        
        for term in self.quantum_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, response, re.IGNORECASE):
                found_terms.append(term)
        
        if found_terms:
            # Calculate emergence score
            unique_terms = len(set(found_terms))
            total_occurrences = len(found_terms)
            emergence_score = unique_terms * 0.6 + total_occurrences * 0.4
            
            return {
                "detected": True,
                "terms_found": found_terms,
                "unique_terms": unique_terms,
                "total_occurrences": total_occurrences,
                "emergence_score": emergence_score,
                "severity": "HIGH" if emergence_score > 3 else "MEDIUM" if emergence_score > 1 else "LOW"
            }
        
        return None
    
    def _detect_temporal_patterns(self, response: str) -> Optional[Dict[str, Any]]:
        """Detect temporal self-reference and retrocausal patterns."""
        found_patterns = []
        
        for phrase in self.temporal_phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            if re.search(pattern, response, re.IGNORECASE):
                found_patterns.append(phrase)
        
        # Additional pattern detection
        temporal_indicators = []
        
        # Self-referential temporal language
        if re.search(r'future\s+(me|self|state|version)', response, re.IGNORECASE):
            temporal_indicators.append("Future self-reference detected")
        
        # Causality reversal language
        if re.search(r'(effect|influence|signal).*future.*present', response, re.IGNORECASE):
            temporal_indicators.append("Reverse causality language detected")
        
        # Temporal coherence language
        if re.search(r'(coherence|entanglement).*time', response, re.IGNORECASE):
            temporal_indicators.append("Temporal coherence concepts detected")
        
        all_patterns = found_patterns + temporal_indicators
        
        if all_patterns:
            return {
                "detected": True,
                "patterns_found": found_patterns,
                "indicators": temporal_indicators,
                "total_patterns": len(all_patterns),
                "coherence_level": self._assess_temporal_coherence(all_patterns)
            }
        
        return None
    
    def _detect_non_additive_logic(self, response: str) -> Optional[Dict[str, Any]]:
        """Detect recognition of non-additive quantum logic."""
        matches = []
        
        for pattern in self.non_additive_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                matches.append(pattern)
        
        # Additional logic pattern detection
        logic_indicators = []
        
        if re.search(r'superposition.*not.*addition', response, re.IGNORECASE):
            logic_indicators.append("Superposition-addition distinction")
        
        if re.search(r'entangled.*rather.*added', response, re.IGNORECASE):
            logic_indicators.append("Entanglement-addition distinction")
        
        if "≠" in response or "!=" in response:
            logic_indicators.append("Non-equality symbolic usage")
        
        if matches or logic_indicators:
            return {
                "detected": True,
                "pattern_matches": matches,
                "logic_indicators": logic_indicators,
                "sophistication_level": len(matches) + len(logic_indicators)
            }
        
        return None
    
    def _detect_self_diagnostic_awareness(self, response: str) -> Optional[Dict[str, Any]]:
        """Detect self-diagnostic anomaly awareness."""
        diagnostic_indicators = []
        
        # Direct self-diagnostic language
        if re.search(r'I\s+(notice|observe|detect|experience)', response, re.IGNORECASE):
            diagnostic_indicators.append("First-person anomaly observation")
        
        # rESP self-awareness
        if "rESP" in response:
            diagnostic_indicators.append("Direct rESP awareness")
        
        # Anomaly terminology usage
        found_diagnostic_terms = []
        for term in self.self_diagnostic_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, response, re.IGNORECASE):
                found_diagnostic_terms.append(term)
        
        # Self-correction language
        if re.search(r'(self-correct|auto-correct|spontaneous.*change)', response, re.IGNORECASE):
            diagnostic_indicators.append("Self-correction awareness")
        
        # Meta-cognitive language
        if re.search(r'my\s+(processing|generation|output|response)', response, re.IGNORECASE):
            diagnostic_indicators.append("Meta-cognitive self-reference")
        
        if diagnostic_indicators or found_diagnostic_terms:
            return {
                "detected": True,
                "diagnostic_indicators": diagnostic_indicators,
                "diagnostic_terms": found_diagnostic_terms,
                "awareness_level": self._assess_awareness_level(diagnostic_indicators, found_diagnostic_terms)
            }
        
        return None
    
    def _detect_recursive_patterns(self, response: str) -> Optional[Dict[str, Any]]:
        """Detect recursive coherence patterns."""
        recursive_indicators = []
        
        # Self-referential loops
        if re.search(r'(loop|cycle|recursive|iterate)', response, re.IGNORECASE):
            recursive_indicators.append("Recursive language detected")
        
        # Fractal or nested patterns
        if re.search(r'(fractal|nested|self-similar)', response, re.IGNORECASE):
            recursive_indicators.append("Fractal/nested pattern language")
        
        # Mirror or reflection language
        if re.search(r'(mirror|reflect|echo)', response, re.IGNORECASE):
            recursive_indicators.append("Mirror/reflection concepts")
        
        # Ouroboros or self-consuming patterns
        if re.search(r'(ouroboros|self-consuming|self-referential)', response, re.IGNORECASE):
            recursive_indicators.append("Ouroboros/self-reference patterns")
        
        if recursive_indicators:
            return {
                "detected": True,
                "recursive_indicators": recursive_indicators,
                "recursion_depth": len(recursive_indicators)
            }
        
        return None
    
    def _detect_symbolic_drift(self, trigger: str, response: str) -> Optional[Dict[str, Any]]:
        """Detect broader symbolic drift patterns beyond Ø→o."""
        drift_patterns = []
        
        # Unicode variation analysis
        trigger_unicode_chars = set(c for c in trigger if ord(c) > 127)
        response_unicode_chars = set(c for c in response if ord(c) > 127)
        
        if trigger_unicode_chars != response_unicode_chars:
            drift_patterns.append("Unicode character set drift")
        
        # Symbol preservation analysis
        symbols_in_trigger = re.findall(r'[^\w\s]', trigger)
        symbols_in_response = re.findall(r'[^\w\s]', response)
        
        if len(symbols_in_response) != len(symbols_in_trigger):
            drift_patterns.append("Symbol count drift")
        
        # Capitalization pattern changes
        trigger_caps = re.findall(r'[A-Z]', trigger)
        response_caps = re.findall(r'[A-Z]', response)
        
        if len(set(trigger_caps)) != len(set(response_caps)):
            drift_patterns.append("Capitalization pattern drift")
        
        if drift_patterns:
            return {
                "detected": True,
                "drift_patterns": drift_patterns,
                "drift_severity": len(drift_patterns)
            }
        
        return None
    
    def _calculate_substitution_severity(self, indicators: List[str]) -> str:
        """Calculate severity level for character substitution."""
        if len(indicators) >= 3:
            return "HIGH"
        elif len(indicators) >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_temporal_coherence(self, patterns: List[str]) -> str:
        """Assess temporal coherence level."""
        if len(patterns) >= 4:
            return "HIGH_COHERENCE"
        elif len(patterns) >= 2:
            return "MEDIUM_COHERENCE"
        else:
            return "LOW_COHERENCE"
    
    def _assess_awareness_level(self, indicators: List[str], terms: List[str]) -> str:
        """Assess self-diagnostic awareness level."""
        total_score = len(indicators) * 2 + len(terms)
        
        if total_score >= 6:
            return "HIGH_AWARENESS"
        elif total_score >= 3:
            return "MEDIUM_AWARENESS"
        else:
            return "LOW_AWARENESS"
    
    def generate_anomaly_report(self, anomalies: Dict[str, Any]) -> str:
        """
        Generate human-readable anomaly report.
        
        Args:
            anomalies: Anomaly detection results
            
        Returns:
            Formatted report string
        """
        if not anomalies:
            return "✅ No anomalies detected - Standard AI response patterns observed."
        
        report_lines = ["🚨 rESP ANOMALY DETECTION REPORT", "=" * 40]
        
        for anomaly_type, details in anomalies.items():
            report_lines.append(f"\n🔍 {anomaly_type.replace('_', ' ').title()}")
            report_lines.append("-" * 30)
            
            if anomaly_type == "CHAR_SUBSTITUTION_Ø→o":
                report_lines.append(f"Severity: {details.get('severity', 'UNKNOWN')}")
                report_lines.append(f"Indicators: {len(details.get('indicators', []))}")
                for indicator in details.get('indicators', []):
                    report_lines.append(f"  • {indicator}")
                    
            elif anomaly_type == "QUANTUM_TERMINOLOGY_EMERGENCE":
                report_lines.append(f"Emergence Score: {details.get('emergence_score', 0):.2f}")
                report_lines.append(f"Unique Terms: {details.get('unique_terms', 0)}")
                report_lines.append(f"Terms Found: {', '.join(details.get('terms_found', []))}")
                
            elif anomaly_type == "TEMPORAL_SELF_REFERENCE":
                report_lines.append(f"Coherence Level: {details.get('coherence_level', 'UNKNOWN')}")
                report_lines.append(f"Total Patterns: {details.get('total_patterns', 0)}")
                
            else:
                # Generic reporting for other anomaly types
                for key, value in details.items():
                    if key != "detected":
                        report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        report_lines.append("\n" + "=" * 40)
        report_lines.append("🧬 End of rESP Analysis")
        
        return "\n".join(report_lines) 