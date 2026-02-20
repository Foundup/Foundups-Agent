"""OpenClaw Bridge Module - Digital Twin gateway via OpenClaw + WRE routing."""

# OpenClaw DAE + WRE Plugin adapter are always available (no heavy dependencies)
from .openclaw_dae import OpenClawDAE, OpenClawPlugin, HoneypotDefense

# FastAPI components require fastapi/pydantic (optional at import time)
try:
    from .webhook_receiver import app, MoltbotMessage, OpenClawMessage, FoundupsResponse
    _FASTAPI_AVAILABLE = True
except ImportError:
    app = None  # type: ignore
    MoltbotMessage = None  # type: ignore
    OpenClawMessage = None  # type: ignore
    FoundupsResponse = None  # type: ignore
    _FASTAPI_AVAILABLE = False

__all__ = ["OpenClawDAE", "OpenClawPlugin", "HoneypotDefense", "app", "MoltbotMessage", "OpenClawMessage", "FoundupsResponse"]
