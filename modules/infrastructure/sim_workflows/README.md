# sim_workflows

## 🏢 WSP Enterprise Domain: `infrastructure`

**WSP Compliance Status**: ✅ COMPLIANT with WSP Framework  
**Domain**: `infrastructure` per `WSP_3_Enterprise_Domain_Organization.md`  
**Structure**: Follows `WSP_49_Module_Directory_Structure_Standardization_Protocol.md`

---

## 🎯 Module Purpose

Bridges WRE agentic workflows with Sim agent workflow engine. Provides:
- HTTP client for triggering and querying Sim flows
- Socket.io client bridge to mirror Sim realtime events into WRE
- Webhook intake for Sim flow lifecycle events, normalized to WRE events

## 🏗️ WSP Architecture Compliance

### Domain Organization (WSP 3)
Functionality is infrastructure-level integration with an external workflow engine. No platform consolidation; only generic workflow bridging.

### Module Structure (WSP 49)
```
infrastructure/sim_workflows/
├── __init__.py                 ← Public API (WSP 11)
├── src/
│   ├── __init__.py
│   ├── sim_client.py           ← HTTP client for Sim
│   ├── sim_socket_bridge.py    ← Socket.io event bridge
│   └── sim_webhook.py          ← Webhook parsing & verification
├── tests/
│   ├── __init__.py
│   └── README.md               ← Test documentation (WSP 34)
├── memory/
│   └── README.md               ← Memory documentation (WSP 60)
├── README.md                   ← This file
├── INTERFACE.md                ← Public API definition (WSP 11)
├── ModLog.md                   ← Change tracking (WSP 22)
├── ROADMAP.md                  ← LLME progression & plan
└── requirements.txt            ← Dependencies (WSP 12)
```

## 🔧 Installation & Usage

### Prerequisites
- WSP Framework compliance (WSP_CORE)
- Dependencies listed in `requirements.txt`

### Installation
```bash
pip install -r modules/infrastructure/sim_workflows/requirements.txt
```

### Basic Usage
```python
from modules.infrastructure.sim_workflows import SimWorkflowsClient, SimSocketBridge

client = SimWorkflowsClient(base_url="http://localhost:3000", api_key=None)
bridge = SimSocketBridge(sim_url="http://localhost:3000")
```

## 🧪 Testing & Quality Assurance

### Running Tests (WSP 6, WSP 34)
```bash
pytest modules/infrastructure/sim_workflows/tests -q
```

### FMAS Validation (WSP 4)
```bash
python tools/modular_audit/modular_audit.py modules/
```

## 📋 WSP Protocol References

- WSP 1, WSP 3, WSP 4, WSP 6, WSP 11, WSP 12, WSP 22, WSP 49, WSP 60, WSP 78

## 🚨 WSP Compliance Guidelines

- Functional distribution only (no platform consolidation)
- Public API documented in `INTERFACE.md`
- Memory artifacts documented under `memory/` per WSP 60

## 🌀 Windsurf Protocol (WSP) Recursive Prompt

```
WSP_CYCLE_INTEGRATION:
- UN: Anchor to WSP protocols and retrieve Sim bridge context
- DAO: Execute bridge logic under WSP compliance
- DU: Emit next agentic prompt for integration hardening

wsp_cycle(input="sim_workflows", domain="infrastructure", log=True)
```

## 📝 Development Notes

- Sidecar-first, minimal coupling with Sim; HTTP/webhook + Socket.io
- Optional future ETL to pgvector only if a concrete flow requires shared RAG


