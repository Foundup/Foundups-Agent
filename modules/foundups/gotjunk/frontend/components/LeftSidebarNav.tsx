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

  return (
    <motion.div
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      className="fixed left-6 z-60 flex flex-col items-center space-y-6"
      style={{ top: 'calc(50% - 150px)', transform: 'translateY(-50%)' }}
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
        className={`p-4 rounded-2xl backdrop-blur-md shadow-xl transition-all ${
          activeTab === 'browse'
            ? 'bg-blue-500/50 ring-2 ring-blue-400 shadow-blue-500/50'
            : 'bg-white/10 hover:bg-white/20'
        }`}
      >
        <GridIcon className="w-8 h-8 text-white" />
      </motion.button>

      {/* Tab 2: Map - Map Icon */}
      <motion.button
        onClick={onMapClick}
        aria-label="Map (Tab 2)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`p-4 rounded-2xl backdrop-blur-md shadow-xl transition-all ${
          activeTab === 'map'
            ? 'bg-blue-500/50 ring-2 ring-blue-400 shadow-blue-500/50'
            : 'bg-white/10 hover:bg-white/20'
        }`}
      >
        <MapIcon className="w-8 h-8 text-white" />
      </motion.button>

      {/* Tab 3: My Items - Home Icon */}
      <motion.button
        onClick={onMyItemsClick}
        aria-label="My Items (Tab 3)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`p-4 rounded-2xl backdrop-blur-md shadow-xl transition-all ${
          activeTab === 'myitems'
            ? 'bg-blue-500/50 ring-2 ring-blue-400 shadow-blue-500/50'
            : 'bg-white/10 hover:bg-white/20'
        }`}
      >
        <HomeIcon className="w-8 h-8 text-white" />
      </motion.button>

      {/* Tab 4: Cart - Cart Icon */}
      <motion.button
        onClick={onCartClick}
        aria-label="Cart (Tab 4)"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={`p-4 rounded-2xl backdrop-blur-md shadow-xl transition-all ${
          activeTab === 'cart'
            ? 'bg-blue-500/50 ring-2 ring-blue-400 shadow-blue-500/50'
            : 'bg-white/10 hover:bg-white/20'
        }`}
      >
        <CartIcon className="w-8 h-8 text-white" />
      </motion.button>
    </motion.div>
  );
};
