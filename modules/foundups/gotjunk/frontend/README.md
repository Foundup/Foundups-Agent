<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# GotJunk Frontend

## Architecture

- Capture & Classification: Camera → ClassificationModal → IndexedDB → Firestore (optional sync)
- State: React hooks + IndexedDB persistence (storage.ts) + messaging store
- UI: Framer Motion animations, Tailwind-like utility classes
- Auth & Sync: Firebase auth (anonymous + Google). Firestore sync uses `ownerUid` for cross-device identity. Deploy `firestore.rules` to enforce owner-only writes/updates.

## Run Locally

**Prerequisites:** Node.js

1. Install dependencies:
   `npm install`
2. Set Firebase config in `.env` (see `.env.example`):
   - `VITE_FIREBASE_API_KEY`
   - `VITE_FIREBASE_APP_ID`
   - `VITE_FIREBASE_SENDER_ID`
3. Run the app:
   `npm run dev`

## Firebase Rules

Deploy from the frontend module (uses `firebase.json` + `firestore.rules` in this folder):

```bash
cd modules/foundups/gotjunk/frontend
firebase deploy --only firestore:rules
```

Rules enforce authenticated writes and owner-only updates for items and messages; reads are public by default (adjust to your policy).
