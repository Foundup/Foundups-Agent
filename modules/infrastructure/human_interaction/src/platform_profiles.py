"""
Platform Profile Loader - Human Interaction Module
==================================================

Loads platform-specific configuration (coordinates, timing, actions) from JSON.

WSP Compliance: WSP 49 (Platform Integration Safety), WSP 3 (Module Organization)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PlatformProfile:
    """Represents a platform's interaction profile."""

    def __init__(self, profile_data: Dict[str, Any]):
        self.platform = profile_data.get("platform", "unknown")
        self.description = profile_data.get("description", "")
        self.iframe = profile_data.get("iframe", {})
        self.actions = profile_data.get("actions", {})
        self.global_timing = profile_data.get("global_timing", {})
        self.error_simulation = profile_data.get("error_simulation", {})
        self.safety_bounds = profile_data.get("safety_bounds", {})

    def get_action(self, action_name: str) -> Optional[Dict[str, Any]]:
        """Get action configuration by name."""
        return self.actions.get(action_name)

    def get_coordinates(self, action_name: str) -> Optional[tuple]:
        """Get base coordinates for an action."""
        action = self.get_action(action_name)
        if action and "coordinates" in action:
            coords = action["coordinates"]
            return (coords["x"], coords["y"])
        return None

    def get_variance(self, action_name: str) -> Optional[tuple]:
        """Get coordinate variance for an action."""
        action = self.get_action(action_name)
        if action and "variance" in action:
            var = action["variance"]
            return (var["x"], var["y"])
        return (0, 0)

    def get_timing(self, action_name: str, timing_type: str) -> Optional[Dict[str, float]]:
        """Get timing configuration for an action."""
        action = self.get_action(action_name)
        if action and "timing" in action:
            return action["timing"].get(timing_type)
        return None

    def requires_iframe(self) -> bool:
        """Check if platform requires iframe switching."""
        return self.iframe.get("required", False)

    def get_iframe_selector(self) -> Optional[str]:
        """Get iframe selector if required."""
        if self.requires_iframe():
            return self.iframe.get("selector")
        return None

    def __repr__(self):
        return f"<PlatformProfile platform={self.platform} actions={len(self.actions)}>"


class PlatformProfileLoader:
    """Loads and caches platform profiles from JSON files."""

    def __init__(self):
        self.profiles_dir = Path(__file__).parent.parent / "platforms"
        self._cache = {}

    def load_profile(self, platform: str) -> PlatformProfile:
        """
        Load platform profile from JSON.

        Args:
            platform: Platform name (e.g., "youtube_chat", "linkedin", "twitter")

        Returns:
            PlatformProfile instance

        Raises:
            FileNotFoundError: If platform JSON doesn't exist
            ValueError: If JSON is invalid
        """
        # Check cache first
        if platform in self._cache:
            return self._cache[platform]

        # Load from file
        profile_path = self.profiles_dir / f"{platform}.json"

        if not profile_path.exists():
            raise FileNotFoundError(
                f"Platform profile not found: {profile_path}\n"
                f"Available platforms: {self.list_available_platforms()}"
            )

        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)

            profile = PlatformProfile(profile_data)
            self._cache[platform] = profile

            logger.info(f"[PROFILE] Loaded platform profile: {platform} ({len(profile.actions)} actions)")
            return profile

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {profile_path}: {e}")

    def list_available_platforms(self) -> list:
        """List all available platform profiles."""
        if not self.profiles_dir.exists():
            return []

        return [
            f.stem for f in self.profiles_dir.glob("*.json")
        ]

    def clear_cache(self):
        """Clear the profile cache (useful for testing)."""
        self._cache.clear()


# Global loader instance
_loader = None

def get_profile_loader() -> PlatformProfileLoader:
    """Get or create global profile loader."""
    global _loader
    if _loader is None:
        _loader = PlatformProfileLoader()
    return _loader


def load_platform_profile(platform: str) -> PlatformProfile:
    """Convenience function to load a platform profile."""
    loader = get_profile_loader()
    return loader.load_profile(platform)
