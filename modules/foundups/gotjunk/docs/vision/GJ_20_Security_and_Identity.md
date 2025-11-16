# GJ_20_Security_and_Identity.md — Keys, Verification, VPN, Face+Passphrase

## 1. Purpose

Define **identity, trust, and security** foundations:

- Each device has a **keypair** (public/private).
- Public key is exposed as **QR** and used in chats, invites, LA channels.
- Private key is encrypted and stays on device.
- Liberty Alerts require **location verification** to defeat VPN spoofing.
- Future: optional **face + passphrase** to unlock LA & key operations.

---

## 2. Requirements

### 2.1 Identity & Keys

- Keypair:
  - Generate with WebCrypto (Ed25519 or similar).
  - Store encrypted private key in IndexedDB.
- Public identity:
  - Represent user as:
    - `publicKey`
    - Optional display name / nickname (local only).
  - Show as QR code for:
    - Adding contacts.
    - Inviting to LA channels.
- Key rotation:
  - User can **rotate keys** (new keypair).
  - For backward compatibility:
    - Device keeps list of **old keys** linked to primary identity.
    - Can still decrypt old messages / verify old signatures.
    - New interactions use latest key.

### 2.2 Trust Tiers

- Per publicKey:
  - Locally assign tier:
    - Trusted / Known / New.
- Mapping is **only on the device**; never synced as a global reputation.
- Used for:
  - Chat UI badges.
  - Invites and filters.
  - Later: handshake escrow ratings.

### 2.3 Location Verification vs VPN

- Problem:
  - User could be on VPN and fake IP location.
- Strategy:
  - Use **GPS + image-based verification** for LA posting:
    - Before user can post certain LA alerts (ICE/police, critical shelter):
      - Prompt: "Verify location"
      - Ask user to take a picture of surroundings (e.g. street, signs).
    - App collects:
      - GPS location (device geolocation).
      - The image.
    - Backend AI:
      - Compares image context with GPS region (e.g. signs, landmarks).
      - If plausible: issue a **signed location proof** for this device/glob.
    - Once proof is issued:
      - User can turn VPN on, but **LA posts still tied to verified glob**.

---

## 3. Micro-Sprints

### Sprint 1 — Local Keypair & QR Identity

**Goal:** Basic keypair and QR identity, PWA-local.

- Implement `IdentityService`:
  - `getOrCreateKeypair()`
  - `getPublicKey()`
  - `rotateKeypair()`
  - `listHistoricalKeys()`
- Storage:
  - Encrypted private key using a locally derived key (simple PIN/password for now or system key if available).
- UI:
  - "My ID" screen:
    - Show QR with publicKey.
    - Basic export options (e.g. copy string).

---

### Sprint 2 — Trust Tier Management

**Goal:** Local trust tier editing.

- Model:
  - `TrustTier` enum and mapping: `{ [publicKey: string]: TrustTier }`.
- UI:
  - In any chat, tap on user identity → open "Trust Settings":
    - Set as Trusted / Known / New.
- Storage:
  - Local only (IndexedDB/localforage).
- Effects:
  - Chat messages show trust badges as per Sprint 3 in chat doc.

---

### Sprint 3 — Location Verification Proof (Anti-VPN LA Gate)

**Goal:** Define and implement the **Verify Location** flow for LA posts.

- Data model:
  - `LocationProof`:
    - `proofId`
    - `devicePublicKey`
    - `globId`
    - `gpsLat`, `gpsLng`, `accuracy`
    - `imageRef` (local + cloud path)
    - `issuedAt`
    - `expiresAt`
    - `serverSignature` (if backend issues cryptographic proof)
- Flow:
  1. User tries to post critical LA alert (ICE/police/shelter).
  2. App checks for valid `LocationProof` for current glob.
  3. If missing/expired:
     - App prompts: "Verify location by taking a picture of your surroundings."
     - Capture image + GPS, send to backend.
  4. Backend:
     - Runs image/geolocation checks.
     - Returns a signed `LocationProof`.
  5. App stores proof locally and uses it for:
     - Allowing LA posts in that glob while proof valid.

- UI:
  - "Verify location" call-to-action for LA.

---

### Sprint 4 — Key Rotation & Backward Compatibility

**Goal:** Let users rotate keys without losing old chats.

- IdentityService:
  - Maintain:
    - `currentPublicKey`
    - `historicalKeys[]`
  - When sending new messages:
    - Sign with current key.
  - When reading:
    - Accept messages from any known key in `current + historical`.
- LA channels / chats:
  - Use **stable local identity ID** so user still recognized in membership, even if key rotated.
- Security:
  - Old keys can be optionally "retired":
    - Kept only for decryption of old content.
    - No longer advertised in QR or invites.

---

### Sprint 5 — Future: Face + Passphrase (Design Only, No Implementation)

**Goal:** Document a future **2-factor local unlock** for LA & keys.

- Concept:
  - Use **WebAuthn / platform authenticator** for biometric (FaceID, etc).
  - Combine with a **spoken or typed passphrase** to unlock:
    - LA area
    - Key rotation
    - Identity export
- PWA Constraints:
  - Not all devices support WebAuthn + biometrics in browser.
  - Must gracefully degrade:
    - If unsupported: use passphrase/PIN only.
- Documentation only in this sprint:
  - Add section to this MD.
  - Add TODO in architecture.

---

## 4. Current Status (2025-11-16)

- ❌ Not yet implemented
- 📋 Awaiting Phase 3 kickoff
- ⚠️ Critical dependency for LA chat invite system (GJ_10)
- ⚠️ Location verification needed for anti-VPN measures
