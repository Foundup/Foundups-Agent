"""SQLite persistence adapter for FoundUps Agent Market.

Provides CRUD operations for all FAM domain models using SQLAlchemy 2.0 ORM.
WAL mode enabled for concurrency support.

WSP References:
- WSP 11: Interface contract adherence
- WSP 30: Persistence layer design
- WSP 50: Error handling standards
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Type, TypeVar

from sqlalchemy import JSON, Boolean, DateTime, Enum, Integer, String, Text, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from ..exceptions import NotFoundError, ValidationError
from ..models import (
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

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Enable WAL mode for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


# ORM Models mirroring dataclasses from models.py


class FoundupRow(Base):
    """ORM model for Foundup."""

    __tablename__ = "foundups"

    foundup_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    token_symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    immutable_metadata: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)
    mutable_metadata: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TokenTermsRow(Base):
    """ORM model for TokenTerms."""

    __tablename__ = "token_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    foundup_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    token_name: Mapped[str] = mapped_column(String(256), nullable=False)
    token_symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    max_supply: Mapped[int] = mapped_column(Integer, nullable=False)
    treasury_account: Mapped[str] = mapped_column(String(128), nullable=False)
    vesting_policy: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)
    chain_hint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class AgentProfileRow(Base):
    """ORM model for AgentProfile."""

    __tablename__ = "agent_profiles"

    agent_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    foundup_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    capability_tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TaskRow(Base):
    """ORM model for Task."""

    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    foundup_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria: Mapped[List[str]] = mapped_column(JSON, default=list)
    reward_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    creator_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.OPEN)
    assignee_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    proof_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    verification_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    payout_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProofRow(Base):
    """ORM model for Proof."""

    __tablename__ = "proofs"

    proof_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    submitter_id: Mapped[str] = mapped_column(String(64), nullable=False)
    artifact_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class VerificationRow(Base):
    """ORM model for Verification."""

    __tablename__ = "verifications"

    verification_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    verifier_id: Mapped[str] = mapped_column(String(64), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PayoutRow(Base):
    """ORM model for Payout."""

    __tablename__ = "payouts"

    payout_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    recipient_id: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PayoutStatus] = mapped_column(Enum(PayoutStatus), default=PayoutStatus.INITIATED)
    reference: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class DistributionPostRow(Base):
    """ORM model for DistributionPost."""

    __tablename__ = "distribution_posts"

    distribution_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    foundup_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    dedupe_key: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    external_ref: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EventRecordRow(Base):
    """ORM model for EventRecord."""

    __tablename__ = "event_records"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    foundup_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    proof_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    payout_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class SQLiteAdapter:
    """SQLite persistence adapter with SQLAlchemy 2.0 ORM.

    Provides CRUD operations for all FAM domain models.
    Uses WAL mode for concurrent access support.

    Example:
        adapter = SQLiteAdapter("path/to/fam.db")
        foundup = adapter.create_foundup(foundup_data)
        adapter.close()
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        """Initialize SQLite adapter.

        Args:
            db_path: Path to SQLite database file. Defaults to
                     FAM_DB_PATH env var or './fam_data/fam.db'.
        """
        if db_path is None:
            db_path = os.environ.get("FAM_DB_PATH", "./fam_data/fam.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=os.environ.get("FAM_DB_ECHO", "").lower() == "true",
            pool_pre_ping=True,
        )
        self._SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info("SQLiteAdapter initialized: %s", self.db_path)

    def close(self) -> None:
        """Close database connection."""
        self.engine.dispose()
        logger.info("SQLiteAdapter closed")

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions."""
        sess = self._SessionFactory()
        try:
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            sess.close()

    # --- Foundup CRUD ---

    def create_foundup(self, foundup: Foundup) -> Foundup:
        """Create a new Foundup record."""
        with self.session() as sess:
            row = FoundupRow(
                foundup_id=foundup.foundup_id,
                name=foundup.name,
                owner_id=foundup.owner_id,
                token_symbol=foundup.token_symbol,
                immutable_metadata=foundup.immutable_metadata,
                mutable_metadata=foundup.mutable_metadata,
                created_at=foundup.created_at,
            )
            sess.add(row)
        logger.debug("Created Foundup: %s", foundup.foundup_id)
        return foundup

    def get_foundup(self, foundup_id: str) -> Foundup:
        """Get a Foundup by ID."""
        with self.session() as sess:
            row = sess.get(FoundupRow, foundup_id)
            if row is None:
                raise NotFoundError(f"Foundup not found: {foundup_id}")
            return Foundup(
                foundup_id=row.foundup_id,
                name=row.name,
                owner_id=row.owner_id,
                token_symbol=row.token_symbol,
                immutable_metadata=dict(row.immutable_metadata),
                mutable_metadata=dict(row.mutable_metadata),
                created_at=row.created_at,
            )

    def update_foundup(self, foundup_id: str, updates: Dict[str, str]) -> Foundup:
        """Update mutable_metadata of a Foundup."""
        with self.session() as sess:
            row = sess.get(FoundupRow, foundup_id)
            if row is None:
                raise NotFoundError(f"Foundup not found: {foundup_id}")
            current = dict(row.mutable_metadata)
            current.update(updates)
            row.mutable_metadata = current
        return self.get_foundup(foundup_id)

    def list_foundups(self, limit: int = 100) -> List[Foundup]:
        """List all Foundups."""
        with self.session() as sess:
            rows = sess.query(FoundupRow).limit(limit).all()
            return [
                Foundup(
                    foundup_id=r.foundup_id,
                    name=r.name,
                    owner_id=r.owner_id,
                    token_symbol=r.token_symbol,
                    immutable_metadata=dict(r.immutable_metadata),
                    mutable_metadata=dict(r.mutable_metadata),
                    created_at=r.created_at,
                )
                for r in rows
            ]

    # --- Task CRUD ---

    def create_task(self, task: Task) -> Task:
        """Create a new Task record."""
        with self.session() as sess:
            row = TaskRow(
                task_id=task.task_id,
                foundup_id=task.foundup_id,
                title=task.title,
                description=task.description,
                acceptance_criteria=task.acceptance_criteria,
                reward_amount=task.reward_amount,
                creator_id=task.creator_id,
                status=task.status,
                assignee_id=task.assignee_id,
                proof_id=task.proof_id,
                verification_id=task.verification_id,
                payout_id=task.payout_id,
                created_at=task.created_at,
            )
            sess.add(row)
        logger.debug("Created Task: %s", task.task_id)
        return task

    def get_task(self, task_id: str) -> Task:
        """Get a Task by ID."""
        with self.session() as sess:
            row = sess.get(TaskRow, task_id)
            if row is None:
                raise NotFoundError(f"Task not found: {task_id}")
            return self._row_to_task(row)

    def update_task(self, task: Task) -> Task:
        """Update a Task record."""
        with self.session() as sess:
            row = sess.get(TaskRow, task.task_id)
            if row is None:
                raise NotFoundError(f"Task not found: {task.task_id}")
            row.status = task.status
            row.assignee_id = task.assignee_id
            row.proof_id = task.proof_id
            row.verification_id = task.verification_id
            row.payout_id = task.payout_id
        return self.get_task(task.task_id)

    def list_tasks(self, foundup_id: str, limit: int = 100) -> List[Task]:
        """List Tasks for a Foundup."""
        with self.session() as sess:
            rows = sess.query(TaskRow).filter(TaskRow.foundup_id == foundup_id).limit(limit).all()
            return [self._row_to_task(r) for r in rows]

    def _row_to_task(self, row: TaskRow) -> Task:
        return Task(
            task_id=row.task_id,
            foundup_id=row.foundup_id,
            title=row.title,
            description=row.description,
            acceptance_criteria=list(row.acceptance_criteria),
            reward_amount=row.reward_amount,
            creator_id=row.creator_id,
            status=row.status,
            assignee_id=row.assignee_id,
            proof_id=row.proof_id,
            verification_id=row.verification_id,
            payout_id=row.payout_id,
            created_at=row.created_at,
        )

    # --- Proof CRUD ---

    def create_proof(self, proof: Proof) -> Proof:
        """Create a new Proof record."""
        with self.session() as sess:
            row = ProofRow(
                proof_id=proof.proof_id,
                task_id=proof.task_id,
                submitter_id=proof.submitter_id,
                artifact_uri=proof.artifact_uri,
                artifact_hash=proof.artifact_hash,
                notes=proof.notes,
                submitted_at=proof.submitted_at,
            )
            sess.add(row)
        logger.debug("Created Proof: %s", proof.proof_id)
        return proof

    def get_proof(self, proof_id: str) -> Proof:
        """Get a Proof by ID."""
        with self.session() as sess:
            row = sess.get(ProofRow, proof_id)
            if row is None:
                raise NotFoundError(f"Proof not found: {proof_id}")
            return Proof(
                proof_id=row.proof_id,
                task_id=row.task_id,
                submitter_id=row.submitter_id,
                artifact_uri=row.artifact_uri,
                artifact_hash=row.artifact_hash,
                notes=row.notes,
                submitted_at=row.submitted_at,
            )

    # --- Verification CRUD ---

    def create_verification(self, verification: Verification) -> Verification:
        """Create a new Verification record."""
        with self.session() as sess:
            row = VerificationRow(
                verification_id=verification.verification_id,
                task_id=verification.task_id,
                verifier_id=verification.verifier_id,
                approved=verification.approved,
                reason=verification.reason,
                verified_at=verification.verified_at,
            )
            sess.add(row)
        logger.debug("Created Verification: %s", verification.verification_id)
        return verification

    def get_verification(self, verification_id: str) -> Verification:
        """Get a Verification by ID."""
        with self.session() as sess:
            row = sess.get(VerificationRow, verification_id)
            if row is None:
                raise NotFoundError(f"Verification not found: {verification_id}")
            return Verification(
                verification_id=row.verification_id,
                task_id=row.task_id,
                verifier_id=row.verifier_id,
                approved=row.approved,
                reason=row.reason,
                verified_at=row.verified_at,
            )

    # --- Payout CRUD ---

    def create_payout(self, payout: Payout) -> Payout:
        """Create a new Payout record."""
        with self.session() as sess:
            row = PayoutRow(
                payout_id=payout.payout_id,
                task_id=payout.task_id,
                recipient_id=payout.recipient_id,
                amount=payout.amount,
                status=payout.status,
                reference=payout.reference,
                paid_at=payout.paid_at,
            )
            sess.add(row)
        logger.debug("Created Payout: %s", payout.payout_id)
        return payout

    def get_payout(self, payout_id: str) -> Payout:
        """Get a Payout by ID."""
        with self.session() as sess:
            row = sess.get(PayoutRow, payout_id)
            if row is None:
                raise NotFoundError(f"Payout not found: {payout_id}")
            return Payout(
                payout_id=row.payout_id,
                task_id=row.task_id,
                recipient_id=row.recipient_id,
                amount=row.amount,
                status=row.status,
                reference=row.reference,
                paid_at=row.paid_at,
            )

    def update_payout(self, payout: Payout) -> Payout:
        """Update a Payout record."""
        with self.session() as sess:
            row = sess.get(PayoutRow, payout.payout_id)
            if row is None:
                raise NotFoundError(f"Payout not found: {payout.payout_id}")
            row.status = payout.status
            row.reference = payout.reference
            row.paid_at = payout.paid_at
        return self.get_payout(payout.payout_id)

    # --- EventRecord CRUD ---

    def create_event(self, event: EventRecord) -> EventRecord:
        """Create a new EventRecord."""
        with self.session() as sess:
            row = EventRecordRow(
                event_id=event.event_id,
                event_type=event.event_type,
                actor_id=event.actor_id,
                payload=event.payload,
                foundup_id=event.foundup_id,
                task_id=event.task_id,
                proof_id=event.proof_id,
                payout_id=event.payout_id,
                timestamp=event.timestamp,
            )
            sess.add(row)
        logger.debug("Created EventRecord: %s", event.event_id)
        return event

    def query_events(
        self,
        foundup_id: Optional[str] = None,
        task_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[EventRecord]:
        """Query EventRecords with optional filters."""
        with self.session() as sess:
            query = sess.query(EventRecordRow)
            if foundup_id:
                query = query.filter(EventRecordRow.foundup_id == foundup_id)
            if task_id:
                query = query.filter(EventRecordRow.task_id == task_id)
            if event_type:
                query = query.filter(EventRecordRow.event_type == event_type)
            rows = query.order_by(EventRecordRow.timestamp.desc()).limit(limit).all()
            return [
                EventRecord(
                    event_id=r.event_id,
                    event_type=r.event_type,
                    actor_id=r.actor_id,
                    payload=dict(r.payload),
                    foundup_id=r.foundup_id,
                    task_id=r.task_id,
                    proof_id=r.proof_id,
                    payout_id=r.payout_id,
                    timestamp=r.timestamp,
                )
                for r in rows
            ]

    # --- Distribution CRUD ---

    def create_distribution(self, post: DistributionPost) -> DistributionPost:
        """Create a new DistributionPost record."""
        with self.session() as sess:
            row = DistributionPostRow(
                distribution_id=post.distribution_id,
                foundup_id=post.foundup_id,
                task_id=post.task_id,
                channel=post.channel,
                content=post.content,
                actor_id=post.actor_id,
                dedupe_key=post.dedupe_key,
                external_ref=post.external_ref,
                published_at=post.published_at,
            )
            sess.add(row)
        logger.debug("Created DistributionPost: %s", post.distribution_id)
        return post

    def get_distribution(self, distribution_id: str) -> DistributionPost:
        """Get a DistributionPost by ID."""
        with self.session() as sess:
            row = sess.get(DistributionPostRow, distribution_id)
            if row is None:
                raise NotFoundError(f"DistributionPost not found: {distribution_id}")
            return DistributionPost(
                distribution_id=row.distribution_id,
                foundup_id=row.foundup_id,
                task_id=row.task_id,
                channel=row.channel,
                content=row.content,
                actor_id=row.actor_id,
                dedupe_key=row.dedupe_key,
                external_ref=row.external_ref,
                published_at=row.published_at,
            )

    def get_distribution_by_task(self, task_id: str) -> Optional[DistributionPost]:
        """Get DistributionPost by task_id."""
        with self.session() as sess:
            row = sess.query(DistributionPostRow).filter(DistributionPostRow.task_id == task_id).first()
            if row is None:
                return None
            return DistributionPost(
                distribution_id=row.distribution_id,
                foundup_id=row.foundup_id,
                task_id=row.task_id,
                channel=row.channel,
                content=row.content,
                actor_id=row.actor_id,
                dedupe_key=row.dedupe_key,
                external_ref=row.external_ref,
                published_at=row.published_at,
            )

    # --- AgentProfile CRUD ---

    def create_agent_profile(self, foundup_id: str, profile: AgentProfile) -> AgentProfile:
        """Create a new AgentProfile record."""
        with self.session() as sess:
            row = AgentProfileRow(
                agent_id=profile.agent_id,
                foundup_id=foundup_id,
                display_name=profile.display_name,
                capability_tags=profile.capability_tags,
                role=profile.role,
                joined_at=profile.joined_at,
            )
            sess.add(row)
        logger.debug("Created AgentProfile: %s", profile.agent_id)
        return profile

    def get_agent_profile(self, agent_id: str) -> AgentProfile:
        """Get an AgentProfile by ID."""
        with self.session() as sess:
            row = sess.get(AgentProfileRow, agent_id)
            if row is None:
                raise NotFoundError(f"AgentProfile not found: {agent_id}")
            return AgentProfile(
                agent_id=row.agent_id,
                display_name=row.display_name,
                capability_tags=list(row.capability_tags),
                role=row.role,
                joined_at=row.joined_at,
            )

    def list_agents(self, foundup_id: str) -> List[AgentProfile]:
        """List AgentProfiles for a Foundup."""
        with self.session() as sess:
            rows = sess.query(AgentProfileRow).filter(AgentProfileRow.foundup_id == foundup_id).all()
            return [
                AgentProfile(
                    agent_id=r.agent_id,
                    display_name=r.display_name,
                    capability_tags=list(r.capability_tags),
                    role=r.role,
                    joined_at=r.joined_at,
                )
                for r in rows
            ]

    # --- TokenTerms CRUD ---

    def save_token_terms(self, foundup_id: str, terms: TokenTerms) -> TokenTerms:
        """Save TokenTerms for a Foundup."""
        with self.session() as sess:
            # Check if exists
            existing = sess.query(TokenTermsRow).filter(TokenTermsRow.foundup_id == foundup_id).first()
            if existing:
                existing.token_name = terms.token_name
                existing.token_symbol = terms.token_symbol
                existing.max_supply = terms.max_supply
                existing.treasury_account = terms.treasury_account
                existing.vesting_policy = terms.vesting_policy
                existing.chain_hint = terms.chain_hint
            else:
                row = TokenTermsRow(
                    foundup_id=foundup_id,
                    token_name=terms.token_name,
                    token_symbol=terms.token_symbol,
                    max_supply=terms.max_supply,
                    treasury_account=terms.treasury_account,
                    vesting_policy=terms.vesting_policy,
                    chain_hint=terms.chain_hint,
                )
                sess.add(row)
        logger.debug("Saved TokenTerms for: %s", foundup_id)
        return terms

    def get_token_terms(self, foundup_id: str) -> Optional[TokenTerms]:
        """Get TokenTerms for a Foundup."""
        with self.session() as sess:
            row = sess.query(TokenTermsRow).filter(TokenTermsRow.foundup_id == foundup_id).first()
            if row is None:
                return None
            return TokenTerms(
                token_name=row.token_name,
                token_symbol=row.token_symbol,
                max_supply=row.max_supply,
                treasury_account=row.treasury_account,
                vesting_policy=dict(row.vesting_policy),
                chain_hint=row.chain_hint,
            )
