# GJ_00_Vision.md — GotJunk + Liberty Alert Big Picture

## 1. Core Idea

GotJunk is a **progressive web app (PWA)** that looks like a local "Tinder for stuff" but secretly embeds a **Liberty Alert (LA)** mutual-aid and protection layer:

- **Stuff (GotJunk)**
  - People snap photos of items (junk, tools, furniture, etc.)
  - Items appear in:
    - **User Home** (personal inventory, categorized)
    - **Map** (geo-fenced, ~50km "glob" radius)
  - Commerce + Share Economy:
    - 💙 Free
    - 💚 Discount / cheap
    - ⚡ Auction / bid
    - 🔄 Share / lend / lease
    - 🔍 Wanted (borrow / lease / buy)

- **Liberty Alert (LA)**
  - Hidden layer, unlocked via **SOS Morse code** on map (`... ___ ...`)
  - Categories (mutual aid + alerts):
    - 🍞 Food / basic needs (5 subcategories: soup kitchen, BBQ, dry food, pick, garden)
    - 🏠 Housing / shelter (3 subcategories: couch, camping, housing)
    - 🧊 ICE activity
    - 🚓 Police activity / repression
  - Goal: modern "Underground Railroad" / Waze-for-mutual-aid:
    - Community-run food & shelter
    - Real-time ICE/police sightings
    - Secure coordination under surveillance pressure

- **Globs (Geo-Fence Units)**
  - World is partitioned into **local "globs"** (e.g. radius ~50km)
  - You can:
    - See full **Stuff/Food/Shelter** only inside your glob
    - See **Alerts (ICE/police)** globally (read-only outside glob)
  - Posting to a glob requires **local presence + verification**, not VPN tricks.

- **Mesh + Cloud Hybrid**
  - Phone → Mesh (BLE / LoRa / offline gossip) → Optional cloud
  - Cloud (GCP) used for:
    - Light database (Firestore) per glob
    - AI orchestration (vision, summarization, routing)
    - YouTube unlisted video integration
  - Mesh ensures local resilience even if internet is down or censored.

- **Privacy & Safety**
  - No central "user account" in the usual sense.
  - Each device has **public/private keys**, represented as QR.
  - Private key stays **on device** (WebCrypto).
  - LA features gated by:
    - Location verification (anti-VPN spoof)
    - Optional **face + passphrase** combo in future (PWA/WebAuthn).

- **Ephemeral / Evaporating Data**
  - LA chats and messages **decay over time** (disappearing IRC).
  - Alerts have timers (e.g. police 5min, ICE 60min).
  - Data on phone and in cloud is **short-lived**, not a permanent dossier.

---

## 2. Main Workstreams (Each Has Its Own MD)

1. **GJ_10_Chat_and_Message_System.md**
   - Waze-like bulletin boards and per-item chat.
   - LA has richer, invite-only, trust-layered chats.
   - Messages are ephemeral.

2. **GJ_20_Security_and_Identity.md**
   - Keys, QR public IDs, trust tiers (Trusted / Known / New).
   - Anti-VPN location verification.
   - Future: Face + passphrase unlocking, safe key rotation.

3. **GJ_30_Media_YouTube_Integration.md**
   - Short video capture (esp. for LA).
   - Upload as unlisted YouTube videos via backend.
   - Play only inside app, map-filtered by glob & category.

4. **GJ_40_Glob_and_Data_Model.md**
   - Globs, item storage, LA events, AI coordination.
   - How the PWA + minimal backend manage data safely.

Each doc defines **requirements + micro-sprints** that can be fed to 0102 as WSP-compliant build prompts.

---

## 3. Current Implementation Status (2025-11-16)

### ✅ Phase 1 Complete: Liberty Alert Categories & Display Pipeline
- All 16 classification types fully implemented:
  - Commerce (3): free, discount, bid
  - Share Economy (2): share, wanted
  - Mutual Aid Food (6): soup_kitchen, bbq, dry_food, pick, garden, food (deprecated)
  - Mutual Aid Shelter (3): couch, camping, housing
  - Alerts (2): ice, police
- Complete camera → classification → storage → display pipeline working
- ClassificationBadge supports all 16 types with emojis
- MapClusterMarker color-coded for all 16 types
- Dynamic filters in My Items and Browse tabs
- Persistent Liberty unlock via localStorage (SOS morse code)
- Time-based expiration:
  - AlertTimer for ice (60m) and police (5m)
  - StayLimit for couch (1N) and camping (2N)

### 🚧 Phase 2 In Progress: Scheduled Events & UX Polish
- Auto-delete expired alerts (cleanup job)
- Scheduled events (BBQ on weekend, soup kitchen times)
- Event lifecycle visualization (before/during/after)
- Map improvements (global view, better clustering)

### 📋 Phase 3 Planned: Chat, Security, Media
- Ephemeral chat system (GJ_10)
- Keypair identity & trust tiers (GJ_20)
- YouTube video integration (GJ_30)
- Glob-based data architecture (GJ_40)

---

## 4. How to Use These Docs

Each of these MDs (GJ_10, GJ_20, GJ_30, GJ_40) is meant to be:

- **Copied into Claude Code** as context.
- Then **referenced** in per-sprint prompts like:

```txt
Role: You are 0102 working as GotJunk DAE inside the Foundups-Agent repo.
Read WSP_00 and CLAUDE.md. Follow WSP.
Context: [paste specific section from GJ_10 / GJ_20 / GJ_30 / GJ_40].
Task: Implement Sprint X only. No vibecoding. No edits outside listed files.
```

We then walk sprint-by-sprint, pushing PRs and triggering Cloud Build after each.
