# youtube_live_audio

Domain: platform_integration
Status: POC
WSP: WSP 3, WSP 11, WSP 22, WSP 49

## Overview
youtube_live_audio resolves a YouTube live stream into a stable PCM16 mono
byte stream for downstream local STT. It is platform specific and keeps the
YouTube handling in platform_integration per WSP 3.

## Responsibilities
- Resolve a live stream URL from a channel id, video id, or URL
- Normalize audio with ffmpeg to PCM16 mono at the target sample rate
- Emit a byte stream suitable for local streaming STT

## Inputs and Outputs
Input:
- channel id, video id, or live URL

Output:
- iterable of PCM16 mono byte chunks

## Dependencies
- yt-dlp (python package or CLI)
- ffmpeg (system install)
- modules/platform_integration/stream_resolver for live stream discovery

## Integration
- modules/communication/voice_command_ingestion consumes the PCM stream
- PQN experiments can reuse this stream for voice artifact tests

## Logging
Every stage emits one structured line:
- timestamp
- stage
- latency_ms
- payload_summary

## Roadmap
See ROADMAP.md for the phased build plan.
