/**
 * ClassificationModal - Item categorization UI
 *
 * TECH DEBT (WSP 87 - File Size):
 * --------------------------------
 * Current: ~912 lines | Guideline: 800-1000 | Hard limit: 1500
 *
 * Future refactoring candidates (if exceeds 1200 lines):
 * - Split into CommerceClassificationModal (Free/Discount/Bid) ~400 lines
 * - Split into LibertyClassificationModal (Alert/Food/Shelter) ~450 lines
 * - Keep wrapper that switches based on libertyEnabled prop ~100 lines
 *
 * Decision: Within acceptable range - defer split
 * Audit date: 2025-11-24
 */

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

type ModalShellRenderer = (options: {
  title: string;
  helperText?: string;
  helperTextMargin?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  actionSheets?: React.ReactNode;
  containerClassName?: string;
}) => JSX.Element;

interface ClassificationModalProps {
  isOpen: boolean;
  imageUrl: string;
  libertyEnabled?: boolean; // Determines which classifications to show
  isMapView?: boolean; // Liberty OFF: 5 GotJunk categories; Liberty ON: accordion view
  isSelectionMode?: boolean; // True when selecting preset (long-press toggle) - hides image
  onClassify: (
    classification: ItemClassification,
    discountPercent?: number,
    bidDurationHours?: number,
    stayLimitNights?: number,
    alertTimerMinutes?: number,
    isPermanent?: boolean
  ) => void;
  onCancel?: () => void; // Called when user cancels - discards pending image
}

/**
 * ClassificationModal - Post-capture classification popup
 *
 * GOTJUNK CAMERA (5 options):
 * - 💙 free, 💚 discount, ⚡ bid, 🔄 share, 🔍 wanted
 *
 * LIBERTY CAMERA (accordion):
 * - Stuff!: free/discount/bid/share/wanted
 * - Alert!: ice/police
 * - Food!: soup_kitchen/bbq/dry_food/pick/garden
 * - Shelter!: couch/camping/housing
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
  isSelectionMode = false,
  onClassify,
  onCancel,
}) => {
  // Action sheet state
  const [discountSheetOpen, setDiscountSheetOpen] = useState(false);
  const [bidSheetOpen, setBidSheetOpen] = useState(false);
  const [stayLimitSheetOpen, setStayLimitSheetOpen] = useState(false);
  const [alertTimerSheetOpen, setAlertTimerSheetOpen] = useState(false);
  const [currentStayLimitType, setCurrentStayLimitType] = useState<'couch' | 'camping'>('couch');
  const [currentAlertType, setCurrentAlertType] = useState<'ice' | 'police'>('police');

  // Expandable category state (for accordion Liberty menu)
  const [expandedCategory, setExpandedCategory] = useState<'stuff' | 'alert' | 'food' | 'shelter' | null>(null);

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
  // Action Sheet Handlers
  // ============================================================================

  const handleDiscountSelect = (percent: number) => {
    localStorage.setItem('gotjunk_default_discount', percent.toString());
    if (navigator.vibrate) navigator.vibrate([10, 50, 10]);
    setDiscountPercent(percent);
    setDiscountSheetOpen(false);
    onClassify('discount', percent);
  };

  const handleBidSelect = (hours: number) => {
    localStorage.setItem('gotjunk_default_bid_duration', hours.toString());
    if (navigator.vibrate) navigator.vibrate([10, 50, 10]);
    setBidDurationHours(hours);
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
  // SHARED MODAL SHELL
  // ============================================================================

  const renderModalShell: ModalShellRenderer = ({
    title,
    helperText,
    helperTextMargin = 'mt-2',
    children,
    footer,
    actionSheets,
    containerClassName = 'overflow-y-auto',
  }) => (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={`fixed inset-0 bg-black/90 backdrop-blur-sm flex flex-col items-center justify-center p-6 ${containerClassName}`}
          style={{
            zIndex: Z_LAYERS.modal,
            WebkitTouchCallout: 'none',
            WebkitUserSelect: 'none',
            userSelect: 'none',
          }}
        >
          {/* Preview image - hidden in selection mode */}
          {!isSelectionMode && imageUrl && (
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-full max-w-sm mb-4 rounded-2xl overflow-hidden shadow-2xl"
            >
              <img src={imageUrl} alt="Captured item" className="w-full h-auto" />
            </motion.div>
          )}

          {/* Title */}
          <h2 className="text-xl font-bold text-white mb-3 text-center">{title}</h2>

          {children}

          {/* Helper text */}
          {helperText && (
            <p className={`text-xs text-gray-400 ${helperTextMargin} text-center`}>
              {helperText}
            </p>
          )}

          {footer}
          {actionSheets}
        </motion.div>
      )}
    </AnimatePresence>
  );

  const renderGotJunkList = (variant: 'map' | 'regular') => {
    const containerClass = variant === 'map' ? 'w-full max-w-sm space-y-2 mb-4' : 'w-full max-w-sm space-y-2.5';
    const labelText = variant === 'map' ? 'text-sm' : 'text-base';
    const classes = {
      free: variant === 'map'
        ? 'w-full flex items-center justify-between p-3 bg-blue-500/20 hover:bg-blue-500/30 border-2 border-blue-400 rounded-xl transition-all'
        : 'w-full flex items-center justify-between p-3 bg-blue-500/20 hover:bg-blue-500/30 border-2 border-blue-400 rounded-xl transition-all shadow-lg shadow-blue-500/20',
      discount: variant === 'map'
        ? 'w-full flex items-center justify-between p-3 bg-green-500/20 hover:bg-green-500/30 active:scale-95 border-2 border-green-400 rounded-xl transition-all'
        : 'w-full flex items-center justify-between p-3 bg-green-500/20 hover:bg-green-500/30 active:scale-95 border-2 border-green-400 rounded-xl transition-all shadow-lg shadow-green-500/20',
      bid: variant === 'map'
        ? 'w-full flex items-center justify-between p-3 bg-amber-500/20 hover:bg-amber-500/30 active:scale-95 border-2 border-amber-400 rounded-xl transition-all'
        : 'w-full flex items-center justify-between p-3 bg-amber-500/20 hover:bg-amber-500/30 active:scale-95 border-2 border-amber-400 rounded-xl transition-all shadow-lg shadow-amber-500/20',
      share: variant === 'map'
        ? 'w-full flex items-center justify-between p-3 bg-purple-500/20 hover:bg-purple-500/30 border-2 border-purple-400 rounded-xl transition-all'
        : 'w-full flex items-center justify-between p-3 bg-purple-500/20 hover:bg-purple-500/30 border-2 border-purple-400 rounded-xl transition-all shadow-lg shadow-purple-500/20',
      wanted: variant === 'map'
        ? 'w-full flex items-center justify-between p-3 bg-pink-500/20 hover:bg-pink-500/30 border-2 border-pink-400 rounded-xl transition-all'
        : 'w-full flex items-center justify-between p-3 bg-pink-500/20 hover:bg-pink-500/30 border-2 border-pink-400 rounded-xl transition-all shadow-lg shadow-pink-500/20',
    };

    return (
      <div className={containerClass}>
        {/* Commerce (3) */}
        <div className="mb-1">
          <p className="text-xs font-semibold text-gray-400 mb-1 uppercase tracking-wide">Commerce</p>
        </div>

        {/* Free */}
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => onClassify('free')}
          className={classes.free}
          style={{ touchAction: 'manipulation' }}
        >
          <div className="flex items-center space-x-2.5">
            {variant === 'regular' ? (
              <div className="p-1.5 bg-blue-500 rounded-full">
                <FreeIcon className="w-5 h-5 text-white" />
              </div>
            ) : (
              <span className="text-2xl">💙</span>
            )}
            <div className="text-left">
              <h3 className={`${labelText} font-bold text-white`}>Free</h3>
              {variant === 'regular' && <p className="text-[10px] text-blue-200">Give it away</p>}
            </div>
          </div>
          {variant === 'regular' && <span className="text-lg font-bold text-blue-400">$0</span>}
        </motion.button>

        {/* Discount */}
        <button
          {...discountLongPress}
          className={classes.discount}
          style={{ touchAction: 'manipulation' }}
        >
          <div className="flex items-center space-x-2.5">
            {variant === 'regular' ? (
              <div className="p-1.5 bg-green-500 rounded-full">
                <DiscountIcon className="w-5 h-5 text-white" />
              </div>
            ) : (
              <span className="text-2xl">💚</span>
            )}
            <div className="text-left">
              <h3 className={`${labelText} font-bold text-white`}>Discount</h3>
              {variant === 'regular' && <p className="text-[10px] text-green-200">Sell it fast</p>}
            </div>
          </div>
          <span className="text-xs font-bold text-green-400">
            {variant === 'regular' ? `${discountPercent}% OFF` : `${discountPercent}%`}
          </span>
        </button>

        {/* Bid */}
        <button
          {...bidLongPress}
          className={classes.bid}
          style={{ touchAction: 'manipulation' }}
        >
          <div className="flex items-center space-x-2.5">
            {variant === 'regular' ? (
              <div className="p-1.5 bg-amber-500 rounded-full">
                <BidIcon className="w-5 h-5 text-white" />
              </div>
            ) : (
              <span className="text-2xl">⚡</span>
            )}
            <div className="text-left">
              <h3 className={`${labelText} font-bold text-white`}>Bid</h3>
              {variant === 'regular' && <p className="text-[10px] text-amber-200">Let buyers compete</p>}
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
          className={classes.share}
          style={{ touchAction: 'manipulation' }}
        >
          <div className="flex items-center space-x-2.5">
            <span className="text-2xl">🔄</span>
            <div className="text-left">
              <h3 className={`${labelText} font-bold text-white`}>Share</h3>
              {variant === 'regular' && <p className="text-[10px] text-purple-200">Lend it out</p>}
            </div>
          </div>
        </motion.button>

        {/* Wanted */}
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => onClassify('wanted')}
          className={classes.wanted}
          style={{ touchAction: 'manipulation' }}
        >
          <div className="flex items-center space-x-2.5">
            <span className="text-2xl">🔍</span>
            <div className="text-left">
              <h3 className={`${labelText} font-bold text-white`}>Wanted</h3>
              {variant === 'regular' && <p className="text-[10px] text-pink-200">Looking for this</p>}
            </div>
          </div>
        </motion.button>
      </div>
    );
  };

  // ============================================================================
  // RENDER: MAP VIEW (GotJunk Categories Only - 5 Types)
  // When Liberty Alert is OFF: Only show GotJunk default categories (Free, Discount, Bid, Share, Wanted)
  // When Liberty Alert is ON: Use accordion instead (see LIBERTY CAMERA section)
  // ============================================================================

  if (isMapView && !libertyEnabled) {
    return renderModalShell({
      title: isSelectionMode ? 'Choose Default Category' : 'Select Category (5 Types)',
      helperText: 'Tap to select; hold to customize',
      children: (
        renderGotJunkList('map')
      ),
      actionSheets: (
        <>
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
        </>
      ),
    });
  }

  // ============================================================================
  // RENDER: REGULAR CAMERA (GotJunk Categories: Free, Discount, Bid, Share, Wanted)
  // ============================================================================

  if (!libertyEnabled && !isMapView) {
    return renderModalShell({
      title: isSelectionMode ? 'Choose Default Category' : 'How would you like to list this?',
      helperText: 'Tap to select; hold Discount/Bid to customize',
      helperTextMargin: 'mt-3',
      children: (
        renderGotJunkList('regular')
      ),
      footer: (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onCancel?.()}
          className="w-full max-w-sm mt-3 py-2.5 bg-gray-700/50 hover:bg-gray-700/70 border border-gray-600 rounded-xl text-white font-semibold text-sm transition-all"
        >
          Cancel
        </motion.button>
      ),
      actionSheets: (
        <>
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
        </>
      ),
      containerClassName: "",
    });
  }

  // ============================================================================
  // RENDER: LIBERTY CAMERA (Condensed Categories)
  // ============================================================================

  return renderModalShell({
    title: isSelectionMode ? '🗽 Choose Default Category' : '🗽 Liberty Alert - Select Category',
    helperText: 'Tap category to expand; hold to customize',
    helperTextMargin: 'mt-3',
    children: (
      <>
          {/* Category Selection */}
          {/* Main Categories (Order: Stuff, Alert, Food, Shelter for thumb accessibility) */}
          <div className="w-full max-w-sm space-y-3">
            {/* STUFF! Category (GotJunk) */}
            <div className="border-2 border-gray-500/50 rounded-xl overflow-hidden">
              {/* Stuff! Header */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => setExpandedCategory(expandedCategory === 'stuff' ? null : 'stuff')}
                className="w-full flex items-center justify-between p-3 bg-gray-600/30 hover:bg-gray-600/40 transition-all"
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">📦</span>
                  <h3 className="text-base font-bold text-white">Stuff!</h3>
                </div>
                <span className="text-white text-xl">{expandedCategory === 'stuff' ? '−' : '+'}</span>
              </motion.button>

              {/* Stuff Subcategories (GotJunk) */}
              <AnimatePresence>
                {expandedCategory === 'stuff' && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="bg-black/20"
                  >
                    <div className="p-2 space-y-2">
                      {/* Free */}
                      <button onClick={() => onClassify('free')} className="w-full flex items-center gap-2 p-2.5 bg-blue-500/20 hover:bg-blue-500/30 active:scale-95 border border-blue-400 rounded-lg">
                        <span className="text-xl">💙</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Free</h4>
                          <p className="text-[10px] text-blue-200">Give it away</p>
                        </div>
                      </button>

                      {/* Discount */}
                      <button {...discountLongPress} className="w-full flex items-center justify-between p-2.5 bg-green-500/20 hover:bg-green-500/30 active:scale-95 border border-green-400 rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">💚</span>
                          <div className="text-left">
                            <h4 className="text-sm font-bold text-white">Discount</h4>
                            <p className="text-[10px] text-green-200">Sell it fast</p>
                          </div>
                        </div>
                        <span className="text-xs font-bold text-green-400">{discountPercent}%</span>
                      </button>

                      {/* Bid */}
                      <button {...bidLongPress} className="w-full flex items-center justify-between p-2.5 bg-amber-500/20 hover:bg-amber-500/30 active:scale-95 border border-amber-400 rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">⚡</span>
                          <div className="text-left">
                            <h4 className="text-sm font-bold text-white">Bid</h4>
                            <p className="text-[10px] text-amber-200">Let buyers compete</p>
                          </div>
                        </div>
                        <span className="text-xs font-bold text-amber-400">{bidDurationHours}h</span>
                      </button>

                      {/* Share */}
                      <button onClick={() => onClassify('share')} className="w-full flex items-center gap-2 p-2.5 bg-purple-500/20 hover:bg-purple-500/30 active:scale-95 border border-purple-400 rounded-lg">
                        <span className="text-xl">🔄</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Share</h4>
                          <p className="text-[10px] text-purple-200">Lend it out</p>
                        </div>
                      </button>

                      {/* Wanted */}
                      <button onClick={() => onClassify('wanted')} className="w-full flex items-center gap-2 p-2.5 bg-pink-500/20 hover:bg-pink-500/30 active:scale-95 border border-pink-400 rounded-lg">
                        <span className="text-xl">🔍</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Wanted</h4>
                          <p className="text-[10px] text-pink-200">Looking for this</p>
                        </div>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

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
                      <button onClick={() => onClassify('soup_kitchen')} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">🍲</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Soup Kitchen</h4>
                          <p className="text-[10px] text-orange-200">Hot meals</p>
                        </div>
                      </button>

                      {/* BBQ */}
                      <button onClick={() => onClassify('bbq')} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">🍖</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">BBQ</h4>
                          <p className="text-[10px] text-orange-200">Community cook-out</p>
                        </div>
                      </button>

                      {/* Dry Food */}
                      <button onClick={() => onClassify('dry_food')} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">📦</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Dry Food</h4>
                          <p className="text-[10px] text-orange-200">Pantry items</p>
                        </div>
                      </button>

                      {/* Pick */}
                      <button onClick={() => onClassify('pick')} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
                        <span className="text-xl">🫐</span>
                        <div className="text-left">
                          <h4 className="text-sm font-bold text-white">Pick</h4>
                          <p className="text-[10px] text-orange-200">Fresh picking</p>
                        </div>
                      </button>

                      {/* Garden */}
                      <button onClick={() => onClassify('garden')} className="w-full flex items-center gap-2 p-2.5 bg-orange-500/20 hover:bg-orange-500/30 active:scale-95 border border-orange-400 rounded-lg">
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
      </>
    ),
    footer: (
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => onCancel?.()}
        className="w-full max-w-sm mt-3 py-2.5 bg-gray-700/50 hover:bg-gray-700/70 border border-gray-600 rounded-xl text-white font-semibold text-sm transition-all"
      >
        Cancel
      </motion.button>
    ),
    actionSheets: (
      <>
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
      </>
    ),
  });
};
