from __future__ import annotations

from typing import Any, Callable, Dict

import socketio


class SimSocketBridge:
    """Resilient Socket.io client to consume Sim events and forward to WRE.

    Caller registers event handlers via on_event().
    """

    def __init__(self, sim_url: str) -> None:
        self._sim_url: str = sim_url.rstrip("/")
        # Reconnection defaults suitable for local dev
        self._sio = socketio.AsyncClient(reconnection=True, reconnection_attempts=0)
        self._handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}

    def on_event(self, event: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        self._handlers[event] = handler

    async def connect(self) -> None:
        await self._sio.connect(self._sim_url)

        @self._sio.event
        async def connect() -> None:  # type: ignore
            handler = self._handlers.get("connect")
            if handler:
                handler({"event": "connect"})

        @self._sio.event
        async def disconnect() -> None:  # type: ignore
            handler = self._handlers.get("disconnect")
            if handler:
                handler({"event": "disconnect"})

        # Generic catch-all for known Sim events
        for evt in ("flow-status", "flow-log", "flow-error"):
            self._sio.on(evt, self._wrap(evt))

    def _wrap(self, event: str) -> Callable[[Dict[str, Any]], Any]:
        async def _inner(payload: Dict[str, Any]) -> None:
            handler = self._handlers.get(event)
            if handler:
                handler({"event": event, "payload": payload})
        return _inner

    async def disconnect(self) -> None:
        await self._sio.disconnect()
