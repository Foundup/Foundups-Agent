import React from 'react';
import { ItemClassification } from '../types';
import { FreeIcon } from './icons/FreeIcon';
import { DiscountIcon } from './icons/DiscountIcon';
import { BidIcon } from './icons/BidIcon';

interface ClassificationBadgeProps {
  classification: ItemClassification;
  price?: number;
}

/**
 * ClassificationBadge - Small icon overlay for grid thumbnails
 * Shows classification type and price/status
 */
export const ClassificationBadge: React.FC<ClassificationBadgeProps> = ({
  classification,
  price,
}) => {
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
      label: price ? `$${price}` : '75% OFF',
    },
    bid: {
      icon: BidIcon,
      bgColor: 'bg-amber-500',
      textColor: 'text-amber-500',
      label: price ? `$${price}` : 'BID',
    },
  };

  const { icon: Icon, bgColor, textColor, label } = config[classification];

  return (
    <div className="absolute top-2 left-2 z-10 flex items-center space-x-1 bg-black/70 backdrop-blur-sm rounded-full px-2 py-1 shadow-lg">
      {/* Icon */}
      <div className={`p-1 ${bgColor} rounded-full`}>
        <Icon className="w-3 h-3 text-white" />
      </div>
      {/* Label */}
      <span className={`text-xs font-bold ${textColor}`}>{label}</span>
    </div>
  );
};
