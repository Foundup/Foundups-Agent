import React, { useRef } from 'react';
import { motion, PanInfo } from 'framer-motion';
import { CapturedItem } from '../types';
import { TrashIcon } from './icons/TrashIcon';
import { PlayIcon } from './icons/PlayIcon';
import { ClassificationBadge } from './ClassificationBadge';
import { PlusIcon } from './icons/PlusIcon';

interface PhotoCardProps {
  item: CapturedItem;
  onClick: (item: CapturedItem) => void;
  onDelete: (item: CapturedItem) => void;
  onBadgeClick?: (item: CapturedItem) => void; // Tap badge to re-classify
  onBadgeLongPress?: (item: CapturedItem) => void; // Long-press badge to edit options
  onExpand?: (item: CapturedItem) => void; // Optional: explicit expand button handler
}

export const PhotoCard: React.FC<PhotoCardProps> = ({ item, onClick, onDelete, onBadgeClick, onBadgeLongPress, onExpand }) => {
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering onClick for the card itself
    onDelete(item);
  };
  
  // Double-tap detection for fullscreen
  const lastTapRef = useRef<number>(0);

  const handleCardClick = () => {
    const now = Date.now();
    const DOUBLE_TAP_DELAY = 300; // ms

    if (now - lastTapRef.current < DOUBLE_TAP_DELAY) {
      // Double tap detected - open fullscreen
      onClick(item);
    }
    lastTapRef.current = now;
  };

  const isVideo = item.blob?.type?.startsWith('video/') ?? false;

  // Swipe-down gesture to open fullscreen
  const handleDragEnd = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const swipeThreshold = 80;  // pixels
    const velocityThreshold = 200;  // pixels/second

    // Swipe DOWN = open fullscreen
    if (info.offset.y > swipeThreshold || info.velocity.y > velocityThreshold) {
      console.log('[PhotoCard] Swipe down detected - opening fullscreen');
      onClick(item);
    }
  };

  return (
    <motion.div
      className="relative group aspect-square w-full rounded-lg overflow-hidden bg-gray-800 shadow-md cursor-pointer"
      onClick={handleCardClick}
      drag="y"
      dragConstraints={{ top: 0, bottom: 0 }}
      dragElastic={0.3}
      onDragEnd={handleDragEnd}
      whileDrag={{ scale: 1.02, zIndex: 10 }}
    >
      {isVideo ? (
         <video
            src={item.url}
            className="w-full h-full object-cover pointer-events-none group-hover:scale-105 transition-transform duration-300"
            muted
            playsInline
            preload="metadata"
            draggable="false"
        />
      ) : (
        <img
          src={item.url}
          alt="Captured item thumbnail"
          className="w-full h-full object-cover pointer-events-none group-hover:scale-105 transition-transform duration-300"
          draggable="false"
        />
      )}
      
      {/* Classification badge overlay */}
      {item.classification && (
        <ClassificationBadge 
          classification={item.classification} 
          price={item.price}
          discountPercent={item.discountPercent}
          bidDurationHours={item.bidDurationHours}
          onClick={(e) => {
            e.stopPropagation(); // Don't trigger card double-tap
            if (onBadgeClick) onBadgeClick(item);
          }}
          onLongPress={(e) => {
            e.stopPropagation();
            if (onBadgeLongPress) onBadgeLongPress(item);
          }}
        />
      )}
            <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity" />
       {isVideo && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <PlayIcon className="w-10 h-10 text-white/80 drop-shadow-lg" />
        </div>
      )}
      <button
        onClick={handleDeleteClick}
        className="absolute top-1 right-1 z-10 w-6 h-6 bg-red-600 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 scale-50 group-hover:scale-100 transition-all duration-200 hover:bg-red-500"
        aria-label="Delete item"
      >
        <TrashIcon className="w-3.5 h-3.5" />
      </button>

      {/* Manual expand button - bottom LEFT corner (10% smaller) */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          if (onExpand) {
            onExpand(item);
          } else {
            onClick(item);
          }
        }}
        className="absolute bottom-2 left-2 z-10 w-9 h-9 bg-white text-gray-800 rounded-full flex items-center justify-center shadow-lg opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-200"
        aria-label="Expand item"
      >
        <PlusIcon className="w-4 h-4" />
      </button>
    </motion.div>
  );
};