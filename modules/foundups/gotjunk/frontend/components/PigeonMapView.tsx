import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Map, Marker, Overlay } from 'pigeon-maps';
import { motion } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';
import { MapClusterMarker, type ItemCluster } from './MapClusterMarker';
import { clusterItemsByLocation } from '../utils/clusterItems';
import type { CapturedItem, ItemClassification } from '../types';
import { MapFilterModal } from './MapFilterModal';

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
  message: string;
  video_url?: string;
  timestamp: number;
  type: 'region' | 'capture'; // region = 🗽 (global hot zones), capture = 🧊 (user-captured events)
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
  navigationCenter?: { latitude: number; longitude: number } | null;  // NEW: Center map on this location (for arrow navigation)
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
  navigationCenter = null,
}) => {
  // Liberty Global View Toggle (MUST be declared before use in center calculation)
  const [isGlobalLiberty, setIsGlobalLiberty] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState<{ latitude: number; longitude: number } | null>(null);

  // Global view for Liberty Alerts (world map), local view for GotJunk items
  const isGlobalView = showLibertyAlerts && isGlobalLiberty;

  const center: [number, number] = isGlobalView
    ? [20, 0] // World center (shows entire globe with all continents)
    : navigationCenter
    ? [navigationCenter.latitude, navigationCenter.longitude] // Arrow navigation center (priority)
    : selectedRegion
    ? [selectedRegion.latitude, selectedRegion.longitude] // Zoomed to selected 🗽 region
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

  // Swipe gesture detection
  const touchStartY = useRef<number>(0);
  const touchEndY = useRef<number>(0);

  // Map Filter Modal state
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ItemClassification[]>(() => {
    // Load initial filters from localStorage
    const stored = localStorage.getItem('gotjunk_map_filters');
    if (stored) {
      try {
        const filters = JSON.parse(stored);
        return (Object.keys(filters) as ItemClassification[]).filter(
          key => filters[key]
        );
      } catch {
        // Fall through to default
      }
    }
    // Default: all filters enabled
    return ['free', 'discount', 'bid', 'share', 'wanted', 'food', 'couch', 'camping', 'housing', 'ice', 'police'];
  });

  // Split items: Liberty Alert items (🧊) vs regular items, then apply filters
  const { libertyItems, regularItems } = useMemo(() => {
    const liberty = capturedItems.filter(item => item.libertyAlert);
    const regular = capturedItems.filter(item => !item.libertyAlert);

    // Apply filters to both Liberty and regular items (based on classification)
    // Items WITHOUT classification are always visible (bypass filter)
    // Items WITH classification are only visible if filter is enabled
    const filteredLiberty = liberty.filter(item =>
      !item.classification || activeFilters.includes(item.classification)
    );
    const filteredRegular = regular.filter(item =>
      !item.classification || activeFilters.includes(item.classification)
    );

    console.log('[GotJunk] Split items:', filteredLiberty.length, 'Liberty (🧊)', filteredRegular.length, 'regular');
    console.log('[GotJunk] Active filters:', activeFilters);
    return { libertyItems: filteredLiberty, regularItems: filteredRegular };
  }, [capturedItems, activeFilters]);

  // Cluster items by location (memoized to avoid re-computing on every render)
  const itemClusters = useMemo(() => {
    if (!useClustering || regularItems.length === 0) {
      return [];
    }

    const clusters = clusterItemsByLocation(regularItems);
    console.log('[GotJunk] Clustered', regularItems.length, 'items into', clusters.length, 'clusters');
    return clusters;
  }, [regularItems, useClustering]);

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

  // SOS Tap Detection Handlers (ENHANCED DEBUG VERSION)
  const handleMapTapStart = (e: React.MouseEvent | React.TouchEvent) => {
    // Only detect taps on the map surface (not on buttons/markers)
    const target = e.target as HTMLElement;
    const isButton = target.closest('button');
    const isMarker = target.closest('.map-cluster-marker');

    console.log('🗺️ [SOS DEBUG] Tap START detected:', {
      isButton: !!isButton,
      isMarker: !!isMarker,
      targetTag: target.tagName,
      targetClass: target.className,
      willRecord: !isButton && !isMarker
    });

    if (isButton || isMarker) {
      console.log('🗺️ [SOS DEBUG] Tap FILTERED (interactive element)');
      return; // Ignore taps on interactive elements
    }

    tapStartTime.current = Date.now();
    console.log('🗺️ [SOS DEBUG] Tap START recorded:', tapStartTime.current);
  };

  const handleMapTapEnd = (e: React.MouseEvent | React.TouchEvent) => {
    const target = e.target as HTMLElement;
    const isButton = target.closest('button');
    const isMarker = target.closest('.map-cluster-marker');

    if (isButton || isMarker) {
      console.log('🗺️ [SOS DEBUG] Tap END FILTERED (interactive element)');
      return; // Ignore taps on interactive elements
    }

    const tapDuration = Date.now() - tapStartTime.current;
    console.log('🗺️ [SOS DEBUG] Tap END recorded:', {
      startTime: tapStartTime.current,
      endTime: Date.now(),
      duration: tapDuration,
      valid: tapDuration > 0 && tapDuration <= 1000
    });

    if (tapDuration === 0 || tapDuration > 1000) {
      console.log('🗺️ [SOS DEBUG] Tap INVALID (duration:', tapDuration, 'ms)');
      return; // Invalid tap (too long or no start)
    }

    const SHORT_TAP = 200; // Short tap threshold (dot in morse code)
    const tapType = tapDuration < SHORT_TAP ? 'SHORT (S)' : 'LONG (L)';

    setTapTimes(prev => {
      const newTaps = [...prev, tapDuration];
      // Keep only last 9 taps
      if (newTaps.length > 9) newTaps.shift();

      console.log('🗺️ [SOS DEBUG] Tap recorded:', {
        duration: tapDuration,
        type: tapType,
        tapCount: newTaps.length,
        allDurations: newTaps,
        pattern: newTaps.map(d => d < SHORT_TAP ? 'S' : 'L').join('')
      });

      // Check for SOS pattern: SSSLLLSSS (3 short, 3 long, 3 short)
      if (newTaps.length === 9) {
        const pattern = newTaps.map(d => d < SHORT_TAP ? 'S' : 'L').join('');
        console.log('🗺️ [SOS DEBUG] 9 TAPS COLLECTED! Pattern:', pattern, '| Target: SSSLLLSSS');

        if (pattern === 'SSSLLLSSS') {
          console.log('🗽 SOS DETECTED ON MAP! ✓✓✓');
          if (onLibertyActivate) {
            onLibertyActivate();
          } else {
            console.warn('🗺️ [SOS DEBUG] onLibertyActivate callback is undefined!');
          }
          // Clear tap history after successful detection
          return [];
        } else {
          console.log('🗺️ [SOS DEBUG] Pattern MISMATCH - continuing to collect taps');
        }
      } else {
        console.log('🗺️ [SOS DEBUG] Need', 9 - newTaps.length, 'more taps to check pattern');
      }

      return newTaps;
    });

    // Reset timeout - clear taps after 3 seconds of inactivity
    if (tapTimeoutRef.current) clearTimeout(tapTimeoutRef.current);
    tapTimeoutRef.current = setTimeout(() => {
      console.log('🗺️ [SOS DEBUG] TIMEOUT - Clearing all taps (3s inactivity)');
      setTapTimes([]);
    }, 3000);
  };

  // Liberty Alert Camera Handlers
  // Liberty Global View Toggle
  const handleLibertyToggle = () => {
    console.log('[Liberty] Toggling global view:', !isGlobalLiberty);
    setIsGlobalLiberty(!isGlobalLiberty);

    // Zoom to global or local view
    if (!isGlobalLiberty) {
      setZoom(2); // Maximum zoom out - entire world view with all continents
      setSelectedRegion(null); // Clear selected region when going global
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

    // Swipe up (distance > 50px) → return to home location
    if (swipeDistance > 50 && isGlobalLiberty) {
      console.log('[Liberty] Swipe up detected - returning to home location');
      setIsGlobalLiberty(false);
      setSelectedRegion(null); // Clear selected region
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
      {/* Header - Title with mic (inactive) and filter icons */}
      <div className="absolute top-0 left-0 right-0 z-40 bg-gradient-to-b from-black/80 to-transparent p-4">
        <div className="flex items-center justify-between">
          {/* Left spacer for balance */}
          <div className="w-20"></div>

          {/* Center title */}
          <h2 className="text-white text-xl font-bold text-center flex-1">
            {showLibertyAlerts && libertyAlerts.length > 0
              ? '🗽 Liberty Alert Map'
              : '🗺️ GotJunk Map'}
          </h2>

          {/* Right icons: Mic (inactive) + Filter */}
          <div className="flex items-center gap-3">
            {/* Mic icon with red slash (inactive - future voice search) */}
            <div className="relative" title="Voice search (coming soon)">
              <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
              {/* Red diagonal slash */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-8 h-0.5 bg-red-500 transform rotate-45"></div>
              </div>
            </div>

            {/* Filter icon */}
            <button
              onClick={() => setShowFilterModal(true)}
              className="text-white hover:text-blue-400 transition-colors"
              title="Filter items"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
            </button>
          </div>
        </div>
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

        {/* Liberty Alert user captures - Thumbnail at high zoom, icon at low zoom */}
        {showLibertyAlerts && libertyItems.length > 0 &&
          libertyItems.map((item) => {
            // Classification-based icon for zoomed out view
            const getClassificationIcon = () => {
              switch (item.classification) {
                case 'ice': return '🧊';
                case 'police': return '🚔';
                case 'couch': return '🛋️';
                case 'camping': return '⛺';
                default: return '🧊'; // Default to ice cube for Liberty alerts
              }
            };

            // Show thumbnail at zoom >= 10, icon at zoom < 10
            const showThumbnail = zoom >= 10 && item.url && item.blob?.type?.startsWith('image/');
            const isVideo = item.blob?.type?.startsWith('video/');

            return (
              <Overlay
                key={`liberty-${item.id}`}
                anchor={[item.latitude || 0, item.longitude || 0]}
              >
                <div
                  onClick={() => {
                    console.log('[Liberty] Marker clicked:', item.id, item.classification);
                    if (onMarkerClick && item.latitude && item.longitude) {
                      onMarkerClick({ latitude: item.latitude, longitude: item.longitude });
                    }
                  }}
                  className="cursor-pointer hover:scale-110 transition-transform"
                  title={`Liberty Alert - ${item.classification || 'Item'}`}
                >
                  {showThumbnail ? (
                    // Zoomed in: Show photo thumbnail with classification badge
                    <div className="relative">
                      <img
                        src={item.url}
                        alt="Liberty Alert"
                        className="w-12 h-12 rounded-lg object-cover border-2 border-red-500 shadow-lg"
                      />
                      <span className="absolute -bottom-1 -right-1 text-lg drop-shadow-lg">
                        {getClassificationIcon()}
                      </span>
                    </div>
                  ) : isVideo && zoom >= 10 ? (
                    // Zoomed in video: Show play icon with classification badge
                    <div className="relative w-12 h-12 rounded-lg bg-gray-800 border-2 border-red-500 shadow-lg flex items-center justify-center">
                      <span className="text-white text-xl">▶️</span>
                      <span className="absolute -bottom-1 -right-1 text-lg drop-shadow-lg">
                        {getClassificationIcon()}
                      </span>
                    </div>
                  ) : (
                    // Zoomed out: Just show classification icon (larger)
                    <span className={isGlobalView ? 'text-4xl' : 'text-3xl'}>
                      {getClassificationIcon()}
                    </span>
                  )}
                </div>
              </Overlay>
            );
          })}

        {/* Liberty Alert region markers - 🗽 (global hot zones only) */}
        {showLibertyAlerts &&
          libertyAlerts
            .filter(alert => alert.type === 'region') // Only show 🗽 regions (🧊 captures now come from libertyItems)
            .map((alert) => {
            const iconSize = isGlobalView ? 'text-5xl' : 'text-3xl';

            return (
              <Overlay
                key={alert.id}
                anchor={[alert.location.latitude, alert.location.longitude]}
              >
                <div
                  onClick={() => {
                    if (isGlobalView) {
                      // Click 🗽 in global view → zoom to that region (local view)
                      console.log('[Liberty] Region clicked, zooming to:', alert.location);
                      setSelectedRegion(alert.location); // Set center to clicked region
                      setIsGlobalLiberty(false);
                      setZoom(12);
                    } else {
                      // Click 🗽 in local view → show alert details popup
                      setSelectedAlert(alert);
                    }
                  }}
                  className="cursor-pointer hover:scale-110 transition-transform"
                  title={alert.message}
                >
                  <span className={iconSize}>🗽</span>
                </div>
              </Overlay>
            );
          })}

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
                <span className="text-2xl">{selectedAlert.type === 'region' ? '🗽' : '🧊'}</span>
                {selectedAlert.type === 'region' ? 'ICE Activity Region' : 'ICE Event Captured'}
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

      {/* Map Filter Modal */}
      <MapFilterModal
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        onApply={(filters) => setActiveFilters(filters)}
      />
    </div>
  );
};
