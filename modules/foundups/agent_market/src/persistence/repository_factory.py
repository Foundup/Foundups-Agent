"""Factory for persistence adapter selection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..exceptions import ValidationError
from .postgres_adapter import PostgresAdapter
from .sqlite_adapter import SQLiteAdapter


@dataclass(frozen=True)
class RepositoryConfig:
    backend: str = "sqlite"
    sqlite_path: str | Path | None = None
    postgres_url: str | None = None
    auto_migrate: bool = True
    schema_version: int | None = None


def create_repository(config: Optional[RepositoryConfig] = None) -> SQLiteAdapter:
    """Create the configured persistence repository.

    Defaults to sqlite for deterministic local execution.
    """
    cfg = config or _load_config_from_env()
    backend = cfg.backend.strip().lower()

    if backend == "sqlite":
        return SQLiteAdapter(
            db_path=cfg.sqlite_path,
            auto_migrate=cfg.auto_migrate,
            schema_version=cfg.schema_version,
        )
    if backend == "postgres":
        return PostgresAdapter(
            db_url=cfg.postgres_url,
            auto_migrate=cfg.auto_migrate,
            schema_version=cfg.schema_version,
        )

    raise ValidationError(f"Unsupported FAM persistence backend: {cfg.backend}")


def _load_config_from_env() -> RepositoryConfig:
    backend = os.environ.get("FAM_DB_BACKEND", "sqlite")
    sqlite_path = os.environ.get("FAM_DB_PATH", "./fam_data/fam.db")
    postgres_url = os.environ.get("FAM_POSTGRES_URL")
    auto_migrate = os.environ.get("FAM_DB_AUTO_MIGRATE", "1").strip() not in {"0", "false", "False"}
    raw_version = os.environ.get("FAM_DB_SCHEMA_VERSION")
    schema_version = int(raw_version) if raw_version else None
    return RepositoryConfig(
        backend=backend,
        sqlite_path=sqlite_path,
        postgres_url=postgres_url,
        auto_migrate=auto_migrate,
        schema_version=schema_version,
    )
