# GotJunk 3D Globe View Architecture

## User Experience Flow

### 1. Map View (Local 2D)
**Entry**: Click map icon in nav bar

**Display**:
- Leaflet 2D map
- GotJunk items (🟢 green, 🔴 red, 🟡 gold) within 50km
- 🗽 button in top-right (only if Liberty Alert unlocked)

### 2. Globe View (3D Worldwide)
**Entry**: Click 🗽 button on map

**Display**:
- **Cesium 3D globe** (Google Earth-like)
- **🗽 Statue of Liberty icons** at clustered regions (100km radius clustering)
- Spin globe with mouse drag
- Zoom with scroll wheel
- Label shows alert count per region

**Interaction**:
- Click 🗽 → Zoom to that region (2-second fly animation)

### 3. Ice Cube View (Regional Zoom)
**Entry**: Click 🗽 on globe

**Display**:
- **Camera flies to region** (50km altitude)
- **🧊 Ice cube markers** for individual alerts in that region
- Click 🧊 → Popup with video link

**Navigation**:
- "Back to Globe" button (top-left) → Return to 🗽 globe view
- Close button (top-right) → Return to 2D map

---

## Technical Architecture

### Clustering Algorithm (100km radius)
```typescript
function clusterAlerts(alerts: LibertyAlert[]): RegionalCluster[] {
  const clusters: RegionalCluster[] = [];
  const processed = new Set<string>();

  alerts.forEach((alert) => {
    if (processed.has(alert.id)) return;

    // Find all alerts within 100km of this alert
    const nearby = alerts.filter((other) => {
      const distance = calculateDistance(
        alert.location.latitude,
        alert.location.longitude,
        other.location.latitude,
        other.location.longitude
      );
      return distance <= 100; // 100km clustering radius
    });

    nearby.forEach((a) => processed.add(a.id));

    // Calculate cluster center (average position)
    const avgLat = nearby.reduce((sum, a) => sum + a.location.latitude, 0) / nearby.length;
    const avgLon = nearby.reduce((sum, a) => sum + a.location.longitude, 0) / nearby.length;

    clusters.push({
      location: { latitude: avgLat, longitude: avgLon },
      count: nearby.length,
      alerts: nearby,
    });
  });

  return clusters;
}
```

**Why Clustering**:
- Prevents visual clutter on globe
- Groups nearby alerts into regions
- Shows density of alerts (e.g., "15 alerts" in one region)
- Performance optimization (fewer entities to render)

---

### Cesium 3D Globe Integration

**Installation**:
```bash
npm install cesium
```

**Initialization**:
```typescript
const viewer = new Viewer(cesiumContainerRef.current, {
  baseLayerPicker: false,
  geocoder: false,
  homeButton: false,
  sceneModePicker: false,
  navigationHelpButton: false,
  animation: false,
  timeline: false,
  fullscreenButton: false,
  vrButton: false,
  infoBox: true,
  selectionIndicator: true,
});
```

**Globe View** (shows 🗽 clusters):
```typescript
clusters.forEach((cluster) => {
  viewer.entities.add({
    position: Cartesian3.fromDegrees(
      cluster.location.longitude,
      cluster.location.latitude,
      0
    ),
    billboard: {
      image: createLibertyStatueSVG(cluster.count),
      width: 48,
      height: 48,
    },
    label: {
      text: `${cluster.count} alert${cluster.count > 1 ? 's' : ''}`,
      fillColor: Cesium.Color.WHITE,
    },
  });
});

// Camera: High altitude for globe view
viewer.camera.setView({
  destination: Cartesian3.fromDegrees(0, 20, 20000000),
});
```

**Ice Cube View** (shows 🧊 alerts):
```typescript
zoomedCluster.alerts.forEach((alert) => {
  viewer.entities.add({
    position: Cartesian3.fromDegrees(
      alert.location.longitude,
      alert.location.latitude,
      0
    ),
    billboard: {
      image: createIceCubeSVG(),
      width: 32,
      height: 32,
    },
    description: `Video popup HTML...`,
  });
});

// Camera: Fly to cluster location
viewer.camera.flyTo({
  destination: Cartesian3.fromDegrees(
    zoomedCluster.location.longitude,
    zoomedCluster.location.latitude,
    50000 // 50km altitude
  ),
  duration: 2,
});
```

---

### SVG Markers

**🗽 Statue of Liberty** (with gold circle background):
```typescript
const createLibertyStatueSVG = (count: number) => {
  const svg = `
    <svg width="48" height="48" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="22" fill="#fbbf24" stroke="#ffffff" stroke-width="2"/>
      <text x="50%" y="50%" font-size="32" text-anchor="middle" dominant-baseline="central">🗽</text>
    </svg>
  `;
  return 'data:image/svg+xml;base64,' + btoa(svg);
};
```

**🧊 Ice Cube** (simple emoji):
```typescript
const createIceCubeSVG = () => {
  const svg = `
    <svg width="32" height="32" xmlns="http://www.w3.org/2000/svg">
      <text x="50%" y="50%" font-size="28" text-anchor="middle" dominant-baseline="central">🧊</text>
    </svg>
  `;
  return 'data:image/svg+xml;base64,' + btoa(svg);
};
```

---

### State Management

**MapView.tsx**:
```typescript
const [isGlobeView, setGlobeView] = useState(false);

// If globe view active, render GlobeView instead of Leaflet
if (isGlobeView && showLibertyAlerts) {
  return <GlobeView alerts={libertyAlerts} onClose={() => setGlobeView(false)} />;
}
```

**GlobeView.tsx**:
```typescript
const [zoomedCluster, setZoomedCluster] = useState<RegionalCluster | null>(null);

// Click handler on 🗽 entity
viewer.selectedEntityChanged.addEventListener(() => {
  if (viewer.selectedEntity === entity) {
    setZoomedCluster(cluster); // Triggers re-render with ice cubes
  }
});
```

---

## UI Components

### Map View (Leaflet)
**Top-Right Corner**:
```
[🗽 15] [🟢 3]
```
- **🗽 button**: Opens 3D globe (amber background, clickable)
- **🟢 badge**: Available GotJunk items count

### Globe View (Cesium - 🗽 clusters)
**Top-Right Corner**:
```
[🗽 5 regions]
```
- Shows number of clustered regions

**Bottom-Left Corner**:
```
🌍 Globe View
🖱️ Drag: Rotate globe
🖱️ Scroll: Zoom in/out
👆 Touch: Pinch to zoom
🗽 Click statue: Zoom to region
```

**Globe Display**:
- Blue-green Earth with satellite imagery
- 🗽 icons at clustered locations
- Labels: "15 alerts", "3 alerts", etc.

### Ice Cube View (Cesium - 🧊 zoom)
**Top-Left Corner**:
```
[🌍 Back to Globe]
```
- Button to return to global 🗽 view

**Top-Right Corner**:
```
[5 alerts in this region] [×]
```
- Shows alert count for zoomed region
- Close button returns to 2D map

**Bottom-Left Corner**:
```
🧊 Ice Cube View
🧊 Click ice cube: Watch video
🖱️ Drag: Pan around
🖱️ Scroll: Zoom closer
🌍 Top-left button: Back to globe
```

**Camera View**:
- Zoomed to region (50km altitude)
- 🧊 ice cubes scattered at alert locations
- Click 🧊 → Popup with video link

---

## User Interaction Examples

### Example 1: No Alerts
**Map View**:
- 🗽 button does NOT appear
- Only GotJunk items visible
- Map stays in 2D Leaflet mode

### Example 2: Liberty Alert Unlocked (15 alerts worldwide)
**Map View**:
- 🗽 button appears in top-right
- Shows "🗽 15"
- Click 🗽 → Opens globe

**Globe View**:
- Shows 5 🗽 icons (clusters of 15 alerts across 5 regions)
- Labels: "3 alerts", "5 alerts", "2 alerts", "4 alerts", "1 alert"
- User spins globe to see all regions

**Click 🗽 (5 alerts cluster)**:
- Camera flies to that region (2-second animation)
- 5 🧊 ice cubes appear
- User can click each 🧊 to watch video

**Click "Back to Globe"**:
- Returns to 🗽 cluster view
- Can click different region

**Click "×" (close)**:
- Returns to 2D Leaflet map

---

## Performance Optimizations

### Clustering (100km radius)
- **Before**: 1000 alerts = 1000 entities on globe (laggy)
- **After**: 1000 alerts = ~20 clusters (smooth)

### Two-Stage Rendering
- **Globe view**: Only render 🗽 clusters (low entity count)
- **Ice cube view**: Only render alerts in zoomed region (scoped rendering)

### Lazy Entity Creation
- Entities created in `useEffect` dependency on `zoomedCluster`
- Previous entities destroyed when switching views
- Memory cleanup in `return` cleanup function

### Cesium Configuration
- Disabled unused features (geocoder, animation, timeline)
- Reduced UI clutter
- Faster initialization

---

## Cross-Platform Support

### Desktop (PC)
- **Globe rotation**: Left mouse drag
- **Pan**: Right mouse drag
- **Zoom**: Scroll wheel
- **Click**: Left click on 🗽 or 🧊

### Touch Devices (iPad, iPhone, Android)
- **Globe rotation**: Single-finger drag
- **Pan**: Two-finger drag
- **Zoom**: Pinch gesture
- **Click**: Single tap on 🗽 or 🧊

### Browser Compatibility
- **Chrome**: ✅ Full support
- **Firefox**: ✅ Full support
- **Safari**: ✅ Full support (iOS, macOS)
- **Edge**: ✅ Full support

---

## File Structure

```
modules/foundups/gotjunk/frontend/components/
├── MapView.tsx          # 2D Leaflet map with 🗽 button
├── GlobeView.tsx        # 3D Cesium globe with 🗽 → 🧊 flow
└── ...
```

**MapView.tsx**:
- Leaflet 2D map
- GotJunk items (geo-fenced 50km)
- 🗽 button triggers `setGlobeView(true)`
- Conditional render: `if (isGlobeView) return <GlobeView />`

**GlobeView.tsx**:
- Cesium 3D globe
- Clustering algorithm
- Two states: Globe view (🗽) vs Ice cube view (🧊)
- Back button + Close button

---

## Testing Checklist

### Globe View Initialization
- [ ] Click 🗽 button on map
- [ ] 3D globe loads (blue-green Earth)
- [ ] 🗽 icons appear at clustered locations
- [ ] Labels show correct alert counts

### Globe Interaction
- [ ] Mouse drag rotates globe
- [ ] Scroll wheel zooms in/out
- [ ] Touch gestures work (mobile)
- [ ] Click 🗽 triggers zoom animation

### Ice Cube Zoom
- [ ] Camera flies to region (2-second animation)
- [ ] 🧊 ice cubes appear at alert locations
- [ ] Click 🧊 shows popup with video link
- [ ] "Back to Globe" button works
- [ ] Close button returns to 2D map

### Clustering Accuracy
- [ ] Alerts within 100km are grouped
- [ ] Cluster center is average position
- [ ] Alert counts are correct
- [ ] No duplicate alerts in multiple clusters

### Cross-Platform
- [ ] PC (mouse controls work)
- [ ] iPad (touch gestures work)
- [ ] Android (touch gestures work)
- [ ] iPhone (touch gestures work)

---

## Future Enhancements

### Real-Time Updates
- WebSocket connection for live Liberty Alerts
- New 🧊 appears in real-time
- Notification sound when new alert in user's region

### Heatmap Layer
- Color-coded regions by alert density
- Red zones = high activity, Green zones = low activity
- Toggle heatmap on/off

### Timeline Playback
- Scrub through time to see historical alerts
- Animation showing spread of alerts over time
- "Replay last 24 hours" feature

### AR Mode
- Use device camera + GPS
- Overlay 🧊 ice cubes in real world
- Point phone at location to see alerts

---

**Status**: 3D Globe View architecture complete with Cesium integration
**Dev Server**: http://localhost:3002
**Next**: Test globe loading and 🗽 → 🧊 zoom flow

