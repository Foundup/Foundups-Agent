# Voice Command Pipeline - YouTube Live STT MVP

This document describes the MVP implementation for live YouTube audio to local STT
and command execution. It enforces WSP 3 functional distribution and keeps all
speech recognition local (no cloud STT).

## Architecture (Implemented 2026-01-02)

```
Browser (YouTube LIVE playing)
        |
        v
SystemAudioCapture (WASAPI loopback via soundcard)
        |
        v
AudioChunk (float32 @ 16kHz mono)
        |
        v
FasterWhisperSTT (CTranslate2 optimized, 4x faster)
        |
        v
TriggerDetector ("0102" pattern matching)
        |
        v
CommandEvent -> livechat_router -> WRE skills
```

## Architecture Decision: Hybrid Option A

**Chosen**: System audio loopback (Occam's simplest)
- Browser plays YouTube LIVE (already running for livechat DAE)
- WASAPI captures system audio (what speakers play)
- Works with protected/private streams (no auth issues)
- No yt-dlp authentication battles

**Rejected**: yt-dlp stream extraction
- Authentication issues with YouTube rate limiting
- More complex pipeline (yt-dlp + ffmpeg + subprocess management)
- Doesn't work with private/protected streams

## Deep-think gate
Goal (1 sentence):
- Convert YouTube Live audio into local STT events and trigger a single command
  when the token "0102" is spoken.

Minimum modules:
- platform_integration/youtube_live_audio: System audio capture via WASAPI loopback
- communication/voice_command_ingestion: faster-whisper STT + trigger + command events
- communication/livechat: command routing and execution
- infrastructure/wre_core: skill registry and execution entry point

Inputs and outputs:
- youtube_live_audio input: System audio (browser playing YouTube LIVE)
- youtube_live_audio output: Generator of AudioChunk (float32 @ 16kHz mono)
- voice_command_ingestion input: AudioChunk stream
- voice_command_ingestion output: CommandEvent (command string + metadata)

Failure modes (one line each):
- No audio device -> log error and exit
- Audio level too low -> warn user to check volume
- STT backend fails -> lazy reinitialize
- No speech detected -> VAD filters silence automatically
- False trigger -> regex patterns handle Whisper misrecognitions

## Module map (WSP 3)
- platform_integration/youtube_live_audio
  - SystemAudioCapture: WASAPI loopback via soundcard
  - AudioChunk: float32 audio with metadata
  - YouTubeLiveAudioSource: High-level interface

- communication/voice_command_ingestion
  - FasterWhisperSTT: CTranslate2 optimized Whisper
  - TriggerDetector: Regex patterns for "0102" variations
  - VoiceCommandIngestion: Orchestrator class
  - livechat_router: Route CommandEvent to WRE skills

- infrastructure/wre_core
  - Skill registry and safe execution

## STT choice
- **Implemented**: faster-whisper (4x faster than vanilla, pure Python)
- Model sizes: tiny, base (default), small, medium, large-v3
- VAD filter enabled: Automatically skips silence
- Lazy initialization: Model loads on first use

## Trigger grammar
- Trigger patterns recognize variations:
  - "0102" (exact digits)
  - "zero one zero two" (words)
  - "oh one oh two" (common mishearing)
  - "0 1 0 2" (spaced)
  - "01 02" (grouped)
- After trigger, everything in the same chunk is the command

## Command routing reuse (WSP 84)
- Do not create a new orchestrator.
- Convert CommandEvent into a synthetic livechat message payload.
- Route through existing handlers:
  - modules/communication/livechat/src/message_processor.py
  - modules/communication/livechat/src/core/message_router.py

## Logging contract
Each stage emits structured log lines:
- `[AUDIO] Default speaker: {name}`
- `[AUDIO] Loopback device initialized: {name}`
- `[STT] Loading faster-whisper model: {size} on {device}`
- `[STT] '{transcription}'`
- `[TRIGGER] Detected '0102' - Command: '{command}'`

## Sprint Status

### Completed
- [x] Sprint 0: Architecture lock
- [x] Sprint 1: System audio capture (youtube_live_audio)
- [x] Sprint 2: faster-whisper STT (voice_command_ingestion)
- [x] Sprint 3: Trigger detection with pattern variations

### Pending
- [ ] Sprint 4: LiveChat routing hook
- [ ] Sprint 5: Skill routing (MVP)
- [ ] Sprint 6: End-to-end soak test

## Usage

```bash
# Run end-to-end test (play audio in browser first)
python -m modules.platform_integration.youtube_live_audio.scripts.test_live_stt
```

## Non-goals
- No UI
- No cloud STT
- No LLM parsing for commands (rule-based only)
- No multi-language STT in MVP
- No real email sending in MVP

## PQN and digital twin alignment
- Store STT transcripts and command events in module memory for PQN analysis
- These transcripts become the raw training feed for the 0102 digital twin
  profile built from 012 live streams and video archives
