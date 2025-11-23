import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';

interface VoiceInputOverlayProps {
  isOpen: boolean;
  initialText: string;
  onSend: (text: string) => void;
  onClose: () => void;
  placeholder?: string;
}

/**
 * VoiceInputOverlay - Floating input bar for voice transcripts
 *
 * Appears at bottom of screen when nav bar mic captures speech.
 * User can edit the transcript and tap Send, or dismiss with X.
 */
export const VoiceInputOverlay: React.FC<VoiceInputOverlayProps> = ({
  isOpen,
  initialText,
  onSend,
  onClose,
  placeholder = 'Edit your message...',
}) => {
  const [text, setText] = useState(initialText);
  const inputRef = useRef<HTMLInputElement>(null);

  // Update text when initialText changes (new voice input)
  useEffect(() => {
    if (isOpen && initialText) {
      setText(initialText);
      // Focus input when overlay opens
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, initialText]);

  // Clear text when overlay closes
  useEffect(() => {
    if (!isOpen) {
      setText('');
    }
  }, [isOpen]);

  const handleSend = () => {
    if (text.trim()) {
      onSend(text.trim());
      setText('');
      onClose();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed left-0 right-0 px-4 pb-4"
          style={{
            bottom: 'calc(96px + env(safe-area-inset-bottom))', // Above nav bar
            zIndex: Z_LAYERS.modal,
          }}
        >
          <div className="max-w-2xl mx-auto bg-gray-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 p-3">
            <div className="flex items-center gap-2">
              {/* Close button */}
              <button
                onClick={onClose}
                className="w-10 h-10 rounded-xl bg-gray-700/80 hover:bg-gray-600/80 flex items-center justify-center transition-colors"
                aria-label="Dismiss voice input"
              >
                <span className="text-white text-lg">×</span>
              </button>

              {/* Input field */}
              <input
                ref={inputRef}
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                className="flex-1 bg-gray-800/80 text-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/70"
              />

              {/* Send button */}
              <button
                onClick={handleSend}
                disabled={!text.trim()}
                className="px-5 h-10 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
              >
                Send
              </button>
            </div>

            {/* Hint text */}
            <p className="text-xs text-gray-500 text-center mt-2">
              Edit and send, or tap × to dismiss
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
