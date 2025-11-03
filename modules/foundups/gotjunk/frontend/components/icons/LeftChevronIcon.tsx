import React from 'react';

interface IconProps {
  className?: string;
}

export const LeftChevronIcon: React.FC<IconProps> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path 
      d="M15 19l-7-7 7-7" 
      stroke="#34D399" // Green for YES
      strokeWidth="3" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
);