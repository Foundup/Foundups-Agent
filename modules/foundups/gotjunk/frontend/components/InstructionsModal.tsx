/**
 * InstructionsModal - Dismissible welcome modal with swipe instructions
 * Shows on every page load, uses actual swipe button components
 * TRULY centered using grid - iOS Safari viewport-safe
 */

import React from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { Z_LAYERS } from '../constants/zLayers';

interface InstructionsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InstructionsModal: React.FC<InstructionsModalProps> = ({ isOpen, onClose }) => {
  if (typeof document === 'undefined') return null;

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          // Fixed to viewport, grid centers, respects safe areas
          className="fixed inset-0 grid place-items-center px-4"
          style={{
            paddingTop: 'env(safe-area-inset-top, 20px)',
            paddingBottom: 'env(safe-area-inset-bottom, 20px)',
            zIndex: Z_LAYERS.tutorialPopup,
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            backdropFilter: 'blur(2px)'
          }}
          role="dialog"
          aria-modal="true"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="w-[min(92vw,360px)] overflow-auto"
            style={{
              // Use --vh for iOS Safari viewport tracking
              maxHeight: 'calc(var(--vh, 1vh) * 85)'
            }}
            onClick={(e) => e.stopPropagation()}
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

              {/* Version indicator */}
              <p className="text-[10px] text-gray-500 text-center mt-3 font-mono">
                Build: {typeof __COMMIT_HASH__ !== 'undefined' ? __COMMIT_HASH__ : 'dev'}
              </p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body
  );
};
