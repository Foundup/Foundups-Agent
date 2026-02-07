"""Tests for launch orchestrator."""

import pytest

from modules.foundups.agent_market.src.in_memory import InMemoryAgentMarket
from modules.foundups.agent_market.src.models import Foundup, TokenTerms
from modules.foundups.agent_market.src.orchestrator import LaunchOrchestrator, launch_foundup


def test_launch_foundup_happy_path_full():
    """launch_foundup executes full happy path with all options."""
    market = InMemoryAgentMarket()

    foundup = Foundup(
        foundup_id="f_launch_1",
        name="Launch Test Foundup",
        owner_id="owner_1",
        token_symbol="LAUNCH",
        immutable_metadata={"launch_model": "tokenized"},
        mutable_metadata={},
    )

    token_terms = TokenTerms(
        token_name="Launch Token",
        token_symbol="LAUNCH",
        max_supply=1_000_000,
        treasury_account="treasury_1",
        vesting_policy={"cliff": "6m", "duration": "24m"},
    )

    initial_task_params = {
        "task_id": "task_init_1",
        "title": "Initial Setup Task",
        "description": "Complete initial foundup setup",
        "acceptance_criteria": ["Setup complete", "Tests passing"],
        "reward_amount": 500,
    }

    result = launch_foundup(
        registry=market,
        token_adapter=market,
        repo_adapter=market,
        task_pipeline=market,
        foundup=foundup,
        token_terms=token_terms,
        repo_name="foundups-launch-test",
        initial_task_params=initial_task_params,
        actor_id="launcher_1",
        observability=market,
    )

    # Verify success
    assert result.success is True
    assert result.error is None

    # Verify foundup created
    assert result.foundup.foundup_id == "f_launch_1"
    stored_foundup = market.get_foundup("f_launch_1")
    assert stored_foundup.name == "Launch Test Foundup"

    # Verify token deployed
    assert result.token_address is not None
    assert "launch" in result.token_address.lower()

    # Verify repo provisioned
    assert result.repo_url is not None
    assert "foundups-launch-test" in result.repo_url

    # Verify initial task created in task pipeline
    assert result.initial_task is not None
    assert result.initial_task.title == "Initial Setup Task"
    assert result.initial_task.reward_amount == 500
    assert market.get_task("task_init_1").title == "Initial Setup Task"

    # Verify events recorded
    assert len(result.events) >= 4  # created, token, repo, task, complete
    event_types = [e.event_type for e in result.events]
    assert "launch.foundup_created" in event_types
    assert "launch.token_deployed" in event_types
    assert "launch.repo_provisioned" in event_types
    assert "launch.initial_task_created" in event_types
    assert "launch.complete" in event_types


def test_launch_foundup_minimal():
    """launch_foundup works with minimal required inputs."""
    market = InMemoryAgentMarket()

    foundup = Foundup(
        foundup_id="f_minimal",
        name="Minimal Foundup",
        owner_id="owner_1",
        token_symbol="MIN",
        immutable_metadata={},
        mutable_metadata={},
    )

    result = launch_foundup(
        registry=market,
        token_adapter=market,
        foundup=foundup,
    )

    assert result.success is True
    assert result.token_address is None  # No token terms provided
    assert result.repo_url is None  # No repo name provided
    assert result.initial_task is None  # No task params provided

    # Should still have created and complete events
    event_types = [e.event_type for e in result.events]
    assert "launch.foundup_created" in event_types
    assert "launch.complete" in event_types


def test_launch_foundup_existing_foundup():
    """launch_foundup handles existing foundup gracefully."""
    market = InMemoryAgentMarket()

    # Pre-create foundup
    existing = Foundup(
        foundup_id="f_existing",
        name="Existing Foundup",
        owner_id="owner_1",
        token_symbol="EXIST",
        immutable_metadata={},
        mutable_metadata={},
    )
    market.create_foundup(existing)

    # Try to launch same foundup
    result = launch_foundup(
        registry=market,
        token_adapter=market,
        foundup=existing,
    )

    assert result.success is True
    event_types = [e.event_type for e in result.events]
    assert "launch.foundup_exists" in event_types
    assert "launch.foundup_created" not in event_types


def test_launch_orchestrator_emits_traceable_events():
    """LaunchOrchestrator emits auditable events with proper structure."""
    market = InMemoryAgentMarket()
    orchestrator = LaunchOrchestrator(
        registry=market,
        token_adapter=market,
        repo_adapter=market,
        observability=market,
    )

    foundup = Foundup(
        foundup_id="f_trace",
        name="Traceable Foundup",
        owner_id="owner_1",
        token_symbol="TRACE",
        immutable_metadata={},
        mutable_metadata={},
    )

    token_terms = TokenTerms(
        token_name="Trace Token",
        token_symbol="TRACE",
        max_supply=500_000,
        treasury_account="treasury_trace",
    )

    result = orchestrator.launch_foundup(
        foundup=foundup,
        token_terms=token_terms,
        repo_name="trace-repo",
        actor_id="tracer_1",
    )

    # Verify all events have required audit fields
    for event in result.events:
        assert event.event_id.startswith("launch_ev_")
        assert event.foundup_id == "f_trace"
        assert event.actor_id == "tracer_1"
        assert event.timestamp is not None
        assert isinstance(event.payload, dict)

    # Verify observability received events
    obs_events = market.query_events(foundup_id="f_trace")
    assert len(obs_events) > 0


def test_repo_provision_records_deterministic_metadata():
    """Repo provisioning adapter records deterministic repo metadata."""
    market = InMemoryAgentMarket()

    # Create foundup first
    foundup = Foundup(
        foundup_id="f_repo",
        name="Repo Test Foundup",
        owner_id="owner_1",
        token_symbol="REPO",
        immutable_metadata={},
        mutable_metadata={},
    )
    market.create_foundup(foundup)

    # Provision repo
    repo_url = market.provision_repo(
        foundup_id="f_repo",
        repo_name="test-repo",
        provider="github",
        default_branch="main",
    )

    assert repo_url == "https://github.com/foundups/test-repo"

    # Verify metadata stored
    metadata = market.get_repo_metadata("f_repo")
    assert metadata is not None
    assert metadata["foundup_id"] == "f_repo"
    assert metadata["repo_name"] == "test-repo"
    assert metadata["repo_url"] == "https://github.com/foundups/test-repo"
    assert metadata["provider"] == "github"
    assert metadata["default_branch"] == "main"


def test_repo_provision_different_providers():
    """Repo provisioning works with different providers."""
    market = InMemoryAgentMarket()

    for provider, foundup_id in [("github", "f_gh"), ("gitlab", "f_gl"), ("bitbucket", "f_bb")]:
        market.create_foundup(
            Foundup(
                foundup_id=foundup_id,
                name=f"{provider} Foundup",
                owner_id="owner_1",
                token_symbol=provider.upper()[:4],
                immutable_metadata={},
                mutable_metadata={},
            )
        )

        repo_url = market.provision_repo(
            foundup_id=foundup_id,
            repo_name=f"{provider}-repo",
            provider=provider,
        )

        assert provider in repo_url
        metadata = market.get_repo_metadata(foundup_id)
        assert metadata["provider"] == provider


def test_repo_provision_emits_event():
    """Repo provisioning emits auditable event."""
    market = InMemoryAgentMarket()

    market.create_foundup(
        Foundup(
            foundup_id="f_repo_ev",
            name="Event Test Foundup",
            owner_id="owner_1",
            token_symbol="EVNT",
            immutable_metadata={},
            mutable_metadata={},
        )
    )

    market.provision_repo("f_repo_ev", "event-repo", "github", "develop")

    events = market.query_events(foundup_id="f_repo_ev")
    repo_events = [e for e in events if e["event_type"] == "repo.provisioned"]
    assert len(repo_events) == 1
    assert repo_events[0]["payload"]["repo_name"] == "event-repo"
    assert repo_events[0]["payload"]["default_branch"] == "develop"
