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
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed w-[min(92vw,360px)]"
          style={{
            left: 'calc(50% - 50px)',
            transform: 'translateX(-50%)',
            top: 'calc(env(safe-area-inset-top, 20px) + 16px)',
            zIndex: Z_LAYERS.tutorialPopup
          }}
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl shadow-2xl p-6 border-2 border-gray-700 backdrop-blur-md ring-1 ring-white/10">
            {/* Header */}
            <h2 className="text-3xl font-bold text-white mb-2 text-center">
              GotJunk?!
            </h2>

            <p className="text-lg text-gray-300 font-semibold mb-4 text-center">
              Browse items near you
            </p>

            {/* Instructions */}
            <div className="flex items-center justify-center gap-8 mb-4">
              <div className="flex flex-col items-center gap-2">
                <div className="p-3 rounded-full bg-red-600/50 border-2 border-red-500 pointer-events-none scale-90">
                  <LeftArrowIcon className="w-6 h-6 text-white" />
                </div>
                <div className="text-center">
                  <p className="text-red-400 font-bold text-sm">Swipe Left</p>
                  <p className="text-gray-400 text-xs">Skip</p>
                </div>
              </div>

              <div className="flex flex-col items-center gap-2">
                <div className="p-3 rounded-full bg-green-500/50 border-2 border-green-500 pointer-events-none scale-90">
                  <RightArrowIcon className="w-6 h-6 text-white" />
                </div>
                <div className="text-center">
                  <p className="text-green-400 font-bold text-sm">Swipe Right</p>
                  <p className="text-gray-400 text-xs">Add to Cart</p>
                </div>
              </div>
            </div>

            <p className="text-xs text-gray-400 text-center mb-4">
              50km radius • Tinder for stuff
            </p>

            <button
              onClick={onClose}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-2xl transition-all shadow-lg"
            >
              Got it! Start Swiping
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
