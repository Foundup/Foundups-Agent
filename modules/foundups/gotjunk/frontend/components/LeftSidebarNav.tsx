/**
 * LeftSidebarNav - Floating navigation buttons on left side
 * Extracted from BottomNavBar right section for cleaner layout
 */

import React from 'react';
import { motion } from 'framer-motion';
import { GridIcon } from './icons/GridIcon';
import { MapIcon } from './icons/MapIcon';
import { HomeIcon } from './icons/HomeIcon';
import { CartIcon } from './icons/CartIcon';
import { Z_LAYERS } from '../constants/zLayers';

interface LeftSidebarNavProps {
  activeTab: 'browse' | 'map' | 'myitems' | 'cart';
  onGalleryClick: () => void;
  onGalleryIconTap?: (duration: number) => void;
  onMapClick: () => void;
  onMyItemsClick: () => void;
  onCartClick: () => void;
  libertyEnabled: boolean;
}

export const LeftSidebarNav: React.FC<LeftSidebarNavProps> = ({
  activeTab,
  onGalleryClick,
  onGalleryIconTap,
  onMapClick,
  onMyItemsClick,
  onCartClick,
  libertyEnabled,
}) => {
  // SOS Morse Code Detection on Gallery icon (same as BottomNavBar)
  const galleryTapStartTime = React.useRef<number>(0);

  const handleGalleryMouseDown = (e: React.MouseEvent | React.TouchEvent) => {
    galleryTapStartTime.current = Date.now();
  };

  const handleGalleryMouseUp = (e: React.MouseEvent | React.TouchEvent) => {
    const tapDuration = Date.now() - galleryTapStartTime.current;

    // Always send tap duration for SOS detection
    if (onGalleryIconTap && tapDuration > 0) {
      onGalleryIconTap(tapDuration);
    }

    // onGalleryClick will handle whether to open gallery based on SOS detection state
    // This is controlled in App.tsx with sosDetectionActive ref
    onGalleryClick();
  };

  // Adaptive icon styling for map view visibility
  // Map tiles vary (white streets, dark parks, blue water) - inactive icons need high contrast
  const isMapView = activeTab === 'map';
  const getButtonStyle = (isActive: boolean) => {
    if (isActive) {
      // Active state: bright blue with ring (always visible)
      return 'bg-blue-500/70 ring-2 ring-blue-400 shadow-blue-500/50 border-2 border-blue-300';
    }
    // Inactive state: black background for map view, dark gray for other views
    return isMapView
      ? 'bg-black/90 hover:bg-gray-900/90 border-2 border-white shadow-2xl shadow-black/80'
      : 'bg-gray-800/90 hover:bg-gray-700/90 border-2 border-gray-600 shadow-2xl';
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      className="fixed left-4 sm:left-6 flex flex-col items-center pointer-events-auto"
      style={{
        top: 'var(--sb-top)',
        gap: 'var(--sb-gap)',
        zIndex: Z_LAYERS.sidebar,
      }}
    >
      {/* Liberty Alert - Top of sidebar */}
      {libertyEnabled && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="text-3xl filter drop-shadow-lg"
        >
          🗽
        </motion.div>
      )}

      {/* Tab 1: Browse - Grid Icon */}
      <motion.button
        onMouseDown={handleGalleryMouseDown}
        onMouseUp={handleGalleryMouseUp}
        onTouchStart={handleGalleryMouseDown}
        onTouchEnd={handleGalleryMouseUp}
        aria-label="Browse (Tab 1)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`grid place-items-center rounded-2xl backdrop-blur-md shadow-xl transition-all ${getButtonStyle(activeTab === 'browse')}`}
        style={{
          width: 'var(--sb-size)',
          height: 'var(--sb-size)',
        }}
      >
        <GridIcon style={{ width: 'clamp(20px, 3.5vh, 32px)', height: 'clamp(20px, 3.5vh, 32px)' }} className="text-white" />
      </motion.button>

      {/* Tab 2: Map - Map Icon */}
      <motion.button
        onClick={onMapClick}
        aria-label="Map (Tab 2)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`grid place-items-center rounded-2xl backdrop-blur-md shadow-xl transition-all ${getButtonStyle(activeTab === 'map')}`}
        style={{
          width: 'var(--sb-size)',
          height: 'var(--sb-size)',
        }}
      >
        <MapIcon style={{ width: 'clamp(20px, 3.5vh, 32px)', height: 'clamp(20px, 3.5vh, 32px)' }} className="text-white" />
      </motion.button>

      {/* Tab 3: My Items - Home Icon */}
      <motion.button
        onClick={onMyItemsClick}
        aria-label="My Items (Tab 3)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`grid place-items-center rounded-2xl backdrop-blur-md shadow-xl transition-all ${getButtonStyle(activeTab === 'myitems')}`}
        style={{
          width: 'var(--sb-size)',
          height: 'var(--sb-size)',
        }}
      >
        <HomeIcon style={{ width: 'clamp(20px, 3.5vh, 32px)', height: 'clamp(20px, 3.5vh, 32px)' }} className="text-white" />
      </motion.button>

      {/* Tab 4: Cart - Cart Icon */}
      <motion.button
        onClick={onCartClick}
        aria-label="Cart (Tab 4)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`grid place-items-center rounded-2xl backdrop-blur-md shadow-xl transition-all ${getButtonStyle(activeTab === 'cart')}`}
        style={{
          width: 'var(--sb-size)',
          height: 'var(--sb-size)',
        }}
      >
        <CartIcon style={{ width: 'clamp(20px, 3.5vh, 32px)', height: 'clamp(20px, 3.5vh, 32px)' }} className="text-white" />
      </motion.button>
    </motion.div>
  );
};
