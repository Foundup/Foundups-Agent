"""Persistence layer package for FoundUps Agent Market."""

from .migrations import LATEST_SCHEMA_VERSION, MigrationManager
from .postgres_adapter import PostgresAdapter
from .repository_factory import RepositoryConfig, create_repository
from .sqlite_adapter import SQLiteAdapter

__all__ = [
    "LATEST_SCHEMA_VERSION",
    "MigrationManager",
    "PostgresAdapter",
    "RepositoryConfig",
    "SQLiteAdapter",
    "create_repository",
]
