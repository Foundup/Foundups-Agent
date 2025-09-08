from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class SimWorkflowsClient:
    """Minimal HTTP client for Sim workflow operations.

    Sidecar-first: only start/query flows; no data coupling.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        self._base_url: str = base_url.rstrip("/")
        self._api_key: Optional[str] = api_key
        self._client = httpx.AsyncClient(timeout=15.0)

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def start_flow(self, flow_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a Sim flow by name with inputs.

        Returns normalized response with at least { flow_id, status } if present.
        """
        url = f"{self._base_url}/api/flows/start"
        payload = {"flow": flow_name, "inputs": inputs}
        resp = await self._client.post(url, headers=self._headers(), json=payload)
        if resp.status_code >= 400:
            raise RuntimeError(f"Sim start_flow failed: {resp.status_code} {resp.text}")
        data: Dict[str, Any] = resp.json()
        # Normalize common fields
        norm = {
            "flow_id": data.get("id") or data.get("flowId") or data.get("flow_id"),
            "status": data.get("status", "unknown"),
            "raw": data,
        }
        return norm

    async def get_flow_status(self, flow_id: str) -> Dict[str, Any]:
        """Query status of a Sim flow by ID."""
        url = f"{self._base_url}/api/flows/{flow_id}"
        resp = await self._client.get(url, headers=self._headers())
        if resp.status_code >= 400:
            raise RuntimeError(f"Sim get_flow_status failed: {resp.status_code} {resp.text}")
        data: Dict[str, Any] = resp.json()
        norm = {
            "flow_id": flow_id,
            "status": data.get("status", "unknown"),
            "raw": data,
        }
        return norm

    async def aclose(self) -> None:
        await self._client.aclose()
