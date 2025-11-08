# GotJunk Map Architecture - First Principles

## Two Separate Marker Systems

### 1. GotJunk Items (Geo-fenced 50km)
**Purpose**: Show items for sale/trade/auction within local radius

**Marker Colors**:
- 🟢 **Green** = Available (items for sale/trade)
- 🔴 **Red** = Sold/Need Moved (items already sold, waiting pickup)
- 🟡 **Gold** = Auction (items in active bidding)

**Visibility**:
- **Only visible within 50km radius** of user's location
- 50km geo-fence circle displayed on map (blue dashed line)
- Items outside radius are filtered out

**Data Source**:
- `keptItems` state (photos/videos user has kept)
- Each item has `latitude`, `longitude` from when photo was taken
- Stored in IndexedDB via `storage.ts`

**Map Display**:
- Small colored circles (24px) with white border
- Click marker → popup with photo, title, status, timestamp
- Stats badge shows count of available items (green)

---

### 2. Liberty Alerts (Global)
**Purpose**: Emergency alerts visible to ALL users worldwide

**Marker Icon**: 🧊 Ice cube emoji

**Visibility**:
- **Global** - No geo-fence restriction
- Visible to all users regardless of distance
- Only shown if Liberty Alert is unlocked (SOS pattern)

**Data Source**:
- `libertyAlerts` state
- Created when keyword detected during video recording
- Keywords: "ice", "immigration", "checkpoint", "raid", etc.

**Map Display**:
- Large ice cube emoji (32px) with drop shadow
- Click marker → popup with message, video link, timestamp
- Stats badge shows ice cube count (only if Liberty unlocked)

---

## Map Features

### User Location
- **Marker**: 📍 Red pin emoji
- **Center**: Map auto-centers on user location (zoom level 13)
- **Permissions**: Browser requests geolocation on app load
- **Fallback**: San Francisco (37.7749, -122.4194) if permission denied

### Geo-fence Circle
- **Radius**: 50km (50,000 meters)
- **Color**: Blue (#3b82f6)
- **Style**: Dashed line, 5% fill opacity
- **Purpose**: Visual indicator of GotJunk item visibility range

### Legend (Bottom-left)
Shows marker meanings:
- Green circle = Available
- Red circle = Sold/Moving
- Gold circle = Auction
- 🧊 Ice cube = Liberty Alert (Global) [only if unlocked]
- 📍 = Your location
- ⭕ = 50km radius (items only)

### Stats Badge (Top-right)
- Shows count of available items (green dot)
- Shows count of Liberty Alerts (ice cube) if unlocked
- **Clickable ice cube count** toggles global view:
  - 📍 icon = Local view (user location + 50km radius)
  - 🌍 icon = Global view (all Liberty Alerts worldwide)
- Dark background with backdrop blur
- Hover effect on ice cube button

---

## Technical Implementation

### Leaflet Setup
```typescript
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
```

### Marker Icons
```typescript
// GotJunk colored circles
const createJunkIcon = (status: 'available' | 'sold' | 'auction') => {
  const colors = {
    available: '#22c55e', // Green
    sold: '#ef4444',      // Red
    auction: '#eab308',   // Gold
  };
  return new L.DivIcon({
    html: `<div style="
      width: 24px;
      height: 24px;
      background-color: ${colors[status]};
      border: 3px solid white;
      border-radius: 50%;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    "></div>`,
  });
};

// Liberty Alert ice cube
const iceCubeIcon = new L.DivIcon({
  html: '<div style="font-size: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">🧊</div>',
});

// User location
const userIcon = new L.DivIcon({
  html: '<div style="font-size: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">📍</div>',
});
```

### Leaflet Icon Fix (Critical)
**Issue**: Default Leaflet markers don't load properly in bundlers

**Solution**:
```typescript
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});
```

---

## Map View Props

```typescript
interface MapViewProps {
  junkItems: GotJunkItem[];           // Geo-fenced 50km
  libertyAlerts: LibertyAlert[];      // Global (no geo-fence)
  userLocation?: { latitude: number; longitude: number };
  onClose: () => void;
  showLibertyAlerts: boolean;         // Only show if Liberty Alert unlocked
}
```

### GotJunkItem Interface
```typescript
interface GotJunkItem {
  id: string;
  location: { latitude: number; longitude: number };
  title: string;
  imageUrl: string;
  status: 'available' | 'sold' | 'auction';
  timestamp: number;
}
```

### LibertyAlert Interface
```typescript
interface LibertyAlert {
  id: string;
  location: { latitude: number; longitude: number };
  message: string;
  video_url?: string;
  timestamp: number;
}
```

---

## App.tsx Integration

### Data Mapping
```typescript
// Convert keptItems to GotJunk map markers
junkItems={keptItems.map(item => ({
  id: item.id,
  location: {
    latitude: item.latitude || userLocation?.latitude || 37.7749,
    longitude: item.longitude || userLocation?.longitude || -122.4194,
  },
  title: item.id.split('-')[0] || 'Item',
  imageUrl: item.blobUrl || '',
  status: 'available' as const, // TODO: Add status tracking to CapturedItem
  timestamp: Date.now(),
}))}
```

### Map Trigger
- Click map icon in nav bar → `setMapOpen(true)`
- Map opens with z-index 20 (below nav bar z-30)
- Nav bar stays persistent on map screen
- Close button returns to main screen

---

## Future Enhancements

### GotJunk Item Status Tracking
**Current**: All items marked as 'available' (green)

**TODO**: Add status field to `CapturedItem` interface
```typescript
interface CapturedItem {
  // ... existing fields
  marketStatus?: 'available' | 'sold' | 'auction';
}
```

**Flow**:
1. User swipes right (keep) → item status = 'available' (green marker)
2. Item sold → user updates status → marker turns red
3. User lists on auction → marker turns gold

### Backend Integration
**Current**: Items stored in IndexedDB (offline-first)

**TODO**: Sync with backend API
- POST /api/gotjunk/items (create item listing)
- GET /api/gotjunk/items?lat=X&lon=Y&radius=50 (fetch nearby items)
- PATCH /api/gotjunk/items/:id (update status)

### Liberty Alert Backend
**Existing Module**: `modules/communication/liberty_alert/`
- MeshNetwork (peer-to-peer broadcasting)
- AlertBroadcaster (alert distribution)
- Models (Alert, GeoPoint, ThreatType)

**Integration**: Import existing backend (93% code reuse)

---

## Testing Checklist

### Map Loading
- [ ] OpenStreetMap tiles load properly (no gray screen)
- [ ] Map centers on user location (if permission granted)
- [ ] San Francisco fallback if location denied
- [ ] Zoom level 13 default
- [ ] Scroll wheel zoom works

### GotJunk Markers
- [ ] Kept items appear as green circles
- [ ] Markers only show within 50km radius
- [ ] 50km geo-fence circle visible
- [ ] Click marker shows popup with photo
- [ ] Popup displays title, status, timestamp

### Liberty Alert Markers
- [ ] Ice cubes only appear if Liberty unlocked
- [ ] Ice cubes visible globally (no geo-fence)
- [ ] Click ice cube shows popup with message
- [ ] Video link opens in new tab (if available)

### UI Components
- [ ] Legend displays correctly (bottom-left)
- [ ] Stats badge updates counts (top-right)
- [ ] Header shows "GotJunk Map" or "Liberty Alert Map"
- [ ] Close button returns to main screen
- [ ] Nav bar stays visible (z-index hierarchy)

### Cross-Platform
- [ ] PC (Windows) - Mouse scroll, click interactions
- [ ] iPad (Safari) - Touch gestures, pinch zoom
- [ ] Android (Chrome) - Touch gestures, pinch zoom
- [ ] iPhone (Safari) - Touch gestures, pinch zoom

---

## Architecture Benefits

### Separation of Concerns
- **GotJunk items** = Local marketplace (geo-fenced)
- **Liberty Alerts** = Emergency system (global)
- Same map, different purposes, different rules

### Scalability
- Geo-fencing reduces server load (only query 50km radius)
- Global alerts visible to all without distance filtering
- Offline-first with IndexedDB (PWA ready)

### Privacy
- GotJunk items: Location captured when photo taken (user consent)
- Liberty Alerts: Location captured during emergency (user-initiated)
- No background tracking

### Performance
- Leaflet optimized for 1000+ markers
- Only render items within 50km (filtered before render)
- Lazy load images in popups
- CDN-hosted map tiles (OpenStreetMap)

---

**Status**: Map architecture complete with dual marker system
**Dev Server**: http://localhost:3002
**Next**: Test map loading and marker display

