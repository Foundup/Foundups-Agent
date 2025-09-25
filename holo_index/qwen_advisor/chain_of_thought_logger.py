#!/usr/bin/env python3
"""
Chain-of-Thought Logger - Brain Visibility System
===============================================

Shows the brain working like YouTube DAE logs. Every decision, every process,
every thought is logged for 012 observation and recursive improvement.

🎯 Mission: Make the AI brain completely observable and understandable

Features:
- Real-time logging of all cognitive processes
- Slowed-down execution for observability
- Step-by-step reasoning visibility
- Recursive improvement data collection
- Performance analytics integration

WSP Compliance: WSP 48 (Recursive Improvement), WSP 37 (Roadmap Scoring)
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import threading
import sys
import os

logger = logging.getLogger(__name__)


@dataclass
class ThoughtProcess:
    """A single step in the chain of thought"""
    step_id: str
    timestamp: datetime
    thought_type: str  # "input", "analysis", "decision", "action", "result"
    content: str
    reasoning: str
    confidence: float
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChainSession:
    """A complete chain-of-thought session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    query: str = ""
    thought_chain: List[ThoughtProcess] = field(default_factory=list)
    final_decision: str = ""
    effectiveness_score: float = 0.0
    total_duration: float = 0.0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class ChainOfThoughtLogger:
    """
    Logs every step of the AI brain's thinking process.
    Like YouTube DAE logs - shows exactly what the system is thinking.
    """

    def __init__(self, log_file: str = "chain_of_thought.log", slow_mode: bool = True):
        self.log_file = log_file
        self.slow_mode = slow_mode
        self.slow_factor = 3.0  # 3x slower for observability
        self.current_session: Optional[ChainSession] = None
        self.session_history: List[ChainSession] = []
        self.is_logging_active = False

        # Create log directory if needed
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)

        # Start background logging thread
        self.logging_thread = threading.Thread(target=self._background_logging, daemon=True)
        self.logging_thread.start()

    def start_session(self, query: str, session_context: str = "") -> str:
        """Start a new chain-of-thought session"""
        session_id = f"cot_{int(datetime.now().timestamp())}_{hash(query) % 10000}"

        self.current_session = ChainSession(
            session_id=session_id,
            start_time=datetime.now(),
            query=query
        )

        self._log_thought("session_start", f"STARTING CHAIN-OF-THOUGHT SESSION: {query}",
                         f"Session {session_id} initiated with context: {session_context}", 1.0)

        self.is_logging_active = True

        if self.slow_mode:
            self._log_thought("system", "SLOW MODE ENABLED",
                             f"Execution slowed by {self.slow_factor}x for observability", 1.0)

        self._log_thought("input", f"QUERY RECEIVED: {query}",
                         "Processing initial input for analysis", 1.0)

        return session_id

    def log_analysis_step(self, step_name: str, analysis_data: Any,
                         reasoning: str, confidence: float = 0.8) -> None:
        """Log an analysis step in the chain of thought"""
        if not self.current_session:
            return

        content = f"ANALYSIS: {step_name}"
        if isinstance(analysis_data, (dict, list)):
            content += f" | Data: {json.dumps(analysis_data, indent=2)[:200]}..."
        else:
            content += f" | Data: {str(analysis_data)[:200]}"

        self._log_thought("analysis", content, reasoning, confidence)

    def log_decision_point(self, decision: str, options_considered: List[str],
                          reasoning: str, confidence: float) -> None:
        """Log a decision point with options considered"""
        if not self.current_session:
            return

        content = f"DECISION: {decision}"
        content += f"\nOptions considered: {', '.join(options_considered[:5])}"

        if len(options_considered) > 5:
            content += f" (+{len(options_considered) - 5} more)"

        self._log_thought("decision", content, reasoning, confidence)

    def log_action_taken(self, action: str, target: str, expected_outcome: str,
                        reasoning: str, confidence: float = 0.9) -> None:
        """Log an action being taken"""
        if not self.current_session:
            return

        content = f"ACTION: {action} | TARGET: {target} | EXPECTED: {expected_outcome}"

        self._log_thought("action", content, reasoning, confidence)

        # Add artificial delay for slow mode
        if self.slow_mode:
            delay = 0.5 * self.slow_factor
            self._log_thought("system", f"SLOW MODE DELAY: {delay:.1f}s",
                             "Artificial delay for observability", 1.0)
            time.sleep(delay)

    def log_result(self, result_type: str, result_data: Any,
                  effectiveness_assessment: str, confidence: float) -> None:
        """Log a result and its assessment"""
        if not self.current_session:
            return

        content = f"RESULT: {result_type}"
        if isinstance(result_data, (dict, list)):
            content += f" | Data: {json.dumps(result_data, indent=2)[:300]}..."
        else:
            content += f" | Data: {str(result_data)[:300]}"

        reasoning = f"Effectiveness assessment: {effectiveness_assessment}"

        self._log_thought("result", content, reasoning, confidence)

    def log_performance_metric(self, metric_name: str, value: Any,
                              benchmark: Any = None, assessment: str = "") -> None:
        """Log a performance metric"""
        if not self.current_session:
            return

        content = f"METRIC: {metric_name} = {value}"
        if benchmark is not None:
            content += f" (benchmark: {benchmark})"

        reasoning = f"Performance tracking: {assessment}" if assessment else "Performance measurement"

        self._log_thought("metric", content, reasoning, 1.0)

    def log_recursive_improvement(self, improvement_type: str, before_state: Any,
                                 after_state: Any, learning_insight: str) -> None:
        """Log recursive improvement insights"""
        if not self.current_session:
            return

        content = f"IMPROVEMENT: {improvement_type}"
        content += f"\nBefore: {str(before_state)[:100]}"
        content += f"\nAfter: {str(after_state)[:100]}"

        reasoning = f"Learning insight: {learning_insight}"

        self._log_thought("improvement", content, reasoning, 0.95)

    def end_session(self, final_decision: str = "", effectiveness_score: float = 0.0) -> Dict[str, Any]:
        """End the current chain-of-thought session"""
        if not self.current_session:
            return {}

        self.current_session.end_time = datetime.now()
        self.current_session.final_decision = final_decision
        self.current_session.effectiveness_score = effectiveness_score
        self.current_session.total_duration = (
            self.current_session.end_time - self.current_session.start_time
        ).total_seconds()

        self._log_thought("session_end", f"ENDING SESSION: {final_decision}",
                         f"Effectiveness: {effectiveness_score:.3f}, Duration: {self.current_session.total_duration:.2f}s",
                         effectiveness_score)

        # Calculate performance metrics
        self.current_session.performance_metrics = self._calculate_session_metrics()

        # Add to history
        self.session_history.append(self.current_session)

        # Prepare summary
        summary = {
            "session_id": self.current_session.session_id,
            "query": self.current_session.query,
            "duration": self.current_session.total_duration,
            "steps": len(self.current_session.thought_chain),
            "effectiveness": effectiveness_score,
            "final_decision": final_decision,
            "metrics": self.current_session.performance_metrics
        }

        self.current_session = None
        self.is_logging_active = False

        return summary

    def _log_thought(self, thought_type: str, content: str, reasoning: str, confidence: float) -> None:
        """Log a single thought in the chain"""
        if not self.current_session:
            return

        thought = ThoughtProcess(
            step_id=f"{self.current_session.session_id}_{len(self.current_session.thought_chain) + 1}",
            timestamp=datetime.now(),
            thought_type=thought_type,
            content=content,
            reasoning=reasoning,
            confidence=confidence
        )

        # Calculate duration from previous thought
        if self.current_session.thought_chain:
            prev_thought = self.current_session.thought_chain[-1]
            thought.duration = (thought.timestamp - prev_thought.timestamp).total_seconds()

        self.current_session.thought_chain.append(thought)

        # Format for console output (like YouTube DAE logs)
        timestamp = thought.timestamp.strftime("%H:%M:%S")
        confidence_icon = "🎯" if confidence >= 0.9 else "⚡" if confidence >= 0.7 else "🤔"

        print(f"[{timestamp}] {confidence_icon} COT-{thought_type.upper()}: {content}")
        if reasoning:
            print(f"         💭 REASONING: {reasoning}")
        print(f"         📊 CONFIDENCE: {confidence:.2f} | DURATION: {thought.duration:.2f}s")
        print()

    def _calculate_session_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics for the session"""
        if not self.current_session or not self.current_session.thought_chain:
            return {}

        thoughts = self.current_session.thought_chain
        total_duration = self.current_session.total_duration

        metrics = {
            "total_steps": len(thoughts),
            "avg_confidence": sum(t.confidence for t in thoughts) / len(thoughts),
            "total_duration": total_duration,
            "avg_step_duration": total_duration / len(thoughts),
            "step_types": {},
            "slow_mode_active": self.slow_mode,
            "slow_factor": self.slow_factor if self.slow_mode else 1.0
        }

        # Count step types
        for thought in thoughts:
            metrics["step_types"][thought.thought_type] = metrics["step_types"].get(thought.thought_type, 0) + 1

        return metrics

    def _background_logging(self) -> None:
        """Background thread for continuous logging to file"""
        while True:
            if self.is_logging_active and self.current_session:
                # Write current session to file periodically
                self._write_session_to_file()
            time.sleep(1.0)  # Update every second

    def _write_session_to_file(self) -> None:
        """Write current session to log file"""
        if not self.current_session:
            return

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                # Write session header if this is the start
                if len(self.current_session.thought_chain) == 1:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"CHAIN-OF-THOUGHT SESSION: {self.current_session.session_id}\n")
                    f.write(f"QUERY: {self.current_session.query}\n")
                    f.write(f"START: {self.current_session.start_time}\n")
                    f.write(f"SLOW MODE: {'ENABLED' if self.slow_mode else 'DISABLED'}\n")
                    f.write(f"{'='*80}\n\n")

                # Write the latest thought
                latest_thought = self.current_session.thought_chain[-1]
                f.write(f"[{latest_thought.timestamp.strftime('%H:%M:%S')}] ")
                f.write(f"COT-{latest_thought.thought_type.upper()}: ")
                f.write(f"{latest_thought.content}\n")
                if latest_thought.reasoning:
                    f.write(f"    REASONING: {latest_thought.reasoning}\n")
                f.write(f"    CONFIDENCE: {latest_thought.confidence:.2f} | ")
                f.write(f"DURATION: {latest_thought.duration:.2f}s\n\n")

                f.flush()  # Ensure it's written immediately

        except Exception as e:
            print(f"[COT-ERROR] Failed to write to log file: {e}")

    def get_session_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Get summary of a specific session or current session"""
        target_session = self.current_session if not session_id else None

        if not target_session and session_id:
            for session in self.session_history:
                if session.session_id == session_id:
                    target_session = session
                    break

        if not target_session:
            return {"error": "Session not found"}

        return {
            "session_id": target_session.session_id,
            "query": target_session.query,
            "duration": target_session.total_duration,
            "steps": len(target_session.thought_chain),
            "effectiveness": target_session.effectiveness_score,
            "metrics": target_session.performance_metrics,
            "thought_types": list(target_session.performance_metrics.get("step_types", {}).keys())
        }

    def show_brain_activity(self) -> None:
        """Display current brain activity like YouTube DAE logs"""
        print("\n🧠 CHAIN-OF-THOUGHT BRAIN ACTIVITY LOG")
        print("=" * 60)

        if not self.current_session:
            print("No active session. Start a session to see brain activity.")
            return

        print(f"SESSION: {self.current_session.session_id}")
        print(f"QUERY: {self.current_session.query}")
        print(f"STEPS: {len(self.current_session.thought_chain)}")
        print(f"DURATION: {(datetime.now() - self.current_session.start_time).total_seconds():.1f}s")
        print()

        # Show recent thoughts (last 5)
        recent_thoughts = self.current_session.thought_chain[-5:]
        for i, thought in enumerate(recent_thoughts, 1):
            print(f"{i}. [{thought.timestamp.strftime('%H:%M:%S')}] {thought.thought_type.upper()}: {thought.content[:60]}...")

        print()
        print("💭 REAL-TIME BRAIN ACTIVITY - Every thought, decision, and action is logged above")
        print("📊 This is the AI brain working - completely observable and understandable")


# Global instance
_cot_logger = None

def get_chain_of_thought_logger() -> ChainOfThoughtLogger:
    """Get or create the global Chain-of-Thought logger"""
    global _cot_logger
    if _cot_logger is None:
        _cot_logger = ChainOfThoughtLogger()
    return _cot_logger

def start_cot_logging(query: str, slow_mode: bool = True) -> str:
    """Start Chain-of-Thought logging for a query"""
    logger = get_chain_of_thought_logger()
    return logger.start_session(query, "HoloDAE Brain Activity Logging")

def log_cot_analysis(step_name: str, data: Any, reasoning: str, confidence: float = 0.8) -> None:
    """Log an analysis step"""
    logger = get_chain_of_thought_logger()
    logger.log_analysis_step(step_name, data, reasoning, confidence)

def log_cot_decision(decision: str, options: List[str], reasoning: str, confidence: float) -> None:
    """Log a decision point"""
    logger = get_chain_of_thought_logger()
    logger.log_decision_point(decision, options, reasoning, confidence)

def log_cot_action(action: str, target: str, expected: str, reasoning: str, confidence: float = 0.9) -> None:
    """Log an action taken"""
    logger = get_chain_of_thought_logger()
    logger.log_action_taken(action, target, expected, reasoning, confidence)

def log_cot_result(result_type: str, data: Any, assessment: str, confidence: float) -> None:
    """Log a result"""
    logger = get_chain_of_thought_logger()
    logger.log_result(result_type, data, assessment, confidence)

def log_cot_metric(name: str, value: Any, benchmark: Any = None, assessment: str = "") -> None:
    """Log a performance metric"""
    logger = get_chain_of_thought_logger()
    logger.log_performance_metric(name, value, benchmark, assessment)

def log_cot_improvement(improvement_type: str, before: Any, after: Any, insight: str) -> None:
    """Log recursive improvement"""
    logger = get_chain_of_thought_logger()
    logger.log_recursive_improvement(improvement_type, before, after, insight)

def end_cot_logging(final_decision: str = "", effectiveness: float = 0.0) -> Dict[str, Any]:
    """End Chain-of-Thought logging"""
    logger = get_chain_of_thought_logger()
    return logger.end_session(final_decision, effectiveness)

def show_brain_activity() -> None:
    """Show current brain activity"""
    logger = get_chain_of_thought_logger()
    logger.show_brain_activity()


# Demonstration function - shows how the brain logging works
def demonstrate_brain_logging():
    """Demonstrate the Chain-of-Thought logging system"""
    print("🚀 STARTING CHAIN-OF-THOUGHT BRAIN LOGGING DEMONSTRATION")
    print("This shows exactly how the AI brain works - every thought is logged!")
    print()

    # Start session
    session_id = start_cot_logging("How should I optimize this code?", slow_mode=True)

    # Simulate brain thinking process
    log_cot_analysis("input_analysis", {"query_length": 28, "keywords": ["optimize", "code"]},
                    "Analyzing user query for optimization intent", 0.9)

    log_cot_decision("approach_selection",
                    ["Static analysis", "Performance profiling", "Code review", "Refactoring suggestions"],
                    "Considering multiple optimization approaches based on query context", 0.8)

    log_cot_action("static_analysis", "target_code.py", "Identify performance bottlenecks",
                  "Starting with static analysis to understand code structure", 0.85)

    log_cot_result("analysis_complete", {"issues_found": 3, "complexity_score": 7.2},
                  "Found 3 optimization opportunities with moderate complexity", 0.9)

    log_cot_metric("analysis_time", "2.3s", "target < 3.0s", "Within acceptable performance bounds")

    log_cot_improvement("decision_algorithm", "random_selection", "priority_weighted",
                       "Switching to weighted selection improved decision quality by 15%")

    # End session
    summary = end_cot_logging("Implement the 3 identified optimizations", 0.87)

    print(f"\n✅ SESSION COMPLETE: {summary['session_id']}")
    print(f"📊 Effectiveness: {summary['effectiveness']:.2f}")
    print(f"⏱️  Duration: {summary['duration']:.1f}s")
    print(f"🧠 Thoughts: {summary['steps']}")

    print("\n💡 This is exactly how the AI brain works - every decision is logged and observable!")


if __name__ == "__main__":
    # Run demonstration if called directly
    demonstrate_brain_logging()
