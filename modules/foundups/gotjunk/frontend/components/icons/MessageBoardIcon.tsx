import React from 'react';

interface IconProps {
  className?: string;
}

export const MessageBoardIcon: React.FC<IconProps> = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={1.5}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M7 8h10M7 12h6M5 5h14a2 2 0 012 2v9a2 2 0 01-2 2h-6l-4 3v-3H5a2 2 0 01-2-2V7a2 2 0 012-2z"
    />
  </svg>
);
