import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';

interface ActionSheetDiscountProps {
  isOpen: boolean;
  currentPercent: number; // 75 or 50
  onSelect: (percent: number) => void;
  onClose: () => void;
}

/**
 * ActionSheetDiscount - Quick edit sheet for discount percentage
 * Opens on long-press of Discount button
 * Options: 25%, 50%, 75%, Custom
 */
export const ActionSheetDiscount: React.FC<ActionSheetDiscountProps> = ({
  isOpen,
  currentPercent,
  onSelect,
  onClose,
}) => {
  const options = [
    { percent: 25, label: '25% OFF', color: 'green-300' },
    { percent: 50, label: '50% OFF', color: 'green-400' },
    { percent: 75, label: '75% OFF', color: 'green-500' },
  ];

  const handleSelect = (percent: number) => {
    // Just call onSelect - the parent handles close and haptic
    onSelect(percent);
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
              Select Discount
            </h3>

            {/* Current value chip */}
            <div className="flex justify-center mb-4">
              <div className="px-3 py-1 bg-green-500/20 border border-green-500 rounded-full">
                <span className="text-sm font-medium text-green-400">
                  Current: {currentPercent}% OFF
                </span>
              </div>
            </div>

            {/* Options */}
            <div className="space-y-3 mb-4">
              {options.map(({ percent, label, color }) => (
                <button
                  key={percent}
                  onClick={() => handleSelect(percent)}
                  className={`w-full p-4 rounded-xl border-2 transition-all ${
                    percent === currentPercent
                      ? `bg-${color}/30 border-${color} shadow-lg`
                      : `bg-gray-800 border-gray-700 hover:border-${color}/50`
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-semibold text-white">{label}</span>
                    {percent === currentPercent && (
                      <span className="text-green-400">✓</span>
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
