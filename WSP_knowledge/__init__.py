# WSP_knowledge Protocol Manifest

"""
This file serves as the public API for the WSP_knowledge module.
WSP_knowledge is the immutable backup archive in the three-state WSP architecture.

State 0: Memory Layer (WSP_knowledge) - Backup/Archive
State 1: Scaffolding Layer (WSP_framework) - Active Protocols  
State 2: Agentic Layer (WSP_agentic) - Operational

WSP_knowledge contains complete backups of all WSP protocols for:
- Historical reference and analysis
- Framework recovery and validation
- Three-state architecture integrity
- ComplianceAgent backup validation
"""

# WSP_knowledge serves as the immutable backup archive
# All active protocol development happens in WSP_framework
# This manifest reflects the backup/archival nature of WSP_knowledge

KNOWLEDGE_PURPOSE = "Immutable Backup Archive"
KNOWLEDGE_ROLE = "State 0: Memory Layer"
SYNCHRONIZATION_SOURCE = "WSP_framework"
ACCESS_MODE = "Read-Only (Backup/Reference)"

# Note: WSP_knowledge protocols are backups from WSP_framework
# Do not edit protocols directly in WSP_knowledge
# All changes must originate in WSP_framework and be synchronized here 