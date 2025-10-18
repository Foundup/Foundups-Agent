# Social Media Posting Scenarios Map
**Created**: 2025-09-24
**Purpose**: Map all posting scenarios and account routing logic

## [DATA] Posting Scenarios Overview

### 1️⃣ YOUTUBE LIVE STREAM DETECTION
**Trigger**: Stream detected by stream_resolver
**Flow**: stream_resolver -> social_media_orchestrator -> LinkedIn + X

#### Channel -> Account Routing Configuration:

```json
{
  "channel_routing": {
    "UCklMTNnu5POwRmQsg5JJumA": {
      "name": "Move2Japan",
      "linkedin_page_id": "104834798",
      "linkedin_page_name": "Move2Japan",
      "x_account": "X_Acc1",
      "x_handle": "@GeozeAi"
    },
    "UC-LSSlOZwpGIRIYihaz8zCw": {
      "name": "UnDaoDu",
      "linkedin_page_id": "68706058",
      "linkedin_page_name": "UnDaoDu",
      "x_account": "X_Acc2",
      "x_handle": "@Foundups"
    },
    "UCSNTUXjAgpd4sgWYP0xoJgw": {
      "name": "FoundUps",
      "linkedin_page_id": "1263645",
      "linkedin_page_name": "FoundUps",
      "x_account": "X_Acc2",
      "x_handle": "@Foundups"
    }
  },
  "default_routing": {
    "linkedin_page_id": "1263645",
    "linkedin_page_name": "FoundUps",
    "x_account": "X_Acc2",
    "x_handle": "@Foundups"
  }
}
```

#### How to Add New Channels:
1. Add entry to `channel_routing` with YouTube channel ID as key
2. Specify LinkedIn page ID and name
3. Specify X account (X_Acc1 or X_Acc2) and handle
4. No code changes needed - configuration drives the routing!

#### Post Content:
- **LinkedIn**: Full stream announcement with emojis, hashtags, and link
- **X/Twitter**: Short announcement with link (280 char limit)

---

### 2️⃣ GIT COMMIT POSTING
**Trigger**: Option 0 in main.py or git push command
**Flow**: git_linkedin_bridge -> LinkedIn + X

#### Account Configuration:
- **LinkedIn**: Always posts to FoundUps company page (1263645)
- **X/Twitter**: Always posts to @Foundups account (X_Acc2)

#### Post Content:
- **LinkedIn**: Detailed commit summary with file changes, bullet points
- **X/Twitter**: Minimal "GitHub update: X files" with repo link

---

### 3️⃣ MANUAL SOCIAL MEDIA POSTS
**Trigger**: Direct API calls or test scripts
**Flow**: Direct to LinkedIn/X poster modules

---

## [REFRESH] Implementation Flow

### YouTube Stream Detection Flow:
```
1. auto_moderator_dae.py finds stream
   v
2. stream_resolver.resolve_stream() gets video_id
   v
3. stream_resolver._trigger_social_media_post()
   v
4. simple_posting_orchestrator.handle_stream_detected()
   v
5. Routes to correct LinkedIn page based on channel_id
   v
6. Routes to correct X account based on channel_id
   v
7. Posts sequentially (LinkedIn first, then X)
```

### Git Posting Flow:
```
1. main.py option 0 selected
   v
2. git_linkedin_bridge.push_and_post()
   v
3. Generate LinkedIn content (detailed)
   v
4. Generate X content (minimal)
   v
5. Post to LinkedIn (FoundUps page)
   v
6. Post to X (@Foundups)
```

---

## [ALERT] Current Issues & Fixes Needed

### Issue 1: Move2Japan Not Posting to LinkedIn
**Problem**: Stream detected but LinkedIn post not triggering
**Root Cause**: Need to verify _trigger_social_media_post is being called
**Fix**: Add logging to trace the flow

### Issue 2: Account Routing Confusion
**Problem**: X poster might be using wrong account
**Root Cause**: Account selection logic in simple_posting_orchestrator
**Fix**: Ensure use_foundups flag is correctly set based on channel

### Issue 3: Duplicate Prevention Too Aggressive
**Problem**: Posts being blocked as duplicates incorrectly
**Root Cause**: Global duplicate check instead of per-platform
**Fix**: Track duplicates per platform, not globally

---

## [NOTE] Required Code Changes

### 1. Fix LinkedIn Page Routing
In `stream_resolver.py::_get_linkedin_page_for_channel()`:
```python
def _get_linkedin_page_for_channel(self, channel_id):
    channel_to_page = {
        'UCklMTNnu5POwRmQsg5JJumA': '104834798',  # Move2Japan
        'UC-LSSlOZwpGIRIYihaz8zCw': '68706058',   # UnDaoDu
        'UCSNTUXjAgpd4sgWYP0xoJgw': '1263645'     # FoundUps
    }
    return channel_to_page.get(channel_id, '1263645')  # Default to FoundUps
```

### 2. Fix X Account Selection
In `simple_posting_orchestrator.py`:
```python
# Determine X account based on LinkedIn page
use_foundups = linkedin_page != "104834798"  # Use GeozeAi only for Move2Japan
```

### 3. Add Proper Logging
Add clear logging at each step:
- Stream detection
- Social media trigger
- Platform selection
- Account routing
- Post success/failure

---

## [OK] Testing Checklist

- [ ] Move2Japan stream -> LinkedIn Move2Japan page + X @GeozeAi
- [ ] UnDaoDu stream -> LinkedIn UnDaoDu page + X @Foundups
- [ ] FoundUps stream -> LinkedIn FoundUps page + X @Foundups
- [ ] Git push -> LinkedIn FoundUps page + X @Foundups
- [ ] Duplicate prevention per platform, not global
- [ ] Proper error handling when browser closes

---

## [BOOKS] Related Files

### Core Orchestration:
- `modules/platform_integration/social_media_orchestrator/src/simple_posting_orchestrator.py`

### Stream Detection:
- `modules/platform_integration/stream_resolver/src/stream_resolver.py`
- `modules/communication/livechat/src/auto_moderator_dae.py`

### Git Posting:
- `modules/platform_integration/linkedin_agent/src/git_linkedin_bridge.py`

### Platform Posters:
- `modules/platform_integration/linkedin_agent/src/anti_detection_poster.py`
- `modules/platform_integration/x_twitter/src/x_anti_detection_poster.py`

---

## [TOOL] WSP Compliance

- **WSP 3**: Module organization - each platform has its own module
- **WSP 50**: Pre-action verification - check duplicates before posting
- **WSP 84**: Code reuse - use existing orchestrator, don't vibecode
- **WSP 22**: ModLog updates required for all changes