# Video Autonomy Playbook (0102)

**Purpose**: Persist the tightest stack and execution path for 012/0102 to turn 20 years of video into actionable assets (Shorts 9:16, longform 16:9, repurpose/dub), with autonomous orchestration (AI_overseer/0102) and 012 as executor only.

## MTV-Style Headless Channel (RavingANTIFA)
Goal: Use Suno songs to generate continuous music videos (faceless), uploaded and scheduled autonomously.

Occam flow (no new subsystems, only stitching):
1) **Input**: Suno audio files (local library) and minimal metadata (song title/artist).
2) **Visuals**: Generate or reuse visuals via existing generators (Veo3/Sora2) or prebuilt loops.
3) **Assemble**: ffmpeg stitch + audio overlay into final MP4 (Shorts 9:16 or longform 16:9).
4) **Upload**: Use existing YouTube Studio automation to schedule; metadata via FFCPLN content generator.
5) **Index**: Create stub index (scheduler) then full index via video_indexer for search/recall.

Key modules to stitch:
- **Scheduler**: `modules/platform_integration/youtube_shorts_scheduler/src/scheduler.py` supports `ravingantifa` (Edge 9223).
- **Titles/Descriptions**: `modules/platform_integration/youtube_shorts_scheduler/src/content_generator.py` (FFCPLN music templates).
- **Index stub + weave**: `modules/platform_integration/youtube_shorts_scheduler/src/index_weave.py`.
- **Video cache/download**: `modules/ai_intelligence/video_indexer/src/visual_analyzer.py` (yt-dlp cache).
- **Clip/export**: `modules/communication/youtube_shorts/src/clip_exporter.py` + `video_editor.py`.
- **Audio extraction/listing**: `modules/platform_integration/youtube_live_audio/src/youtube_live_audio.py:VideoArchiveExtractor`.

Open gap: direct upload for RavingANTIFA via API is not wired (shorts uploader only supports move2japan/undaodu). Occam path is: manual upload or add a minimal DOM upload step reusing `YouTubeStudioDOM` (future glue).

## Evidence (memory taps)
- main menu: `modules/infrastructure/cli/src/youtube_menu.py` (Shorts gen/scheduler, indexing), `main_menu.py` option 4 Social Media DAE (placeholder).
- indexing: `modules/ai_intelligence/video_indexer/src/*`, `indexing_menu.py` (Gemini-first, Whisper fallback, clip candidates).
- generation: `modules/communication/youtube_shorts/src/shorts_orchestrator.py`, `video_editor.py` (ffmpeg concat/format), clip metadata from `clip_generator.py` (not yet cut/exported).
- training/voice: `video_enhancer.py`, `dataset_builder.py`, `digital_twin/voice_memory.py` (RAG over video transcripts).
 - ravingantifa scheduler: `modules/platform_integration/youtube_shorts_scheduler/src/scheduler.py` (supports RavingANTIFA + index weave).
 - music metadata: `modules/platform_integration/youtube_shorts_scheduler/src/content_generator.py` (FFCPLN music titles/descriptions).

## Decisions (WSP 15 MPS)
- P1: Auto-clip → 9:16 Shorts export → schedule/upload. Reuse clip candidates; wire FFmpeg/OpenCV auto-crop (pattern: SamurAIGPT/AI-Youtube-Shorts-Generator) then `video_editor.ensure_shorts_format` → `youtube_shorts_scheduler`.
- P1: Repurpose/dub/caption pipeline. Use ShortGPT-style chain (transcribe/translate/tts/captions/export) with toggle for 012 voice vs TTS; feed `training_data/*/voice_clips_manifest.jsonl` when present.
- P2: Longform (16:9) builder. case-ai-digital-creator style: script from `video_index` (Gemini transcript/summary), narrate with 012 voice/TTS, assemble B-roll/Sora/Veo frames, add captions.
- P2: Telemetry bridge. AI_overseer consumes video_indexer telemetry to auto-retry P0 failures and fall back to Whisper; surface “retry failed indexes” in menu.
- P3: Channel crawler + search UI. Use YouTubeStudioDOM to list videos; add Chroma multi-collection search in indexing menu for selection.
 - P1 (music channel): Suno song ingest → visuals → audio overlay → unlisted upload → scheduler metadata + index weave.

## Execution wiring (menu-level)
- Add “Video Lab” submenu under YouTube menu:
  - Auto-clip → export → schedule (uses clip candidates → ffmpeg crop/cut → shorts_scheduler).
  - Repurpose/dub/caption (ShortGPT-like, 012 voice toggle).
  - Longform builder (script-from-index + voice + B-roll).
  - Music video builder (Suno audio → visuals → overlay → upload → schedule).
- Social Media DAE hookup: consume Video Lab outputs into post queue; 0102/overseer runs generation, 012 executes publish.

## Next actions (0102 autonomous queue)
1) Implement FFmpeg/OpenCV cutter that takes `clip_generator` output → `video_editor` exporter; smoke-test on one indexed video; schedule via `youtube_shorts_scheduler`.
2) Add repurpose command (translate/dub/caption) with 012 voice flag; validate on a single source video; store artifacts in `memory/video_lab/`.
3) Extend `indexing_menu.py`: add “retry failed indexes” (AI_overseer telemetry), add channel crawler stub.
4) Draft longform POC: script-from-index → TTS/012 voice → B-roll montage; one test upload path.
5) Music video POC (RavingANTIFA): take one Suno track, generate visuals (Veo3/Sora2), overlay audio, upload unlisted, run scheduler to title/describe/schedule + create stub index.
