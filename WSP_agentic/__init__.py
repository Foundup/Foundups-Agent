# WSP_agentic/__init__.py
"""
This __init__.py file makes the WSP_agentic directory a Python package,
allowing for structured imports of its submodules. It also defines the
canonical paths for key agentic documents.
"""
# Canonical paths to agentic documents
# This dictionary provides a single source of truth for locating
# foundational agentic texts.
AGENTIC_DOCUMENTS = {
    "AGENTIC_SYSTEM": "src/AGENTIC_SYSTEM.md",
    "WSP_44_SEMANTIC_STATE_ENGINE": "../WSP_framework/src/WSP_44_Semantic_State_Engine_Protocol.md",
    "WSP_17_rESP_SELF_CHECK": "src/WSP_17_rESP_SELF_CHECK.md",
    "AGENTIC_CORE": "src/WSP_agentic.md"
}