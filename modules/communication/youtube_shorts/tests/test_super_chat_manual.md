# Manual Testing Guide - Super Chat Monetization

**Module**: `youtube_shorts`
**Feature**: Super Chat -> YouTube Shorts creation
**Test Date**: _________________
**Tester**: _________________

---

## Pre-Test Setup

### 1. Environment Check

```bash
# Verify all required environment variables
cd O:\Foundups-Agent

# Check Gemini API key
python -c "import os; print('Gemini API:', '[OK] Set' if os.getenv('GEMINI_API_KEY') else '[FAIL] Missing')"

# Check YouTube OAuth
python -c "from pathlib import Path; print('OAuth Token:', '[OK] Exists' if Path('credentials/oauth_token.json').exists() else '[FAIL] Missing')"
```

**Checklist**:
- [ ] Gemini API key configured in `.env`
- [ ] YouTube OAuth token exists (`credentials/oauth_token.json`)
- [ ] Veo 3 API enabled in Google Cloud Console
- [ ] YouTube channel has Super Chats enabled

---

## Test 1: Automated Integration Tests

**Purpose**: Verify all components work without live stream

### Run Automated Tests

```bash
cd O:\Foundups-Agent
python modules/communication/youtube_shorts/tests/test_super_chat_integration.py
```

### Expected Output

```
==============================================================
YOUTUBE SHORTS SUPER CHAT INTEGRATION TESTS
==============================================================

TEST 1: Super Chat Event Structure
[OK] Event structure validation passed

TEST 2: Amount Conversion (micros -> USD)
[OK] All conversions passed

TEST 3: $20 Minimum Threshold Check
[OK] $15.00 (Below minimum): Rejected
[OK] $20.00 (Exact minimum): Processed
[OK] $50.00 (Well above): Processed

TEST 4: Topic Extraction
[OK] All topic extractions passed

TEST 5: Concurrent Generation Lock
[OK] First request started generation
[OK] Second request blocked

TEST 6: Message Processor Routing
[OK] Event routed to handler

TEST 7: Full Pipeline Dry Run
[OK] Complete pipeline validated

==============================================================
TEST SUMMARY
==============================================================
Results: 7/7 tests passed (100.0%)
```

### Checklist

- [ ] All 7 tests passed
- [ ] No exceptions or errors
- [ ] Event structure matches YouTube API
- [ ] Amount conversion accurate (micros -> USD)
- [ ] $20 threshold enforced
- [ ] Topic extraction working
- [ ] Concurrent generation blocked

---

## Test 2: Video Generation (Costs Money!)

**[U+26A0]️ WARNING**: This test will charge ~$12 to your Google Cloud account

### Test Short Video Generation

```bash
cd O:\Foundups-Agent

# Test Veo 3 video generation (30 seconds)
python -c "
from modules.communication.youtube_shorts.src.veo3_generator import Veo3Generator

gen = Veo3Generator()
print('Testing Veo 3 generation...')

# Generate 5-second test (cheapest option: $2)
result = gen.generate_video(
    prompt='Cherry blossoms falling in Tokyo',
    duration=5  # 5 seconds = $2.00
)

print(f'[OK] Video generated: {result}')
"
```

### Expected Output

```
Testing Veo 3 generation...
[Veo3] Generating 5s video...
[Veo3] Operation: projects/.../operations/...
[Veo3] Polling for completion...
[Veo3] [OK] Video ready!
[OK] Video generated: {'video_url': 'gs://...', 'metadata': {...}}
```

### Checklist

- [ ] Video generation started
- [ ] Operation ID returned
- [ ] Polling completed successfully
- [ ] Video URL returned
- [ ] Cost: $2 for 5-second test

**If successful, proceed to 30-second test ($12)**:

```bash
# Generate full 30-second Short
python -c "
from modules.communication.youtube_shorts.src.veo3_generator import Veo3Generator

gen = Veo3Generator()
result = gen.generate_video(
    prompt='Cherry blossoms in Tokyo with Mount Fuji in background',
    duration=30  # 30 seconds = $12.00
)
print(f'[OK] Full Short generated: {result}')
"
```

- [ ] 30-second video generated successfully
- [ ] Cost: $12 charged to Google Cloud

---

## Test 3: YouTube Upload

**Purpose**: Verify video upload to YouTube channel

### Test Upload Functionality

```bash
# Assuming you have a test video file
cd O:\Foundups-Agent

python -c "
from modules.communication.youtube_shorts.src.youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()

# Upload test video (use video from Test 2)
result = uploader.upload_short(
    video_path='/path/to/test_video.mp4',
    title='TEST: Cherry Blossoms',
    description='Test upload - Super Chat monetization',
    privacy='unlisted'  # Use 'unlisted' for testing
)

print(f'[OK] Uploaded: https://youtube.com/shorts/{result['video_id']}')
"
```

### Checklist

- [ ] Video uploaded successfully
- [ ] YouTube Short URL returned
- [ ] Video is unlisted (not public)
- [ ] Title and description correct
- [ ] Video appears in YouTube Studio

---

## Test 4: End-to-End Orchestrator Test

**Purpose**: Test complete orchestrator flow (generation + upload)

### Run Orchestrator Test

```bash
cd O:\Foundups-Agent

python -c "
from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

orchestrator = ShortsOrchestrator()

# Test with 5-second video (cheaper test)
result = orchestrator.create_and_upload(
    topic='Cherry blossoms in Tokyo',
    duration=5,  # 5 seconds = $2
    privacy='unlisted'
)

print(f'[OK] Complete flow: {result}')
"
```

### Expected Output

```
[Orchestrator] Starting Short creation...
[Orchestrator] Topic: Cherry blossoms in Tokyo
[Orchestrator] Enhancing prompt with Gemini...
[Orchestrator] Generating video with Veo 3...
[Orchestrator] Video ready!
[Orchestrator] Uploading to YouTube...
[Orchestrator] [OK] Complete!
[OK] Complete flow: https://youtube.com/shorts/ABC123
```

### Checklist

- [ ] Prompt enhancement worked (Gemini)
- [ ] Video generation worked (Veo 3)
- [ ] Upload worked (YouTube)
- [ ] YouTube Short URL returned
- [ ] Total time: 1-2 minutes
- [ ] Cost: $2 (5 seconds)

**If successful, test with full 30-second Short ($12)**:

```bash
# Full 30-second Short test
python -c "
from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

orchestrator = ShortsOrchestrator()
result = orchestrator.create_and_upload(
    topic='Mount Fuji at sunrise with cherry blossoms',
    duration=30,
    privacy='unlisted'
)
print(f'[OK] Full Short: {result}')
"
```

- [ ] Full 30-second Short created
- [ ] Cost: $12 charged

---

## Test 5: Super Chat Integration (Full Pipeline)

**Purpose**: Test complete Super Chat -> Short creation flow

### Simulate Super Chat Event

```bash
cd O:\Foundups-Agent

python -c "
from modules.communication.youtube_shorts.tests.test_super_chat_integration import create_mock_super_chat_event
from modules.communication.youtube_shorts.src.chat_commands import ShortsCommandHandler

# Create mock $25 Super Chat
event = create_mock_super_chat_event(
    amount_usd=25.00,
    message='Cherry blossoms in Tokyo',
    donor_name='TestDonor'
)

# Process with handler
handler = ShortsCommandHandler()
handler.generating = False

response = handler.handle_super_chat_short(
    donor_name=event['donor_name'],
    donor_id=event['donor_id'],
    amount_usd=event['amount_usd'],
    message=event['message']
)

print(f'Bot response: {response}')
print()
print('[U+26A0]️ Note: Generation happens in background thread')
print('Check logs for generation progress')
"
```

### Monitor Logs

```bash
# In separate terminal, monitor logs
tail -f logs/youtube_shorts.log
```

### Expected Log Output

```
[ShortsChat] [U+1F4B0] TestDonor ($25.00 SC) requested Short: Cherry blossoms in Tokyo
[Orchestrator] Starting Short creation...
[Veo3] Generating video...
[Veo3] [OK] Video ready!
[Uploader] Uploading to YouTube...
[Uploader] [OK] Uploaded: youtube.com/shorts/ABC123
[ShortsChat] [OK] Super Chat Short created: youtube.com/shorts/ABC123
```

### Checklist

- [ ] Super Chat event processed
- [ ] $25 validated ([GREATER_EQUAL] $20 threshold)
- [ ] Topic extracted: "Cherry blossoms in Tokyo"
- [ ] Bot response sent immediately
- [ ] Background generation started
- [ ] Video generated successfully
- [ ] Upload completed
- [ ] Total time: 1-2 minutes
- [ ] Cost: $12 (generation)
- [ ] Revenue: $25 (Super Chat)
- [ ] **Net profit: $13**

---

## Test 6: Live Stream Test (OPTIONAL)

**Purpose**: Test with real YouTube Live stream and Super Chat

### Prerequisites

- [ ] YouTube Live stream active
- [ ] LiveChat module running
- [ ] Bot connected to stream
- [ ] Super Chats enabled on channel

### Test Procedure

1. **Start LiveChat**:
   ```bash
   # Option 2 in main.py
   python main.py
   # Select: 2) YouTube Live Chat
   ```

2. **Monitor Logs**:
   ```bash
   # Separate terminal
   tail -f logs/livechat.log | grep "SUPER CHAT"
   ```

3. **Send Test Super Chat**:
   - Go to live stream in browser
   - Send $20+ Super Chat with topic
   - Example: "$25 - Cherry blossoms in Tokyo"

4. **Verify Detection**:
   - Check logs for Super Chat detection
   - Check bot response in chat
   - Monitor generation progress

### Expected Behavior

```
# In livechat.log:
[U+1F4B0] SUPER CHAT: TestUser donated $25.00 (USD) - Tier 2
[U+1F4AC] Super Chat message: Cherry blossoms in Tokyo
[U+1F3AC] YouTube Shorts: @TestUser [U+1F4B0] Thank you for $25.00! Creating Short...

# In chat:
Bot: @TestUser [U+1F4B0] Thank you for the $25.00 Super Chat!
     Creating YouTube Short for: 'Cherry blossoms in Tokyo'
     | This will take 1-2 minutes... [CAMERA][U+2728]

# 1-2 minutes later (completion notification would require chat_sender integration):
# [Currently: Check YouTube channel for new Short]
```

### Checklist

- [ ] Super Chat detected in real-time
- [ ] Amount extracted correctly
- [ ] Topic extracted from message
- [ ] Bot responded immediately
- [ ] Video generation started
- [ ] Upload completed
- [ ] Short appears on channel

---

## Test Results Summary

| Test | Status | Cost | Notes |
|------|--------|------|-------|
| 1. Automated Tests | [U+2B1C] Pass / [U+2B1C] Fail | $0 | |
| 2. Video Generation (5s) | [U+2B1C] Pass / [U+2B1C] Fail | $2 | |
| 2. Video Generation (30s) | [U+2B1C] Pass / [U+2B1C] Fail | $12 | |
| 3. YouTube Upload | [U+2B1C] Pass / [U+2B1C] Fail | $0 | |
| 4. Orchestrator (5s) | [U+2B1C] Pass / [U+2B1C] Fail | $2 | |
| 4. Orchestrator (30s) | [U+2B1C] Pass / [U+2B1C] Fail | $12 | |
| 5. Super Chat Integration | [U+2B1C] Pass / [U+2B1C] Fail | $12 | |
| 6. Live Stream Test | [U+2B1C] Pass / [U+2B1C] Fail | $12 | |

**Total Testing Cost**: $52 (if all tests run)

---

## Troubleshooting

### Issue: Veo 3 Generation Fails

**Check**:
```bash
# Verify Gemini API key
python -c "import os; v=os.getenv('GEMINI_API_KEY'); print('[OK] GEMINI_API_KEY set (len=%d)'%len(v) if v else '[FAIL] GEMINI_API_KEY missing')"

# Test Gemini API
python modules/communication/youtube_shorts/tests/test_gemini_api.py
```

**Solution**: Ensure `.env` file has valid `GEMINI_API_KEY`

### Issue: YouTube Upload Fails

**Check**:
```bash
# Verify OAuth token
python -c "from pathlib import Path; print(Path('credentials/oauth_token.json').exists())"

# Re-authorize if needed
python modules/platform_integration/youtube_auth/scripts/authorize_set1.py
```

**Solution**: Re-run authorization script

### Issue: Super Chat Not Detected

**Check**:
- Is LiveChat running?
- Is bot connected to active stream?
- Are Super Chats enabled on channel?
- Check logs: `tail -f logs/livechat.log`

**Solution**: Verify YouTube Live Chat API permissions

---

## Sign-Off

**Tester**: _________________
**Date**: _________________
**Overall Result**: [U+2B1C] PASS / [U+2B1C] FAIL

**Notes**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
