# Liberty Alert Test Suite

**Module**: liberty_alert
**Coverage Target**: [GREATER_EQUAL]90% (WSP 5)

## Test Organization

### Unit Tests
```
tests/
+-- test_models.py           # Data model tests
+-- test_mesh_network.py     # Mesh networking tests
+-- test_alert_broadcaster.py # Alert system tests
+-- test_voice_synthesizer.py # Voice synthesis tests
+-- test_orchestrator.py      # Integration tests
```

### Integration Tests
```
tests/integration/
+-- test_two_phone_mesh.py     # POC: 2-phone mesh demo
+-- test_alert_propagation.py  # Alert through mesh test
+-- test_offline_mode.py        # Offline functionality test
```

### PWA Tests
```
tests/pwa/
+-- offline-functionality.test.js
+-- service-worker.test.js
+-- mesh-connection.test.js
```

## Running Tests

### All Tests
```bash
# From module root
pytest tests/ -v --cov=src --cov-report=term-missing

# Coverage target: [GREATER_EQUAL]90%
```

### Specific Test Suites
```bash
# Unit tests only
pytest tests/test_*.py

# Integration tests
pytest tests/integration/

# PWA tests
npm test -- tests/pwa/
```

### POC Demo Test (Sprint 1)
```bash
# 2-phone mesh ping test
pytest tests/integration/test_two_phone_mesh.py -v

# Expected:
# - Phone A broadcasts ping
# - Phone B receives via WebRTC mesh
# - Latency <500ms
# - Map shows both devices
```

## Test Fixtures

### Mock Mesh Network
```python
# tests/conftest.py
@pytest.fixture
async def mock_mesh():
    """Mock mesh network for testing"""
    mesh = MeshNetwork(peer_id="test-peer-1")
    await mesh.start()
    yield mesh
    await mesh.stop()
```

### Fake Alert Data
```python
@pytest.fixture
def fake_alert():
    """Generate fake alert for testing"""
    return Alert(
        location=GeoPoint(34.0522, -118.2437, accuracy=10.0),
        threat_type=ThreatType.SURVEILLANCE_VEHICLE,
        message="Test alert - van blanca en 38th",
        language="es"
    )
```

## Coverage Requirements (WSP 5)

### Critical Paths (100% coverage)
- Alert creation and broadcast
- Mesh message routing
- Encryption/decryption
- Alert expiration

### Standard Paths ([GREATER_EQUAL]90% coverage)
- Voice synthesis
- Map rendering
- Peer discovery
- Route calculation

### Edge Cases
- Network disconnection handling
- Message corruption recovery
- Concurrent alert handling
- Memory cleanup

## Performance Benchmarks

### Target Metrics
- Mesh latency: <500ms
- Alert propagation: <2s to 10 nodes
- Voice synthesis: <1s for Spanish
- Memory usage: <50MB per device

### Benchmark Tests
```bash
# Run performance tests
pytest tests/benchmarks/ --benchmark-only
```

## Test Data Privacy

### Fake Data Only
- NO real location data in tests
- Anonymous peer IDs
- Generic threat scenarios
- Synthetic voice audio

### Cleanup
- All test data auto-deleted after tests
- No persistent test artifacts
- Memory wiped in teardown

---

**Status**: POC Development
**Next**: Implement core unit tests for models and mesh network
