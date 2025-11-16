# GJ_30_Media_YouTube_Integration.md — Unlisted Video for LA

## 1. Purpose

Use **YouTube as a storage backend** for short LA videos (ICE/police, on-the-ground footage), while ensuring:

- Videos are **unlisted** and not easily discovered.
- Playable **only via the app** (no public links surfaced).
- Organized by **glob + category**.
- Connect to LA alerts and chats.

---

## 2. Requirements

- Capture:
  - PWA triggers camera (video mode).
  - Videos must be short (e.g. ≤ 30–60s) for upload cost and safety.
- Upload:
  - Backend service (Node/Cloud Function) using YouTube Data API:
    - Upload video as **unlisted**.
    - Tag with metadata:
      - `globId`
      - `category` (ICE / police / food / shelter)
      - `timestamp`
- Storage:
  - Map item / alert → `youtubeVideoId`.
- Viewing:
  - In app:
    - Full-screen LA view can show video thumbnail.
    - Embedded player, but no share/copy link button.
- Privacy:
  - No user personal data baked into title/description.
  - Glob/city-level labels only (e.g. "LA – ICE – Chicago Area – 2025-11-16").

---

## 3. Micro-Sprints

### Sprint 1 — Backend Upload Skeleton

**Goal:** Minimal backend route to upload a video to YouTube as unlisted.

- Create GCP Cloud Function / Cloud Run service:
  - `POST /api/media/uploadVideo`
    - Input: signed URL or temporary storage reference from app.
    - Behavior:
      - Fetch video from GCS.
      - Call YouTube API with service account channel.
      - Return `youtubeVideoId`.
- Security:
  - Only callable by authenticated app clients (token).
- Docs:
  - Document environment variables, auth, quotas.

---

### Sprint 2 — Frontend Video Capture & Hand-off

**Goal:** Allow PWA to capture video and send to backend.

- PWA:
  - Use `MediaRecorder` and `<video>` capture flow.
  - Allow user to:
    - Record short clip.
    - Review.
    - Confirm to attach to LA alert.
  - On confirm:
    - Upload to GCS (or direct to backend endpoint if supported).
    - Then call `/api/media/uploadVideo` and attach `youtubeVideoId` to LA item.

---

### Sprint 3 — LA View + Playback

**Goal:** Surface video in LA map/detail UI.

- Data model extension:
  - LA item gets `videoRef` (e.g. `youtubeVideoId`).
- UI:
  - Full-screen LA view:
    - If `videoRef` exists:
      - Show video thumbnail.
      - Tap → open embedded player.
- Constraints:
  - Avoid exposing channel name, share URLs, etc. in UI.

---

### Sprint 4 — AI Summaries & Moderation (Optional Later)

**Goal:** Let server-side AI summarize, classify content, and flag abuse.

- Backend:
  - Given `youtubeVideoId`, fetch transcript/frame analysis.
  - Generate:
    - Text summary.
    - Category check (is it actually ICE/police/food?).
- Use:
  - Map overlays of "recent ICE videos".
  - Auto-tagging and abuse detection.

---

## 4. Current Status (2025-11-16)

- ❌ Not yet implemented
- 📋 Awaiting Phase 3 kickoff
- Dependencies:
  - Backend infrastructure (Cloud Functions/Cloud Run)
  - YouTube API service account setup
  - Video capture UI (can reuse existing camera component)
