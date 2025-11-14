import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { Camera, CameraHandle } from './Camera';
import { CaptureMode } from '../App';
import { MicIcon } from './icons/MicIcon';
import { Z_LAYERS } from '../constants/zLayers';
import { useLongPress } from '../hooks/useLongPress';

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
  showCameraOrb = true,
  autoClassifyEnabled = false,
  onToggleAutoClassify = () => console.log('🔄 Auto-classify toggled'),
  onLongPressAutoClassify = () => console.log('🔄 Long-press: Select classification'),
  lastClassification = null,
  libertyEnabled = false,
  onLongPressLibertyBadge = () => console.log('🗽 Long-press: Select Liberty classification'),
  lastLibertyClassification = null,
}) => {
  const cameraRef = useRef<CameraHandle>(null);
  const pressTimerRef = useRef<number | null>(null);
  const countdownIntervalRef = useRef<number | null>(null);
  const stopTimeoutRef = useRef<number | null>(null);
  const momentaryRecordingRef = useRef<boolean>(false);
  const captureLockRef = useRef<boolean>(false); // Prevents double-capture from touch+mouse events
  const [isCameraInitialized, setIsCameraInitialized] = useState(false); // Defer getUserMedia() until user clicks camera

  const stopRecording = () => {
    if (countdownIntervalRef.current) {
      clearInterval(countdownIntervalRef.current);
      countdownIntervalRef.current = null;
    }
    if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
        stopTimeoutRef.current = null;
    }
    
    cameraRef.current?.stopRecording();
    setIsRecording(false);
    
    if (momentaryRecordingRef.current) {
        onToggleCaptureMode();
        momentaryRecordingRef.current = false;
    }
  };

  const startRecording = (isMomentary: boolean) => {
    if (isRecording) return;
    momentaryRecordingRef.current = isMomentary;
    if (isMomentary) {
        onToggleCaptureMode();
    }

    setIsRecording(true);
    setCountdown(10);
    cameraRef.current?.startRecording();
    
    countdownIntervalRef.current = window.setInterval(() => {
        setCountdown(prev => {
            if (prev <= 1) {
                clearInterval(countdownIntervalRef.current!);
                return 0;
            }
            return prev - 1;
        });
    }, 1000);
    
    stopTimeoutRef.current = window.setTimeout(stopRecording, 10000);
  };

  const handlePressStart = () => {
    // Initialize camera on first press (defers getUserMedia() until user actually uses camera)
    if (!isCameraInitialized) {
      setIsCameraInitialized(true);
      console.log('[GotJunk] Camera initialized on first press');
    }

    if (isRecording) return;
    if (captureMode === 'photo') {
        pressTimerRef.current = window.setTimeout(() => startRecording(true), 250);
    }
  };

  const handlePressEnd = () => {
    if (pressTimerRef.current) {
        clearTimeout(pressTimerRef.current);
        pressTimerRef.current = null;
    }

    if (momentaryRecordingRef.current) {
        stopRecording();
    } else if (!isRecording) {
        // Capture lock prevents double-fire from touch+mouse events
        if (captureLockRef.current) {
          console.log('[GotJunk] Capture blocked - lock active');
          return;
        }

        captureLockRef.current = true;

        if (captureMode === 'photo') {
            cameraRef.current?.takePhoto();
        } else if (captureMode === 'video') {
            startRecording(false);
        }

        // Release lock after 500ms to allow next capture
        setTimeout(() => {
          captureLockRef.current = false;
        }, 500);
    }
  };

  // Long-press handler for auto-classify toggle button
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

  // Long-press handler for Liberty badge
  const libertyBadgeLongPress = useLongPress({
    onLongPress: () => {
      console.log('[GotJunk] Long-press detected on Liberty badge');
      onLongPressLibertyBadge();
    },
    onTap: () => {
      console.log('[GotJunk] Short tap on Liberty badge (no action)');
      // No action on short tap - badge is just visual indicator with long-press selector
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
      {/* Camera Orb - Floating above nav bar */}
      {showCameraOrb && (
        <div
          className="absolute bottom-32 flex flex-row items-center gap-2"
          style={{
            zIndex: Z_LAYERS.cameraOrb,
            left: '50%',
            transform: 'translateX(-50%)'
          }}
        >
            {/* Main capture button with live preview - Intelligent scaling: iPhone 11=143px, iPhone 16=149px */}
            <div
              className="relative p-2 bg-gray-800 rounded-full shadow-2xl cursor-pointer"
              style={{
                width: 'clamp(147px, 18.4vh, 221px)', // 15% bigger: 128*1.15=147, 192*1.15=221
                height: 'clamp(147px, 18.4vh, 221px)',
                aspectRatio: '1 / 1' // Ensure perfect circle
              }}
              onMouseDown={handlePressStart}
              onMouseUp={handlePressEnd}
              onTouchStart={handlePressStart}
              onTouchEnd={handlePressEnd}
            >
                 {/* Defer Camera mount until first press (saves 200-500ms on app load) */}
                 {isCameraInitialized && <Camera ref={cameraRef} onCapture={onCapture} captureMode={captureMode} />}

                 {/* Liberty Alert Badge - Long-press to select classification (PRE-SELECTION) */}
                 {libertyEnabled && (
                   <motion.div
                     {...libertyBadgeLongPress}
                     className={`absolute -top-1 -right-1 rounded-full flex items-center justify-center shadow-lg border-2 cursor-pointer ${
                       lastLibertyClassification
                         ? 'bg-blue-600 border-white w-14 h-10 px-2' // Expanded when classification selected
                         : 'bg-blue-600/70 border-white w-10 h-10'    // Regular size when no classification
                     }`}
                     initial={{ scale: 0 }}
                     animate={{ scale: 1 }}
                     transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                     whileHover={{ scale: 1.1 }}
                     whileTap={{ scale: 0.95 }}
                     aria-label={lastLibertyClassification ? `Liberty: ${lastLibertyClassification.type}` : 'Liberty mode (long-press to select)'}
                   >
                     <span className="text-2xl">🗽</span>
                     {lastLibertyClassification && (
                       <span className="text-xs font-bold text-white ml-1">
                         {lastLibertyClassification.type === 'food' && '🍞'}
                         {lastLibertyClassification.type === 'couch' && '🛏️'}
                         {lastLibertyClassification.type === 'camping' && '⛺'}
                         {lastLibertyClassification.type === 'housing' && '🏠'}
                         {lastLibertyClassification.type === 'ice' && '🧊'}
                         {lastLibertyClassification.type === 'police' && '🚓'}
                       </span>
                     )}
                   </motion.div>
                 )}
            </div>

            {/* Auto-Classify Toggle Button - Moved to RIGHT of orb to prevent accidental triggers */}
            <motion.button
              {...autoClassifyLongPress}
              className={`px-3 py-1.5 rounded-full shadow-lg font-semibold text-xs transition-all ${
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
              style={{
                marginTop: '10px'    // 10px down
              }}
              variants={buttonVariants}
              whileHover="hover"
              whileTap="tap"
              aria-label={autoClassifyEnabled ? `Auto-classify: ${lastClassification?.type || 'ON'}` : 'Auto-classify: OFF (long-press to select)'}
            >
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${autoClassifyEnabled ? 'bg-white' : 'bg-white/70'}`} />
                <span>
                  Auto: {autoClassifyEnabled ? 'ON' : 'OFF'}
                </span>
              </div>
              {autoClassifyEnabled && lastClassification && (
                <div className="text-xs opacity-90 mt-0.5">
                  {lastClassification.type === 'discount' && `${lastClassification.discountPercent || 75}% OFF`}
                  {lastClassification.type === 'bid' && `${lastClassification.bidDurationHours || 48}h`}
                  {lastClassification.type === 'free' && 'FREE'}
                </div>
              )}
            </motion.button>
        </div>
      )}

      {/* Main Nav Bar */}
      <div
        className="relative flex justify-between items-center w-full h-28 bg-gray-800/80 backdrop-blur-lg border-t border-white/10 max-w-2xl mx-auto rounded-t-2xl shadow-2xl px-6 pb-4"
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

        {/* Right Section: Search Bar */}
        <div className="flex-1 max-w-md ml-4">
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
