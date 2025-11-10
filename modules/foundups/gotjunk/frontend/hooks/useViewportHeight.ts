/**
 * useViewportHeight - Track visual viewport height for iOS Safari
 *
 * iOS Safari has dynamic viewport height when URL bar/permission chips show.
 * This hook sets a CSS custom property `--vh` that always reflects the
 * actual visible viewport height.
 *
 * Usage: Call once in App.tsx, then use `calc(var(--vh) * 100)` in CSS
 */

import { useEffect } from 'react';

export function useViewportHeight() {
  useEffect(() => {
    const updateVh = () => {
      // Use visualViewport API if available (iOS Safari 13+)
      const vh = (window.visualViewport?.height ?? window.innerHeight) * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    // Set initial value
    updateVh();

    // Update on resize (orientation change, keyboard, etc)
    window.addEventListener('resize', updateVh);

    // Update on visual viewport changes (iOS Safari URL bar, permission chips)
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', updateVh as EventListener);
      window.visualViewport.addEventListener('scroll', updateVh as EventListener);
    }

    return () => {
      window.removeEventListener('resize', updateVh);
      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', updateVh as EventListener);
        window.visualViewport.removeEventListener('scroll', updateVh as EventListener);
      }
    };
  }, []);
}
