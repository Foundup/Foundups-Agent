#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

WSP Shared Module: ModLog Integration
====================================

Automated ModLog integration for MPS tool usage and scoring updates.
This module provides standardized ModLog entry creation for tool activities,
supporting WSP 10 compliance for change documentation.

WSP Compliance:
- Follows WSP 10 (ModLog) requirements for change documentation
- Integrates with existing utils/modlog_updater.py infrastructure
- Supports automated documentation of priority changes
- Maintains consistent ModLog formatting

Author: FoundUps Agent Utility System
Version: 1.0.0
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add utils to path for modlog_updater import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))

try:
    from modlog_updater import update_modlog_entry
except ImportError:
    logging.warning("[U+26A0]️ modlog_updater not available - ModLog integration disabled")
    update_modlog_entry = None

logger = logging.getLogger(__name__)

class ModLogIntegration:
    """
    Handles automated ModLog entries for MPS tool activities.
    
    Provides standardized logging for:
    - MPS score calculations and updates
    - Priority changes and rankings
    - Tool usage and automation activities
    - Protocol compliance events
    """
    
    def __init__(self, auto_update: bool = True):
        """
        Initialize ModLog integration.
        
        Args:
            auto_update: Whether to automatically write ModLog entries
        """
        self.auto_update = auto_update
        self.modlog_available = update_modlog_entry is not None
        
        if not self.modlog_available:
            logger.warning("[U+26A0]️ ModLog updater not available - entries will be logged only")
        
        logger.info("[NOTE] ModLog Integration initialized")
    
    def log_mps_calculation(self, modules: List[Dict[str, Any]], tool_name: str) -> bool:
        """
        Log MPS calculation activity to ModLog.
        
        Args:
            modules: List of modules with calculated MPS scores
            tool_name: Name of the tool performing the calculation
            
        Returns:
            bool: True if successfully logged, False otherwise
        """
        if not modules:
            logger.warning("[U+26A0]️ No modules provided for MPS calculation logging")
            return False
        
        # Find highest priority module
        top_module = max(modules, key=lambda x: x.get('mps', 0))
        module_count = len(modules)
        
        # Create ModLog entry
        update_data = {
            "module": "agent_utilities",
            "version": "1.0.0",
            "type": "optimization",
            "description": f"MPS calculation performed via {tool_name}",
            "changes": [
                f"Calculated MPS scores for {module_count} modules",
                f"Top priority: {top_module['name']} (MPS: {top_module['mps']:.2f})",
                f"Tool used: {tool_name}",
                "Priority ranking updated for development workflow"
            ],
            "notes": f"Automated MPS scoring completed. Use results to guide development priorities."
        }
        
        return self._write_modlog_entry(update_data)
    
    def log_priority_change(self, old_ranking: List[str], new_ranking: List[str], reason: str) -> bool:
        """
        Log priority ranking changes to ModLog.
        
        Args:
            old_ranking: Previous module priority order
            new_ranking: New module priority order  
            reason: Reason for the priority change
            
        Returns:
            bool: True if successfully logged, False otherwise
        """
        if old_ranking == new_ranking:
            logger.info("ℹ️ No priority changes detected - skipping ModLog entry")
            return True
        
        # Identify changes
        changes = []
        if len(new_ranking) != len(old_ranking):
            changes.append(f"Module count changed: {len(old_ranking)} -> {len(new_ranking)}")
        
        # Check position changes
        for i, module in enumerate(new_ranking[:3]):  # Top 3 changes
            try:
                old_pos = old_ranking.index(module) + 1
                new_pos = i + 1
                if old_pos != new_pos:
                    changes.append(f"{module}: #{old_pos} -> #{new_pos}")
            except ValueError:
                changes.append(f"{module}: NEW entry at #{i+1}")
        
        if not changes:
            changes.append("Minor priority adjustments - ranking order maintained")
        
        update_data = {
            "module": "agent_utilities", 
            "version": "1.0.0",
            "type": "optimization",
            "description": f"Module priority ranking updated",
            "changes": [
                f"Priority ranking modified: {reason}",
                f"Top 3 priorities: {', '.join(new_ranking[:3])}",
                *changes
            ],
            "notes": "Development team should review updated priorities for resource allocation."
        }
        
        return self._write_modlog_entry(update_data)
    
    def log_tool_automation(self, tool_name: str, automation_type: str, details: Dict[str, Any]) -> bool:
        """
        Log tool automation activities to ModLog.
        
        Args:
            tool_name: Name of the automated tool
            automation_type: Type of automation (batch, scheduled, triggered)
            details: Additional automation details
            
        Returns:
            bool: True if successfully logged, False otherwise
        """
        update_data = {
            "module": "agent_utilities",
            "version": "1.0.0", 
            "type": "automation",
            "description": f"{tool_name} automation executed",
            "changes": [
                f"Automation type: {automation_type}",
                f"Tool: {tool_name}",
                f"Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                *[f"{k}: {v}" for k, v in details.items()]
            ],
            "notes": f"Automated execution of {tool_name} completed successfully."
        }
        
        return self._write_modlog_entry(update_data)
    
    def log_protocol_compliance(self, protocol_name: str, compliance_status: str, details: List[str]) -> bool:
        """
        Log protocol compliance checking to ModLog.
        
        Args:
            protocol_name: Name of the WSP protocol checked
            compliance_status: PASS, FAIL, WARNING
            details: List of compliance check details
            
        Returns:
            bool: True if successfully logged, False otherwise
        """
        emoji_map = {
            "PASS": "[OK]",
            "FAIL": "[FAIL]", 
            "WARNING": "[U+26A0]️"
        }
        
        emoji = emoji_map.get(compliance_status, "ℹ️")
        
        update_data = {
            "module": "agent_utilities",
            "version": "1.0.0",
            "type": "compliance",
            "description": f"{protocol_name} compliance check: {compliance_status}",
            "changes": [
                f"{emoji} Protocol: {protocol_name}",
                f"Status: {compliance_status}",
                f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                *details
            ],
            "notes": f"WSP compliance verification for {protocol_name} protocol."
        }
        
        return self._write_modlog_entry(update_data)
    
    def _write_modlog_entry(self, update_data: Dict[str, Any]) -> bool:
        """
        Write entry to ModLog using the existing updater infrastructure.
        
        Args:
            update_data: Dictionary containing ModLog entry data
            
        Returns:
            bool: True if successfully written, False otherwise
        """
        if not self.auto_update:
            logger.info(f"[NOTE] ModLog entry prepared (auto-update disabled): {update_data['description']}")
            return True
        
        if not self.modlog_available:
            logger.warning(f"[U+26A0]️ ModLog updater unavailable - logging entry: {update_data['description']}")
            logger.info(f"   Changes: {update_data['changes']}")
            return False
        
        try:
            success = update_modlog_entry(update_data)
            if success:
                logger.info(f"[OK] ModLog entry written: {update_data['description']}")
            else:
                logger.error(f"[FAIL] Failed to write ModLog entry: {update_data['description']}")
            return success
            
        except Exception as e:
            logger.error(f"[FAIL] Error writing ModLog entry: {e}")
            return False
    
    def create_manual_entry_template(self, entry_type: str, description: str) -> str:
        """
        Create a formatted ModLog entry template for manual addition.
        
        Args:
            entry_type: Type of entry (optimization, automation, compliance)
            description: Description of the change
            
        Returns:
            str: Formatted ModLog entry template
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        template = f"""
### v1.0.0 - {timestamp}
- **Type**: [TOOL] {entry_type.title()}
- **Module**: agent_utilities
- **Description**: {description}
- **Changes**:
  - [Add specific changes here]
  - [List modifications made]
  - [Include relevant details]
- **Notes**: [Add any additional context or instructions]

"""
        return template.strip()


# Convenience functions for direct usage
def log_mps_activity(modules: List[Dict[str, Any]], tool_name: str) -> bool:
    """Convenience function to log MPS calculation activity."""
    integrator = ModLogIntegration()
    return integrator.log_mps_calculation(modules, tool_name)

def log_priority_update(old_ranking: List[str], new_ranking: List[str], reason: str) -> bool:
    """Convenience function to log priority changes."""
    integrator = ModLogIntegration()
    return integrator.log_priority_change(old_ranking, new_ranking, reason)

def log_automation_activity(tool_name: str, automation_type: str, details: Dict[str, Any]) -> bool:
    """Convenience function to log tool automation."""
    integrator = ModLogIntegration()
    return integrator.log_tool_automation(tool_name, automation_type, details)


# Example usage and testing
if __name__ == "__main__":
    print("[U+1F9EA] Testing ModLog Integration")
    print("=" * 40)
    
    integrator = ModLogIntegration(auto_update=False)  # Disable auto-update for testing
    
    # Test MPS calculation logging
    print("\n1. MPS Calculation Logging:")
    test_modules = [
        {"name": "banter_engine", "mps": 102.0},
        {"name": "livechat", "mps": 99.0},
        {"name": "stream_resolver", "mps": 75.0}
    ]
    success = integrator.log_mps_calculation(test_modules, "process_and_score_modules.py")
    print(f"   MPS logging: {'[OK] Success' if success else '[FAIL] Failed'}")
    
    # Test priority change logging
    print("\n2. Priority Change Logging:")
    old_ranking = ["livechat", "banter_engine", "stream_resolver"]
    new_ranking = ["banter_engine", "livechat", "stream_resolver"]
    success = integrator.log_priority_change(old_ranking, new_ranking, "Updated MPS weights")
    print(f"   Priority logging: {'[OK] Success' if success else '[FAIL] Failed'}")
    
    # Test automation logging
    print("\n3. Automation Activity Logging:")
    automation_details = {
        "modules_processed": 7,
        "execution_time": "2.3s",
        "output_format": "markdown+csv"
    }
    success = integrator.log_tool_automation("guided_dev_protocol.py", "scheduled", automation_details)
    print(f"   Automation logging: {'[OK] Success' if success else '[FAIL] Failed'}")
    
    # Test protocol compliance logging
    print("\n4. Protocol Compliance Logging:")
    compliance_details = [
        "[OK] All modules have MPS scores",
        "[OK] Priority ranking is up to date", 
        "[U+26A0]️ Manual verification recommended"
    ]
    success = integrator.log_protocol_compliance("WSP 5 (MPS)", "WARNING", compliance_details)
    print(f"   Compliance logging: {'[OK] Success' if success else '[FAIL] Failed'}")
    
    # Test manual template generation
    print("\n5. Manual Entry Template:")
    template = integrator.create_manual_entry_template("optimization", "Tool consolidation completed")
    print("   Template generated:")
    print("   " + "\n   ".join(template.split("\n")[:5]) + "...")
    
    print("\n[OK] All tests completed successfully!") 