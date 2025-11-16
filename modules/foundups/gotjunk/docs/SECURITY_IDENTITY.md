# Identity & Encryption (Design Only)

**Scope:** GotJunk + Liberty Alert mesh + LA chat  
**Status:** Design only – do **not** implement in current sprints  
**WSP Guardrails:** WSP 49 (docs), WSP 50 (pre-action), WSP 84 (evolve modules), WSP 96 (skill catalog)

## 1) Per-User Crypto Identity
- Each user holds a keypair on-device only (private key never leaves device).
- Likely types: `ed25519` (signatures) + `x25519` (encryption).
- Store keys in OS secure storage (Keychain/Secure Enclave, Android Keystore).
- Rotation supported (mark legacy-encrypted messages as needed).
- Server/mesh sees only public keys and signatures.

## 2) Device Auth: Face ID + Spoken Passphrase (2FA on decrypt)
- To use private key: require OS biometric **and** on-device spoken passphrase check.
- No raw audio stored; only a derived hash/embedding, validated locally.
- Private key stays locked; short-lived in-memory access or session key unwrap after both checks.
- Applies to LA chats and sensitive Liberty Alerts.

## 3) LA Chat Encryption (Future E2EE)
- Each LA chat/thread gets a session key (X3DH-style or group key wrapped per participant).
- Messages encrypted client-side; servers/mesh relay ciphertext + metadata only.
- Ephemeral: tied to alert timers/TTL; purge on expiry (best-effort server + device).
- GotJunk item chat PoC can start non-E2EE, upgrade later with same architecture.

## 4) Blockchain Integration (Later)
- On-chain identity record: publicKey, reputationScore, meshStake.
- Staking/earn for Liberty Alert mesh relays (HELTEC/LoRa, etc.).
- Private keys stay on-device; chain sees signatures and public keys only.

## 5) User Types (Placeholder)
- `trusted`, `known`, `new` enums only—no enforcement yet. Used later for routing/permissions.

## 6) Future Sprint Markers (Do Not Build Now)
- `SEC-0`: Land this spec doc and references.
- `SEC-1`: On-device keypair + secure storage (no UI).
- `SEC-2`: E2EE LA chat PoC.
- `SEC-3`: FaceID + spoken passphrase gate for key unlock.
- `SEC-4`: Blockchain identity mapping (public keys + minimal reputation).

### Implementation Notes for 0102 (Now)
- Do **not** add crypto/biometric/blockchain code in current GotJunk/LA sprints.
- You may add placeholders/types (`UserIdentity`, `EncryptionProfile`) and TODOs.
- Reference this doc in relevant modules (mesh, LA chat, user model) as the north star.
