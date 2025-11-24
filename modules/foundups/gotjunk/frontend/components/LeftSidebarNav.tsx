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
  activeTab: 'browse' | 'myitems' | 'cart';
  onGalleryClick: () => void;
  onGalleryIconTap?: (duration: number) => void;
  onMapClick: () => void;
  onMyItemsClick: () => void;
  onCartClick: () => void;
}

export const LeftSidebarNav: React.FC<LeftSidebarNavProps> = ({
  activeTab,
  onGalleryClick,
  onGalleryIconTap,
  onMapClick,
  onMyItemsClick,
  onCartClick,
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

  const getButtonStyle = (isActive: boolean) => {
    if (isActive) {
      // Active state: bright blue with ring (always visible)
      return 'bg-blue-500/70 ring-2 ring-blue-400 shadow-blue-500/50 border-2 border-blue-300';
    }
    // Inactive state: dark gray background
    return 'bg-gray-800/90 hover:bg-gray-700/90 border-2 border-gray-600 shadow-2xl';
  };

  // Responsive sizing - scales with viewport height
  const gapValue = 'clamp(8px, 2vh, 18px)';      // Reduced gap for small screens
  const iconSize = 'clamp(44px, 5.5vh, 58px)';   // Slightly smaller min for tight viewports
  const innerIconSize = 'clamp(18px, 2.2vh, 22px)'; // Scale inner icons with viewport

  return (
    <motion.div
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      className="fixed left-4 sm:left-6 flex flex-col items-center pointer-events-auto"
      style={{
        // Center in USABLE area (above 96px bottom nav), not full viewport
        // Formula: (viewport - navHeight) / 2 = center point of usable area
        top: 'calc((100% - 96px) / 2)',
        transform: 'translateY(-50%)',
        gap: gapValue,
        zIndex: Z_LAYERS.sidebar,
        // Prevent overflow on very short viewports (landscape, keyboard)
        maxHeight: 'calc(100vh - 120px)', // Leave room for nav + padding
        overflow: 'hidden',
      }}
    >
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
          width: iconSize,
          height: iconSize,
        }}
      >
        <GridIcon style={{ width: innerIconSize, height: innerIconSize }} className="text-white" />
      </motion.button>

      {/* Tab 2: Map - Map Icon */}
      <motion.button
        onClick={onMapClick}
        aria-label="Map (Tab 2)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`grid place-items-center rounded-2xl backdrop-blur-md shadow-xl transition-all ${getButtonStyle(activeTab === 'map')}`}
        style={{
          width: iconSize,
          height: iconSize,
        }}
      >
        <MapIcon style={{ width: innerIconSize, height: innerIconSize }} className="text-white" />
      </motion.button>

      {/* Tab 3: My Items - Home Icon */}
      <motion.button
        onClick={onMyItemsClick}
        aria-label="My Items (Tab 3)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`grid place-items-center rounded-2xl backdrop-blur-md shadow-xl transition-all ${getButtonStyle(activeTab === 'myitems')}`}
        style={{
          width: iconSize,
          height: iconSize,
        }}
      >
        <HomeIcon style={{ width: innerIconSize, height: innerIconSize }} className="text-white" />
      </motion.button>

      {/* Tab 4: Cart - Cart Icon */}
      <motion.button
        onClick={onCartClick}
        aria-label="Cart (Tab 4)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`grid place-items-center rounded-2xl backdrop-blur-md shadow-xl transition-all ${getButtonStyle(activeTab === 'cart')}`}
        style={{
          width: iconSize,
          height: iconSize,
        }}
      >
        <CartIcon style={{ width: innerIconSize, height: innerIconSize }} className="text-white" />
      </motion.button>

      {/* Version indicator - subtle at bottom */}
      <div className="mt-2 text-[8px] text-white/30 font-mono select-none">
        {typeof __COMMIT_HASH__ !== 'undefined' ? __COMMIT_HASH__ : 'dev'}
      </div>
    </motion.div>
  );
};
