import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Z_LAYERS } from '../constants/zLayers';
import type { ItemClassification } from '../types';

interface MapFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (filters: ItemClassification[]) => void;
}

// LocalStorage key for filter persistence
const FILTER_STORAGE_KEY = 'gotjunk_map_filters';

/**
 * MapFilterModal - Filter map items by 11 classification types
 * Organized into 4 groups: Commerce (3), Share Economy (2), Mutual Aid (4), Alerts (2)
 * Filters persist across sessions via localStorage
 */
export const MapFilterModal: React.FC<MapFilterModalProps> = ({
  isOpen,
  onClose,
  onApply,
}) => {
  // Load initial filters from localStorage or default to all enabled
  const [filters, setFilters] = useState<Record<ItemClassification, boolean>>(() => {
    const stored = localStorage.getItem(FILTER_STORAGE_KEY);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch {
        // Fall through to default
      }
    }
    // Default: all filters enabled
    return {
      free: true,
      discount: true,
      bid: true,
      share: true,
      wanted: true,
      food: true,
      couch: true,
      camping: true,
      housing: true,
      ice: true,
      police: true,
    };
  });

  const toggleFilter = (classification: ItemClassification) => {
    setFilters(prev => ({
      ...prev,
      [classification]: !prev[classification],
    }));
  };

  const handleSelectAll = () => {
    setFilters({
      free: true,
      discount: true,
      bid: true,
      share: true,
      wanted: true,
      food: true,
      couch: true,
      camping: true,
      housing: true,
      ice: true,
      police: true,
    });
  };

  const handleClearAll = () => {
    setFilters({
      free: false,
      discount: false,
      bid: false,
      share: false,
      wanted: false,
      food: false,
      couch: false,
      camping: false,
      housing: false,
      ice: false,
      police: false,
    });
  };

  const handleApply = () => {
    // Save to localStorage
    localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(filters));

    // Return enabled filters
    const enabledFilters = (Object.keys(filters) as ItemClassification[]).filter(
      key => filters[key]
    );
    onApply(enabledFilters);
    onClose();
  };

  // Prevent background scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            style={{ zIndex: Z_LAYERS.modal }}
          />

          {/* Modal */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 bg-gray-900 rounded-t-3xl shadow-2xl p-6 max-h-[85vh] overflow-y-auto"
            style={{ zIndex: Z_LAYERS.modal + 1 }}
          >
            {/* Handle bar */}
            <div className="w-12 h-1.5 bg-gray-700 rounded-full mx-auto mb-6" />

            {/* Title */}
            <h3 className="text-xl font-bold text-white mb-2 text-center">
              🗺️ Map Filters
            </h3>
            <p className="text-sm text-gray-400 mb-6 text-center">
              Show/hide items by classification type
            </p>

            {/* Filter Groups */}
            <div className="space-y-6">
              {/* COMMERCE (3) */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">
                  Commerce
                </h4>
                <div className="space-y-2">
                  <FilterToggle
                    emoji="💙"
                    label="Free"
                    enabled={filters.free}
                    onToggle={() => toggleFilter('free')}
                  />
                  <FilterToggle
                    emoji="💚"
                    label="Discount"
                    enabled={filters.discount}
                    onToggle={() => toggleFilter('discount')}
                  />
                  <FilterToggle
                    emoji="⚡"
                    label="Bid"
                    enabled={filters.bid}
                    onToggle={() => toggleFilter('bid')}
                  />
                </div>
              </div>

              {/* SHARE ECONOMY (2) */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">
                  Share Economy
                </h4>
                <div className="space-y-2">
                  <FilterToggle
                    emoji="🔄"
                    label="Share"
                    enabled={filters.share}
                    onToggle={() => toggleFilter('share')}
                  />
                  <FilterToggle
                    emoji="🔍"
                    label="Wanted"
                    enabled={filters.wanted}
                    onToggle={() => toggleFilter('wanted')}
                  />
                </div>
              </div>

              {/* MUTUAL AID (4) */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">
                  Mutual Aid
                </h4>
                <div className="space-y-2">
                  <FilterToggle
                    emoji="🍞"
                    label="Food"
                    enabled={filters.food}
                    onToggle={() => toggleFilter('food')}
                  />
                  <FilterToggle
                    emoji="🛏️"
                    label="Couch Surfing"
                    subtitle="1 night max"
                    enabled={filters.couch}
                    onToggle={() => toggleFilter('couch')}
                  />
                  <FilterToggle
                    emoji="⛺"
                    label="Camping"
                    subtitle="2 nights default"
                    enabled={filters.camping}
                    onToggle={() => toggleFilter('camping')}
                  />
                  <FilterToggle
                    emoji="🏠"
                    label="Housing"
                    enabled={filters.housing}
                    onToggle={() => toggleFilter('housing')}
                  />
                </div>
              </div>

              {/* ALERTS - TIME SENSITIVE (2) */}
              <div>
                <h4 className="text-sm font-semibold text-red-400 mb-3 uppercase tracking-wide">
                  Alerts — Time Sensitive
                </h4>
                <div className="space-y-2">
                  <FilterToggle
                    emoji="🧊"
                    label="ICE Alert"
                    subtitle="60min default"
                    enabled={filters.ice}
                    onToggle={() => toggleFilter('ice')}
                  />
                  <FilterToggle
                    emoji="🚓"
                    label="Police Alert"
                    subtitle="5min default"
                    enabled={filters.police}
                    onToggle={() => toggleFilter('police')}
                  />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 space-y-3">
              <div className="flex gap-3">
                <button
                  onClick={handleSelectAll}
                  className="flex-1 px-4 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl transition-colors"
                >
                  Select All
                </button>
                <button
                  onClick={handleClearAll}
                  className="flex-1 px-4 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl transition-colors"
                >
                  Clear All
                </button>
              </div>
              <button
                onClick={handleApply}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-colors"
              >
                Apply Filters
              </button>
              <button
                onClick={onClose}
                className="w-full px-4 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl transition-colors"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

// Filter toggle component
interface FilterToggleProps {
  emoji: string;
  label: string;
  subtitle?: string;
  enabled: boolean;
  onToggle: () => void;
}

const FilterToggle: React.FC<FilterToggleProps> = ({
  emoji,
  label,
  subtitle,
  enabled,
  onToggle,
}) => {
  return (
    <button
      onClick={onToggle}
      className={`w-full p-4 rounded-xl border-2 transition-all ${
        enabled
          ? 'bg-blue-500/30 border-blue-400 shadow-lg'
          : 'bg-gray-800 border-gray-700'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{emoji}</span>
          <div className="text-left">
            <div className="text-lg font-semibold text-white">{label}</div>
            {subtitle && <div className="text-xs text-gray-400">{subtitle}</div>}
          </div>
        </div>
        {enabled && <span className="text-blue-400 text-xl">✓</span>}
      </div>
    </button>
  );
};
