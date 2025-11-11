/**
 * PurchaseModal - Cart item purchase confirmation
 *
 * Triggered by:
 * - Right swipe on cart item in fullscreen
 * - > button in cart fullscreen
 *
 * Shows:
 * - Item preview
 * - Classification type (free/discount/bid)
 * - Price (discount % or bid amount)
 * - Fiat equivalent (USD)
 * - Confirm/Cancel buttons
 *
 * TODO: Integrate with FoundUps crypto wallet (testnet)
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CapturedItem } from '../types';
import { Z_LAYERS } from '../constants/zLayers';

interface PurchaseModalProps {
  isOpen: boolean;
  item: CapturedItem | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export const PurchaseModal: React.FC<PurchaseModalProps> = ({
  isOpen,
  item,
  onConfirm,
  onCancel,
}) => {
  if (!item) return null;

  // Calculate price based on classification
  const getPrice = () => {
    if (item.classification === 'free') {
      return { amount: 'FREE', fiat: '$0.00' };
    } else if (item.classification === 'discount') {
      const discount = item.discountPercent || 50;
      // Placeholder: Assume original price $10
      const originalPrice = 10.00;
      const discountedPrice = originalPrice * (1 - discount / 100);
      return {
        amount: `${discount}% OFF`,
        fiat: `$${discountedPrice.toFixed(2)}`,
        original: `$${originalPrice.toFixed(2)}`,
      };
    } else if (item.classification === 'bid') {
      // Placeholder: Show bid duration
      const hours = item.bidDurationHours || 48;
      return {
        amount: `BID (${hours}h)`,
        fiat: 'Auction',
      };
    }
    return { amount: 'Unknown', fiat: '$0.00' };
  };

  const price = getPrice();

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 flex items-center justify-center p-4"
          style={{ zIndex: Z_LAYERS.PURCHASE_MODAL }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/90 backdrop-blur-md"
            onClick={onCancel}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Modal Content */}
          <motion.div
            className="relative bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl shadow-2xl border-2 border-gray-700 overflow-hidden max-w-sm w-full"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-center">
              <h2 className="text-2xl font-bold text-white mb-1">Purchase Item?</h2>
              <p className="text-sm text-blue-100">Confirm your purchase</p>
            </div>

            {/* Item Preview */}
            <div className="p-6">
              <div className="relative w-full aspect-square rounded-2xl overflow-hidden mb-4 shadow-xl">
                <img
                  src={item.url}
                  alt="Item preview"
                  className="w-full h-full object-cover"
                />
                {/* Classification Badge */}
                <div className="absolute top-2 right-2 px-3 py-1 rounded-full text-xs font-bold uppercase shadow-lg backdrop-blur-md"
                  style={{
                    backgroundColor:
                      item.classification === 'free'
                        ? '#22c55e' // Green
                        : item.classification === 'discount'
                        ? '#f59e0b' // Amber
                        : '#8b5cf6', // Purple (bid)
                    color: '#fff',
                  }}
                >
                  {item.classification}
                </div>
              </div>

              {/* Price Details */}
              <div className="bg-gray-800/50 rounded-xl p-4 mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400 text-sm">Type:</span>
                  <span className="text-white font-semibold">{price.amount}</span>
                </div>
                {price.original && (
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-400 text-sm">Original:</span>
                    <span className="text-gray-500 line-through">{price.original}</span>
                  </div>
                )}
                <div className="flex justify-between items-center border-t border-gray-700 pt-2">
                  <span className="text-gray-400 text-sm">Price:</span>
                  <span className="text-2xl font-bold text-green-400">{price.fiat}</span>
                </div>
              </div>

              {/* Crypto Wallet Notice */}
              <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3 mb-6">
                <p className="text-xs text-blue-200 text-center">
                  💰 Payment via FoundUps Wallet (Testnet)
                  <br />
                  <span className="text-blue-300 font-semibold">Balance: $1,000.00</span>
                </p>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-3">
                <motion.button
                  onClick={onCancel}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-semibold shadow-lg transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Cancel
                </motion.button>
                <motion.button
                  onClick={onConfirm}
                  className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white rounded-xl font-semibold shadow-lg transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Confirm
                </motion.button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
