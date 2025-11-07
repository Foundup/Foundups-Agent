import React, { useRef } from 'react';
import { ItemClassification } from '../types';
import { FreeIcon } from './icons/FreeIcon';
import { DiscountIcon } from './icons/DiscountIcon';
import { BidIcon } from './icons/BidIcon';

interface ClassificationBadgeProps {
  classification: ItemClassification;
  price?: number;
  discountPercent?: number;
  bidDurationHours?: number;
  onClick?: (e: React.MouseEvent) => void; // Tap to re-classify
  onLongPress?: (e: React.TouchEvent | React.MouseEvent) => void; // Long-press to edit options
}

/**
 * ClassificationBadge - Small icon overlay for grid thumbnails
 * Shows classification type and price/status
 * 
 * Gestures:
 * - Tap: Re-classify (Free/Discount/Bid)
 * - Long-press: Edit options (discount % or bid duration)
 */
export const ClassificationBadge: React.FC<ClassificationBadgeProps> = ({
  classification,
  price,
  discountPercent,
  bidDurationHours,
  onClick,
  onLongPress,
}) => {
  const longPressTimerRef = useRef<number | null>(null);
  const longPressTriggeredRef = useRef(false);

  const config = {
    free: {
      icon: FreeIcon,
      bgColor: 'bg-blue-500',
      textColor: 'text-blue-500',
      label: 'FREE',
    },
    discount: {
      icon: DiscountIcon,
      bgColor: 'bg-green-500',
      textColor: 'text-green-500',
      label: price ? `$${price}` : `${discountPercent || 75}% OFF`,
    },
    bid: {
      icon: BidIcon,
      bgColor: 'bg-amber-500',
      textColor: 'text-amber-500',
      label: bidDurationHours ? `${bidDurationHours}h` : 'BID',
    },
  };

  const { icon: Icon, bgColor, textColor, label } = config[classification];

  // Long-press detection (800ms)
  const handleTouchStart = (e: React.TouchEvent) => {
    longPressTriggeredRef.current = false;
    longPressTimerRef.current = window.setTimeout(() => {
      longPressTriggeredRef.current = true;
      if (onLongPress && classification !== 'free') {
        onLongPress(e);
      }
    }, 800);
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
    }
    // If long-press was triggered, don't fire onClick
    if (!longPressTriggeredRef.current && onClick) {
      onClick(e as any);
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    longPressTriggeredRef.current = false;
    longPressTimerRef.current = window.setTimeout(() => {
      longPressTriggeredRef.current = true;
      if (onLongPress && classification !== 'free') {
        onLongPress(e);
      }
    }, 800);
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
    }
    // If long-press was triggered, don't fire onClick
    if (!longPressTriggeredRef.current && onClick) {
      onClick(e);
    }
  };

  return (
    <div
      className="absolute top-2 left-2 z-10 flex items-center space-x-1 bg-black/70 backdrop-blur-sm rounded-full px-2 py-1 shadow-lg cursor-pointer active:scale-95 transition-transform"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
    >
      {/* Icon */}
      <div className={`p-1 ${bgColor} rounded-full`}>
        <Icon className="w-3 h-3 text-white" />
      </div>
      {/* Label */}
      <span className={`text-xs font-bold ${textColor}`}>{label}</span>
    </div>
  );
};
