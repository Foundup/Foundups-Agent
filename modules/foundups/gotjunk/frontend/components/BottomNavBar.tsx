
import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { GridIcon } from './icons/GridIcon';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { PhotoIcon } from './icons/PhotoIcon';
import { VideoIcon } from './icons/VideoIcon';
import { Camera, CameraHandle } from './Camera';
import { CaptureMode } from '../App';
import { MapIcon } from './icons/MapIcon';

interface BottomNavBarProps {
  captureMode: CaptureMode;
  onToggleCaptureMode: () => void;
  onCapture: (blob: Blob) => void;
  onReviewAction: (action: 'keep' | 'delete') => void;
  onGalleryClick: () => void;
  onMapClick: () => void;
  isRecording: boolean;
  setIsRecording: React.Dispatch<React.SetStateAction<boolean>>;
  countdown: number;
  setCountdown: React.Dispatch<React.SetStateAction<number>>;
  hasReviewItems: boolean;
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
  onGalleryClick,
  onMapClick,
  isRecording,
  setIsRecording,
  setCountdown,
  hasReviewItems,
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
        className="fixed bottom-0 left-0 right-0 z-30"
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <div 
        className="relative flex justify-between items-center h-28 bg-gray-800/80 backdrop-blur-lg border-t border-white/10 max-w-2xl mx-auto rounded-t-2xl shadow-2xl px-4" 
        style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
      >

        {/* Left: Navigation Arrows */}
        {/* User requested specific colors and spacing. DO NOT CHANGE. */}
        <div className="flex items-center space-x-4">
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

        {/* Center: Capture Control */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
            {/* Main capture button with live preview */}
            <div 
              className="w-[88px] h-[88px] p-1 bg-gray-800 rounded-full -translate-y-16 shadow-2xl cursor-pointer"
              onMouseDown={handlePressStart}
              onMouseUp={handlePressEnd}
              onTouchStart={handlePressStart}
              onTouchEnd={handlePressEnd}
            >
                 <Camera ref={cameraRef} onCapture={onCapture} captureMode={captureMode} />
            </div>
            {/* Photo/Video Toggle */}
            {/* User requested specific vertical positioning. DO NOT CHANGE or REVERT. */}
            {/* User requested specific spacing and icon size. DO NOT CHANGE or REVERT. */}
            <div className="absolute top-9 flex items-center justify-center space-x-5 bg-black/30 p-2 rounded-full">
                <button 
                  onClick={onToggleCaptureMode} 
                  className={`p-2 rounded-full transition-colors ${captureMode === 'photo' && !momentaryRecordingRef.current ? 'text-white' : 'text-gray-500'}`} 
                  aria-label="Photo mode"
                  disabled={isRecording}
                >
                    <PhotoIcon className="w-7 h-7" />
                </button>
                 <button 
                  onClick={onToggleCaptureMode} 
                  className={`p-2 rounded-full transition-colors ${captureMode === 'video' || momentaryRecordingRef.current ? 'text-white' : 'text-gray-500'}`} 
                  aria-label="Video mode"
                  disabled={isRecording}
                >
                    <VideoIcon className="w-7 h-7" />
                </button>
            </div>
        </div>


        {/* Right: Action Buttons */}
        <div className="flex items-center space-x-2">
           <motion.button
              onClick={onMapClick}
              aria-label="Open Map"
              className="p-3 rounded-full flex items-center justify-center text-white transition-colors bg-white/10 hover:bg-white/20"
              variants={buttonVariants}
              whileTap="tap"
            >
              <MapIcon className="w-6 h-6" />
            </motion.button>
            <motion.button
              onClick={onGalleryClick}
              aria-label="Open Gallery"
              className="p-3 rounded-full flex items-center justify-center text-white transition-colors bg-white/10 hover:bg-white/20"
              variants={buttonVariants}
              whileTap="tap"
            >
              <GridIcon className="w-6 h-6" />
            </motion.button>
        </div>
      </div>
    </motion.div>
  );
};
