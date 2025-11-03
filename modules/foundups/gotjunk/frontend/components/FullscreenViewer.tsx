import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CapturedItem } from '../types';
import { TrashIcon } from './icons/TrashIcon';

interface FullscreenViewerProps {
  items: CapturedItem[];
  startIndex: number;
  onClose: () => void;
  onNavigate: (direction: 'prev' | 'next') => void;
  onDelete: (item: CapturedItem) => void;
}

const ArrowButton: React.FC<{ direction: 'left' | 'right', onClick: () => void }> = ({ direction, onClick }) => (
    <button onClick={onClick} className={`absolute top-1/2 -translate-y-1/2 ${direction === 'left' ? 'left-4' : 'right-4'} z-20 bg-black/30 text-white rounded-full w-16 h-16 flex items-center justify-center backdrop-blur-sm transition-transform active:scale-95`}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-8 h-8">
            {direction === 'left' ? <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /> : <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />}
        </svg>
    </button>
);

export const FullscreenViewer: React.FC<FullscreenViewerProps> = ({ items, startIndex, onClose, onNavigate, onDelete }) => {
  const item = items[startIndex];

  if (!item) return null;

  const handleDragEnd = (event: any, info: any) => {
    if (info.offset.x > 100) {
      onNavigate('prev');
    } else if (info.offset.x < -100) {
      onNavigate('next');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center"
      onDoubleClick={onClose}
    >
        <AnimatePresence initial={false}>
            <motion.img
                key={item.id}
                src={item.url}
                className="max-w-full max-h-full object-contain"
                drag="x"
                dragConstraints={{ left: 0, right: 0 }}
                onDragEnd={handleDragEnd}
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -300, opacity: 0 }}
                transition={{ type: 'tween' }}
            />
        </AnimatePresence>

        {startIndex > 0 && <ArrowButton direction="left" onClick={() => onNavigate('prev')} />}
        {startIndex < items.length - 1 && <ArrowButton direction="right" onClick={() => onNavigate('next')} />}

        <button onClick={onClose} className="absolute top-4 right-4 bg-black/30 text-white rounded-full w-10 h-10 flex items-center justify-center z-20" aria-label="Close">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
        </button>

        <button onClick={() => onDelete(item)} className="absolute bottom-4 right-4 bg-black/30 text-white rounded-full w-12 h-12 flex items-center justify-center z-20 hover:bg-red-500/50 transition-colors" aria-label="Delete item">
            <TrashIcon className="w-6 h-6" />
        </button>
    </motion.div>
  );
};