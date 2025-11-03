import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { PhotoCard } from './PhotoCard';
import { CapturedItem } from '../types';

interface PhotoGridProps {
  items: CapturedItem[];
  onClick: (item: CapturedItem) => void; // Renamed from onView
  onDelete: (item: CapturedItem) => void;
}

export const PhotoGrid: React.FC<PhotoGridProps> = ({ items, onClick, onDelete }) => {
  if (items.length === 0) {
      return (
          <div className="text-center py-20 px-4">
              <p className="text-gray-400">Your gallery is empty.</p>
              <p className="text-gray-500 text-sm mt-1">Close this view and use the camera to capture items.</p>
          </div>
      )
  }

  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-1 p-1">
      <AnimatePresence>
        {items.map((item, index) => (
          <motion.div
            key={item.id}
            layout
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0, transition: { duration: 0.2 } }}
            transition={{
              type: 'spring',
              damping: 20,
              stiffness: 200,
              delay: index * 0.02,
            }}
          >
            <PhotoCard
              item={item}
              onClick={onClick}
              onDelete={onDelete}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
