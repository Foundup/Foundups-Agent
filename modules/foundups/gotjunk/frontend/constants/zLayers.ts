/**
 * Shared z-index contract for the GotJunk? HOLO UI.
 * Keep floating controls above popups/modals to satisfy WSP layering rules.
 */
export const Z_LAYERS = {
  popup: 1200,
  fullscreen: 1400,
  gallery: 1500,
  mapOverlay: 1600,
  floatingControls: 2100,
  sidebar: 2200,
} as const;

export type ZLayerKey = keyof typeof Z_LAYERS;
