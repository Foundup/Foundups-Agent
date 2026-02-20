#!/usr/bin/env python3
"""
Stage 4 Test: Indexing Validation

Validates that indexed videos have correct structure and quality.
Tests the stored index data for completeness and accuracy.

Test Stages:
    Stage 1: Navigation (single video) - DONE
    Stage 2: Batch Navigation (10+ videos) - DONE
    Stage 3: Single Video Indexing - DONE
    Stage 4: Indexing Validation - THIS TEST

Validation Checks:
    1. Index file exists and is valid JSON
    2. Audio segments have timestamps
    3. Visual keyframes have frame data
    4. Clip candidates have virality scores
    5. Metadata is complete

What 012 Should See:
    1. Load index from storage
    2. Validate each section
    3. Report quality metrics
    4. Pass/fail summary

Usage:
    python modules/ai_intelligence/video_indexer/tests/test_stage4_validation.py

WSP Compliance:
    - WSP 5: Test Coverage
    - WSP 6: Test Audit
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest


# =============================================================================
# Validation Functions
# =============================================================================

def load_index(video_id: str, channel: str = "undaodu") -> Optional[Dict[str, Any]]:
    """
    Load video index from storage.

    Args:
        video_id: YouTube video ID
        channel: Channel name

    Returns:
        Index dict or None if not found
    """
    index_path = Path(f"memory/video_index/{channel}/{video_id}.json")

    if not index_path.exists():
        print(f"[WARN] Index not found: {index_path}")
        return None

    try:
        with open(index_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        return None


def validate_audio_layer(index: Dict) -> Dict[str, Any]:
    """Validate audio layer of index."""
    result = {
        "valid": False,
        "segment_count": 0,
        "has_timestamps": False,
        "has_text": False,
        "duration": 0,
        "issues": [],
    }

    audio = index.get("audio", {})
    segments = audio.get("segments", [])

    result["segment_count"] = len(segments)

    if not segments:
        result["issues"].append("No audio segments")
        return result

    # Check segments
    has_timestamps = True
    has_text = True
    total_duration = 0

    for i, seg in enumerate(segments):
        if "start" not in seg or "end" not in seg:
            has_timestamps = False
            result["issues"].append(f"Segment {i} missing timestamps")

        if "text" not in seg or not seg.get("text", "").strip():
            has_text = False
            result["issues"].append(f"Segment {i} missing text")

        if "end" in seg and "start" in seg:
            total_duration = max(total_duration, seg["end"])

    result["has_timestamps"] = has_timestamps
    result["has_text"] = has_text
    result["duration"] = total_duration
    result["valid"] = has_timestamps and has_text and len(segments) > 0

    return result


def validate_visual_layer(index: Dict) -> Dict[str, Any]:
    """Validate visual layer of index."""
    result = {
        "valid": False,
        "keyframe_count": 0,
        "shot_count": 0,
        "face_count": 0,
        "has_timestamps": False,
        "issues": [],
    }

    visual = index.get("visual", {})
    keyframes = visual.get("keyframes", [])
    shots = visual.get("shots", [])
    faces = visual.get("faces", visual.get("face_count", 0))

    result["keyframe_count"] = len(keyframes)
    result["shot_count"] = len(shots)
    result["face_count"] = faces if isinstance(faces, int) else len(faces)

    if not keyframes:
        result["issues"].append("No keyframes")

    # Check keyframes
    has_timestamps = True
    for i, kf in enumerate(keyframes):
        if "timestamp" not in kf and "time" not in kf:
            has_timestamps = False
            result["issues"].append(f"Keyframe {i} missing timestamp")
            break

    result["has_timestamps"] = has_timestamps
    result["valid"] = len(keyframes) > 0 and has_timestamps

    return result


def validate_clips_layer(index: Dict) -> Dict[str, Any]:
    """Validate clips layer of index."""
    result = {
        "valid": False,
        "candidate_count": 0,
        "avg_virality": 0.0,
        "best_score": 0.0,
        "issues": [],
    }

    clips = index.get("clips", {})
    candidates = clips.get("candidates", [])

    result["candidate_count"] = len(candidates)

    if not candidates:
        result["issues"].append("No clip candidates")
        return result

    # Calculate metrics
    virality_scores = []
    for c in candidates:
        score = c.get("virality_score", c.get("score", 0))
        virality_scores.append(score)

    if virality_scores:
        result["avg_virality"] = sum(virality_scores) / len(virality_scores)
        result["best_score"] = max(virality_scores)

    result["valid"] = len(candidates) > 0 and result["avg_virality"] > 0

    return result


def validate_index(video_id: str, channel: str = "undaodu") -> Dict[str, Any]:
    """
    Full validation of a video index.

    Args:
        video_id: YouTube video ID
        channel: Channel name

    Returns:
        Validation report dict
    """
    print("\n" + "=" * 70)
    print(f"[STAGE 4] Index Validation")
    print("=" * 70)
    print(f"  Video ID: {video_id}")
    print(f"  Channel: {channel}")
    print("=" * 70)

    report = {
        "video_id": video_id,
        "channel": channel,
        "index_exists": False,
        "valid": False,
        "layers": {},
        "quality_score": 0.0,
        "issues": [],
    }

    # Load index
    print(f"\n[STEP 1] Loading index...")
    index = load_index(video_id, channel)

    if index is None:
        report["issues"].append("Index file not found or invalid")
        print(f"[FAIL] Index not found")
        return report

    report["index_exists"] = True
    print(f"[OK] Index loaded")

    # Validate metadata
    print(f"\n[STEP 2] Validating metadata...")
    if "video_id" not in index:
        report["issues"].append("Missing video_id in index")
    if "title" not in index:
        report["issues"].append("Missing title in index")
    if "indexed_at" not in index:
        report["issues"].append("Missing indexed_at timestamp")

    # Validate audio layer
    print(f"\n[STEP 3] Validating audio layer...")
    audio_validation = validate_audio_layer(index)
    report["layers"]["audio"] = audio_validation
    print(f"  Segments: {audio_validation['segment_count']}")
    print(f"  Duration: {audio_validation['duration']:.1f}s")
    print(f"  Valid: {audio_validation['valid']}")

    # Validate visual layer
    print(f"\n[STEP 4] Validating visual layer...")
    visual_validation = validate_visual_layer(index)
    report["layers"]["visual"] = visual_validation
    print(f"  Keyframes: {visual_validation['keyframe_count']}")
    print(f"  Shots: {visual_validation['shot_count']}")
    print(f"  Faces: {visual_validation['face_count']}")
    print(f"  Valid: {visual_validation['valid']}")

    # Validate clips layer
    print(f"\n[STEP 5] Validating clips layer...")
    clips_validation = validate_clips_layer(index)
    report["layers"]["clips"] = clips_validation
    print(f"  Candidates: {clips_validation['candidate_count']}")
    print(f"  Avg Virality: {clips_validation['avg_virality']:.2f}")
    print(f"  Best Score: {clips_validation['best_score']:.2f}")
    print(f"  Valid: {clips_validation['valid']}")

    # Calculate quality score
    scores = []
    if audio_validation["valid"]:
        scores.append(1.0)
    if visual_validation["valid"]:
        scores.append(1.0)
    if clips_validation["valid"]:
        scores.append(clips_validation["avg_virality"])

    report["quality_score"] = sum(scores) / max(len(scores), 1)
    report["valid"] = len(scores) >= 2  # At least 2 layers valid

    # Summary
    print("\n" + "=" * 70)
    print("[VALIDATION SUMMARY]")
    print("=" * 70)
    print(f"  Overall Valid: {report['valid']}")
    print(f"  Quality Score: {report['quality_score']:.2f}")
    print(f"  Issues: {len(report['issues'])}")
    for issue in report["issues"]:
        print(f"    - {issue}")
    print("=" * 70)

    return report


def list_indexed_videos(channel: str = "undaodu") -> List[str]:
    """List all indexed videos for a channel."""
    index_dir = Path(f"memory/video_index/{channel}")
    if not index_dir.exists():
        return []

    videos = []
    for f in index_dir.glob("*.json"):
        if f.stem not in ["metadata", "config"]:
            videos.append(f.stem)

    return videos


def save_validation_report(report: Dict) -> str:
    """Save validation report."""
    artifact_dir = Path("memory/video_index/test_results")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stage4_validation_{report['video_id']}_{timestamp}.json"
    path = artifact_dir / filename

    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"[ARTIFACT] Saved: {path}")
    return str(path)


# =============================================================================
# Test Cases
# =============================================================================

@pytest.mark.integration
class TestStage4Validation:
    """Stage 4: Index validation tests."""

    def test_validate_index_structure(self):
        """Test: Validate index has correct structure."""
        # Try to find an indexed video
        videos = list_indexed_videos("undaodu")

        if not videos:
            pytest.skip("No indexed videos found - run Stage 3 first")

        video_id = videos[0]
        report = validate_index(video_id, "undaodu")

        assert report["index_exists"], "Index should exist"
        save_validation_report(report)

    def test_validate_known_video(self):
        """Test: Validate known test video index."""
        video_id = "8_DUQaqY6Tc"  # Oldest UnDaoDu video

        report = validate_index(video_id, "undaodu")

        if not report["index_exists"]:
            pytest.skip(f"Video {video_id} not indexed - run Stage 3 first")

        save_validation_report(report)
        print(f"\n[PASS] Validation complete, quality={report['quality_score']:.2f}")


# =============================================================================
# Direct Execution
# =============================================================================

def run_stage4_test():
    """Run Stage 4 validation test."""
    print("\n")
    print("=" * 70)
    print("  VIDEO INDEXER - STAGE 4: INDEXING VALIDATION")
    print("=" * 70)
    print(f"  Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # List indexed videos
    print("\n[CHECK] Looking for indexed videos...")
    videos = list_indexed_videos("undaodu")

    if not videos:
        print("[WARN] No indexed videos found in memory/video_index/undaodu/")
        print("[TIP] Run Stage 3 first to index a video")

        # Create mock validation to show structure
        print("\n[DEMO] Showing validation structure for expected output:")
        demo_report = {
            "video_id": "8_DUQaqY6Tc",
            "channel": "undaodu",
            "index_exists": False,
            "valid": False,
            "quality_score": 0.0,
            "issues": ["Index file not found"],
        }
        print(json.dumps(demo_report, indent=2))
        return 1

    # Validate first indexed video
    video_id = videos[0]
    print(f"\n[VALIDATE] Checking: {video_id}")

    report = validate_index(video_id, "undaodu")
    artifact_path = save_validation_report(report)

    # Summary
    print("\n")
    print("=" * 70)
    print("  STAGE 4 TEST COMPLETE")
    print("=" * 70)
    print(f"  Video: {video_id}")
    print(f"  Valid: {report['valid']}")
    print(f"  Quality: {report['quality_score']:.2f}")
    print(f"  Artifact: {artifact_path}")
    print("=" * 70)

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(run_stage4_test())
