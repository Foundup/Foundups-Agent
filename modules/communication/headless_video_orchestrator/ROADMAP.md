# Headless Video Orchestrator - Roadmap

## Phase 0 (Current)
- Scaffolding, docs, and minimal build pipeline (audio overlay + visuals concat).
- Output Shorts (9:16) and longform (16:9) variants.

## Phase 1
- Auto-pull clip candidates from `video_indexer` for visuals.
- Add music metadata (song name/artist) into scheduler templates.
- Add Video Lab menu action to emit unlisted-ready assets.

## Phase 2
- Visual generator integration (Veo3/Sora2) with deterministic prompts.
- Per-track visual style presets (retro MTV, lyric visualizer, abstract loops).

## Phase 3
- AI_overseer autonomous queue (generate -> schedule -> index).
- Telemetry + retry loop for failed builds.
