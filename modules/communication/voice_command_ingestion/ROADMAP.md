# voice_command_ingestion Roadmap (Sprint Plan)

## Sprint 0 - Architecture Lock (COMPLETE)
- [x] Confirm reuse of LiveChat routing (message_processor/message_router)
- [x] Document whisper.cpp vs faster-whisper decision
- [x] Update docs and interfaces

## Sprint 1 - Streaming STT (COMPLETE - 2026-01-02)
Architecture Decision: faster-whisper over whisper.cpp (4x faster, pure Python)
- [x] Implement FasterWhisperSTT with lazy model loading
- [x] Implement stream_audio_to_text() for AudioChunk integration
- [x] VAD filter enabled (auto-skip silence)
- [x] Log latency and confidence scores

## Sprint 2 - Trigger Detection (COMPLETE - 2026-01-02)
- [x] Implement TriggerDetector with regex patterns
- [x] Handle variations: "0102", "zero one zero two", "oh one oh two"
- [x] Extract command text after trigger
- [x] Emit CommandEvent with timestamp and confidence
- [x] Tests passing for all trigger patterns

## Sprint 3 - LiveChat Routing Hook (COMPLETE - 2026-01-03)
- [x] Convert CommandEvent into synthetic livechat message payload
- [x] Route through livechat_router.py (LiveChatVoiceRouter)
- [x] Ensure command handler path is exercised (MessageProcessor)
- [x] Store transcripts in memory/ for PQN (voice_transcripts.jsonl)

## Sprint 4 - Skill Routing (MVP) (PENDING)
- [ ] Map command text to WRE skills (rule-based)
- [ ] One demo command (e.g., "send email", "take screenshot")
- [ ] Emit no_match for unknown commands

## Sprint 5 - End-to-End Soak (PENDING)
- [ ] Run with youtube_live_audio for 30 minutes
- [ ] Monitor memory usage and latency
- [ ] Restart on STT stall
- [ ] Digital twin: Store all transcripts for 012 pattern learning

## Notes
- faster-whisper chosen for 4x speedup and pure Python integration
- Lazy initialization: Model loads on first transcribe() call
- Trigger patterns handle common Whisper misrecognitions of "0102"
