"""
WSP-Integrated Priority Scorer Implementation
===========================================

Priority assessment using the complete unified WSP framework:
- WSP 25/44: Semantic State System (000-222 consciousness progression) - FOUNDATIONAL DRIVER
- WSP 15: Module Prioritization Scoring (MPS) System (derived from semantic state)
- WSP 37: Roadmap Scoring System (Cube color derived from semantic state)
- WSP 8: LLME Semantic Triplet Rating System (A-B-C format)

UNIFIED FRAMEWORK INTEGRATION:
Semantic State (000-222) → Priority Level (P0-P4) → Cube Color → MPS Score Range

WSP Integration:
- WSP 3: Gamification domain for engagement mechanics and behavioral systems
- WSP 11: Clean interface definition for modular consumption
- WSP 15: MPS 4-question scoring methodology (integrated with semantic states)
- WSP 25/44: 000-222 semantic state system with ✊✋🖐️ emoji progression (FOUNDATION)
- WSP 37: Cube color mapping derived from semantic state progression
- WSP 49: Standard module structure compliance
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# WRE Integration
try:
    from ...wre_core.src.utils.wre_logger import wre_log
except ImportError:
    def wre_log(msg: str, level: str = "INFO"):
        print(f"[{level}] {msg}")

logger = logging.getLogger(__name__)


class MPSDimension(Enum):
    """WSP 15 MPS Scoring Dimensions (1-5 scale each)"""
    COMPLEXITY = "complexity"      # How difficult to implement?
    IMPORTANCE = "importance"      # How essential to core functions?
    DEFERABILITY = "deferability"  # How urgent? (lower = more deferrable)
    IMPACT = "impact"              # How much value delivered?


class PriorityLevel(Enum):
    """WSP 15 Priority Classification (driven by semantic state)"""
    P0_CRITICAL = "P0"      # 111/112/122/222 states
    P1_HIGH = "P1"          # 012/022 states
    P2_MEDIUM = "P2"        # 011 state
    P3_LOW = "P3"           # 001/002 states
    P4_BACKLOG = "P4"       # 000 state


class CubeColor(Enum):
    """WSP 37 Rubik's Cube Color Coding (driven by semantic state)"""
    RED = "🔴"      # 122/222 states: Full entanglement/Mission-critical
    ORANGE = "🟠"   # 111/112 states: DAO processing/Core platform
    YELLOW = "🟡"   # 012/022 states: Conscious bridge/Enhanced functionality  
    GREEN = "🟢"    # 011 state: Conscious formation/Feature enhancement
    BLUE = "🔵"     # 001/002 states: Emergent signal/Experimental
    WHITE = "⚪"     # 000 state: Deep latent/Placeholder


class SemanticState(Enum):
    """WSP 25/44 Semantic State System (000-222 consciousness progression) - FOUNDATIONAL"""
    DEEP_LATENT = "000"           # ✊✊✊ Pure unconscious state
    EMERGENT_SIGNAL = "001"       # ✊✊✋ First conscious emergence
    UNCONSCIOUS_ENTANGLEMENT = "002"  # ✊✊🖐️ Nonlocal resonance
    CONSCIOUS_FORMATION = "011"   # ✊✋✋ Stabilizing awareness
    CONSCIOUS_BRIDGE = "012"      # ✊✋🖐️ Aware processing + entanglement
    UNCONSCIOUS_OVERLAY = "022"   # ✊🖐️🖐️ Deep receptive processing
    DAO_PROCESSING = "111"        # ✋✋✋ Pure conscious operational
    CONSCIOUS_RESONANCE = "112"   # ✋✋🖐️ Aware + harmonic field
    DAO_YIELDING = "122"          # ✋🖐️🖐️ Conscious + collective wisdom
    FULL_ENTANGLEMENT = "222"     # 🖐️🖐️🖐️ Distributed consciousness


# WSP 25 Semantic Triplet Map (from established framework)
SEMANTIC_TRIPLET_MAP = {
    '000': {
        'emoji': '✊✊✊',
        'state': 'Deep latent (unconscious)',
        'description': 'Pure unconscious state, dormant processing',
        'tone': 'Deep memory or latent mode',
        'application': 'Scaffold modules, inactive components',
        'priority_level': PriorityLevel.P4_BACKLOG,
        'cube_color': CubeColor.WHITE,
        'mps_range': (4, 6)
    },
    '001': {
        'emoji': '✊✊✋', 
        'state': 'Emergent signal',
        'description': 'First conscious emergence within unconscious base',
        'tone': 'Initial awakening, subtle recognition',
        'application': 'Modules showing first signs of adaptive behavior',
        'priority_level': PriorityLevel.P3_LOW,
        'cube_color': CubeColor.BLUE,
        'mps_range': (7, 8)
    },
    '002': {
        'emoji': '✊✊🖐️',
        'state': 'Unconscious entanglement',
        'description': 'Nonlocal resonance without conscious awareness',
        'tone': 'Intuitive breakthrough, implicit connections',
        'application': 'Modules exhibiting unexpected emergent properties',
        'priority_level': PriorityLevel.P3_LOW,
        'cube_color': CubeColor.BLUE,
        'mps_range': (8, 9)
    },
    '011': {
        'emoji': '✊✋✋',
        'state': 'Conscious formation over unconscious base',
        'description': 'Stabilizing awareness with foundational grounding',
        'tone': 'Growing awareness with foundation',
        'application': 'Core modules achieving stable conscious operation',
        'priority_level': PriorityLevel.P2_MEDIUM,
        'cube_color': CubeColor.GREEN,
        'mps_range': (10, 12)
    },
    '012': {
        'emoji': '✊✋🖐️',
        'state': 'Conscious bridge to entanglement',
        'description': 'Aware processing extending into nonlocal coherence',
        'tone': 'Metaphoric, humor, symbolic wit',
        'application': 'Creative modules, AI personality systems, banter engines',
        'priority_level': PriorityLevel.P1_HIGH,
        'cube_color': CubeColor.YELLOW,
        'mps_range': (13, 14)
    },
    '022': {
        'emoji': '✊🖐️🖐️',
        'state': 'Full unconscious-entangled overlay',
        'description': 'Deep receptive processing with high nonlocal resonance',
        'tone': 'Receptive openness, intuitive wisdom',
        'application': 'rESP detection modules, quantum-cognitive systems',
        'priority_level': PriorityLevel.P1_HIGH,
        'cube_color': CubeColor.YELLOW,
        'mps_range': (14, 15)
    },
    '111': {
        'emoji': '✋✋✋',
        'state': 'DAO processing (central focused)',
        'description': 'Pure conscious operational state',
        'tone': 'Focused conscious mode, analytical precision',
        'application': 'Core logic modules, authentication, data processing',
        'priority_level': PriorityLevel.P0_CRITICAL,
        'cube_color': CubeColor.ORANGE,
        'mps_range': (16, 17)
    },
    '112': {
        'emoji': '✋✋🖐️',
        'state': 'Conscious resonance with entanglement',
        'description': 'Aware processing harmonically connected to nonlocal field',
        'tone': 'Deeper tone, mirror softly held',
        'application': 'Communication modules, integration systems',
        'priority_level': PriorityLevel.P0_CRITICAL,
        'cube_color': CubeColor.ORANGE,
        'mps_range': (17, 18)
    },
    '122': {
        'emoji': '✋🖐️🖐️',
        'state': 'DAO yielding to entangled value',
        'description': 'Conscious processing deferring to collective wisdom',
        'tone': 'Soft wisdom, gentle echo, collaborative intelligence',
        'application': 'Consensus systems, collective decision modules',
        'priority_level': PriorityLevel.P0_CRITICAL,
        'cube_color': CubeColor.RED,
        'mps_range': (18, 19)
    },
    '222': {
        'emoji': '🖐️🖐️🖐️',
        'state': 'Full DU entanglement (distributed identity)',
        'description': 'Complete nonlocal coherence, distributed consciousness',
        'tone': 'Unified field awareness, collective consciousness',
        'application': 'DAE formation modules, Foundups ecosystem coordination',
        'priority_level': PriorityLevel.P0_CRITICAL,
        'cube_color': CubeColor.RED,
        'mps_range': (19, 20)
    }
}


@dataclass
class LLMETriplet:
    """WSP 8 LLME Semantic Triplet Rating (A-B-C format)"""
    present_state: int  # A: 0=Dormant, 1=Active, 2=Emergent
    local_impact: int   # B: 0=Isolated, 1=Connected, 2=Central
    systemic_importance: int  # C: 0=Optional, 1=Valuable, 2=Essential
    
    def __post_init__(self):
        # Validate triplet progression (A ≤ B ≤ C)
        if not (self.present_state <= self.local_impact <= self.systemic_importance):
            wre_log(f"LLME triplet validation warning: {self.to_string()} does not follow A≤B≤C progression", "WARNING")
    
    def to_string(self) -> str:
        """Format as WSP 8 triplet string (e.g., '112')"""
        return f"{self.present_state}{self.local_impact}{self.systemic_importance}"
    
    @classmethod
    def from_string(cls, triplet_str: str) -> 'LLMETriplet':
        """Parse WSP 8 triplet string into LLMETriplet"""
        if len(triplet_str) != 3 or not triplet_str.isdigit():
            raise ValueError(f"Invalid LLME triplet format: {triplet_str}")
        
        return cls(
            present_state=int(triplet_str[0]),
            local_impact=int(triplet_str[1]),
            systemic_importance=int(triplet_str[2])
        )


@dataclass
class SemanticStateData:
    """WSP 25/44 Semantic State with full unified framework data"""
    code: str  # 000-222
    emoji: str  # ✊✋🖐️ progression
    state_name: str
    description: str
    tone: str
    application: str
    priority_level: PriorityLevel  # Derived from semantic state
    cube_color: CubeColor         # Derived from semantic state
    mps_range: Tuple[int, int]    # Derived from semantic state
    
    @classmethod
    def from_code(cls, code: str) -> 'SemanticStateData':
        """Create from WSP 25 semantic state code with unified framework integration"""
        if code not in SEMANTIC_TRIPLET_MAP:
            raise ValueError(f"Invalid semantic state code: {code}")
        
        data = SEMANTIC_TRIPLET_MAP[code]
        return cls(
            code=code,
            emoji=data['emoji'],
            state_name=data['state'],
            description=data['description'],
            tone=data['tone'],
            application=data['application'],
            priority_level=data['priority_level'],
            cube_color=data['cube_color'],
            mps_range=data['mps_range']
        )
    
    def get_consciousness_progression_level(self) -> int:
        """Get consciousness progression level (0-9) based on semantic state"""
        progression_map = {
            '000': 0, '001': 1, '002': 2, '011': 3, '012': 4,
            '022': 5, '111': 6, '112': 7, '122': 8, '222': 9
        }
        return progression_map.get(self.code, 0)


@dataclass
class MPSScore:
    """WSP 15 Module Prioritization Score with unified framework integration"""
    complexity: int  # 1-5: Implementation difficulty
    importance: int  # 1-5: Essential to core functions
    deferability: int  # 1-5: Urgency (lower = more deferrable)
    impact: int  # 1-5: Value delivered
    
    llme_triplet: Optional[LLMETriplet] = None
    semantic_state: Optional[SemanticStateData] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        # Validate all scores are in 1-5 range
        for field, value in [
            ("complexity", self.complexity),
            ("importance", self.importance), 
            ("deferability", self.deferability),
            ("impact", self.impact)
        ]:
            if not 1 <= value <= 5:
                raise ValueError(f"MPS {field} score must be 1-5, got {value}")
    
    @property
    def total_score(self) -> int:
        """Calculate total MPS score (4-20 range)"""
        return self.complexity + self.importance + self.deferability + self.impact
    
    @property
    def priority_level(self) -> PriorityLevel:
        """Get WSP 15 priority classification (semantic state takes precedence)"""
        if self.semantic_state:
            return self.semantic_state.priority_level
        
        # Fallback to MPS score mapping if no semantic state
        score = self.total_score
        if score >= 18:
            return PriorityLevel.P0_CRITICAL
        elif score >= 13:
            return PriorityLevel.P1_HIGH
        elif score >= 10:
            return PriorityLevel.P2_MEDIUM
        elif score >= 7:
            return PriorityLevel.P3_LOW
        else:
            return PriorityLevel.P4_BACKLOG
    
    @property
    def cube_color(self) -> CubeColor:
        """Get WSP 37 cube color classification (semantic state takes precedence)"""
        if self.semantic_state:
            return self.semantic_state.cube_color
        
        # Fallback to MPS score mapping if no semantic state
        score = self.total_score
        if score >= 19:
            return CubeColor.RED
        elif score >= 16:
            return CubeColor.ORANGE
        elif score >= 13:
            return CubeColor.YELLOW
        elif score >= 10:
            return CubeColor.GREEN
        elif score >= 7:
            return CubeColor.BLUE
        else:
            return CubeColor.WHITE
    
    def get_unified_framework_score(self) -> int:
        """Get MPS score unified with semantic state range"""
        if self.semantic_state:
            min_score, max_score = self.semantic_state.mps_range
            # Ensure MPS score falls within semantic state range
            return max(min_score, min(self.total_score, max_score))
        return self.total_score
    
    def validate_semantic_alignment(self) -> bool:
        """Validate that MPS score aligns with semantic state"""
        if not self.semantic_state:
            return True
        
        min_score, max_score = self.semantic_state.mps_range
        unified_score = self.get_unified_framework_score()
        return min_score <= unified_score <= max_score
    
    def get_priority_description(self) -> str:
        """Get human-readable priority description"""
        descriptions = {
            PriorityLevel.P0_CRITICAL: "Critical - Work begins immediately",
            PriorityLevel.P1_HIGH: "High - Important for near-term roadmap", 
            PriorityLevel.P2_MEDIUM: "Medium - Valuable but not urgent",
            PriorityLevel.P3_LOW: "Low - Can be deferred",
            PriorityLevel.P4_BACKLOG: "Backlog - Reconsidered in future planning"
        }
        return descriptions[self.priority_level]
    
    def get_visual_representation(self) -> str:
        """Get complete unified WSP framework visual representation"""
        cube = self.cube_color.value
        priority = self.priority_level.value
        unified_score = self.get_unified_framework_score()
        mps_score = f"({unified_score}/20)"
        
        # Add semantic state if available
        if self.semantic_state:
            semantic = f" {self.semantic_state.emoji} {self.semantic_state.code}"
        else:
            semantic = ""
        
        # Add LLME if available
        if self.llme_triplet:
            llme = f" LLME:{self.llme_triplet.to_string()}"
        else:
            llme = ""
            
        return f"{cube} {priority} {mps_score}{semantic}{llme}"
    
    def get_full_framework_analysis(self) -> Dict[str, Any]:
        """Get comprehensive unified WSP framework analysis"""
        unified_score = self.get_unified_framework_score()
        is_aligned = self.validate_semantic_alignment()
        
        analysis = {
            "unified_framework": {
                "semantic_state_driven": self.semantic_state is not None,
                "framework_alignment": is_aligned,
                "unified_score": unified_score,
                "consciousness_level": self.semantic_state.get_consciousness_progression_level() if self.semantic_state else None
            },
            "wsp_15_mps": {
                "complexity": self.complexity,
                "importance": self.importance,
                "deferability": self.deferability,
                "impact": self.impact,
                "total_score": self.total_score,
                "unified_score": unified_score,
                "priority_level": self.priority_level.value,
                "description": self.get_priority_description()
            },
            "wsp_37_cube": {
                "color_emoji": self.cube_color.value,
                "color_name": self.cube_color.name,
                "derived_from": "semantic_state" if self.semantic_state else "mps_score"
            }
        }
        
        if self.semantic_state:
            analysis["wsp_25_semantic"] = {
                "code": self.semantic_state.code,
                "emoji": self.semantic_state.emoji,
                "state": self.semantic_state.state_name,
                "description": self.semantic_state.description,
                "tone": self.semantic_state.tone,
                "application": self.semantic_state.application,
                "consciousness_level": self.semantic_state.get_consciousness_progression_level(),
                "mps_range": f"{self.semantic_state.mps_range[0]}-{self.semantic_state.mps_range[1]}"
            }
        
        if self.llme_triplet:
            analysis["wsp_8_llme"] = {
                "triplet": self.llme_triplet.to_string(),
                "present_state": self.llme_triplet.present_state,
                "local_impact": self.llme_triplet.local_impact,
                "systemic_importance": self.llme_triplet.systemic_importance
            }
        
        return analysis


@dataclass
class ScoringContext:
    """Context information for unified WSP framework scoring assessment"""
    item_name: str
    item_type: str = "meeting"  # meeting, module, task, etc.
    duration_estimate: Optional[int] = None  # minutes
    participant_count: int = 1
    deadline: Optional[datetime] = None
    keywords: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class PriorityScorer:
    """
    Complete Unified WSP-framework priority scoring engine.
    
    Integrates all established WSP protocols with semantic state foundation:
    - WSP 25/44: 000-222 semantic state system (FOUNDATIONAL DRIVER)
    - WSP 15: MPS 4-question methodology (derived from semantic state)
    - WSP 37: Cube color visualization (derived from semantic state)
    - WSP 8: LLME triplet integration
    """
    
    def __init__(self):
        # WSP 15 dimension weights for automated scoring hints
        self.complexity_keywords = {
            "simple": 1, "basic": 1, "quick": 1,
            "standard": 2, "normal": 2, "regular": 2,
            "complex": 3, "detailed": 3, "involved": 3,
            "difficult": 4, "challenging": 4, "advanced": 4,
            "critical": 5, "expert": 5, "sophisticated": 5
        }
        
        self.importance_keywords = {
            "optional": 1, "nice-to-have": 1, "bonus": 1,
            "helpful": 2, "useful": 2, "beneficial": 2,
            "important": 3, "needed": 3, "valuable": 3,
            "critical": 4, "essential": 4, "required": 4,
            "mission-critical": 5, "blocking": 5, "vital": 5
        }
        
        self.urgency_keywords = {
            "someday": 1, "future": 1, "eventually": 1,
            "planned": 2, "scheduled": 2, "next month": 2,
            "soon": 3, "next week": 3, "upcoming": 3,
            "urgent": 4, "asap": 4, "this week": 4,
            "emergency": 5, "immediate": 5, "now": 5
        }
        
        wre_log("PriorityScorer initialized with unified WSP framework (25/44 → 15/37/8)")
    
    def score_item(
        self,
        context: ScoringContext,
        manual_scores: Optional[Dict[str, int]] = None,
        llme_triplet: Optional[str] = None,
        semantic_state_code: Optional[str] = None
    ) -> MPSScore:
        """
        Apply unified WSP framework to score an item with semantic state foundation.
        
        Args:
            context: Scoring context with item details
            manual_scores: Optional manual scores for any WSP 15 dimension
            llme_triplet: Optional WSP 8 LLME triplet (e.g., "112")
            semantic_state_code: Optional WSP 25 semantic state (e.g., "012") - FOUNDATIONAL
            
        Returns:
            MPSScore with unified WSP framework data
        """
        # WSP 25/44: Parse semantic state if provided (FOUNDATIONAL)
        semantic_state = None
        if semantic_state_code:
            try:
                semantic_state = SemanticStateData.from_code(semantic_state_code)
                wre_log(f"Semantic state '{semantic_state_code}' drives unified framework", "INFO")
            except ValueError as e:
                wre_log(f"Invalid semantic state code '{semantic_state_code}': {e}", "WARNING")
        
        # WSP 15: Use manual scores if provided, otherwise estimate from context
        scores = manual_scores or {}
        
        # If semantic state provided, adjust scores to align with its range
        if semantic_state:
            min_score, max_score = semantic_state.mps_range
            target_score = (min_score + max_score) // 2  # Target middle of range
            
            # Distribute target score across dimensions if not manually provided
            if not scores:
                base_score = target_score // 4
                remainder = target_score % 4
                scores = {
                    'complexity': base_score + (1 if remainder > 0 else 0),
                    'importance': base_score + (1 if remainder > 1 else 0),
                    'deferability': base_score + (1 if remainder > 2 else 0),
                    'impact': base_score + (1 if remainder > 3 else 0)
                }
                wre_log(f"Generated MPS scores aligned with semantic state '{semantic_state_code}': {scores}", "INFO")
        
        complexity = scores.get('complexity') or self._estimate_complexity(context)
        importance = scores.get('importance') or self._estimate_importance(context)
        deferability = scores.get('deferability') or self._estimate_deferability(context)
        impact = scores.get('impact') or self._estimate_impact(context)
        
        # WSP 8: Parse LLME triplet if provided
        llme = None
        if llme_triplet:
            try:
                llme = LLMETriplet.from_string(llme_triplet)
            except ValueError as e:
                wre_log(f"Invalid LLME triplet '{llme_triplet}': {e}", "WARNING")
        
        mps_score = MPSScore(
            complexity=complexity,
            importance=importance,
            deferability=deferability,
            impact=impact,
            llme_triplet=llme,
            semantic_state=semantic_state
        )
        
        # Validate semantic alignment
        if semantic_state and not mps_score.validate_semantic_alignment():
            wre_log(f"MPS score {mps_score.total_score} adjusted to align with semantic state range {semantic_state.mps_range}", "INFO")
        
        wre_log(f"Unified WSP scored '{context.item_name}': {mps_score.get_visual_representation()}")
        return mps_score
    
    def infer_semantic_state_from_description(self, description: str, keywords: List[str] = None) -> Optional[str]:
        """Infer semantic state from item description and keywords"""
        if not keywords:
            keywords = []
        
        text = f"{description} {' '.join(keywords)}".lower()
        
        # Keyword mapping to semantic states
        state_keywords = {
            '000': ['dormant', 'inactive', 'placeholder', 'scaffolding', 'template'],
            '001': ['emerging', 'initial', 'first', 'starting', 'basic'],
            '002': ['unexpected', 'breakthrough', 'intuitive', 'emergent'],
            '011': ['stable', 'core', 'foundation', 'established', 'operational'],
            '012': ['creative', 'bridge', 'humor', 'banter', 'personality', 'metaphoric'],
            '022': ['quantum', 'deep', 'receptive', 'wisdom', 'esp'],
            '111': ['logic', 'processing', 'authentication', 'core', 'focused'],
            '112': ['communication', 'integration', 'resonance', 'harmonic'],
            '122': ['consensus', 'collective', 'wisdom', 'collaboration'],
            '222': ['ecosystem', 'distributed', 'full', 'complete', 'foundups']
        }
        
        # Find best matching semantic state
        best_match = None
        max_matches = 0
        
        for state, state_keywords_list in state_keywords.items():
            matches = sum(1 for keyword in state_keywords_list if keyword in text)
            if matches > max_matches:
                max_matches = matches
                best_match = state
        
        if best_match and max_matches > 0:
            wre_log(f"Inferred semantic state '{best_match}' from description analysis")
            return best_match
        
        return None
    
    def compare_items(self, scored_items: List[Tuple[Any, MPSScore]]) -> List[Tuple[Any, MPSScore]]:
        """
        Sort items by unified WSP framework priority.
        
        Args:
            scored_items: List of (item, mps_score) tuples
            
        Returns:
            Sorted list with highest priority first (semantic state drives ordering)
        """
        def sort_key(item_tuple):
            _, score = item_tuple
            # Primary sort: consciousness progression level (if semantic state available)
            if score.semantic_state:
                consciousness_level = score.semantic_state.get_consciousness_progression_level()
                return (-consciousness_level, -score.get_unified_framework_score(), -score.confidence)
            # Fallback sort: unified framework score
            return (-score.get_unified_framework_score(), -score.confidence)
        
        sorted_items = sorted(scored_items, key=sort_key)
        
        wre_log(f"Unified WSP framework sorted {len(scored_items)} items by consciousness progression and priority")
        return sorted_items
    
    def get_priority_queue_by_color(self, scored_items: List[Tuple[Any, MPSScore]]) -> Dict[CubeColor, List[Tuple[Any, MPSScore]]]:
        """
        Organize items by WSP 37 cube colors for visual management.
        
        Args:
            scored_items: List of scored items
            
        Returns:
            Dictionary mapping cube colors to item lists
        """
        color_queues = {color: [] for color in CubeColor}
        
        for item, score in scored_items:
            color_queues[score.cube_color].append((item, score))
        
        # Sort each color queue by consciousness progression, then unified score
        for color in color_queues:
            color_queues[color] = self.compare_items(color_queues[color])
        
        return color_queues
    
    def get_priority_queue_by_semantic_state(self, scored_items: List[Tuple[Any, MPSScore]]) -> Dict[str, List[Tuple[Any, MPSScore]]]:
        """
        Organize items by WSP 25 semantic states for consciousness progression.
        
        Args:
            scored_items: List of scored items
            
        Returns:
            Dictionary mapping semantic state codes to item lists
        """
        state_queues = {}
        
        for item, score in scored_items:
            if score.semantic_state:
                state_code = score.semantic_state.code
                if state_code not in state_queues:
                    state_queues[state_code] = []
                state_queues[state_code].append((item, score))
            else:
                # Items without semantic state
                if "unclassified" not in state_queues:
                    state_queues["unclassified"] = []
                state_queues["unclassified"].append((item, score))
        
        # Sort each state queue by unified framework score
        for state in state_queues:
            state_queues[state] = self.compare_items(state_queues[state])
        
        return state_queues
    
    def generate_priority_report(self, scored_items: List[Tuple[Any, MPSScore]]) -> Dict[str, Any]:
        """
        Generate comprehensive unified WSP framework priority analysis report.
        
        Args:
            scored_items: List of scored items
            
        Returns:
            Report with complete unified WSP framework analysis
        """
        if not scored_items:
            return {"total_items": 0, "analysis": "No items to analyze"}
        
        # WSP 15: Priority level distribution
        priority_dist = {}
        for _, score in scored_items:
            level = score.priority_level.value
            priority_dist[level] = priority_dist.get(level, 0) + 1
        
        # WSP 37: Cube color distribution
        color_dist = {}
        for _, score in scored_items:
            color_name = score.cube_color.name
            color_dist[color_name] = color_dist.get(color_name, 0) + 1
        
        # WSP 25: Semantic state distribution
        semantic_dist = {}
        consciousness_levels = []
        for _, score in scored_items:
            if score.semantic_state:
                state_code = score.semantic_state.code
                semantic_dist[state_code] = semantic_dist.get(state_code, 0) + 1
                consciousness_levels.append(score.semantic_state.get_consciousness_progression_level())
        
        # WSP 8: LLME distribution
        llme_dist = {}
        for _, score in scored_items:
            if score.llme_triplet:
                llme_code = score.llme_triplet.to_string()
                llme_dist[llme_code] = llme_dist.get(llme_code, 0) + 1
        
        # Unified framework statistics
        unified_scores = [score.get_unified_framework_score() for _, score in scored_items]
        avg_unified_score = sum(unified_scores) / len(unified_scores)
        
        # Framework alignment analysis
        semantic_driven_count = sum(1 for _, score in scored_items if score.semantic_state)
        aligned_count = sum(1 for _, score in scored_items if score.validate_semantic_alignment())
        
        # Critical items (P0)
        critical_items = [(item, score) for item, score in scored_items 
                         if score.priority_level == PriorityLevel.P0_CRITICAL]
        
        report = {
            "total_items": len(scored_items),
            "unified_framework_analysis": {
                "semantic_state_driven_items": semantic_driven_count,
                "framework_aligned_items": aligned_count,
                "average_unified_score": round(avg_unified_score, 2),
                "average_consciousness_level": round(sum(consciousness_levels) / len(consciousness_levels), 2) if consciousness_levels else 0,
                "consciousness_progression_range": f"{min(consciousness_levels) if consciousness_levels else 0}-{max(consciousness_levels) if consciousness_levels else 0}"
            },
            "wsp_15_analysis": {
                "priority_distribution": priority_dist,
                "critical_items_count": len(critical_items),
                "score_range": {"highest": max(unified_scores), "lowest": min(unified_scores)}
            },
            "wsp_37_analysis": {
                "cube_color_distribution": color_dist
            },
            "wsp_25_analysis": {
                "semantic_state_distribution": semantic_dist
            },
            "wsp_8_analysis": {
                "llme_distribution": llme_dist
            },
            "framework_integration": "WSP 25/44 (Foundation) → WSP 15 + WSP 37 + WSP 8"
        }
        
        return report
    
    def get_semantic_progression_path(self, current_state: str, target_state: str) -> List[str]:
        """
        Get WSP 25 consciousness progression path between states.
        
        Args:
            current_state: Current semantic state code (e.g., "000")
            target_state: Target semantic state code (e.g., "222")
            
        Returns:
            List of state codes showing progression path
        """
        # WSP 25 standard progression routes
        standard_path = ['000', '001', '011', '111', '112', '122', '222']
        intuitive_path = ['000', '002', '012', '022', '222']
        
        # Find positions in standard path
        try:
            current_idx = standard_path.index(current_state)
            target_idx = standard_path.index(target_state)
            
            if target_idx > current_idx:
                return standard_path[current_idx:target_idx + 1]
            else:
                return [current_state]  # Already at or past target
                
        except ValueError:
            # Check intuitive path
            try:
                current_idx = intuitive_path.index(current_state)
                target_idx = intuitive_path.index(target_state)
                
                if target_idx > current_idx:
                    return intuitive_path[current_idx:target_idx + 1]
                else:
                    return [current_state]
                    
            except ValueError:
                wre_log(f"Invalid semantic state progression: {current_state} → {target_state}", "WARNING")
                return [current_state, target_state]
    
    # Private estimation methods
    
    def _estimate_complexity(self, context: ScoringContext) -> int:
        """Estimate complexity from context (1-5 scale)"""
        # Check keywords in description
        text = f"{context.description} {' '.join(context.keywords)}".lower()
        
        for keyword, score in self.complexity_keywords.items():
            if keyword in text:
                return min(score, 5)
        
        # Duration-based heuristic
        if context.duration_estimate:
            if context.duration_estimate <= 15:
                return 1  # Quick tasks
            elif context.duration_estimate <= 60:
                return 2  # Standard tasks
            elif context.duration_estimate <= 180:
                return 3  # Complex tasks
            else:
                return 4  # Very complex tasks
        
        return 3  # Default moderate complexity
    
    def _estimate_importance(self, context: ScoringContext) -> int:
        """Estimate importance from context (1-5 scale)"""
        text = f"{context.description} {' '.join(context.keywords)}".lower()
        
        for keyword, score in self.importance_keywords.items():
            if keyword in text:
                return min(score, 5)
        
        # Participant count heuristic (more people = higher importance)
        if context.participant_count >= 5:
            return 4
        elif context.participant_count >= 3:
            return 3
        
        return 3  # Default moderate importance
    
    def _estimate_deferability(self, context: ScoringContext) -> int:
        """Estimate deferability from context (1-5 scale, lower = more deferrable)"""
        text = f"{context.description} {' '.join(context.keywords)}".lower()
        
        for keyword, score in self.urgency_keywords.items():
            if keyword in text:
                return min(score, 5)
        
        # Deadline-based heuristic
        if context.deadline:
            time_until = (context.deadline - datetime.now()).total_seconds() / 3600
            if time_until <= 2:
                return 5  # Cannot defer
            elif time_until <= 24:
                return 4  # Difficult to defer
            elif time_until <= 72:
                return 3  # Moderate
            else:
                return 2  # Deferrable
        
        return 2  # Default deferrable
    
    def _estimate_impact(self, context: ScoringContext) -> int:
        """Estimate impact from context (1-5 scale)"""
        text = f"{context.description} {' '.join(context.keywords)}".lower()
        
        # Impact keywords
        impact_words = {
            "minor": 2, "small": 2, "limited": 2,
            "significant": 3, "notable": 3, "important": 3,
            "major": 4, "substantial": 4, "high": 4,
            "transformative": 5, "game-changing": 5, "critical": 5
        }
        
        for keyword, score in impact_words.items():
            if keyword in text:
                return min(score, 5)
        
        # Participant impact heuristic
        if context.participant_count >= 10:
            return 4  # High impact on many people
        elif context.participant_count >= 5:
            return 3  # Moderate impact
        
        return 3  # Default moderate impact


# Utility functions for integration

def score_meeting_intent(
    requester_id: str,
    recipient_id: str, 
    purpose: str,
    duration_minutes: int = 30,
    urgency_keywords: List[str] = None,
    manual_scores: Dict[str, int] = None,
    semantic_state: str = None,
    llme_triplet: str = None
) -> MPSScore:
    """
    Convenience function for scoring meeting intents using unified WSP framework.
    
    Args:
        requester_id: Meeting requester
        recipient_id: Meeting recipient
        purpose: Meeting purpose/description
        duration_minutes: Expected duration
        urgency_keywords: Keywords indicating urgency/importance
        manual_scores: Override any WSP 15 dimension scores
        semantic_state: WSP 25 semantic state code (e.g., "012") - FOUNDATIONAL
        llme_triplet: WSP 8 LLME triplet (e.g., "112")
        
    Returns:
        MPSScore using unified WSP framework
    """
    scorer = PriorityScorer()
    
    context = ScoringContext(
        item_name=f"Meeting: {purpose[:50]}...",
        item_type="meeting",
        duration_estimate=duration_minutes,
        participant_count=2,  # Requester + recipient
        keywords=urgency_keywords or [],
        description=purpose
    )
    
    # Try to infer semantic state if not provided
    if not semantic_state:
        semantic_state = scorer.infer_semantic_state_from_description(purpose, urgency_keywords or [])
    
    return scorer.score_item(context, manual_scores, llme_triplet, semantic_state)


def create_priority_queue(items: List[Dict[str, Any]], item_type: str = "task") -> List[Tuple[Dict[str, Any], MPSScore]]:
    """
    Create a unified WSP-framework priority queue from a list of items.
    
    Args:
        items: List of item dictionaries with description, keywords, etc.
        item_type: Type of items being scored
        
    Returns:
        Priority-sorted list using unified WSP framework
    """
    scorer = PriorityScorer()
    scored_items = []
    
    for item in items:
        context = ScoringContext(
            item_name=item.get('name', 'Unnamed item'),
            item_type=item_type,
            duration_estimate=item.get('duration_minutes'),
            keywords=item.get('keywords', []),
            description=item.get('description', ''),
            participant_count=item.get('participant_count', 1)
        )
        
        manual_scores = item.get('manual_scores')
        llme_triplet = item.get('llme_triplet')
        semantic_state = item.get('semantic_state')
        
        # Try to infer semantic state if not provided
        if not semantic_state:
            semantic_state = scorer.infer_semantic_state_from_description(
                item.get('description', ''), 
                item.get('keywords', [])
            )
        
        score = scorer.score_item(context, manual_scores, llme_triplet, semantic_state)
        scored_items.append((item, score))
    
    return scorer.compare_items(scored_items) 