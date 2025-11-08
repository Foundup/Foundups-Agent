/**
 * useViewport Hook
 * Fixes iOS Safari vh bug by syncing CSS custom properties with actual viewport height
 * WSP Compliance: WSP 50 (Pre-Action Verification), WSP 64 (Violation Prevention)
 */

import { useEffect } from 'react';

/**
 * Synchronizes CSS --vh variable with actual viewport height
 * Handles iOS Safari viewport height changes on scroll and orientation changes
 */
export function useViewport() {
  useEffect(() => {
    const setViewportHeight = () => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    // Set initial value
    setViewportHeight();

    // Update on resize (iOS address bar show/hide)
    window.addEventListener('resize', setViewportHeight);

    // Update on orientation change (landscape/portrait)
    window.addEventListener('orientationchange', setViewportHeight);

    // Cleanup
    return () => {
      window.removeEventListener('resize', setViewportHeight);
      window.removeEventListener('orientationchange', setViewportHeight);
    };
  }, []);
}
