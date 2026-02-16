"""Tests for persistence repository factory."""

import tempfile
from pathlib import Path

import pytest

from modules.foundups.agent_market.src.exceptions import ValidationError
from modules.foundups.agent_market.src.persistence import RepositoryConfig, SQLiteAdapter, create_repository
from modules.foundups.agent_market.src.persistence import repository_factory


class TestRepositoryFactory:
    def test_default_factory_returns_sqlite(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "factory.db"
            repo = create_repository(
                RepositoryConfig(
                    backend="sqlite",
                    sqlite_path=db_path,
                    auto_migrate=True,
                )
            )
            try:
                assert isinstance(repo, SQLiteAdapter)
                assert db_path.exists()
            finally:
                repo.close()

    def test_unsupported_backend_raises(self):
        with pytest.raises(ValidationError):
            create_repository(RepositoryConfig(backend="unknown"))

    def test_postgres_path_uses_postgres_adapter(self, monkeypatch):
        captured = {}

        class FakePostgresAdapter:
            def __init__(self, db_url=None, auto_migrate=True, schema_version=None):
                captured["db_url"] = db_url
                captured["auto_migrate"] = auto_migrate
                captured["schema_version"] = schema_version

        monkeypatch.setattr(repository_factory, "PostgresAdapter", FakePostgresAdapter)
        repo = create_repository(
            RepositoryConfig(
                backend="postgres",
                postgres_url="postgresql://user:pass@localhost/fam",
                auto_migrate=False,
                schema_version=3,
            )
        )

        assert isinstance(repo, FakePostgresAdapter)
        assert captured["db_url"] == "postgresql://user:pass@localhost/fam"
        assert captured["auto_migrate"] is False
        assert captured["schema_version"] == 3
