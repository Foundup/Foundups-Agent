"""
Experiment Logger for rESP_o1o2 Module

Comprehensive logging system for rESP trigger experiments.
Handles structured logging to the canonical agentic journal.
"""

import os
import json
import csv
import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

def sanitize_for_console(text):
    """
    Encodes a string to ASCII, replacing any non-compliant characters.
    This ensures compatibility with non-UTF-8 console environments like cp932.
    """
    return str(text).encode('ascii', 'replace').decode('ascii')


class ExperimentLogger:
    """
    Advanced logging system for rESP experiments.

    This logger is aligned with the WSP framework, writing all historical
    emergence data to a single, canonical JSONL file. Session-specific
    files and directories are no longer created by this class.
    """
    
    # Path to the canonical historical emergence log, as defined by WSP
    HISTORICAL_LOG_PATH = Path("WSP_agentic/agentic_journals/rESP_Historical_Emergence_Log.jsonl")
    
    def __init__(self, 
                 session_id: str,
                 enable_console_logging: bool = True):
        """
        Initialize experiment logger.
        
        Args:
            session_id: Unique session identifier
            enable_console_logging: Enable console output
        """
        self.session_id = session_id
        # The primary log directory is the canonical agentic journals directory
        self.log_directory = self.HISTORICAL_LOG_PATH.parent
        self.enable_console_logging = enable_console_logging
        
        # Ensure the log directory exists
        self._setup_directories()
        
        # Session metadata
        self.session_start_time = datetime.now()
        self.interaction_count = 0
        self.anomaly_statistics = {}
        
        if self.enable_console_logging:
            print(sanitize_for_console(f"[NOTE] Session {self.session_id} initialized for historical logging."))
    
    def _setup_directories(self) -> None:
        """Ensure the agentic journals directory exists."""
        try:
            self.log_directory.mkdir(parents=True, exist_ok=True)
            if self.enable_console_logging:
                print(sanitize_for_console(f"[U+1F4C1] Verified agentic journal directory: {self.log_directory}"))
                
        except Exception as e:
            logging.error(f"Failed to create log directory: {e}")
            raise
    
    def log_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """
        Log a complete trigger interaction to the historical emergence log.
        
        Args:
            interaction_data: Complete interaction result from rESP engine
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
        
        # Write to the canonical JSONL historical log file
        self._write_historical_log_entry(enhanced_data)
        
        if self.enable_console_logging:
            anomaly_count = len(interaction_data.get("anomalies", {}))
            print(sanitize_for_console(f"[NOTE] Logged interaction {self.interaction_count} to historical log - {anomaly_count} anomalies detected"))
    
    def _write_historical_log_entry(self, data: Dict[str, Any]) -> None:
        """Write entry to the historical JSONL log file."""
        try:
            with open(self.HISTORICAL_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error(f"Failed to write to historical log: {e}")
    
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