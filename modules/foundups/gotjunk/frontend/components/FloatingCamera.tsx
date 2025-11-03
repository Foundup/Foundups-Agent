import React from 'react';
import { motion } from 'framer-motion';
import { CameraIcon } from './icons/CameraIcon';

interface FloatingCameraProps {
    onClick: () => void;
}

export const FloatingCamera: React.FC<FloatingCameraProps> = ({ onClick }) => {
    return (
        <motion.button
            onClick={onClick}
            className="fixed bottom-6 right-6 z-30 w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center text-white shadow-lg"
            aria-label="Open camera"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            initial={{ scale: 0, y: 100 }}
            animate={{ scale: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
        >
            <CameraIcon className="w-8 h-8"/>
        </motion.button>
    )
}
