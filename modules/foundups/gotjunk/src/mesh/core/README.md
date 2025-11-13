# Mesh Core Module

## Purpose

Foundational mesh networking layer for GotJunk's decentralized emergency communication system. Provides peer registry, packet broadcasting, and discovery interfaces ready for Sprint 2 BLE integration and Sprint 3 emergency broadcast integration.

## Architecture

### Core Components

- **MeshCore**: Central orchestrator for mesh operations
- **MeshPacket**: Standardized packet format for mesh communication
- **MeshPeer**: Peer representation with extensible properties

### Design Principles

- **Zero Dependencies**: Pure TypeScript implementation
- **Extensible**: Ready for BLE, LoRa, and hybrid switching
- **Minimal**: Foundation only, no implementation bleed
- **Testable**: 100% test coverage with Jest

## Usage

`	ypescript
import { MeshCore } from './src/meshCore';
import { MeshPacket } from './src/packet';

const mesh = new MeshCore();
mesh.goOnline();
mesh.addPeer('peer-123');

const packet: MeshPacket = {
  id: 'uuid-123',
  type: 'alert',
  timestamp: Date.now(),
  payload: { message: 'ICE raid detected' }
};

mesh.broadcast(packet);
`

## FMAS Tests

Run tests with:
`ash
npm test modules/foundups/gotjunk/src/mesh/core/tests/
`

Test coverage includes:
- Peer addition/removal
- Online/offline state management
- Packet broadcasting interface
- Discovery placeholder (returns [] for Sprint 1)

## Future Sprint Hooks

### Sprint 2: BLE Integration
- discoverPeers() ↁEBLE device discovery
- roadcast() ↁEBLE packet transmission
- MeshPeer.signalStrength ↁEBLE RSSI values

### Sprint 3: Emergency Broadcast
- Packet type validation for emergency categories
- TTL-based packet expiration
- Priority queuing for critical alerts

### Sprint 4: Hybrid Network Switch
- Automatic online/offline detection
- Seamless cloud/mesh mode switching
- Network state persistence

## WSP Compliance

- **WSP 3**: Modular architecture with clear boundaries
- **WSP 22**: Comprehensive documentation and change tracking
- **WSP 49**: Standard module structure
- **WSP 50**: Pre-action verification in all methods
- **WSP 64**: Violation prevention through strict interfaces
