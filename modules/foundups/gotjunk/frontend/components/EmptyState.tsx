import React from 'react';
import { motion } from 'framer-motion';
import { BrandLogoIcon } from './icons/BrandLogoIcon';
import { NoCameraIcon } from './icons/NoCameraIcon';

export const EmptyState: React.FC = () => {
    return (
        <motion.div
            className="w-full h-full flex flex-col items-center justify-center p-8 text-center"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
        >
            <div className="flex-grow flex items-center justify-center">
                <BrandLogoIcon className="w-48 h-48 md:w-64 md:h-64" />
            </div>

            <div className="flex-shrink-0 w-full flex flex-col items-center pb-20">
                 <NoCameraIcon className="w-32 h-32 text-gray-100" />
                 <h2 className="text-xl font-bold text-white mt-4">Ready to Capture</h2>
                 <p className="text-gray-300 mt-1 max-w-xs">Tap the camera icon below to take your first photo and start organizing.</p>
            </div>

        </motion.div>
    );
};