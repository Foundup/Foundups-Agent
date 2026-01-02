#!/usr/bin/env python
"""End-to-end test: YouTube Live Audio -> STT -> Trigger Detection.

Usage:
    1. Play a YouTube live stream in your browser
    2. Run this script:
       python -m modules.platform_integration.youtube_live_audio.scripts.test_live_stt

    Say "0102" followed by a command to test trigger detection.

WSP Compliance:
    - WSP 49: Test script in scripts/ directory
    - WSP 84: Reuses youtube_live_audio and voice_command_ingestion modules
"""

import logging
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def test_audio_capture():
    """Test system audio capture only."""
    from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import (
        get_audio_source
    )

    print("\n" + "=" * 60)
    print("TEST 1: System Audio Capture")
    print("=" * 60)
    print("Play some audio (YouTube, music, etc.) and press Enter...")
    input()

    source = get_audio_source()
    success = source.test_audio(duration_sec=3.0)

    if success:
        print("[PASS] Audio capture working!")
    else:
        print("[FAIL] Audio capture failed - check audio output")

    return success


def test_stt_transcription():
    """Test STT transcription on captured audio."""
    from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import (
        get_audio_source
    )
    from modules.communication.voice_command_ingestion.src.voice_command_ingestion import (
        get_voice_ingestion
    )

    print("\n" + "=" * 60)
    print("TEST 2: STT Transcription")
    print("=" * 60)
    print("Play some speech audio and press Enter...")
    input()

    source = get_audio_source()
    ingestion = get_voice_ingestion(model_size="base")

    print("[INFO] Capturing 5 seconds of audio...")
    chunk = source.capture_single(duration_sec=5.0)

    if chunk is None:
        print("[FAIL] Failed to capture audio")
        return False

    print(f"[INFO] Captured {len(chunk.audio)} samples")
    print("[INFO] Transcribing...")

    event = ingestion.transcribe_audio(chunk.audio)

    if event and event.text:
        print(f"[PASS] Transcription: '{event.text}'")
        print(f"       Confidence: {event.confidence:.2f}")
        return True
    else:
        print("[FAIL] No transcription produced (silence or error)")
        return False


def test_trigger_detection():
    """Test trigger detection (say '0102' followed by command)."""
    from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import (
        get_audio_source
    )
    from modules.communication.voice_command_ingestion.src.voice_command_ingestion import (
        get_voice_ingestion
    )

    print("\n" + "=" * 60)
    print("TEST 3: Trigger Detection")
    print("=" * 60)
    print("Say '0102' followed by a command (e.g., '0102 send email')")
    print("Press Enter to start recording...")
    input()

    source = get_audio_source()
    ingestion = get_voice_ingestion(model_size="base")

    print("[INFO] Capturing 5 seconds of audio...")
    chunk = source.capture_single(duration_sec=5.0)

    if chunk is None:
        print("[FAIL] Failed to capture audio")
        return False

    print("[INFO] Processing...")
    stt_event, cmd_event = ingestion.process_single_chunk(chunk.audio)

    if stt_event:
        print(f"[STT] Heard: '{stt_event.text}'")

    if cmd_event:
        print(f"[PASS] Trigger detected!")
        print(f"       Command: '{cmd_event.command}'")
        print(f"       Confidence: {cmd_event.confidence:.2f}")
        return True
    else:
        print("[INFO] No trigger detected in this chunk")
        return False


def test_continuous_streaming(duration_chunks: int = 5):
    """Test continuous streaming STT."""
    from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import (
        get_audio_source
    )
    from modules.communication.voice_command_ingestion.src.voice_command_ingestion import (
        get_voice_ingestion
    )

    print("\n" + "=" * 60)
    print("TEST 4: Continuous Streaming")
    print("=" * 60)
    print(f"Will process {duration_chunks} audio chunks (5 seconds each)")
    print("Say '0102' followed by a command at any point")
    print("Press Enter to start...")
    input()

    source = get_audio_source()
    ingestion = get_voice_ingestion(model_size="base")

    print("[INFO] Streaming started. Press Ctrl+C to stop.")

    try:
        for chunk in source.stream_audio_chunks(max_chunks=duration_chunks):
            print(f"\n[CHUNK {chunk.chunk_index}] Processing {chunk.duration_sec}s of audio...")

            stt_event, cmd_event = ingestion.process_single_chunk(chunk.audio)

            if stt_event and stt_event.text:
                print(f"  [STT] '{stt_event.text}'")

            if cmd_event:
                print(f"  [TRIGGER] Command: '{cmd_event.command}'")

    except KeyboardInterrupt:
        print("\n[STOP] Streaming stopped by user")

    print("[DONE] Streaming test complete")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("YouTube Live Audio -> STT Pipeline Test")
    print("=" * 60)
    print("\nPrerequisites:")
    print("- Audio playing through system (YouTube, music, etc.)")
    print("- Microphone NOT required (uses system audio loopback)")
    print()

    # Test 1: Audio capture
    if not test_audio_capture():
        print("\n[ABORT] Audio capture failed. Check audio output.")
        return 1

    # Test 2: STT
    if not test_stt_transcription():
        print("\n[WARNING] STT test failed, but continuing...")

    # Test 3: Trigger detection
    test_trigger_detection()

    # Test 4: Continuous streaming
    test_continuous_streaming(duration_chunks=3)

    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
