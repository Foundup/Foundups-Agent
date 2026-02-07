# SECURITY - FoundUps Agent Market

## Threat Model (PoC)
- Unauthorized verification/payout actions.
- Fraudulent proof artifacts.
- Replay or duplicate payout attempts.
- Metadata tampering on immutable launch properties.

## Controls
1. Role Gates
- Verification requires `verifier` role.
- Payout requires `treasury` role.
- Distribution publish requires `distribution` role.

2. State-Gated Transitions
- Lifecycle progression is strict and validated.
- Duplicate transitions are rejected.
- Distribution publish requires verified milestone state and idempotent dedupe key.

3. Proof Integrity Hooks
- Proof requires `artifact_uri` and `artifact_hash`.
- Hash verification plumbing is reserved for adapter implementation.

4. Immutable Launch Metadata
- Immutable keys are write-once.

5. Audit Trail
- Every mutation emits event records with actor and lineage pointers.
- Trace endpoint links payout -> proof -> task -> foundup.

6. Key and Secret Handling
- No secret material is stored in this module.
- Chain/governance adapters must consume secrets through existing secrets infrastructure.

## Known PoC Gaps
- No cryptographic signature verification for proof payloads.
- No external KMS/HSM integration.
- No treasury consensus threshold logic.
- No signed outbound proof for external distribution posts.

## Required Prototype Hardening
- Add idempotency keys for payout requests.
- Add verifier quorum policy.
- Add tamper-evident event persistence.
