import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { PhotoCard } from './PhotoCard';
import { CapturedItem } from '../types';

interface PhotoGridProps {
  items: CapturedItem[];
  onClick: (item: CapturedItem) => void; // Renamed from onView
  onDelete: (item: CapturedItem) => void;
  onBadgeClick?: (item: CapturedItem) => void;
  onBadgeLongPress?: (item: CapturedItem) => void;
  onMessageBoard?: (item: CapturedItem) => void; // Sprint M6: Open message board
  getUnreadCount?: (itemId: string) => number; // Sprint M6: Get unread count for item
}

export const PhotoGrid: React.FC<PhotoGridProps> = ({ 
  items, 
  onClick, 
  onDelete, 
  onBadgeClick, 
  onBadgeLongPress,
  onMessageBoard,
  getUnreadCount,
}) => {
  if (items.length === 0) {
      return (
          <div className="text-center py-20 px-4">
              <p className="text-gray-400">Your gallery is empty.</p>
              <p className="text-gray-500 text-sm mt-1">Close this view and use the camera to capture items.</p>
          </div>
      )
  }

  return (
    <div className="grid grid-cols-4 gap-2 p-2">
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
              onBadgeClick={onBadgeClick}
              onBadgeLongPress={onBadgeLongPress}
              onExpand={onClick}
              onMessageBoard={onMessageBoard}
              unreadMessageCount={getUnreadCount ? getUnreadCount(item.id) : 0}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
