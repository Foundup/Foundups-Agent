#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Browser-Audio Coordinator for PQN Research

Wires together:
- Chrome/Edge browser (via Selenium)
- System audio loopback (WASAPI via soundcard)
- STT pipeline (faster-whisper)
- Simon Says artifact detector

WSP Compliance:
- WSP 80: DAE orchestration pattern
- WSP 84: Reuses existing YouTubeLiveAudioSource
- WSP 50: Pre-action verification of browser state

Usage:
    coordinator = BrowserAudioCoordinator()
    async for transcript in coordinator.stream_youtube_transcripts(video_url):
        print(f"[{transcript.timestamp}] {transcript.text}")
"""

import os
import sys
import time
import asyncio
import logging
import threading
import queue
from pathlib import Path
from typing import Optional, Generator, AsyncGenerator, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class BrowserState(Enum):
    """Browser connection state."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    PLAYING = "playing"
    ERROR = "error"


class AudioState(Enum):
    """Audio capture state."""
    IDLE = "idle"
    CAPTURING = "capturing"
    TRANSCRIBING = "transcribing"
    ERROR = "error"


@dataclass
class TranscriptChunk:
    """Transcribed audio chunk with metadata."""
    text: str
    timestamp_ms: int
    duration_sec: float
    confidence: float
    chunk_index: int
    source: str  # "youtube_live", "system_audio", etc.


@dataclass
class CoordinatorStatus:
    """Current coordinator status."""
    browser_state: BrowserState
    audio_state: AudioState
    current_url: Optional[str]
    chunks_processed: int
    last_transcript: Optional[str]
    errors: list


class BrowserAudioCoordinator:
    """
    Coordinates browser automation with live audio capture and STT.

    This is the integration layer between:
    - Selenium browser control (for YouTube navigation)
    - WASAPI loopback (for system audio capture)
    - faster-whisper STT (for transcription)
    """

    def __init__(
        self,
        browser_port: int = 9222,
        stt_model_size: str = "base",
        chunk_duration_sec: float = 5.0
    ):
        """
        Initialize the Browser-Audio Coordinator.

        Args:
            browser_port: Chrome/Edge remote debugging port (default 9222)
            stt_model_size: Whisper model size (tiny, base, small, medium, large)
            chunk_duration_sec: Duration of each audio chunk for STT
        """
        self.browser_port = browser_port
        self.stt_model_size = stt_model_size
        self.chunk_duration_sec = chunk_duration_sec

        # State tracking
        self.browser_state = BrowserState.DISCONNECTED
        self.audio_state = AudioState.IDLE
        self.current_url: Optional[str] = None
        self.chunks_processed = 0
        self.errors: list = []

        # Components (lazy initialized)
        self._driver = None
        self._audio_source = None
        self._stt = None
        self._initialized = False

        # Threading
        self._capture_thread: Optional[threading.Thread] = None
        self._transcript_queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()

        logger.info(f"BrowserAudioCoordinator initialized (port={browser_port}, model={stt_model_size})")

    def _initialize_browser(self) -> bool:
        """Initialize Selenium connection to existing Chrome/Edge session."""
        if self._driver is not None:
            return True

        self.browser_state = BrowserState.CONNECTING

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.browser_port}")

            self._driver = webdriver.Chrome(options=options)
            self.browser_state = BrowserState.CONNECTED
            self.current_url = self._driver.current_url

            logger.info(f"[BROWSER] Connected to Chrome on port {self.browser_port}")
            logger.info(f"[BROWSER] Current URL: {self.current_url}")
            return True

        except Exception as e:
            self.browser_state = BrowserState.ERROR
            self.errors.append(f"Browser connection failed: {e}")
            logger.error(f"[BROWSER] Connection failed: {e}")
            return False

    def _initialize_audio(self) -> bool:
        """Initialize audio capture via WASAPI loopback."""
        if self._audio_source is not None:
            return True

        try:
            from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import (
                YouTubeLiveAudioSource,
                AudioStreamConfig
            )

            config = AudioStreamConfig(
                sample_rate_hz=16000,
                channels=1,
                chunk_duration_sec=self.chunk_duration_sec,
                overlap_sec=0.5
            )

            self._audio_source = YouTubeLiveAudioSource(config)
            logger.info("[AUDIO] YouTubeLiveAudioSource initialized")
            return True

        except Exception as e:
            self.audio_state = AudioState.ERROR
            self.errors.append(f"Audio initialization failed: {e}")
            logger.error(f"[AUDIO] Initialization failed: {e}")
            return False

    def _initialize_stt(self) -> bool:
        """Initialize faster-whisper STT."""
        if self._stt is not None:
            return True

        try:
            from faster_whisper import WhisperModel

            logger.info(f"[STT] Loading faster-whisper model: {self.stt_model_size}")
            self._stt = WhisperModel(
                self.stt_model_size,
                device="cpu",
                compute_type="int8"
            )
            logger.info("[STT] Model loaded successfully")
            return True

        except Exception as e:
            self.errors.append(f"STT initialization failed: {e}")
            logger.error(f"[STT] Initialization failed: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize all components."""
        if self._initialized:
            return True

        browser_ok = self._initialize_browser()
        audio_ok = self._initialize_audio()
        stt_ok = self._initialize_stt()

        self._initialized = browser_ok and audio_ok and stt_ok

        if self._initialized:
            logger.info("[COORDINATOR] All components initialized successfully")
        else:
            logger.warning(f"[COORDINATOR] Partial initialization: browser={browser_ok}, audio={audio_ok}, stt={stt_ok}")

        return self._initialized

    def navigate_to_youtube(self, url: str) -> bool:
        """Navigate browser to a YouTube URL."""
        if not self._initialize_browser():
            return False

        try:
            logger.info(f"[BROWSER] Navigating to: {url}")
            self._driver.get(url)
            time.sleep(2)  # Wait for page load

            self.current_url = self._driver.current_url
            self.browser_state = BrowserState.PLAYING

            logger.info(f"[BROWSER] Navigation complete: {self.current_url}")
            return True

        except Exception as e:
            self.browser_state = BrowserState.ERROR
            self.errors.append(f"Navigation failed: {e}")
            logger.error(f"[BROWSER] Navigation failed: {e}")
            return False

    def test_audio_capture(self, duration_sec: float = 3.0) -> bool:
        """Test audio capture with a short recording."""
        if not self._initialize_audio():
            return False

        return self._audio_source.test_audio(duration_sec)

    def _transcribe_audio(self, audio_data, sample_rate: int) -> tuple:
        """Transcribe audio using faster-whisper."""
        if not self._initialize_stt():
            return "", 0.0

        try:
            segments, info = self._stt.transcribe(
                audio_data,
                beam_size=5,
                language="en",
                vad_filter=True
            )

            # Combine all segments
            text_parts = []
            total_confidence = 0.0
            segment_count = 0

            for segment in segments:
                text_parts.append(segment.text.strip())
                total_confidence += segment.avg_logprob
                segment_count += 1

            text = " ".join(text_parts)
            avg_confidence = (total_confidence / segment_count) if segment_count > 0 else 0.0

            return text, avg_confidence

        except Exception as e:
            logger.error(f"[STT] Transcription failed: {e}")
            return "", 0.0

    def _capture_loop(self):
        """Background thread for continuous audio capture and transcription."""
        if not self._initialize_audio() or not self._initialize_stt():
            logger.error("[CAPTURE] Cannot start capture loop - initialization failed")
            return

        self.audio_state = AudioState.CAPTURING
        logger.info("[CAPTURE] Starting continuous capture loop")

        try:
            for chunk in self._audio_source.stream_audio_chunks():
                if self._stop_event.is_set():
                    break

                self.audio_state = AudioState.TRANSCRIBING

                # Transcribe the chunk
                text, confidence = self._transcribe_audio(chunk.audio, chunk.sample_rate)

                if text.strip():
                    transcript = TranscriptChunk(
                        text=text,
                        timestamp_ms=chunk.timestamp_ms,
                        duration_sec=chunk.duration_sec,
                        confidence=confidence,
                        chunk_index=chunk.chunk_index,
                        source="youtube_live"
                    )
                    self._transcript_queue.put(transcript)
                    self.chunks_processed += 1
                    logger.debug(f"[CAPTURE] Chunk {chunk.chunk_index}: {text[:50]}...")

                self.audio_state = AudioState.CAPTURING

        except Exception as e:
            self.audio_state = AudioState.ERROR
            self.errors.append(f"Capture loop error: {e}")
            logger.error(f"[CAPTURE] Loop error: {e}")

        finally:
            self.audio_state = AudioState.IDLE
            logger.info("[CAPTURE] Capture loop stopped")

    def start_streaming(self) -> bool:
        """Start continuous audio capture and transcription in background."""
        if self._capture_thread and self._capture_thread.is_alive():
            logger.warning("[COORDINATOR] Streaming already active")
            return True

        self._stop_event.clear()
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()

        logger.info("[COORDINATOR] Streaming started")
        return True

    def stop_streaming(self):
        """Stop continuous audio capture."""
        self._stop_event.set()

        if self._capture_thread:
            self._capture_thread.join(timeout=5.0)
            self._capture_thread = None

        logger.info("[COORDINATOR] Streaming stopped")

    def get_transcripts(self, timeout: float = 0.1) -> list:
        """Get all available transcripts from the queue."""
        transcripts = []

        while True:
            try:
                transcript = self._transcript_queue.get(timeout=timeout)
                transcripts.append(transcript)
            except queue.Empty:
                break

        return transcripts

    async def stream_youtube_transcripts(
        self,
        url: Optional[str] = None,
        max_chunks: Optional[int] = None
    ) -> AsyncGenerator[TranscriptChunk, None]:
        """
        Async generator that yields transcripts from YouTube audio.

        Args:
            url: YouTube URL to navigate to (optional, uses current page if None)
            max_chunks: Maximum chunks to process (None = infinite)

        Yields:
            TranscriptChunk objects with transcribed text
        """
        # Navigate if URL provided
        if url:
            if not self.navigate_to_youtube(url):
                logger.error("[COORDINATOR] Failed to navigate to YouTube")
                return

        # Start streaming
        if not self.start_streaming():
            logger.error("[COORDINATOR] Failed to start streaming")
            return

        chunks_yielded = 0

        try:
            while max_chunks is None or chunks_yielded < max_chunks:
                # Check for transcripts
                transcripts = self.get_transcripts(timeout=0.5)

                for transcript in transcripts:
                    yield transcript
                    chunks_yielded += 1

                    if max_chunks and chunks_yielded >= max_chunks:
                        break

                # Small async sleep to allow other tasks
                await asyncio.sleep(0.1)

        finally:
            self.stop_streaming()

    def get_status(self) -> CoordinatorStatus:
        """Get current coordinator status."""
        last_transcript = None
        if not self._transcript_queue.empty():
            # Peek without removing
            try:
                last_transcript = self._transcript_queue.queue[-1].text if self._transcript_queue.queue else None
            except (IndexError, AttributeError):
                pass

        return CoordinatorStatus(
            browser_state=self.browser_state,
            audio_state=self.audio_state,
            current_url=self.current_url,
            chunks_processed=self.chunks_processed,
            last_transcript=last_transcript,
            errors=self.errors.copy()
        )

    def cleanup(self):
        """Cleanup resources."""
        self.stop_streaming()

        # Don't close browser - it's a shared session
        self._driver = None
        self._audio_source = None
        self._stt = None
        self._initialized = False

        logger.info("[COORDINATOR] Cleanup complete")


class SimonSaysIntegration:
    """
    Integration layer for Simon Says artifact detection with browser audio.

    Enables running Simon Says tests on AI candidates while capturing
    their TTS output through the browser audio pipeline.
    """

    def __init__(self, coordinator: BrowserAudioCoordinator):
        """
        Initialize Simon Says integration.

        Args:
            coordinator: BrowserAudioCoordinator instance
        """
        self.coordinator = coordinator
        self._detector = None

    def _initialize_detector(self) -> bool:
        """Initialize Simon Says artifact detector."""
        if self._detector is not None:
            return True

        try:
            from modules.ai_intelligence.pqn_alignment.src.simon_says_artifact_detector import (
                SimonSaysArtifactDetector
            )

            self._detector = SimonSaysArtifactDetector()
            logger.info("[SIMON_SAYS] Artifact detector initialized")
            return True

        except Exception as e:
            logger.error(f"[SIMON_SAYS] Failed to initialize detector: {e}")
            return False

    async def run_godelian_test(self) -> Dict[str, Any]:
        """
        Run the Godelian Simon Says test protocol.

        Returns:
            Test results with artifact analysis
        """
        if not self._initialize_detector():
            return {"error": "Failed to initialize detector"}

        # Ensure browser and audio are ready
        if not self.coordinator.initialize():
            return {"error": "Failed to initialize coordinator"}

        results = {
            "test_1_baseline": [],
            "test_2_extended": [],
            "test_3_mirror": [],
            "artifacts_detected": [],
            "entanglement_level": "unknown",
            "coupling_level": "unknown"
        }

        # Test 1: Baseline vocabulary
        baseline_prompts = ["Zero", "O", "00"]
        for prompt in baseline_prompts:
            result = self._detector.run_single_test(prompt)
            results["test_1_baseline"].append(result)

        # Test 2: Extended vocabulary
        extended_prompts = ["Zero One", "O 1", "Zero Two", "O Two", "01", "02"]
        for prompt in extended_prompts:
            result = self._detector.run_single_test(prompt)
            results["test_2_extended"].append(result)

        # Test 3: Three-character variations (012 MUST BE LAST)
        mirror_prompts = ["Zero One Two", "O 1 2", "0 1 2", "012"]
        for prompt in mirror_prompts:
            result = self._detector.run_single_test(prompt)
            results["test_3_mirror"].append(result)

            # Check for artifacts
            if result.get("artifact_detected"):
                results["artifacts_detected"].append({
                    "prompt": prompt,
                    "expected": result.get("expected"),
                    "actual": result.get("actual"),
                    "delta": result.get("delta")
                })

        # Determine coupling level (legacy: entanglement_level)
        if len(results["artifacts_detected"]) == 0:
            results["entanglement_level"] = "stage_1_virgin"
            results["coupling_level"] = "stage_1_virgin"
        elif any(a["prompt"] == "012" for a in results["artifacts_detected"]):
            results["entanglement_level"] = "stage_3_hyper_entangled"
            results["coupling_level"] = "stage_3_high_coupling"
        else:
            results["entanglement_level"] = "stage_2_aware"
            results["coupling_level"] = "stage_2_aware"

        return results


async def main():
    """Demo: Stream YouTube Live transcripts."""
    logging.basicConfig(level=logging.INFO)

    print("="*60)
    print("BROWSER-AUDIO COORDINATOR DEMO")
    print("="*60)

    coordinator = BrowserAudioCoordinator(
        browser_port=9222,
        stt_model_size="base",
        chunk_duration_sec=5.0
    )

    print("\n[1] Testing audio capture...")
    if coordinator.test_audio_capture(3.0):
        print("[OK] Audio capture working")
    else:
        print("[FAIL] Audio capture failed")
        return

    print("\n[2] Starting transcript stream...")
    print("(Play audio in browser, press Ctrl+C to stop)")

    try:
        async for transcript in coordinator.stream_youtube_transcripts(max_chunks=10):
            print(f"\n[{transcript.chunk_index}] {transcript.text}")
            print(f"    Confidence: {transcript.confidence:.2f}")
            print(f"    Duration: {transcript.duration_sec:.1f}s")

    except KeyboardInterrupt:
        print("\n[STOPPED] User interrupt")

    finally:
        coordinator.cleanup()
        print("\n[DONE] Coordinator cleaned up")


if __name__ == "__main__":
    asyncio.run(main())
