import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { Camera, CameraHandle } from './Camera';
import { CaptureMode } from '../App';
import { MicIcon } from './icons/MicIcon';
import { Z_LAYERS } from '../constants/zLayers';

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
}) => {
  const cameraRef = useRef<CameraHandle>(null);
  const pressTimerRef = useRef<number | null>(null);
  const countdownIntervalRef = useRef<number | null>(null);
  const stopTimeoutRef = useRef<number | null>(null);
  const momentaryRecordingRef = useRef<boolean>(false);
  const captureLockRef = useRef<boolean>(false); // Prevents double-capture from touch+mouse events

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
          className="absolute left-1/2 -translate-x-1/2 bottom-32 flex flex-col items-center"
          style={{ zIndex: Z_LAYERS.cameraOrb }}
        >
            {/* Main capture button with live preview - Intelligent scaling: iPhone 11=143px, iPhone 16=149px */}
            <div
              className="p-2 bg-gray-800 rounded-full shadow-2xl cursor-pointer"
              style={{
                width: 'clamp(128px, 16vh, 192px)',
                height: 'clamp(128px, 16vh, 192px)'
              }}
              onMouseDown={handlePressStart}
              onMouseUp={handlePressEnd}
              onTouchStart={handlePressStart}
              onTouchEnd={handlePressEnd}
            >
                 <Camera ref={cameraRef} onCapture={onCapture} captureMode={captureMode} />
            </div>
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
