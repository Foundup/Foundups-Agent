# -*- coding: utf-8 -*-
import sys
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

Infrastructure Deployment Module

Provides deployment tooling and configuration for FoundUps autonomous platform.

Public API:
- deploy-vercel.ps1: Automated Vercel deployment script
- vercel.json: Vercel deployment configuration
- package.json: Node.js package configuration
"""

__version__ = "1.0.0"
__all__ = []  # No Python modules to export - scripts and configs only
