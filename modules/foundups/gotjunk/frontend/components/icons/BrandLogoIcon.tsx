import React from 'react';

interface IconProps {
  className?: string;
}

export const BrandLogoIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="brand-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style={{ stopColor: 'rgb(243, 244, 246)', stopOpacity: 1 }} />
        <stop offset="100%" style={{ stopColor: 'rgb(209, 213, 219)', stopOpacity: 1 }} />
      </linearGradient>
    </defs>
    <circle cx="128" cy="128" r="120" fill="#111827" stroke="white" strokeWidth="8"/>
    <g transform="translate(128,128) scale(0.9)">
      <path d="M0-100 A100,100 0 0,1 86.6,50 L51.96,30 A60,60 0 0,0 0,-60 z" fill="url(#brand-grad)"/>
      <path d="M86.6,50 A100,100 0 0,1 -86.6,50 L-51.96,30 A60,60 0 0,0 51.96,30 z" fill="url(#brand-grad)"/>
      <path d="M-86.6,50 A100,100 0 0,1 0,-100 L0,-60 A60,60 0 0,0 -51.96,30 z" fill="url(#brand-grad)"/>
    </g>
  </svg>
);