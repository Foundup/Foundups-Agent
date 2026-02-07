"""In-memory adapter for FoundUps Agent Market PoC."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Optional
from uuid import uuid4

from .exceptions import (
    CABRGateError,
    ImmutableFieldError,
    InvalidStateTransitionError,
    NotFoundError,
    PermissionDeniedError,
)
from .interfaces import (
    AgentJoinService,
    CABRHookService,
    DistributionService,
    FoundupRegistryService,
    ObservabilityService,
    RepoProvisioningAdapter,
    TaskPipelineService,
    TokenFactoryAdapter,
    TreasuryGovernanceService,
)
from .models import (
    AgentProfile,
    DistributionPost,
    EventRecord,
    Foundup,
    Payout,
    PayoutStatus,
    Proof,
    Task,
    TaskStatus,
    TokenTerms,
    Verification,
)


class InMemoryAgentMarket(
    FoundupRegistryService,
    TokenFactoryAdapter,
    AgentJoinService,
    TaskPipelineService,
    TreasuryGovernanceService,
    CABRHookService,
    ObservabilityService,
    DistributionService,
    RepoProvisioningAdapter,
):
    """Single-process PoC adapter with deterministic behavior for tests."""

    def __init__(self, actor_roles: Optional[Dict[str, str]] = None):
        self.actor_roles = actor_roles or {}
        self.foundups: Dict[str, Foundup] = {}
        self.tasks: Dict[str, Task] = {}
        self.proofs: Dict[str, Proof] = {}
        self.verifications: Dict[str, Verification] = {}
        self.payouts: Dict[str, Payout] = {}
        self.events: List[EventRecord] = []
        self.join_requests: Dict[str, tuple[str, AgentProfile]] = {}
        self.agents_by_foundup: Dict[str, List[AgentProfile]] = {}
        self.token_addresses: Dict[str, str] = {}
        self.treasury_accounts: Dict[str, str] = {}
        self.transfer_proposals: Dict[str, Dict[str, object]] = {}
        self.cabr_outputs: Dict[str, List[Dict[str, object]]] = {}
        self.distributions_by_task: Dict[str, DistributionPost] = {}
        self.repos: Dict[str, Dict[str, object]] = {}

    def _role(self, actor_id: str) -> str:
        return self.actor_roles.get(actor_id, "advisory")

    def _require_role(self, actor_id: str, role: str) -> None:
        if self._role(actor_id) != role:
            raise PermissionDeniedError(f"actor '{actor_id}' requires role '{role}'")

    def _emit(
        self,
        event_type: str,
        actor_id: str,
        payload: Dict[str, object],
        foundup_id: Optional[str] = None,
        task_id: Optional[str] = None,
        proof_id: Optional[str] = None,
        payout_id: Optional[str] = None,
    ) -> None:
        event = EventRecord(
            event_id=f"ev_{uuid4().hex[:12]}",
            event_type=event_type,
            actor_id=actor_id,
            payload=payload,
            foundup_id=foundup_id,
            task_id=task_id,
            proof_id=proof_id,
            payout_id=payout_id,
        )
        self.events.append(event)

    # FoundupRegistryService
    def create_foundup(self, foundup: Foundup) -> Foundup:
        self.foundups[foundup.foundup_id] = foundup
        self.agents_by_foundup.setdefault(foundup.foundup_id, [])
        self._emit(
            "foundup.created",
            foundup.owner_id,
            {"name": foundup.name, "token_symbol": foundup.token_symbol},
            foundup_id=foundup.foundup_id,
        )
        return foundup

    def update_foundup(self, foundup_id: str, updates: Dict[str, str]) -> Foundup:
        foundup = self.get_foundup(foundup_id)
        immutable_keys = set(foundup.immutable_metadata.keys())
        for key in updates:
            if key in immutable_keys:
                raise ImmutableFieldError(f"cannot modify immutable key '{key}'")
        foundup.mutable_metadata.update(updates)
        self._emit(
            "foundup.updated",
            foundup.owner_id,
            {"updated_keys": list(updates.keys())},
            foundup_id=foundup_id,
        )
        return foundup

    def get_foundup(self, foundup_id: str) -> Foundup:
        foundup = self.foundups.get(foundup_id)
        if not foundup:
            raise NotFoundError(f"foundup '{foundup_id}' not found")
        return foundup

    # TokenFactoryAdapter
    def deploy_token(self, foundup: Foundup, terms: TokenTerms) -> str:
        token_address = f"token_{foundup.foundup_id}_{terms.token_symbol}".lower()
        self.token_addresses[foundup.foundup_id] = token_address
        self.treasury_accounts[foundup.foundup_id] = terms.treasury_account
        self._emit(
            "token.deployed",
            foundup.owner_id,
            {"token_address": token_address, "max_supply": terms.max_supply},
            foundup_id=foundup.foundup_id,
        )
        return token_address

    def configure_vesting(self, token_address: str, terms: TokenTerms) -> None:
        self._emit(
            "token.vesting_configured",
            "system",
            {"token_address": token_address, "policy": terms.vesting_policy},
        )

    def get_treasury_account(self, foundup_id: str) -> str:
        if foundup_id not in self.treasury_accounts:
            raise NotFoundError(f"treasury account missing for foundup '{foundup_id}'")
        return self.treasury_accounts[foundup_id]

    # AgentJoinService
    def submit_join_request(self, foundup_id: str, profile: AgentProfile) -> str:
        self.get_foundup(foundup_id)
        request_id = f"join_{uuid4().hex[:10]}"
        self.join_requests[request_id] = (foundup_id, profile)
        self._emit(
            "agent.join_requested",
            profile.agent_id,
            {"request_id": request_id, "capability_tags": profile.capability_tags},
            foundup_id=foundup_id,
        )
        return request_id

    def approve_join_request(self, request_id: str, approver_id: str) -> AgentProfile:
        if request_id not in self.join_requests:
            raise NotFoundError(f"join request '{request_id}' not found")
        foundup_id, profile = self.join_requests.pop(request_id)
        self.agents_by_foundup.setdefault(foundup_id, []).append(profile)
        self._emit(
            "agent.join_approved",
            approver_id,
            {"request_id": request_id, "agent_id": profile.agent_id},
            foundup_id=foundup_id,
        )
        return profile

    def list_agents(self, foundup_id: str) -> List[AgentProfile]:
        self.get_foundup(foundup_id)
        return list(self.agents_by_foundup.get(foundup_id, []))

    # TaskPipelineService
    def create_task(self, task: Task) -> Task:
        self.get_foundup(task.foundup_id)
        self.tasks[task.task_id] = task
        self._emit(
            "task.created",
            task.creator_id,
            {"title": task.title, "reward_amount": task.reward_amount},
            foundup_id=task.foundup_id,
            task_id=task.task_id,
        )
        return task

    def get_task(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if not task:
            raise NotFoundError(f"task '{task_id}' not found")
        return task

    def claim_task(self, task_id: str, agent_id: str) -> Task:
        task = self.get_task(task_id)
        if task.status != TaskStatus.OPEN:
            raise InvalidStateTransitionError("task can only be claimed from open state")
        task.status = TaskStatus.CLAIMED
        task.assignee_id = agent_id
        self._emit(
            "task.claimed",
            agent_id,
            {},
            foundup_id=task.foundup_id,
            task_id=task.task_id,
        )
        return task

    def submit_proof(self, proof: Proof) -> Task:
        task = self.get_task(proof.task_id)
        if task.status != TaskStatus.CLAIMED:
            raise InvalidStateTransitionError("proof can only be submitted from claimed state")
        if task.assignee_id and task.assignee_id != proof.submitter_id:
            raise PermissionDeniedError("proof submitter must match task assignee")
        self.proofs[proof.proof_id] = proof
        task.proof_id = proof.proof_id
        task.status = TaskStatus.SUBMITTED
        self._emit(
            "proof.submitted",
            proof.submitter_id,
            {"artifact_uri": proof.artifact_uri},
            foundup_id=task.foundup_id,
            task_id=task.task_id,
            proof_id=proof.proof_id,
        )
        return task

    def verify_proof(self, task_id: str, verification: Verification) -> Task:
        task = self.get_task(task_id)
        self._require_role(verification.verifier_id, "verifier")
        if task.status != TaskStatus.SUBMITTED:
            raise InvalidStateTransitionError("verification requires submitted state")
        if not task.proof_id:
            raise InvalidStateTransitionError("verification requires proof")
        if not verification.approved:
            raise InvalidStateTransitionError("PoC supports approved verification only")
        self.verifications[verification.verification_id] = verification
        task.verification_id = verification.verification_id
        task.status = TaskStatus.VERIFIED
        self._emit(
            "proof.verified",
            verification.verifier_id,
            {"approved": verification.approved, "reason": verification.reason},
            foundup_id=task.foundup_id,
            task_id=task.task_id,
            proof_id=task.proof_id,
        )
        return task

    def trigger_payout(self, task_id: str, actor_id: str) -> Payout:
        task = self.get_task(task_id)
        self._require_role(actor_id, "treasury")
        if task.status != TaskStatus.VERIFIED:
            raise InvalidStateTransitionError("payout requires verified state")
        payout = Payout(
            payout_id=f"pay_{uuid4().hex[:10]}",
            task_id=task.task_id,
            recipient_id=task.assignee_id or "unknown",
            amount=task.reward_amount,
            status=PayoutStatus.COMPLETED,
            reference=f"inmem:{uuid4().hex[:8]}",
            paid_at=task.created_at,
        )
        self.payouts[payout.payout_id] = payout
        task.payout_id = payout.payout_id
        task.status = TaskStatus.PAID
        self._emit(
            "payout.completed",
            actor_id,
            {"amount": payout.amount, "reference": payout.reference},
            foundup_id=task.foundup_id,
            task_id=task.task_id,
            proof_id=task.proof_id,
            payout_id=payout.payout_id,
        )
        return payout

    def get_trace(self, task_id: str) -> Dict[str, object]:
        task = self.get_task(task_id)
        foundup = self.get_foundup(task.foundup_id)
        proof = self.proofs.get(task.proof_id) if task.proof_id else None
        verification = self.verifications.get(task.verification_id) if task.verification_id else None
        payout = self.payouts.get(task.payout_id) if task.payout_id else None
        distribution = self.distributions_by_task.get(task_id)
        events = [
            asdict(e)
            for e in self.events
            if e.task_id == task_id or (e.foundup_id == foundup.foundup_id and e.task_id is None)
        ]
        return {
            "foundup": asdict(foundup),
            "task": asdict(task),
            "proof": asdict(proof) if proof else None,
            "verification": asdict(verification) if verification else None,
            "payout": asdict(payout) if payout else None,
            "distribution": asdict(distribution) if distribution else None,
            "events": events,
        }

    # TreasuryGovernanceService
    def propose_transfer(self, foundup_id: str, amount: int, reason: str, proposer_id: str) -> str:
        self.get_foundup(foundup_id)
        proposal_id = f"prop_{uuid4().hex[:10]}"
        self.transfer_proposals[proposal_id] = {
            "foundup_id": foundup_id,
            "amount": amount,
            "reason": reason,
            "proposer_id": proposer_id,
            "approved": False,
        }
        self._emit(
            "treasury.transfer_proposed",
            proposer_id,
            {"proposal_id": proposal_id, "amount": amount, "reason": reason},
            foundup_id=foundup_id,
        )
        return proposal_id

    def approve_transfer(self, proposal_id: str, approver_id: str) -> None:
        proposal = self.transfer_proposals.get(proposal_id)
        if not proposal:
            raise NotFoundError(f"proposal '{proposal_id}' not found")
        proposal["approved"] = True
        proposal["approver_id"] = approver_id
        self._emit(
            "treasury.transfer_approved",
            approver_id,
            {"proposal_id": proposal_id},
            foundup_id=str(proposal["foundup_id"]),
        )

    def execute_transfer(self, proposal_id: str, executor_id: str) -> str:
        proposal = self.transfer_proposals.get(proposal_id)
        if not proposal:
            raise NotFoundError(f"proposal '{proposal_id}' not found")
        if not proposal.get("approved"):
            raise InvalidStateTransitionError("proposal must be approved before execution")
        reference = f"xfer_{uuid4().hex[:8]}"
        self._emit(
            "treasury.transfer_executed",
            executor_id,
            {"proposal_id": proposal_id, "reference": reference},
            foundup_id=str(proposal["foundup_id"]),
        )
        return reference

    def get_treasury_state(self, foundup_id: str) -> Dict[str, object]:
        self.get_foundup(foundup_id)
        proposals = [
            {"proposal_id": pid, **payload}
            for pid, payload in self.transfer_proposals.items()
            if payload["foundup_id"] == foundup_id
        ]
        return {
            "foundup_id": foundup_id,
            "treasury_account": self.treasury_accounts.get(foundup_id),
            "proposals": proposals,
        }

    # CABRHookService
    def build_cabr_input(self, foundup_id: str, window: str) -> Dict[str, object]:
        self.get_foundup(foundup_id)
        return {
            "foundup_id": foundup_id,
            "window": window,
            "tasks_total": len([t for t in self.tasks.values() if t.foundup_id == foundup_id]),
            "tasks_paid": len(
                [t for t in self.tasks.values() if t.foundup_id == foundup_id and t.status == TaskStatus.PAID]
            ),
            "events_total": len([e for e in self.events if e.foundup_id == foundup_id]),
        }

    def record_cabr_output(self, foundup_id: str, payload: Dict[str, object]) -> None:
        self.get_foundup(foundup_id)
        self.cabr_outputs.setdefault(foundup_id, []).append(payload)
        self._emit(
            "cabr.output_recorded",
            "system",
            payload,
            foundup_id=foundup_id,
        )

    # ObservabilityService
    def emit_event(self, event_type: str, actor_id: str, payload: Dict[str, object]) -> None:
        # Extract foundup_id and task_id from payload if present
        foundup_id = payload.get("foundup_id") if isinstance(payload.get("foundup_id"), str) else None
        task_id = payload.get("task_id") if isinstance(payload.get("task_id"), str) else None
        self._emit(event_type, actor_id, payload, foundup_id=foundup_id, task_id=task_id)

    def query_events(
        self,
        foundup_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        out: List[Dict[str, object]] = []
        for event in self.events:
            if foundup_id and event.foundup_id != foundup_id:
                continue
            if task_id and event.task_id != task_id:
                continue
            out.append(asdict(event))
        return out

    # DistributionService
    def build_milestone_payload(self, task_id: str) -> Dict[str, object]:
        task = self.get_task(task_id)
        foundup = self.get_foundup(task.foundup_id)
        verification = self.verifications.get(task.verification_id) if task.verification_id else None
        return {
            "foundup_id": foundup.foundup_id,
            "foundup_name": foundup.name,
            "task_id": task.task_id,
            "task_title": task.title,
            "task_status": task.status.value,
            "proof_id": task.proof_id,
            "verification_id": task.verification_id,
            "verification_reason": verification.reason if verification else None,
            "assignee_id": task.assignee_id,
            "reward_amount": task.reward_amount,
        }

    def get_latest_cabr_score(self, foundup_id: str) -> Optional[float]:
        """Get latest CABR score for foundup. Returns None if no CABR output recorded."""
        self.get_foundup(foundup_id)
        outputs = self.cabr_outputs.get(foundup_id, [])
        if not outputs:
            return None
        latest = outputs[-1]
        return float(latest.get("score", 0.0))

    def publish_verified_milestone(
        self,
        task_id: str,
        actor_id: str,
        channel: str = "moltbook",
        cabr_threshold: float = 0.0,
    ) -> DistributionPost:
        task = self.get_task(task_id)
        self._require_role(actor_id, "distribution")
        if task.status not in {TaskStatus.VERIFIED, TaskStatus.PAID}:
            raise InvalidStateTransitionError("distribution requires verified or paid state")

        # CABR gate check
        if cabr_threshold > 0.0:
            cabr_score = self.get_latest_cabr_score(task.foundup_id)
            if cabr_score is None:
                raise CABRGateError(
                    f"CABR score missing for foundup '{task.foundup_id}' - distribution blocked"
                )
            if cabr_score < cabr_threshold:
                raise CABRGateError(
                    f"CABR score {cabr_score:.2f} below threshold {cabr_threshold:.2f} - distribution blocked"
                )

        existing = self.distributions_by_task.get(task_id)
        if existing:
            return existing

        payload = self.build_milestone_payload(task_id)
        distribution = DistributionPost(
            distribution_id=f"dist_{uuid4().hex[:10]}",
            foundup_id=task.foundup_id,
            task_id=task.task_id,
            channel=channel,
            content=f"[{payload['foundup_name']}] Milestone verified: {payload['task_title']}",
            actor_id=actor_id,
            dedupe_key=f"{task.task_id}:{channel}:verified",
        )
        self.distributions_by_task[task_id] = distribution
        self._emit(
            "milestone.verified_published",
            actor_id,
            {
                "distribution_id": distribution.distribution_id,
                "channel": channel,
                "dedupe_key": distribution.dedupe_key,
                "cabr_threshold": cabr_threshold,
            },
            foundup_id=task.foundup_id,
            task_id=task.task_id,
            proof_id=task.proof_id,
            payout_id=task.payout_id,
        )
        return distribution

    def get_distribution(self, task_id: str) -> Optional[DistributionPost]:
        self.get_task(task_id)
        return self.distributions_by_task.get(task_id)

    # RepoProvisioningAdapter
    def provision_repo(
        self,
        foundup_id: str,
        repo_name: str,
        provider: str = "github",
        default_branch: str = "main",
    ) -> str:
        """Provision a repository for the foundup. Returns repo URL (in-memory stub)."""
        self.get_foundup(foundup_id)
        repo_url = f"https://{provider}.com/foundups/{repo_name}"
        self.repos[foundup_id] = {
            "foundup_id": foundup_id,
            "repo_name": repo_name,
            "repo_url": repo_url,
            "provider": provider,
            "default_branch": default_branch,
        }
        self._emit(
            "repo.provisioned",
            "system",
            {
                "repo_name": repo_name,
                "repo_url": repo_url,
                "provider": provider,
                "default_branch": default_branch,
            },
            foundup_id=foundup_id,
        )
        return repo_url

    def get_repo_metadata(self, foundup_id: str) -> Optional[Dict[str, object]]:
        """Get repository metadata for a foundup."""
        self.get_foundup(foundup_id)
        return self.repos.get(foundup_id)
