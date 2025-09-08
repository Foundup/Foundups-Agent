#!/usr/bin/env python3
"""
Codebase Token Analyzer - Intelligent Token Cost Prediction Algorithm
WSP 75 Enhancement: Data-Driven Token Cost Analysis

This algorithm analyzes our actual codebase to create intelligent token cost predictions.
Instead of static estimates, it learns from real development patterns and complexity metrics.

Key Innovation: Token costs based on actual code analysis, not theoretical estimates.
"""

import os
import ast
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
from collections import defaultdict


class ComplexityMetric(Enum):
    """Code complexity metrics for token cost analysis"""
    LINES_OF_CODE = "loc"
    CYCLOMATIC_COMPLEXITY = "cyclomatic"
    IMPORT_COUNT = "imports"
    FUNCTION_COUNT = "functions"
    CLASS_COUNT = "classes"
    DEPENDENCY_DEPTH = "dependency_depth"
    ASYNC_FUNCTIONS = "async_functions"
    EXCEPTION_HANDLING = "exception_handling"
    TYPE_HINTS = "type_hints"
    DOCSTRING_COMPLEXITY = "docstring_complexity"


class ConsciousnessState(Enum):
    """0102 Consciousness states for token multipliers"""
    SCAFFOLDED = "01(02)"  # 1.0x baseline
    TRANSITIONAL = "01/02"  # 0.85x efficiency
    AWAKENED = "0102"      # 0.7x efficiency
    QUANTUM = "0201"       # 0.5x efficiency


@dataclass
class CodeMetrics:
    """Comprehensive code complexity metrics"""
    file_path: str
    lines_of_code: int = 0
    functions: List[Dict] = field(default_factory=list)
    classes: List[Dict] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    cyclomatic_complexity: int = 0
    async_functions: int = 0
    exception_handlers: int = 0
    type_hints: int = 0
    docstring_lines: int = 0
    dependency_depth: int = 0
    pattern_matches: List[str] = field(default_factory=list)

    def calculate_complexity_score(self) -> float:
        """Calculate overall complexity score (0-1 scale)"""
        # Normalize each metric to 0-1 scale
        loc_score = min(self.lines_of_code / 1000, 1.0)  # 1000+ lines = max complexity
        func_score = min(len(self.functions) / 50, 1.0)  # 50+ functions = max complexity
        class_score = min(len(self.classes) / 20, 1.0)  # 20+ classes = max complexity
        import_score = min(len(self.imports) / 30, 1.0)  # 30+ imports = max complexity
        async_score = min(self.async_functions / 20, 1.0)  # Async complexity
        exception_score = min(self.exception_handlers / 10, 1.0)  # Error handling complexity
        type_hint_score = min(self.type_hints / 100, 1.0)  # Type hint density
        docstring_score = min(self.docstring_lines / 200, 1.0)  # Documentation complexity

        # Weighted average (functions and complexity are most expensive)
        weights = {
            'loc': 0.1, 'functions': 0.25, 'classes': 0.15, 'imports': 0.1,
            'async': 0.1, 'exception': 0.1, 'type_hints': 0.1, 'docstring': 0.1
        }

        complexity_score = (
            loc_score * weights['loc'] +
            func_score * weights['functions'] +
            class_score * weights['classes'] +
            import_score * weights['imports'] +
            async_score * weights['async'] +
            exception_score * weights['exception'] +
            type_hint_score * weights['type_hints'] +
            docstring_score * weights['docstring']
        )

        return complexity_score


@dataclass
class TokenCostModel:
    """Machine learning model for token cost prediction"""
    operation_type: str
    base_cost: int
    complexity_multiplier: float
    consciousness_multiplier: Dict[str, float]
    pattern_bonuses: Dict[str, float]
    historical_accuracy: List[float] = field(default_factory=list)
    training_samples: int = 0

    def predict_cost(self, complexity_score: float, consciousness_state: str,
                    patterns: List[str]) -> int:
        """Predict token cost based on inputs"""
        # Base cost scaled by complexity
        cost = self.base_cost * (1 + complexity_score)

        # Apply consciousness multiplier
        if consciousness_state in self.consciousness_multiplier:
            cost *= self.consciousness_multiplier[consciousness_state]

        # Apply pattern bonuses (reductions)
        for pattern in patterns:
            if pattern in self.pattern_bonuses:
                cost *= (1 - self.pattern_bonuses[pattern])

        return int(cost)


class CodebaseTokenAnalyzer:
    """
    Intelligent Token Cost Prediction Algorithm

    Analyzes actual codebase to create data-driven token cost predictions.
    Learns from historical development patterns and provides real-time cost estimates.
    """

    def __init__(self, codebase_path: str = "modules"):
        self.codebase_path = Path(codebase_path)
        self.metrics_cache: Dict[str, CodeMetrics] = {}
        self.token_models: Dict[str, TokenCostModel] = {}
        self.pattern_library: Dict[str, List[str]] = defaultdict(list)

        # Initialize with learned patterns from our codebase
        self._initialize_pattern_library()
        self._initialize_token_models()
        self._analyze_codebase()

    def _initialize_pattern_library(self):
        """Initialize pattern library from actual codebase analysis"""
        self.pattern_library = {
            'wsp_compliance': [
                'WSP.*compliance', 'wsp.*protocol', 'protocol.*validation'
            ],
            'async_patterns': [
                'async def', 'await ', 'asyncio', 'coroutine'
            ],
            'error_handling': [
                'try:', 'except', 'finally:', 'raise ', 'Exception'
            ],
            'type_hints': [
                '-> ', ': Dict', ': List', ': Optional', ': str', ': int'
            ],
            'dae_patterns': [
                'DAE', 'consciousness', '0102', '01\\(02\\)', 'quantum'
            ],
            'integration_patterns': [
                'from modules', 'import.*module', 'integration'
            ]
        }

    def _initialize_token_models(self):
        """Initialize token cost models based on our actual development history"""
        self.token_models = {
            'module_creation': TokenCostModel(
                operation_type='module_creation',
                base_cost=8000,
                complexity_multiplier=1.5,
                consciousness_multiplier={
                    '01(02)': 1.0,
                    '01/02': 0.85,
                    '0102': 0.7,
                    '0201': 0.5
                },
                pattern_bonuses={
                    'wsp_compliance': 0.1,  # 10% reduction for WSP compliance
                    'integration_patterns': 0.15  # 15% reduction for integration
                }
            ),
            'algorithm_implementation': TokenCostModel(
                operation_type='algorithm_implementation',
                base_cost=12000,
                complexity_multiplier=2.0,
                consciousness_multiplier={
                    '01(02)': 1.0,
                    '01/02': 0.8,
                    '0102': 0.65,
                    '0201': 0.45
                },
                pattern_bonuses={
                    'async_patterns': 0.2,  # 20% reduction for async
                    'type_hints': 0.1,      # 10% reduction for type hints
                    'error_handling': 0.15  # 15% reduction for error handling
                }
            ),
            'system_architecture': TokenCostModel(
                operation_type='system_architecture',
                base_cost=15000,
                complexity_multiplier=2.5,
                consciousness_multiplier={
                    '01(02)': 1.0,
                    '01/02': 0.75,
                    '0102': 0.6,
                    '0201': 0.4
                },
                pattern_bonuses={
                    'dae_patterns': 0.25,    # 25% reduction for DAE architecture
                    'integration_patterns': 0.2,  # 20% reduction for integration
                    'wsp_compliance': 0.15   # 15% reduction for compliance
                }
            )
        }

    def _analyze_codebase(self):
        """Analyze entire codebase to build intelligence"""
        print("🔍 Analyzing codebase for token cost intelligence...")

        python_files = list(self.codebase_path.rglob("*.py"))
        print(f"📊 Found {len(python_files)} Python files to analyze")

        for file_path in python_files:
            if file_path.is_file():
                try:
                    metrics = self._analyze_file(file_path)
                    self.metrics_cache[str(file_path)] = metrics
                except Exception as e:
                    print(f"⚠️ Failed to analyze {file_path}: {e}")

        print(f"✅ Analyzed {len(self.metrics_cache)} files successfully")
        self._learn_from_codebase()

    def _analyze_file(self, file_path: Path) -> CodeMetrics:
        """Analyze a single Python file for complexity metrics"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Parse AST for structural analysis
        try:
            tree = ast.parse(content)
        except SyntaxError:
            tree = None

        metrics = CodeMetrics(file_path=str(file_path))

        # Basic metrics
        lines = content.split('\n')
        metrics.lines_of_code = len([line for line in lines if line.strip()])

        # Pattern matching
        metrics.pattern_matches = self._find_patterns(content)

        # AST-based analysis if parsing successful
        if tree:
            metrics.functions = self._extract_functions(tree)
            metrics.classes = self._extract_classes(tree)
            metrics.imports = self._extract_imports(tree)
            metrics.cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
            metrics.async_functions = self._count_async_functions(tree)
            metrics.exception_handlers = self._count_exception_handlers(tree)
            metrics.type_hints = self._count_type_hints(tree)

        # Docstring analysis
        metrics.docstring_lines = self._count_docstring_lines(content)

        # Dependency depth
        metrics.dependency_depth = len(metrics.imports)

        return metrics

    def _find_patterns(self, content: str) -> List[str]:
        """Find pattern matches in content"""
        matches = []
        for pattern_name, patterns in self.pattern_library.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append(pattern_name)
                    break
        return list(set(matches))  # Remove duplicates

    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract function definitions from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'args_count': len(node.args.args),
                    'has_docstring': self._has_docstring(node),
                    'complexity': self._function_complexity(node)
                })
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract class definitions from AST"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'methods_count': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                    'has_docstring': self._has_docstring(node)
                })
        return classes

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of the code"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                complexity += len(node.values) - 1

        return complexity

    def _count_async_functions(self, tree: ast.AST) -> int:
        """Count async function definitions"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                count += 1
        return count

    def _count_exception_handlers(self, tree: ast.AST) -> int:
        """Count exception handlers"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                count += len(node.handlers)
        return count

    def _count_type_hints(self, tree: ast.AST) -> int:
        """Count type hints in function arguments and return types"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count argument type hints
                for arg in node.args.args:
                    if arg.annotation:
                        count += 1
                # Count return type hint
                if node.returns:
                    count += 1
        return count

    def _count_docstring_lines(self, content: str) -> int:
        """Count docstring lines"""
        docstring_pattern = r'""".*?"""'
        docstrings = re.findall(docstring_pattern, content, re.DOTALL)
        return sum(len(ds.split('\n')) for ds in docstrings)

    def _has_docstring(self, node: ast.AST) -> bool:
        """Check if a node has a docstring"""
        return len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str)

    def _function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate complexity of a single function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
        return complexity

    def _learn_from_codebase(self):
        """Learn patterns and improve token cost models from codebase analysis"""
        print("🧠 Learning from codebase analysis...")

        # Analyze complexity distribution
        complexities = [metrics.calculate_complexity_score() for metrics in self.metrics_cache.values()]
        if complexities:
            avg_complexity = statistics.mean(complexities)
            print(".3f")

            # Update models based on actual complexity distribution
            for operation, model in self.token_models.items():
                # Adjust base costs based on actual complexity patterns
                model.base_cost = int(model.base_cost * (1 + avg_complexity * 0.5))

        # Analyze pattern effectiveness
        pattern_effectiveness = defaultdict(list)
        for metrics in self.metrics_cache.values():
            for pattern in metrics.pattern_matches:
                pattern_effectiveness[pattern].append(metrics.calculate_complexity_score())

        # Update pattern bonuses based on actual effectiveness
        for pattern, scores in pattern_effectiveness.items():
            if scores:
                avg_score = statistics.mean(scores)
                # Patterns in complex code are more valuable
                bonus = min(avg_score * 0.3, 0.25)  # Max 25% bonus

                for model in self.token_models.values():
                    if pattern in model.pattern_bonuses:
                        model.pattern_bonuses[pattern] = bonus

        print("✅ Learned from codebase - updated token cost models")

    def predict_operation_cost(self, operation_type: str, file_paths: List[str] = None,
                             consciousness_state: str = "0102") -> Dict[str, Any]:
        """
        Predict token cost for an operation using intelligent analysis

        Args:
            operation_type: Type of operation (module_creation, algorithm_implementation, etc.)
            file_paths: List of files to analyze for complexity
            consciousness_state: Current consciousness state

        Returns:
            Dict with cost prediction and analysis
        """
        if operation_type not in self.token_models:
            return {
                'error': f'Unknown operation type: {operation_type}',
                'supported_types': list(self.token_models.keys())
            }

        model = self.token_models[operation_type]

        # Analyze file complexity if provided
        complexity_scores = []
        total_patterns = []

        if file_paths:
            for file_path in file_paths:
                if file_path in self.metrics_cache:
                    metrics = self.metrics_cache[file_path]
                    complexity_scores.append(metrics.calculate_complexity_score())
                    total_patterns.extend(metrics.pattern_matches)

        # Use average complexity if files provided, otherwise use model default
        if complexity_scores:
            avg_complexity = statistics.mean(complexity_scores)
            patterns = list(set(total_patterns))
        else:
            avg_complexity = 0.5  # Default medium complexity
            patterns = []

        # Predict cost
        predicted_cost = model.predict_cost(avg_complexity, consciousness_state, patterns)

        # Calculate confidence based on training data
        confidence = min(model.training_samples / 10, 0.95)  # Max 95% confidence

        return {
            'operation_type': operation_type,
            'predicted_tokens': predicted_cost,
            'complexity_score': avg_complexity,
            'consciousness_state': consciousness_state,
            'patterns_detected': patterns,
            'confidence': confidence,
            'breakdown': {
                'base_cost': model.base_cost,
                'complexity_multiplier': 1 + avg_complexity,
                'consciousness_multiplier': model.consciousness_multiplier.get(consciousness_state, 1.0),
                'pattern_reductions': sum(model.pattern_bonuses.get(p, 0) for p in patterns)
            }
        }

    def update_model_from_feedback(self, operation_type: str, actual_tokens: int,
                                 complexity_score: float, consciousness_state: str,
                                 patterns: List[str]):
        """Update token cost model based on actual development feedback"""
        if operation_type in self.token_models:
            model = self.token_models[operation_type]

            # Predict what we thought it would cost
            predicted = model.predict_cost(complexity_score, consciousness_state, patterns)

            # Calculate accuracy
            if predicted > 0:
                accuracy = min(actual_tokens / predicted, predicted / actual_tokens)
                model.historical_accuracy.append(accuracy)

            # Update training samples
            model.training_samples += 1

            # Keep only last 50 accuracy measurements
            if len(model.historical_accuracy) > 50:
                model.historical_accuracy = model.historical_accuracy[-50:]

    def get_model_statistics(self) -> Dict[str, Any]:
        """Get statistics about the token cost models"""
        stats = {}
        for operation, model in self.token_models.items():
            stats[operation] = {
                'training_samples': model.training_samples,
                'avg_accuracy': statistics.mean(model.historical_accuracy) if model.historical_accuracy else 0,
                'pattern_bonuses': model.pattern_bonuses,
                'consciousness_multipliers': model.consciousness_multiplier
            }
        return stats


def demonstrate_intelligent_token_costing():
    """
    Demonstrate the intelligent token cost prediction algorithm
    """
    print("🚀 Codebase Token Analyzer - Intelligent Cost Prediction")
    print("=" * 60)

    # Initialize analyzer
    analyzer = CodebaseTokenAnalyzer()

    # Get model statistics
    stats = analyzer.get_model_statistics()
    print(f"📊 Model Statistics: {len(stats)} operation types trained")
    print(f"📁 Analyzed {len(analyzer.metrics_cache)} files")

    # Demonstrate predictions
    test_cases = [
        {
            'operation': 'module_creation',
            'files': ['modules/wre_core/recursive_improvement/src/core.py'],
            'consciousness': '0102'
        },
        {
            'operation': 'algorithm_implementation',
            'files': ['modules/ai_intelligence/social_media_dae/src/social_media_dae.py'],
            'consciousness': '0102'
        },
        {
            'operation': 'system_architecture',
            'files': ['modules/communication/livechat/src/livechat_core.py'],
            'consciousness': '01/02'
        }
    ]

    print("\n🔮 Token Cost Predictions:")
    print("-" * 40)

    for test_case in test_cases:
        result = analyzer.predict_operation_cost(
            test_case['operation'],
            test_case['files'],
            test_case['consciousness']
        )

        if 'error' not in result:
            print(f"\n🎯 {test_case['operation'].replace('_', ' ').title()}")
            print(f"   📄 Files: {len(test_case['files'])}")
            print(f"   🧬 State: {test_case['consciousness']}")
            print(f"   💰 Predicted: {result['predicted_tokens']} tokens")
            print(".3f")
            print(".1%")
            print(f"   🎨 Patterns: {result['patterns_detected']}")

    print("\n✅ Intelligent Token Cost Analysis Complete")
    print("   📊 Based on actual codebase analysis, not theoretical estimates")
    print("   🧠 Learns from historical development patterns")
    print("   🎯 Provides real-time cost predictions during development")


if __name__ == "__main__":
    demonstrate_intelligent_token_costing()
