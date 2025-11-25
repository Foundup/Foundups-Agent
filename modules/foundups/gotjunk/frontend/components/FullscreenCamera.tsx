import React, { useRef, useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, CameraHandle } from './Camera';
import { CaptureMode } from '../App';
import { Z_LAYERS } from '../constants/zLayers';
import { useLongPress } from '../hooks/useLongPress';

const VIDEO_RECORDING_MAX_SECONDS = 10;

interface FullscreenCameraProps {
  isOpen: boolean;
  onCapture: (blob: Blob) => void;
  onClose: () => void;
  captureMode?: CaptureMode;
  libertyEnabled?: boolean;
}

/**
 * FullscreenCamera - Expands to cover entire screen with tap/hold capture
 *
 * Capture Modes:
 * - TAP: Short tap → take photo (JPEG)
 * - HOLD: Long press (450ms+) → record video (WebM, max 10 seconds)
 *
 * Flow:
 * 1. Camera icon clicked in nav bar
 * 2. This component animates to fullscreen
 * 3. User sees live camera feed
 * 4. User taps (photo) or holds (video) anywhere on screen
 * 5. Captured media → onCapture callback (Blob)
 * 6. Component stays open - user classifies or continues capturing
 *
 * Uses: useLongPress hook (extended with onLongPressRelease for video)
 */
export const FullscreenCamera: React.FC<FullscreenCameraProps> = ({
  isOpen,
  onCapture,
  onClose,
  captureMode = 'photo',
  libertyEnabled = false,
}) => {
  const cameraRef = useRef<CameraHandle>(null);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const captureLockRef = useRef<boolean>(false);

  // Video recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingProgress, setRecordingProgress] = useState(0);
  const recordingTimerRef = useRef<number | null>(null);
  const progressIntervalRef = useRef<number | null>(null);

  // Shutter flash state
  const [showShutterFlash, setShowShutterFlash] = useState(false);

  // Initialize camera when component opens, cleanup when closed
  useEffect(() => {
    if (isOpen) {
      setIsCameraReady(true);
    } else {
      // Reset camera state when closing to ensure clean reinitialization
      setIsCameraReady(false);
      captureLockRef.current = false;
      setIsRecording(false);
      setRecordingProgress(0);
      // Clear all timers
      if (recordingTimerRef.current) clearTimeout(recordingTimerRef.current);
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    }
  }, [isOpen]);

  // Stop recording helper
  const stopRecording = useCallback(() => {
    console.log('[FullscreenCamera] Stopping video recording');
    cameraRef.current?.stopRecording();
    setIsRecording(false);
    setRecordingProgress(0);
    if (recordingTimerRef.current) clearTimeout(recordingTimerRef.current);
    if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    // Haptic feedback
    if (navigator.vibrate) navigator.vibrate([20, 50, 20]);
  }, []);

  // Start recording helper
  const startRecording = useCallback(() => {
    console.log('[FullscreenCamera] Starting video recording (max 10s)');
    cameraRef.current?.startRecording();
    setIsRecording(true);
    setRecordingProgress(0);

    // Haptic feedback
    if (navigator.vibrate) navigator.vibrate(30);

    // Progress bar update every 100ms
    const startTime = Date.now();
    progressIntervalRef.current = window.setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min((elapsed / (VIDEO_RECORDING_MAX_SECONDS * 1000)) * 100, 100);
      setRecordingProgress(progress);
    }, 100);

    // Auto-stop after max duration
    recordingTimerRef.current = window.setTimeout(() => {
      console.log('[FullscreenCamera] Auto-stopping after 10 seconds');
      stopRecording();
    }, VIDEO_RECORDING_MAX_SECONDS * 1000);
  }, [stopRecording]);

  // Take photo helper
  const takePhoto = useCallback(() => {
    if (captureLockRef.current) {
      console.log('[FullscreenCamera] Capture blocked - lock active');
      return;
    }
    captureLockRef.current = true;

    // Trigger shutter flash animation
    setShowShutterFlash(true);
    setTimeout(() => setShowShutterFlash(false), 200);

    // Haptic feedback
    if (navigator.vibrate) navigator.vibrate(10);

    cameraRef.current?.takePhoto();
    setTimeout(() => {
      captureLockRef.current = false;
    }, 500);
  }, []);

  // Use existing useLongPress hook (extended with onLongPressRelease)
  const longPressHandlers = useLongPress({
    onTap: takePhoto,
    onLongPress: startRecording,
    onLongPressRelease: () => {
      if (isRecording) {
        stopRecording();
      }
    },
    threshold: 450,
  });

  const handleCaptureComplete = (blob: Blob) => {
    console.log('[FullscreenCamera] Media captured, size:', blob.size);
    onCapture(blob);
    // Camera stays open - user closes via nav bar camera icon toggle or X button
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 bg-black"
          style={{
            zIndex: Z_LAYERS.fullscreenCamera,
            touchAction: 'manipulation', // Prevent pinch-to-zoom affecting UI
          }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.5 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          {...longPressHandlers}
        >
          {/* Camera Feed - Full screen */}
          <div className="absolute inset-0">
            {isCameraReady && (
              <Camera
                ref={cameraRef}
                onCapture={handleCaptureComplete}
                captureMode={captureMode}
                fullscreen={true}
              />
            )}
          </div>

          {/* Shutter Flash - White flash overlay when photo taken */}
          <AnimatePresence>
            {showShutterFlash && (
              <motion.div
                className="absolute inset-0 bg-white pointer-events-none"
                initial={{ opacity: 0.9 }}
                animate={{ opacity: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
              />
            )}
          </AnimatePresence>

          {/* Recording Indicator - Top of screen */}
          <AnimatePresence>
            {isRecording && (
              <motion.div
                className="absolute top-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center gap-2"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {/* Recording badge */}
                <div className="flex items-center gap-2 px-4 py-2 bg-red-600/90 rounded-full backdrop-blur-md">
                  <div className="w-3 h-3 rounded-full bg-white animate-pulse" />
                  <span className="text-white font-semibold text-sm">REC</span>
                  <span className="text-white/80 text-xs">
                    {Math.ceil((VIDEO_RECORDING_MAX_SECONDS * (100 - recordingProgress)) / 100)}s
                  </span>
                </div>
                {/* Progress bar */}
                <div className="w-48 h-1.5 bg-white/30 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-red-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${recordingProgress}%` }}
                    transition={{ duration: 0.1 }}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Tap to Capture Hint - Hidden while recording */}
          {!isRecording && (
            <motion.div
              className="absolute bottom-32 left-1/2 transform -translate-x-1/2 px-6 py-3 bg-black/60 rounded-full backdrop-blur-md"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <p className="text-white text-sm font-semibold text-center">
                Tap for photo • Hold for video {libertyEnabled && '🗽'}
              </p>
            </motion.div>
          )}

          {/* Release hint while recording */}
          {isRecording && (
            <motion.div
              className="absolute bottom-32 left-1/2 transform -translate-x-1/2 px-6 py-3 bg-red-600/60 rounded-full backdrop-blur-md"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <p className="text-white text-sm font-semibold text-center">
                Release to stop recording
              </p>
            </motion.div>
          )}

          {/* Close button */}
          <motion.button
            className="absolute top-8 right-8 p-3 rounded-full bg-black/60 hover:bg-black/80 backdrop-blur-md"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onPointerDown={(e) => e.stopPropagation()}
            onClick={(e) => {
              e.stopPropagation(); // Prevent triggering capture
              if (isRecording) stopRecording(); // Stop recording if active
              onClose();
            }}
          >
            <span className="text-white text-2xl">✕</span>
          </motion.button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
