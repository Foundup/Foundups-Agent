# GotJunk FoundUp - CRITICAL REQUIREMENTS

## 🚨 NEVER REMOVE - BOTTOM NAV BAR 🚨

**CRITICAL**: The `BottomNavBar` component must NEVER be removed or replaced.

### Component Location
```
modules/foundups/gotjunk/frontend/components/BottomNavBar.tsx
```

### Why This Component is Critical

1. **Camera Functionality**: Contains the live camera preview and capture controls
2. **Swipe Navigation**: Left/right arrows for Tinder-style item review
3. **Photo/Video Toggle**: Switches between capture modes
4. **Gallery Access**: Opens user's kept items gallery
5. **Map Access**: Opens map view
6. **SOS Detection**: Liberty Alert easter egg (morse code on gallery icon)

### Component Features (DO NOT MODIFY)

- **Live Camera Preview** in center circular button
- **Press & Hold** for video recording
- **Quick Tap** for photo capture
- **Left Arrow** (red) - Delete/skip item
- **Right Arrow** (green) - Keep item
- **Photo/Video Icons** - Mode toggle
- **Gallery Icon** (grid) - Opens FullscreenGallery
- **Map Icon** - Opens PigeonMapView
- **Liberty Alert Icon** 🗽 (when unlocked)

### Import & Usage in App.tsx

```typescript
import { BottomNavBar } from './components/BottomNavBar';

// ... in render:

<BottomNavBar
  captureMode={captureMode}
  onToggleCaptureMode={() => setCaptureMode(mode => mode === 'photo' ? 'video' : 'photo')}
  onCapture={handleCapture}
  onReviewAction={(action) => currentReviewItem && handleReviewDecision(currentReviewItem, action)}
  onGalleryClick={() => {
    if (!sosDetectionActive.current) {
      setGalleryOpen(true);
    }
  }}
  onGalleryIconTap={(duration) => {
    // SOS morse code detection logic
  }}
  onMapClick={() => {
    setMapOpen(true);
  }}
  isRecording={isRecording}
  setIsRecording={setIsRecording}
  countdown={countdown}
  setCountdown={setCountdown}
  hasReviewItems={reviewItems.length > 0}
  libertyEnabled={libertyEnabled}
/>
```

### What You CAN Do

✅ **ADD** persistent icons/navigation ABOVE the BottomNavBar (e.g., top-right icons)
✅ **ENHANCE** BottomNavBar with additional features
✅ **STYLE** BottomNavBar appearance (colors, sizes)
✅ **EXTEND** BottomNavBar with new buttons/icons

### What You CANNOT Do

❌ **REMOVE** BottomNavBar component
❌ **REPLACE** BottomNavBar with custom nav
❌ **DELETE** camera controls from BottomNavBar
❌ **REMOVE** swipe navigation arrows
❌ **DISABLE** SOS detection functionality

---

## History

**2025-11-03**: BottomNavBar was accidentally removed during refactoring. This caused:
- Loss of camera functionality
- Loss of swipe navigation
- Loss of SOS easter egg detection

**Resolution**: BottomNavBar was immediately restored. This document created to prevent future removal.

---

## If BottomNavBar Must Be Modified

1. **Test thoroughly** before committing changes
2. **Preserve all existing functionality**:
   - Camera preview & capture
   - Left/right swipe controls
   - Photo/video mode toggle
   - Gallery icon with SOS detection
   - Map icon
   - Liberty Alert icon (when enabled)
3. **Document changes** in ModLog.md
4. **Verify** camera permissions still work
5. **Test** SOS morse code detection (tap gallery icon: ... ___ ...)

---

**REMEMBER**: This component is the CORE of the GotJunk experience. Handle with care! 🎥📸
