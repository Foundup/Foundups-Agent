import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CapturedItem, ItemClassification } from '../types';

interface OptionsModalProps {
  isOpen: boolean;
  item: CapturedItem;
  onSave: (discountPercent?: number, bidDurationHours?: number) => void;
  onClose: () => void;
}

export const OptionsModal: React.FC<OptionsModalProps> = ({ isOpen, item, onSave, onClose }) => {
  // Default values
  const [discountPercent, setDiscountPercent] = useState<number>(75);
  const [bidDurationHours, setBidDurationHours] = useState<number>(48);

  const handleSave = () => {
    if (item.classification === 'discount') {
      onSave(discountPercent, undefined);
    } else if (item.classification === 'bid') {
      onSave(undefined, bidDurationHours);
    }
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-[300] bg-black/90 backdrop-blur-sm flex flex-col items-center justify-center p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl p-8 max-w-sm w-full shadow-2xl border border-white/10"
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl font-bold text-white mb-6 text-center">
              {item.classification === 'discount' ? '🔽 Discount Options' : '🎯 Bid Options'}
            </h2>

            {/* Discount Options */}
            {item.classification === 'discount' && (
              <div className="space-y-4">
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Select Discount
                </label>
                <select
                  value={discountPercent}
                  onChange={(e) => setDiscountPercent(Number(e.target.value))}
                  className="w-full px-4 py-3 bg-gray-700 text-white rounded-xl border border-gray-600 focus:border-green-500 focus:ring-2 focus:ring-green-500/50 outline-none text-lg font-semibold"
                >
                  <option value={75}>75% OFF (Default)</option>
                  <option value={50}>50% OFF</option>
                </select>
              </div>
            )}

            {/* Bid Options */}
            {item.classification === 'bid' && (
              <div className="space-y-4">
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Auction Duration
                </label>
                <select
                  value={bidDurationHours}
                  onChange={(e) => setBidDurationHours(Number(e.target.value))}
                  className="w-full px-4 py-3 bg-gray-700 text-white rounded-xl border border-gray-600 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/50 outline-none text-lg font-semibold"
                >
                  <option value={24}>24 Hours</option>
                  <option value={48}>48 Hours (Default)</option>
                  <option value={72}>72 Hours</option>
                </select>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 mt-8">
              <button
                onClick={onClose}
                className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className={`flex-1 px-6 py-3 font-semibold rounded-xl transition-colors ${
                  item.classification === 'discount'
                    ? 'bg-green-500 hover:bg-green-600 text-white'
                    : 'bg-amber-500 hover:bg-amber-600 text-white'
                }`}
              >
                Save
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
