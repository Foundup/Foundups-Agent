
import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ToastProps {
  message: string;
  show: boolean;
  onClose: () => void;
  duration?: number; // milliseconds
}

export const Toast: React.FC<ToastProps> = ({ message, show, onClose, duration = 4000 }) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [show, onClose, duration]);

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed bottom-32 left-1/2 -translate-x-1/2 z-50 px-6 py-4 bg-gray-900/95 text-white rounded-2xl shadow-2xl max-w-sm mx-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">💡</span>
            <p className="text-sm leading-relaxed flex-1">{message}</p>
            <button
              onClick={onClose}
              className="text-white/60 hover:text-white transition-colors ml-2"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
