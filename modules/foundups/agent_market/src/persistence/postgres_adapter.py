"""Postgres persistence adapter for FoundUps Agent Market.

This adapter shares the SQLAlchemy ORM model set used by SQLiteAdapter and
supports the same CRUD contract. It is instantiated via repository_factory.
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchModuleError
from sqlalchemy.orm import sessionmaker

from ..exceptions import ValidationError
from .migrations import LATEST_SCHEMA_VERSION, MigrationManager
from .sqlite_adapter import Base, SQLiteAdapter


class PostgresAdapter(SQLiteAdapter):
    """Postgres-backed repository adapter.

    Uses the same method surface as SQLiteAdapter to keep service code
    backend-agnostic.
    """

    def __init__(
        self,
        db_url: str | None = None,
        *,
        auto_migrate: bool | None = None,
        schema_version: int | None = None,
    ) -> None:
        db_url = db_url or os.environ.get("FAM_POSTGRES_URL")
        if not db_url:
            raise ValidationError("FAM_POSTGRES_URL is required for postgres backend")
        if not db_url.startswith(("postgresql://", "postgresql+", "postgres://")):
            raise ValidationError("Postgres URL must start with postgresql:// or postgres://")

        try:
            self.engine = create_engine(
                db_url,
                echo=os.environ.get("FAM_DB_ECHO", "").lower() == "true",
                pool_pre_ping=True,
            )
        except (ModuleNotFoundError, NoSuchModuleError) as exc:
            raise ValidationError(
                "Postgres driver missing; install psycopg or psycopg2-binary for FAM postgres backend"
            ) from exc

        # Keep this attribute for compatibility with SQLiteAdapter call sites.
        self.db_path = Path("<postgres>")
        self._SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

        Base.metadata.create_all(self.engine)
        migrate = (
            auto_migrate
            if auto_migrate is not None
            else os.environ.get("FAM_DB_AUTO_MIGRATE", "1").strip() not in {"0", "false", "False"}
        )
        if migrate:
            target_version = schema_version if schema_version is not None else LATEST_SCHEMA_VERSION
            MigrationManager(self.engine).migrate(target_version=target_version)
