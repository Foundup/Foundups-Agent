import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ItemClassification } from '../types';
import { FreeIcon } from './icons/FreeIcon';
import { DiscountIcon } from './icons/DiscountIcon';
import { BidIcon } from './icons/BidIcon';

interface ClassificationModalProps {
  isOpen: boolean;
  imageUrl: string;
  onClassify: (classification: ItemClassification) => void;
}

/**
 * ClassificationModal - Post-capture classification popup
 * User must choose Free, Discount, or Bid before item is saved
 */
export const ClassificationModal: React.FC<ClassificationModalProps> = ({
  isOpen,
  imageUrl,
  onClassify,
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[200] bg-black/90 backdrop-blur-sm flex flex-col items-center justify-center p-6"
        >
          {/* Preview image */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="w-full max-w-sm mb-8 rounded-2xl overflow-hidden shadow-2xl"
          >
            <img src={imageUrl} alt="Captured item" className="w-full h-auto" />
          </motion.div>

          {/* Classification title */}
          <h2 className="text-2xl font-bold text-white mb-6 text-center">
            How would you like to list this?
          </h2>

          {/* Classification buttons */}
          <div className="w-full max-w-sm space-y-4">
            {/* Free button */}
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onClassify('free')}
              className="w-full flex items-center justify-between p-5 bg-blue-500/20 hover:bg-blue-500/30 border-2 border-blue-400 rounded-2xl transition-all shadow-lg shadow-blue-500/20"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-500 rounded-full">
                  <FreeIcon className="w-8 h-8 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-xl font-bold text-white">Free</h3>
                  <p className="text-sm text-blue-200">Give it away</p>
                </div>
              </div>
              <span className="text-2xl font-bold text-blue-400">$0</span>
            </motion.button>

            {/* Discount button */}
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onClassify('discount')}
              className="w-full flex items-center justify-between p-5 bg-green-500/20 hover:bg-green-500/30 border-2 border-green-400 rounded-2xl transition-all shadow-lg shadow-green-500/20"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-green-500 rounded-full">
                  <DiscountIcon className="w-8 h-8 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-xl font-bold text-white">Discount</h3>
                  <p className="text-sm text-green-200">Sell it fast</p>
                </div>
              </div>
              <span className="text-lg font-bold text-green-400">75% OFF</span>
            </motion.button>

            {/* Bid button */}
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onClassify('bid')}
              className="w-full flex items-center justify-between p-5 bg-amber-500/20 hover:bg-amber-500/30 border-2 border-amber-400 rounded-2xl transition-all shadow-lg shadow-amber-500/20"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-amber-500 rounded-full">
                  <BidIcon className="w-8 h-8 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-xl font-bold text-white">Bid</h3>
                  <p className="text-sm text-amber-200">Let buyers compete</p>
                </div>
              </div>
              <span className="text-lg font-bold text-amber-400">AUCTION</span>
            </motion.button>
          </div>

          {/* Helper text */}
          <p className="text-sm text-gray-400 mt-6 text-center">
            You can change this later
          </p>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
