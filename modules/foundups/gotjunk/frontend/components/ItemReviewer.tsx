
import React, { useState, useEffect, useRef } from 'react';
import { motion, PanInfo } from 'framer-motion';
import { CapturedItem } from '../types';

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

  const handleDragEnd = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const swipeThreshold = 50;
    const velocityThreshold = 200;

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
      className="w-full h-full absolute inset-0 flex items-center justify-center p-4 pb-28"
      drag="x"
      dragConstraints={{ left: -150, right: 150 }}
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
      <div className="w-full h-full max-w-sm max-h-[75vh] relative">
        {isVideo ? (
          <video
            src={item.url}
            className="w-full h-full object-contain rounded-lg shadow-2xl pointer-events-none"
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
            className="w-full h-full object-contain rounded-lg shadow-2xl pointer-events-none"
            draggable="false"
          />
        )}
      </div>
    </motion.div>
  );
};
