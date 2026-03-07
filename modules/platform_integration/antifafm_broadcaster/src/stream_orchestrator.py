"""
antifaFM Stream Orchestrator - Intelligent Video Layer Management

Solves:
1. Video stacking (only 1 video visible at a time)
2. Animated transitions (grow/shrink effects)
3. Song-synced video changes

Architecture:
- VideoLayer: Atomic show/hide with z-order control
- TransitionEngine: Animate bounds over time
- SongSync: Monitor antifaFM API for track changes
"""

import obsws_python as obs
import urllib.request
import json
import time
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


@dataclass
class Rect:
    """Rectangle for positioning."""
    x: float
    y: float
    width: float
    height: float

    def interpolate(self, target: 'Rect', t: float) -> 'Rect':
        """Interpolate between self and target (t=0 to 1)."""
        return Rect(
            x=self.x + (target.x - self.x) * t,
            y=self.y + (target.y - self.y) * t,
            width=self.width + (target.width - self.width) * t,
            height=self.height + (target.height - self.height) * t,
        )


# Layout constants
FULL_SCREEN = Rect(0, 0, 1920, 980)  # Leave room for ticker
SMALL_CORNER = Rect(1550, 50, 350, 200)
HIDDEN = Rect(-500, -500, 320, 180)


class VideoLayer:
    """Manages video layer visibility - ensures only ONE video visible."""

    def __init__(self, client: obs.ReqClient, scene: str):
        self.client = client
        self.scene = scene
        self.videos: Dict[str, int] = {}  # name -> item_id
        self.active: Optional[str] = None

    def register(self, name: str) -> bool:
        """Register a video source."""
        try:
            item_id = self.client.get_scene_item_id(self.scene, name).scene_item_id
            self.videos[name] = item_id
            return True
        except:
            return False

    def _disable_all(self):
        """Disable ALL videos - atomic first step."""
        for name, item_id in self.videos.items():
            try:
                self.client.set_scene_item_enabled(self.scene, item_id, False)
            except:
                pass

    def show(self, name: str) -> bool:
        """Show ONLY this video, hide all others."""
        if name not in self.videos:
            return False

        # ATOMIC: First disable ALL
        self._disable_all()

        # Then enable the one we want
        try:
            self.client.set_scene_item_enabled(self.scene, self.videos[name], True)
            self.active = name
            return True
        except:
            return False

    def set_bounds(self, name: str, rect: Rect):
        """Set video bounds/position."""
        if name not in self.videos:
            return
        try:
            self.client.set_scene_item_transform(self.scene, self.videos[name], {
                'positionX': rect.x,
                'positionY': rect.y,
                'boundsType': 'OBS_BOUNDS_SCALE_INNER',
                'boundsWidth': rect.width,
                'boundsHeight': rect.height,
                'boundsAlignment': 0,
            })
        except:
            pass


class TransitionEngine:
    """Animate video transitions."""

    def __init__(self, layer: VideoLayer):
        self.layer = layer

    def transition(self, from_video: str, to_video: str, duration: float = 1.0):
        """
        Transition from one video to another with animation.
        1. Shrink current video
        2. Show next video small
        3. Grow next video to full screen
        """
        steps = 10
        step_delay = duration / steps / 2  # Half for shrink, half for grow

        # Phase 1: Shrink current video (if any)
        if from_video and from_video in self.layer.videos:
            for i in range(steps):
                t = i / steps
                rect = FULL_SCREEN.interpolate(SMALL_CORNER, t)
                self.layer.set_bounds(from_video, rect)
                time.sleep(step_delay)

        # Phase 2: Switch videos (atomic)
        self.layer.show(to_video)
        self.layer.set_bounds(to_video, SMALL_CORNER)

        # Phase 3: Grow new video to full screen
        for i in range(steps):
            t = i / steps
            rect = SMALL_CORNER.interpolate(FULL_SCREEN, t)
            self.layer.set_bounds(to_video, rect)
            time.sleep(step_delay)

        # Ensure full screen at end
        self.layer.set_bounds(to_video, FULL_SCREEN)

    def instant_switch(self, to_video: str):
        """Instant switch (no animation)."""
        self.layer.show(to_video)
        self.layer.set_bounds(to_video, FULL_SCREEN)


class SongSync:
    """Monitor antifaFM for song changes."""

    API_URL = 'https://a12.asurahosting.com/api/nowplaying'

    def __init__(self):
        self.last_song: Optional[str] = None

    def get_current(self) -> Tuple[str, str]:
        """Get current artist and title."""
        try:
            req = urllib.request.Request(
                self.API_URL,
                headers={'User-Agent': 'Mozilla/5.0 antifaFM-StreamBot'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

            for station in data:
                if 'antifa' in station.get('station', {}).get('name', '').lower():
                    song = station.get('now_playing', {}).get('song', {})
                    return song.get('artist', ''), song.get('title', '')
        except:
            pass
        return '', ''

    def check_changed(self) -> Optional[Tuple[str, str]]:
        """Check if song changed. Returns (artist, title) if changed, None otherwise."""
        artist, title = self.get_current()
        song_key = f'{artist}|{title}'

        if song_key != self.last_song and title:
            self.last_song = song_key
            return artist, title
        return None


class StreamOrchestrator:
    """Main orchestrator - coordinates all components."""

    ROTATION_VIDEOS = [
        'antifaFM Background',
        'BBC Straits',
        'Telaviv',
        # Add more OBS source names here as needed
        # 'DW News',
        # 'France 24',
        # 'Al Jazeera',
    ]

    def __init__(self):
        self.client = obs.ReqClient(host='localhost', port=4455, password='')
        self.scene = self.client.get_current_program_scene().scene_name

        self.layer = VideoLayer(self.client, self.scene)
        self.transition = TransitionEngine(self.layer)
        self.song_sync = SongSync()

        self.current_idx = 0
        self.running = False

    def setup(self):
        """Initialize - register videos and set initial state."""
        print(f'Scene: {self.scene}')

        # Register rotation videos
        for name in self.ROTATION_VIDEOS:
            if self.layer.register(name):
                print(f'  [OK] {name}')
            else:
                print(f'  [SKIP] {name}')

        # Disable ALL registered videos first
        self.layer._disable_all()

        # Show first video
        if self.layer.videos:
            first = list(self.layer.videos.keys())[0]
            self.transition.instant_switch(first)
            print(f'Initial video: {first}')

    def update_now_playing(self, artist: str, title: str):
        """Update the Now Playing text source."""
        if artist:
            text = f'NOW PLAYING: {artist.upper()} - {title.upper()}'
        else:
            text = f'NOW PLAYING: {title.upper()}'

        try:
            self.client.set_input_settings('Now Playing', {'text': text}, True)
        except:
            pass

    def next_video(self) -> str:
        """Get next video in rotation."""
        videos = list(self.layer.videos.keys())
        if not videos:
            return ''

        self.current_idx = (self.current_idx + 1) % len(videos)
        return videos[self.current_idx]

    def run(self, animate: bool = True):
        """Main loop - sync videos with song changes."""
        self.running = True
        print(f'\nStream Orchestrator running...')
        print(f'Videos: {len(self.layer.videos)}')
        print(f'Animate: {animate}')
        print('Ctrl+C to stop\n')
        sys.stdout.flush()

        while self.running:
            try:
                # Check for song change
                change = self.song_sync.check_changed()

                if change:
                    artist, title = change

                    # Update Now Playing
                    self.update_now_playing(artist, title)

                    # Get next video
                    current = self.layer.active
                    next_vid = self.next_video()

                    # Transition
                    if animate and current:
                        self.transition.transition(current, next_vid, duration=1.0)
                    else:
                        self.transition.instant_switch(next_vid)

                    # Log
                    safe_title = title.encode('ascii', 'replace').decode('ascii')[:30]
                    print(f'[{time.strftime("%H:%M:%S")}] {safe_title} -> {next_vid}')
                    sys.stdout.flush()

                time.sleep(5)

            except KeyboardInterrupt:
                print('\nStopping...')
                self.running = False
            except Exception as e:
                print(f'Error: {e}')
                time.sleep(5)

    def stop(self):
        self.running = False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='antifaFM Stream Orchestrator')
    parser.add_argument('--no-animate', action='store_true',
                        help='Disable transition animations')
    args = parser.parse_args()

    orchestrator = StreamOrchestrator()
    orchestrator.setup()
    orchestrator.run(animate=not args.no_animate)


if __name__ == '__main__':
    main()
