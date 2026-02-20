import pytest

from modules.foundups.agent_market.src.exceptions import PermissionDeniedError
from modules.foundups.agent_market.src.in_memory import InMemoryAgentMarket
from modules.foundups.agent_market.src.models import Foundup, Proof, Task, Verification


def _seed_market() -> InMemoryAgentMarket:
    market = InMemoryAgentMarket(actor_roles={"verifier_1": "verifier", "treasury_1": "treasury"})
    market.create_foundup(
        Foundup(
            foundup_id="f_1",
            name="outer layer launch",
            owner_id="owner_1",
            token_symbol="FAM",
            immutable_metadata={"launch_model": "tokenized"},
            mutable_metadata={},
        )
    )
    market.create_task(
        Task(
            task_id="t_1",
            foundup_id="f_1",
            title="proof pipeline",
            description="implement proof pipeline",
            acceptance_criteria=["proof submitted"],
            reward_amount=100,
            creator_id="owner_1",
        )
    )
    market.claim_task("t_1", "agent_1")
    market.submit_proof(
        Proof(
            proof_id="proof_1",
            task_id="t_1",
            submitter_id="agent_1",
            artifact_uri="ipfs://proof",
            artifact_hash="sha256:123",
        )
    )
    return market


def test_only_verifier_can_verify():
    market = _seed_market()
    with pytest.raises(PermissionDeniedError):
        market.verify_proof(
            "t_1",
            Verification(
                verification_id="ver_fail",
                task_id="t_1",
                verifier_id="random_actor",
                approved=True,
                reason="trying to bypass role gate",
            ),
        )


def test_only_treasury_can_trigger_payout():
    market = _seed_market()
    market.verify_proof(
        "t_1",
        Verification(
            verification_id="ver_1",
            task_id="t_1",
            verifier_id="verifier_1",
            approved=True,
            reason="approved",
        ),
    )

    with pytest.raises(PermissionDeniedError):
        market.trigger_payout("t_1", "random_actor")


def test_only_distribution_role_can_publish_verified_milestone():
    market = _seed_market()
    market.verify_proof(
        "t_1",
        Verification(
            verification_id="ver_2",
            task_id="t_1",
            verifier_id="verifier_1",
            approved=True,
            reason="approved",
        ),
    )

    with pytest.raises(PermissionDeniedError):
        market.publish_verified_milestone("t_1", "random_actor")
