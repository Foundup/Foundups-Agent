"""Service contracts for FoundUps Agent Market."""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import AgentProfile, DistributionPost, Foundup, Payout, Proof, Task, TokenTerms, Verification


class FoundupRegistryService:
    def create_foundup(self, foundup: Foundup) -> Foundup:
        raise NotImplementedError

    def update_foundup(self, foundup_id: str, updates: Dict[str, str]) -> Foundup:
        raise NotImplementedError

    def get_foundup(self, foundup_id: str) -> Foundup:
        raise NotImplementedError


class TokenFactoryAdapter:
    def deploy_token(self, foundup: Foundup, terms: TokenTerms) -> str:
        raise NotImplementedError

    def configure_vesting(self, token_address: str, terms: TokenTerms) -> None:
        raise NotImplementedError

    def get_treasury_account(self, foundup_id: str) -> str:
        raise NotImplementedError


class AgentJoinService:
    def submit_join_request(self, foundup_id: str, profile: AgentProfile) -> str:
        raise NotImplementedError

    def approve_join_request(self, request_id: str, approver_id: str) -> AgentProfile:
        raise NotImplementedError

    def list_agents(self, foundup_id: str) -> List[AgentProfile]:
        raise NotImplementedError


class TaskPipelineService:
    def create_task(self, task: Task) -> Task:
        raise NotImplementedError

    def claim_task(self, task_id: str, agent_id: str) -> Task:
        raise NotImplementedError

    def submit_proof(self, proof: Proof) -> Task:
        raise NotImplementedError

    def verify_proof(self, task_id: str, verification: Verification) -> Task:
        raise NotImplementedError

    def trigger_payout(self, task_id: str, actor_id: str) -> Payout:
        raise NotImplementedError

    def get_task(self, task_id: str) -> Task:
        raise NotImplementedError

    def get_trace(self, task_id: str) -> Dict[str, object]:
        raise NotImplementedError


class TreasuryGovernanceService:
    def propose_transfer(self, foundup_id: str, amount: int, reason: str, proposer_id: str) -> str:
        raise NotImplementedError

    def approve_transfer(self, proposal_id: str, approver_id: str) -> None:
        raise NotImplementedError

    def execute_transfer(self, proposal_id: str, executor_id: str) -> str:
        raise NotImplementedError

    def get_treasury_state(self, foundup_id: str) -> Dict[str, object]:
        raise NotImplementedError


class CABRHookService:
    def build_cabr_input(self, foundup_id: str, window: str) -> Dict[str, object]:
        raise NotImplementedError

    def record_cabr_output(self, foundup_id: str, payload: Dict[str, object]) -> None:
        raise NotImplementedError


class ObservabilityService:
    def emit_event(self, event_type: str, actor_id: str, payload: Dict[str, object]) -> None:
        raise NotImplementedError

    def query_events(
        self,
        foundup_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        raise NotImplementedError


class DistributionService:
    def build_milestone_payload(self, task_id: str) -> Dict[str, object]:
        raise NotImplementedError

    def publish_verified_milestone(
        self,
        task_id: str,
        actor_id: str,
        channel: str = "moltbook",
        cabr_threshold: float = 0.0,
    ) -> DistributionPost:
        raise NotImplementedError

    def get_distribution(self, task_id: str) -> Optional[DistributionPost]:
        raise NotImplementedError

    def get_latest_cabr_score(self, foundup_id: str) -> Optional[float]:
        raise NotImplementedError


class RepoProvisioningAdapter:
    """Adapter for repository provisioning (GitHub, GitLab, etc)."""

    def provision_repo(
        self,
        foundup_id: str,
        repo_name: str,
        provider: str = "github",
        default_branch: str = "main",
    ) -> str:
        """Provision a repository for the foundup. Returns repo URL."""
        raise NotImplementedError

    def get_repo_metadata(self, foundup_id: str) -> Optional[Dict[str, object]]:
        """Get repository metadata for a foundup."""
        raise NotImplementedError


class MoltbookDistributionAdapter:
    """
    Adapter for Moltbook distribution channel.

    Publishes verified milestone achievements to the Moltbook social layer.
    This is the outbound boundary from FAM to the communication domain.

    WSP 11: Interface contract - implementations in communication domain.
    WSP 72: Module independence - FAM defines interface, moltbot_bridge implements.
    """

    def publish_milestone(
        self,
        foundup_id: str,
        task_id: str,
        milestone_payload: Dict[str, object],
        actor_id: str,
    ) -> Dict[str, object]:
        """
        Publish a verified milestone to Moltbook.

        Args:
            foundup_id: The FoundUp this milestone belongs to
            task_id: The task that was verified
            milestone_payload: Structured payload with proof, verification, etc.
            actor_id: Actor performing the publish

        Returns:
            Dict with publish result: {post_id, channel, timestamp, status}
        """
        raise NotImplementedError

    def get_publish_status(self, post_id: str) -> Optional[Dict[str, object]]:
        """Get status of a published milestone post."""
        raise NotImplementedError

    def list_published_milestones(
        self,
        foundup_id: str,
        limit: int = 10,
    ) -> List[Dict[str, object]]:
        """List published milestones for a FoundUp."""
        raise NotImplementedError
