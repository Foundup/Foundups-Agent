#!/usr/bin/env python
"""
antifaFM Broadcaster - Main Entry Point

Launches all streaming components:
1. Grid Orchestrator - Video rotation synced to songs
2. News Monitor - Breaking news from international sources
3. Ticker & Now Playing - Auto-updating text overlays

Usage:
    python -m antifafm_broadcaster.main
    python modules/platform_integration/antifafm_broadcaster/main.py
"""

import asyncio
import threading
import time
import sys
import os
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def run_grid_orchestrator():
    """Run the grid-based video orchestrator."""
    import obsws_python as obs
    import urllib.request
    import json

    c = obs.ReqClient(host='localhost', port=4455, password='')
    scene = c.get_current_program_scene().scene_name

    GRID = {
        'LEFT':  {'x': 0,   'y': 0, 'w': 960,  'h': 910},
        'RIGHT': {'x': 960, 'y': 0, 'w': 960,  'h': 910},
        'FULL':  {'x': 0,   'y': 0, 'w': 1920, 'h': 910},
    }

    LAYOUTS = [
        {'LEFT': 'Charlie Chaplin', 'RIGHT': 'BBC Straits'},
        {'LEFT': 'antifaFM Background', 'RIGHT': 'Telaviv'},
        {'FULL': 'Charlie Chaplin'},
        {'FULL': 'BBC Straits'},
    ]

    videos = ['Charlie Chaplin', 'BBC Straits', 'antifaFM Background', 'Telaviv']
    video_ids = {}
    for name in videos:
        try:
            video_ids[name] = c.get_scene_item_id(scene, name).scene_item_id
        except:
            pass

    def apply_layout(idx):
        layout = LAYOUTS[idx % len(LAYOUTS)]
        for name, item_id in video_ids.items():
            c.set_scene_item_enabled(scene, item_id, False)
        for cell, video in layout.items():
            if video in video_ids:
                item_id = video_ids[video]
                g = GRID[cell]
                c.set_scene_item_transform(scene, item_id, {
                    'positionX': float(g['x']), 'positionY': float(g['y']),
                    'boundsType': 'OBS_BOUNDS_SCALE_INNER',
                    'boundsWidth': float(g['w']), 'boundsHeight': float(g['h']),
                })
                c.set_scene_item_enabled(scene, item_id, True)
        return list(layout.values())

    def get_song():
        try:
            req = urllib.request.Request(
                'https://a12.asurahosting.com/api/nowplaying',
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            for s in data:
                if 'antifa' in s.get('station', {}).get('name', '').lower():
                    song = s.get('now_playing', {}).get('song', {})
                    return song.get('artist', ''), song.get('title', '')
        except:
            pass
        return '', ''

    print('[GRID] Starting video orchestrator')
    layout_idx = 0
    last_song = None
    apply_layout(0)

    while True:
        try:
            artist, title = get_song()
            song_key = artist + title
            if song_key != last_song and title:
                last_song = song_key
                layout_idx = (layout_idx + 1) % len(LAYOUTS)
                active = apply_layout(layout_idx)

                # Update Now Playing
                np = 'NOW PLAYING: ' + (artist.upper() + ' - ' if artist else '') + title.upper()
                c.set_input_settings('Now Playing', {'text': np}, True)

                safe = title.encode('ascii', 'replace').decode('ascii')[:25]
                print(f'[GRID] {safe} -> {active}')

            time.sleep(5)
        except Exception as e:
            print(f'[GRID] Error: {e}')
            time.sleep(5)


def run_news_monitor():
    """Monitor international news for breaking alerts."""
    import obsws_python as obs
    import urllib.request
    import xml.etree.ElementTree as ET

    RSS_FEEDS = {
        'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
        'BBC': 'https://feeds.bbci.co.uk/news/world/rss.xml',
        'Guardian': 'https://www.theguardian.com/world/rss',
        'France24': 'https://www.france24.com/en/rss',
        'DW': 'https://rss.dw.com/xml/rss-en-world',
    }

    KEYWORDS = ['iran', 'tehran', 'attack', 'missile', 'strike', 'war',
                'beirut', 'israel', 'hezbollah', 'idf', 'bombing']

    c = obs.ReqClient(host='localhost', port=4455, password='')
    seen_titles = set()

    def scan_news():
        alerts = []
        for source, url in RSS_FEEDS.items():
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    content = response.read().decode('utf-8', errors='ignore')

                root = ET.fromstring(content)
                for item in root.findall('.//item')[:10]:
                    title_el = item.find('title')
                    if title_el is not None and title_el.text:
                        title = title_el.text.strip()
                        if any(kw in title.lower() for kw in KEYWORDS):
                            if title not in seen_titles:
                                seen_titles.add(title)
                                safe = title.encode('ascii', 'replace').decode('ascii')[:70]
                                alerts.append(safe.upper())
            except:
                pass
        return alerts[:5]

    def update_ticker(alerts):
        # Clean separator (no >>> <<< noise)
        ticker_parts = alerts.copy()
        ticker_parts.extend(['ANTIFAFM.COM', 'FOUNDUPS.COM'])
        # Red dot separator (on brand) - cleaner than ***
        ticker_text = '  ●  '.join(ticker_parts)
        # Larger font for mobile viewing (48pt -> 64pt)
        c.set_input_settings('Scrolling Ticker', {
            'text': ticker_text,
            'font': {'face': 'Arial Black', 'size': 64, 'style': 'Bold'}
        }, True)

    print('[NEWS] Starting news monitor')

    # Initial scan
    alerts = scan_news()
    if alerts:
        update_ticker(alerts)
        print(f'[NEWS] Loaded {len(alerts)} alerts')

    while True:
        time.sleep(300)  # 5 minutes
        new_alerts = scan_news()
        if new_alerts:
            update_ticker(new_alerts)
            print(f'[NEWS] Updated: {new_alerts[0][:40]}...')


def check_obs_connection():
    """Check if OBS is running and connected."""
    try:
        import obsws_python as obs
        c = obs.ReqClient(host='localhost', port=4455, password='')
        version = c.get_version()
        print(f'[OBS] Connected - OBS {version.obs_version}')
        return True
    except Exception as e:
        print(f'[OBS] Connection failed: {e}')
        print('[OBS] Make sure OBS is running with WebSocket enabled on port 4455')
        return False


def main():
    print('=' * 60)
    print('antifaFM Broadcaster')
    print('=' * 60)

    # Check OBS connection
    if not check_obs_connection():
        print('\nWaiting for OBS...')
        while not check_obs_connection():
            time.sleep(5)

    print('\nStarting components...\n')

    # Start grid orchestrator in thread
    grid_thread = threading.Thread(target=run_grid_orchestrator, daemon=True)
    grid_thread.start()

    # Start news monitor in thread
    news_thread = threading.Thread(target=run_news_monitor, daemon=True)
    news_thread.start()

    print('[MAIN] All components running')
    print('[MAIN] Press Ctrl+C to stop\n')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n[MAIN] Shutting down...')


if __name__ == '__main__':
    main()
