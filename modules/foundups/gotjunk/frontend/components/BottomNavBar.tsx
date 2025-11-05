
import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { PhotoIcon } from './icons/PhotoIcon';
import { VideoIcon } from './icons/VideoIcon';
import { Camera, CameraHandle } from './Camera';
import { CaptureMode } from '../App';
import { SearchIcon } from './icons/SearchIcon';
import { MicIcon } from './icons/MicIcon';

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
}) => {
  const cameraRef = useRef<CameraHandle>(null);
  const pressTimerRef = useRef<number | null>(null);
  const countdownIntervalRef = useRef<number | null>(null);
  const stopTimeoutRef = useRef<number | null>(null);
  const momentaryRecordingRef = useRef<boolean>(false);

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
        if (captureMode === 'photo') {
            cameraRef.current?.takePhoto();
        } else if (captureMode === 'video') {
            startRecording(false);
        }
    }
  };

  return (
    <motion.div
        className="fixed bottom-0 left-0 right-0 z-50"
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      {/* Search Bar - positioned above nav bar, to the right of camera */}
      <div className="relative max-w-2xl mx-auto mb-2 px-6">
        <div className="absolute left-[280px] bottom-0">
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
              className="w-96 pl-12 pr-4 py-2.5 bg-gray-800/90 border-2 border-white/30 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/70 focus:border-blue-500/70 text-sm backdrop-blur-lg shadow-lg"
            />
          </div>
        </div>
      </div>

      {/* Main Nav Bar */}
      <div
        className="relative flex justify-between items-end w-full h-28 bg-gray-800/80 backdrop-blur-lg border-t border-white/10 max-w-2xl mx-auto rounded-t-2xl shadow-2xl px-6 pb-4"
        style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
      >

        {/* Left Section: Arrows + Camera */}
        <div className="flex items-end space-x-8 pb-2">
            {/* Navigation Arrows */}
            <div className="flex items-center space-x-6 pb-4">
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

            {/* Camera Orb with Photo/Video Toggle */}
            <div className="relative flex flex-col items-center pb-3">
                {/* Main capture button with live preview - 5% bigger (105px) */}
                <div
                  className="w-[105px] h-[105px] p-1 bg-gray-800 rounded-full shadow-2xl cursor-pointer mb-2"
                  onMouseDown={handlePressStart}
                  onMouseUp={handlePressEnd}
                  onTouchStart={handlePressStart}
                  onTouchEnd={handlePressEnd}
                >
                     <Camera ref={cameraRef} onCapture={onCapture} captureMode={captureMode} />
                </div>
                {/* Photo/Video Toggle */}
                <div className="flex items-center justify-center space-x-4 bg-black/30 px-3 py-1.5 rounded-full">
                    <button
                      onClick={onToggleCaptureMode}
                      className={`transition-colors ${captureMode === 'photo' && !momentaryRecordingRef.current ? 'text-white' : 'text-gray-500'}`}
                      aria-label="Photo mode"
                      disabled={isRecording}
                    >
                        <PhotoIcon className="w-6 h-6" />
                    </button>
                     <button
                      onClick={onToggleCaptureMode}
                      className={`transition-colors ${captureMode === 'video' || momentaryRecordingRef.current ? 'text-white' : 'text-gray-500'}`}
                      aria-label="Video mode"
                      disabled={isRecording}
                    >
                        <VideoIcon className="w-6 h-6" />
                    </button>
                </div>
            </div>
        </div>
      </div>
    </motion.div>
  );
};
