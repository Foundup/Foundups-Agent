import React from 'react';

interface IconProps {
  className?: string;
}

/**
 * DiscountIcon - Price tag icon for discount items
 * Green tag - feels like savings
 */
export const DiscountIcon: React.FC<IconProps> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    strokeWidth="2"
    stroke="currentColor"
    fill="none"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Tag shape */}
    <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
    {/* Tag hole */}
    <line x1="7" y1="7" x2="7.01" y2="7" />
  </svg>
);
