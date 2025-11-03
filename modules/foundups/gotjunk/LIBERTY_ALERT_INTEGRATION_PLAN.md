# Liberty Alert Integration Plan - GotJunk Easter Egg

**Status**: Ready for Implementation
**Trigger**: SOS Morse Code on Camera Orb
**Unlock**: Permanent (localStorage)
**Icon**: 🗽 Liberty Alert Mode

## Architecture

```
GotJunk Frontend (React/Vite)
├── Camera Orb → SOS Detection (... --- ...)
├── Liberty Icon 🗽 → Appears in Nav Bar (permanent)
├── LibertyAlert.tsx → Full UI overlay
└── Leaflet Map → Ice cube 🧊 markers

Liberty Alert Backend (Existing Python - REUSE)
├── mesh_network.py → WebRTC P2P mesh
├── models.py → Alert, GeoPoint, ThreatType
├── alert_broadcaster.py → Broadcast system
└── NEW: FastAPI wrapper for frontend
```

## Implementation Steps

### 1. SOS Morse Detection (~50 tokens)

**File**: `modules/foundups/gotjunk/frontend/App.tsx`

```typescript
// Add state
const [tapTimes, setTapTimes] = useState<number[]>([]);
const [libertyUnlocked, setLibertyUnlocked] = useState(
  () => localStorage.getItem('libertyUnlocked') === 'true'
);

// Modify camera orb in BottomNavBar (line 158-166)
<div
  className="w-[88px] h-[88px] p-1 bg-gray-800 rounded-full -translate-y-16 shadow-2xl cursor-pointer"
  onMouseDown={handlePressStart}
  onMouseUp={handlePressEnd}
  onTouchStart={handlePressStart}
  onTouchEnd={handlePressEnd}
  onClick={handleOrbTap}  // ADD THIS
>

// SOS detection function
const handleOrbTap = () => {
  const now = Date.now();
  const newTaps = [...tapTimes, now].slice(-9);
  setTapTimes(newTaps);

  if (detectSOS(newTaps)) {
    localStorage.setItem('libertyUnlocked', 'true');
    setLibertyUnlocked(true);
  }
};

const detectSOS = (taps: number[]): boolean => {
  if (taps.length < 9) return false;

  // SOS = 3 short (< 200ms apart), 3 long (> 400ms apart), 3 short
  const intervals = taps.slice(1).map((t, i) => t - taps[i]);

  const short1 = intervals.slice(0, 2).every(i => i < 200);
  const pause1 = intervals[2] > 400;
  const long = intervals.slice(3, 5).every(i => i > 400);
  const pause2 = intervals[5] > 400;
  const short2 = intervals.slice(6, 8).every(i => i < 200);

  return short1 && pause1 && long && pause2 && short2;
};
```

### 2. Add Liberty Icon to Nav Bar (~30 tokens)

**File**: `modules/foundups/gotjunk/frontend/components/BottomNavBar.tsx`

```typescript
// Add props
interface BottomNavBarProps {
  // ... existing props
  libertyUnlocked: boolean;
  onLibertyClick: () => void;
}

// Add icon (line 192, before MapIcon)
{libertyUnlocked && (
  <motion.button
    onClick={onLibertyClick}
    aria-label="Liberty Alert"
    className="p-3 rounded-full flex items-center justify-center text-white transition-colors bg-amber-500/20 hover:bg-amber-500/30"
    variants={buttonVariants}
    whileTap="tap"
  >
    <span className="text-2xl">🗽</span>
  </motion.button>
)}
```

### 3. Liberty Alert Overlay Component (~200 tokens)

**File**: `modules/foundups/gotjunk/frontend/components/LibertyAlert.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface Alert {
  id: string;
  location: { lat: number; lng: number };
  message: string;
  timestamp: string;
}

interface LibertyAlertProps {
  onClose: () => void;
}

export const LibertyAlert: React.FC<LibertyAlertProps> = ({ onClose }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [meshPeers, setMeshPeers] = useState(0);
  const [userLocation, setUserLocation] = useState({ lat: 0, lng: 0 });

  useEffect(() => {
    // Get user location
    navigator.geolocation.getCurrentPosition((pos) => {
      setUserLocation({
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
      });
    });

    // Fetch alerts from backend
    fetch('/api/liberty/alerts')
      .then(res => res.json())
      .then(data => setAlerts(data.alerts));

    // Connect to mesh network
    fetch('/api/liberty/mesh/status')
      .then(res => res.json())
      .then(data => setMeshPeers(data.peers));
  }, []);

  const broadcastAlert = async (message: string) => {
    await fetch('/api/liberty/broadcast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: userLocation,
        message,
        threat_type: 'SURVEILLANCE_VEHICLE',
      }),
    });
  };

  return (
    <div className="fixed inset-0 z-50 bg-gray-900">
      {/* Header */}
      <div className="bg-amber-600 p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-white flex items-center">
          <span className="mr-2">🗽</span>
          Liberty Alert
        </h1>
        <button onClick={onClose} className="text-white text-2xl">×</button>
      </div>

      {/* Mesh Status */}
      <div className="bg-gray-800 p-3 text-white text-sm">
        <span className="text-green-400">● Connected</span>
        <span className="ml-4">{meshPeers} peers in mesh</span>
      </div>

      {/* Map */}
      <div className="h-96">
        <MapContainer
          center={[userLocation.lat, userLocation.lng]}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='© OpenStreetMap contributors'
          />
          {alerts.map(alert => (
            <Marker
              key={alert.id}
              position={[alert.location.lat, alert.location.lng]}
              icon={iceCubeIcon}
            >
              <Popup>
                <div>
                  <p className="font-bold">🧊 Liberty User</p>
                  <p className="text-sm">{alert.message}</p>
                  <p className="text-xs text-gray-500">{alert.timestamp}</p>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* Alert List */}
      <div className="p-4 overflow-y-auto">
        <h2 className="font-bold mb-2">Recent Alerts</h2>
        {alerts.map(alert => (
          <div key={alert.id} className="bg-gray-800 p-3 mb-2 rounded">
            <p className="text-white">{alert.message}</p>
            <p className="text-gray-400 text-sm">{alert.timestamp}</p>
          </div>
        ))}
      </div>

      {/* Broadcast Button */}
      <div className="fixed bottom-4 right-4">
        <button
          onClick={() => broadcastAlert('Alert: Surveillance detected')}
          className="bg-red-600 text-white px-6 py-3 rounded-full shadow-lg"
        >
          🚨 Broadcast Alert
        </button>
      </div>
    </div>
  );
};

// Ice cube marker icon
const iceCubeIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><text y="28" font-size="28">🧊</text></svg>',
  iconSize: [32, 32],
});
```

### 4. FastAPI Backend Wrapper (~100 tokens)

**File**: `modules/foundups/gotjunk/backend/liberty_api.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sys
sys.path.append('../../..')

from modules.communication.liberty_alert.src.mesh_network import MeshNetwork
from modules.communication.liberty_alert.src.models import Alert, GeoPoint, ThreatType

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

mesh = MeshNetwork()

class BroadcastRequest(BaseModel):
    location: dict
    message: str
    threat_type: str

@app.get("/api/liberty/alerts")
async def get_alerts():
    alerts = mesh.get_recent_alerts()
    return {
        "alerts": [
            {
                "id": a.id,
                "location": {"lat": a.location.latitude, "lng": a.location.longitude},
                "message": a.message,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in alerts
        ]
    }

@app.get("/api/liberty/mesh/status")
async def mesh_status():
    return {
        "peers": len(mesh.peers),
        "connected": len(mesh.peers) > 0,
    }

@app.post("/api/liberty/broadcast")
async def broadcast_alert(req: BroadcastRequest):
    alert = Alert(
        location=GeoPoint(req.location["lat"], req.location["lng"]),
        message=req.message,
        threat_type=ThreatType[req.threat_type],
    )
    await mesh.broadcast(alert)
    return {"success": True, "alert_id": alert.id}
```

### 5. Update package.json Dependencies

**File**: `modules/foundups/gotjunk/frontend/package.json`

```json
{
  "dependencies": {
    "react-leaflet": "^4.2.1",
    "leaflet": "^1.9.4"
  }
}
```

### 6. Update cloudbuild.yaml for Backend

**File**: `modules/foundups/gotjunk/cloudbuild.yaml`

```yaml
steps:
  # Step 1: Install frontend dependencies
  - name: 'node:20'
    dir: 'modules/foundups/gotjunk/frontend'
    entrypoint: 'npm'
    args: ['install']

  # Step 2: Build frontend
  - name: 'node:20'
    dir: 'modules/foundups/gotjunk/frontend'
    entrypoint: 'npm'
    args: ['run', 'build']

  # Step 3: Install Python backend dependencies
  - name: 'python:3.11'
    dir: 'modules/foundups/gotjunk/backend'
    entrypoint: 'pip'
    args: ['install', '-r', 'requirements.txt', '-t', '.']

  # Step 4: Deploy to Cloud Run with backend
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    dir: 'modules/foundups/gotjunk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'gotjunk'
      - '--source=.'
      - '--region=us-west1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--update-secrets=GEMINI_API_KEY_GotJunk=GEMINI_API_KEY_GOTJUNK:latest'
```

## Token Estimate

- SOS Detection: ~50 tokens
- Liberty Icon: ~30 tokens
- LibertyAlert.tsx: ~200 tokens
- FastAPI Backend: ~100 tokens
- Integration: ~50 tokens
**Total**: ~430 tokens (not weeks!)

## Features

✅ SOS morse code unlock (permanent via localStorage)
✅ 🗽 Liberty Alert icon in nav bar
✅ Leaflet map with real-time alerts
✅ 🧊 Ice cube markers for Liberty users
✅ WebRTC P2P mesh networking (reuses existing Python)
✅ Alert broadcasting
✅ Mesh peer status

## Next Steps

1. Implement SOS detection
2. Add Liberty icon to nav
3. Create LibertyAlert.tsx component
4. Create FastAPI backend wrapper
5. Deploy to Cloud Run
6. Test SOS unlock sequence
7. Verify map + mesh features

**Total Implementation Time**: ~430 tokens (0102 execution, not human weeks!)
