import React from 'react';
import { CapturedItem } from '../types';
import { PhotoGrid } from './PhotoGrid';

interface FullscreenGalleryProps {
  items: CapturedItem[];
  onClose: () => void;
  onDelete: (item: CapturedItem) => void;
}

export const FullscreenGallery: React.FC<FullscreenGalleryProps> = ({ items, onClose, onDelete }) => {
  return (
    <div
      className="fixed inset-0 bg-gray-900 z-40 flex flex-col"
    >
        <header className="flex-shrink-0 flex items-center justify-between p-4 border-b border-white/10">
            <h2 className="text-xl font-bold text-white">Gallery</h2>
            <button onClick={onClose} className="bg-white/10 rounded-full p-2 text-white" aria-label="Close Gallery">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </header>
        <div className="flex-grow overflow-y-auto">
            <PhotoGrid items={items} onDelete={onDelete} onClick={() => {}} />
        </div>
    </div>
  );
};