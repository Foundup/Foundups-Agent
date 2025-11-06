import React from 'react';
import { motion } from 'framer-motion';
import { CapturedItem } from '../types';
import { TrashIcon } from './icons/TrashIcon';
import { PlayIcon } from './icons/PlayIcon';
import { ClassificationBadge } from './ClassificationBadge';

interface PhotoCardProps {
  item: CapturedItem;
  onClick: (item: CapturedItem) => void;
  onDelete: (item: CapturedItem) => void;
}

export const PhotoCard: React.FC<PhotoCardProps> = ({ item, onClick, onDelete }) => {
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering onClick for the card itself
    onDelete(item);
  };
  
  const isVideo = item.blob.type.startsWith('video/');

  return (
    <div className="relative group aspect-square w-full rounded-lg overflow-hidden bg-gray-800 shadow-md cursor-pointer" onClick={() => onClick(item)}>
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
        <ClassificationBadge classification={item.classification} price={item.price} />
      )}
            <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity" />
       {isVideo && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <PlayIcon className="w-10 h-10 text-white/80 drop-shadow-lg" />
        </div>
      )}
      <button
        onClick={handleDeleteClick}
        className="absolute top-1 right-1 z-10 w-7 h-7 bg-red-600 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 scale-50 group-hover:scale-100 transition-all duration-200 hover:bg-red-500"
        aria-label="Delete item"
      >
        <TrashIcon className="w-4 h-4" />
      </button>
    </div>
  );
};