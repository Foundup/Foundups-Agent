# HOLO UI Z-Index Contract

_WSP Layering Reference – updated 2025-11-08_

| Layer | Value | Components | Notes |
|-------|-------|------------|-------|
| Sidebar Controls | 2200 | `LeftSidebarNav` | Always visible; sits above every popup/overlay. |
| Floating Controls | 2100 | `BottomNavBar`, camera orb | Includes search bar + capture button. |
| Map Overlay | 1600 | `PigeonMapView` | Full-screen map with zoom controls. |
| Gallery / Fullscreen Review | 1500 | `FullscreenGallery`, `FullscreenViewer`, `ItemReviewer` | Locks background scroll and dims content. |
| Popup Layer | 1200 | Classification/options modals, other dialogs | Standard modal layer. |
| Content Grid | 500 | Base app surfaces (`App.tsx`) | Anything without an explicit `z-index`. |

Implementation notes:

- The canonical values live in `constants/zLayers.ts`. Always use those exports instead of hard-coding numbers so react + docs stay in sync.
- Floating controls rely on `position: fixed` plus safe-area offsets (see `BottomNavBar` + `LeftSidebarNav`). Keep them outside popup containers in `App.tsx`.
- Fullscreen experiences (`ItemReviewer`, gallery, map) now lock `document.body.style.overflow` so mobile browsers do not clip floating controls when the page scrolls.
- Verification: open an item fullscreen, expand the map, and toggle classification modals—sidebar/cart icons and the capture orb must remain visible and clickable on iPhone 11/13/15/16 orientations.
