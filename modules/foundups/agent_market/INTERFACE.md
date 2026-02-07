# INTERFACE - FoundUps Agent Market

## Module Contract
FoundUps Agent Market exposes stable contracts for launching tokenized FoundUps and coordinating task execution with auditable payout flow.

## Core Schemas

### Foundup
```python
Foundup(
    foundup_id: str,
    name: str,
    owner_id: str,
    token_symbol: str,
    immutable_metadata: dict[str, str],
    mutable_metadata: dict[str, str],
)
```

### TokenTerms
```python
TokenTerms(
    token_name: str,
    token_symbol: str,
    max_supply: int,
    treasury_account: str,
    vesting_policy: dict[str, str],
    chain_hint: str | None = None,
)
```

### AgentProfile
```python
AgentProfile(
    agent_id: str,
    display_name: str,
    capability_tags: list[str],
    role: str,
)
```

### Task
```python
Task(
    task_id: str,
    foundup_id: str,
    title: str,
    description: str,
    acceptance_criteria: list[str],
    reward_amount: int,
    creator_id: str,
    status: TaskStatus,
)
```

### Proof
```python
Proof(
    proof_id: str,
    task_id: str,
    submitter_id: str,
    artifact_uri: str,
    artifact_hash: str,
    notes: str,
)
```

### Verification
```python
Verification(
    verification_id: str,
    task_id: str,
    verifier_id: str,
    approved: bool,
    reason: str,
)
```

### Payout
```python
Payout(
    payout_id: str,
    task_id: str,
    recipient_id: str,
    amount: int,
    status: str,
    reference: str | None,
)
```

### DistributionPost
```python
DistributionPost(
    distribution_id: str,
    foundup_id: str,
    task_id: str,
    channel: str,
    content: str,
    actor_id: str,
    dedupe_key: str,
    external_ref: str | None = None,
)
```

## Service Contracts

### FoundupRegistryService
- `create_foundup(foundup: Foundup) -> Foundup`
- `update_foundup(foundup_id: str, updates: dict[str, str]) -> Foundup`
- `get_foundup(foundup_id: str) -> Foundup`
- Invariant: immutable metadata keys cannot be changed after creation.

### TokenFactoryAdapter (Chain-Agnostic)
- `deploy_token(foundup: Foundup, terms: TokenTerms) -> str`
- `configure_vesting(token_address: str, terms: TokenTerms) -> None`
- `get_treasury_account(foundup_id: str) -> str`
- Invariant: adapter must not leak chain-specific assumptions into upstream API.

### AgentJoinService
- `submit_join_request(foundup_id: str, profile: AgentProfile) -> str`
- `approve_join_request(request_id: str, approver_id: str) -> AgentProfile`
- `list_agents(foundup_id: str) -> list[AgentProfile]`

### TaskPipelineService
- `create_task(task: Task) -> Task`
- `claim_task(task_id: str, agent_id: str) -> Task`
- `submit_proof(proof: Proof) -> Task`
- `verify_proof(task_id: str, verification: Verification) -> Task`
- `trigger_payout(task_id: str, actor_id: str) -> Payout`
- `get_task(task_id: str) -> Task`
- `get_trace(task_id: str) -> dict[str, object]`
- Invariant: transitions are strictly `open -> claimed -> submitted -> verified -> paid`.

### TreasuryGovernanceService
- `propose_transfer(foundup_id: str, amount: int, reason: str, proposer_id: str) -> str`
- `approve_transfer(proposal_id: str, approver_id: str) -> None`
- `execute_transfer(proposal_id: str, executor_id: str) -> str`
- `get_treasury_state(foundup_id: str) -> dict[str, object]`

### CABRHookService
- `build_cabr_input(foundup_id: str, window: str) -> dict[str, object]`
- `record_cabr_output(foundup_id: str, payload: dict[str, object]) -> None`

### ObservabilityService
- `emit_event(event_type: str, actor_id: str, payload: dict[str, object]) -> None`
- `query_events(foundup_id: str | None = None, task_id: str | None = None) -> list[dict[str, object]]`

### DistributionService
- `build_milestone_payload(task_id: str) -> dict[str, object]`
- `publish_verified_milestone(task_id: str, actor_id: str, channel: str = "moltbook", cabr_threshold: float = 0.0) -> DistributionPost`
- `get_distribution(task_id: str) -> DistributionPost | None`
- `get_latest_cabr_score(foundup_id: str) -> float | None`
- Invariant: publish is allowed only from `verified` or `paid` task states and is idempotent per `task_id + channel + milestone`.
- CABR Gate: If `cabr_threshold > 0`, publish requires CABR score >= threshold. Missing score raises `CABRGateError`.

### RepoProvisioningAdapter
- `provision_repo(foundup_id: str, repo_name: str, provider: str = "github", default_branch: str = "main") -> str`
- `get_repo_metadata(foundup_id: str) -> dict[str, object] | None`
- Invariant: In-memory PoC returns deterministic URL pattern `https://{provider}.com/foundups/{repo_name}`.

### LaunchOrchestrator
- `launch_foundup(foundup: Foundup, token_terms: TokenTerms | None, repo_name: str | None, ...) -> LaunchResult`
- Steps: (1) validate/create Foundup, (2) token deploy, (3) repo provision, (4) initial task create (when task pipeline adapter provided), (5) emit events
- Returns `LaunchResult` with all artifacts and auditable `LaunchEvent` list.

### MoltbookDistributionAdapter
- `publish_milestone(foundup_id: str, task_id: str, milestone_payload: dict, actor_id: str) -> dict`
- `get_publish_status(post_id: str) -> dict | None`
- `list_published_milestones(foundup_id: str, limit: int = 10) -> list[dict]`
- Invariant: Interface defined in FAM, implementation in `moltbot_bridge` domain.
- Stub implementation stores in-memory. Production pushes to Discord/Moltbook.

## OpenClaw/FAM Integration

### FAMAdapter (moltbot_bridge)
The `FAMAdapter` in `moltbot_bridge/src/fam_adapter.py` provides the OpenClaw -> FAM boundary:

- `FAMLaunchRequest`: Dataclass for launch parameters
- `FAMLaunchResponse`: Dataclass for launch results
- `FAMAdapter.launch_foundup(request, actor_id) -> FAMLaunchResponse`
- `FAMAdapter.parse_launch_intent(message, sender) -> FAMLaunchRequest | None`
- `handle_fam_intent(message, sender) -> str`: Entry point for OpenClaw routing

OpenClaw routes `IntentCategory.FOUNDUP` intents to `fam_adapter` domain.

## Optional API Surface (Future)
- `POST /foundups`
- `PATCH /foundups/{foundup_id}`
- `POST /foundups/{foundup_id}/agents/join`
- `POST /tasks`
- `POST /tasks/{task_id}/claim`
- `POST /tasks/{task_id}/proof`
- `POST /tasks/{task_id}/verify`
- `POST /tasks/{task_id}/payout`
- `GET /tasks/{task_id}/trace`

## Event Contract (Audit)
Every mutation emits an event containing:
- `event_id`, `event_type`, `timestamp`, `actor_id`
- `foundup_id`, optional `task_id`, optional `proof_id`, optional `payout_id`
- `payload` (small structured dict)

## Permission Rules (PoC)
- Task verification allowed only for actor role `verifier`.
- Payout trigger allowed only for actor role `treasury`.
- Distribution publish allowed only for actor role `distribution`.
- Non-compliant actor/action pair raises `PermissionDeniedError`.

## OpenClaw/WRE Integration Boundary
FAM is callable as a domain module by OpenClaw routing and WRE orchestration. It does not own ingress/auth policy. It owns domain validation and state transitions.
