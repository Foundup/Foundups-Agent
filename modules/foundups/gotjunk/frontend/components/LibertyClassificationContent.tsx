import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ItemClassification } from '../types';
import { useLongPress } from '../hooks/useLongPress';
import { ActionSheetStayLimit } from './ActionSheetStayLimit';
import { ActionSheetAlertTimer } from './ActionSheetAlertTimer';

type ModalShellRenderer = (options: {
  title: string;
  helperText?: string;
  helperTextMargin?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  actionSheets?: React.ReactNode;
  containerClassName?: string;
}) => JSX.Element;

interface LibertyClassificationContentProps {
  renderModalShell: ModalShellRenderer;
  onClassify: (
    classification: ItemClassification,
    discountPercent?: number,
    bidDurationHours?: number,
    stayLimitNights?: number,
    alertTimerMinutes?: number,
    isPermanent?: boolean
  ) => void;
  onCancel?: () => void;
  discountLongPress: ReturnType<typeof useLongPress>;
  bidLongPress: ReturnType<typeof useLongPress>;
  discountPercent: number;
  bidDurationHours: number;
}

type ExpandedCategory = 'stuff' | 'alert' | 'food' | 'shelter' | null;

export const LibertyClassificationContent: React.FC<LibertyClassificationContentProps> = ({
  renderModalShell,
  onClassify,
  onCancel,
  discountLongPress,
  bidLongPress,
  discountPercent,
  bidDurationHours,
}) => {
  const [stayLimitSheetOpen, setStayLimitSheetOpen] = useState(false);
  const [alertTimerSheetOpen, setAlertTimerSheetOpen] = useState(false);
  const [currentStayLimitType, setCurrentStayLimitType] = useState<'couch' | 'camping'>('couch');
  const [currentAlertType, setCurrentAlertType] = useState<'ice' | 'police'>('police');
  const [expandedCategory, setExpandedCategory] = useState<ExpandedCategory>(null);

  // Long press handlers (Liberty only)
  const couchLongPress = useLongPress({
    onLongPress: () => {
      setCurrentStayLimitType('couch');
      setStayLimitSheetOpen(true);
    },
    onTap: () => onClassify('couch', undefined, undefined, 1),
    threshold: 450,
  });

  const campingLongPress = useLongPress({
    onLongPress: () => {
      setCurrentStayLimitType('camping');
      setStayLimitSheetOpen(true);
    },
    onTap: () => onClassify('camping', undefined, undefined, 2),
    threshold: 450,
  });

  const iceLongPress = useLongPress({
    onLongPress: () => {
      setCurrentAlertType('ice');
      setAlertTimerSheetOpen(true);
    },
    onTap: () => onClassify('ice', undefined, undefined, undefined, 60),
    threshold: 450,
  });

  const policeLongPress = useLongPress({
    onLongPress: () => {
      setCurrentAlertType('police');
      setAlertTimerSheetOpen(true);
    },
    onTap: () => onClassify('police', undefined, undefined, undefined, 5),
    threshold: 450,
  });

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

  return renderModalShell({
    title: '🗽 Liberty Alert - Select Category',
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
