# Liberty Alert - React WebRTC Architecture (Occam's Razor PoC)

**Status**: First Principles Design
**Approach**: Hybrid Fallback (WebRTC P2P + Signaling Server)
**Philosophy**: User IS the Intelligence (No AI Classification)

## 🧠 First Principles Analysis

### The Core Problem
**Goal**: Enable users to broadcast location-based alerts peer-to-peer

### Occam's Razor Solution
**Simplest Path**:
1. User unlocks Liberty mode (SOS morse code) ✅ Already implemented
2. Camera orb appears ON THE MAP (when Liberty enabled)
3. User taps orb → captures photo + GPS coordinates
4. Alert broadcasts to connected peers via WebRTC P2P mesh
5. Other users see 🧊 ice cube markers on their maps

**Why This Is Simpler**:
- ❌ NO AI classification needed (user decides what's an alert)
- ❌ NO complex ML models
- ❌ NO Gemini Vision API calls
- ✅ User intelligence > Artificial intelligence
- ✅ Direct action = direct broadcast
- ✅ GPS already available in map context

## 🏗️ Architecture: Hybrid Fallback System

### Option A: Pure WebRTC P2P (Primary)
**Best Case**: Direct browser-to-browser connections
```
User A Browser ←--WebRTC P2P--→ User B Browser
      ↓                              ↓
User C Browser ←--WebRTC P2P--→ User D Browser
         ↖                      ↗
          True mesh topology
          (no central server)
```

**Advantages**:
- ✅ Zero server costs
- ✅ Truly decentralized
- ✅ Censorship-resistant
- ✅ Maximum privacy

**Limitations**:
- Requires peers to be online simultaneously
- NAT traversal may fail in some networks
- Needs signaling to establish initial connection

### Option B: Signaling Server Fallback (Secondary)
**Fallback**: Minimal server for peer discovery only
```
User A → Signaling Server → User B
         (just exchange offers)
              ↓
        Actual data still P2P
        (not relayed through server)
```

**Advantages**:
- ✅ Helps peers discover each other
- ✅ Handles NAT traversal (STUN/TURN)
- ✅ Offline message queue (optional)
- ✅ Still P2P once connected

**Server Role** (minimal):
- Exchange WebRTC SDP offers/answers
- Provide STUN/TURN servers for NAT
- Queue messages if peer offline
- NOT relay actual alert data

## 📦 Technology Stack

### Frontend (React/TypeScript)
```bash
npm install simple-peer          # WebRTC P2P library
npm install socket.io-client     # Signaling fallback (optional)
```

### Backend (Optional - Signaling Only)
```python
# FastAPI for WebRTC signaling
pip install fastapi uvicorn python-socketio
```

## 🎯 Implementation: Camera Orb on Map

### Phase 1: Map Integration (~200 tokens)

**File**: `modules/foundups/gotjunk/frontend/components/PigeonMapView.tsx`

```typescript
interface PigeonMapViewProps {
  // ... existing props
  libertyEnabled: boolean;          // Show camera orb when true
  onLibertyCapture?: (alert: LibertyAlert) => void;
}

export const PigeonMapView: React.FC<PigeonMapViewProps> = ({
  libertyEnabled,
  onLibertyCapture,
  userLocation,
  // ...
}) => {
  const handleCameraCapture = () => {
    // Open camera to capture alert
    // Same camera component as GotJunk items
    // But tagged as Liberty Alert
    if (onLibertyCapture && userLocation) {
      onLibertyCapture({
        id: crypto.randomUUID(),
        location: {
          lat: userLocation.latitude,
          lng: userLocation.longitude,
        },
        photo: capturedBlob,
        timestamp: Date.now(),
        threatType: 'surveillance', // User can change later
      });
    }
  };

  return (
    <div>
      {/* Existing map */}
      <Map>...</Map>

      {/* Camera Orb - Only when Liberty enabled */}
      {libertyEnabled && (
        <motion.button
          onClick={handleCameraCapture}
          className="absolute bottom-24 right-1/2 translate-x-1/2 w-20 h-20 bg-amber-500 rounded-full shadow-2xl border-4 border-white z-50"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <span className="text-4xl">📸</span>
          <div className="absolute -top-2 -right-2 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-xl">🗽</span>
          </div>
        </motion.button>
      )}
    </div>
  );
};
```

### Phase 2: WebRTC P2P Mesh (~400 tokens)

**File**: `modules/foundups/gotjunk/frontend/utils/libertyMesh.ts`

```typescript
import SimplePeer from 'simple-peer';

export interface LibertyAlert {
  id: string;
  location: { lat: number; lng: number };
  photo: Blob;
  timestamp: number;
  threatType: 'surveillance' | 'checkpoint' | 'raid';
  peerId: string;
}

export class LibertyMesh {
  private peers: Map<string, SimplePeer.Instance> = new Map();
  private onAlertReceived: (alert: LibertyAlert) => void;

  constructor(onAlertReceived: (alert: LibertyAlert) => void) {
    this.onAlertReceived = onAlertReceived;
  }

  // Connect to peer via WebRTC
  connectToPeer(peerId: string, initiator: boolean, signalData?: any) {
    const peer = new SimplePeer({
      initiator,
      trickle: false,
      config: {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' }, // Free STUN server
        ],
      },
    });

    // Handle signaling
    peer.on('signal', (data) => {
      console.log('[Liberty] Signal data for peer:', peerId, data);
      // Option A: Exchange via QR code (fully decentralized)
      // Option B: Send to signaling server (fallback)
      this.sendSignalToServer(peerId, data);
    });

    // Handle incoming data
    peer.on('data', (data) => {
      const alert: LibertyAlert = JSON.parse(data.toString());
      console.log('[Liberty] Alert received from peer:', peerId, alert);

      // Show alert locally
      this.onAlertReceived(alert);

      // Re-broadcast to other peers (mesh propagation)
      this.broadcast(alert, peerId); // Skip sender
    });

    peer.on('connect', () => {
      console.log('[Liberty] Connected to peer:', peerId);
    });

    peer.on('error', (err) => {
      console.error('[Liberty] Peer error:', peerId, err);
    });

    // If we received signal data, process it
    if (signalData) {
      peer.signal(signalData);
    }

    this.peers.set(peerId, peer);
    return peer;
  }

  // Broadcast alert to all connected peers
  broadcast(alert: LibertyAlert, excludePeerId?: string) {
    const alertData = JSON.stringify(alert);

    this.peers.forEach((peer, peerId) => {
      if (peerId !== excludePeerId && peer.connected) {
        peer.send(alertData);
      }
    });
  }

  // Fallback: Send signal via server (Option B)
  private async sendSignalToServer(peerId: string, signalData: any) {
    try {
      await fetch('/api/liberty/signal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ peerId, signalData }),
      });
    } catch (err) {
      console.warn('[Liberty] Signaling server unavailable (using QR fallback)');
      // Option A: Show QR code for manual exchange
      this.showQRCode(signalData);
    }
  }

  private showQRCode(signalData: any) {
    // Generate QR code with signal data
    // User can scan friend's QR to connect P2P
    console.log('[Liberty] QR Code:', JSON.stringify(signalData));
  }

  disconnect() {
    this.peers.forEach(peer => peer.destroy());
    this.peers.clear();
  }
}
```

### Phase 3: Signaling Server (Fallback) (~200 tokens)

**File**: `modules/foundups/gotjunk/backend/signaling_server.py`

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple signaling board (ephemeral - resets on restart)
signal_board: dict[str, dict] = {}
websocket_connections: dict[str, WebSocket] = {}

@app.post("/api/liberty/signal")
async def post_signal(data: dict):
    """Store signal data for peer discovery"""
    peer_id = data.get("peerId")
    signal_data = data.get("signalData")

    signal_board[peer_id] = signal_data

    # Notify connected websocket if available
    if peer_id in websocket_connections:
        ws = websocket_connections[peer_id]
        await ws.send_text(json.dumps({"type": "signal", "data": signal_data}))

    return {"status": "ok"}

@app.get("/api/liberty/signal/{peer_id}")
async def get_signal(peer_id: str):
    """Retrieve signal data for peer"""
    return signal_board.get(peer_id, {})

@app.websocket("/ws/liberty/{peer_id}")
async def websocket_endpoint(websocket: WebSocket, peer_id: str):
    """Real-time signaling via websocket"""
    await websocket.accept()
    websocket_connections[peer_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Forward signal to target peer
            target_peer = message.get("targetPeer")
            if target_peer in websocket_connections:
                target_ws = websocket_connections[target_peer]
                await target_ws.send_text(data)
    except:
        pass
    finally:
        del websocket_connections[peer_id]
```

## 🔄 User Flow

### Unlock Liberty Mode
1. User taps SOS morse code (... ___ ...) on map ✅ Already implemented
2. Liberty enabled: `setLibertyEnabled(true)`
3. Camera orb appears on map with 🗽 badge

### Capture Alert
1. User sees something suspicious
2. Opens map view
3. Taps camera orb (📸🗽) in center of map
4. Camera opens (reuses GotJunk camera component)
5. Captures photo → tagged with current GPS coordinates
6. Alert created: `{ id, location: { lat, lng }, photo, timestamp, threatType }`

### Broadcast to Mesh
1. Alert sent to all connected peers via WebRTC
2. Peers receive alert and show 🧊 ice cube marker on their maps
3. Each peer re-broadcasts to their peers (mesh propagation)
4. Alert spreads through network organically

### View Alerts
1. Map shows 🧊 ice cube markers at alert locations
2. Tap marker → see alert photo + timestamp
3. Tap again → navigate to Browse filtered by location

## 🎨 UI Components

### Camera Orb on Map
```
         Map View
┌─────────────────────────┐
│  🗺️ Map Surface         │
│    🧊  🧊               │
│  🧊      🧊     🧊      │
│                         │
│         📸🗽            │ ← Camera orb
│         ^^^^            │    (center bottom)
│     Camera + Liberty    │
│                         │
│   [-]           [+]     │ ← Zoom controls
└─────────────────────────┘
```

### Ice Cube Markers
- **Color**: Blue (like ice)
- **Icon**: 🧊
- **Badge**: Shows peer count if multiple alerts at location
- **Click**: Opens alert photo + details

## 📊 Hybrid Fallback Decision Tree

```
User captures alert
  ↓
Attempt WebRTC P2P (Option A)
  ↓
Are peers online & reachable?
  ├─ YES → Direct P2P broadcast ✅
  │         (zero server costs)
  │
  └─ NO → Use signaling server (Option B) ⚠️
            ↓
            Queue message for offline peers
            Notify when peers come online
```

## 🔐 Privacy & Security

### What Is Stored
- **Client-side**: Alert photos (IndexedDB)
- **Server** (if fallback): Only signal data (temporary)
- **Mesh**: Alert metadata (not photos) for propagation

### What Is NOT Stored
- ❌ NO centralized alert database
- ❌ NO user tracking
- ❌ NO location history
- ❌ NO photo analysis by server

### Encryption
- **WebRTC**: DTLS encrypted by default
- **Signaling**: HTTPS + WSS
- **At Rest**: IndexedDB encrypted (browser sandbox)

## 🚀 Token Estimate

| Component | Tokens | Complexity |
|-----------|--------|------------|
| Camera orb on map | ~50 | Low |
| Alert capture flow | ~100 | Low |
| WebRTC mesh setup | ~200 | Medium |
| Signaling fallback | ~100 | Low |
| UI integration | ~100 | Low |
| **Total** | **~550** | **Medium** |

## ✅ WSP Compliance

- **WSP 3**: Domain separation (GotJunk frontend, Liberty utils)
- **WSP 22**: ModLog updates after implementation
- **WSP 50**: Pre-action verification (existing code reuse)
- **WSP 87**: Code navigation via HoloIndex

## 🎯 Next Steps

1. ✅ Document architecture (this file)
2. Add camera orb to PigeonMapView (when libertyEnabled)
3. Implement LibertyMesh class (WebRTC P2P)
4. Create signaling server (FastAPI)
5. Test alert capture + broadcast flow
6. Deploy signaling server (Cloud Run)
7. Test hybrid fallback scenarios

---

**Philosophy**: The simplest solution is often the best. Users ARE the intelligence - we just provide the mesh network to amplify their awareness.
