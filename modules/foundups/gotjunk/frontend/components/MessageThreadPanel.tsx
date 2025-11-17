import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { messageStore } from '../src/message/messageStore';
import { MessageContextRef, Message } from '../src/message/types';
import { Z_LAYERS } from '../constants/zLayers';

interface MessageThreadPanelProps {
  context: MessageContextRef;
  title?: string;
  subtitle?: string;
  onClose: () => void;
}

const formatTime = (timestamp: number) =>
  new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

export const MessageThreadPanel: React.FC<MessageThreadPanelProps> = ({ context, title, subtitle, onClose }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const refreshMessages = () => {
    messageStore.pruneExpired();
    setMessages(messageStore.getMessages(context));
  };

  // Auto-scroll to newest message (top of reversed list)
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [messages]);

  // Keyboard accessibility: Escape to close
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  useEffect(() => {
    refreshMessages();
  }, [context]);

  const handleSend = () => {
    if (!input.trim()) return;
    messageStore.addMessage({
      context,
      authorId: 'local-user',
      authorDisplayName: 'You',
      text: input.trim(),
    });
    setInput('');
    refreshMessages();
  };

  return (
    <div
      className="fixed inset-0"
      style={{ zIndex: Z_LAYERS.fullscreen + 200 }}
    >
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <motion.div
        className="absolute inset-x-0 bottom-0 bg-gray-950/95 rounded-t-3xl shadow-2xl max-h-[90vh] flex flex-col"
        initial={{ y: '100%' }}
        animate={{ y: 0 }}
        exit={{ y: '100%' }}
        transition={{ type: 'spring', stiffness: 260, damping: 30 }}
      >
        <div className="px-6 pt-5 pb-3 border-b border-white/10 flex items-center justify-between">
          <div>
            <p className="text-white font-semibold text-lg">{title || 'Message Board'}</p>
            {subtitle && <p className="text-white/60 text-sm">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="w-12 h-12 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white text-2xl"
            aria-label="Close message board"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
          {messages.length === 0 && (
            <p className="text-center text-white/60 text-sm">No messages yet. Start the thread below.</p>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className="bg-gray-900/80 rounded-2xl p-3 text-white shadow-lg">
              <div className="flex justify-between text-xs text-white/60">
                <span>{msg.authorDisplayName || 'Anonymous'}</span>
                <span>{formatTime(msg.createdAt)}</span>
              </div>
              <p className="mt-1 text-sm whitespace-pre-wrap">{msg.text}</p>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="px-6 py-4 border-t border-white/10 bg-gray-950/95">
          <div className="flex items-center gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSend();
              }}
              placeholder="Share info with nearby community..."
              className="flex-1 rounded-2xl bg-gray-900/80 text-white px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/70"
            />
            <button
              onClick={handleSend}
              className="w-16 h-12 rounded-2xl bg-blue-600 text-white font-semibold disabled:opacity-50 flex items-center justify-center"
              disabled={!input.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
