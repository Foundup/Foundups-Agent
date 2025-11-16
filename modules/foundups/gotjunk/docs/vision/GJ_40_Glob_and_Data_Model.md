# GJ_40_Glob_and_Data_Model.md — Globs, Database, AI Coordination

## 1. Purpose

Define how data (items, alerts, chats) is stored and coordinated between:

- **PWA (client)** — local IndexedDB.
- **Mesh network** — BLE/LoRa/gossip (GotJunk mesh modules).
- **Cloud backend** — GCP (Firestore/Storage/Functions).
- **AI** — Cloud models using data snapshots.

---

## 2. Globs

- Glob definition:
  - `globId` based on lat/lng (e.g. geohash+radius).
- Rules:
  - User sees entire **Stuff/Food/Shelter** inventory for their current glob.
  - User can see **alerts** globally (read-only outside glob).
  - User can only create alerts if:
    - Inside that glob + have `LocationProof`.

---

## 3. Data Storage Strategy

### Local (PWA)

- IndexedDB/localforage used for:
  - Items posted by user.
  - Cached items for current glob.
  - Chats & LA channels.
  - Identity & trust tiers.
  - Location proofs.

### Mesh

- Mesh packets (from `meshCore`) carry:
  - Small LA events (ICE/police).
  - Possibly minimal text for food/shelter.
- Gateway nodes (Heltec / phones):
  - Bridge mesh to cloud when online.

### Cloud

- Firestore collections (sketch):
  - `globs/{globId}/items` (Stuff/Food/Shelter)
  - `globs/{globId}/alerts` (ICE/police events, video references)
  - `globs/{globId}/stats` (for AI)
- Storage:
  - GCS buckets for images and raw videos.
- AI:
  - Periodic or event-triggered:
    - Summarize needs per glob.
    - Detect patterns (spike in ICE events, food shortages, etc.).

---

## 4. Micro-Sprints

### Sprint 1 — Glob ID + Local Filtering

**Goal:** Formalize globs and filter items purely client-side.

- Implement `globId` function from lat/lng.
- Tag items with `globId` at creation.
- Map & list views filter on `globId == current`.

---

### Sprint 2 — Firestore Skeleton

**Goal:** Minimal Firestore integration.

- Add config for Firestore in GCP (via console).
- Implement:
  - `uploadItemMetadata(item)` → `globs/{globId}/items/{itemId}`
  - `listenToGlobItems(globId)` for:
    - Stuff/Food/Shelter (but no chat yet).
- Keep writes minimal; rely primarily on PWA local cache.

---

### Sprint 3 — Alert Storage & TTL in Firestore

**Goal:** Store LA alerts centrally with timers.

- Data:
  - `alertId`, `globId`, `category`, `location`, `time`, `expiresAt`, optional `videoRef`.
- Add Cloud Function to periodically:
  - Delete or mark expired alerts.
- Client respects `expiresAt` regardless of local misbehavior.

---

### Sprint 4 — AI Coordination Hooks (Design-Only or Minimal)

**Goal:** Prepare hooks for AI to coordinate needs.

- For each glob, AI should be able to compute:
  - Active needs:
    - # of food requests
    - # of shelter offers vs requests
    - ICE/police heat
- Implement:
  - `globs/{globId}/stats` document that AI updates.
- PWA:
  - Reads stats to show at a glance:
    - "High food need in this area"
    - "Shelter available nearby"

---

## 5. Current Status (2025-11-16)

- ✅ Local storage (IndexedDB) fully implemented
- ✅ GlobId calculation based on ~50km radius
- ✅ Local filtering by globId working
- ❌ Firestore integration not yet started
- ❌ Mesh network integration pending
- 📋 Awaiting Phase 3 kickoff for cloud backend

---

## 6. Current Implementation Details

### Implemented (Phase 1)
- **Local Storage**: All items stored in IndexedDB via localforage
- **Geo-filtering**: Haversine distance calculation with 50km radius
- **Classification System**: 16 types across 4 pillars (Commerce, Share, Mutual Aid, Alerts)
- **TTL System**: AlertTimer and StayLimit for time-based expiration

### Data Model (Current)
```typescript
interface CapturedItem {
  id: string;
  blobUrl: string;
  thumbnail?: string;
  videoUrl?: string;
  latitude: number;
  longitude: number;
  timestamp: number;
  ownership: 'mine' | 'others';
  status: 'draft' | 'listed' | 'sold';
  classification?: ItemClassification; // 16 types

  // Commerce metadata
  price?: number;
  discountPercent?: number;
  bidDurationHours?: number;

  // LA metadata
  alertTimer?: {
    type: 'ice' | 'police';
    startTime: number;
    durationMinutes: number;
    expiresAt: number;
  };
  stayLimit?: {
    type: 'couch' | 'camping';
    nights: number;
  };

  // Future: chat, video, trust tier
  description?: string;
  createdAt: number;
  userId?: string;
}
```

### Next Phase Requirements
- Firestore schema matching local model
- Sync strategy (local-first with cloud backup)
- Conflict resolution for multi-device
- Mesh packet format for offline propagation
