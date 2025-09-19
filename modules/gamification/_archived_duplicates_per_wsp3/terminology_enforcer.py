"""
MAGADOOM Terminology Enforcer
WSP-compliant: Ensures consistent terminology across all announcements
Purpose: Prevent terminology drift and enforce MAGADOOM theme

This module validates and corrects any old terminology that might slip through.
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TerminologyEnforcer:
    """Enforces MAGADOOM terminology across all game announcements."""
    
    def __init__(self):
        # Old terminology -> New terminology mappings
        self.replacements = {
            # Core terms
            r'\bkills?\b': 'whacks',
            r'\bfrags?\b': 'whacks',
            r'\bfragged\b': 'whacked',
            r'\bfragging\b': 'whacking',
            r'\bfragger\b': 'whacker',
            r'\bkilled\b': 'whacked',
            r'\bkilling\b': 'whacking',
            
            # Old rank names (should never appear)
            r'\bCOVFEFE CADET\b': 'GRUNT',
            r'\bQANON QUASHER\b': 'MARINE', 
            r'\bMAGA MAULER\b': 'WARRIOR',
            r'\bTROLL TERMINATOR\b': 'SLAYER',
            r'\bREDHAT RIPPER\b': 'HUNTER',
            r'\bCOUP CRUSHER\b': 'CHAMPION',
            r'\bPATRIOT PULVERIZER\b': 'MASTER',
            r'\bFASCIST FRAGGER\b': 'ELITE',
            r'\bORANGE OBLITERATOR\b': 'GODLIKE',
            r'\bMAGA DOOMSLAYER\b': 'LEGENDARY',
            r'\bDEMOCRACY DEFENDER\b': 'DOOM SLAYER',
            
            # Variations
            r'\bFRAG COUNT\b': 'WHACK COUNT',
            r'\bfrag count\b': 'whack count',
            r'\bTOP FRAGGER\b': 'TOP WHACKER',
            r'\btop fragger\b': 'top whacker',
            
            # Kill variations (critical to replace!)
            r'\bconfirmed kills\b': 'confirmed whacks',
            r'\bCONFIRMED KILLS\b': 'CONFIRMED WHACKS',
            r'\bkills\b': 'whacks',
            r'\bKILLS\b': 'WHACKS',
            r'\bkill\b': 'whack',
            r'\bKILL\b': 'WHACK',
            
            # Preserve special terms
            # Note: "RIP AND TEAR" and "DOOM" references should stay
        }
        
        # Track corrections for learning
        self.corrections_made = []
        
    def enforce(self, text: str) -> str:
        """
        Enforce MAGADOOM terminology on the given text.
        
        Args:
            text: The text to check and correct
            
        Returns:
            The corrected text with proper MAGADOOM terminology
        """
        original = text
        
        # Apply all replacements (case-insensitive where appropriate)
        for old_term, new_term in self.replacements.items():
            if re.search(old_term, text, re.IGNORECASE):
                # Log the correction for tracking
                matches = re.findall(old_term, text, re.IGNORECASE)
                for match in matches:
                    self.corrections_made.append({
                        'original_term': match,
                        'replacement': new_term,
                        'context': text[:50] + '...' if len(text) > 50 else text
                    })
                
                # Perform replacement
                text = re.sub(old_term, new_term, text, flags=re.IGNORECASE)
        
        if text != original:
            logger.warning(f"🔧 Terminology corrected: '{original[:100]}...' -> '{text[:100]}...'")
            
        return text
    
    def validate(self, text: str) -> List[str]:
        """
        Validate text for terminology violations without correcting.
        
        Args:
            text: The text to validate
            
        Returns:
            List of violation messages
        """
        violations = []
        
        for old_term in self.replacements.keys():
            if re.search(old_term, text, re.IGNORECASE):
                matches = re.findall(old_term, text, re.IGNORECASE)
                for match in matches:
                    violations.append(f"Found old terminology: '{match}'")
        
        return violations
    
    def get_correction_stats(self) -> Dict:
        """
        Get statistics about corrections made.
        
        Returns:
            Dictionary with correction statistics
        """
        if not self.corrections_made:
            return {'total_corrections': 0, 'unique_terms': 0}
        
        unique_terms = set(c['original_term'] for c in self.corrections_made)
        
        return {
            'total_corrections': len(self.corrections_made),
            'unique_terms': len(unique_terms),
            'most_common': self._get_most_common_correction(),
            'recent_corrections': self.corrections_made[-5:]
        }
    
    def _get_most_common_correction(self) -> Optional[Dict]:
        """Get the most commonly corrected term."""
        if not self.corrections_made:
            return None
            
        term_counts = {}
        for correction in self.corrections_made:
            term = correction['original_term']
            term_counts[term] = term_counts.get(term, 0) + 1
        
        most_common = max(term_counts.items(), key=lambda x: x[1])
        return {
            'term': most_common[0],
            'count': most_common[1]
        }
    
    def clear_cache(self):
        """Clear the corrections tracking cache."""
        self.corrections_made = []
        logger.info("🔄 Terminology enforcer cache cleared")


# Module-level singleton for easy access
_enforcer = TerminologyEnforcer()

def enforce_terminology(text: str) -> str:
    """
    Global function to enforce MAGADOOM terminology.
    
    Args:
        text: Text to check and correct
        
    Returns:
        Corrected text
    """
    return _enforcer.enforce(text)

def validate_terminology(text: str) -> List[str]:
    """
    Global function to validate terminology without correcting.
    
    Args:
        text: Text to validate
        
    Returns:
        List of violations
    """
    return _enforcer.validate(text)

def get_stats() -> Dict:
    """Get terminology enforcement statistics."""
    return _enforcer.get_correction_stats()

def clear_cache():
    """Clear the terminology cache."""
    _enforcer.clear_cache()