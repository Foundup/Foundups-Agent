# PeerTube Relay Setup Guide

## Overview

The PeerTube relay automatically mirrors YouTube live streams to a PeerTube instance when detected by the YouTube DAE (AutoModeratorDAE).

**Integration**: Hooks into existing `AutoModeratorDAE._trigger_social_media_posting_for_streams()` method.

---

## 1. Prerequisites

### Required Software
- Python 3.12+ (already installed)
- `yt-dlp` - YouTube HLS extraction
  ```bash
  pip install yt-dlp
  ```
- `FFmpeg` - Stream relay
  - Windows: Download from https://ffmpeg.org/download.html
  - Add to PATH: `C:\ffmpeg\bin\`
  - Verify: `ffmpeg -version`

### Required Accounts
- YouTube channel (already configured)
- [WAIT] PeerTube account (setup below)

---

## 2. PeerTube Account Setup

### Step 1: Choose a PeerTube Instance

**Options**:
1. **Self-Hosted**: Install PeerTube on your own server
   - Guide: https://docs.joinpeertube.org/install/any-os
   - Requires: VPS/server with NodeJS, PostgreSQL, Redis

2. **Public Instance**: Create account on existing instance
   - List: https://instances.joinpeertube.org/
   - Recommended: Choose instance with good uptime + live streaming enabled

### Step 2: Create Account

1. Go to your chosen PeerTube instance
2. Click "Sign Up" or "Create Account"
3. Fill in: Username, Email, Password
4. Verify email (if required)
5. Complete profile setup

### Step 3: Create a Channel

1. Log in to PeerTube
2. Go to "My Account" -> "My Channels"
3. Click "Create Channel"
4. Fill in:
   - **Name**: e.g., "YouTube Live Mirror"
   - **Description**: Auto-mirrored streams from YouTube
5. Save channel
6. **Copy Channel ID**:
   - Click channel -> URL will be: `https://peertube.example.com/c/CHANNEL_NAME`
   - Go to Settings -> Note the UUID (this is your `PEERTUBE_CHANNEL_ID`)

### Step 4: Generate API Token

1. Go to "Settings" -> "Applications"
2. Click "Generate new application"
3. **Application Name**: `FoundUps YouTube Relay`
4. Click "Create"
5. **Copy API Token** (long string like `a1b2c3d4-...`)
   - [WARN] **IMPORTANT**: Store securely - shown only once!

---

## 3. Configure Foundups Agent

### Option A: System Environment Variables (Recommended)

**Windows** (PowerShell as Administrator):
```powershell
[System.Environment]::SetEnvironmentVariable("PEERTUBE_INSTANCE_URL", "https://peertube.example.com", "User")
[System.Environment]::SetEnvironmentVariable("PEERTUBE_API_TOKEN", "your_api_token_here", "User")
[System.Environment]::SetEnvironmentVariable("PEERTUBE_CHANNEL_ID", "your_channel_uuid_here", "User")
[System.Environment]::SetEnvironmentVariable("PEERTUBE_RELAY_ENABLED", "true", "User")
```

**Linux/Mac**:
```bash
echo 'export PEERTUBE_INSTANCE_URL="https://peertube.example.com"' >> ~/.bashrc
echo 'export PEERTUBE_API_TOKEN="your_api_token_here"' >> ~/.bashrc
echo 'export PEERTUBE_CHANNEL_ID="your_channel_uuid_here"' >> ~/.bashrc
echo 'export PEERTUBE_RELAY_ENABLED="true"' >> ~/.bashrc
source ~/.bashrc
```

### Option B: .env File (Alternative)

Add to `O:/Foundups-Agent/.env`:
```bash
# PeerTube Configuration
PEERTUBE_INSTANCE_URL=https://peertube.example.com
PEERTUBE_API_TOKEN=your_api_token_here
PEERTUBE_CHANNEL_ID=your_channel_uuid_here
PEERTUBE_RELAY_ENABLED=true
```

[WARN] **Security**: Never commit `.env` to git!

---

## 4. Integration with AutoModeratorDAE

### File Modified
`modules/communication/livechat/src/auto_moderator_dae.py`

### Changes Required

**Add to `__init__()` method** (after WRE integration, around line 85):

```python
# PeerTube Relay Integration (YouTube -> PeerTube stream relay)
try:
    from .peertube_relay_handler import PeerTubeRelayHandler
    self.peertube_relay = PeerTubeRelayHandler()
    if self.peertube_relay.enabled:
        logger.info("[PEERTUBE] [RELAY] PeerTube relay handler connected to YouTube DAE")
except Exception as e:
    logger.debug(f"[PEERTUBE] Relay handler not available: {e}")
    self.peertube_relay = None
```

**Add to `_trigger_social_media_posting_for_streams()` method** (after line 504):

```python
# Trigger PeerTube relay if enabled
if self.peertube_relay:
    try:
        self.peertube_relay.handle_streams_detected(found_streams)
    except Exception as e:
        logger.error(f"[PEERTUBE] [RELAY] Error handling streams: {e}")
```

---

## 5. Testing

### Test 1: Configuration Validation

```bash
python -c "from modules.communication.livechat.src.peertube_relay_handler import PeerTubeRelayHandler; h = PeerTubeRelayHandler(); print('Enabled:', h.enabled)"
```

**Expected Output**:
```
Enabled: True
```

### Test 2: YouTube DAE with PeerTube Relay

1. Start YouTube DAE:
   ```bash
   python main.py
   # Select Option 1 or Option 5
   ```

2. Watch logs for PeerTube relay initialization:
   ```
   [PEERTUBE] [RELAY] Initialized - instance=https://peertube.example.com
   [PEERTUBE] [RELAY] PeerTube relay handler connected to YouTube DAE
   ```

3. When YouTube stream detected, look for:
   ```
   [PEERTUBE] [RELAY] [START] Starting relay for VIDEO_ID (Channel Name)
   [PEERTUBE] [RELAY] [OK] Extracted HLS URL
   [PEERTUBE] [RELAY] [OK] Created PeerTube live stream (ID: 12345)
   [PEERTUBE] [RELAY] [OK] [ROCKET] Relay ACTIVE for VIDEO_ID (PID: 67890)
   ```

4. Verify on PeerTube:
   - Go to your PeerTube instance
   - Navigate to your channel
   - Live stream should appear in "My Videos" -> "Live"

### Test 3: Stream Quality Check

1. Open PeerTube live stream in browser
2. Verify:
   - Stream is playing
   - Audio/video synchronized
   - Minimal latency (5-10 seconds behind YouTube)
   - No buffering issues

---

## 6. Monitoring & Troubleshooting

### Check Relay Status

All PeerTube relay actions log through the **YouTube DAE logger**, so watch the YouTube DAE console output.

**Log Prefixes**:
- `[PEERTUBE] [RELAY] [START]` - Relay starting
- `[PEERTUBE] [RELAY] [OK]` - Success
- `[PEERTUBE] [RELAY] [FAIL]` - Error
- `[PEERTUBE] [RELAY] [STOP]` - Relay stopping
- `[PEERTUBE] [RELAY] [CLEANUP]` - Shutdown cleanup

### Common Issues

#### Issue 1: "yt-dlp not found"
**Solution**:
```bash
pip install yt-dlp
```

#### Issue 2: "ffmpeg not found"
**Solution**:
- Download FFmpeg: https://ffmpeg.org/download.html
- Add to PATH
- Verify: `ffmpeg -version`

#### Issue 3: "API error (401): Unauthorized"
**Solution**:
- Check `PEERTUBE_API_TOKEN` is correct
- Regenerate token in PeerTube Settings -> Applications
- Update environment variable

#### Issue 4: "API error (404): Channel not found"
**Solution**:
- Verify `PEERTUBE_CHANNEL_ID` is the UUID (not channel name)
- Check channel exists: PeerTube -> My Channels

#### Issue 5: "FFmpeg crashed"
**Solution**:
- Check HLS URL is still valid (expires ~6 hours)
- Check PeerTube accepts stream format
- Verify network connectivity to PeerTube instance

---

## 7. Advanced Configuration

### Disable Relay Temporarily

```bash
# Set environment variable
set PEERTUBE_RELAY_ENABLED=false   # Windows
export PEERTUBE_RELAY_ENABLED=false  # Linux/Mac

# Or edit .env
PEERTUBE_RELAY_ENABLED=false
```

### Multiple RTMP Targets (Future)

**Not Yet Implemented** - Current PoC supports single PeerTube target only.

**Roadmap**:
- Add `config/stream_endpoints.json` for multi-target support
- Support Twitch, Facebook, custom RTMP simultaneously
- Per-target enable/disable flags

---

## 8. Architecture

```
YouTube Live Detection (AutoModeratorDAE)
    v
find_livestream() discovers stream
    v
_trigger_social_media_posting_for_streams(found_streams)
    v
peertube_relay.handle_streams_detected(found_streams)
    v
For each stream:
    1. Extract HLS URL (yt-dlp)
    2. Create PeerTube live (API POST)
    3. Start FFmpeg relay (subprocess)
    4. Track process (active_relays dict)
    v
Stream ends -> stop_relay() -> terminate FFmpeg
```

---

## 9. Files Created

- `modules/communication/livechat/src/peertube_relay_handler.py` (329 lines)
  - `PeerTubeRelayHandler` class
  - Integrates with AutoModeratorDAE
  - Logs to YouTube DAE logger

---

## 10. WSP Compliance

- **WSP 27**: DAE architecture integration
- **WSP 64**: Secure credential management (ENV vars)
- **WSP 91**: DAEMON observability (YouTube DAE logger)
- **WSP 1**: Occam's Razor (minimal PoC integration)

---

## 11. Support

**Logs**: Monitor YouTube DAE console output (all PeerTube logs go there)

**Disable**: Set `PEERTUBE_RELAY_ENABLED=false`

**Report Issues**: Include YouTube DAE log excerpt showing `[PEERTUBE] [RELAY]` lines

---

**Status**: - Ready for testing (pending AutoModeratorDAE integration code changes)
