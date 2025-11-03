import React from 'react';

interface IconProps {
  className?: string;
}

export const NoCameraIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <g fill="currentColor" opacity="0.5">
        {/* Video Camera Shape */}
        <path d="M5 25 l0 50 l80 0 l0 -30 l-20 -20 l-60 0 Z" />
        
        {/* Slash */}
        <line x1="10" y1="90" x2="90" y2="10" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
        
        {/* Circle for photo camera */}
        <circle cx="50" cy="50" r="28" fill="currentColor" stroke="none"/>
        
        {/* Photo Camera Icon inside the circle */}
        <g stroke="white" strokeWidth="4" fill="none" transform="translate(2, 2) scale(0.9)">
            <path d="M28 42a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0135.07 37h8.86a2 2 0 011.664.89l.812 1.22A2 2 0 0058.07 40H59a2 2 0 012 2v14a2 2 0 01-2 2H30a2 2 0 01-2-2V42z" />
            <circle cx="44" cy="50" r="6" />
        </g>
    </g>
  </svg>
);