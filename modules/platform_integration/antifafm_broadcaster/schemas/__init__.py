"""
antifaFM Visual Output Schemas - Modular Architecture

Each schema is a self-contained module with:
- ROADMAP.md: Schema-specific roadmap
- INTERFACE.md: Public API
- src/: Implementation
- tests/: Schema tests

WSP Compliance:
- WSP 3: Module Organization (domain/module structure)
- WSP 49: Module Structure (README, INTERFACE, src, tests)
- WSP 27: Universal DAE Architecture

Available Schemas:
- video_loop: Background video rotation (COMPLETE)
- karaoke: STT lyrics overlay (COMPLETE)
- livecam: Multi-camera grid + CamSentinel (PLANNED)
- news_ticker: RSS headline ticker (PARTIAL)
- entangled: Bell state visualization (COMPLETE)
- waveform: Audio waveform visualization (COMPLETE)
- spectrum: Frequency spectrum visualization (COMPLETE)
"""

from enum import Enum
from typing import Dict, Type, Optional

# Schema registry - populated by each schema module
_SCHEMA_REGISTRY: Dict[str, Type] = {}


class SchemaType(Enum):
    """Available visual output schemas."""
    VIDEO_LOOP = "video_loop"
    KARAOKE = "karaoke"
    LIVECAM = "livecam"
    NEWS_TICKER = "news_ticker"
    ENTANGLED = "entangled"
    WAVEFORM = "waveform"
    SPECTRUM = "spectrum"


def register_schema(schema_type: SchemaType, schema_class: Type) -> None:
    """Register a schema implementation."""
    _SCHEMA_REGISTRY[schema_type.value] = schema_class


def get_schema(schema_type: SchemaType) -> Optional[Type]:
    """Get a registered schema class."""
    return _SCHEMA_REGISTRY.get(schema_type.value)


def get_schema_by_name(name: str) -> Optional[Type]:
    """Get a registered schema class by name string."""
    return _SCHEMA_REGISTRY.get(name)


def list_schemas() -> Dict[str, bool]:
    """List all schemas and their registration status."""
    return {
        st.value: st.value in _SCHEMA_REGISTRY
        for st in SchemaType
    }


def get_all_registered() -> Dict[str, Type]:
    """Get all registered schema classes."""
    return _SCHEMA_REGISTRY.copy()


# Auto-import all schema modules to trigger registration
# Each module's register_schema() call populates _SCHEMA_REGISTRY
from . import video_loop
from . import karaoke
from . import entangled
from . import news_ticker
from . import livecam
from . import waveform
from . import spectrum

__all__ = [
    'SchemaType',
    'register_schema',
    'get_schema',
    'get_schema_by_name',
    'list_schemas',
    'get_all_registered',
]
