/**
 * InstructionsModal - Dismissible welcome modal with swipe instructions
 * Shows on every page load, uses actual swipe button components
 * Positioned above camera orb for compact layout
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { Z_LAYERS } from '../constants/zLayers';

interface InstructionsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InstructionsModal: React.FC<InstructionsModalProps> = ({ isOpen, onClose }) => {
  const topOffset = 'calc(env(safe-area-inset-top, 20px) + 16px)';
  const maxHeightDvh = 'min(420px, calc(100dvh - env(safe-area-inset-top, 20px) - 220px))';
  const maxHeightFallback = 'min(420px, calc(100vh - env(safe-area-inset-top, 20px) - 220px))';

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed w-[min(92vw,360px)] px-1"
          style={{
            left: '50%',
            transform: 'translateX(calc(-50% - 50px))',
            top: topOffset,
            zIndex: Z_LAYERS.tutorialPopup,
            maxHeight: maxHeightDvh,
            overflowY: 'auto'
          }}
          role="dialog"
          aria-modal="true"
          onClick={onClose}
        >
          <div
            className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl shadow-2xl p-5 border border-gray-700 backdrop-blur-md ring-1 ring-white/10"
            style={{ maxHeight: maxHeightFallback }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <h2 className="text-2xl font-bold text-white mb-1 text-center">
              GotJunk?!
            </h2>

            <p className="text-base text-gray-300 font-semibold mb-3 text-center">
              Browse items near you
            </p>

            {/* Instructions */}
            <div className="grid grid-cols-2 gap-4 mb-3">
              <div className="flex flex-col items-center gap-1.5">
                <div className="p-2.5 rounded-full bg-red-600/50 border border-red-500 pointer-events-none">
                  <LeftArrowIcon className="w-6 h-6 text-white" />
                </div>
                <div className="text-center leading-tight">
                  <p className="text-red-400 font-semibold text-sm">Swipe Left</p>
                  <p className="text-gray-400 text-xs">Skip</p>
                </div>
              </div>

              <div className="flex flex-col items-center gap-1.5">
                <div className="p-2.5 rounded-full bg-green-500/50 border border-green-500 pointer-events-none">
                  <RightArrowIcon className="w-6 h-6 text-white" />
                </div>
                <div className="text-center leading-tight">
                  <p className="text-green-400 font-semibold text-sm">Swipe Right</p>
                  <p className="text-gray-400 text-xs">Add to Cart</p>
                </div>
              </div>
            </div>

            <p className="text-xs text-gray-400 text-center mb-3">
              50km radius • Tinder for stuff
            </p>

            <button
              onClick={onClose}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2.5 rounded-2xl transition-all shadow-lg"
            >
              Got it! Start Swiping
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
