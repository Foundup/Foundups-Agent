import React, { useEffect, useState, lazy, Suspense } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Lazy load GlobeView to avoid Cesium loading issues
const GlobeView = lazy(() => import('./GlobeView').then(m => ({ default: m.GlobeView })));

// Fix for default marker icons in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Interfaces
interface GotJunkItem {
  id: string;
  location: { latitude: number; longitude: number };
  title: string;
  imageUrl: string;
  status: 'available' | 'sold' | 'auction'; // Green, Red, Gold
  timestamp: number;
}

interface LibertyAlert {
  id: string;
  location: { latitude: number; longitude: number };
  message: string;
  video_url?: string;
  timestamp: number;
}

interface MapViewProps {
  junkItems: GotJunkItem[]; // Geo-fenced 50km
  libertyAlerts: LibertyAlert[]; // Global (no geo-fence)
  userLocation?: { latitude: number; longitude: number };
  onClose: () => void;
  showLibertyAlerts: boolean; // Only show if Liberty Alert unlocked
}

// GotJunk Item Markers (Color-coded)
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
    className: 'gotjunk-marker',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  });
};

// Liberty Alert Ice Cube Marker (Global)
const iceCubeIcon = new L.DivIcon({
  html: '<div style="font-size: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">🧊</div>',
  className: 'ice-cube-marker',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

// User location marker
const userIcon = new L.DivIcon({
  html: '<div style="font-size: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">📍</div>',
  className: 'user-marker',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
});

// Auto-center map on user location
function MapCenter({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, 13);
  }, [center, map]);
  return null;
}

export const MapView: React.FC<MapViewProps> = ({
  junkItems,
  libertyAlerts,
  userLocation,
  onClose,
  showLibertyAlerts,
}) => {
  const defaultCenter: [number, number] = userLocation
    ? [userLocation.latitude, userLocation.longitude]
    : [37.7749, -122.4194]; // San Francisco default

  // Globe view state (3D Cesium globe for Liberty Alerts)
  const [isGlobeView, setGlobeView] = useState(false);

  // If globe view is active, render GlobeView instead of Leaflet map
  if (isGlobeView && showLibertyAlerts) {
    return (
      <Suspense fallback={
        <div className="fixed inset-0 bg-black z-30 flex items-center justify-center">
          <div className="text-white text-xl">Loading 3D Globe...</div>
        </div>
      }>
        <GlobeView alerts={libertyAlerts} onClose={() => setGlobeView(false)} />
      </Suspense>
    );
  }

  // DAEmon logging: mapview_component_mounted
  useEffect(() => {
    console.log('[DAEmon Beat] mapview_component_mounted', {
      showLibertyAlerts,
      junkItemsCount: junkItems.length,
      libertyAlertsCount: libertyAlerts.length,
      userLocation
    });
    return () => {
      console.log('[DAEmon Beat] mapview_component_unmounted');
    };
  }, []);

  return (
    <div
      className="fixed inset-0 bg-gray-900 z-20 flex flex-col"
      style={{ paddingBottom: '7rem' }}
    >
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between p-4 border-b border-white/10 bg-gray-800">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🗺️</span>
          <h2 className="text-xl font-bold text-white">
            {showLibertyAlerts ? 'Liberty Alert Map' : 'GotJunk Map'}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="bg-white/10 rounded-full p-2 text-white hover:bg-white/20 transition-colors"
          aria-label="Close Map"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      {/* Map Container */}
      <div className="flex-grow relative">
        <MapContainer
          center={defaultCenter}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
          className="z-0"
          scrollWheelZoom={true}
        >
          {/* OpenStreetMap Tiles */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />

          {/* Auto-center on user location or fit global bounds */}
          <MapCenter center={defaultCenter} fitBounds={globalBounds} />

          {/* User Location Marker */}
          {userLocation && (
            <>
              <Marker position={[userLocation.latitude, userLocation.longitude]} icon={userIcon}>
                <Popup>
                  <div className="text-center">
                    <strong>Your Location</strong>
                  </div>
                </Popup>
              </Marker>

              {/* 50km Geo-fence circle (for GotJunk items only) */}
              <Circle
                center={[userLocation.latitude, userLocation.longitude]}
                radius={50000} // 50km in meters
                pathOptions={{
                  color: '#3b82f6',
                  fillColor: '#3b82f6',
                  fillOpacity: 0.05,
                  weight: 2,
                  dashArray: '10, 10',
                }}
              />
            </>
          )}

          {/* GotJunk Item Markers (Geo-fenced 50km) */}
          {junkItems.map((item) => (
            <Marker
              key={item.id}
              position={[item.location.latitude, item.location.longitude]}
              icon={createJunkIcon(item.status)}
            >
              <Popup>
                <div className="p-2 min-w-[200px]">
                  {item.imageUrl && (
                    <img
                      src={item.imageUrl}
                      alt={item.title}
                      className="w-full h-32 object-cover rounded mb-2"
                    />
                  )}
                  <div className="flex items-center gap-2 mb-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor:
                          item.status === 'available'
                            ? '#22c55e'
                            : item.status === 'sold'
                            ? '#ef4444'
                            : '#eab308',
                      }}
                    />
                    <strong className="text-sm capitalize">{item.status}</strong>
                  </div>
                  <p className="font-medium mb-1">{item.title}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Liberty Alert Ice Cube Markers (GLOBAL - No geo-fence) */}
          {showLibertyAlerts &&
            libertyAlerts.map((alert) => (
              <Marker
                key={alert.id}
                position={[alert.location.latitude, alert.location.longitude]}
                icon={iceCubeIcon}
              >
                <Popup>
                  <div className="p-2 min-w-[200px]">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">🧊</span>
                      <strong className="text-lg">Liberty Alert</strong>
                    </div>
                    <p className="text-sm mb-2">{alert.message}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                    {alert.video_url && (
                      <button
                        className="mt-2 w-full bg-blue-500 text-white py-1 px-3 rounded text-sm hover:bg-blue-600 transition-colors"
                        onClick={() => window.open(alert.video_url, '_blank')}
                      >
                        ▶️ Watch Video
                      </button>
                    )}
                  </div>
                </Popup>
              </Marker>
            ))}
        </MapContainer>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm p-3 rounded-lg shadow-lg z-10 text-sm">
          <div className="font-bold mb-2">Legend</div>

          {/* GotJunk Items */}
          <div className="space-y-1 mb-3">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
              <span>Available</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded-full border-2 border-white"></div>
              <span>Sold/Moving</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded-full border-2 border-white"></div>
              <span>Auction</span>
            </div>
          </div>

          {/* Liberty Alerts (only if unlocked) */}
          {showLibertyAlerts && (
            <div className="border-t pt-2">
              <div className="flex items-center gap-2">
                <span className="text-xl">🧊</span>
                <span className="font-medium">Liberty Alert (Global)</span>
              </div>
            </div>
          )}

          {/* Geo-fence info */}
          <div className="text-xs text-gray-600 mt-2 border-t pt-2">
            <div>📍 = Your location</div>
            <div>⭕ = 50km radius (items only)</div>
          </div>
        </div>

        {/* Stats Badge + Globe Button */}
        <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
          {/* 🗽 Globe View Button (only if Liberty unlocked) */}
          {showLibertyAlerts && libertyAlerts.length > 0 && (
            <button
              onClick={() => setGlobeView(true)}
              className="bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 transition-colors"
              title="Open 3D Globe View"
            >
              <span className="text-2xl">🗽</span>
              <span className="font-bold">{libertyAlerts.length}</span>
            </button>
          )}

          {/* Stats Badge */}
          <div className="bg-gray-800/90 backdrop-blur-sm text-white px-4 py-2 rounded-full shadow-lg">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="font-bold text-sm">{junkItems.filter(i => i.status === 'available').length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
