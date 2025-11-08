import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ActionSheetBidProps {
  isOpen: boolean;
  currentDurationHours: number; // 24, 48, or 72
  onSelect: (durationHours: number) => void;
  onClose: () => void;
}

/**
 * ActionSheetBid - Quick edit sheet for bid/auction duration
 * Opens on long-press of Bid button
 * Options: 24h, 48h, 72h
 */
export const ActionSheetBid: React.FC<ActionSheetBidProps> = ({
  isOpen,
  currentDurationHours,
  onSelect,
  onClose,
}) => {
  const options = [
    { hours: 24, label: '24 Hours', color: 'amber-300' },
    { hours: 48, label: '48 Hours', color: 'amber-400' },
    { hours: 72, label: '72 Hours', color: 'amber-500' },
  ];

  const handleSelect = (hours: number) => {
    // Just call onSelect - the parent handles close and haptic
    onSelect(hours);
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
            className="fixed inset-0 z-[250] bg-black/50 backdrop-blur-sm"
          />

          {/* Action Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 z-[251] bg-gray-900 rounded-t-3xl shadow-2xl p-6"
          >
            {/* Handle bar */}
            <div className="w-12 h-1.5 bg-gray-700 rounded-full mx-auto mb-6" />

            {/* Title */}
            <h3 className="text-xl font-bold text-white mb-4 text-center">
              Auction Duration
            </h3>

            {/* Current value chip */}
            <div className="flex justify-center mb-4">
              <div className="px-3 py-1 bg-amber-500/20 border border-amber-500 rounded-full">
                <span className="text-sm font-medium text-amber-400">
                  Current: {currentDurationHours}h
                </span>
              </div>
            </div>

            {/* Options */}
            <div className="space-y-3 mb-4">
              {options.map(({ hours, label, color }) => (
                <button
                  key={hours}
                  onClick={() => handleSelect(hours)}
                  className={`w-full p-4 rounded-xl border-2 transition-all ${
                    hours === currentDurationHours
                      ? `bg-${color}/30 border-${color} shadow-lg`
                      : `bg-gray-800 border-gray-700 hover:border-${color}/50`
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-semibold text-white">{label}</span>
                    {hours === currentDurationHours && (
                      <span className="text-amber-400">✓</span>
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
