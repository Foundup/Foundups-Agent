/**
 * Shared z-index contract for the GotJunk? HOLO UI.
 * Modals appear above all interactive controls for user decisions.
 */
export const Z_LAYERS = {
  popup: 1200,
  fullscreen: 1400,
  fullscreenCamera: 1450, // Fullscreen camera view (below modals)
  gallery: 1500,
  mapOverlay: 1600,
  floatingControls: 2050,
  cameraOrb: 2100,
  sidebar: 2150,
  messagePanel: 2200, // Message panel - above sidebar, below modals (drops from top)
  modal: 2300, // Classification, Options - above all controls
  PURCHASE_MODAL: 2350, // Purchase confirmation - above regular modals
  tutorialPopup: 2400,
  actionSheet: 2500, // Discount/Bid sheets - above modals
} as const;

export type ZLayerKey = keyof typeof Z_LAYERS;
