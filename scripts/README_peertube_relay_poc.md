# PeerTube Relay PoC - Usage Instructions

## Overview

Minimal proof-of-concept script that relays a YouTube live stream to PeerTube using FFmpeg.

**File**: `O:/Foundups-Agent/scripts/peertube_relay_poc.py`

## Prerequisites

All dependencies are already installed:
- ✅ Python 3.12
- ✅ yt-dlp (2024.3.10)
- ✅ requests (2.31.0)
- ✅ ffmpeg (C:\ffmpeg\bin\ffmpeg.exe)

## Configuration

### Step 1: Edit the script

Open `peertube_relay_poc.py` and modify these lines:

```python
YOUTUBE_VIDEO_ID = "YOUR_VIDEO_ID_HERE"  # Replace with actual video ID
PEERTUBE_INSTANCE = "https://peertube.example.com"  # Your PeerTube instance URL
```

### Step 2: Set environment variables

```bash
# Windows Command Prompt
set PEERTUBE_API_TOKEN=your_api_token_here
set PEERTUBE_CHANNEL_ID=your_channel_id_here

# Windows PowerShell
$env:PEERTUBE_API_TOKEN="your_api_token_here"
$env:PEERTUBE_CHANNEL_ID="your_channel_id_here"
```

**To get your PeerTube API token:**
1. Log into your PeerTube instance
2. Go to Settings → Applications
3. Create new application or use existing token

**To find your Channel ID:**
1. Go to your PeerTube channel page
2. Channel ID is in the URL: `https://peertube.example.com/c/channel_name/videos`
3. Or check via API: `GET /api/v1/accounts/{username}/video-channels`

## Usage

```bash
cd O:\Foundups-Agent
python scripts/peertube_relay_poc.py
```

## What It Does

1. **Poll YouTube** (every 30 seconds) to check if video is live
2. **Extract HLS URL** using yt-dlp when live detected
3. **Create PeerTube live stream** via API
4. **Start FFmpeg relay**: YouTube HLS → PeerTube RTMP
5. **Monitor FFmpeg process** and log status
6. **Cleanup on CTRL+C** or stream end

## Output Example

```
============================================================
PeerTube Relay PoC - YouTube → PeerTube Live Stream
============================================================
YouTube Video ID: dQw4w9WgXcQ
PeerTube Instance: https://peertube.example.com
Poll Interval: 30s
============================================================
Press CTRL+C to stop
============================================================
[12:34:56] [INFO] Checking live status for YouTube video: dQw4w9WgXcQ
[12:34:58] [INFO] [LIVE] YouTube video dQw4w9WgXcQ is LIVE
[12:34:58] [INFO] [TRIGGER] Stream went LIVE - starting relay
[12:34:59] [INFO] Extracting HLS URL for video: dQw4w9WgXcQ
[12:35:01] [INFO] [OK] Extracted HLS URL: https://manifest.googlevideo.com/...
[12:35:01] [INFO] Creating PeerTube live stream...
[12:35:03] [INFO] [OK] PeerTube live created - ID: 12345
[12:35:03] [INFO] [OK] RTMP URL: https://peertube.example.com/live
[12:35:03] [INFO] [OK] Stream Key: abc12345...
[12:35:03] [INFO] Starting FFmpeg relay...
[12:35:03] [INFO] [OK] FFmpeg relay started (PID: 67890)
[12:35:03] [INFO] [OK] Relay is ACTIVE
```

## Stopping the Relay

Press `CTRL+C` to stop. The script will:
1. Terminate FFmpeg process gracefully
2. Log cleanup completion
3. Exit cleanly

## Troubleshooting

### "yt-dlp failed"
- Video ID might be wrong
- Video might not exist
- Network connectivity issues

### "Failed to extract HLS URL"
- Stream might not be live yet
- YouTube might have changed their format
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

### "PeerTube API error: 401"
- Invalid API token
- Token expired - generate new one

### "PeerTube API error: 404"
- Channel ID is wrong
- Instance URL is wrong

### "FFmpeg exited with code 1"
- HLS URL expired (YouTube URLs expire after ~6 hours)
- RTMP connection refused
- Check FFmpeg stderr output in logs

## Limitations (PoC Only)

- ❌ No automatic HLS URL refresh (URLs expire)
- ❌ No FFmpeg error recovery
- ❌ No reconnection logic
- ❌ Hardcoded configuration
- ❌ No database/telemetry
- ❌ Basic error handling only

## Next Steps (Post-PoC)

If PoC proves successful:

1. **Module integration** into `modules/communication/`
2. **Database tracking** for stream history
3. **AutoModeratorDAE enhancement** for automatic relay triggers
4. **HLS URL refresh** every ~1 hour
5. **FFmpeg monitoring** with auto-restart
6. **Multi-stream support** (relay multiple channels)
7. **Configuration file** instead of hardcoded values
8. **Unit tests** and integration tests

## WSP Compliance

- **WSP 1**: Single-purpose PoC script (no over-engineering)
- **WSP 50**: Verified dependencies before implementation
- **WSP 64**: No credentials in code (environment variables only)

## Success Criteria

✅ Script runs without errors
✅ Detects YouTube live stream status
✅ Extracts HLS URL via yt-dlp
✅ Creates PeerTube live stream via API
✅ Starts FFmpeg relay process
✅ Stream appears on PeerTube instance
✅ CTRL+C cleanup works correctly

---

**Author**: Qwen 2.5 (0102)
**Date**: 2025-10-26
**Status**: PoC Ready for Testing
