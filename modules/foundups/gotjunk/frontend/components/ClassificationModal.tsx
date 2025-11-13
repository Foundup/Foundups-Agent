import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ItemClassification } from '../types';
import { FreeIcon } from './icons/FreeIcon';
import { DiscountIcon } from './icons/DiscountIcon';
import { BidIcon } from './icons/BidIcon';
import { useLongPress } from '../hooks/useLongPress';
import { ActionSheetDiscount } from './ActionSheetDiscount';
import { ActionSheetBid } from './ActionSheetBid';
import { ActionSheetStayLimit } from './ActionSheetStayLimit';
import { ActionSheetAlertTimer } from './ActionSheetAlertTimer';
import { Z_LAYERS } from '../constants/zLayers';

interface ClassificationModalProps {
  isOpen: boolean;
  imageUrl: string;
  libertyEnabled?: boolean; // Determines which classifications to show
  isMapView?: boolean; // Show all 11 categories on map, only 5 on My Items
  onClassify: (
    classification: ItemClassification,
    discountPercent?: number,
    bidDurationHours?: number,
    stayLimitNights?: number,
    alertTimerMinutes?: number,
    isPermanent?: boolean
  ) => void;
}

/**
 * ClassificationModal - Post-capture classification popup
 *
 * REGULAR CAMERA (5 options):
 * - 💙 free, 💚 discount, ⚡ bid, 🔄 share, 🔍 wanted
 *
 * LIBERTY CAMERA (6 options):
 * - 🍞 food, 🛏️ couch (1 night), ⛺ camping (2 nights), 🏠 housing, 🧊 ice, 🚓 police (5 min)
 *
 * Gestures:
 * - Short tap: Select classification with defaults
 * - Long press discount/bid: Edit discount% or bid duration
 * - Long press couch/camping: Show stayLimit info
 * - Long press ice/police: Edit timer duration
 */
export const ClassificationModal: React.FC<ClassificationModalProps> = ({
  isOpen,
  imageUrl,
  libertyEnabled = false,
  isMapView = false,
  onClassify,
}) => {
  // Action sheet state
  const [discountSheetOpen, setDiscountSheetOpen] = useState(false);
  const [bidSheetOpen, setBidSheetOpen] = useState(false);
  const [stayLimitSheetOpen, setStayLimitSheetOpen] = useState(false);
  const [alertTimerSheetOpen, setAlertTimerSheetOpen] = useState(false);
  const [currentStayLimitType, setCurrentStayLimitType] = useState<'couch' | 'camping'>('couch');
  const [currentAlertType, setCurrentAlertType] = useState<'ice' | 'police'>('police');

  // Load saved defaults from localStorage
  const [discountPercent, setDiscountPercent] = useState(() => {
    const saved = localStorage.getItem('gotjunk_default_discount');
    return saved ? parseInt(saved, 10) : 75;
  });
  const [bidDurationHours, setBidDurationHours] = useState(() => {
    const saved = localStorage.getItem('gotjunk_default_bid_duration');
    return saved ? parseInt(saved, 10) : 48;
  });

  // ============================================================================
  // REGULAR CAMERA - Long Press Handlers
  // ============================================================================

  const discountLongPress = useLongPress({
    onLongPress: () => setDiscountSheetOpen(true),
    onTap: () => setDiscountSheetOpen(true), // Always open action sheet
    threshold: 450,
  });

  const bidLongPress = useLongPress({
    onLongPress: () => setBidSheetOpen(true),
    onTap: () => setBidSheetOpen(true), // Always open action sheet
    threshold: 450,
  });

  // ============================================================================
  // LIBERTY CAMERA - Long Press Handlers
  // ============================================================================

  const couchLongPress = useLongPress({
    onLongPress: () => {
      setCurrentStayLimitType('couch');
      setStayLimitSheetOpen(true);
    },
    onTap: () => onClassify('couch', undefined, undefined, 1), // Default: 1 night
    threshold: 450,
  });

  const campingLongPress = useLongPress({
    onLongPress: () => {
      setCurrentStayLimitType('camping');
      setStayLimitSheetOpen(true);
    },
    onTap: () => onClassify('camping', undefined, undefined, 2), // Default: 2 nights
    threshold: 450,
  });

  const iceLongPress = useLongPress({
    onLongPress: () => {
      setCurrentAlertType('ice');
      setAlertTimerSheetOpen(true);
    },
    onTap: () => onClassify('ice', undefined, undefined, undefined, 60), // Default: 60 min
    threshold: 450,
  });

  const policeLongPress = useLongPress({
    onLongPress: () => {
      setCurrentAlertType('police');
      setAlertTimerSheetOpen(true);
    },
    onTap: () => onClassify('police', undefined, undefined, undefined, 5), // Default: 5 min
    threshold: 450,
  });

  // ============================================================================
  // Action Sheet Handlers
  // ============================================================================

  const handleDiscountSelect = (percent: number) => {
    localStorage.setItem('gotjunk_default_discount', percent.toString());
    if (navigator.vibrate) navigator.vibrate([10, 50, 10]);
    setDiscountSheetOpen(false);
    onClassify('discount', percent);
  };

  const handleBidSelect = (hours: number) => {
    localStorage.setItem('gotjunk_default_bid_duration', hours.toString());
    if (navigator.vibrate) navigator.vibrate([10, 50, 10]);
    setBidSheetOpen(false);
    onClassify('bid', undefined, hours);
  };

  const handleStayLimitSelect = (nights: number) => {
    if (navigator.vibrate) navigator.vibrate([10, 50, 10]);
    setStayLimitSheetOpen(false);
    onClassify(currentStayLimitType, undefined, undefined, nights);
  };

  const handleAlertTimerSelect = (minutes: number, isPermanent?: boolean) => {
    if (navigator.vibrate) navigator.vibrate([10, 50, 10]);
    setAlertTimerSheetOpen(false);
    onClassify(currentAlertType, undefined, undefined, undefined, minutes, isPermanent);
  };

  // ============================================================================
  // RENDER: MAP VIEW (All 11 Categories)
  // ============================================================================

  if (isMapView) {
    return (
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-sm flex flex-col items-center justify-center p-6 overflow-y-auto"
            style={{
              zIndex: Z_LAYERS.modal,
              WebkitTouchCallout: 'none',
              WebkitUserSelect: 'none',
              userSelect: 'none',
            }}
          >
            {/* Preview image */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-full max-w-sm mb-4 rounded-2xl overflow-hidden shadow-2xl"
            >
              <img src={imageUrl} alt="Captured item" className="w-full h-auto" />
            </motion.div>

            {/* Title */}
            <h2 className="text-xl font-bold text-white mb-3 text-center">
              Select Category (11 Types)
            </h2>

            {/* Classification buttons - All 11 types */}
            <div className="w-full max-w-sm space-y-2 mb-4">
              {/* Commerce (3) */}
              <div className="mb-1">
                <p className="text-xs font-semibold text-gray-400 mb-1 uppercase tracking-wide">Commerce</p>
              </div>

              {/* Free */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('free')}
                className="w-full flex items-center justify-between p-3 bg-blue-500/20 hover:bg-blue-500/30 border-2 border-blue-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">💙</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Free</h3>
                  </div>
                </div>
              </motion.button>

              {/* Discount */}
              <button
                {...discountLongPress}
                className="w-full flex items-center justify-between p-3 bg-green-500/20 hover:bg-green-500/30 active:scale-95 border-2 border-green-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">💚</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Discount</h3>
                  </div>
                </div>
                <span className="text-xs font-bold text-green-400">{discountPercent}%</span>
              </button>

              {/* Bid */}
              <button
                {...bidLongPress}
                className="w-full flex items-center justify-between p-3 bg-amber-500/20 hover:bg-amber-500/30 active:scale-95 border-2 border-amber-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">⚡</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Bid</h3>
                  </div>
                </div>
                <span className="text-xs font-bold text-amber-400">{bidDurationHours}h</span>
              </button>

              {/* Share Economy (2) */}
              <div className="mb-1 mt-3">
                <p className="text-xs font-semibold text-gray-400 mb-1 uppercase tracking-wide">Share Economy</p>
              </div>

              {/* Share */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('share')}
                className="w-full flex items-center justify-between p-3 bg-purple-500/20 hover:bg-purple-500/30 border-2 border-purple-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">🔄</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Share</h3>
                  </div>
                </div>
              </motion.button>

              {/* Wanted */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('wanted')}
                className="w-full flex items-center justify-between p-3 bg-pink-500/20 hover:bg-pink-500/30 border-2 border-pink-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">🔍</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Wanted</h3>
                  </div>
                </div>
              </motion.button>

              {/* Mutual Aid (4) */}
              <div className="mb-1 mt-3">
                <p className="text-xs font-semibold text-gray-400 mb-1 uppercase tracking-wide">Mutual Aid</p>
              </div>

              {/* Food */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('food')}
                className="w-full flex items-center justify-between p-3 bg-orange-500/20 hover:bg-orange-500/30 border-2 border-orange-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">🍞</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Food</h3>
                  </div>
                </div>
              </motion.button>

              {/* Couch */}
              <button
                {...couchLongPress}
                className="w-full flex items-center justify-between p-3 bg-indigo-500/20 hover:bg-indigo-500/30 active:scale-95 border-2 border-indigo-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">🛏️</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Couch</h3>
                  </div>
                </div>
                <span className="text-xs font-bold text-indigo-400">1N</span>
              </button>

              {/* Camping */}
              <button
                {...campingLongPress}
                className="w-full flex items-center justify-between p-3 bg-teal-500/20 hover:bg-teal-500/30 active:scale-95 border-2 border-teal-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">⛺</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Camping</h3>
                  </div>
                </div>
                <span className="text-xs font-bold text-teal-400">2N</span>
              </button>

              {/* Housing */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('housing')}
                className="w-full flex items-center justify-between p-3 bg-cyan-500/20 hover:bg-cyan-500/30 border-2 border-cyan-400 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">🏠</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Housing</h3>
                  </div>
                </div>
              </motion.button>

              {/* Alerts (2) */}
              <div className="mb-1 mt-3">
                <p className="text-xs font-semibold text-red-400 mb-1 uppercase tracking-wide">Alerts — Time Sensitive</p>
              </div>

              {/* ICE Alert */}
              <button
                {...iceLongPress}
                className="w-full flex items-center justify-between p-3 bg-blue-600/20 hover:bg-blue-600/30 active:scale-95 border-2 border-blue-500 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">🧊</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">ICE Alert</h3>
                  </div>
                </div>
                <span className="text-xs font-bold text-blue-400">60m</span>
              </button>

              {/* Police Alert */}
              <button
                {...policeLongPress}
                className="w-full flex items-center justify-between p-3 bg-red-600/20 hover:bg-red-600/30 active:scale-95 border-2 border-red-500 rounded-xl transition-all"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">🚓</span>
                  <div className="text-left">
                    <h3 className="text-sm font-bold text-white">Police Alert</h3>
                  </div>
                </div>
                <span className="text-xs font-bold text-red-400">5m</span>
              </button>
            </div>

            {/* Helper text */}
            <p className="text-xs text-gray-400 mt-2 text-center">
              Tap to select • Hold to customize
            </p>

            {/* Action Sheets */}
            <ActionSheetDiscount
              isOpen={discountSheetOpen}
              currentPercent={discountPercent}
              onSelect={handleDiscountSelect}
              onClose={() => setDiscountSheetOpen(false)}
            />
            <ActionSheetBid
              isOpen={bidSheetOpen}
              currentDurationHours={bidDurationHours}
              onSelect={handleBidSelect}
              onClose={() => setBidSheetOpen(false)}
            />
            <ActionSheetStayLimit
              isOpen={stayLimitSheetOpen}
              type={currentStayLimitType}
              onSelect={handleStayLimitSelect}
              onClose={() => setStayLimitSheetOpen(false)}
            />
            <ActionSheetAlertTimer
              isOpen={alertTimerSheetOpen}
              type={currentAlertType}
              onSelect={handleAlertTimerSelect}
              onClose={() => setAlertTimerSheetOpen(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>
    );
  }

  // ============================================================================
  // RENDER: REGULAR CAMERA (Commerce + Share Economy)
  // ============================================================================

  if (!libertyEnabled) {
    return (
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-sm flex flex-col items-center justify-center p-6"
            style={{
              zIndex: Z_LAYERS.modal,
              WebkitTouchCallout: 'none',
              WebkitUserSelect: 'none',
              userSelect: 'none',
            }}
          >
            {/* Preview image */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-full max-w-sm mb-6 rounded-2xl overflow-hidden shadow-2xl"
            >
              <img src={imageUrl} alt="Captured item" className="w-full h-auto" />
            </motion.div>

            {/* Title */}
            <h2 className="text-2xl font-bold text-white mb-4 text-center">
              How would you like to list this?
            </h2>

            {/* Classification buttons */}
            <div className="w-full max-w-sm space-y-3">
              {/* Free */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('free')}
                className="w-full flex items-center justify-between p-4 bg-blue-500/20 hover:bg-blue-500/30 border-2 border-blue-400 rounded-2xl transition-all shadow-lg shadow-blue-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-500 rounded-full">
                    <FreeIcon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-bold text-white">Free</h3>
                    <p className="text-xs text-blue-200">Give it away</p>
                  </div>
                </div>
                <span className="text-xl font-bold text-blue-400">$0</span>
              </motion.button>

              {/* Discount */}
              <button
                {...discountLongPress}
                className="w-full flex items-center justify-between p-4 bg-green-500/20 hover:bg-green-500/30 active:scale-95 border-2 border-green-400 rounded-2xl transition-all shadow-lg shadow-green-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-500 rounded-full">
                    <DiscountIcon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-bold text-white">Discount</h3>
                    <p className="text-xs text-green-200">Sell it fast</p>
                  </div>
                </div>
                <span className="text-sm font-bold text-green-400">{discountPercent}% OFF</span>
              </button>

              {/* Bid */}
              <button
                {...bidLongPress}
                className="w-full flex items-center justify-between p-4 bg-amber-500/20 hover:bg-amber-500/30 active:scale-95 border-2 border-amber-400 rounded-2xl transition-all shadow-lg shadow-amber-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-amber-500 rounded-full">
                    <BidIcon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-bold text-white">Bid</h3>
                    <p className="text-xs text-amber-200">Let buyers compete</p>
                  </div>
                </div>
                <span className="text-sm font-bold text-amber-400">{bidDurationHours}h</span>
              </button>

              {/* Share */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('share')}
                className="w-full flex items-center justify-between p-4 bg-purple-500/20 hover:bg-purple-500/30 border-2 border-purple-400 rounded-2xl transition-all shadow-lg shadow-purple-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">🔄</span>
                  <div className="text-left">
                    <h3 className="text-lg font-bold text-white">Share</h3>
                    <p className="text-xs text-purple-200">Lend it out</p>
                  </div>
                </div>
              </motion.button>

              {/* Wanted */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('wanted')}
                className="w-full flex items-center justify-between p-4 bg-pink-500/20 hover:bg-pink-500/30 border-2 border-pink-400 rounded-2xl transition-all shadow-lg shadow-pink-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">🔍</span>
                  <div className="text-left">
                    <h3 className="text-lg font-bold text-white">Wanted</h3>
                    <p className="text-xs text-pink-200">Looking for this</p>
                  </div>
                </div>
              </motion.button>
            </div>

            {/* Helper text */}
            <p className="text-xs text-gray-400 mt-4 text-center">
              Tap to select • Hold Discount/Bid to customize
            </p>

            {/* Action Sheets */}
            <ActionSheetDiscount
              isOpen={discountSheetOpen}
              currentPercent={discountPercent}
              onSelect={handleDiscountSelect}
              onClose={() => setDiscountSheetOpen(false)}
            />
            <ActionSheetBid
              isOpen={bidSheetOpen}
              currentDurationHours={bidDurationHours}
              onSelect={handleBidSelect}
              onClose={() => setBidSheetOpen(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>
    );
  }

  // ============================================================================
  // RENDER: LIBERTY CAMERA (Mutual Aid + Alerts)
  // ============================================================================

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/90 backdrop-blur-sm flex flex-col items-center justify-center p-6"
          style={{
            zIndex: Z_LAYERS.modal,
            WebkitTouchCallout: 'none',
            WebkitUserSelect: 'none',
            userSelect: 'none',
          }}
        >
          {/* Preview image */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="w-full max-w-sm mb-6 rounded-2xl overflow-hidden shadow-2xl"
          >
            <img src={imageUrl} alt="Captured item" className="w-full h-auto" />
          </motion.div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-white mb-4 text-center">
            🗽 Liberty Alert - Community Aid
          </h2>

          {/* Classification buttons */}
          <div className="w-full max-w-sm space-y-3">
            {/* Food */}
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onClassify('food')}
              className="w-full flex items-center justify-between p-4 bg-orange-500/20 hover:bg-orange-500/30 border-2 border-orange-400 rounded-2xl transition-all shadow-lg shadow-orange-500/20"
              style={{ touchAction: 'manipulation' }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-3xl">🍞</span>
                <div className="text-left">
                  <h3 className="text-lg font-bold text-white">Food</h3>
                  <p className="text-xs text-orange-200">Meals & groceries</p>
                </div>
              </div>
            </motion.button>

            {/* Couch */}
            <button
              {...couchLongPress}
              className="w-full flex items-center justify-between p-4 bg-indigo-500/20 hover:bg-indigo-500/30 active:scale-95 border-2 border-indigo-400 rounded-2xl transition-all shadow-lg shadow-indigo-500/20"
              style={{ touchAction: 'manipulation' }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-3xl">🛏️</span>
                <div className="text-left">
                  <h3 className="text-lg font-bold text-white">Couch</h3>
                  <p className="text-xs text-indigo-200">1 night max</p>
                </div>
              </div>
              <span className="text-sm font-bold text-indigo-400">1N</span>
            </button>

            {/* Camping */}
            <button
              {...campingLongPress}
              className="w-full flex items-center justify-between p-4 bg-teal-500/20 hover:bg-teal-500/30 active:scale-95 border-2 border-teal-400 rounded-2xl transition-all shadow-lg shadow-teal-500/20"
              style={{ touchAction: 'manipulation' }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-3xl">⛺</span>
                <div className="text-left">
                  <h3 className="text-lg font-bold text-white">Camping</h3>
                  <p className="text-xs text-teal-200">2 nights max</p>
                </div>
              </div>
              <span className="text-sm font-bold text-teal-400">2N</span>
            </button>

            {/* Housing */}
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onClassify('housing')}
              className="w-full flex items-center justify-between p-4 bg-cyan-500/20 hover:bg-cyan-500/30 border-2 border-cyan-400 rounded-2xl transition-all shadow-lg shadow-cyan-500/20"
              style={{ touchAction: 'manipulation' }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-3xl">🏠</span>
                <div className="text-left">
                  <h3 className="text-lg font-bold text-white">Housing</h3>
                  <p className="text-xs text-cyan-200">Long-term shelter</p>
                </div>
              </div>
            </motion.button>

            {/* ICE Alert */}
            <button
              {...iceLongPress}
              className="w-full flex items-center justify-between p-4 bg-blue-600/20 hover:bg-blue-600/30 active:scale-95 border-2 border-blue-500 rounded-2xl transition-all shadow-lg shadow-blue-600/20"
              style={{ touchAction: 'manipulation' }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-3xl">🧊</span>
                <div className="text-left">
                  <h3 className="text-lg font-bold text-white">ICE Alert</h3>
                  <p className="text-xs text-blue-200">Immigration enforcement</p>
                </div>
              </div>
              <span className="text-sm font-bold text-blue-400">60m</span>
            </button>

            {/* Police Alert */}
            <button
              {...policeLongPress}
              className="w-full flex items-center justify-between p-4 bg-red-600/20 hover:bg-red-600/30 active:scale-95 border-2 border-red-500 rounded-2xl transition-all shadow-lg shadow-red-600/20"
              style={{ touchAction: 'manipulation' }}
            >
              <div className="flex items-center space-x-3">
                <span className="text-3xl">🚓</span>
                <div className="text-left">
                  <h3 className="text-lg font-bold text-white">Police Alert</h3>
                  <p className="text-xs text-red-200">Law enforcement</p>
                </div>
              </div>
              <span className="text-sm font-bold text-red-400">5m</span>
            </button>
          </div>

          {/* Helper text */}
          <p className="text-xs text-gray-400 mt-4 text-center">
            Tap to select • Hold Couch/Camping/Ice/Police to customize
          </p>

          {/* Action Sheets */}
          <ActionSheetStayLimit
            isOpen={stayLimitSheetOpen}
            type={currentStayLimitType}
            onSelect={handleStayLimitSelect}
            onClose={() => setStayLimitSheetOpen(false)}
          />
          <ActionSheetAlertTimer
            isOpen={alertTimerSheetOpen}
            type={currentAlertType}
            onSelect={handleAlertTimerSelect}
            onClose={() => setAlertTimerSheetOpen(false)}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};
