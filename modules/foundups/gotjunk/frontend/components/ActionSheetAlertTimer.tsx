import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';

interface ActionSheetAlertTimerProps {
  isOpen: boolean;
  type: 'ice' | 'police';
  onSelect: (minutes: number, isPermanent?: boolean) => void;
  onClose: () => void;
}

/**
 * ActionSheetAlertTimer - Quick edit sheet for alert timer duration
 * Opens on long-press of ICE or Police button
 * Police: 5, 10, 15 minutes
 * ICE: 30, 60, 120 minutes, or Permanent (facility)
 */
export const ActionSheetAlertTimer: React.FC<ActionSheetAlertTimerProps> = ({
  isOpen,
  type,
  onSelect,
  onClose,
}) => {
  const policeOptions = [
    { minutes: 5, label: '5 Minutes', emoji: '🚓', isPermanent: false },
    { minutes: 10, label: '10 Minutes', emoji: '🚓', isPermanent: false },
    { minutes: 15, label: '15 Minutes', emoji: '🚓', isPermanent: false },
  ];

  const iceOptions = [
    { minutes: 30, label: '30 Minutes', emoji: '🧊', isPermanent: false },
    { minutes: 60, label: '1 Hour', emoji: '🧊', isPermanent: false },
    { minutes: 120, label: '2 Hours', emoji: '🧊', isPermanent: false },
    { minutes: 0, label: 'Permanent (Facility)', emoji: '🏢', isPermanent: true },
  ];

  const options = type === 'police' ? policeOptions : iceOptions;
  const title = type === 'police' ? 'Police Alert Duration' : 'ICE Alert Duration';
  const defaultMinutes = type === 'police' ? 5 : 60;

  const handleSelect = (minutes: number, isPermanent?: boolean) => {
    onSelect(minutes, isPermanent);
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
              {type === 'police'
                ? 'Alert expires after countdown - use for active enforcement'
                : 'Alert duration or permanent for ICE facilities'}
            </p>

            {/* Options */}
            <div className="space-y-3 mb-4">
              {options.map(({ minutes, label, emoji, isPermanent }) => (
                <button
                  key={`${minutes}-${isPermanent}`}
                  onClick={() => handleSelect(minutes, isPermanent)}
                  className={`w-full p-4 rounded-xl border-2 transition-all ${
                    minutes === defaultMinutes && !isPermanent
                      ? type === 'police'
                        ? 'bg-red-500/30 border-red-400 shadow-lg'
                        : 'bg-blue-500/30 border-blue-400 shadow-lg'
                      : 'bg-gray-800 border-gray-700 hover:border-blue-400/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{emoji}</span>
                      <span className="text-lg font-semibold text-white">{label}</span>
                    </div>
                    {minutes === defaultMinutes && !isPermanent && (
                      <span className={type === 'police' ? 'text-red-400' : 'text-blue-400'}>
                        ✓ Default
                      </span>
                    )}
                    {isPermanent && (
                      <span className="text-yellow-400">∞</span>
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
