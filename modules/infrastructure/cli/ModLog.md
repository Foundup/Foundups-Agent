# CLI Module - Modification Log

**WSP Compliance**: WSP 22 (ModLog Updates)

## V0.3.0 - Rotation Controls Menu (2026-01-28)

### Added

- **Rotation Controls Menu** (`R` option in YouTube DAEs):
  - Test swap to channel (with UI-TARS verification)
  - Check rotation status (current channel on Chrome/Edge)
  - Toggle rotation enable/disable
  - Toggle halt on error
  - Set rotation order
  - Quick swap shortcuts (Move2Japan <-> UnDaoDu)

- **Helper functions**:
  - `_handle_rotation_controls_menu()`: Main rotation controls submenu
  - `_test_swap_to_channel(target)`: Test account swap with TarsAccountSwapper
  - `_check_rotation_status()`: Check active channel on both browsers

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `YT_ROTATION_ENABLED` | true | Enable/disable rotation |
| `YT_ROTATION_ORDER` | Move2Japan,UnDaoDu,FoundUps,RavingANTIFA | Channel rotation order |
| `YT_ROTATION_HALT_ON_ERROR` | false | Stop rotation on errors |

### Files Changed
- `src/youtube_menu.py`: Added Rotation Controls menu and handlers

### WSP Compliance
- **WSP 22**: ModLog documentation
- **WSP 87**: Navigation Protocol (account swap testing)

---

## V0.2.1 - Video Lab Auto Mode (2026-01-22)

### Added
- Video Lab menu uses env defaults and supports auto mode for index-based Shorts.

### Changed
- Optional upload now runs across supported channels (including FoundUps).

### WSP Compliance
- **WSP 22**: ModLog documentation

## V0.2.0 - Path Resolution Fixes (2026-01-22)

### AUDIT: Deep Dive Indexing Menu

Conducted comprehensive audit of all 6 indexing menu options. Fixed critical path resolution issues that would cause failures when CWD != repo root.

### Fixed

- **`_handle_batch_indexing()`**: Replaced relative paths with absolute paths
  - `data/{channel}_video_ids.txt` -> `repo_root / "data" / f"{channel}_video_ids.txt"`
  - `scripts/batch_index_videos.py` -> `repo_root / "scripts" / "batch_index_videos.py"`
  - Added `cwd=str(repo_root)` to subprocess.run()

- **`_handle_batch_enhancement()`**: Replaced relative paths with absolute paths
  - `memory/enhancement_checkpoint.json` -> `repo_root / "memory" / "enhancement_checkpoint.json"`
  - `memory/video_index/{channel}` -> `repo_root / "memory" / "video_index" / channel`
  - `scripts/batch_enhance_videos.py` -> `repo_root / "scripts" / "batch_enhance_videos.py"`
  - Added `cwd=str(repo_root)` to subprocess.run()

- **`_handle_training_data_extraction()`**: Replaced relative paths with absolute paths
  - `memory/video_index/{channel}` -> `repo_root / "memory" / "video_index" / channel`
  - `memory/training_data/{channel}` -> `repo_root / "memory" / "training_data" / channel`

### Audit Results

| Option | Handler | Status | Notes |
|--------|---------|--------|-------|
| 1 | Gemini AI Indexing | OK (fragile) | Selenium/DOM-based |
| 2 | Whisper Indexing | OK | Dependencies available |
| 3 | Test Video Indexing | OK | API-based |
| 4 | Batch Index Channel | FIXED | Path resolution |
| 5 | Batch Enhance Videos | FIXED | Path resolution |
| 6 | Extract Training Data | FIXED | Path resolution |

### WSP Compliance
- **WSP 22**: ModLog documentation
- **WSP 50**: Pre-action verification (audited before fixing)
- **WSP 62**: File size enforcement (thin router pattern)

---

## V0.1.0 - Initial Extraction (2026-01-21)

### Created

Extracted CLI components from main.py per WSP 62 (file size enforcement).

### Files

- **indexing_menu.py**: YouTube indexing submenu handlers
- **youtube_menu.py**: YouTube DAEs submenu handlers
- **utilities.py**: Common helpers (select_channel, env_truthy, etc.)

### WSP Compliance
- **WSP 62**: File size enforcement
- **WSP 49**: Module structure

---

## Change Template

```markdown
## VX.X.X - Description (YYYY-MM-DD)

### Added
-

### Changed
-

### Fixed
-

### WSP Compliance
-
```
