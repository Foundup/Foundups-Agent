import React from 'react';

interface IconProps {
  className?: string;
}

export const PhotoIcon: React.FC<IconProps> = ({ className }) => (
  <svg 
    className={className}
    xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 24 24" 
    fill="currentColor"
  >
    <path d="M4 4h3l2-2h6l2 2h3a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2zm8 14a5 5 0 100-10 5 5 0 000 10z"/>
    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
  </svg>
);
