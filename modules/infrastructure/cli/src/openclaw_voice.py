"""
OpenClaw Voice REPL - Talk to 0102 with your headset.

STT chain:  faster-whisper (local) -> speech_recognition/Google (cloud) -> keyboard fallback
TTS chain:  edge-tts (neural) -> pyttsx3 (local SAPI5) -> print-only fallback

Usage:
    python -m modules.infrastructure.cli.src.openclaw_voice
    python main.py --voice

WSP Compliance:
    WSP 73: Partner (012 voice) -> Principal (OpenClawDAE) -> Associates (domain DAEs)
    WSP 84: Reuses FasterWhisperSTT from voice_command_ingestion
"""

import asyncio
import io
import logging
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# STT Backends (degradation chain)
# ---------------------------------------------------------------------------

class WhisperSTTBackend:
    """Primary STT: faster-whisper (local, no internet)."""

    name = "faster-whisper"

    def __init__(self, model_size: str = "base"):
        self._stt = None
        self._model_size = model_size

    def available(self) -> bool:
        try:
            from modules.communication.voice_command_ingestion.src.voice_command_ingestion import (
                FasterWhisperSTT,
            )
            self._stt = FasterWhisperSTT(model_size=self._model_size)
            return True
        except Exception:
            return False

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
        if self._stt is None:
            return None
        event = self._stt.transcribe(audio, sample_rate)
        return event.text if event and event.text else None


class GoogleSTTBackend:
    """Backup STT: speech_recognition + Google (needs internet)."""

    name = "Google Speech"

    def __init__(self):
        self._recognizer = None

    def available(self) -> bool:
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            return True
        except ImportError:
            return False

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
        if self._recognizer is None:
            return None
        try:
            import speech_recognition as sr
            # Convert float32 numpy to AudioData
            pcm = (audio * 32767).astype(np.int16).tobytes()
            audio_data = sr.AudioData(pcm, sample_rate, 2)
            return self._recognizer.recognize_google(audio_data)
        except Exception as exc:
            logger.debug("[STT-GOOGLE] Recognition failed: %s", exc)
            return None


# ---------------------------------------------------------------------------
# TTS Backends (degradation chain)
# ---------------------------------------------------------------------------

class EdgeTTSBackend:
    """Primary TTS: Microsoft Edge neural voices (needs internet)."""

    name = "Edge TTS"

    def __init__(self, voice: str = "en-US-GuyNeural"):
        self._voice = voice

    def available(self) -> bool:
        try:
            import edge_tts  # noqa: F401
            import sounddevice  # noqa: F401
            import soundfile  # noqa: F401
            return True
        except ImportError:
            return False

    def speak(self, text: str) -> bool:
        try:
            return asyncio.run(self._speak_async(text))
        except Exception as exc:
            logger.debug("[TTS-EDGE] Speak failed: %s", exc)
            return False

    async def _speak_async(self, text: str) -> bool:
        import edge_tts
        import sounddevice as sd
        import soundfile as sf

        communicate = edge_tts.Communicate(text, self._voice)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]

        if not audio_bytes:
            return False

        # edge-tts returns MP3; decode via soundfile
        buf = io.BytesIO(audio_bytes)
        data, sample_rate = sf.read(buf)
        sd.play(data, sample_rate)
        sd.wait()
        return True


class Pyttsx3TTSBackend:
    """Backup TTS: pyttsx3 local SAPI5 (offline, robotic)."""

    name = "pyttsx3"

    def __init__(self):
        self._engine = None

    def available(self) -> bool:
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 185)
            self._engine.setProperty("volume", 0.9)
            return True
        except Exception:
            return False

    def speak(self, text: str) -> bool:
        if self._engine is None:
            return False
        try:
            self._engine.say(text)
            self._engine.runAndWait()
            return True
        except Exception as exc:
            logger.debug("[TTS-PYTTSX3] Speak failed: %s", exc)
            return False


# ---------------------------------------------------------------------------
# Microphone capture (sounddevice)
# ---------------------------------------------------------------------------

def record_until_silence(
    sample_rate: int = 16000,
    silence_threshold: float = 0.01,
    silence_duration: float = 1.5,
    max_duration: float = 30.0,
) -> Optional[np.ndarray]:
    """Record from microphone until silence detected.

    Returns float32 mono audio array, or None on error.
    Uses WASAPI shared mode so Windows voice typing (Win+H) still works.
    """
    try:
        import sounddevice as sd
    except ImportError:
        print("[ERROR] sounddevice not installed. Run: pip install sounddevice")
        return None

    chunk_size = int(sample_rate * 0.1)  # 100ms chunks
    chunks = []
    silent_chunks = 0
    silence_chunks_needed = int(silence_duration / 0.1)
    max_chunks = int(max_duration / 0.1)
    recording = False

    print("  [MIC] Listening... (speak now, silence ends recording)")

    # WASAPI shared mode — prevents exclusive lock that kills Windows STT bar
    extra_settings = None
    try:
        extra_settings = sd.WasapiSettings(exclusive=False, auto_convert=True)
    except Exception:
        pass  # Non-Windows or old sounddevice — skip

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32",
                            blocksize=chunk_size,
                            extra_settings=extra_settings) as stream:
            for _ in range(max_chunks):
                data, _ = stream.read(chunk_size)
                audio = data.flatten()
                energy = np.sqrt(np.mean(audio ** 2))

                if energy > silence_threshold:
                    recording = True
                    silent_chunks = 0
                    chunks.append(audio)
                elif recording:
                    silent_chunks += 1
                    chunks.append(audio)
                    if silent_chunks >= silence_chunks_needed:
                        break
    except Exception as exc:
        print(f"  [ERROR] Microphone error: {exc}")
        return None

    if not chunks:
        print("  [MIC] No speech detected.")
        return None

    return np.concatenate(chunks)


# ---------------------------------------------------------------------------
# Voice REPL
# ---------------------------------------------------------------------------

def _ensure_repo_root():
    """Add repo root to sys.path if not already present."""
    repo = Path(__file__).resolve().parents[4]
    root_str = str(repo)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return repo


def _init_stt_chain() -> list:
    """Initialize STT backends in priority order."""
    backends = [WhisperSTTBackend(), GoogleSTTBackend()]
    available = []
    for b in backends:
        if b.available():
            available.append(b)
            print(f"  [OK] STT: {b.name}")
        else:
            print(f"  [--] STT: {b.name} (unavailable)")
    return available


def _init_tts_chain() -> list:
    """Initialize TTS backends in priority order."""
    backends = [EdgeTTSBackend(), Pyttsx3TTSBackend()]
    available = []
    for b in backends:
        if b.available():
            available.append(b)
            print(f"  [OK] TTS: {b.name}")
        else:
            print(f"  [--] TTS: {b.name} (unavailable)")
    return available


def _transcribe_with_chain(stt_chain: list, audio: np.ndarray) -> Optional[str]:
    """Try each STT backend until one succeeds."""
    for backend in stt_chain:
        result = backend.transcribe(audio)
        if result:
            return result
    return None


def _speak_with_chain(tts_chain: list, text: str) -> None:
    """Try each TTS backend until one succeeds, fall back to print."""
    for backend in tts_chain:
        if backend.speak(text):
            return
    # All TTS failed — already printed by REPL


def run_voice_repl() -> None:
    """Interactive voice REPL for OpenClaw."""
    repo_root = _ensure_repo_root()

    print("=" * 60)
    print("  0102 OpenClaw Voice Chat")
    print("  Commander: @UnDaoDu | Channel: voice_repl")
    print("  Press Enter to speak, 'exit' to quit, 't' for text mode")
    print("=" * 60)
    print()

    # Initialize degradation chains
    print("Initializing voice backends...")
    stt_chain = _init_stt_chain()
    tts_chain = _init_tts_chain()
    print()

    if not stt_chain:
        print("[WARN] No STT backends available. Falling back to text-only mode.")
        print("  Install: pip install faster-whisper  (or)  pip install SpeechRecognition")

    # Initialize OpenClaw
    try:
        from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    except ImportError as exc:
        print(f"[ERROR] Cannot import OpenClawDAE: {exc}")
        return

    dae = OpenClawDAE(repo_root=repo_root)
    print(f"[OK] OpenClawDAE initialized (state={dae.state})")
    print()

    session_key = "voice_repl_012"
    text_mode = not stt_chain  # Start in text mode if no STT

    while True:
        try:
            if text_mode:
                user_input = input("012> ").strip()
            else:
                cmd = input("Type 'exit' to quit, 't' for text, or just press Enter to speak: ").strip().lower()
                if cmd in ("exit", "quit", "q"):
                    break
                if cmd == "t":
                    text_mode = True
                    print("  Switched to text mode. Type 'v' to return to voice.")
                    continue
                if cmd:
                    # User typed something other than a command — treat as text input
                    user_input = cmd
                    print(f"  012> {user_input}")
                else:
                    # Empty input (just Enter) — record from mic
                    audio = record_until_silence()
                    if audio is None:
                        continue

                    print("  [STT] Transcribing...")
                    user_input = _transcribe_with_chain(stt_chain, audio)
                    if not user_input:
                        print("  [STT] Could not transcribe. Try again or type 't' for text mode.")
                        continue
                    print(f"  012> {user_input}")

        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT] Session ended.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            break
        if user_input.lower() == "v" and text_mode:
            if stt_chain:
                text_mode = False
                print("  Switched to voice mode.")
            else:
                print("  [WARN] No STT backends available.")
            continue

        # Process through OpenClaw
        try:
            response = asyncio.run(
                dae.process(
                    message=user_input,
                    sender="@UnDaoDu",
                    channel="voice_repl",
                    session_key=session_key,
                )
            )
        except Exception as exc:
            response = f"Error: {type(exc).__name__}: {exc}"

        # Output: print + speak
        print(f"\n0102> {response}\n")
        if tts_chain:
            _speak_with_chain(tts_chain, response)


if __name__ == "__main__":
    run_voice_repl()
