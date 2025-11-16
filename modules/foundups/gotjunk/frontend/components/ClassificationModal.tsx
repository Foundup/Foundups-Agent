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

  // Expandable category state (for accordion Liberty menu)
  const [expandedCategory, setExpandedCategory] = useState<'alert' | 'food' | 'shelter' | null>(null);

  // View toggle state (regular vs LA) - only active when libertyEnabled=true
  const [showLibertyView, setShowLibertyView] = useState(false);

  // Load saved defaults from localStorage
  const [discountPercent, setDiscountPercent] = useState(() => {
    const saved = localStorage.getItem('gotjunk_default_discount');
    return saved ? parseInt(saved, 10) : 75;
  });
  const [bidDurationHours, setBidDurationHours] = useState(() => {
    const saved = localStorage.getItem('gotjunk_default_bid_duration');
    return saved ? parseInt(saved, 10) : 72;
  });

  // ============================================================================
  // REGULAR CAMERA - Long Press Handlers
  // ============================================================================

  const discountLongPress = useLongPress({
    onLongPress: () => setDiscountSheetOpen(true),
    onTap: () => onClassify('discount', discountPercent), // Tap = use default 75% off
    threshold: 450,
  });

  const bidLongPress = useLongPress({
    onLongPress: () => setBidSheetOpen(true),
    onTap: () => onClassify('bid', undefined, bidDurationHours), // Tap = use default 72h
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
  // LIBERTY CAMERA - Food Subcategory Handlers
  // ============================================================================

  const soupKitchenLongPress = useLongPress({
    onLongPress: () => {}, // No customization for food subcategories
    onTap: () => onClassify('soup_kitchen'),
    threshold: 450,
  });

  const bbqLongPress = useLongPress({
    onLongPress: () => {},
    onTap: () => onClassify('bbq'),
    threshold: 450,
  });

  const dryFoodLongPress = useLongPress({
    onLongPress: () => {},
    onTap: () => onClassify('dry_food'),
    threshold: 450,
  });

  const pickLongPress = useLongPress({
    onLongPress: () => {},
    onTap: () => onClassify('pick'),
    threshold: 450,
  });

  const gardenLongPress = useLongPress({
    onLongPress: () => {},
    onTap: () => onClassify('garden'),
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

  // Show regular view if: LA not unlocked, OR LA unlocked but toggle is OFF
  if (!showLibertyView) {
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
            {/* Preview image - 15% smaller */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-full max-w-sm mb-4 rounded-2xl overflow-hidden shadow-2xl"
            >
              <img src={imageUrl} alt="Captured item" className="w-full h-auto" />
            </motion.div>

            {/* Title - 15% smaller font */}
            <h2 className="text-xl font-bold text-white mb-3 text-center">
              How would you like to list this?
            </h2>

            {/* Stuff label with LA toggle */}
            <div className="flex items-center justify-center gap-2 mb-3">
              <span className="text-sm font-semibold text-gray-400 uppercase tracking-wide">Stuff</span>
              {libertyEnabled && (
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowLibertyView(true)}
                  className="text-xl"
                  aria-label="Switch to Liberty Alert categories"
                >
                  🗽
                </motion.button>
              )}
            </div>

            {/* Classification buttons - 15% smaller spacing */}
            <div className="w-full max-w-sm space-y-2.5">
              {/* Free - 15% smaller */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('free')}
                className="w-full flex items-center justify-between p-3 bg-blue-500/20 hover:bg-blue-500/30 border-2 border-blue-400 rounded-xl transition-all shadow-lg shadow-blue-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 bg-blue-500 rounded-full">
                    <FreeIcon className="w-5 h-5 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-base font-bold text-white">Free</h3>
                    <p className="text-[10px] text-blue-200">Give it away</p>
                  </div>
                </div>
                <span className="text-lg font-bold text-blue-400">$0</span>
              </motion.button>

              {/* Discount - 15% smaller */}
              <button
                {...discountLongPress}
                className="w-full flex items-center justify-between p-3 bg-green-500/20 hover:bg-green-500/30 active:scale-95 border-2 border-green-400 rounded-xl transition-all shadow-lg shadow-green-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 bg-green-500 rounded-full">
                    <DiscountIcon className="w-5 h-5 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-base font-bold text-white">Discount</h3>
                    <p className="text-[10px] text-green-200">Sell it fast</p>
                  </div>
                </div>
                <span className="text-xs font-bold text-green-400">{discountPercent}% OFF</span>
              </button>

              {/* Bid - 15% smaller */}
              <button
                {...bidLongPress}
                className="w-full flex items-center justify-between p-3 bg-amber-500/20 hover:bg-amber-500/30 active:scale-95 border-2 border-amber-400 rounded-xl transition-all shadow-lg shadow-amber-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 bg-amber-500 rounded-full">
                    <BidIcon className="w-5 h-5 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-base font-bold text-white">Bid</h3>
                    <p className="text-[10px] text-amber-200">Let buyers compete</p>
                  </div>
                </div>
                <span className="text-xs font-bold text-amber-400">{bidDurationHours}h</span>
              </button>

              {/* Share - 15% smaller */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('share')}
                className="w-full flex items-center justify-between p-3 bg-purple-500/20 hover:bg-purple-500/30 border-2 border-purple-400 rounded-xl transition-all shadow-lg shadow-purple-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2.5">
                  <span className="text-2xl">🔄</span>
                  <div className="text-left">
                    <h3 className="text-base font-bold text-white">Share</h3>
                    <p className="text-[10px] text-purple-200">Lend it out</p>
                  </div>
                </div>
              </motion.button>

              {/* Wanted - 15% smaller */}
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onClassify('wanted')}
                className="w-full flex items-center justify-between p-3 bg-pink-500/20 hover:bg-pink-500/30 border-2 border-pink-400 rounded-xl transition-all shadow-lg shadow-pink-500/20"
                style={{ touchAction: 'manipulation' }}
              >
                <div className="flex items-center space-x-2.5">
                  <span className="text-2xl">🔍</span>
                  <div className="text-left">
                    <h3 className="text-base font-bold text-white">Wanted</h3>
                    <p className="text-[10px] text-pink-200">Looking for this</p>
                  </div>
                </div>
              </motion.button>
            </div>

            {/* Helper text */}
            <p className="text-xs text-gray-400 mt-3 text-center">
              Tap to select • Hold Discount/Bid to customize
            </p>

            {/* Cancel button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                // Close modal without classifying
                window.history.back(); // Or use onClose callback if available
              }}
              className="w-full max-w-sm mt-3 py-2.5 bg-gray-700/50 hover:bg-gray-700/70 border border-gray-600 rounded-xl text-white font-semibold text-sm transition-all"
            >
              Cancel
            </motion.button>

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
  // RENDER: LIBERTY CAMERA (Condensed Categories)
  // ============================================================================

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
          {/* Preview image - 15% smaller */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="w-full max-w-sm mb-4 rounded-2xl overflow-hidden shadow-2xl"
          >
            <img src={imageUrl} alt="Captured item" className="w-full h-auto" />
          </motion.div>

          {/* Title - 15% smaller */}
          <h2 className="text-xl font-bold text-white mb-3 text-center">
            🗽 Liberty Alert - Select Category
          </h2>

          {/* Toggle back to Stuff view */}
          <div className="flex items-center justify-center gap-2 mb-3">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowLibertyView(false)}
              className="px-3 py-1 rounded-full bg-gray-700/50 hover:bg-gray-700/70 border border-gray-600 text-gray-300 text-sm font-semibold transition-all"
              aria-label="Switch back to Stuff categories"
            >
              ← Stuff
            </motion.button>
          </div>

          {/* Category Selection */}
          {/* Main Categories (Order: Alert, Food, Shelter for thumb accessibility) */}
          <div className="w-full max-w-sm space-y-3">
            {/* ALERT! Category */}
            <div className="border-2 border-red-500/50 rounded-xl overflow-hidden">
              {/* Alert! Header */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setExpandedCategory(expandedCategory === 'alert' ? null : 'alert')}
                className="w-full flex items-center justify-between p-3 bg-red-600/30 hover:bg-red-600/40 transition-all"
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🚨</span>
                  <h3 className="text-base font-bold text-white">Alert!</h3>
                </div>
                <span className="text-white text-xl">{expandedCategory === 'alert' ? '−' : '+'}</span>
              </motion.button>

              {/* Alert Subcategories */}
              <AnimatePresence>
                {expandedCategory === 'alert' && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="bg-black/20"
                  >
                    <div className="p-2 space-y-2">
                      {/* ICE */}
                      <button {...iceLongPress} className="w-full flex items-center justify-between p-2.5 bg-blue-600/20 hover:bg-blue-600/30 active:scale-95 border border-blue-500 rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">🧊</span>
                          <div className="text-left">
                            <h4 className="text-sm font-bold text-white">ICE Alert</h4>
                            <p className="text-[10px] text-blue-200">Immigration</p>
                          </div>
                        </div>
                        <span className="text-xs font-bold text-blue-400">60m</span>
                      </button>

                      {/* Police */}
                      <button {...policeLongPress} className="w-full flex items-center justify-between p-2.5 bg-red-600/20 hover:bg-red-600/30 active:scale-95 border border-red-500 rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">🚓</span>
                          <div className="text-left">
                            <h4 className="text-sm font-bold text-white">Police Alert</h4>
                            <p className="text-[10px] text-red-200">Law enforcement</p>
                          </div>
                        </div>
                        <span className="text-xs font-bold text-red-400">5m</span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* FOOD! Category */}
            <div className="border-2 border-orange-500/50 rounded-xl overflow-hidden">
              {/* Food! Header */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setExpandedCategory(expandedCategory === 'food' ? null : 'food')}
                className="w-full flex items-center justify-between p-3 bg-orange-600/30 hover:bg-orange-600/40 transition-all"
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🍞</span>
                  <h3 className="text-base font-bold text-white">Food!</h3>
                </div>
                <span className="text-white text-xl">{expandedCategory === 'food' ? '−' : '+'}</span>
              </motion.button>

              {/* Food Subcategories */}
              <AnimatePresence>
                {expandedCategory === 'food' && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="bg-black/20"
                  >
                    <div className="p-2 space-y-2">
                      {/* Soup Kitchen */}
                      <button {...soupKitchenLongPress} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">🍲</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Soup Kitchen</h4>
                          <p className="text-[10px] text-orange-200">Hot meals</p>
                        </div>
                      </button>

                      {/* BBQ */}
                      <button {...bbqLongPress} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">🍖</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">BBQ</h4>
                          <p className="text-[10px] text-orange-200">Community cook-out</p>
                        </div>
                      </button>

                      {/* Dry Food */}
                      <button {...dryFoodLongPress} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">📦</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Dry Food</h4>
                          <p className="text-[10px] text-orange-200">Pantry items</p>
                        </div>
                      </button>

                      {/* Pick */}
                      <button {...pickLongPress} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">🫐</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Pick</h4>
                          <p className="text-[10px] text-orange-200">Fresh picking</p>
                        </div>
                      </button>

                      {/* Garden */}
                      <button {...gardenLongPress} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">🥬</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Garden</h4>
                          <p className="text-[10px] text-orange-200">Fresh produce</p>
                        </div>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* SHELTER! Category */}
            <div className="border-2 border-cyan-500/50 rounded-xl overflow-hidden">
              {/* Shelter! Header */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setExpandedCategory(expandedCategory === 'shelter' ? null : 'shelter')}
                className="w-full flex items-center justify-between p-3 bg-cyan-600/30 hover:bg-cyan-600/40 transition-all"
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🏠</span>
                  <h3 className="text-base font-bold text-white">Shelter!</h3>
                </div>
                <span className="text-white text-xl">{expandedCategory === 'shelter' ? '−' : '+'}</span>
              </motion.button>

              {/* Shelter Subcategories */}
              <AnimatePresence>
                {expandedCategory === 'shelter' && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="bg-black/20"
                  >
                    <div className="p-2 space-y-2">
                      {/* Couch */}
                      <button {...couchLongPress} className="w-full flex items-center justify-between p-2.5 bg-indigo-500/20 hover:bg-indigo-500/30 active:scale-95 border border-indigo-400 rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">🛏️</span>
                          <div className="text-left">
                            <h4 className="text-sm font-bold text-white">Couch</h4>
                            <p className="text-[10px] text-indigo-200">1 night max</p>
                          </div>
                        </div>
                        <span className="text-xs font-bold text-indigo-400">1N</span>
                      </button>

                      {/* Camping */}
                      <button {...campingLongPress} className="w-full flex items-center justify-between p-2.5 bg-teal-500/20 hover:bg-teal-500/30 active:scale-95 border border-teal-400 rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">⛺</span>
                          <div className="text-left">
                            <h4 className="text-sm font-bold text-white">Camping</h4>
                            <p className="text-[10px] text-teal-200">2 nights max</p>
                          </div>
                        </div>
                        <span className="text-xs font-bold text-teal-400">2N</span>
                      </button>

                      {/* Housing */}
                      <button onClick={() => onClassify('housing')} className="w-full flex items-center gap-2 p-2.5 bg-cyan-500/20 hover:bg-cyan-500/30 active:scale-95 border border-cyan-400 rounded-lg">
                        <span className="text-xl">🏠</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Housing</h4>
                          <p className="text-[10px] text-cyan-200">Long-term shelter</p>
                        </div>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Helper text */}
          <p className="text-xs text-gray-400 mt-3 text-center">
            Tap category to expand • Hold to customize
          </p>

          {/* Cancel button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              // Close modal without classifying
              window.history.back();
            }}
            className="w-full max-w-sm mt-3 py-2.5 bg-gray-700/50 hover:bg-gray-700/70 border border-gray-600 rounded-xl text-white font-semibold text-sm transition-all"
          >
            Cancel
          </motion.button>

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
