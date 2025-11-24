import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, CameraHandle } from './Camera';
import { CaptureMode } from '../App';
import { Z_LAYERS } from '../constants/zLayers';

interface FullscreenCameraProps {
  isOpen: boolean;
  onCapture: (blob: Blob) => void;
  onClose: () => void;
  captureMode?: CaptureMode;
  libertyEnabled?: boolean;
}

/**
 * FullscreenCamera - Expands to cover entire screen with tap-to-capture
 *
 * Flow:
 * 1. Camera icon clicked in nav bar
 * 2. This component animates to fullscreen
 * 3. User sees live camera feed
 * 4. User taps anywhere on screen to capture
 * 5. Photo captured → onCapture callback
 * 6. Component closes → ClassificationModal appears
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

  // Initialize camera when component opens, cleanup when closed
  useEffect(() => {
    if (isOpen) {
      setIsCameraReady(true);
    } else {
      // Reset camera state when closing to ensure clean reinitialization
      setIsCameraReady(false);
      captureLockRef.current = false;
    }
  }, [isOpen]);

  const handleTapToCapture = () => {
    // Prevent double-capture
    if (captureLockRef.current) {
      console.log('[FullscreenCamera] Capture blocked - lock active');
      return;
    }

    captureLockRef.current = true;

    // Take photo
    cameraRef.current?.takePhoto();

    // Release lock after 500ms
    setTimeout(() => {
      captureLockRef.current = false;
    }, 500);
  };

  const handleCaptureComplete = (blob: Blob) => {
    console.log('[FullscreenCamera] Photo captured, size:', blob.size);
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
          onClick={handleTapToCapture}
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

          {/* Tap to Capture Hint */}
          <motion.div
            className="absolute bottom-32 left-1/2 transform -translate-x-1/2 px-6 py-3 bg-black/60 rounded-full backdrop-blur-md"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <p className="text-white text-sm font-semibold text-center">
              Tap anywhere to capture {libertyEnabled && '🗽'}
            </p>
          </motion.div>

          {/* Close button */}
          <motion.button
            className="absolute top-8 right-8 p-3 rounded-full bg-black/60 hover:bg-black/80 backdrop-blur-md"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={(e) => {
              e.stopPropagation(); // Prevent triggering capture
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
