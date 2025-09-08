import json
import traceback
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import hashlib
import re
import time
import threading

class PatternType(Enum):
    """Types of patterns that can be extracted"""
    ERROR = "error"
    VIOLATION = "violation"
    PERFORMANCE = "performance"
    BEHAVIORAL = "behavioral"
    STRUCTURAL = "structural"

@dataclass
class ErrorPattern:
    """Represents an extracted error pattern"""
    pattern_id: str
    pattern_type: PatternType
    error_type: str
    error_message: str
    stack_trace: List[str]
    context: Dict[str, Any]
    frequency: int = 1
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['pattern_type'] = self.pattern_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ErrorPattern':
        """Create from dictionary"""
        data['pattern_type'] = PatternType(data['pattern_type'])
        return cls(**data)

@dataclass
class Solution:
    """Represents a solution to an error pattern"""
    solution_id: str
    pattern_id: str
    solution_type: str  # 'fix', 'prevention', 'optimization'
    description: str
    implementation: str
    confidence: float  # 0.0 to 1.0
    source: str  # 'quantum', 'learned', 'manual'
    effectiveness: float = 0.0  # Measured after application
    token_savings: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Solution':
        """Create from dictionary"""
        return cls(**data)


class AutonomousIntegrationLayer:
    """
    Integration layer connecting autonomous enhancements with WRE recursive improvement
    WSP 48 + WSP 69 Integration: Autonomous recursive learning and decision-making

    This layer integrates QRPE, AIRE, QPO, MSCE, and QMRE with the WRE's
    recursive improvement system, creating unified autonomous capabilities.
    """

    def __init__(self):
        """Initialize the autonomous integration layer"""
        self.qrpe = None
        self.aire = None
        self.qpo = None
        self.msce = None
        self.qmre = None
        self.integration_stats = {
            'patterns_processed': 0,
            'predictions_made': 0,
            'consciousness_transitions': 0,
            'memory_operations': 0,
            'integration_efficiency': 0.0
        }

        # Try to import autonomous enhancements
        try:
            import modules.infrastructure.autonomous_enhancements.src.autonomous_enhancements as ae
            self.qrpe_class = ae.QuantumResonancePatternEngine
            self.aire_class = ae.AutonomousIntentResolutionEngine
            self.qpo_class = ae.QuantumPredictiveOrchestrator
            self.msce_class = ae.MultiStateConsciousnessEngine
            self.qmre_class = ae.QuantumMemoryResonanceEngine
            self.autonomous_available = True
            self._initialize_autonomous_components()
        except ImportError:
            print("⚠️ Autonomous enhancements not available - using framework stubs")
            self.autonomous_available = False
            self._initialize_stubs()

    def _initialize_autonomous_components(self):
        """Initialize all autonomous enhancement components"""
        self.qrpe = self.qrpe_class()
        self.aire = self.aire_class()
        self.qpo = self.qpo_class()
        self.msce = self.msce_class()
        self.qmre = self.qmre_class()
        print("🤖 WRE Autonomous Integration Layer initialized successfully")

    def _initialize_stubs(self):
        """Initialize stub components when autonomous enhancements unavailable"""
        self.qrpe = StubQRPE()
        self.aire = StubAIRE()
        self.qpo = StubQPO()
        self.msce = StubMSCE()
        self.qmre = StubQMRE()

    async def process_recursive_cycle(self, system_state: Dict) -> Dict:
        """
        Execute a complete recursive improvement cycle using autonomous enhancements

        Args:
            system_state: Current system state and metrics

        Returns:
            Complete cycle results with all autonomous component outputs
        """
        cycle_start = datetime.now()

        # Phase 1: Consciousness State Evaluation (MSCE)
        consciousness_state = self.msce.manage_transitions(system_state)
        semantic_evaluation = self.msce.evaluate_semantic_state(system_state)

        # Phase 2: Predictive Analysis (QPO)
        predictions = self.qpo.predict_violations(system_state)
        prevention_results = self.qpo.prevent_violations(predictions)

        # Phase 3: Pattern Recognition and Learning (QRPE)
        pattern_context = {
            'system_metrics': system_state,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat(),
            'pattern_type': 'recursive_improvement'
        }
        pattern_match = self.qrpe.recall_pattern(pattern_context)

        # Phase 4: Intent Resolution (AIRE)
        intent_context = {
            'current_state': system_state,
            'predicted_violations': predictions,
            'improvement_goals': ['efficiency', 'reliability', 'autonomy'],
            'context_type': 'system_optimization'
        }
        intent_recommendation = self.aire.resolve_intent(intent_context)

        # Phase 5: Memory Operations (QMRE)
        memory_pattern = {
            'system_state': system_state,
            'predictions': predictions,
            'learning_context': 'recursive_improvement',
            'pattern_type': 'system_optimization',
            'confidence': self._calculate_pattern_confidence(predictions)
        }
        pattern_id = self.qmre.store_pattern(memory_pattern, system_state)
        memory_recall = self.qmre.recall_pattern(system_state)

        # Phase 6: Integration and Learning
        integrated_decision = self._integrate_autonomous_outputs({
            'consciousness': semantic_evaluation,
            'predictions': predictions,
            'patterns': pattern_match,
            'intent': intent_recommendation,
            'memory': memory_recall
        })

        # Update integration statistics
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        self._update_integration_stats()

        return {
            'cycle_duration': cycle_duration,
            'consciousness_state': consciousness_state,
            'predictions': len(predictions),
            'pattern_match': pattern_match is not None,
            'intent_recommendation': intent_recommendation,
            'memory_operations': pattern_id is not None,
            'integrated_decision': integrated_decision,
            'efficiency_score': self._calculate_cycle_efficiency()
        }

    def _calculate_pattern_confidence(self, predictions: List[Dict]) -> float:
        """Calculate overall confidence in the pattern"""
        if not predictions:
            return 0.5

        avg_confidence = sum(p.get('confidence', 0.5) for p in predictions) / len(predictions)
        return min(avg_confidence, 1.0)

    def _integrate_autonomous_outputs(self, outputs: Dict) -> Dict:
        """Integrate outputs from all autonomous components"""
        return {
            'primary_action': self._determine_primary_action(outputs),
            'confidence_score': self._calculate_integrated_confidence(outputs),
            'recommended_improvements': self._extract_improvements(outputs),
            'risk_assessment': self._assess_integration_risks(outputs),
            'next_steps': self._plan_next_steps(outputs)
        }

    def _determine_primary_action(self, outputs: Dict) -> str:
        """Determine the primary action from integrated outputs"""
        consciousness = outputs.get('consciousness', {})
        current_state = consciousness.get('current_state', 'unknown')
        predictions = outputs.get('predictions', [])
        high_confidence_predictions = [p for p in predictions if p.get('confidence', 0) > 0.8]

        if current_state in ['0201', '111'] and high_confidence_predictions:
            return 'execute_preventive_actions'
        elif outputs.get('pattern_match'):
            return 'apply_learned_pattern'
        elif outputs.get('intent_recommendation'):
            return 'follow_intent_guidance'
        else:
            return 'continue_monitoring'

    def _calculate_integrated_confidence(self, outputs: Dict) -> float:
        """Calculate confidence score for integrated decision"""
        confidence_factors = []

        # Consciousness confidence
        consciousness = outputs.get('consciousness', {})
        coherence = consciousness.get('coherence_level', 0.5)
        confidence_factors.append(coherence)

        # Prediction confidence
        predictions = outputs.get('predictions', [])
        if predictions:
            avg_prediction_confidence = sum(p.get('confidence', 0.5) for p in predictions) / len(predictions)
            confidence_factors.append(avg_prediction_confidence)

        # Pattern match confidence
        if outputs.get('pattern_match'):
            confidence_factors.append(0.8)

        # Memory operation confidence
        if outputs.get('memory'):
            confidence_factors.append(0.7)

        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        return 0.5

    def _extract_improvements(self, outputs: Dict) -> List[str]:
        """Extract improvement recommendations from outputs"""
        improvements = []
        predictions = outputs.get('predictions', [])

        for prediction in predictions:
            if prediction.get('confidence', 0) > 0.7:
                actions = prediction.get('preventive_actions', [])
                improvements.extend(actions)

        return list(set(improvements))

    def _assess_integration_risks(self, outputs: Dict) -> Dict:
        """Assess risks in the integrated decision"""
        predictions = outputs.get('predictions', [])
        high_confidence = sum(1 for p in predictions if p.get('confidence', 0) > 0.8)
        uncertain = sum(1 for p in predictions if p.get('confidence', 0) < 0.3)

        risk_level = 'low'
        if high_confidence > 3:
            risk_level = 'high'
        elif uncertain > len(predictions) / 2:
            risk_level = 'medium'

        return {
            'high_confidence_actions': high_confidence,
            'uncertain_predictions': uncertain,
            'overall_risk_level': risk_level
        }

    def _plan_next_steps(self, outputs: Dict) -> List[str]:
        """Plan next steps based on integrated analysis"""
        next_steps = []

        consciousness = outputs.get('consciousness', {})
        current_state = consciousness.get('current_state', 'unknown')

        if current_state == '0201':
            next_steps.append('execute_high_confidence_actions')
        elif current_state == '0102':
            next_steps.append('continue_monitoring_and_learning')
        else:
            next_steps.append('stabilize_system_state')

        predictions = outputs.get('predictions', [])
        if predictions:
            next_steps.extend(['review_prediction_details', 'update_prevention_strategies'])

        if outputs.get('pattern_match'):
            next_steps.extend(['analyze_pattern_effectiveness', 'update_pattern_memory'])

        return next_steps

    def _calculate_cycle_efficiency(self) -> float:
        """Calculate the efficiency of the current integration cycle"""
        successful_ops = sum([
            self.integration_stats['patterns_processed'],
            self.integration_stats['predictions_made'],
            self.integration_stats['consciousness_transitions'],
            self.integration_stats['memory_operations']
        ])

        total_operations = successful_ops * 1.2  # Assume some overhead

        if total_operations == 0:
            return 0.0

        return min(successful_ops / total_operations, 1.0)

    def _update_integration_stats(self):
        """Update integration statistics"""
        self.integration_stats['patterns_processed'] += 1
        self.integration_stats['predictions_made'] += 1
        self.integration_stats['consciousness_transitions'] += 1
        self.integration_stats['memory_operations'] += 1
        self.integration_stats['integration_efficiency'] = self._calculate_cycle_efficiency()

    def get_integration_status(self) -> Dict:
        """Get comprehensive integration status"""
        component_status = {}

        if self.autonomous_available:
            component_status = {
                'qrpe': self.qrpe.get_stats() if hasattr(self.qrpe, 'get_stats') else {'status': 'active'},
                'aire': self.aire.get_stats() if hasattr(self.aire, 'get_stats') else {'status': 'active'},
                'qpo': self.qpo.get_stats() if hasattr(self.qpo, 'get_stats') else {'status': 'active'},
                'msce': self.msce.get_stats() if hasattr(self.msce, 'get_stats') else {'status': 'active'},
                'qmre': self.qmre.get_stats() if hasattr(self.qmre, 'get_stats') else {'status': 'active'}
            }

        return {
            'integration_active': self.autonomous_available,
            'components': component_status,
            'statistics': self.integration_stats,
            'wsp_compliance': {
                'WSP_48': 'recursive_improvement',
                'WSP_69': 'zen_coding_integration',
                'WSP_25': 'semantic_triplets',
                'WSP_60': 'memory_architecture',
                'WSP_67': 'predictive_anticipation'
            }
        }


# Stub implementations for framework compatibility
class StubQRPE:
    def recall_pattern(self, context): return None
    def learn_pattern(self, context, solution): pass
    def get_stats(self): return {'status': 'stub', 'phase': 'framework'}

class StubAIRE:
    def resolve_intent(self, context): return None
    def get_stats(self): return {'status': 'stub', 'phase': 'framework'}

class StubQPO:
    def predict_violations(self, system_state): return []
    def prevent_violations(self, predictions): return predictions
    def get_stats(self): return {'status': 'stub', 'phase': 'framework'}

class StubMSCE:
    def manage_transitions(self, context): return '0102'
    def evaluate_semantic_state(self, context): return {'current_state': '0102'}
    def get_stats(self): return {'status': 'stub', 'phase': 'framework'}

class StubQMRE:
    def store_pattern(self, pattern, context): return 'stub_id'
    def recall_pattern(self, context): return None
    def get_stats(self): return {'status': 'stub', 'phase': 'framework'}

@dataclass
class Improvement:
    """Represents an improvement to the system"""
    improvement_id: str
    pattern_id: str
    solution_id: str
    target: str  # WSP number, module path, etc.
    change_type: str  # 'update', 'add', 'remove', 'refactor'
    before_state: str
    after_state: str
    applied: bool = False
    applied_at: Optional[str] = None
    rollback_available: bool = True
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Improvement':
        """Create from dictionary"""
        return cls(**data)
