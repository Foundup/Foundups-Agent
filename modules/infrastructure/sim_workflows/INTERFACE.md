# INTERFACE: sim_workflows (WSP 11)

## Public API Definition

### `SimWorkflowsClient`
```python
class SimWorkflowsClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None: ...

    async def start_flow(self, flow_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]: ...

    async def get_flow_status(self, flow_id: str) -> Dict[str, Any]: ...
```

#### Parameters
- `base_url` (str): Sim base URL (e.g., `http://localhost:3000`)
- `api_key` (Optional[str]): Optional Sim-managed key when required
- `flow_name` (str): Named flow in Sim
- `inputs` (Dict[str, Any]): Flow inputs payload
- `flow_id` (str): Correlation ID from Sim

#### Returns
- `Dict[str, Any]`: JSON-like response from Sim and normalized fields

#### Errors
- Raises `RuntimeError` on non-2xx responses or protocol mismatches

---

### `SimSocketBridge`
```python
class SimSocketBridge:
    def __init__(self, sim_url: str) -> None: ...

    async def connect(self) -> None: ...

    def on_event(self, event: str, handler: Callable[[Dict[str, Any]], None]) -> None: ...

    async def disconnect(self) -> None: ...
```

#### Parameters
- `sim_url` (str): Socket.io endpoint for Sim (default origin)
- `event` (str): Event name (e.g., `flow-status`)
- `handler` (Callable): Consumer callback

#### Behavior
- Maintains resilient Socket.io connection; exposes event subscription

---

### `verify_signature`
```python
def verify_signature(secret: str, payload: bytes, signature: str) -> bool: ...
```

#### Parameters
- `secret` (str): Shared secret for webhooks
- `payload` (bytes): Raw request body
- `signature` (str): Signature header from Sim

#### Returns
- `bool`: True if signature is valid

#### Errors
- None (returns False for invalid/unsupported cases)

---

## Examples
```python
client = SimWorkflowsClient(base_url="http://localhost:3000")
flow = await client.start_flow("code_review_meeting", {"repo": "foundups"})

bridge = SimSocketBridge(sim_url="http://localhost:3000")
bridge.on_event("flow-status", lambda e: print(e))
await bridge.connect()
```

## Backward Compatibility
- New module; no upstream dependents; stable interfaces defined above

## Error Handling
- Network-level errors surfaced as exceptions; callers should apply retries


