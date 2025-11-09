/**
 * Shared z-index contract for the GotJunk? HOLO UI.
 * Modals appear above all interactive controls for user decisions.
 */
export const Z_LAYERS = {
  popup: 1200,
  fullscreen: 1400,
  gallery: 1500,
  mapOverlay: 1600,
  floatingControls: 2100,
  sidebar: 2200,
  modal: 2300, // Classification, Options - above all controls
  actionSheet: 2400, // Discount/Bid sheets - above modals
} as const;

export type ZLayerKey = keyof typeof Z_LAYERS;
