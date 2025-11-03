import React from 'react';
import { motion } from 'framer-motion';
import { Camera } from './Camera';
import { CaptureMode } from '../App';

interface CameraViewProps {
  onCapture: (blob: Blob) => void;
  onClose: () => void;
  captureMode: CaptureMode;
}

export const CameraView: React.FC<CameraViewProps> = ({ onCapture, onClose, captureMode }) => {
  return (
    <motion.div
      className="fixed inset-0 z-40 bg-black"
      initial={{ y: '100%' }}
      animate={{ y: 0 }}
      exit={{ y: '100%' }}
      transition={{ type: 'tween', ease: 'easeInOut', duration: 0.4 }}
    >
      {/* FIX: Pass captureMode to Camera component. The component requires this prop. */}
      <Camera onCapture={onCapture} captureMode={captureMode} />
      <button 
        onClick={onClose} 
        className="absolute top-4 right-4 bg-black/30 text-white rounded-full w-10 h-10 flex items-center justify-center z-20"
        aria-label="Close camera"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </motion.div>
  );
};