import React from 'react';
import { motion } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { CameraIcon } from './icons/CameraIcon';
import { MicIcon } from './icons/MicIcon';
import { useLongPress } from '../hooks/useLongPress';
import { Z_LAYERS } from '../constants/zLayers';
import { CaptureMode } from '../App';

interface BottomNavBarProps {
  captureMode: CaptureMode;
  onToggleCaptureMode: () => void;
  onCapture: (blob: Blob) => void;
  onReviewAction: (action: 'keep' | 'delete') => void;
  isRecording: boolean;
  setIsRecording: React.Dispatch<React.SetStateAction<boolean>>;
  countdown: number;
  setCountdown: React.Dispatch<React.SetStateAction<number>>;
  hasReviewItems: boolean;
  onSearchClick?: () => void; // Search functionality
  onCameraClick?: () => void; // Open fullscreen camera
  showCameraOrb?: boolean;
  autoClassifyEnabled?: boolean;
  onToggleAutoClassify?: () => void;
  onLongPressAutoClassify?: () => void; // Long press to select classification
  lastClassification?: { type: string, discountPercent?: number, bidDurationHours?: number } | null;
  libertyEnabled?: boolean; // Liberty Alert mode (show 🗽 badge on camera)
  onLongPressLibertyBadge?: () => void; // Long press 🗽 badge to select Liberty classification
  lastLibertyClassification?: { type: string, stayLimitNights?: number, alertTimerMinutes?: number, isPermanent?: boolean } | null;
}

const buttonVariants = {
    hover: { scale: 1.05 },
    tap: { scale: 0.95 }
};

export const BottomNavBar: React.FC<BottomNavBarProps> = ({
  captureMode,
  onToggleCaptureMode,
  onCapture,
  onReviewAction,
  isRecording,
  setIsRecording,
  setCountdown,
  hasReviewItems,
  onSearchClick = () => console.log('🔍 Search clicked'),
  onCameraClick = () => console.log('📷 Camera clicked'),
  showCameraOrb = true,
  autoClassifyEnabled = false,
  onToggleAutoClassify = () => console.log('🔄 Auto-classify toggled'),
  onLongPressAutoClassify = () => console.log('🔄 Long-press: Select classification'),
  lastClassification = null,
  libertyEnabled = false,
  onLongPressLibertyBadge = () => console.log('🗽 Long-press: Select Liberty classification'),
  lastLibertyClassification = null,
  }) => {
  // Navigation Bar Layout: [<] [>] ... [📷] [Auto: OFF] [🎤]
  // - Left: Swipe left/right thumb toggles (delete/keep)
  // - Right: Camera icon + Auto toggle + AI MIC (voice interface to DAE system)

  // Long-press handler for auto-classify toggle button (ORIGINAL LOGIC - DO NOT MODIFY)
  const autoClassifyLongPress = useLongPress({
    onLongPress: () => {
      console.log('[GotJunk] Long-press detected on auto-classify toggle');
      onLongPressAutoClassify();
    },
    onTap: () => {
      console.log('[GotJunk] Short tap on auto-classify toggle');
      onToggleAutoClassify();
    },
    threshold: 450, // 450ms to trigger long-press
  });

  return (
    <motion.div
        className="fixed bottom-0 left-0 right-0"
        style={{ zIndex: Z_LAYERS.floatingControls }}
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      {/* Main Nav Bar - Layout: [Delete] [Keep] ... [Camera] [Auto] ... [AI MIC] */}
      {/* Compact on mobile (h-20), taller on tablets+ (h-28) */}
      <div
        className="relative flex items-center justify-between w-full h-20 md:h-28 bg-gray-800/80 backdrop-blur-lg border-t border-white/10 max-w-2xl mx-auto rounded-t-2xl shadow-2xl px-4 md:px-6"
        style={{ paddingBottom: 'max(12px, env(safe-area-inset-bottom))' }}
      >

        {/* Left Section: Delete & Keep Arrows - Hidden on phones, visible on tablets+ */}
        <div className="hidden md:flex items-center gap-6">
            <motion.button
                onClick={() => onReviewAction('delete')}
                aria-label="Delete item"
                className="w-16 h-16 rounded-full flex items-center justify-center transition-colors bg-red-600/50 hover:bg-red-600/70 disabled:opacity-50"
                variants={buttonVariants}
                whileTap="tap"
                disabled={!hasReviewItems || isRecording}
            >
                <LeftArrowIcon className="w-7 h-7 text-white" />
            </motion.button>

            <motion.button
                onClick={() => onReviewAction('keep')}
                aria-label="Keep item"
                className="w-16 h-16 rounded-full flex items-center justify-center transition-colors bg-green-500/50 hover:bg-green-500/70 disabled:opacity-50"
                variants={buttonVariants}
                whileTap="tap"
                disabled={!hasReviewItems || isRecording}
            >
                <RightArrowIcon className="w-7 h-7 text-white" />
            </motion.button>
        </div>

        {/* Center Section: Camera Icon + Auto Toggle */}
        {/* On mobile: left-aligned (no arrows), on tablet+: centered */}
        <div className="flex md:absolute md:left-1/2 md:-translate-x-1/2 items-center gap-2 md:gap-4">
          {/* Camera Icon - Smaller on mobile */}
          <motion.button
            onClick={onCameraClick}
            className="w-12 h-12 md:w-16 md:h-16 rounded-full bg-white flex items-center justify-center shadow-lg transition-all hover:scale-105"
            variants={buttonVariants}
            whileTap="tap"
            aria-label="Toggle camera"
          >
            <CameraIcon className="w-5 h-5 md:w-7 md:h-7 text-gray-800" />
          </motion.button>

         {/* Auto-Classify Toggle Button - Compact on mobile */}
         <motion.button
           {...autoClassifyLongPress}
           className={`px-2 py-0.5 md:px-2.5 md:py-1 rounded-full shadow-lg font-semibold text-[10px] md:text-xs transition-all ${
             autoClassifyEnabled
               ? lastClassification?.type === 'free'
                 ? 'bg-blue-600 text-white'      // Free = Blue
                 : lastClassification?.type === 'discount'
                 ? 'bg-green-600 text-white'     // Discount = Green
                 : lastClassification?.type === 'bid'
                 ? 'bg-amber-600 text-white'     // Bid = Amber
                 : 'bg-green-600 text-white'     // Fallback = Green
               : 'bg-red-500/60 text-white'      // OFF = Softer red
           }`}
           variants={buttonVariants}
           whileHover="hover"
           whileTap="tap"
           aria-label={autoClassifyEnabled ? `Auto-classify: ${lastClassification?.type || 'ON'}` : 'Auto-classify: OFF (long-press to select)'}
         >
           <div className="flex items-center gap-1 md:gap-2">
             <div className={`w-1.5 h-1.5 md:w-2 md:h-2 rounded-full ${autoClassifyEnabled ? 'bg-white' : 'bg-white/70'}`} />
             <span>
               {autoClassifyEnabled ? 'ON' : 'OFF'}
             </span>
           </div>
           {autoClassifyEnabled && lastClassification && (
             <div className="text-[9px] md:text-xs opacity-90 mt-0.5">
               {lastClassification.type === 'discount' && `${lastClassification.discountPercent || 75}%`}
               {lastClassification.type === 'bid' && `${lastClassification.bidDurationHours || 48}h`}
               {lastClassification.type === 'free' && 'FREE'}
             </div>
           )}
         </motion.button>
        </div>

        {/* Right Section: AI MIC - Smaller on mobile */}
        <div className="flex items-center">
          {/* AI MIC - Voice interface to DAE system */}
          <motion.button
            onClick={() => console.log('🎤 AI MIC clicked - 012 ↔ 0102 voice interaction')}
            className="w-12 h-12 md:w-16 md:h-16 rounded-full bg-white flex items-center justify-center shadow-lg transition-all hover:scale-105 opacity-50"
            variants={buttonVariants}
            whileTap="tap"
            aria-label="AI Voice Assistant (coming soon)"
            disabled={true}
          >
            <MicIcon className="w-5 h-5 md:w-7 md:h-7 text-gray-800" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};
