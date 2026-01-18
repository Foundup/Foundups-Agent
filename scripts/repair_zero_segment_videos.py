#!/usr/bin/env python
"""Repair zero-segment videos by extracting JSON from transcript_summary.

These videos have Gemini's response stored as raw text (with markdown code blocks)
instead of properly parsed into the data structure.
"""
import json
import re
from pathlib import Path
from datetime import datetime


def fix_trailing_commas(json_str: str) -> str:
    """Remove trailing commas from JSON (common Gemini output issue)."""
    import re
    # Remove trailing commas before closing braces/brackets
    # Pattern: comma followed by whitespace and closing brace/bracket
    fixed = re.sub(r',(\s*[}\]])', r'\1', json_str)
    return fixed


def extract_json_from_text(text: str) -> dict | None:
    """Extract JSON from markdown code blocks or raw text.

    Handles Gemini's response format which includes:
    - JSON in markdown code blocks (```json ... ```)
    - Trailing commas (invalid JSON that Gemini sometimes produces)
    - Sometimes nested or escaped quotes
    """
    import re

    def try_parse(json_str: str) -> dict | None:
        """Try to parse JSON, fixing trailing commas if needed."""
        # First try raw parsing
        try:
            data = json.loads(json_str)
            if 'segments' in data and len(data['segments']) > 0:
                return data
        except json.JSONDecodeError:
            pass

        # Try with trailing comma fix
        try:
            fixed = fix_trailing_commas(json_str)
            data = json.loads(fixed)
            if 'segments' in data and len(data['segments']) > 0:
                return data
        except json.JSONDecodeError:
            pass

        return None

    # Method 1: Look for ```json block and extract content
    json_block_match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
    if json_block_match:
        result = try_parse(json_block_match.group(1).strip())
        if result:
            return result

    # Method 2: Look for any ``` block
    code_block_match = re.search(r'```\s*\n?(.*?)\n?```', text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1).strip()
        if json_str.startswith('{'):
            result = try_parse(json_str)
            if result:
                return result

    # Method 3: Find first { and match to last } for segments-containing JSON
    first_brace = text.find('{')
    if first_brace >= 0:
        # Find the matching closing brace by counting
        brace_count = 0
        for i in range(first_brace, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[first_brace:i+1]
                    result = try_parse(json_str)
                    if result:
                        return result
                    break

    return None


def repair_video(json_path: Path) -> tuple[bool, str]:
    """Repair a single video's JSON structure.

    Returns: (success, message)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check if already has segments
    segments = data.get('audio', {}).get('segments', [])
    if segments:
        return True, f"Already has {len(segments)} segments"

    # Try to extract from transcript_summary
    transcript_summary = data.get('audio', {}).get('transcript_summary', '')
    if not transcript_summary:
        # Also check metadata.summary
        transcript_summary = data.get('metadata', {}).get('summary', '')

    if not transcript_summary:
        return False, "No transcript_summary to extract from"

    extracted = extract_json_from_text(transcript_summary)
    if not extracted:
        return False, "Could not extract JSON from transcript_summary"

    extracted_segments = extracted.get('segments', [])
    if not extracted_segments:
        return False, "Extracted JSON has no segments"

    # Update the data structure
    data['title'] = extracted.get('title', data.get('title', ''))
    data['audio']['segments'] = extracted_segments

    # Update with clean summary (not the JSON blob)
    clean_summary = extracted.get('summary', extracted.get('transcript_summary', ''))
    if clean_summary:
        data['audio']['transcript_summary'] = clean_summary

    # Update metadata
    if 'metadata' not in data:
        data['metadata'] = {}
    data['metadata']['duration'] = extracted.get('duration', '')
    data['metadata']['topics'] = extracted.get('topics', [])
    data['metadata']['speakers'] = extracted.get('speakers', [])
    data['metadata']['key_points'] = extracted.get('key_points', [])
    data['metadata']['summary'] = clean_summary

    # Mark as repaired
    data['repaired_at'] = datetime.now().isoformat()

    # Write back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return True, f"Repaired with {len(extracted_segments)} segments"


def main():
    video_index_dir = Path('memory/video_index/undaodu')
    if not video_index_dir.exists():
        print(f"ERROR: {video_index_dir} not found")
        return

    json_files = list(video_index_dir.glob('*.json'))
    print(f"Scanning {len(json_files)} video index files...")
    print("=" * 60)

    # Find zero-segment videos
    zero_segment_videos = []
    for jf in json_files:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        segments = data.get('audio', {}).get('segments', [])
        if len(segments) == 0:
            zero_segment_videos.append(jf)

    print(f"Found {len(zero_segment_videos)} zero-segment videos")
    print("=" * 60)

    repaired = 0
    failed = 0

    for jf in zero_segment_videos:
        success, message = repair_video(jf)
        status = "REPAIRED" if success else "FAILED"
        print(f"[{status}] {jf.stem}: {message}")
        if success and "Already has" not in message:
            repaired += 1
        elif not success:
            failed += 1

    print("=" * 60)
    print(f"Summary: {repaired} repaired, {failed} failed")

    # Verify repair
    if repaired > 0:
        print("\nVerification:")
        for jf in zero_segment_videos[:3]:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            segs = len(data.get('audio', {}).get('segments', []))
            title = data.get('title', 'No title')[:40]
            print(f"  {jf.stem}: {segs} segments | {title}")


if __name__ == '__main__':
    main()
