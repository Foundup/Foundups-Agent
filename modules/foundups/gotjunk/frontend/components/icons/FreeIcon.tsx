import React from 'react';

interface IconProps {
  className?: string;
}

/**
 * FreeIcon - Gift box icon for free items
 * Bright blue, round shape - feels generous
 */
export const FreeIcon: React.FC<IconProps> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    strokeWidth="2"
    stroke="currentColor"
    fill="none"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Gift box body */}
    <path d="M20 12v10H4V12" />
    {/* Gift box lid */}
    <path d="M2 7h20v5H2z" />
    {/* Vertical ribbon */}
    <path d="M12 22V7" />
    {/* Left bow */}
    <path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z" />
    {/* Right bow */}
    <path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z" />
  </svg>
);
