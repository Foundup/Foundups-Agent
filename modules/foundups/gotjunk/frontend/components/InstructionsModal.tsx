/**
 * InstructionsModal - Dismissible welcome modal with swipe instructions
 * Shows on every page load
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface InstructionsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InstructionsModal: React.FC<InstructionsModalProps> = ({ isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl shadow-2xl p-8 max-w-md w-full border-2 border-gray-700">
              {/* Header */}
              <h2 className="text-4xl font-bold text-white mb-4 text-center">
                GotJunk?!
              </h2>

              <p className="text-xl text-gray-300 font-semibold mb-6 text-center">
                Browse items near you
              </p>

              {/* Instructions */}
              <div className="space-y-4 mb-8">
                <div className="flex items-center gap-3 bg-green-500/10 border-2 border-green-500 rounded-xl p-4">
                  <span className="text-3xl">➡️</span>
                  <div>
                    <p className="text-green-400 font-bold">Swipe Right</p>
                    <p className="text-gray-300 text-sm">Add to Cart</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 bg-red-500/10 border-2 border-red-500 rounded-xl p-4">
                  <span className="text-3xl">⬅️</span>
                  <div>
                    <p className="text-red-400 font-bold">Swipe Left</p>
                    <p className="text-gray-300 text-sm">Skip</p>
                  </div>
                </div>
              </div>

              {/* Info */}
              <p className="text-sm text-gray-400 text-center mb-6">
                50km radius • Tinder for stuff
              </p>

              {/* Close Button */}
              <button
                onClick={onClose}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-4 rounded-2xl transition-all shadow-lg"
              >
                Got it! Start Swiping
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
