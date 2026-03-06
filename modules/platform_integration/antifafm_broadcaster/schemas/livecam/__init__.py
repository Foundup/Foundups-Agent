"""
Livecam Schema - Multi-camera grid with CamSentinel AI.

Status: PLANNED (Layer 7)
Commands: /cam, /grid, !cam1-4, !pip, !rotate1-4
"""

from typing import List, Optional
from ..base import BaseSchema, SchemaMode, SchemaConfig, OBSSceneConfig
from .. import register_schema, SchemaType


class LivecamSchema(BaseSchema):
    """
    Multi-camera live feed grid with Gemma-based pattern detection.

    Inspired by MIDDLE EAST MULTI-LIVE (YouTube).

    Features (PLANNED):
    - 4-cam grid (2x2 layout)
    - 2-cam split (side-by-side)
    - Single fullscreen (!cam1-4)
    - CamSentinel: Gemma pattern detection (~10ms binary classification)
    - Viewer voting: 51% threshold for camera rotation
    - Camera labels with city + time overlay
    - Picture-in-picture mode

    Mode: OBS (not FFmpeg - requires scene switching)
    """

    NAME = "livecam"
    DISPLAY_NAME = "Live Cam Grid"
    DESCRIPTION = "Multi-camera grid with AI pattern detection"
    MODE = SchemaMode.OBS  # This schema uses OBS scenes, not FFmpeg

    def __init__(self, config: SchemaConfig = None):
        super().__init__(config)
        # Default settings
        defaults = {
            'layout': '4grid',  # 4grid, 2split, single
            'active_cam': 1,    # For single mode
            'pip_main': 1,      # For PiP mode
            'pip_overlay': 2,
            'sentinel_enabled': True,
            'sentinel_interval': 30,  # seconds
            'sentinel_threshold': 0.7,
            'voter_threshold': 0.51,
            'vote_window': 60,  # seconds
        }
        for key, value in defaults.items():
            if key not in self.config.settings:
                self.config.settings[key] = value

    def build_ffmpeg_filter(self) -> str:
        """
        Livecam uses OBS, not FFmpeg filters.
        Returns placeholder filter for fallback.
        """
        return (
            "[1:v]scale=1920:1080,format=yuv420p[bg];"
            "[bg]drawtext=text='Livecam Mode - Use OBS for multi-cam':"
            "fontsize=48:fontcolor=white:"
            "x=(w-text_w)/2:y=(h-text_h)/2:"
            "shadowcolor=black:shadowx=2:shadowy=2[out]"
        )

    def get_obs_scene(self) -> Optional[OBSSceneConfig]:
        """Get OBS scene configuration for current layout."""
        layout = self.config.settings.get('layout', '4grid')

        if layout == '4grid':
            return OBSSceneConfig(
                scene_name="Livecam 4-Grid",
                sources=["CAM 1", "CAM 2", "CAM 3", "CAM 4"],
                transitions={"type": "fade", "duration_ms": 500}
            )
        elif layout == '2split':
            return OBSSceneConfig(
                scene_name="Livecam 2-Split",
                sources=["CAM 1", "CAM 2"],
                transitions={"type": "cut", "duration_ms": 0}
            )
        elif layout == 'single':
            cam_num = self.config.settings.get('active_cam', 1)
            return OBSSceneConfig(
                scene_name=f"Livecam Single CAM {cam_num}",
                sources=[f"CAM {cam_num}"],
                transitions={"type": "fade", "duration_ms": 300}
            )
        elif layout == 'pip':
            main = self.config.settings.get('pip_main', 1)
            overlay = self.config.settings.get('pip_overlay', 2)
            return OBSSceneConfig(
                scene_name=f"Livecam PiP {main}+{overlay}",
                sources=[f"CAM {main}", f"CAM {overlay} (PiP)"],
                transitions={"type": "fade", "duration_ms": 300}
            )

        return None

    def set_layout(self, layout: str) -> None:
        """Set camera layout (4grid, 2split, single, pip)."""
        valid = ['4grid', '2split', 'single', 'pip']
        if layout in valid:
            self.config.settings['layout'] = layout

    def set_active_cam(self, cam_num: int) -> None:
        """Set active camera for single mode (1-4)."""
        if 1 <= cam_num <= 4:
            self.config.settings['active_cam'] = cam_num
            self.config.settings['layout'] = 'single'

    def get_camera_labels(self) -> List[str]:
        """Get configured camera labels."""
        # Future: Load from camera_presets.json
        return [
            "CAM 1 - BEIRUT",
            "CAM 2 - TEL AVIV",
            "CAM 3 - BEIRUT",
            "CAM 4 - JERUSALEM"
        ]


# Register on import
register_schema(SchemaType.LIVECAM, LivecamSchema)
