import asyncio
import pytest

from holo_index.mcp_client.holo_mcp_client import HoloIndexMCPClient


def test_connect_fails_cleanly_when_fastmcp_missing(monkeypatch):
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None if name == "fastmcp" else object())

    client = HoloIndexMCPClient(server_script_path="dummy.py")

    with pytest.raises(RuntimeError, match="fastmcp is not installed"):
        asyncio.run(client.connect())

    assert client.last_error == "fastmcp is not installed"
