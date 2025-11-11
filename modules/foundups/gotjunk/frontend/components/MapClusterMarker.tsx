/**
 * Map Cluster Marker - Dynamic Zoom-Based Rendering
 *
 * - Zoomed out (< 14): Small number badge (compact)
 * - Zoomed in (>= 14): Thumbnail grid with images (detailed)
 * - Smooth transitions between view modes (no pop)
 *
 * Clicking the marker navigates to browse tab filtered to this location.
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface ItemLocation {
  latitude: number;
  longitude: number;
}

export interface ClusteredItem {
  id: string;
  url: string;  // Blob URL for thumbnail
  classification: 'free' | 'discount' | 'bid';
  latitude: number;
  longitude: number;
}

export interface ItemCluster {
  location: ItemLocation;  // Center point of cluster
  items: ClusteredItem[];
  count: number;
}

interface MapClusterMarkerProps {
  cluster: ItemCluster;
  zoom?: number;  // Zoom level for dynamic rendering (default: 14)
  onClick: (location: ItemLocation) => void;
}

const ZOOM_THRESHOLD = 14; // Switch from compact to detailed view

export const MapClusterMarker: React.FC<MapClusterMarkerProps> = ({ cluster, zoom = 14, onClick }) => {
  const { location, items, count } = cluster;
  const isZoomedOut = zoom < ZOOM_THRESHOLD;

  // Show up to 4 thumbnails (detailed view only)
  const displayItems = items.slice(0, 4);
  const hasMore = count > 4;

  // Grid size based on count (detailed view)
  const gridSize = count === 1 ? '64px' : '80px';

  // Smooth transition animations
  const transitionConfig = {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.8, opacity: 0 },
    transition: { duration: 0.2, ease: 'easeOut' }
  };

  // COMPACT VIEW: Zoomed out - show small number badge
  if (isZoomedOut) {
    return (
      <AnimatePresence mode="wait">
        <motion.div
          key="compact"
          className="cursor-pointer transform -translate-x-1/2 -translate-y-1/2"
          onClick={(e) => {
            e.stopPropagation();
            onClick(location);
          }}
          style={{ position: 'relative' }}
          {...transitionConfig}
        >
          <div
            className="bg-blue-600 text-white text-sm font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-lg border-2 border-white hover:bg-blue-500 transition-all hover:scale-110"
          >
            {count}
          </div>
        </motion.div>
      </AnimatePresence>
    );
  }

  // DETAILED VIEW: Zoomed in - show thumbnail grid
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="detailed"
        className="map-cluster-marker cursor-pointer transform -translate-x-1/2 -translate-y-1/2"
        onClick={(e) => {
          e.stopPropagation();
          onClick(location);
        }}
        style={{
          position: 'relative',
          width: gridSize,
          height: gridSize,
        }}
        {...transitionConfig}
      >
      {/* Thumbnail Grid */}
      <div
        className="grid gap-0.5 bg-white rounded-lg shadow-2xl overflow-hidden border-2 border-gray-800"
        style={{
          gridTemplateColumns: count === 1 ? '1fr' : '1fr 1fr',
          gridTemplateRows: count === 1 ? '1fr' : '1fr 1fr',
          width: gridSize,
          height: gridSize,
        }}
      >
        {displayItems.map((item, index) => (
          <div
            key={item.id}
            className="relative"
            style={{
              width: count === 1 ? '64px' : '39px',
              height: count === 1 ? '64px' : '39px',
            }}
          >
            <img
              src={item.url}
              alt={`Item ${index + 1}`}
              className="w-full h-full object-cover"
            />
            {/* Classification indicator (corner dot) */}
            <div
              className="absolute top-0.5 right-0.5 w-2 h-2 rounded-full"
              style={{
                backgroundColor:
                  item.classification === 'free'
                    ? '#22c55e' // Green
                    : item.classification === 'discount'
                    ? '#f59e0b' // Amber
                    : '#8b5cf6', // Purple (bid)
              }}
            />
          </div>
        ))}
      </div>

      {/* Count Badge (if more than 4 items) */}
      {hasMore && (
        <div
          className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-lg border-2 border-white"
          style={{ zIndex: 10 }}
        >
          {count}
        </div>
      )}

      {/* Pulse animation to attract attention */}
      <div
        className="absolute inset-0 rounded-lg animate-pulse"
        style={{
          boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.3)',
          pointerEvents: 'none',
        }}
      />
      </motion.div>
    </AnimatePresence>
  );
};
