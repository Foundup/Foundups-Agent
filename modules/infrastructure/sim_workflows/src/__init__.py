# sim_workflows src package
from .sim_client import SimWorkflowsClient
from .sim_socket_bridge import SimSocketBridge
from .sim_webhook import verify_signature

import asyncio
import threading
from typing import Optional, Callable, Dict, Any


def start_sim_bridge_background(
    sim_url: str,
    on_event: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Callable[[], None]:
    """Start Socket.io bridge in a background thread and return a stopper.

    - Non-blocking; designed for optional initialization from main.
    - on_event receives a dict with keys: event, payload
    """
    loop = asyncio.new_event_loop()
    bridge = SimSocketBridge(sim_url=sim_url)
    if on_event:
        for evt in ("flow-status", "flow-log", "flow-error", "connect", "disconnect"):
            bridge.on_event(evt, on_event)

    async def run() -> None:
        await bridge.connect()
        # Keep loop alive
        while True:
            await asyncio.sleep(1.0)

    def thread_target() -> None:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())

    thread = threading.Thread(target=thread_target, daemon=True)
    thread.start()

    def stop() -> None:
        try:
            loop.call_soon_threadsafe(asyncio.create_task, bridge.disconnect())
            loop.call_soon_threadsafe(loop.stop)
        except Exception:
            pass

    return stop
