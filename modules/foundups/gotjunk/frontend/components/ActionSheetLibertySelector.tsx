import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';
import type { MutualAidClassification, AlertClassification } from '../types';

type LibertyClassification = MutualAidClassification | AlertClassification;

interface ActionSheetLibertySelectorProps {
  isOpen: boolean;
  currentSelection?: LibertyClassification;
  onSelect: (classification: LibertyClassification) => void;
  onClose: () => void;
}

interface LibertyOption {
  type: LibertyClassification;
  label: string;
  emoji: string;
  description: string;
}

const LIBERTY_OPTIONS: LibertyOption[] = [
  {
    type: 'food',
    label: 'Food',
    emoji: '🍞',
    description: 'Community food distribution',
  },
  {
    type: 'couch',
    label: 'Couch Surfing',
    emoji: '🛏️',
    description: '1 night max',
  },
  {
    type: 'camping',
    label: 'Camping',
    emoji: '⛺',
    description: '2 nights default',
  },
  {
    type: 'housing',
    label: 'Housing',
    emoji: '🏠',
    description: 'Long-term housing resources',
  },
  {
    type: 'ice',
    label: 'ICE Alert',
    emoji: '🧊',
    description: '60min default, permanent for facilities',
  },
  {
    type: 'police',
    label: 'Police Alert',
    emoji: '🚓',
    description: '5min default countdown',
  },
];

/**
 * ActionSheetLibertySelector - Liberty Alert classification selector
 * Opens on long-press of 🗽 badge
 * Pre-selects classification for rapid capture (like auto-classify toggle)
 * User selects once, then takes multiple photos with auto-classification
 */
export const ActionSheetLibertySelector: React.FC<ActionSheetLibertySelectorProps> = ({
  isOpen,
  currentSelection,
  onSelect,
  onClose,
}) => {
  const handleSelect = (classification: LibertyClassification) => {
    onSelect(classification);
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
            <h3 className="text-xl font-bold text-white mb-2 text-center">
              🗽 Select Liberty Alert Type
            </h3>

            {/* Info text */}
            <p className="text-sm text-gray-400 mb-4 text-center">
              Select once, then take multiple photos with auto-classification
            </p>

            {/* Options */}
            <div className="space-y-3 mb-4">
              {LIBERTY_OPTIONS.map(({ type, label, emoji, description }) => (
                <button
                  key={type}
                  onClick={() => handleSelect(type)}
                  className={`w-full p-4 rounded-xl border-2 transition-all ${
                    type === currentSelection
                      ? 'bg-blue-500/30 border-blue-400 shadow-lg'
                      : 'bg-gray-800 border-gray-700 hover:border-blue-400/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{emoji}</span>
                      <div className="text-left">
                        <div className="text-lg font-semibold text-white">{label}</div>
                        <div className="text-xs text-gray-400">{description}</div>
                      </div>
                    </div>
                    {type === currentSelection && (
                      <span className="text-blue-400">✓ Selected</span>
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
