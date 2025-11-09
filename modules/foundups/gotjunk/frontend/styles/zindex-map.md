# HOLO UI Z-Index Contract

_WSP Layering Reference – updated 2025-11-08_

| Layer | Value | Components | Notes |
|-------|-------|------------|-------|
| Tutorial Popup | 2400 | `InstructionsModal` | Safe-area aware onboarding card; always above camera orb. |
| Action Sheets | 2500 | Discount/Bid sheets | Highest layer; interactive prompts. |
| Modal Layer | 2300 | Classification/options modals | Confirmation dialogs above nav. |
| Sidebar Controls | 2150 | `LeftSidebarNav` | Always visible; sits above floating controls. |
| Camera Orb | 2100 | Capture orb container | Hovers above nav bar but below tutorials. |
| Floating Controls | 2050 | `BottomNavBar`, search bar | Includes search + capture tray. |
| Map Overlay | 1600 | `PigeonMapView` | Full-screen map with zoom controls. |
| Gallery / Fullscreen Review | 1500 | `FullscreenGallery`, `FullscreenViewer`, `ItemReviewer` | Locks background scroll and dims content. |
| Popup Layer | 1200 | Classification/options popups | Standard modal layer. |
| Content Grid | 500 | Base app surfaces (`App.tsx`) | Anything without an explicit `z-index`. |

Implementation notes:

- The canonical values live in `constants/zLayers.ts`. Always use those exports instead of hard-coding numbers so react + docs stay in sync.
- Floating controls rely on `position: fixed` plus safe-area offsets (see `BottomNavBar` + `LeftSidebarNav`). Keep them outside popup containers in `App.tsx`.
- Fullscreen experiences (`ItemReviewer`, gallery, map) now lock `document.body.style.overflow` so mobile browsers do not clip floating controls when the page scrolls.
- Verification: open an item fullscreen, expand the map, and toggle classification modals—sidebar/cart icons and the capture orb must remain visible and clickable on iPhone 11/13/15/16 orientations.
