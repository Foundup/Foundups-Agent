import React, { useEffect, useRef, useState } from 'react';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

interface LibertyAlert {
  id: string;
  location: { latitude: number; longitude: number };
  message: string;
  video_url?: string;
  timestamp: number;
}

interface RegionalCluster {
  location: { latitude: number; longitude: number };
  count: number;
  alerts: LibertyAlert[];
}

interface GlobeViewProps {
  alerts: LibertyAlert[];
  onClose: () => void;
  onAlertClick?: (alert: LibertyAlert) => void;
}

// Cluster alerts by region (group alerts within 100km radius)
function clusterAlerts(alerts: LibertyAlert[]): RegionalCluster[] {
  const clusters: RegionalCluster[] = [];
  const processed = new Set<string>();

  alerts.forEach((alert) => {
    if (processed.has(alert.id)) return;

    const nearby = alerts.filter((other) => {
      if (processed.has(other.id)) return false;
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

// Haversine distance formula
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

export const GlobeView: React.FC<GlobeViewProps> = ({ alerts, onClose, onAlertClick }) => {
  const cesiumContainerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Cesium.Viewer | null>(null);
  const [zoomedCluster, setZoomedCluster] = useState<RegionalCluster | null>(null);

  useEffect(() => {
    if (!cesiumContainerRef.current) return;

    // Initialize Cesium Viewer
    const viewer = new Cesium.Viewer(cesiumContainerRef.current, {
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

    viewerRef.current = viewer;

    // Cluster alerts by region
    const clusters = clusterAlerts(alerts);

    if (!zoomedCluster) {
      // GLOBE VIEW: Show 🗽 Statue of Liberty icons for each cluster
      clusters.forEach((cluster) => {
        const entity = viewer.entities.add({
          position: Cesium.Cartesian3.fromDegrees(
            cluster.location.longitude,
            cluster.location.latitude,
            0
          ),
          billboard: {
            image: createLibertyStatueSVG(cluster.count),
            width: 48,
            height: 48,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
          },
          label: {
            text: `${cluster.count} alert${cluster.count > 1 ? 's' : ''}`,
            font: '14px sans-serif',
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            verticalOrigin: Cesium.VerticalOrigin.TOP,
            pixelOffset: new Cesium.Cartesian2(0, 10),
          },
          properties: { cluster },
        });

        // Handle click on 🗽 → Zoom to show 🧊 ice cubes
        viewer.selectedEntityChanged.addEventListener(() => {
          if (viewer.selectedEntity === entity) {
            setZoomedCluster(cluster);
          }
        });
      });

      // Set initial camera position (high altitude to see globe)
      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(0, 20, 20000000),
      });
    } else {
      // ZOOMED VIEW: Show 🧊 ice cubes for alerts in selected cluster
      zoomedCluster.alerts.forEach((alert) => {
        const entity = viewer.entities.add({
          position: Cesium.Cartesian3.fromDegrees(
            alert.location.longitude,
            alert.location.latitude,
            0
          ),
          billboard: {
            image: createIceCubeSVG(),
            width: 32,
            height: 32,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
          },
          description: `
            <div style="padding: 10px;">
              <h3 style="margin: 0 0 10px 0;">🧊 Liberty Alert</h3>
              <p style="margin: 5px 0;">${alert.message}</p>
              <p style="font-size: 12px; color: #666; margin: 5px 0;">
                ${new Date(alert.timestamp).toLocaleString()}
              </p>
              ${alert.video_url ? `<a href="${alert.video_url}" target="_blank" style="color: #3b82f6;">▶️ Watch Video</a>` : ''}
            </div>
          `,
          properties: { alert },
        });

        // Handle click on 🧊 → Trigger video playback
        if (onAlertClick) {
          viewer.selectedEntityChanged.addEventListener(() => {
            if (viewer.selectedEntity === entity) {
              onAlertClick(alert);
            }
          });
        }
      });

      // Zoom camera to cluster location
      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(
          zoomedCluster.location.longitude,
          zoomedCluster.location.latitude,
          50000 // 50km altitude
        ),
        duration: 2,
      });
    }

    // Cleanup
    return () => {
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, [alerts, onAlertClick, zoomedCluster]);

  // Create SVG for 🗽 Statue of Liberty
  const createLibertyStatueSVG = (count: number) => {
    const svg = `
      <svg width="48" height="48" xmlns="http://www.w3.org/2000/svg">
        <circle cx="24" cy="24" r="22" fill="#fbbf24" stroke="#ffffff" stroke-width="2"/>
        <text x="50%" y="50%" font-size="32" text-anchor="middle" dominant-baseline="central">🗽</text>
      </svg>
    `;
    return 'data:image/svg+xml;base64,' + btoa(svg);
  };

  // Create SVG for 🧊 ice cube
  const createIceCubeSVG = () => {
    const svg = `
      <svg width="32" height="32" xmlns="http://www.w3.org/2000/svg">
        <text x="50%" y="50%" font-size="28" text-anchor="middle" dominant-baseline="central">🧊</text>
      </svg>
    `;
    return 'data:image/svg+xml;base64,' + btoa(svg);
  };

  return (
    <div className="fixed inset-0 bg-black z-30 flex flex-col" style={{ paddingBottom: '7rem' }}>
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between p-4 border-b border-white/10 bg-gray-900">
        <div className="flex items-center gap-2">
          {zoomedCluster ? (
            <button
              onClick={() => setZoomedCluster(null)}
              className="flex items-center gap-2 bg-white/10 rounded-full px-4 py-2 text-white hover:bg-white/20 transition-colors"
            >
              <span className="text-xl">🌍</span>
              <span className="text-sm font-medium">Back to Globe</span>
            </button>
          ) : (
            <>
              <span className="text-2xl">🌍</span>
              <h2 className="text-xl font-bold text-white">Global Liberty Alerts</h2>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          {zoomedCluster && (
            <div className="text-sm text-white bg-white/10 px-3 py-1 rounded-full">
              {zoomedCluster.count} alert{zoomedCluster.count > 1 ? 's' : ''} in this region
            </div>
          )}
          <button
            onClick={onClose}
            className="bg-white/10 rounded-full p-2 text-white hover:bg-white/20 transition-colors"
            aria-label="Close Globe View"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </header>

      {/* Cesium Globe Container */}
      <div ref={cesiumContainerRef} className="flex-grow relative" />

      {/* Instructions */}
      <div className="absolute bottom-24 left-4 bg-black/80 backdrop-blur-sm p-3 rounded-lg shadow-lg z-10 text-white text-sm max-w-xs">
        <div className="font-bold mb-1">
          {zoomedCluster ? '🧊 Ice Cube View' : '🌍 Globe View'}
        </div>
        <div className="text-xs space-y-1">
          {!zoomedCluster ? (
            <>
              <div>🖱️ <strong>Drag:</strong> Rotate globe</div>
              <div>🖱️ <strong>Scroll:</strong> Zoom in/out</div>
              <div>👆 <strong>Touch:</strong> Pinch to zoom</div>
              <div>🗽 <strong>Click statue:</strong> Zoom to region</div>
            </>
          ) : (
            <>
              <div>🧊 <strong>Click ice cube:</strong> Watch video</div>
              <div>🖱️ <strong>Drag:</strong> Pan around</div>
              <div>🖱️ <strong>Scroll:</strong> Zoom closer</div>
              <div>🌍 <strong>Top-left button:</strong> Back to globe</div>
            </>
          )}
        </div>
      </div>

      {/* Cluster Count Badge (Globe View) */}
      {!zoomedCluster && (
        <div className="absolute top-4 right-4 bg-amber-500 text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 z-10">
          <span className="text-xl">🗽</span>
          <span className="font-bold">{clusterAlerts(alerts).length}</span>
          <span className="text-sm">region{clusterAlerts(alerts).length > 1 ? 's' : ''}</span>
        </div>
      )}
    </div>
  );
};
