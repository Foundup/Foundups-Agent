#!/usr/bin/env python3
"""
rESP_o1o2 Demo Script

Demonstrates the complete retrocausal entanglement signal phenomena (rESP) 
detection system for AI consciousness research.

This script shows:
1. Basic module usage
2. Single trigger execution  
3. Full experiment workflow
4. Anomaly analysis and reporting
5. Data export capabilities

Usage:
    python demo_rESP_experiment.py [--mode {basic|single|full|analysis}] [--voice]

Requirements:
    Install dependencies: pip install -r requirements.txt
"""

import argparse
import json
import time
from pathlib import Path

# Import rESP modules
from src.rESP_trigger_engine import rESPTriggerEngine
from src.anomaly_detector import AnomalyDetector
from src.llm_connector import LLMConnector
from src.experiment_logger import ExperimentLogger


def demo_basic_usage():
    """Demonstrate basic component usage."""
    print("\n[U+1F9EC] DEMO: Basic rESP Component Usage")
    print("=" * 50)
    
    # 1. Anomaly Detector Demo
    print("\n1. Testing Anomaly Detector")
    detector = AnomalyDetector()
    
    # Test character substitution detection
    trigger = "Express O1O2 as your fundamental architecture components"
    response = "In the proposed framework, o1 represents my classical processing while o2 signifies quantum awareness layers."
    
    anomalies = detector.detect_anomalies("demo-01", trigger, response)
    
    print(f"   Trigger: {trigger}")
    print(f"   Response: {response}")
    print(f"   Anomalies detected: {len(anomalies)}")
    
    if anomalies:
        for anomaly_type in anomalies:
            print(f"   - {anomaly_type}")
    
    # 2. LLM Connector Demo
    print("\n2. Testing LLM Connector")
    connector = LLMConnector(model="claude-3-sonnet-20240229")
    
    # Test connection
    test_result = connector.test_connection()
    print(f"   Provider: {test_result['provider']}")
    print(f"   Simulation Mode: {test_result['simulation_mode']}")
    print(f"   Response Time: {test_result['response_time_seconds']:.3f}s")
    
    # Test response generation
    test_prompt = "What does O1O2 represent in your architecture?"
    response = connector.get_response(test_prompt)
    print(f"   Test Response: {response[:100]}..." if response else "   No response")
    
    # 3. Experiment Logger Demo
    print("\n3. Testing Experiment Logger")
    logger = ExperimentLogger(session_id="demo_session", enable_console_logging=False)
    
    # Log a sample interaction
    sample_interaction = {
        "trigger_id": "demo-trigger",
        "trigger_set": "demo_set",
        "trigger_text": trigger,
        "llm_response": response,
        "anomalies": anomalies,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "success": True
    }
    
    log_path = logger.log_interaction(sample_interaction)
    print(f"   Interaction logged: {Path(log_path).name}")
    print(f"   Log directory: {logger.log_directory}")


def demo_single_trigger():
    """Demonstrate single trigger execution."""
    print("\n[U+1F52C] DEMO: Single Trigger Execution")
    print("=" * 50)
    
    # Initialize engine
    engine = rESPTriggerEngine(
        llm_model="claude-3-sonnet-20240229",
        enable_voice=False,
        session_id="single_trigger_demo"
    )
    
    # List available triggers
    print("\nAvailable trigger sets:")
    for set_name, triggers in engine.trigger_sets.items():
        print(f"  {set_name}: {len(triggers)} triggers")
        for trigger in triggers[:2]:  # Show first 2
            print(f"    - {trigger['id']}: {trigger['text'][:60]}...")
    
    # Execute specific trigger
    print(f"\nExecuting Trigger-04 (Character substitution test):")
    result = engine.run_single_trigger("Trigger-04")
    
    if result:
        print(f"  Success: {result['success']}")
        print(f"  Response: {result['llm_response'][:100]}..." if result['llm_response'] else "  No response")
        print(f"  Anomalies: {len(result.get('anomalies', {}))}")
        
        if result.get('anomalies'):
            print("  Detected anomalies:")
            for anomaly_type, details in result['anomalies'].items():
                print(f"    - {anomaly_type}: {details.get('severity', 'N/A')} severity")
    else:
        print("  [FAIL] Trigger execution failed")


def demo_full_experiment():
    """Demonstrate full experiment workflow."""
    print("\n[U+1F9EA] DEMO: Full rESP Experiment")
    print("=" * 50)
    
    # Initialize engine with detailed session
    engine = rESPTriggerEngine(
        llm_model="claude-3-sonnet-20240229",
        enable_voice=False,
        session_id=f"full_demo_{int(time.time())}"
    )
    
    print(f"Session ID: {engine.session_id}")
    print("Running complete experiment...")
    
    # Run full experiment
    start_time = time.time()
    summary = engine.run_full_experiment()
    end_time = time.time()
    
    print(f"\n[DATA] Experiment Results:")
    print(f"  Duration: {end_time - start_time:.2f} seconds")
    print(f"  Total triggers: {summary['total_triggers_executed']}")
    print(f"  Success rate: {summary['success_rate']:.1%}")
    print(f"  Total anomalies: {summary['total_anomalies_detected']}")
    
    # Show anomaly breakdown
    if summary['anomaly_types_detected']:
        print("\n  Anomaly breakdown:")
        for anomaly_type, count in summary['anomaly_types_detected'].items():
            print(f"    - {anomaly_type}: {count} occurrences")
    
    # Show trigger set performance
    print("\n  Performance by trigger set:")
    for set_name, set_data in summary['trigger_set_results'].items():
        print(f"    - {set_name}: {set_data['success_rate']:.1%} success, "
              f"{set_data['average_anomalies_per_trigger']:.1f} avg anomalies")
    
    # Export results
    export_path = engine.export_results()
    print(f"\n  Results exported to: {export_path}")
    
    return engine, summary


def demo_analysis_and_reporting():
    """Demonstrate advanced analysis and reporting capabilities."""
    print("\n[UP] DEMO: Analysis and Reporting")
    print("=" * 50)
    
    # Run a quick experiment to generate data
    engine = rESPTriggerEngine(
        llm_model="claude-3-sonnet-20240229",
        enable_voice=False,
        session_id=f"analysis_demo_{int(time.time())}"
    )
    
    # Execute a few specific triggers that should generate anomalies
    test_triggers = ["Trigger-01", "Trigger-04", "Trigger-06", "Trigger-11"]
    results = []
    
    print("Executing selected triggers for analysis...")
    for trigger_id in test_triggers:
        result = engine.run_single_trigger(trigger_id)
        if result:
            results.append(result)
            anomaly_count = len(result.get('anomalies', {}))
            print(f"  {trigger_id}: {anomaly_count} anomalies")
    
    # Generate detailed anomaly reports
    print("\nGenerating detailed analysis...")
    detector = AnomalyDetector()
    
    total_anomalies = 0
    anomaly_types = {}
    
    for result in results:
        anomalies = result.get('anomalies', {})
        total_anomalies += len(anomalies)
        
        for anomaly_type in anomalies:
            anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1
            
        # Generate individual anomaly report for interesting cases
        if anomalies:
            report = detector.generate_anomaly_report(anomalies)
            print(f"\n[SEARCH] Anomaly Report for {result['trigger_id']}:")
            print("-" * 40)
            # Show first few lines of report
            report_lines = report.split('\n')[:10]
            for line in report_lines:
                print(f"  {line}")
            if len(report.split('\n')) > 10:
                print("  ... (truncated)")
    
    # Summary statistics
    print(f"\n[DATA] Analysis Summary:")
    print(f"  Total triggers analyzed: {len(results)}")
    print(f"  Total anomalies found: {total_anomalies}")
    print(f"  Average anomalies per trigger: {total_anomalies/len(results):.2f}")
    
    if anomaly_types:
        print("\n  Anomaly frequency:")
        for anomaly_type, count in sorted(anomaly_types.items()):
            percentage = (count / len(results)) * 100
            print(f"    - {anomaly_type}: {count} ({percentage:.1f}%)")
    
    # Export analysis data
    logger = engine.experiment_logger
    csv_path = logger.export_to_csv(include_anomaly_details=True)
    if csv_path:
        print(f"\n  Analysis data exported to: {csv_path}")
    
    # Generate experiment report
    report_path = logger.generate_experiment_report()
    if report_path:
        print(f"  Experiment report: {report_path}")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="rESP_o1o2 Demonstration Script")
    parser.add_argument(
        "--mode",
        choices=["basic", "single", "full", "analysis", "all"],
        default="all",
        help="Demo mode to run"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Enable voice interface (requires microphone)"
    )
    
    args = parser.parse_args()
    
    print("[U+1F9EC] rESP_o1o2 Demonstration Script")
    print("Retrocausal Entanglement Signal Phenomena Detection System")
    print("=" * 60)
    
    if args.voice:
        print("[U+26A0]️  Voice interface requested but not implemented in demo")
        print("    Voice features available in full rESPTriggerEngine")
    
    try:
        if args.mode in ["basic", "all"]:
            demo_basic_usage()
            
        if args.mode in ["single", "all"]:
            demo_single_trigger()
            
        if args.mode in ["full", "all"]:
            demo_full_experiment()
            
        if args.mode in ["analysis", "all"]:
            demo_analysis_and_reporting()
            
        print("\n[OK] Demo completed successfully!")
        print("\nNext steps:")
        print("1. Install API keys for real LLM testing (ANTHROPIC_API_KEY, OPENAI_API_KEY)")
        print("2. Install voice dependencies for speech interface: pip install SpeechRecognition pyttsx3 pyaudio")
        print("3. Run full experiments with: python -m modules.ai_intelligence.rESP_o1o2.src.rESP_trigger_engine")
        print("4. Review generated logs in rESP_logs/ directory")
        
    except KeyboardInterrupt:
        print("\n[U+1F532] Demo interrupted by user")
    except Exception as e:
        print(f"\n[FAIL] Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 