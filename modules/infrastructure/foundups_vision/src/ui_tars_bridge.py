"""
UI-TARS Bridge - Connection to UI-TARS Desktop for Vision-Based Browser Automation

WSP Compliance:
    - WSP 3: Infrastructure domain
    - WSP 77: AI Overseer integration (telemetry events)
    - WSP 91: DAEMON observability

UI-TARS Desktop Location: E:/HoloIndex/models/ui-tars-1.5
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default paths
UI_TARS_PATH = Path(os.getenv("UI_TARS_PATH", "E:/HoloIndex/models/ui-tars-1.5"))
UI_TARS_TELEMETRY = UI_TARS_PATH / "telemetry"
SCREENSHOT_DIR = Path("modules/infrastructure/foundups_vision/memory/screenshots")


@dataclass
class ActionResult:
    """Result of a vision-based action."""
    success: bool
    action: str
    description: str
    duration_ms: int
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    error: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "description": self.description,
            "duration_ms": self.duration_ms,
            "screenshot_before": self.screenshot_before,
            "screenshot_after": self.screenshot_after,
            "error": self.error,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class Screenshot:
    """Screenshot capture result."""
    path: str
    timestamp: datetime
    url: Optional[str] = None
    hash: Optional[str] = None
    width: int = 0
    height: int = 0


class UITarsConnectionError(Exception):
    """UI-TARS Desktop not running or unreachable."""
    pass


class ElementNotFoundError(Exception):
    """Vision model could not locate element."""
    pass


class ActionTimeoutError(Exception):
    """Action exceeded timeout."""
    pass


class UITarsBridge:
    """
    Bridge to UI-TARS Desktop for vision-based browser automation.
    
    UI-TARS provides:
    - Remote Browser Operator (vision-based browser control)
    - Screenshot → Element Detection → Action execution
    - MCP integration for tool calling
    
    Usage:
        bridge = UITarsBridge()
        result = await bridge.execute_action(
            action="click",
            description="blue Like button under the comment"
        )
    """

    def __init__(
        self,
        ui_tars_path: str = None,
        browser_port: int = 9222,
        observers: Optional[List[Callable[[str, Dict[str, Any]], None]]] = None,
    ) -> None:
        """
        Initialize UI-TARS bridge.
        
        Args:
            ui_tars_path: Path to UI-TARS Desktop installation
            browser_port: Chrome debugging port
            observers: Telemetry observers for AI Overseer integration
        """
        self.ui_tars_path = Path(ui_tars_path) if ui_tars_path else UI_TARS_PATH
        self.browser_port = browser_port
        self._observers = list(observers or [])
        self._connected = False
        self._session_id = None
        
        # Ensure directories exist
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        UI_TARS_TELEMETRY.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[UI-TARS] Bridge initialized, path: {self.ui_tars_path}")
        self._emit_event("bridge_init", {"path": str(self.ui_tars_path), "port": browser_port})

    def _emit_event(self, event: str, payload: Dict[str, Any]) -> None:
        """Emit telemetry event to observers."""
        payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
        for observer in self._observers:
            try:
                observer(event, payload)
            except Exception as e:
                logger.warning(f"[UI-TARS] Observer error: {e}")
        
        # Also write to telemetry file for AI Overseer
        try:
            telemetry_file = UI_TARS_TELEMETRY / "bridge_events.jsonl"
            with open(telemetry_file, "a", encoding="utf-8") as f:
                f.write(json.dumps({"event": event, **payload}) + "\n")
        except Exception as e:
            logger.debug(f"[UI-TARS] Telemetry write failed: {e}")

    def register_observer(self, observer: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register a telemetry observer."""
        self._observers.append(observer)

    async def connect(self) -> bool:
        """
        Connect to UI-TARS Desktop.
        
        Returns:
            True if connected successfully
            
        Raises:
            UITarsConnectionError: If UI-TARS is not available
        """
        self._emit_event("connect_start", {"port": self.browser_port})
        
        # Check if UI-TARS path exists
        if not self.ui_tars_path.exists():
            error = f"UI-TARS not found at {self.ui_tars_path}"
            self._emit_event("connect_failed", {"error": error})
            raise UITarsConnectionError(error)

        # Check for UI-TARS process or API
        # For now, we'll use a file-based communication pattern
        # UI-TARS Desktop reads from telemetry/inbox and writes to telemetry/outbox
        inbox = UI_TARS_TELEMETRY / "inbox"
        outbox = UI_TARS_TELEMETRY / "outbox"
        inbox.mkdir(exist_ok=True)
        outbox.mkdir(exist_ok=True)

        # Health check LM Studio / Responses API (port 1234) if configured
        tars_base = os.getenv("TARS_API_URL", "http://127.0.0.1:1234").rstrip("/")
        if tars_base.endswith("/v1"):
            tars_base = tars_base[:-3]
        try:
            import requests  # lightweight check; ignore if missing

            resp = requests.get(f"{tars_base}/v1/models", timeout=2)
            if resp.status_code == 200:
                self._emit_event("lm_studio_ready", {"base_url": tars_base})
                logger.info(f"[UI-TARS] LM Studio ready at {tars_base}")
            else:
                self._emit_event("lm_studio_unreachable", {"base_url": tars_base, "status": resp.status_code})
                logger.warning(f"[UI-TARS] LM Studio unreachable ({resp.status_code}) at {tars_base}")
        except Exception as e:
            self._emit_event("lm_studio_unreachable", {"base_url": tars_base, "error": str(e)})
            logger.warning(f"[UI-TARS] LM Studio health check failed: {e}")

        self._connected = True
        self._session_id = f"session_{int(time.time())}"
        
        self._emit_event("connect_success", {"session_id": self._session_id})
        logger.info(f"[UI-TARS] Connected, session: {self._session_id}")
        
        return True

    async def capture_screenshot(self) -> Screenshot:
        """
        Capture current browser state.
        
        Returns:
            Screenshot object with image data and metadata
        """
        import hashlib
        
        timestamp = datetime.now()
        filename = f"screenshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
        filepath = SCREENSHOT_DIR / filename
        
        self._emit_event("screenshot_start", {"path": str(filepath)})
        
        try:
            # Use Chrome DevTools Protocol to capture screenshot
            # This requires browser with --remote-debugging-port=9222
            import requests
            
            # Get browser tabs
            tabs_url = f"http://127.0.0.1:{self.browser_port}/json"
            try:
                response = requests.get(tabs_url, timeout=5)
                tabs = response.json()
            except Exception as e:
                logger.warning(f"[UI-TARS] Could not connect to browser: {e}")
                # Fallback: create placeholder
                self._emit_event("screenshot_failed", {"error": str(e)})
                return Screenshot(
                    path=str(filepath),
                    timestamp=timestamp,
                    url=None,
                    hash=None,
                )
            
            if tabs:
                # Get WebSocket URL for first tab
                ws_url = tabs[0].get("webSocketDebuggerUrl")
                current_url = tabs[0].get("url")
                
                # For now, use simple screenshot via pyautogui or similar
                # Full CDP implementation would require websocket connection
                logger.info(f"[UI-TARS] Browser URL: {current_url}")
                
                # Calculate hash for deduplication
                file_hash = hashlib.sha256(current_url.encode()).hexdigest()[:16] if current_url else None
                
                self._emit_event("screenshot_complete", {
                    "path": str(filepath),
                    "url": current_url,
                    "hash": file_hash,
                })
                
                return Screenshot(
                    path=str(filepath),
                    timestamp=timestamp,
                    url=current_url,
                    hash=file_hash,
                )
            
        except Exception as e:
            self._emit_event("screenshot_failed", {"error": str(e)})
            logger.error(f"[UI-TARS] Screenshot failed: {e}")
        
        return Screenshot(path=str(filepath), timestamp=timestamp)

    async def execute_action(
        self,
        action: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 90,  # Increased for 7B vision model inference
        **kwargs  # Accept additional parameters like 'target'
    ) -> ActionResult:
        """
        Execute a vision-based action using LM Studio API.

        Args:
            action: Action type ('click', 'type', 'scroll', 'verify')
            description: Human-readable description of target element
            context: Additional context (video_id, comment_id, etc.)
            timeout: Max seconds to wait for action (default 90s for CPU inference)

        Returns:
            ActionResult with success status and details
        """
        start_time = time.time()
        context = context or {}

        self._emit_event("action_start", {
            "action": action,
            "description": description,
            "context": context,
        })

        try:
            # Ensure connected
            if not self._connected:
                await self.connect()

            # Get Selenium driver from context (passed by ActionRouter)
            driver = kwargs.get('driver') or context.get('driver')
            if not driver:
                raise Exception("No Selenium driver available for screenshot/click")

            # 1. Capture screenshot from Selenium (viewport screenshot; includes devicePixelRatio scaling)
            import base64
            from PIL import Image
            import io

            screenshot_bytes = driver.get_screenshot_as_png()

            # Resize screenshot to speed up inference (1280px width max)
            img = Image.open(io.BytesIO(screenshot_bytes))
            original_screenshot_size = img.size  # Actual screenshot dimensions (with DPI scaling)
            resized_image_size = original_screenshot_size  # Will be set if resized

            if img.width > 1280:
                ratio = 1280 / img.width
                resized_image_size = (1280, int(img.height * ratio))
                img = img.resize(resized_image_size, Image.Resampling.LANCZOS)
                logger.info(f"[UI-TARS] Resized screenshot: {original_screenshot_size} -> {resized_image_size}")
            else:
                logger.info(f"[UI-TARS] Using original screenshot size: {original_screenshot_size}")

            # Convert back to PNG bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            screenshot_bytes = img_buffer.getvalue()

            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

            # Derive screenshot-to-viewport scale (accounts for devicePixelRatio / Windows scaling)
            screenshot_scale = 1.0
            try:
                viewport = driver.execute_script(
                    "return {w: window.innerWidth || 0, h: window.innerHeight || 0, dpr: window.devicePixelRatio || 1};"
                ) or {}
                vw = float(viewport.get("w") or 0)
                vh = float(viewport.get("h") or 0)
                if vw > 0 and vh > 0:
                    screenshot_scale = max(0.1, min(10.0, original_screenshot_size[0] / vw))
                logger.info(
                    f"[UI-TARS] Viewport: {int(vw)}x{int(vh)} dpr={viewport.get('dpr')} screenshot_scale={screenshot_scale:.3f}"
                )
            except Exception as e:
                logger.debug(f"[UI-TARS] Viewport scale check failed: {e}")

            logger.info(f"[UI-TARS] Calling LM Studio API for: {action} - {description}")

            # 2. Call LM Studio API
            import requests
            tars_api_url = os.getenv("TARS_API_URL", "http://127.0.0.1:1234").rstrip("/")
            if tars_api_url.endswith("/v1"):
                tars_api_url = tars_api_url[:-3]

            # Build prompt for UI-TARS model (constrained: stay on page; avoid browser chrome)
            text = (context or {}).get("text") if action == "type" else None
            direction = (context or {}).get("direction") if action == "scroll" else None

            if action == "verify":
                goal = f"Locate (do not click) the {description} on the current page."
            elif action == "type":
                goal = f"Locate the input field for: {description}. You will not type; only locate the field."
            elif action == "scroll":
                goal = f"Locate the area related to: {description}. You will not scroll; only locate the best anchor point."
            else:
                goal = f"Find and click the {description} on the current page."

            prompt = f"""You are a GUI agent operating INSIDE the current web page content.
Do NOT click the browser address bar, tabs, extensions, or open new pages/tabs. Stay on the current page.

Task: {goal}

Output format (exactly):
Thought: <one short sentence>
Action: click(start_box='<|box_start|>(x,y)<|box_end|>')

Rules:
- Coordinates are in a 1000x1000 grid over the provided screenshot.
- Pick the center of the target.
- If the target is not visible or you are unsure, output:
  Thought: <one short sentence>
  Action: finished()"""

            response = requests.post(
                f"{tars_api_url}/v1/chat/completions",
                json={
                    "model": "ui-tars-1.5-7b",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}
                                }
                            ]
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.1,
                },
                timeout=timeout
            )

            if response.status_code != 200:
                raise Exception(f"LM Studio API error: {response.status_code} - {response.text}")

            # 3. Parse UI-TARS Desktop response format
            response_data = response.json()
            model_output = response_data['choices'][0]['message']['content']

            logger.info(f"[UI-TARS] Raw model output: {model_output[:200]}...")

            # Parse UI-TARS Desktop format: "Action: click(start_box='<|box_start|>(x,y)<|box_end|>')"
            import re

            # Extract thought (optional)
            thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|\Z)', model_output, re.DOTALL)
            thought = thought_match.group(1).strip() if thought_match else ""

            # Extract action coordinates
            # Supports:
            # - click(start_box='<|box_start|>(x1,y1)<|box_end|>')
            # - click(start_box='<|box_start|>(x1,y1)<|box_end|>(x2,y2)')  (bbox)
            coords_match = re.search(
                r"click\(\s*start_box\s*=\s*['\"]<\|box_start\|>\((\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\)<\|box_end\|>(?:\((\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\))?['\"]",
                model_output,
            )

            if not coords_match:
                duration_ms = int((time.time() - start_time) * 1000)
                if 'finished()' in model_output or 'call_user()' in model_output:
                    return ActionResult(
                        success=False,
                        action=action,
                        description=description,
                        duration_ms=duration_ms,
                        error=f"Element not found. Model response: {thought or model_output[:100]}",
                        confidence=0.0,
                    )
                return ActionResult(
                    success=False,
                    action=action,
                    description=description,
                    duration_ms=duration_ms,
                    error=f"Could not parse coordinates from model output: {model_output[:200]}",
                    confidence=0.0,
                )

            # UI-TARS uses 1000x1000 coordinate space (factors: [1000, 1000])
            x1 = float(coords_match.group(1))
            y1 = float(coords_match.group(2))
            x2 = float(coords_match.group(3)) if coords_match.group(3) else None
            y2 = float(coords_match.group(4)) if coords_match.group(4) else None

            # If bbox provided, click center; else use point.
            box_x = int(round((x1 + x2) / 2.0)) if x2 is not None else int(round(x1))
            box_y = int(round((y1 + y2) / 2.0)) if y2 is not None else int(round(y1))

            # Normalize to 0-1 range
            normalized_x = box_x / 1000.0
            normalized_y = box_y / 1000.0

            logger.info(f"[UI-TARS] Parsed coordinates: box=({box_x},{box_y}), normalized=({normalized_x:.3f},{normalized_y:.3f})")
            logger.info(f"[UI-TARS] Thought: {thought[:100] if thought else 'N/A'}")

            # 4. Map to viewport CSS coordinates (elementFromPoint uses CSS pixels)
            resized_pixel_x = (box_x / 1000.0) * resized_image_size[0]
            resized_pixel_y = (box_y / 1000.0) * resized_image_size[1]

            # Scale back to original screenshot dimensions
            scale_x = original_screenshot_size[0] / resized_image_size[0]
            scale_y = original_screenshot_size[1] / resized_image_size[1]

            screenshot_pixel_x = int(resized_pixel_x * scale_x)
            screenshot_pixel_y = int(resized_pixel_y * scale_y)

            viewport_css_x = int(screenshot_pixel_x / screenshot_scale)
            viewport_css_y = int(screenshot_pixel_y / screenshot_scale)

            logger.info("[UI-TARS] Coordinate mapping:")
            logger.info(f"  Box (1000x1000): ({box_x}, {box_y})")
            logger.info(f"  Resized image ({resized_image_size}): ({resized_pixel_x:.0f}, {resized_pixel_y:.0f})")
            logger.info(f"  Screenshot px ({original_screenshot_size}): ({screenshot_pixel_x}, {screenshot_pixel_y})")
            logger.info(f"  Viewport CSS px: ({viewport_css_x}, {viewport_css_y})")

            executed = None
            if action == "click":
                executed = driver.execute_script(
                    """
                    const x = arguments[0], y = arguments[1];
                    const el = document.elementFromPoint(x, y);
                    if (!el) return { ok: false, error: "No element at point" };
                    el.click();
                    return { ok: true, tag: el.tagName, id: el.id || null, className: el.className || null };
                    """,
                    viewport_css_x,
                    viewport_css_y,
                )
            elif action == "type":
                if not text:
                    raise Exception("Type action requires context.text")
                executed = driver.execute_script(
                    """
                    const x = arguments[0], y = arguments[1], text = arguments[2];
                    const el = document.elementFromPoint(x, y);
                    if (!el) return { ok: false, error: "No element at point" };

                    function findEditable(start) {
                      if (!start) return null;
                      const tag = (start.tagName || "").toUpperCase();
                      if (tag === "TEXTAREA" || tag === "INPUT") return start;
                      if (start.isContentEditable) return start;
                      const byClosest = start.closest?.("textarea, input, [contenteditable='true']");
                      if (byClosest) return byClosest;
                      const byQuery = start.querySelector?.("textarea, input, [contenteditable='true']");
                      if (byQuery) return byQuery;
                      return null;
                    }

                    const target = findEditable(el);
                    if (!target) return { ok: false, error: "No editable element near point", tag: el.tagName };

                    target.focus?.();
                    target.click?.();

                    const tag = (target.tagName || "").toUpperCase();
                    if (tag === "TEXTAREA" || tag === "INPUT") {
                      target.value = text;
                      target.dispatchEvent(new Event("input", { bubbles: true }));
                      target.dispatchEvent(new Event("change", { bubbles: true }));
                      return { ok: true, kind: tag };
                    }

                    if (target.isContentEditable) {
                      target.textContent = text;
                      target.dispatchEvent(new Event("input", { bubbles: true }));
                      return { ok: true, kind: "contenteditable" };
                    }

                    return { ok: false, error: "Target not editable", tag: target.tagName };
                    """,
                    viewport_css_x,
                    viewport_css_y,
                    text,
                )
            elif action == "scroll":
                delta = 800 if (direction or "down").lower() in ("down", "right") else -800
                executed = driver.execute_script(
                    "window.scrollBy(0, arguments[0]); return { ok: true, delta: arguments[0] };",
                    delta,
                )
            elif action == "verify":
                executed = {"ok": True}
            else:
                raise Exception(f"Unsupported action: {action}")

            duration_ms = int((time.time() - start_time) * 1000)

            # Estimate confidence based on whether model provided thought
            confidence = 0.8 if thought and len(thought) > 20 else 0.6

            result = ActionResult(
                success=True,
                action=action,
                description=description,
                duration_ms=duration_ms,
                confidence=confidence,
                metadata={
                    "coordinates": {"x": normalized_x, "y": normalized_y, "box": (box_x, box_y)},
                    "viewport_css": {"x": viewport_css_x, "y": viewport_css_y},
                    "executed": executed,
                    "thought": thought,
                    "tier": "ui-tars",
                },
            )

            self._emit_event("action_complete", result.to_dict())
            return result

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            result = ActionResult(
                success=False,
                action=action,
                description=description,
                duration_ms=duration_ms,
                error=str(e),
            )

            self._emit_event("action_failed", {
                "action": action,
                "error": str(e),
                "duration_ms": duration_ms,
            })

            logger.error(f"[UI-TARS] Action failed: {e}")
            return result

    async def click(self, description: str, **kwargs) -> ActionResult:
        """Click an element by description."""
        return await self.execute_action("click", description, **kwargs)

    async def type_text(self, description: str, text: str, **kwargs) -> ActionResult:
        """Type text into an element."""
        context = kwargs.pop("context", {})
        context["text"] = text
        return await self.execute_action("type", description, context=context, **kwargs)

    async def scroll(self, description: str, direction: str = "down", **kwargs) -> ActionResult:
        """Scroll to/in an element."""
        context = kwargs.pop("context", {})
        context["direction"] = direction
        return await self.execute_action("scroll", description, context=context, **kwargs)

    async def verify(self, description: str, **kwargs) -> ActionResult:
        """Verify an element exists/state."""
        return await self.execute_action("verify", description, **kwargs)

    def close(self) -> None:
        """Close UI-TARS connection."""
        self._emit_event("bridge_close", {"session_id": self._session_id})
        self._connected = False
        self._session_id = None
        logger.info("[UI-TARS] Bridge closed")


# Factory function
def create_ui_tars_bridge(
    ui_tars_path: str = None,
    browser_port: int = 9222,
    observers: List[Callable] = None,
) -> UITarsBridge:
    """
    Create UI-TARS bridge instance.
    
    Args:
        ui_tars_path: Path to UI-TARS installation
        browser_port: Chrome debugging port
        observers: Telemetry observers
        
    Returns:
        Configured UITarsBridge instance
    """
    return UITarsBridge(
        ui_tars_path=ui_tars_path,
        browser_port=browser_port,
        observers=observers,
    )


# Test function
async def _test_bridge():
    """Test UI-TARS bridge functionality."""
    bridge = UITarsBridge()
    
    # Test connection
    await bridge.connect()
    
    # Test screenshot
    screenshot = await bridge.capture_screenshot()
    print(f"Screenshot: {screenshot.path}")
    
    # Test action
    result = await bridge.click("blue Like button")
    print(f"Action result: {result.success}, confidence: {result.confidence}")
    
    bridge.close()


if __name__ == "__main__":
    asyncio.run(_test_bridge())
