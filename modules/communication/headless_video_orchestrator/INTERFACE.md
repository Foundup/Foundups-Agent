# Headless Video Orchestrator - Interface

## Public API

### `HeadlessVideoOrchestrator`

```python
from modules.communication.headless_video_orchestrator.src.orchestrator import (
    HeadlessVideoOrchestrator,
    MusicVideoRequest,
)

req = MusicVideoRequest(
    audio_path="data/suno/track_01.mp3",
    visual_paths=["memory/video_lab/visuals/v1.mp4"],
    aspect="shorts",
    add_transitions=False,
    loop_video=False,
)

out = HeadlessVideoOrchestrator().build_music_video(req)
print(out.output_path)
```

### `MusicVideoRequest`

| Field | Type | Description |
| --- | --- | --- |
| `audio_path` | `str` | Path to audio file (Suno output). |
| `visual_paths` | `List[str]` | One or more MP4 clips to stitch. |
| `output_dir` | `str` | Output folder (default `memory/video_lab/music_videos`). |
| `aspect` | `str` | `shorts`, `landscape`, or `raw`. |
| `add_transitions` | `bool` | Add crossfades between clips. |
| `loop_video` | `bool` | Loop visuals to cover audio duration. |

### `MusicVideoOutput`

| Field | Type | Description |
| --- | --- | --- |
| `output_path` | `str` | Path to the final MP4. |
| `formatted_path` | `Optional[str]` | Path to formatted output (if applied). |
| `combined_visual_path` | `Optional[str]` | Path to stitched visuals (if used). |

## Error Handling
Raises `MusicVideoBuildError` for missing files, ffmpeg failures, or invalid inputs.

## Optional OSS Adapter

```python
from modules.communication.headless_video_orchestrator.src.oss_adapters import (
    run_ai_shorts_generator,
)

out_path = run_ai_shorts_generator(input_ref="https://youtu.be/VIDEO_ID")
```
