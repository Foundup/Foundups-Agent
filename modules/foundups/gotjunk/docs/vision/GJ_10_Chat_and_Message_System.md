# GJ_10_Chat_and_Message_System.md — Message Boards & Ephemeral IRC

## 1. Purpose

Design a **two-layer chat system**:

- **GotJunk Stuff Chat**
  Simple, per-item thread for negotiating, questions, pickup coordination.

- **Liberty Alert Chat (LA Chat)**
  Waze-style, **ephemeral bulletin boards** and **invite-only IRC-like channels**:
  - Only for LA categories (🍞 🏠 🛏️ ⛺ 🧊 🚓).
  - Latest messages at top.
  - Threads auto-evaporate over time.

PWA-first, mesh+cloud hybrid.

---

## 2. Requirements

### 2.1 Common

- Per-item message boards:
  - Thread keyed by **itemId** (Stuff or LA).
  - Messages contain:
    - `messageId`
    - `itemId`
    - `senderPublicKey`
    - `timestamp`
    - `body`
    - `ttl` / `expiresAt`
    - `trustTierSnapshot` (Trusted / Known / New at send time)
- **Ordering**:
  - Latest messages on top.
- **Storage**:
  - Local (IndexedDB/localforage) for offline.
  - Optional sync to Firestore for multi-device & AI.

### 2.2 GotJunk Stuff Chat

- Simple, **public to anyone who can view the item** in the glob.
- No invite system needed.
- TTL longer (e.g. 7–30 days) but still finite (evaporating).
- UI:
  - From item detail (Stuff):
    - "Chat" icon → open thread.
  - Basic text, no encryption UI surfacing (encryption handled under the hood).

### 2.3 LA Chat (Liberty Alert)

- Only for items classified as:
  - 🧊 ICE, 🚓 police, 🍞 food, 🏠/🛏️/⛺ shelter.
- Two modes:
  1. **Open LA bulletin board** (default)
     - Anyone in glob can read & post.
     - Short TTL (e.g. 24–72h; ICE/police even shorter).
  2. **Invite-only LA channel**
     - User can create **private IRC-like room** from full-screen image:
       - "Create LA chat" icon when viewing full-screen LA photo/video.
     - Invite others via:
       - QR scan of public key
       - Selecting contact from local "Known" / "Trusted" list.
     - Only invited keys see and post.
- UI:
  - Full-screen LA media view has:
    - "Chat" icon (open board)
    - "Create LA chat" or "Invite" icon (for private channel)
- Ephemerality:
  - Room TTL (e.g. 7 days) + per-message TTL.
  - Automatic cleanup on device and server.

---

## 3. Micro-Sprints

### Sprint 1 — Local Per-Item Chat (Stuff Only)

**Goal:** Basic chat system for Stuff items, fully local PWA.

- Data model:
  - `Message`, `ItemChatThread` interfaces in `gotjunk/src/types/chat.ts`.
- Storage:
  - Implement `chatStorage` wrapper using IndexedDB (localforage) for:
    - `saveMessage(threadId, message)`
    - `getMessages(threadId)`
    - `pruneExpiredMessages()`
- UI:
  - Add simple **Chat icon** in Stuff item detail.
  - Chat screen: list of messages (newest on top), input box.
- TTL:
  - Base TTL (e.g. 7 days) and scheduled pruning.

**Constraints:** No backend yet, no LA, no mesh.

---

### Sprint 2 — Extend to Liberty Alert Items (Open Bulletin)

**Goal:** Same chat mechanics, but for LA items with shorter TTL.

- Hook classification:
  - Only enable LA chat if classification ∈ {🍞, 🏠, 🛏️, ⛺, 🧊, 🚓}.
- UI:
  - In LA full-screen image view:
    - "Chat" icon to open **LA bulletin board**.
  - Distinct header (e.g. "LA Chat – ICE").
- TTL:
  - ICE/Police: TTL ~ 1–6h.
  - Food/Shelter: TTL ~ 24–72h.
- Storage:
  - Still local only; same `chatStorage` with category-aware TTL.

---

### Sprint 3 — Trust Tiers in Chat (Trusted / Known / New)

**Goal:** Display and eventually use **trust tiers** in chat, even if simple for now.

- Define trust tiers (placeholder):
  - `enum TrustTier { Trusted = 'trusted', Known = 'known', New = 'new' }`
- Store user's **view of each publicKey**:
  - `trustedContacts` in local storage:
    - `{ [publicKey: string]: TrustTier }`
- In message model:
  - Add `senderTrustTier` at send time (snapshot from local map).
- UI:
  - Badge next to sender:
    - Trusted = ⭐
    - Known = ✅
    - New = 👤 or no badge.
- No rating or handshake yet; just display.

---

### Sprint 4 — Invite-Only LA IRC Channels

**Goal:** Waze-like, invite-only LA chats per alert.

- Channel model:
  - `LAChannel`:
    - `channelId`
    - `rootItemId` (LA item)
    - `members: string[]` (publicKeys)
    - `ttl / expiresAt`
- Creation flow:
  - From LA full-screen view:
    - Tap "Create LA Chat" → creates channel with creator as first member.
- Invites:
  - "Invite" action:
    - Show QR of channel + user's key.
    - Or add from local contact list (Trusted/Known/New).
- Access control:
  - Messages in that channel only visible to listed members.
- Storage:
  - Start **local-only** (for PoC; membership and messages just on device).
  - Document future upgrade to mesh/cloud.

---

### Sprint 5 — Ephemeral Cleanup & Mesh/Cloud Hooks

**Goal:** Make chat self-cleaning and ready for mesh integration.

- Cleanup:
  - Background job (on app start + periodic) to:
    - Remove expired messages.
    - Remove expired channels.
- Hooks:
  - Abstract chat I/O through `ChatTransport`:
    - `sendMessage(message)`
    - `onMessage(callback)`
  - Implement:
    - Local transport (no network) now.
    - Future: mesh + Firestore plug-ins.
- Documentation:
  - Update README with flow:
    - PWA → Local storage → Optional mesh/cloud forwarder.

---

## 4. Current Status (2025-11-16)

- ❌ Not yet implemented
- 📋 Awaiting Phase 3 kickoff
- Dependencies: GJ_20 (identity/keys) for trust tiers and invite system
