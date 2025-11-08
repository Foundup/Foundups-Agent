# GotJunk + Liberty Alert DAEmon Monitoring

## Occam's Razor: What Beats Matter?

Following **first principles**, every user action in GotJunk/Liberty Alert is a **beat** that forms a chain:

```
SOS Unlock → Voice Detection → Ice Cube Creation → Video Upload → Mesh Broadcast
```

Each beat can **succeed** or **fail**. AI Overseer monitors these beats using **WSP 77 (Gemma→Qwen→0102)** coordination.

---

## 5 Monitored Beat Flows

### 1. **SOS Unlock Beat**
**User Flow**: Tap gallery icon in morse code pattern `...___...` to unlock Liberty Alert

**Events**:
- `gallery_icon_tap` - User taps gallery icon
- `sos_pattern_detected` - Pattern matches SSSLLLSSS
- `liberty_alert_enabled` - 🗽 badge appears

**Metrics**:
- **Tap Accuracy**: % of correct SOS patterns
- **False Positives**: Gallery opens during SOS attempt
- **Unlock Rate**: Successful unlocks / total attempts

**Error Patterns**:
- `sos_false_positive` (P2) - Gallery opens too early
- Qwen auto-fix: Increase timeout window

---

### 2. **Voice Detection Beat**
**User Flow**: Record 10-second video, say keywords, Web Speech API detects

**Events**:
- `recording_started` - User presses camera orb
- `voice_listening_started` - Web Speech API initialized
- `keyword_detected` - ICE/immigration/checkpoint/etc heard
- `recording_stopped` - 10 seconds elapsed

**Metrics**:
- **Detection Accuracy**: Keywords detected / keywords spoken
- **False Positives**: Non-keyword triggers
- **Latency**: Time from keyword to detection

**Error Patterns**:
- `web_speech_api_not_supported` (P1) - Browser incompatibility
- `keyword_false_negative` (P1) - Missed keyword detection
- Qwen creates bug reports for 0102 review

---

### 3. **Ice Cube Creation Beat**
**User Flow**: Keyword detected → Ice cube 🧊 marker added to map at user location

**Events**:
- `keyword_detected` - Voice trigger confirmed
- `geolocation_captured` - User's lat/lon obtained
- `alert_created` - LibertyAlert object created
- `ice_cube_added_to_map` - Marker appears on map

**Metrics**:
- **Creation Success Rate**: Alerts created / keywords detected
- **Geolocation Failures**: Failed location captures
- **Video Link Integrity**: Video URLs valid

**Error Patterns**:
- `geolocation_permission_denied` (P0) - Location permission missing
- Qwen auto-fix: Show permission prompt modal

---

### 4. **Video Upload Beat**
**User Flow**: 10-second video uploads to YouTube as unlisted, URL stored with alert

**Events**:
- `video_recorded` - MediaRecorder completes
- `upload_started` - YouTube API call initiated
- `youtube_api_called` - API request sent
- `upload_completed` - YouTube returns video URL
- `video_linked_to_alert` - URL attached to ice cube alert

**Metrics**:
- **Upload Success Rate**: Successful uploads / total videos
- **Upload Latency**: Time from recording to YouTube URL
- **API Quota Usage**: YouTube API calls per hour

**Error Patterns**:
- `youtube_upload_failed` (P0) - Upload error or quota exhausted
- Qwen creates bug report: Implement local storage fallback + retry queue

---

### 5. **Mesh Broadcast Beat**
**User Flow**: Alert broadcasts to nearby Liberty Alert users via existing mesh network

**Events**:
- `alert_created` - New ice cube alert ready
- `mesh_broadcast_started` - WebRTC broadcast initiated
- `peers_notified` - Connected peers receive alert
- `broadcast_confirmed` - Peers acknowledge receipt

**Metrics**:
- **Broadcast Success Rate**: Peers notified / total peers
- **Network Latency**: Time to reach all peers
- **Peer Count**: Active mesh connections

**Error Patterns**:
- `mesh_broadcast_timeout` (P1) - WebRTC connection failures
- Qwen creates bug report: Add exponential backoff + reconnection

---

## WSP 15 MPS Scoring (Module Prioritization Score)

**Formula**: `MPS = Complexity + Importance + Deferability + Impact`

**Priority Mapping**:
- **P0**: MPS 17-20 (Essential, cannot defer, transformative)
- **P1**: MPS 13-16 (Critical, difficult to defer, major impact)
- **P2**: MPS 9-12 (Important, moderate urgency)
- **P3**: MPS 5-8 (Nice to have, low urgency)
- **P4**: MPS 1-4 (Backlog, minimal impact)

---

## AI Overseer Integration

### Phase 1: Gemma (Fast Detection)
- Regex pattern matching <100ms
- Detects error patterns from console logs
- Example: `"Web Speech API not supported"`

### Phase 2: Qwen (MPS Scoring + Decision)
- Calculates WSP 15 MPS score
- **Complexity 1-2**: Auto-fix (no 0102 needed)
- **Complexity 3+**: Create bug report for 0102

### Phase 3: Learning
- Store patterns in `gotjunk_daemon_monitor.json`
- Update accuracy metrics
- Improve detection over time

---

## Monitored Error Patterns (7 Total)

| Error Pattern | Priority | Complexity | Qwen Action | Needs 0102? |
|---------------|----------|------------|-------------|-------------|
| `camera_permission_denied` | P0 | 2 | auto_fix | ❌ |
| `geolocation_permission_denied` | P0 | 2 | auto_fix | ❌ |
| `youtube_upload_failed` | P0 | 3 | bug_report | ✅ |
| `web_speech_api_not_supported` | P1 | 3 | bug_report | ✅ |
| `mesh_broadcast_timeout` | P1 | 4 | bug_report | ✅ |
| `keyword_false_negative` | P1 | 5 | bug_report | ✅ |
| `sos_false_positive` | P2 | 2 | auto_fix | ❌ |

---

## Implementation Status

### ✅ Completed:
- DAEmon monitor skill created: `skills/gotjunk_daemon_monitor.json`
- 5 beat flows defined (SOS → Voice → Ice Cube → Video → Mesh)
- 7 error patterns with WSP 15 MPS scoring
- Qwen decision logic (auto-fix vs bug report)

### 🔄 Next Steps:
1. Integrate AI Overseer monitoring
2. Add console logging for all beats
3. Test error detection accuracy
4. Deploy to Cloud Run with monitoring enabled

---

## Architecture: Beats as First Principles

**Every action = Beat**
**Every beat = Success or Failure**
**Every failure = Monitored by AI Overseer**

```
User Tap → SOS Detection → Liberty Unlock → Voice Listening → Keyword Detection
   ↓            ↓                ↓                ↓                  ↓
(Beat 1)    (Beat 2)         (Beat 3)         (Beat 4)          (Beat 5)
   ↓            ↓                ↓                ↓                  ↓
Success?    Success?         Success?         Success?          Success?
   ↓            ↓                ↓                ↓                  ↓
If Fail → Gemma Detects → Qwen Scores → Auto-Fix or Report → 0102 Reviews
```

This is **Occam's Razor applied to monitoring**: Monitor the minimal set of critical beats that determine success/failure.

---

**Created**: 2025-11-03
**WSP Compliance**: WSP 77 (Agent Coordination), WSP 15 (MPS Scoring), WSP 96 (Skills), WSP 3 (FoundUp Structure)
