"""
TARS Vision backend stub for future replay via UI-TARS.

Recording not implemented; replay will be wired to UI-TARS vision bridge later.
"""
from ..src.skill import WardrobeSkill
from . import WardrobeBackendBase


class TarsBackend(WardrobeBackendBase):
    def record_session(self, target_url: str, duration_seconds: int = 15):
        raise NotImplementedError("Recording via UI-TARS not implemented. Use Playwright to record.")

    def replay_skill(self, skill: WardrobeSkill) -> None:
        # TODO: implement replay via UI-TARS vision bridge (action router + coordinates)
        raise NotImplementedError("Replay via UI-TARS not yet implemented.")


__all__ = ["TarsBackend"]
