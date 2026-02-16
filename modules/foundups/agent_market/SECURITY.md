# SECURITY - FoundUps Agent Market

## Threat Model (PoC)
- Unauthorized verification/payout actions.
- Fraudulent proof artifacts.
- Replay or duplicate payout attempts.
- Metadata tampering on immutable launch properties.
- Credit bypass on metered execution routes.
- Ledger tampering between debit and recorded workload.

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

7. Compute Access Controls (P0 In-Memory Implemented)
- Metered routes fail closed when `credit_balance < required_credits`.
- Debit, session, and rebate operations require idempotency keys.
- Access denials and successful debits both emit auditable events.
- Operator override (manual credit adjustment) requires explicit reason and audit lineage.

## Known PoC Gaps
- No cryptographic signature verification for proof payloads.
- No external KMS/HSM integration.
- No treasury consensus threshold logic.
- No signed outbound proof for external distribution posts.
- Persistent compute access is merged for registry/task pipeline paths; remaining service paths are pending.

## Required Prototype Hardening
- Add idempotency keys for payout requests.
- Add verifier quorum policy.
- Add tamper-evident event persistence.
- Add compute debit ledger and session lineage checks.
- Add per-actor/per-foundup rate limits on metered endpoints.
