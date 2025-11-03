import React from 'react';

interface IconProps {
  className?: string;
}

export const RightChevronIcon: React.FC<IconProps> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path 
      d="M9 5l7 7-7 7" 
      stroke="#F87171" // Red for NO
      strokeWidth="3"
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
);