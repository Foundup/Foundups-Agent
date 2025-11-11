import React, { useState, useEffect, useMemo } from 'react';
import { Map, Marker, Overlay } from 'pigeon-maps';
import { Z_LAYERS } from '../constants/zLayers';
import { MapClusterMarker, type ItemCluster } from './MapClusterMarker';
import { clusterItemsByLocation } from '../utils/clusterItems';
import type { CapturedItem } from '../types';

interface JunkItem {
  id: string;
  location: { latitude: number; longitude: number };
  title: string;
  imageUrl: string;
  status: 'available' | 'sold' | 'auction';
  timestamp: number;
}

interface LibertyAlert {
  id: string;
  location: { latitude: number; longitude: number };
  type: 'checkpoint' | 'raid' | 'ice';
  timestamp: number;
  radius?: number;
}

interface PigeonMapViewProps {
  junkItems: JunkItem[];  // Legacy format for Liberty Alerts
  capturedItems?: CapturedItem[];  // NEW: Pass raw items for clustering
  libertyAlerts?: LibertyAlert[];
  userLocation: { latitude: number; longitude: number } | null;
  onClose: () => void;
  onMarkerClick?: (location: { latitude: number; longitude: number }) => void;
  showLibertyAlerts?: boolean;
  useClustering?: boolean;  // Enable/disable clustering (default: true)
}

export const PigeonMapView: React.FC<PigeonMapViewProps> = ({
  junkItems,
  capturedItems = [],
  libertyAlerts = [],
  userLocation,
  onClose,
  onMarkerClick,
  showLibertyAlerts = false,
  useClustering = true,
}) => {
  // Global view for Liberty Alerts, local view for GotJunk items
  const isGlobalView = showLibertyAlerts && libertyAlerts.length > 0;

  const center: [number, number] = isGlobalView
    ? [20, 0] // Global center (shows full world map)
    : userLocation
    ? [userLocation.latitude, userLocation.longitude]
    : [37.7749, -122.4194]; // Default: San Francisco

  const [zoom, setZoom] = useState(isGlobalView ? 2 : 12); // Global zoom vs local zoom
  const [selectedItem, setSelectedItem] = useState<JunkItem | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<LibertyAlert | null>(null);
  const [legendExpanded, setLegendExpanded] = useState(false); // Collapsible legend

  // Cluster items by location (memoized to avoid re-computing on every render)
  const itemClusters = useMemo(() => {
    if (!useClustering || capturedItems.length === 0) {
      return [];
    }

    const clusters = clusterItemsByLocation(capturedItems);
    console.log('[GotJunk] Clustered', capturedItems.length, 'items into', clusters.length, 'clusters');
    return clusters;
  }, [capturedItems, useClustering]);

  // Lock body scroll when map is open (prevent Safari from clipping floating controls)
  useEffect(() => {
    if (typeof document === 'undefined') return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, []);

  console.log('[DAEmon Beat] pigeon_map_mounted', {
    junkItems: junkItems.length,
    libertyAlerts: libertyAlerts.length,
    showLibertyAlerts,
    userLocation,
  });

  // Color mapping for item status
  const getMarkerColor = (status: JunkItem['status']): string => {
    switch (status) {
      case 'available':
        return '#22c55e'; // Green
      case 'sold':
        return '#ef4444'; // Red
      case 'auction':
        return '#eab308'; // Gold
      default:
        return '#3b82f6'; // Blue
    }
  };

  return (
    <div
      className="fixed top-0 left-0 right-0 bottom-32 bg-black"
      style={{
        zIndex: Z_LAYERS.mapOverlay,
        touchAction: "pan-x pan-y pinch-zoom",
        userSelect: "none",
        WebkitUserSelect: "none",
        pointerEvents: "auto",
      }}
    >
      {/* Header - Title only, close button moved to thumb zone */}
      <div className="absolute top-0 left-0 right-0 z-40 bg-gradient-to-b from-black/80 to-transparent p-4">
        <h2 className="text-white text-xl font-bold text-center">
          {showLibertyAlerts && libertyAlerts.length > 0
            ? '🗽 Liberty Alert Map'
            : '🗺️ GotJunk Map'}
        </h2>
      </div>

      {/* Close Button - Lower thumb zone (bottom-3 = 12px from bottom) */}
      <button
        onClick={onClose}
        className="absolute bottom-3 left-4 z-40 grid place-items-center rounded-2xl backdrop-blur-md shadow-2xl transition-all bg-black/90 hover:bg-gray-900/90 border-2 border-white shadow-black/80"
        style={{
          width: 'var(--sb-size)',
          height: 'var(--sb-size)',
        }}
        title="Close Map"
      >
        <span className="text-white text-2xl font-bold">✕</span>
      </button>

      {/* Zoom Controls - Lower thumb zone (bottom-3 = 12px from bottom) */}
      <div className="absolute bottom-3 right-4 z-40 flex flex-col gap-2">
        <button
          onClick={() => setZoom(Math.min(zoom + 1, 18))}
          className="bg-gray-800 hover:bg-gray-700 text-white text-2xl w-12 h-12 rounded-lg shadow-2xl border-2 border-gray-600 font-bold"
          title="Zoom In"
        >
          +
        </button>
        <button
          onClick={() => setZoom(Math.max(zoom - 1, 1))}
          className="bg-gray-800 hover:bg-gray-700 text-white text-2xl w-12 h-12 rounded-lg shadow-2xl border-2 border-gray-600 font-bold"
          title="Zoom Out"
        >
          −
        </button>
        {isGlobalView && (
          <button
            onClick={() => setZoom(2)} // Reset to global view
            className="bg-gray-800 hover:bg-gray-700 text-white text-xl w-12 h-12 rounded-lg shadow-2xl border-2 border-gray-600"
            title="Reset Global View"
          >
            🌍
          </button>
        )}
      </div>

      {/* Pigeon Map */}
      <Map
        height={window.innerHeight}
        center={center}
        zoom={zoom}
        onBoundsChanged={({ zoom: newZoom }) => setZoom(newZoom)}
        mouseEvents={true}
        touchEvents={true}
        metaWheelZoom={true}
        twoFingerDrag={true}
        zoomSnap={false}
      >
        {/* User location marker */}
        {userLocation && (
          <Marker
            width={40}
            anchor={[userLocation.latitude, userLocation.longitude]}
            color="#3b82f6"
          />
        )}

        {/* GotJunk item markers - CLUSTERED (with thumbnails) or SIMPLE (fallback) */}
        {useClustering && itemClusters.length > 0 ? (
          // CLUSTERED: Show thumbnail grid markers (dynamic based on zoom level)
          itemClusters.map((cluster, index) => (
            <Overlay
              key={`cluster-${index}`}
              anchor={[cluster.location.latitude, cluster.location.longitude]}
            >
              <MapClusterMarker
                cluster={cluster}
                zoom={zoom}  // Pass zoom level for dynamic rendering
                onClick={(location) => {
                  if (onMarkerClick) {
                    console.log('[GotJunk] Cluster clicked:', location, 'items:', cluster.count);
                    onMarkerClick(location);
                  } else {
                    onClose();
                  }
                }}
              />
            </Overlay>
          ))
        ) : (
          // SIMPLE: Fallback to colored dots (original behavior)
          junkItems.map((item) => (
            <Marker
              key={item.id}
              width={30}
              anchor={[item.location.latitude, item.location.longitude]}
              color={getMarkerColor(item.status)}
              onClick={() => {
                if (onMarkerClick) {
                  onMarkerClick(item.location);
                } else {
                  onClose();
                }
              }}
            />
          ))
        )}

        {/* Liberty Alert markers (ice cubes) - only if unlocked */}
        {showLibertyAlerts &&
          libertyAlerts.map((alert) => (
            <Marker
              key={alert.id}
              width={isGlobalView ? 50 : 35} // Larger markers in global view
              anchor={[alert.location.latitude, alert.location.longitude]}
              color="#60a5fa"
              onClick={() => setSelectedAlert(alert)}
            />
          ))}

        {/* Selected item popup */}
        {selectedItem && (
          <Overlay
            anchor={[
              selectedItem.location.latitude,
              selectedItem.location.longitude,
            ]}
            offset={[0, -20]}
          >
            <div className="bg-white rounded-lg shadow-lg p-3 max-w-xs relative">
              <button
                onClick={() => setSelectedItem(null)}
                className="absolute top-1 right-1 text-gray-500 hover:text-black"
              >
                ✕
              </button>
              {selectedItem.imageUrl && (
                <img
                  src={selectedItem.imageUrl}
                  alt={selectedItem.title}
                  className="w-full h-32 object-cover rounded mb-2"
                />
              )}
              <h3 className="font-bold text-black">{selectedItem.title}</h3>
              <p className="text-sm text-gray-600 capitalize">
                Status: {selectedItem.status}
              </p>
            </div>
          </Overlay>
        )}

        {/* Selected Liberty Alert popup */}
        {selectedAlert && (
          <Overlay
            anchor={[
              selectedAlert.location.latitude,
              selectedAlert.location.longitude,
            ]}
            offset={[0, -25]}
          >
            <div className="bg-blue-900 text-white rounded-lg shadow-lg p-3 max-w-xs relative">
              <button
                onClick={() => setSelectedAlert(null)}
                className="absolute top-1 right-1 text-white/70 hover:text-white"
              >
                ✕
              </button>
              <h3 className="font-bold text-white flex items-center gap-2">
                <span className="text-2xl">🧊</span>
                Liberty Alert
              </h3>
              <p className="text-sm text-blue-200 capitalize mt-1">
                Type: {selectedAlert.type}
              </p>
              <p className="text-xs text-blue-300 mt-1">
                {new Date(selectedAlert.timestamp).toLocaleString()}
              </p>
              {selectedAlert.radius && (
                <p className="text-xs text-blue-300">
                  Radius: {selectedAlert.radius}km
                </p>
              )}
            </div>
          </Overlay>
        )}
      </Map>

      {/* Collapsible Legend - Higher position (100px from bottom) */}
      <div className="absolute bottom-[100px] left-4 z-40">
        {/* Legend Toggle Button */}
        <button
          onClick={() => setLegendExpanded(!legendExpanded)}
          className="bg-gray-800 hover:bg-gray-700 backdrop-blur rounded-full w-12 h-12 shadow-2xl border-2 border-gray-600 flex items-center justify-center transition-all"
          title="Toggle Legend"
        >
          <span className="text-2xl">{legendExpanded ? '✕' : 'ℹ️'}</span>
        </button>

        {/* Legend Popup (Expanded) */}
        {legendExpanded && (
          <div className="mt-2 bg-white backdrop-blur rounded-lg p-4 shadow-2xl border-2 border-gray-300 max-w-xs">
            <h3 className="font-bold mb-3 text-black text-sm">Map Legend</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-[#22c55e] bg-gray-200" />
                <span className="text-black">Available Items</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-[#ef4444] bg-gray-200" />
                <span className="text-black">Sold - Needs Move</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-[#eab308] bg-gray-200" />
                <span className="text-black">Auction Items</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-[#3b82f6] bg-gray-200" />
                <span className="text-black">Stuff I Want (Cart)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-[#8b5cf6] bg-gray-200" />
                <span className="text-black">My Items (Selling)</span>
              </div>

              {showLibertyAlerts && (
                <div className="border-t pt-2 mt-2">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded border-2 border-[#60a5fa] bg-blue-100" />
                    <span className="text-black">🧊 Liberty Alert</span>
                  </div>
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="text-xs text-black mt-3 pt-3 border-t">
              <div className="font-bold mb-1">Items on Map:</div>
              <div className="grid grid-cols-2 gap-1">
                <span>Total: {junkItems.length}</span>
                {showLibertyAlerts && <span>Alerts: {libertyAlerts.length}</span>}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
