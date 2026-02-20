# -*- coding: utf-8 -*-
"""
Video Quality Analyzer - Capture quality metrics for video indexing.

WSP Compliance:
    WSP 72: Module Independence
    WSP 91: DAE Observability

Purpose:
    Analyze video quality (resolution, bitrate, noise) for Digital Twin training.
    Helps identify low-quality videos that may need enhancement.
"""

import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Video quality metrics."""
    video_id: str
    resolution: str  # e.g., "1920x1080"
    width: int
    height: int
    bitrate_kbps: Optional[int]
    frame_rate: float
    codec: str
    duration_seconds: float
    file_size_mb: Optional[float]
    quality_score: float  # 0-1 normalized score
    quality_tier: str  # "high", "medium", "low", "poor"
    issues: list  # List of quality issues


def get_quality_tier(width: int, height: int, bitrate_kbps: Optional[int]) -> str:
    """Determine quality tier based on resolution and bitrate."""
    if height >= 1080:
        return "high"
    elif height >= 720:
        return "medium"
    elif height >= 480:
        return "low"
    else:
        return "poor"


def calculate_quality_score(
    width: int,
    height: int,
    bitrate_kbps: Optional[int],
    frame_rate: float
) -> float:
    """
    Calculate normalized quality score (0-1).
    
    Factors:
    - Resolution: 40%
    - Bitrate: 30%
    - Frame rate: 30%
    """
    # Resolution score (1080p = 1.0, 720p = 0.7, 480p = 0.4, lower = 0.2)
    if height >= 1080:
        res_score = 1.0
    elif height >= 720:
        res_score = 0.7
    elif height >= 480:
        res_score = 0.4
    elif height >= 360:
        res_score = 0.3
    else:
        res_score = 0.2
    
    # Bitrate score (normalized to 10 Mbps = 1.0)
    if bitrate_kbps:
        bitrate_score = min(bitrate_kbps / 10000, 1.0)
    else:
        bitrate_score = 0.5  # Unknown bitrate
    
    # Frame rate score (60fps = 1.0, 30fps = 0.7, lower = 0.4)
    if frame_rate >= 60:
        fps_score = 1.0
    elif frame_rate >= 30:
        fps_score = 0.7
    elif frame_rate >= 24:
        fps_score = 0.6
    else:
        fps_score = 0.4
    
    # Weighted average
    return (res_score * 0.4) + (bitrate_score * 0.3) + (fps_score * 0.3)


def detect_quality_issues(
    width: int,
    height: int,
    bitrate_kbps: Optional[int],
    frame_rate: float
) -> list:
    """Detect specific quality issues."""
    issues = []
    
    if height < 480:
        issues.append("very_low_resolution")
    elif height < 720:
        issues.append("low_resolution")
    
    if bitrate_kbps and bitrate_kbps < 1000:
        issues.append("low_bitrate")
    
    if frame_rate < 24:
        issues.append("low_frame_rate")
    
    return issues


def analyze_video_quality_yt(video_id: str) -> Optional[QualityMetrics]:
    """
    Analyze video quality using yt-dlp (no download required).
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        QualityMetrics or None if analysis fails
    """
    try:
        import json
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Get video info via yt-dlp (no download)
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            "--no-playlist",
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.warning(f"[QUALITY] yt-dlp failed for {video_id}: {result.stderr}")
            return None
        
        info = json.loads(result.stdout)
        
        # Extract quality info
        width = info.get("width", 0) or 0
        height = info.get("height", 0) or 0
        
        # Get bitrate (may be in different fields)
        bitrate = info.get("vbr") or info.get("tbr") or info.get("abr")
        bitrate_kbps = int(bitrate) if bitrate else None
        
        # Frame rate
        fps = info.get("fps", 30) or 30
        
        # Codec
        vcodec = info.get("vcodec", "unknown")
        
        # Duration
        duration = info.get("duration", 0) or 0
        
        # File size (estimated)
        filesize = info.get("filesize") or info.get("filesize_approx")
        filesize_mb = filesize / (1024 * 1024) if filesize else None
        
        # Calculate metrics
        quality_score = calculate_quality_score(width, height, bitrate_kbps, fps)
        quality_tier = get_quality_tier(width, height, bitrate_kbps)
        issues = detect_quality_issues(width, height, bitrate_kbps, fps)
        
        return QualityMetrics(
            video_id=video_id,
            resolution=f"{width}x{height}",
            width=width,
            height=height,
            bitrate_kbps=bitrate_kbps,
            frame_rate=fps,
            codec=vcodec,
            duration_seconds=duration,
            file_size_mb=filesize_mb,
            quality_score=quality_score,
            quality_tier=quality_tier,
            issues=issues
        )
        
    except subprocess.TimeoutExpired:
        logger.error(f"[QUALITY] Timeout analyzing {video_id}")
        return None
    except Exception as e:
        logger.error(f"[QUALITY] Error analyzing {video_id}: {e}")
        return None


def analyze_batch(video_ids: list) -> Dict[str, QualityMetrics]:
    """
    Analyze multiple videos.
    
    Args:
        video_ids: List of YouTube video IDs
        
    Returns:
        Dict mapping video_id -> QualityMetrics
    """
    results = {}
    
    for i, vid in enumerate(video_ids):
        logger.info(f"[QUALITY] Analyzing {i+1}/{len(video_ids)}: {vid}")
        metrics = analyze_video_quality_yt(vid)
        if metrics:
            results[vid] = metrics
            logger.info(f"[QUALITY] {vid}: {metrics.quality_tier} ({metrics.resolution})")
        else:
            logger.warning(f"[QUALITY] {vid}: Analysis failed")
    
    return results


def get_oldest_channel_videos(channel_id: str, count: int = 10) -> list:
    """
    Get oldest videos from a YouTube channel using yt-dlp.
    
    Args:
        channel_id: YouTube channel ID
        count: Number of videos to get
        
    Returns:
        List of video IDs (oldest first)
    """
    try:
        import json
        
        url = f"https://www.youtube.com/channel/{channel_id}/videos"
        
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            "--playlist-end", str(count * 2),  # Get extra in case some fail
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            logger.error(f"[QUALITY] Failed to get channel videos: {result.stderr}")
            return []
        
        videos = []
        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    info = json.loads(line)
                    videos.append({
                        "id": info.get("id"),
                        "title": info.get("title"),
                    })
                except json.JSONDecodeError:
                    continue
        
        # Videos are typically newest first, reverse for oldest
        videos.reverse()
        
        return [v["id"] for v in videos[:count]]
        
    except Exception as e:
        logger.error(f"[QUALITY] Error getting channel videos: {e}")
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Video Quality Analyzer Test")
    print("=" * 60)
    
    # Test with a known video
    test_id = "8_DUQaqY6Tc"  # Education Singularity
    print(f"\nAnalyzing test video: {test_id}")
    
    metrics = analyze_video_quality_yt(test_id)
    if metrics:
        print(f"  Resolution: {metrics.resolution}")
        print(f"  Quality Tier: {metrics.quality_tier}")
        print(f"  Quality Score: {metrics.quality_score:.2f}")
        print(f"  Frame Rate: {metrics.frame_rate} fps")
        print(f"  Codec: {metrics.codec}")
        print(f"  Duration: {metrics.duration_seconds:.1f}s")
        if metrics.issues:
            print(f"  Issues: {', '.join(metrics.issues)}")
    else:
        print("  Analysis failed")
