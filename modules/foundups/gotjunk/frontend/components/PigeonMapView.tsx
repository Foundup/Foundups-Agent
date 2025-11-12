import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Map, Marker, Overlay } from 'pigeon-maps';
import { motion } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';
import { MapClusterMarker, type ItemCluster } from './MapClusterMarker';
import { clusterItemsByLocation } from '../utils/clusterItems';
import type { CapturedItem } from '../types';
import { Camera, CameraHandle } from './Camera';
import type { CaptureMode } from '../App';

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
  onLibertyActivate?: () => void;  // NEW: Callback when SOS morse code detected
  onLibertyCapture?: (blob: Blob, location: { latitude: number; longitude: number }) => void;  // NEW: Callback when user captures Liberty Alert
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
  onLibertyActivate,
  onLibertyCapture,
}) => {
  // Global view for Liberty Alerts, local view for GotJunk items
  const isGlobalView = showLibertyAlerts && isGlobalLiberty;

  const center: [number, number] = isGlobalView
    ? [20, 0] // Global center (shows full world map)
    : userLocation
    ? [userLocation.latitude, userLocation.longitude]
    : [37.7749, -122.4194]; // Default: San Francisco

  const [zoom, setZoom] = useState(12); // Start at local zoom
  const [selectedItem, setSelectedItem] = useState<JunkItem | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<LibertyAlert | null>(null);
  const [legendExpanded, setLegendExpanded] = useState(false); // Collapsible legend

  // SOS Morse Code Detection: ...___... (3 short, 3 long, 3 short)
  const [tapTimes, setTapTimes] = useState<number[]>([]);
  const tapStartTime = useRef<number>(0);
  const tapTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Liberty Alert Camera (for capturing alerts on map)
  const libertyCameraRef = useRef<CameraHandle>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  // Liberty Global View Toggle
  const [isGlobalLiberty, setIsGlobalLiberty] = useState(false);

  // Swipe gesture detection
  const touchStartY = useRef<number>(0);
  const touchEndY = useRef<number>(0);

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

  // SOS Tap Detection Handlers
  const handleMapTapStart = (e: React.MouseEvent | React.TouchEvent) => {
    // Only detect taps on the map surface (not on buttons/markers)
    const target = e.target as HTMLElement;
    if (target.closest('button') || target.closest('.map-cluster-marker')) {
      return; // Ignore taps on interactive elements
    }
    tapStartTime.current = Date.now();
  };

  const handleMapTapEnd = (e: React.MouseEvent | React.TouchEvent) => {
    const target = e.target as HTMLElement;
    if (target.closest('button') || target.closest('.map-cluster-marker')) {
      return; // Ignore taps on interactive elements
    }

    const tapDuration = Date.now() - tapStartTime.current;
    if (tapDuration === 0 || tapDuration > 1000) return; // Invalid tap (too long or no start)

    const SHORT_TAP = 200; // Short tap threshold (dot in morse code)

    setTapTimes(prev => {
      const newTaps = [...prev, tapDuration];
      // Keep only last 9 taps
      if (newTaps.length > 9) newTaps.shift();

      // Check for SOS pattern: SSSLLLSSS (3 short, 3 long, 3 short)
      if (newTaps.length === 9) {
        const pattern = newTaps.map(d => d < SHORT_TAP ? 'S' : 'L').join('');
        console.log('🗺️ Map SOS Pattern:', pattern);

        if (pattern === 'SSSLLLSSS') {
          console.log('🗽 SOS DETECTED ON MAP!');
          if (onLibertyActivate) {
            onLibertyActivate();
          }
          // Clear tap history after successful detection
          return [];
        }
      }

      return newTaps;
    });

    // Reset timeout - clear taps after 3 seconds of inactivity
    if (tapTimeoutRef.current) clearTimeout(tapTimeoutRef.current);
    tapTimeoutRef.current = setTimeout(() => {
      setTapTimes([]);
      console.log('🗺️ Map SOS timeout - taps cleared');
    }, 3000);
  };

  // Liberty Alert Camera Handlers
  const handleCameraOrbClick = () => {
    console.log('[Liberty] Camera orb clicked - opening camera for alert');
    setIsCameraOpen(true);
  };

  const handleLibertyCapture = (blob: Blob) => {
    console.log('[Liberty] Alert captured:', blob.type, blob.size, 'bytes');
    setIsCameraOpen(false);

    if (!onLibertyCapture || !userLocation) {
      console.warn('[Liberty] Cannot capture alert - missing callback or location');
      return;
    }

    // Pass blob + GPS coordinates to parent handler
    onLibertyCapture(blob, userLocation);
  };

  // Liberty Global View Toggle
  const handleLibertyToggle = () => {
    console.log('[Liberty] Toggling global view:', !isGlobalLiberty);
    setIsGlobalLiberty(!isGlobalLiberty);

    // Zoom to global or local view
    if (!isGlobalLiberty) {
      setZoom(2); // Zoom out to world view
    } else {
      setZoom(12); // Zoom back to local view
    }
  };

  // Swipe Up Gesture - Return to Home Location
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    touchEndY.current = e.changedTouches[0].clientY;
    const swipeDistance = touchStartY.current - touchEndY.current;

    // Swipe up (distance > 50px) → return to home
    if (swipeDistance > 50 && isGlobalLiberty) {
      console.log('[Liberty] Swipe up detected - returning to home location');
      setIsGlobalLiberty(false);
      setZoom(12);
    }
  };

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
      onMouseDown={handleMapTapStart}
      onMouseUp={handleMapTapEnd}
      onTouchStart={(e) => {
        handleMapTapStart(e);
        handleTouchStart(e);
      }}
      onTouchEnd={(e) => {
        handleMapTapEnd(e);
        handleTouchEnd(e);
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
        {/* Liberty Global View Toggle - Only when Liberty enabled */}
        {showLibertyAlerts && (
          <motion.button
            onClick={handleLibertyToggle}
            className={`text-3xl w-12 h-12 rounded-lg shadow-2xl border-2 transition-all ${
              isGlobalLiberty
                ? 'bg-blue-600 border-blue-400 hover:bg-blue-500'
                : 'bg-gray-800 border-gray-600 hover:bg-gray-700'
            }`}
            title={isGlobalLiberty ? "Return to Local View" : "View Global Liberty Alerts"}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🗽
          </motion.button>
        )}

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
      </div>

      {/* Liberty Alert Camera Orb - Center bottom (only in local view, not global) */}
      {showLibertyAlerts && !isCameraOpen && !isGlobalLiberty && (
        <motion.button
          onClick={handleCameraOrbClick}
          className="absolute bottom-24 left-1/2 -translate-x-1/2 w-20 h-20 bg-amber-500 rounded-full shadow-2xl border-4 border-white z-50 flex items-center justify-center"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          title="Capture Liberty Alert"
        >
          <span className="text-4xl">📸</span>
          {/* Liberty Badge */}
          <div className="absolute -top-2 -right-2 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center border-2 border-white">
            <span className="text-xl">🗽</span>
          </div>
        </motion.button>
      )}

      {/* Liberty Alert Camera Component */}
      {showLibertyAlerts && isCameraOpen && (
        <div className="absolute inset-0 z-50">
          <Camera
            ref={libertyCameraRef}
            onCapture={handleLibertyCapture}
            captureMode="photo" // Liberty alerts are photos only
          />
        </div>
      )}

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

        {/* Liberty Alert markers (🗽 statue) - only if unlocked */}
        {showLibertyAlerts &&
          libertyAlerts.map((alert) => (
            <Overlay
              key={alert.id}
              anchor={[alert.location.latitude, alert.location.longitude]}
            >
              <div
                onClick={() => setSelectedAlert(alert)}
                className="cursor-pointer hover:scale-110 transition-transform"
                title={alert.message}
              >
                <span className={isGlobalView ? "text-5xl" : "text-3xl"}>🗽</span>
              </div>
            </Overlay>
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
                <span className="text-2xl">🗽</span>
                Liberty Alert
              </h3>
              <p className="text-sm text-blue-200 mt-1">
                {selectedAlert.message}
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
                    <span className="text-xl">🗽</span>
                    <span className="text-black">Liberty Alert</span>
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
