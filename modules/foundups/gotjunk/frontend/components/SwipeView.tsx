import React from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { CapturedItem } from '../types';
import { TrashIcon } from './icons/TrashIcon';

interface SwipeViewProps {
  items: CapturedItem[];
  onSwipe: (item: CapturedItem, direction: 'left' | 'right') => void;
}

const SwipeCard: React.FC<{ item: CapturedItem, onSwipe: (direction: 'left' | 'right') => void }> = ({ item, onSwipe }) => {
  const handleDragEnd = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (info.offset.x > 100) {
      onSwipe('right'); // Keep
    } else if (info.offset.x < -100) {
      onSwipe('left'); // Discard
    }
  };

  return (
    <motion.div
      className="absolute h-full w-full"
      drag="x"
      dragConstraints={{ left: -150, right: 150 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      initial={{ scale: 0.9, y: 20, opacity: 0 }}
      animate={{ scale: 1, y: 0, opacity: 1 }}
      exit={{ x: 300, opacity: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      whileTap={{ cursor: 'grabbing' }}
    >
      <div className="relative w-full h-full rounded-2xl overflow-hidden shadow-2xl bg-gray-800 cursor-grab">
          <img src={item.url} className="w-full h-full object-contain pointer-events-none" alt="Captured item to swipe"/>
          <div className="absolute bottom-4 left-0 right-0 flex justify-center">
              <motion.button
                  onClick={() => onSwipe('left')}
                  className="w-16 h-16 bg-red-500/70 backdrop-blur-sm rounded-full flex items-center justify-center text-white transition-all hover:bg-red-500"
                  aria-label="Discard item"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
              >
                  <TrashIcon className="w-8 h-8" />
              </motion.button>
          </div>
      </div>
    </motion.div>
  );
};

export const SwipeView: React.FC<SwipeViewProps> = ({ items, onSwipe }) => {
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <h2 className="text-2xl font-bold text-white mb-2">All Sorted!</h2>
        <p className="text-gray-400">You've gone through all your new captures. Use the camera to add more.</p>
      </div>
    );
  }

  const currentItem = items[0];

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-4">
        <div className="relative w-full max-w-sm aspect-[3/4]">
            <AnimatePresence>
            {currentItem && (
                <SwipeCard 
                key={currentItem.id}
                item={currentItem} 
                onSwipe={(direction) => onSwipe(currentItem, direction)} 
                />
            )}
            </AnimatePresence>
        </div>
        <div className="mt-8 text-center text-gray-400">
            <p>Swipe Right to Keep, Left to Discard</p>
        </div>
    </div>
  );
};
