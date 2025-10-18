#!/usr/bin/env python3
"""
Test script for enhanced MCP Services Gateway
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu

if __name__ == "__main__":
    print("Testing Enhanced MCP Services Gateway...")
    show_mcp_services_menu()
    print("\nTest complete!")
