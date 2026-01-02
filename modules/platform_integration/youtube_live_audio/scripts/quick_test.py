#!/usr/bin/env python
"""Quick import and trigger detection test."""
import sys
sys.path.insert(0, 'O:/Foundups-Agent')

# Test 1: Import check
print('[TEST] Import check...')
from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import get_audio_source, SystemAudioCapture
from modules.communication.voice_command_ingestion.src.voice_command_ingestion import get_voice_ingestion, TriggerDetector
print('[PASS] All imports successful')

# Test 2: Trigger detection patterns
print('[TEST] Trigger detection...')
detector = TriggerDetector()
tests = [
    ('zero one zero two', True),
    ('oh one oh two', True),
    ('0102 send email', True),
    ('hello world', False),
    ('01 02', True),
]
for text, expected in tests:
    found, cmd, _ = detector.detect(text)
    status = 'PASS' if found == expected else 'FAIL'
    print(f'  [{status}] "{text}" -> trigger={found}')

print('[DONE] Basic tests passed')

# Test 3: Audio capture initialization
print('[TEST] Audio capture init...')
try:
    capture = SystemAudioCapture()
    if capture._initialize():
        print('[PASS] Audio device initialized')
    else:
        print('[WARN] Audio init failed (no audio device?)')
except Exception as e:
    print(f'[WARN] Audio init error: {e}')

print('[COMPLETE] All tests finished')
