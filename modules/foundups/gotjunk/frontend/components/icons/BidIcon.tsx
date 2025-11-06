import React from 'react';

interface IconProps {
  className?: string;
}

/**
 * BidIcon - Gavel icon for auction/bid items
 * Amber/orange - feels competitive
 */
export const BidIcon: React.FC<IconProps> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    strokeWidth="2"
    stroke="currentColor"
    fill="none"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Gavel head */}
    <path d="M14 3l7 7-5 5-7-7 5-5z" />
    {/* Gavel base */}
    <path d="M3 21h18" />
    {/* Gavel handle */}
    <path d="m10 10-6.5 6.5" />
  </svg>
);
