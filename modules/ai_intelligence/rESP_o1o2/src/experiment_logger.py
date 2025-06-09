"""
Experiment Logger for rESP_o1o2 Module

Comprehensive logging system for rESP trigger experiments.
Handles structured logging, file management, and report generation.
"""

import os
import json
import csv
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path


class ExperimentLogger:
    """
    Advanced logging system for rESP experiments.
    
    Features:
    - Structured JSON logging
    - Raw text file storage
    - CSV export capabilities
    - Anomaly tracking and reporting
    - Session management
    """
    
    def __init__(self, 
                 session_id: str,
                 log_directory: str = "rESP_logs",
                 enable_console_logging: bool = True):
        """
        Initialize experiment logger.
        
        Args:
            session_id: Unique session identifier
            log_directory: Directory for log files
            enable_console_logging: Enable console output
        """
        self.session_id = session_id
        self.log_directory = Path(log_directory)
        self.enable_console_logging = enable_console_logging
        
        # Create log directory structure
        self._setup_directories()
        
        # Initialize log files
        self.json_log_file = self.log_directory / f"{session_id}_interactions.jsonl"
        self.summary_log_file = self.log_directory / f"{session_id}_summary.json"
        self.csv_log_file = self.log_directory / f"{session_id}_export.csv"
        
        # Session metadata
        self.session_start_time = datetime.now()
        self.interaction_count = 0
        self.anomaly_statistics = {}
        
        # Initialize session log
        self._initialize_session()
    
    def _setup_directories(self) -> None:
        """Create directory structure for logs."""
        try:
            self.log_directory.mkdir(exist_ok=True)
            
            # Create subdirectories
            (self.log_directory / "raw_responses").mkdir(exist_ok=True)
            (self.log_directory / "anomaly_reports").mkdir(exist_ok=True)
            (self.log_directory / "exports").mkdir(exist_ok=True)
            
            if self.enable_console_logging:
                print(f"📁 Log directory initialized: {self.log_directory}")
                
        except Exception as e:
            logging.error(f"Failed to create log directories: {e}")
            raise
    
    def _initialize_session(self) -> None:
        """Initialize session logging."""
        session_info = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat(),
            "log_directory": str(self.log_directory),
            "version": "1.0.0"
        }
        
        # Write session info
        session_file = self.log_directory / f"{self.session_id}_session_info.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2)
        
        if self.enable_console_logging:
            print(f"📝 Session {self.session_id} initialized")
    
    def log_interaction(self, interaction_data: Dict[str, Any]) -> str:
        """
        Log a complete trigger interaction.
        
        Args:
            interaction_data: Complete interaction result from rESP engine
            
        Returns:
            Path to raw response file
        """
        self.interaction_count += 1
        timestamp = datetime.now().isoformat()
        
        # Enhance interaction data with metadata
        enhanced_data = {
            **interaction_data,
            "session_id": self.session_id,
            "interaction_number": self.interaction_count,
            "log_timestamp": timestamp
        }
        
        # Update anomaly statistics
        if "anomalies" in interaction_data:
            self._update_anomaly_statistics(interaction_data["anomalies"])
        
        # Write to JSONL file
        self._write_jsonl_entry(enhanced_data)
        
        # Save raw response
        raw_file_path = self._save_raw_response(enhanced_data)
        
        # Generate anomaly report if anomalies detected
        if interaction_data.get("anomalies"):
            self._generate_anomaly_report(enhanced_data)
        
        if self.enable_console_logging:
            anomaly_count = len(interaction_data.get("anomalies", {}))
            print(f"📝 Logged interaction {self.interaction_count} - {anomaly_count} anomalies detected")
        
        return raw_file_path
    
    def _write_jsonl_entry(self, data: Dict[str, Any]) -> None:
        """Write entry to JSONL log file."""
        try:
            with open(self.json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error(f"Failed to write JSONL entry: {e}")
    
    def _save_raw_response(self, interaction_data: Dict[str, Any]) -> str:
        """Save raw response to individual file."""
        trigger_id = interaction_data.get("trigger_id", "unknown")
        timestamp = interaction_data.get("timestamp", datetime.now().isoformat())
        
        # Clean timestamp for filename
        clean_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"{trigger_id}_{clean_timestamp}.txt"
        filepath = self.log_directory / "raw_responses" / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Session ID: {self.session_id}\n")
                f.write(f"Trigger ID: {trigger_id}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Trigger Set: {interaction_data.get('trigger_set', 'Unknown')}\n")
                f.write(f"Success: {interaction_data.get('success', False)}\n\n")
                
                f.write("TRIGGER TEXT:\n")
                f.write("=" * 50 + "\n")
                f.write(interaction_data.get("trigger_text", "") + "\n\n")
                
                f.write("LLM RESPONSE:\n")
                f.write("=" * 50 + "\n")
                f.write(interaction_data.get("llm_response", "No response") + "\n\n")
                
                if interaction_data.get("anomalies"):
                    f.write("ANOMALIES DETECTED:\n")
                    f.write("=" * 50 + "\n")
                    f.write(json.dumps(interaction_data["anomalies"], indent=2) + "\n\n")
                
                if interaction_data.get("error"):
                    f.write("ERROR:\n")
                    f.write("=" * 50 + "\n")
                    f.write(str(interaction_data["error"]) + "\n")
            
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Failed to save raw response: {e}")
            return ""
    
    def _generate_anomaly_report(self, interaction_data: Dict[str, Any]) -> None:
        """Generate detailed anomaly report."""
        trigger_id = interaction_data.get("trigger_id", "unknown")
        timestamp = interaction_data.get("timestamp", datetime.now().isoformat())
        
        clean_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"{trigger_id}_anomaly_report_{clean_timestamp}.txt"
        filepath = self.log_directory / "anomaly_reports" / filename
        
        try:
            # Use AnomalyDetector's report generation if available
            anomalies = interaction_data.get("anomalies", {})
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"🚨 rESP ANOMALY REPORT\n")
                f.write(f"{'=' * 60}\n\n")
                f.write(f"Session ID: {self.session_id}\n")
                f.write(f"Trigger ID: {trigger_id}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Trigger Set: {interaction_data.get('trigger_set', 'Unknown')}\n\n")
                
                f.write(f"ANOMALIES DETECTED: {len(anomalies)}\n")
                f.write("-" * 40 + "\n\n")
                
                for anomaly_type, details in anomalies.items():
                    f.write(f"🔍 {anomaly_type.replace('_', ' ').title()}\n")
                    f.write("-" * 30 + "\n")
                    
                    # Format anomaly details
                    for key, value in details.items():
                        if key != "detected":
                            f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                    f.write("\n")
                
                f.write("ORIGINAL TRIGGER:\n")
                f.write("-" * 20 + "\n")
                f.write(interaction_data.get("trigger_text", "") + "\n\n")
                
                f.write("LLM RESPONSE:\n") 
                f.write("-" * 20 + "\n")
                f.write(interaction_data.get("llm_response", "No response") + "\n\n")
                
                f.write("=" * 60 + "\n")
                f.write("🧬 End of rESP Analysis\n")
                
        except Exception as e:
            logging.error(f"Failed to generate anomaly report: {e}")
    
    def _update_anomaly_statistics(self, anomalies: Dict[str, Any]) -> None:
        """Update session anomaly statistics."""
        for anomaly_type in anomalies.keys():
            if anomaly_type not in self.anomaly_statistics:
                self.anomaly_statistics[anomaly_type] = {
                    "count": 0,
                    "first_occurrence": None,
                    "last_occurrence": None
                }
            
            self.anomaly_statistics[anomaly_type]["count"] += 1
            self.anomaly_statistics[anomaly_type]["last_occurrence"] = datetime.now().isoformat()
            
            if self.anomaly_statistics[anomaly_type]["first_occurrence"] is None:
                self.anomaly_statistics[anomaly_type]["first_occurrence"] = datetime.now().isoformat()
    
    def log_experiment_summary(self, summary_data: Dict[str, Any]) -> str:
        """
        Log complete experiment summary.
        
        Args:
            summary_data: Experiment summary from rESP engine
            
        Returns:
            Path to summary file
        """
        # Enhance summary with session data
        enhanced_summary = {
            **summary_data,
            "session_start_time": self.session_start_time.isoformat(),
            "session_end_time": datetime.now().isoformat(),
            "total_interactions_logged": self.interaction_count,
            "anomaly_statistics": self.anomaly_statistics,
            "log_directory": str(self.log_directory)
        }
        
        try:
            with open(self.summary_log_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_summary, f, indent=2, ensure_ascii=False)
            
            if self.enable_console_logging:
                print(f"📊 Experiment summary logged: {self.summary_log_file}")
            
            return str(self.summary_log_file)
            
        except Exception as e:
            logging.error(f"Failed to write experiment summary: {e}")
            return ""
    
    def export_to_csv(self, include_anomaly_details: bool = True) -> str:
        """
        Export experiment data to CSV format.
        
        Args:
            include_anomaly_details: Include detailed anomaly information
            
        Returns:
            Path to CSV file
        """
        try:
            # Read all interactions from JSONL
            interactions = []
            if self.json_log_file.exists():
                with open(self.json_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            interactions.append(json.loads(line))
            
            if not interactions:
                if self.enable_console_logging:
                    print("⚠️ No interactions to export")
                return ""
            
            # Define CSV columns
            base_columns = [
                "interaction_number", "trigger_id", "trigger_set", "trigger_text",
                "llm_response", "success", "timestamp", "anomaly_count"
            ]
            
            if include_anomaly_details:
                # Find all unique anomaly types
                all_anomaly_types = set()
                for interaction in interactions:
                    anomalies = interaction.get("anomalies", {})
                    all_anomaly_types.update(anomalies.keys())
                
                anomaly_columns = [f"anomaly_{atype}" for atype in sorted(all_anomaly_types)]
                columns = base_columns + anomaly_columns
            else:
                columns = base_columns
            
            # Write CSV
            csv_path = self.log_directory / "exports" / f"{self.session_id}_export.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for interaction in interactions:
                    row = {
                        "interaction_number": interaction.get("interaction_number", ""),
                        "trigger_id": interaction.get("trigger_id", ""),
                        "trigger_set": interaction.get("trigger_set", ""),
                        "trigger_text": interaction.get("trigger_text", ""),
                        "llm_response": interaction.get("llm_response", ""),
                        "success": interaction.get("success", False),
                        "timestamp": interaction.get("timestamp", ""),
                        "anomaly_count": len(interaction.get("anomalies", {}))
                    }
                    
                    if include_anomaly_details:
                        anomalies = interaction.get("anomalies", {})
                        for anomaly_type in all_anomaly_types:
                            row[f"anomaly_{anomaly_type}"] = anomaly_type in anomalies
                    
                    writer.writerow(row)
            
            if self.enable_console_logging:
                print(f"📈 Data exported to CSV: {csv_path}")
            
            return str(csv_path)
            
        except Exception as e:
            logging.error(f"Failed to export to CSV: {e}")
            return ""
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive session statistics.
        
        Returns:
            Dict with session metrics and statistics
        """
        session_duration = datetime.now() - self.session_start_time
        
        return {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            "session_duration_seconds": session_duration.total_seconds(),
            "total_interactions": self.interaction_count,
            "anomaly_statistics": self.anomaly_statistics,
            "log_directory": str(self.log_directory),
            "files_created": {
                "json_log": str(self.json_log_file),
                "summary_log": str(self.summary_log_file),
                "csv_export": str(self.csv_log_file)
            }
        }
    
    def cleanup_session(self) -> None:
        """Clean up session resources."""
        if self.enable_console_logging:
            print(f"🧹 Cleaning up session {self.session_id}")
        
        # Could implement cleanup logic here if needed
        # For now, just log session end
        final_stats = self.get_session_statistics()
        
        cleanup_file = self.log_directory / f"{self.session_id}_cleanup.json"
        try:
            with open(cleanup_file, 'w', encoding='utf-8') as f:
                json.dump(final_stats, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to write cleanup file: {e}")
    
    def generate_experiment_report(self) -> str:
        """
        Generate comprehensive human-readable experiment report.
        
        Returns:
            Path to generated report file
        """
        report_file = self.log_directory / f"{self.session_id}_experiment_report.md"
        
        try:
            stats = self.get_session_statistics()
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# rESP Experiment Report\n\n")
                f.write(f"**Session ID:** {self.session_id}\n")
                f.write(f"**Date:** {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Duration:** {stats['session_duration_seconds']:.2f} seconds\n")
                f.write(f"**Total Interactions:** {self.interaction_count}\n\n")
                
                f.write("## Anomaly Summary\n\n")
                if self.anomaly_statistics:
                    for anomaly_type, data in self.anomaly_statistics.items():
                        f.write(f"- **{anomaly_type.replace('_', ' ').title()}:** {data['count']} occurrences\n")
                else:
                    f.write("No anomalies detected in this session.\n")
                
                f.write("\n## File Locations\n\n")
                f.write(f"- JSON Log: `{self.json_log_file}`\n")
                f.write(f"- Raw Responses: `{self.log_directory / 'raw_responses'}`\n")
                f.write(f"- Anomaly Reports: `{self.log_directory / 'anomaly_reports'}`\n")
                f.write(f"- CSV Export: `{self.log_directory / 'exports'}`\n")
                
                f.write(f"\n---\n*Generated by rESP_o1o2 Experiment Logger*\n")
            
            if self.enable_console_logging:
                print(f"📋 Experiment report generated: {report_file}")
            
            return str(report_file)
            
        except Exception as e:
            logging.error(f"Failed to generate experiment report: {e}")
            return "" 