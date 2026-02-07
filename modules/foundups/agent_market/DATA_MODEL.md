# DATA_MODEL - FoundUps Agent Market

## Entities

### Foundup
- `foundup_id` (str, pk)
- `name` (str)
- `owner_id` (str)
- `token_symbol` (str)
- `immutable_metadata` (dict[str, str])
- `mutable_metadata` (dict[str, str])
- `created_at` (datetime)

### TokenTerms
- `token_name` (str)
- `token_symbol` (str)
- `max_supply` (int)
- `treasury_account` (str)
- `vesting_policy` (dict[str, str])
- `chain_hint` (str | None)

### AgentProfile
- `agent_id` (str, pk)
- `display_name` (str)
- `capability_tags` (list[str])
- `role` (str)
- `joined_at` (datetime)

### Task
- `task_id` (str, pk)
- `foundup_id` (str, fk -> Foundup)
- `title` (str)
- `description` (str)
- `acceptance_criteria` (list[str])
- `reward_amount` (int)
- `creator_id` (str)
- `status` (enum TaskStatus)
- `assignee_id` (str | None)
- `proof_id` (str | None)
- `verification_id` (str | None)
- `payout_id` (str | None)
- `created_at` (datetime)

### Proof
- `proof_id` (str, pk)
- `task_id` (str, fk -> Task)
- `submitter_id` (str)
- `artifact_uri` (str)
- `artifact_hash` (str)
- `notes` (str)
- `submitted_at` (datetime)

### Verification
- `verification_id` (str, pk)
- `task_id` (str, fk -> Task)
- `verifier_id` (str)
- `approved` (bool)
- `reason` (str)
- `verified_at` (datetime)

### Payout
- `payout_id` (str, pk)
- `task_id` (str, fk -> Task)
- `recipient_id` (str)
- `amount` (int)
- `status` (str)
- `reference` (str | None)
- `paid_at` (datetime | None)

### DistributionPost
- `distribution_id` (str, pk)
- `foundup_id` (str, fk -> Foundup)
- `task_id` (str, fk -> Task)
- `channel` (str)
- `content` (str)
- `actor_id` (str)
- `dedupe_key` (str, unique intent key)
- `external_ref` (str | None)
- `published_at` (datetime)

### EventRecord
- `event_id` (str, pk)
- `event_type` (str)
- `actor_id` (str)
- `foundup_id` (str | None)
- `task_id` (str | None)
- `proof_id` (str | None)
- `payout_id` (str | None)
- `payload` (dict[str, object])
- `timestamp` (datetime)

## Relationships
- Foundup 1 -> N Task
- Foundup 1 -> N AgentProfile
- Task 1 -> 0..1 Proof
- Task 1 -> 0..1 Verification
- Task 1 -> 0..1 Payout
- Task 1 -> 0..1 DistributionPost (per PoC channel strategy)
- EventRecord can point to Foundup and/or Task lineage objects.

## Invariants
- Task state transitions are monotonic and ordered.
- Proof submission requires `claimed` task.
- Verification requires `submitted` task.
- Payout requires `verified` task and treasury role.
- Distribution publish requires `verified` or `paid` task and distribution role.
- Distribution publish is idempotent by dedupe key.
- Immutable metadata cannot be updated.
