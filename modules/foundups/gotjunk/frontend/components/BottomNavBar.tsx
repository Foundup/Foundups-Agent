import React from 'react';
import { motion } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
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

  return (
    <motion.div
        className="fixed bottom-0 left-0 right-0"
        style={{ zIndex: Z_LAYERS.floatingControls }}
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      {/* Main Nav Bar - Layout: [Delete] [Keep] ... [Camera] */}
      <div
        className="relative flex items-center justify-between w-full h-28 bg-gray-800/80 backdrop-blur-lg border-t border-white/10 max-w-2xl mx-auto rounded-t-2xl shadow-2xl px-6 pb-4"
        style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
      >
        {/* Left Section: Delete & Keep Arrows */}
        <div className="flex items-center gap-6">
          <motion.button
            onClick={() => onReviewAction('delete')}
            aria-label="Delete item"
            className="p-3 rounded-full transition-colors bg-red-600/50 hover:bg-red-600/70 disabled:opacity-50"
            variants={buttonVariants}
            whileTap="tap"
            disabled={!hasReviewItems || isRecording}
          >
            <LeftArrowIcon className="w-6 h-6 text-white" />
          </motion.button>

          <motion.button
            onClick={() => onReviewAction('keep')}
            aria-label="Keep item"
            className="p-3 rounded-full transition-colors bg-green-500/50 hover:bg-green-500/70 disabled:opacity-50"
            variants={buttonVariants}
            whileTap="tap"
            disabled={!hasReviewItems || isRecording}
          >
            <RightArrowIcon className="w-6 h-6 text-white" />
          </motion.button>
        </div>

        {/* Right Section: Camera Icon + Auto Toggle + AI MIC */}
        <div className="flex items-center gap-3">
          {/* Camera Icon */}
          <motion.button
            onClick={onCameraClick}
            className="p-4 rounded-full bg-white/10 hover:bg-white/20 transition-all"
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            aria-label="Open camera"
          >
            <span className="text-3xl">📷</span>
          </motion.button>

          {/* Auto Toggle - with long-press for category selection */}
          <motion.button
            onClick={onToggleAutoClassify}
            onTouchStart={(e) => {
              e.stopPropagation();
              const timer = setTimeout(() => {
                onLongPressAutoClassify();
              }, 450);
              (e.target as HTMLElement).dataset.timer = timer.toString();
            }}
            onTouchEnd={(e) => {
              const timer = (e.target as HTMLElement).dataset.timer;
              if (timer) clearTimeout(parseInt(timer));
            }}
            className={`px-3 py-2 rounded-full text-xs font-bold transition-all ${
              autoClassifyEnabled
                ? 'bg-green-500/30 border-2 border-green-400 text-green-300'
                : 'bg-gray-700/50 border-2 border-gray-600 text-gray-400'
            }`}
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            aria-label={`Auto-classify ${autoClassifyEnabled ? 'ON' : 'OFF'}`}
          >
            Auto: {autoClassifyEnabled ? 'ON' : 'OFF'}
          </motion.button>

          {/* AI MIC - Voice interface to DAE system (to implement later) */}
          <motion.button
            onClick={() => console.log('🎤 AI MIC clicked - 012 ↔ 0102 voice interaction')}
            className="p-4 rounded-full bg-white/10 hover:bg-white/20 transition-all opacity-50"
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            aria-label="AI Voice Assistant (coming soon)"
            disabled={true}
          >
            <span className="text-3xl">🎤</span>
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};
