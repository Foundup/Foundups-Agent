"""
Action Router - Intelligent routing of browser actions to optimal driver

Routes actions with tiered fallback:
- Tier 1: UI-TARS (local vision on LM Studio port 1234) - Fast, private, local
- Tier 2: Gemini Vision (cloud vision API) - Reliable fallback
- Tier 3: Selenium (foundups_selenium) - Fast DOM-based for known selectors
- Tier 3: Playwright (alternative browser automation) - Coming soon

Architecture:
    Vision Actions → Try UI-TARS → Fallback to Gemini → Final fallback to Selenium
    DOM Actions → Selenium/Playwright directly

Environment Variables:
    TARS_API_URL: UI-TARS API endpoint (default: http://127.0.0.1:1234)
    FOUNDUPS_CHROME_PORT: Browser debugging port (default: 9222)
    FOUNDUPS_VISION_ONLY: Force vision-only mode (1/true)
    FOUNDUPS_DISABLE_FALLBACK: Disable driver fallback (1/true)

WSP Compliance:
    - WSP 3: Infrastructure domain
    - WSP 77: AI Overseer integration (routing telemetry)
    - WSP 91: DAEMON observability
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class DriverType(Enum):
    """Available driver types."""
    SELENIUM = "selenium"
    TARS = "tars"  # Tier 1: UI-TARS local vision (LM Studio)
    GEMINI = "gemini"  # Tier 2: Gemini Vision cloud
    VISION = "vision"  # Auto-select best vision (TARS → GEMINI)
    PLAYWRIGHT = "playwright"  # Alternative browser automation
    AUTO = "auto"  # Router decides


@dataclass
class RoutingResult:
    """Result of action routing."""
    success: bool
    driver_used: str
    action: str
    duration_ms: int
    fallback_used: bool = False
    error: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "driver_used": self.driver_used,
            "action": self.action,
            "duration_ms": self.duration_ms,
            "fallback_used": self.fallback_used,
            "error": self.error,
            "result_data": self.result_data,
        }


class ActionRouter:
    """
    Routes browser actions to the optimal driver based on action complexity.
    
    Simple actions (known selectors) → Selenium (fast, reliable)
    Complex actions (vision-based) → UI-TARS (flexible, AI-powered)
    
    Usage:
        router = ActionRouter(profile='youtube_move2japan')
        
        # Router decides which driver
        result = await router.execute('like_comment', {
            'video_id': 'abc123',
            'comment_id': 'xyz789'
        })
        
        # Force specific driver
        result = await router.execute('navigate', {'url': '...'}, driver=DriverType.SELENIUM)
    """

    # Actions that use Selenium (fast, known DOM)
    SELENIUM_ACTIONS = {
        'navigate',
        'click_by_xpath',
        'click_by_id',
        'click_by_css',
        'type_text',
        'get_element_text',
        'wait_for_element',
        'get_page_source',
        'execute_script',
    }

    # Actions that use UI-TARS Vision (complex, dynamic)
    VISION_ACTIONS = {
        'like_comment',
        'click_by_description',
        'find_by_description',
        'fill_form_smart',
        'verify_element_state',
        'scroll_to_element',
        'interact_with_dialog',
    }

    def __init__(
        self,
        profile: str = None,
        selenium_driver: Any = None,
        ui_tars_bridge: Any = None,
        gemini_vision_bridge: Any = None,
        vision_bridge: Any = None,  # Deprecated: use ui_tars_bridge or gemini_vision_bridge
        fallback_enabled: bool = True,
        observers: Optional[List[Callable[[str, Dict[str, Any]], None]]] = None,
        feedback_mode: bool = False,
    ) -> None:
        """
        Initialize action router.

        Args:
            profile: Browser profile name (e.g., 'youtube_move2japan')
            selenium_driver: Pre-initialized FoundUpsDriver (optional)
            ui_tars_bridge: Pre-initialized UITarsBridge (Tier 1, optional)
            gemini_vision_bridge: Pre-initialized GeminiVisionBridge (Tier 2, optional)
            vision_bridge: Deprecated - use ui_tars_bridge or gemini_vision_bridge
            fallback_enabled: Allow fallback to other driver on failure
            observers: Telemetry observers for AI Overseer
            feedback_mode: Enable 012 human-in-the-loop verification
        """
        self.profile = profile
        self._selenium_driver = selenium_driver
        self._ui_tars_bridge = ui_tars_bridge
        self._gemini_vision_bridge = gemini_vision_bridge or vision_bridge  # Backward compat
        self._vision_bridge = vision_bridge  # Deprecated, kept for compat
        # Allow global override to disable fallback (vision-first without Selenium backstop)
        env_no_fallback = os.getenv("FOUNDUPS_DISABLE_FALLBACK") or os.getenv("ACTION_ROUTER_NO_FALLBACK")
        if env_no_fallback and str(env_no_fallback).lower() in {"1", "true", "yes"}:
            fallback_enabled = False
        self.fallback_enabled = fallback_enabled
        env_vision_only = os.getenv("FOUNDUPS_VISION_ONLY") or os.getenv("ACTION_ROUTER_VISION_ONLY")
        self._vision_only = bool(env_vision_only and str(env_vision_only).lower() in {"1", "true", "yes"})
        self.feedback_mode = feedback_mode
        self._observers = list(observers or [])
        self._initialized = False
        
        # Routing metrics
        self._routing_stats = {
            'selenium_calls': 0,
            'tars_calls': 0,  # Tier 1: Local vision
            'gemini_calls': 0,  # Tier 2: Cloud vision
            'vision_calls': 0,  # Legacy: Combined vision calls
            'playwright_calls': 0,
            'fallbacks': 0,
            'successes': 0,
            'failures': 0,
        }

        # Pattern learner for V6 optimization (lazy init)
        self._pattern_learner = None

        logger.info(f"[ROUTER] Initialized with profile={profile}, fallback={fallback_enabled}, feedback={feedback_mode}")

    def _emit_event(self, event: str, payload: Dict[str, Any]) -> None:
        """Emit telemetry event to observers."""
        payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
        for observer in self._observers:
            try:
                observer(event, payload)
            except Exception as e:
                logger.warning(f"[ROUTER] Observer error: {e}")

    async def _ensure_selenium(self) -> Any:
        """Ensure Selenium driver is available."""
        if self._selenium_driver is None:
            try:
                # Check if connecting to existing Chrome via port (test/dev mode)
                port_env = os.getenv("FOUNDUPS_CHROME_PORT") or os.getenv("BROWSER_DEBUG_PORT")
                port_val = None
                if port_env:
                    try:
                        port_val = int(port_env)
                    except ValueError:
                        logger.warning(f"[ROUTER] Invalid port in FOUNDUPS_CHROME_PORT/BROWSER_DEBUG_PORT: {port_env}")

                if port_val:
                    browser_type_env = (
                        os.getenv("FOUNDUPS_BROWSER_TYPE")
                        or os.getenv("ACTION_ROUTER_BROWSER_TYPE")
                        or os.getenv("BROWSER_TYPE")
                        or ""
                    ).strip().lower()
                    edge_port_env = os.getenv("FOUNDUPS_EDGE_PORT") or os.getenv("EDGE_DEBUG_PORT") or "9223"
                    try:
                        edge_port = int(str(edge_port_env).strip())
                    except ValueError:
                        edge_port = 9223

                    use_edge = browser_type_env in {"edge", "msedge"} or port_val == edge_port
                    if browser_type_env and (browser_type_env in {"edge", "msedge"}) and port_val != edge_port:
                        logger.warning(
                            f"[ROUTER] Browser type=Edge but port={port_val} (expected {edge_port}); attempting Edge attach anyway"
                        )
                    if browser_type_env and (browser_type_env in {"chrome", "chromium"}) and port_val == edge_port:
                        logger.warning(
                            f"[ROUTER] Browser type=Chrome but port={port_val} matches Edge port; forcing Edge attach"
                        )

                    devtools_version = self._probe_devtools_version(port_val)
                    if devtools_version is not None:
                        devtools_is_edge = self._devtools_is_edge(devtools_version)
                        if use_edge and not devtools_is_edge:
                            raise RuntimeError(
                                f"DevTools port {port_val} is not Edge (browser={devtools_version.get('Browser')})"
                            )
                        if not use_edge and devtools_is_edge:
                            raise RuntimeError(
                                f"DevTools port {port_val} is Edge (browser={devtools_version.get('Browser')})"
                            )

                    if use_edge:
                        from selenium import webdriver
                        from selenium.webdriver.edge.options import Options as EdgeOptions

                        edge_options = EdgeOptions()
                        edge_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port_val}")
                        edge_driver = webdriver.Edge(options=edge_options)
                        self._selenium_driver = self._wrap_edge_with_telemetry(edge_driver, port_val)
                        logger.info(f"[ROUTER] Selenium driver connected to existing Edge (port={port_val})")
                    else:
                        # Port-based connection (test/dev): Create driver directly
                        from modules.infrastructure.foundups_selenium.src.foundups_driver import FoundUpsDriver
                        self._selenium_driver = FoundUpsDriver(
                            profile_dir=f"modules/platform_integration/browser_profiles/{self.profile}/chrome" if self.profile else None,
                            stealth_mode=False,  # Turn off stealth to avoid unsupported options when attaching
                            port=port_val,
                        )
                        logger.info(f"[ROUTER] Selenium driver connected to existing Chrome (port={port_val})")
                else:
                    # Profile-based connection (production): Use BrowserManager singleton
                    from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
                    browser_manager = get_browser_manager()
                    if not self.profile:
                        logger.warning("[ROUTER] No profile specified, using default")
                        self.profile = "default"
                    self._selenium_driver = browser_manager.get_browser('chrome', self.profile)
                    logger.info(f"[ROUTER] Selenium driver from BrowserManager (profile={self.profile})")
            except Exception as e:
                logger.warning(f"[ROUTER] Selenium driver not available: {e}")
                return None
        return self._selenium_driver

    @staticmethod
    def _probe_devtools_version(port: int) -> Optional[Dict[str, Any]]:
        """Fetch DevTools /json/version payload for browser identity checks."""
        try:
            from urllib.request import urlopen
            import json

            with urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1.0) as resp:
                payload = resp.read().decode("utf-8", errors="replace")
            return json.loads(payload)
        except Exception as exc:
            logger.debug(f"[ROUTER] DevTools preflight skipped on port {port}: {exc}")
            return None

    @staticmethod
    def _devtools_is_edge(version_payload: Dict[str, Any]) -> bool:
        """Return True when DevTools payload indicates an Edge browser."""
        user_agent = (version_payload.get("User-Agent") or version_payload.get("userAgent") or "")
        browser = (version_payload.get("Browser") or "")
        combined = f"{user_agent} {browser}".lower()
        return ("edg" in combined) or ("edge" in combined)

    def _wrap_edge_with_telemetry(self, driver: Any, port: int) -> Any:
        """Attach Edge driver to FoundUps telemetry stream using an event shim."""
        try:
            from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
        except Exception as exc:
            logger.debug(f"[ROUTER] Edge telemetry shim unavailable: {exc}")
            return driver

        observer = None
        browser_key = f"edge_{self.profile or f'port_{port}'}"
        try:
            from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
            browser_manager = get_browser_manager()
            observer = browser_manager._get_observer(browser_key)
        except Exception as exc:
            logger.warning(f"[ROUTER] Edge telemetry observer unavailable: {exc}")
            return driver

        if observer is None:
            return driver

        def emit(event: str, payload: Optional[Dict[str, Any]] = None) -> None:
            data = dict(payload or {})
            data.setdefault("browser", "edge")
            data.setdefault("port", port)
            data.setdefault("browser_key", browser_key)
            try:
                observer(event, data)
            except Exception:
                pass

        def describe_element(element: Any) -> Dict[str, Any]:
            try:
                return {
                    "tag": getattr(element, "tag_name", None),
                    "id": element.get_attribute("id"),
                    "class": element.get_attribute("class"),
                }
            except Exception:
                return {}

        def script_summary(script: Any) -> str:
            if script is None:
                return ""
            summary = str(script).replace("\n", " ")
            if len(summary) > 160:
                summary = summary[:160] + "..."
            return summary

        class EdgeTelemetryListener(AbstractEventListener):
            def before_navigate_to(self, url: str, driver_obj: Any) -> None:
                emit("navigate_start", {"url": url})

            def after_navigate_to(self, url: str, driver_obj: Any) -> None:
                emit("navigate_done", {"url": url})

            def before_click(self, element: Any, driver_obj: Any) -> None:
                emit("click_start", describe_element(element))

            def after_click(self, element: Any, driver_obj: Any) -> None:
                emit("click_done", describe_element(element))

            def before_execute_script(self, script: Any, driver_obj: Any) -> None:
                emit("execute_script_start", {"script": script_summary(script)})

            def after_execute_script(self, script: Any, driver_obj: Any) -> None:
                emit("execute_script_done", {"script": script_summary(script)})

            def on_exception(self, exception: Exception, driver_obj: Any) -> None:
                current_url = None
                try:
                    current_url = driver_obj.current_url
                except Exception:
                    current_url = None
                emit("exception", {"error": str(exception), "url": current_url})

        try:
            wrapped = EventFiringWebDriver(driver, EdgeTelemetryListener())
            logger.info(f"[ROUTER] Edge telemetry shim attached (key={browser_key})")
            return wrapped
        except Exception as exc:
            logger.warning(f"[ROUTER] Edge telemetry shim failed: {exc}")
            return driver

    async def _ensure_ui_tars(self) -> Any:
        """Ensure UI-TARS Bridge (Tier 1 local vision) is available."""
        if self._ui_tars_bridge is None:
            try:
                # Check if LM Studio is running on port 1234
                tars_api_url = os.getenv("TARS_API_URL", "http://127.0.0.1:1234").rstrip("/")
                if tars_api_url.endswith("/v1"):
                    tars_api_url = tars_api_url[:-3]

                # Lightweight health check so we fail-fast and log to AI_overseer.
                try:
                    from urllib.request import urlopen
                    with urlopen(f"{tars_api_url}/v1/models", timeout=2) as resp:
                        if getattr(resp, "status", 200) != 200:
                            raise RuntimeError(f"LM Studio returned status {getattr(resp, 'status', 'unknown')}")
                except Exception as e:
                    self._emit_event("tars_unreachable", {"base_url": tars_api_url, "error": str(e)})
                    logger.warning(f"[ROUTER] LM Studio not reachable at {tars_api_url}: {e}")
                    return None

                # Lazy import
                from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge

                # Get browser port for UI-TARS to connect
                browser_port = 9222
                port_env = os.getenv("FOUNDUPS_CHROME_PORT") or os.getenv("BROWSER_DEBUG_PORT")
                if port_env:
                    try:
                        browser_port = int(port_env)
                    except ValueError:
                        pass

                self._ui_tars_bridge = UITarsBridge(
                    browser_port=browser_port,
                    observers=self._observers,
                )
                await self._ui_tars_bridge.connect()
                logger.info(f"[ROUTER] UI-TARS bridge initialized (Tier 1, port={browser_port})")
            except Exception as e:
                logger.warning(f"[ROUTER] UI-TARS bridge not available (will fallback to Gemini): {e}")
                return None
        return self._ui_tars_bridge

    async def _ensure_gemini_vision(self) -> Any:
        """Ensure Gemini Vision Bridge (Tier 2 cloud fallback) is available."""
        if self._gemini_vision_bridge is None:
            try:
                # Ensure Selenium is available first (required for Gemini Bridge execution)
                driver = await self._ensure_selenium()
                if not driver:
                    logger.warning("[ROUTER] Cannot init Gemini Bridge: Selenium driver missing")
                    return None

                # Lazy import
                from modules.infrastructure.foundups_vision.src.gemini_vision_bridge import GeminiVisionBridge

                self._gemini_vision_bridge = GeminiVisionBridge(driver, feedback_mode=self.feedback_mode)
                await self._gemini_vision_bridge.connect()
                logger.info(f"[ROUTER] Gemini Vision bridge initialized (Tier 2, feedback_mode={self.feedback_mode})")
            except Exception as e:
                logger.warning(f"[ROUTER] Gemini Vision bridge not available: {e}")
                return None
        return self._gemini_vision_bridge

    async def _ensure_vision(self) -> Any:
        """
        Ensure vision bridge is available with tiered fallback.

        Tier 1: UI-TARS (local, fast, private) → LM Studio port 1234
        Tier 2: Gemini Vision (cloud fallback) → Google AI API

        Returns the best available vision bridge.
        """
        # Try Tier 1: UI-TARS first (local model)
        ui_tars = await self._ensure_ui_tars()
        if ui_tars:
            return ui_tars

        # Fallback to Tier 2: Gemini Vision (cloud)
        logger.info("[ROUTER] UI-TARS unavailable, falling back to Gemini Vision (Tier 2)")
        gemini = await self._ensure_gemini_vision()
        if gemini:
            return gemini

        logger.warning("[ROUTER] No vision bridge available (both UI-TARS and Gemini failed)")
        return None

    def get_driver_for_action(self, action: str) -> DriverType:
        """
        Determine which driver should handle an action.
        
        Args:
            action: Action name
            
        Returns:
            DriverType for the action
        """
        # Vision-only mode: keep Selenium only for navigate bootstrapping
        if getattr(self, "_vision_only", False):
            if action == "navigate":
                return DriverType.SELENIUM
            return DriverType.VISION

        if action in self.SELENIUM_ACTIONS:
            return DriverType.SELENIUM
        elif action in self.VISION_ACTIONS:
            return DriverType.VISION
        else:
            # Unknown action - default to vision (more flexible)
            logger.debug(f"[ROUTER] Unknown action '{action}', defaulting to vision")
            return DriverType.VISION

    async def execute(
        self,
        action: str,
        params: Dict[str, Any],
        driver: DriverType = DriverType.AUTO,
        timeout: int = 90,  # Increased for vision model inference (7B model on CPU)
    ) -> RoutingResult:
        """
        Execute an action via the appropriate driver.

        Args:
            action: Action name (e.g., 'like_comment', 'navigate')
            params: Action parameters
            driver: Force specific driver or AUTO for router decision
            timeout: Max seconds for action (default 90s for vision models)
            
        Returns:
            RoutingResult with outcome
        """
        start_time = time.time()
        
        # Determine driver
        if driver == DriverType.AUTO:
            driver = self.get_driver_for_action(action)
        # In vision-only mode, force everything except navigate to Vision
        if getattr(self, "_vision_only", False) and action != "navigate":
            driver = DriverType.VISION
        
        self._emit_event("action_routed", {
            "action": action,
            "driver": driver.value,
            "params": params,
        })
        
        # Try primary driver
        result = await self._execute_with_driver(action, params, driver, timeout)
        
        # Fallback if enabled and failed
        if (
            not result.success
            and self.fallback_enabled
            and not getattr(self, "_vision_only", False)
        ):
            fallback_driver = DriverType.VISION if driver == DriverType.SELENIUM else DriverType.SELENIUM
            
            logger.info(f"[ROUTER] Primary driver failed, trying fallback: {fallback_driver.value}")
            self._routing_stats['fallbacks'] += 1
            
            result = await self._execute_with_driver(action, params, fallback_driver, timeout)
            result.fallback_used = True
        
        # Update stats
        if result.success:
            self._routing_stats['successes'] += 1
        else:
            self._routing_stats['failures'] += 1

        result.duration_ms = int((time.time() - start_time) * 1000)

        # Record pattern for learning (Sprint V6)
        self._record_pattern(action, params, result)

        self._emit_event("action_complete", result.to_dict())

        return result

    async def _execute_with_driver(
        self,
        action: str,
        params: Dict[str, Any],
        driver: DriverType,
        timeout: int,
    ) -> RoutingResult:
        """Execute action with specific driver."""
        try:
            if driver == DriverType.SELENIUM:
                return await self._execute_selenium(action, params, timeout)
            else:
                return await self._execute_vision(action, params, timeout)
        except Exception as e:
            logger.error(f"[ROUTER] Driver {driver.value} failed: {e}")
            return RoutingResult(
                success=False,
                driver_used=driver.value,
                action=action,
                duration_ms=0,
                error=str(e),
            )

    async def _execute_selenium(
        self,
        action: str,
        params: Dict[str, Any],
        timeout: int,
    ) -> RoutingResult:
        """Execute action via Selenium."""
        driver = await self._ensure_selenium()
        if driver is None:
            return RoutingResult(
                success=False,
                driver_used="selenium",
                action=action,
                duration_ms=0,
                error="Selenium driver not available",
            )
        
        self._routing_stats['selenium_calls'] += 1
        
        try:
            # Map action to Selenium method
            if action == 'navigate':
                driver.get(params.get('url'))
                success = True
            elif action == 'click_by_xpath':
                from selenium.webdriver.common.by import By
                element = driver.find_element(By.XPATH, params.get('xpath'))
                element.click()
                success = True
            elif action == 'click_by_id':
                from selenium.webdriver.common.by import By
                element = driver.find_element(By.ID, params.get('id'))
                element.click()
                success = True
            elif action == 'type_text':
                from selenium.webdriver.common.by import By
                element = driver.find_element(By.XPATH, params.get('xpath'))
                element.send_keys(params.get('text'))
                success = True
            elif action == 'get_element_text':
                from selenium.webdriver.common.by import By
                element = driver.find_element(By.XPATH, params.get('xpath'))
                return RoutingResult(
                    success=True,
                    driver_used="selenium",
                    action=action,
                    duration_ms=0,
                    result_data={"text": element.text},
                )
            else:
                # Unsupported action for Selenium
                return RoutingResult(
                    success=False,
                    driver_used="selenium",
                    action=action,
                    duration_ms=0,
                    error=f"Selenium does not support action: {action}",
                )
            
            return RoutingResult(
                success=success,
                driver_used="selenium",
                action=action,
                duration_ms=0,
            )
            
        except Exception as e:
            return RoutingResult(
                success=False,
                driver_used="selenium",
                action=action,
                duration_ms=0,
                error=str(e),
            )

    async def _execute_vision(
        self,
        action: str,
        params: Dict[str, Any],
        timeout: int,
    ) -> RoutingResult:
        """
        Execute action via vision bridge with tiered fallback.

        Attempts Tier 1 (UI-TARS) first, falls back to Tier 2 (Gemini) if unavailable.
        """
        bridge = await self._ensure_vision()
        if bridge is None:
            return RoutingResult(
                success=False,
                driver_used="vision",
                action=action,
                duration_ms=0,
                error="Vision bridge not available (both UI-TARS and Gemini failed)",
            )

        # Detect which tier is actually being used
        driver_tier = "vision"  # Generic fallback
        if bridge == self._ui_tars_bridge:
            driver_tier = "tars"
            self._routing_stats['tars_calls'] += 1
        elif bridge == self._gemini_vision_bridge:
            driver_tier = "gemini"
            self._routing_stats['gemini_calls'] += 1
        self._routing_stats['vision_calls'] += 1  # Legacy counter

        try:
            # Map action to Vision method
            description = params.get('description', '')
            context = {k: v for k, v in params.items() if k != 'description'}

            if action == 'like_comment':
                description = f"thumbs up Like button on comment {params.get('comment_id', '')}"
            elif action == 'click_by_description':
                description = params.get('description', 'button')
            elif action == 'find_by_description':
                description = params.get('description', 'element')
            elif action == 'scroll_to_element':
                description = f"scroll to {params.get('description', 'element')}"

            # Ensure Selenium driver is available for screenshots
            if self._selenium_driver is None:
                await self._ensure_selenium()

            result = await bridge.execute_action(
                action=action.replace('_by_description', '').replace('_comment', ''),
                description=description,
                context=context,
                timeout=timeout,
                driver=self._selenium_driver,  # Pass driver for screenshots/clicks
            )

            return RoutingResult(
                success=result.success,
                driver_used=driver_tier,
                action=action,
                duration_ms=result.duration_ms,
                result_data={
                    "confidence": result.confidence,
                    "screenshot": result.screenshot_before,
                    "tier": driver_tier,
                },
                error=result.error,
            )

        except Exception as e:
            return RoutingResult(
                success=False,
                driver_used=driver_tier,
                action=action,
                duration_ms=0,
                error=str(e),
            )

    def get_stats(self) -> Dict[str, int]:
        """Get routing statistics."""
        return self._routing_stats.copy()

    def get_pattern_recommendation(self, action: str) -> DriverType:
        """
        Get pattern-based routing recommendation.

        Uses historical success rates to recommend optimal driver.
        This is Sprint A6 pattern optimization.

        Args:
            action: Action name

        Returns:
            Recommended DriverType
        """
        # Default to rule-based routing if no pattern data
        if self._routing_stats['successes'] + self._routing_stats['failures'] < 10:
            return self.get_driver_for_action(action)

        # Pattern-based: If we have good success rate, stick with current routing
        success_rate = self._routing_stats['successes'] / (
            self._routing_stats['successes'] + self._routing_stats['failures']
        )

        # If success rate > 80%, use current routing
        if success_rate > 0.8:
            return self.get_driver_for_action(action)

        # If success rate < 50%, try opposite driver
        if success_rate < 0.5:
            default_driver = self.get_driver_for_action(action)
            opposite = DriverType.VISION if default_driver == DriverType.SELENIUM else DriverType.SELENIUM
            logger.info(f"[ROUTER] Low success rate ({success_rate:.1%}), recommending opposite driver: {opposite.value}")
            return opposite

        # Otherwise, use default
        return self.get_driver_for_action(action)

    def _get_pattern_learner(self):
        """Lazy initialize pattern learner (Sprint V6)."""
        if self._pattern_learner is None:
            try:
                from modules.infrastructure.foundups_vision.src.action_pattern_learner import get_learner
                self._pattern_learner = get_learner()
            except Exception as e:
                logger.warning(f"[ROUTER] Pattern learner unavailable: {e}")
                self._pattern_learner = False  # Mark as unavailable
        return self._pattern_learner if self._pattern_learner is not False else None

    def _record_pattern(self, action: str, params: Dict[str, Any], result: RoutingResult) -> None:
        """Record action pattern for learning (Sprint V6)."""
        learner = self._get_pattern_learner()
        if learner is None:
            return

        try:
            # Determine platform from params or action context
            platform = params.get('platform', 'unknown')

            if result.success:
                learner.record_success(
                    action=action,
                    platform=platform,
                    driver=result.driver_used,
                    params=params,
                    duration_ms=result.duration_ms,
                )
            else:
                learner.record_failure(
                    action=action,
                    platform=platform,
                    driver=result.driver_used,
                    params=params,
                )
        except Exception as e:
            logger.debug(f"[ROUTER] Pattern recording failed: {e}")

    def close(self) -> None:
        """Close all drivers."""
        if self._selenium_driver:
            try:
                self._selenium_driver.quit()
            except Exception:
                pass
        
        if self._vision_bridge:
            try:
                self._vision_bridge.close()
            except Exception:
                pass
        
        logger.info(f"[ROUTER] Closed. Stats: {self._routing_stats}")


# Factory function
def create_action_router(
    profile: str = None,
    fallback_enabled: bool = True,
) -> ActionRouter:
    """
    Create action router instance.
    
    Args:
        profile: Browser profile name
        fallback_enabled: Allow fallback between drivers
        
    Returns:
        Configured ActionRouter instance
    """
    return ActionRouter(profile=profile, fallback_enabled=fallback_enabled)


# Test function
async def _test_router():
    """Test action router functionality."""
    router = ActionRouter(profile='youtube_move2japan')
    
    # Test action classification
    print(f"navigate -> {router.get_driver_for_action('navigate')}")
    print(f"like_comment -> {router.get_driver_for_action('like_comment')}")
    
    # Test execution (will use simulated responses)
    result = await router.execute('like_comment', {
        'video_id': 'test123',
        'comment_id': 'comment456',
    })
    
    print(f"Result: success={result.success}, driver={result.driver_used}")
    print(f"Stats: {router.get_stats()}")
    
    router.close()


if __name__ == "__main__":
    asyncio.run(_test_router())
