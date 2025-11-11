
import React, { useState, useEffect, useRef } from 'react';
import { motion, PanInfo } from 'framer-motion';
import { CapturedItem } from '../types';
import { Z_LAYERS } from '../constants/zLayers';

interface ItemReviewerProps {
  item: CapturedItem;
  onDecision: (item: CapturedItem, decision: 'keep' | 'delete') => void;
  onClose?: () => void; // Optional: close fullscreen without making a decision
}

export const ItemReviewer: React.FC<ItemReviewerProps> = ({ item, onDecision, onClose }) => {
  const [swipeDecision, setSwipeDecision] = useState<'keep' | 'delete' | null>(null);
  const lastTapRef = useRef<number>(0);

  useEffect(() => {
    if (swipeDecision) {
      onDecision(item, swipeDecision);
    }
  }, [swipeDecision, item, onDecision]);

  useEffect(() => {
    if (typeof document === 'undefined') return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, []);

  const handleDragEnd = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const swipeThreshold = 50;
    const velocityThreshold = 200;

    // Check for vertical swipe UP to close (collapse back to thumbnails)
    if (onClose && (info.offset.y < -swipeThreshold || info.velocity.y < -velocityThreshold)) {
      console.log('[ItemReviewer] Swipe up detected - closing fullscreen');
      onClose();
      return;
    }

    // Horizontal swipe for keep/delete
    let decision: 'keep' | 'delete' | null = null;

    if (info.offset.x > swipeThreshold || info.velocity.x > velocityThreshold) {
      decision = 'keep';
    } else if (info.offset.x < -swipeThreshold || info.velocity.x < -velocityThreshold) {
      decision = 'delete';
    }

    if (decision) {
      setSwipeDecision(decision);
    }
  };

  // Double-tap to exit fullscreen (same 300ms window as PhotoCard)
  const handleTap = () => {
    if (!onClose) return; // Exit early if no onClose handler provided

    const now = Date.now();
    const DOUBLE_TAP_DELAY = 300; // ms

    if (now - lastTapRef.current < DOUBLE_TAP_DELAY) {
      // Double tap detected - close fullscreen
      onClose();
    }
    lastTapRef.current = now;
  };

  const isVideo = item.blob.type.startsWith('video/');

  return (
    <motion.div
      className="fixed inset-0 flex items-center justify-center p-4 pb-28 bg-black/80 backdrop-blur-sm"
      style={{ zIndex: Z_LAYERS.fullscreen }}
      role="dialog"
      aria-modal="true"
      drag
      dragConstraints={{ left: -150, right: 150, top: -200, bottom: 50 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      onClick={handleTap}
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      // FIX: The exit animation now correctly uses state to determine the direction.
      // The previous implementation used a function for `x` which is not a valid type, causing an error.
      exit={{ opacity: 0, scale: 0.9, x: swipeDecision === 'keep' ? 300 : -300 }}
      transition={{ type: 'spring', stiffness: 400, damping: 40 }}
    >
      <div className="fixed inset-0 bottom-32">
        {isVideo ? (
          <video
            src={item.url}
            className="w-full h-full object-cover pointer-events-none"
            autoPlay
            loop
            muted
            playsInline
            draggable="false"
          />
        ) : (
          <img
            src={item.url}
            alt="Captured item for review"
            className="w-full h-full object-cover pointer-events-none"
            draggable="false"
          />
        )}
      </div>

      {/* Collapse button (-) - Bottom right corner */}
      {onClose && (
        <button
          onClick={(e) => {
            e.stopPropagation(); // Prevent double-tap detection
            onClose();
          }}
          className="absolute bottom-8 right-8 w-14 h-14 bg-gray-800/90 hover:bg-gray-700/90 active:scale-95 rounded-full flex items-center justify-center shadow-2xl border-2 border-gray-600 transition-all z-10"
          aria-label="Collapse to thumbnails"
        >
          <svg
            className="w-8 h-8 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={3}
              d="M20 12H4"
            />
          </svg>
        </button>
      )}
    </motion.div>
  );
};
