import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = 'Delete',
  cancelText = 'Cancel',
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onCancel}
        >
          <motion.div
            className="bg-gray-800 rounded-xl p-6 w-full max-w-sm shadow-lg"
            initial={{ scale: 0.9, y: 20, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.9, y: 20, opacity: 0 }}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            onClick={(e) => e.stopPropagation()}
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="dialog-title"
            aria-describedby="dialog-description"
          >
            <h2 id="dialog-title" className="text-xl font-bold text-white mb-2">{title}</h2>
            <p id="dialog-description" className="text-gray-300 mb-6">{message}</p>
            <div className="flex justify-end gap-3">
              <button
                onClick={onCancel}
                className="px-5 py-2 rounded-md bg-gray-600 hover:bg-gray-500 text-white font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
                aria-label="Cancel deletion"
              >
                {cancelText}
              </button>
              <button
                onClick={onConfirm}
                className="px-5 py-2 rounded-md bg-red-600 hover:bg-red-500 text-white font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-red-400"
                aria-label="Confirm deletion"
              >
                {confirmText}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
