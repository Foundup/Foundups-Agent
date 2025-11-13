import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';

interface ActionSheetStayLimitProps {
  isOpen: boolean;
  type: 'couch' | 'camping';
  onSelect: (nights: number) => void;
  onClose: () => void;
}

/**
 * ActionSheetStayLimit - Quick edit sheet for stay limit nights
 * Opens on long-press of Couch or Camping button
 * Couch: 1 night max (default)
 * Camping: 1-3 nights (default: 2)
 */
export const ActionSheetStayLimit: React.FC<ActionSheetStayLimitProps> = ({
  isOpen,
  type,
  onSelect,
  onClose,
}) => {
  const couchOptions = [{ nights: 1, label: '1 Night', emoji: '🛏️' }];

  const campingOptions = [
    { nights: 1, label: '1 Night', emoji: '⛺' },
    { nights: 2, label: '2 Nights', emoji: '⛺⛺' },
    { nights: 3, label: '3 Nights', emoji: '⛺⛺⛺' },
  ];

  const options = type === 'couch' ? couchOptions : campingOptions;
  const title = type === 'couch' ? 'Couch Surfing Stay' : 'Camping Stay Limit';
  const defaultNights = type === 'couch' ? 1 : 2;

  const handleSelect = (nights: number) => {
    onSelect(nights);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            style={{ zIndex: Z_LAYERS.actionSheet }}
          />

          {/* Action Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 bg-gray-900 rounded-t-3xl shadow-2xl p-6"
            style={{ zIndex: Z_LAYERS.actionSheet + 1 }}
          >
            {/* Handle bar */}
            <div className="w-12 h-1.5 bg-gray-700 rounded-full mx-auto mb-6" />

            {/* Title */}
            <h3 className="text-xl font-bold text-white mb-4 text-center">
              {title}
            </h3>

            {/* Info text */}
            <p className="text-sm text-gray-400 mb-4 text-center">
              {type === 'couch'
                ? 'Maximum 1 night for couch surfing'
                : 'Select duration for camping stay'}
            </p>

            {/* Options */}
            <div className="space-y-3 mb-4">
              {options.map(({ nights, label, emoji }) => (
                <button
                  key={nights}
                  onClick={() => handleSelect(nights)}
                  className={`w-full p-4 rounded-xl border-2 transition-all ${
                    nights === defaultNights
                      ? 'bg-indigo-500/30 border-indigo-400 shadow-lg'
                      : 'bg-gray-800 border-gray-700 hover:border-indigo-400/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{emoji}</span>
                      <span className="text-lg font-semibold text-white">{label}</span>
                    </div>
                    {nights === defaultNights && (
                      <span className="text-indigo-400">✓ Default</span>
                    )}
                  </div>
                </button>
              ))}
            </div>

            {/* Cancel button */}
            <button
              onClick={onClose}
              className="w-full p-4 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl transition-colors"
            >
              Cancel
            </button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
