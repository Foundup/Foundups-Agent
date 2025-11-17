import React from 'react';
import { motion } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { MicIcon } from './icons/MicIcon';
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
  // All camera orb logic removed - camera now handled by FullscreenCamera component

  return (
    <motion.div
        className="fixed bottom-0 left-0 right-0"
        style={{ zIndex: Z_LAYERS.floatingControls }}
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      {/* Main Nav Bar */}
      <div
        className="relative flex items-center w-full h-28 bg-gray-800/80 backdrop-blur-lg border-t border-white/10 max-w-2xl mx-auto rounded-t-2xl shadow-2xl px-6 pb-4"
        style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
      >

        {/* Left Section: Arrows */}
        <div className="flex items-center space-x-6">
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

        {/* Center Section: Camera Icon */}
        <div className="flex-1 flex justify-center">
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
        </div>

        {/* Right Section: Search Bar */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <button
              onClick={onSearchClick}
              className="absolute left-3 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-white/10 hover:bg-white/20 transition-colors z-10"
              aria-label="Voice search"
            >
              <MicIcon className="w-5 h-5 text-gray-300" />
            </button>
            <input
              type="text"
              placeholder="Search items..."
              onClick={onSearchClick}
              className="w-full pl-12 pr-4 py-2.5 bg-gray-800/90 border-2 border-white/30 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/70 focus:border-blue-500/70 text-sm backdrop-blur-lg shadow-lg"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};
