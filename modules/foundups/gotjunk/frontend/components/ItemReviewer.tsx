
import React, { useState, useEffect, useRef } from 'react';
import { motion, PanInfo } from 'framer-motion';
import { CapturedItem } from '../types';
import { Z_LAYERS } from '../constants/zLayers';
import { ClassificationBadge } from './ClassificationBadge';
import { MessageBoardIcon } from './icons/MessageBoardIcon';

interface ItemReviewerProps {
  item: CapturedItem;
  onDecision: (item: CapturedItem, decision: 'keep' | 'delete') => void;
  onClose?: () => void; // Optional: close fullscreen without making a decision
  showForwardButton?: boolean; // Optional: show > button for cart purchase
  onMessageBoard?: (item: CapturedItem) => void; // Open message board/chat
}

export const ItemReviewer: React.FC<ItemReviewerProps> = ({
  item,
  onDecision,
  onClose,
  showForwardButton = false,
  onMessageBoard = () => console.log('[ItemReviewer] Message board open'),
}) => {
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

    // Check for vertical swipe DOWN to skip to next item
    if (info.offset.y > swipeThreshold || info.velocity.y > velocityThreshold) {
      console.log('[ItemReviewer] Swipe down detected - skipping to next item');
      setSwipeDecision('delete'); // Skip = delete in browse context
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

  const isVideo = item.blob?.type?.startsWith('video/') ?? false;

  // Check if item has valid URL/blob for rendering
  if (!item.url || !item.blob) {
    console.warn('[ItemReviewer] Item missing URL or blob:', item.id);
    return (
      <motion.div
        className="fixed inset-0 flex items-center justify-center p-4 pb-28 bg-black/80 backdrop-blur-sm"
        style={{ zIndex: Z_LAYERS.fullscreen }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className="text-center">
          <p className="text-white text-xl mb-2">Media unavailable</p>
          <p className="text-gray-400 text-sm">This item cannot be displayed</p>
          {onClose && (
            <button
              onClick={onClose}
              className="mt-4 px-4 py-2 bg-gray-700 text-white rounded-lg"
            >
              Close
            </button>
          )}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="fixed inset-0 flex items-center justify-center p-4 pb-28 bg-black/80 backdrop-blur-sm"
      style={{ zIndex: Z_LAYERS.fullscreen }}
      role="dialog"
      aria-modal="true"
      drag
      dragConstraints={{ left: -150, right: 150, top: -200, bottom: 150 }}
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

        {/* Classification Badge - Top left corner (same as PhotoCard) */}
        {item.classification && (
          <div className="absolute top-4 left-4 z-10">
            <ClassificationBadge
              classification={item.classification}
              price={item.price}
              discountPercent={item.discountPercent}
              bidDurationHours={item.bidDurationHours}
              onClick={(e) => {
                e.stopPropagation();
                console.log('[ItemReviewer] Classification badge clicked');
              }}
            />
          </div>
        )}
      </div>

      {/* Message Board Icon - Mid-right side (Occam's razor: cart is in left sidebar) */}
      <div className="absolute right-6 top-1/2 -translate-y-1/2 flex flex-col items-end gap-3 z-10">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onMessageBoard(item);
          }}
          className="w-14 h-14 rounded-full bg-white flex items-center justify-center shadow-2xl hover:scale-105 transition-all"
          aria-label="Open message board"
        >
          <MessageBoardIcon className="w-6 h-6 text-gray-900" />
        </button>

        {onClose && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="w-14 h-14 rounded-full bg-white flex items-center justify-center shadow-2xl hover:scale-105 transition-all"
            aria-label="Collapse to thumbnails"
          >
            <span className="text-2xl text-gray-900 leading-none">−</span>
          </button>
        )}
      </div>

      {/* Forward button (>) - Bottom left corner (10% smaller) */}
      {showForwardButton && (
        <button
          onClick={(e) => {
            e.stopPropagation(); // Prevent double-tap detection
            onDecision(item, 'keep'); // Trigger purchase
          }}
          className="absolute bottom-8 left-8 w-12 h-12 bg-green-600/90 hover:bg-green-500/90 active:scale-95 rounded-full flex items-center justify-center shadow-2xl border-2 border-green-400 transition-all z-10"
          aria-label="Purchase Item"
        >
          <svg
            className="w-7 h-7 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={3}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      )}
    </motion.div>
  );
};
