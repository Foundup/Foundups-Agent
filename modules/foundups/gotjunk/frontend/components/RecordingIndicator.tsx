import React from 'react';
import { motion } from 'framer-motion';

interface RecordingIndicatorProps {
  countdown: number;
}

export const RecordingIndicator: React.FC<RecordingIndicatorProps> = ({ countdown }) => {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="relative w-40 h-40 flex items-center justify-center">
        <svg className="absolute w-full h-full" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="rgba(255, 255, 255, 0.2)"
            strokeWidth="8"
            fill="transparent"
          />
          <motion.circle
            cx="50"
            cy="50"
            r="45"
            stroke="#ef4444"
            strokeWidth="8"
            fill="transparent"
            strokeLinecap="round"
            transform="rotate(-90 50 50)"
            strokeDasharray={2 * Math.PI * 45}
            strokeDashoffset={2 * Math.PI * 45 * (1 - (countdown / 10))}
            transition={{ duration: 1, ease: 'linear' }}
          />
        </svg>
        <span className="text-6xl font-bold text-white tabular-nums drop-shadow-lg">
          {countdown}
        </span>
      </div>
    </motion.div>
  );
};
