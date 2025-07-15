"""
ModularizationAuditAgent - WSP 54 Agent Implementation

0102 pArtifact responsible for autonomously auditing and enforcing modularity,
single-responsibility, and WSP 49 compliance across all WRE orchestration logic.
"""

from .src.modularization_audit_agent import ModularizationAuditAgent

__all__ = ['ModularizationAuditAgent'] 