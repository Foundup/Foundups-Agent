# voice_command_ingestion Interface

## STTEvent
```python
STTEvent(
    text: str,           # Transcribed text
    is_final: bool,      # Always True for faster-whisper
    start_ms: int,       # Start time in milliseconds
    end_ms: int,         # End time in milliseconds
    confidence: float,   # Confidence score (0-1)
)
```

## CommandEvent
```python
CommandEvent(
    command: str,           # Command text after trigger
    raw_text: str,          # Full transcription
    trigger_detected: bool, # Always True when emitted
    timestamp_iso: str,     # ISO timestamp
    confidence: float,      # STT confidence
)
```

## FasterWhisperSTT
```python
stt = FasterWhisperSTT(
    model_size: str = "base",      # tiny, base, small, medium, large-v3
    device: str = "cpu",           # cpu or cuda
    compute_type: str = "int8",    # int8, float16, float32
)
```

### transcribe
```python
transcribe(audio: np.ndarray, sample_rate: int = 16000) -> Optional[STTEvent]
```
Transcribe audio chunk to text.

### transcribe_stream
```python
transcribe_stream(audio_chunks: Iterable[np.ndarray], sample_rate: int = 16000) -> Generator[STTEvent, None, None]
```
Transcribe streaming audio chunks.

## TriggerDetector
```python
detector = TriggerDetector(trigger_token: str = "0102")
```

### detect
```python
detect(text: str) -> tuple[bool, str, str]
```
Returns `(trigger_found, command_after_trigger, full_text)`.

Recognizes patterns:
- `0102` (exact digits)
- `zero one zero two` (words)
- `oh one oh two` (common mishearing)
- `0 1 0 2` (spaced)
- `01 02` (grouped)

## VoiceCommandIngestion
```python
ingestion = VoiceCommandIngestion(
    trigger_token: str = "0102",
    stt_backend: str = "faster_whisper",
    command_window_seconds: int = 5,
    model_size: str = "base",
    device: str = "cpu",
)
```

### transcribe_audio
```python
transcribe_audio(audio: np.ndarray, sample_rate: int = 16000) -> Optional[STTEvent]
```
Transcribe a single audio chunk.

### stream_to_text
```python
stream_to_text(audio_stream: Iterable[bytes]) -> Iterator[STTEvent]
```
Convert PCM16 audio chunks into streaming STT events.

### stream_audio_to_text
```python
stream_audio_to_text(audio_chunks: Iterable[np.ndarray]) -> Iterator[STTEvent]
```
Convert float32 audio chunks into STT events. **Preferred interface.**

### detect_commands
```python
detect_commands(events: Iterable[STTEvent]) -> Iterator[CommandEvent]
```
Detect trigger tokens and emit command events.

### run
```python
run(audio_stream: Iterable[bytes]) -> Iterator[CommandEvent]
```
End-to-end pipeline: PCM16 bytes -> STT -> trigger -> commands.

### run_on_audio_chunks
```python
run_on_audio_chunks(audio_chunks: Iterable[np.ndarray]) -> Iterator[CommandEvent]
```
End-to-end pipeline for float32 audio. **Preferred interface.**

### process_single_chunk
```python
process_single_chunk(audio: np.ndarray) -> tuple[Optional[STTEvent], Optional[CommandEvent]]
```
Process single chunk and check for trigger. Convenience method.

## Convenience Function
```python
get_voice_ingestion(
    trigger_token: str = "0102",
    model_size: str = "base",
    device: str = "cpu"
) -> VoiceCommandIngestion
```

## LiveChat Routing (Sprint 3)

### LiveChatVoiceRouter
```python
router = LiveChatVoiceRouter(
    identity: Optional[LiveChatIdentity] = None,
    message_processor: Optional[MessageProcessor] = None,
)
```

Routes voice commands through livechat MessageProcessor.

### route_command_event
```python
route_command_event(
    event: CommandEvent,
    router: Optional[LiveChatVoiceRouter] = None,
    store_for_pqn: bool = True,
) -> Optional[Dict[str, Any]]
```
Main Sprint 3 integration point. Routes CommandEvent through livechat infrastructure
and stores transcript for PQN learning.

### store_transcript_for_pqn
```python
store_transcript_for_pqn(
    raw_text: str,
    command: str,
    confidence: float = 1.0,
    timestamp_iso: Optional[str] = None,
) -> None
```
Store voice transcript in `memory/voice_transcripts.jsonl` for PQN pattern learning.

### get_voice_router
```python
get_voice_router() -> LiveChatVoiceRouter
```
Get or create singleton voice router instance.

## Notes
- Uses faster-whisper (CTranslate2 optimized, 4x faster)
- Lazy model loading (loads on first use)
- VAD filter enabled (skips silence automatically)
- Route CommandEvent into LiveChat command handling
- PQN transcripts stored in `memory/voice_transcripts.jsonl`
