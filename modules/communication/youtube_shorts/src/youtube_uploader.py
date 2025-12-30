"""
YouTube Shorts Uploader

Uploads videos as YouTube Shorts using existing youtube_auth module.
Read-only integration - ZERO modifications to youtube_auth.

WSP Compliance:
- Comprehensive daemon logging for upload monitoring
- Step-by-step progress tracking
- Integration with main.py DAE logging system
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Optional
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import google.oauth2.credentials
from google.auth.transport.requests import Request

# Initialize logger for daemon monitoring
logger = logging.getLogger(__name__)


class YouTubeUploadError(Exception):
    """YouTube upload failed"""
    pass


class YouTubeShortsUploader:
    """
    YouTube Shorts upload handler.

    Uses existing youtube_auth OAuth for authentication.
    Standalone module - no modifications to youtube_auth.
    """

    def __init__(self, channel: str = "move2japan"):
        """
        Initialize uploader with existing YouTube OAuth.

        Args:
            channel: Which channel to use ("move2japan" or "undaodu")
                    - "move2japan": Set 2 (oauth_token2.json) - Move2Japan channel
                    - "undaodu": Set 1 (oauth_token.json) - UnDaoDu channel

        Uses youtube_auth.get_authenticated_service() - read-only.
        """
        # Map channel names to token files
        token_files = {
            "move2japan": "credentials/oauth_token2.json",  # Set 2
            "undaodu": "credentials/oauth_token.json"       # Set 1
        }

        if channel not in token_files:
            raise YouTubeUploadError(f"Unknown channel: {channel}. Use 'move2japan' or 'undaodu'")

        token_file = token_files[channel]

        # Verify token file exists
        if not Path(token_file).exists():
            raise YouTubeUploadError(
                f"Token file not found: {token_file}\n"
                f"Run: python modules/platform_integration/youtube_auth/scripts/authorize_set2.py"
            )

        try:
            logger.info(f"[U+1F510] [UPLOAD-AUTH] Loading OAuth credentials from {token_file}")
            # Load credentials from token file
            with open(token_file, 'r') as f:
                creds_data = json.load(f)

            # Create credentials object
            creds = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_data)

            # Refresh if expired
            if creds.expired and creds.refresh_token:
                logger.info("[REFRESH] [UPLOAD-AUTH] Refreshing expired OAuth token...")
                creds.refresh(Request())

                # Save refreshed token
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())
                logger.info("[OK] [UPLOAD-AUTH] OAuth token refreshed and saved")

            # Build YouTube API service
            # Disable discovery caching to avoid noisy `googleapiclient.discovery_cache` logs on Windows.
            self.youtube = build('youtube', 'v3', credentials=creds, cache_discovery=False)
            self.channel = channel
            logger.info(f"[OK] [UPLOAD-INIT] YouTube API service initialized for {channel.upper()} channel")

        except Exception as e:
            logger.error(f"[FAIL] [UPLOAD-ERROR] Failed to initialize YouTube auth: {e}")
            raise YouTubeUploadError(f"Failed to get YouTube auth for {channel}: {e}")

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        privacy: str = "public"
    ) -> str:
        """
        Upload video as YouTube Short.

        Args:
            video_path: Path to .mp4 file
            title: Video title (max 100 chars)
            description: Video description
            tags: List of tags (default: ["Shorts", "Japan", "Move2Japan"])
            privacy: "public", "unlisted", or "private" (default: "public")

        Returns:
            str: YouTube Shorts URL (https://youtube.com/shorts/VIDEO_ID)

        Raises:
            YouTubeUploadError: If upload fails
        """

        logger.info("[U+1F4E4] [UPLOAD-START] Starting YouTube Short upload")
        logger.info(f"[NOTE] [UPLOAD-START] Title: {title}")
        logger.info(f"[U+1F4C1] [UPLOAD-START] File: {video_path}")
        logger.info(f"[LOCK] [UPLOAD-START] Privacy: {privacy}")

        # Validate file exists
        if not Path(video_path).exists():
            logger.error(f"[FAIL] [UPLOAD-ERROR] Video file not found: {video_path}")
            raise YouTubeUploadError(f"Video file not found: {video_path}")

        # Default tags
        if tags is None:
            tags = ["Shorts", "Japan", "Move2Japan"]

        # Ensure #Shorts in description for proper categorization
        if "#Shorts" not in description and "#shorts" not in description:
            description = description + " #Shorts"
            logger.info("[OK] [UPLOAD-PREP] Added #Shorts tag to description")

        logger.info(f"[U+1F3F7]️  [UPLOAD-PREP] Tags: {', '.join(tags)}")

        try:
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": title[:100],  # YouTube max 100 chars
                    "description": description,
                    "tags": tags,
                    "categoryId": "22"  # Category 22 = People & Blogs (good for Shorts)
                },
                "status": {
                    "privacyStatus": privacy,
                    "selfDeclaredMadeForKids": False
                }
            }
            logger.info("[CLIPBOARD] [UPLOAD-PREP] Video metadata prepared")
            logger.info("[U+1F4C2] [UPLOAD-PREP] Category: 22 (People & Blogs)")

            # Create media upload
            media = MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            logger.info("[BOX] [UPLOAD-PREP] Media upload object created (1MB chunks)")

            # Execute upload
            logger.info("[ROCKET] [UPLOAD-PROGRESS] Starting YouTube API upload...")

            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            last_logged = -10  # Track last logged progress
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    # Log every 10% to avoid spam
                    if progress >= last_logged + 10:
                        logger.info(f"[DATA] [UPLOAD-PROGRESS] Upload progress: {progress}%")
                        last_logged = progress

            # Get video ID
            video_id = response['id']
            logger.info(f"[OK] [UPLOAD-SUCCESS] Upload complete! Video ID: {video_id}")

            # Construct Shorts URL
            # YouTube automatically detects vertical videos <60s as Shorts
            shorts_url = f"https://youtube.com/shorts/{video_id}"

            logger.info(f"[U+1F3AC] [UPLOAD-SUCCESS] Shorts URL: {shorts_url}")
            logger.info(f"[U+1F4FA] [UPLOAD-SUCCESS] Channel: {self.channel.upper()}")

            return shorts_url

        except Exception as e:
            logger.error(f"[FAIL] [UPLOAD-ERROR] Upload failed: {e}")
            raise YouTubeUploadError(f"Upload failed: {e}")

    def get_channel_info(self) -> dict:
        """
        Get current YouTube channel information.

        Returns:
            dict: Channel metadata (id, title, subscriber count)
        """
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()

            if 'items' not in response or len(response['items']) == 0:
                return {"error": "No channel found"}

            channel = response['items'][0]

            return {
                "id": channel['id'],
                "title": channel['snippet']['title'],
                "subscribers": channel['statistics'].get('subscriberCount', 'N/A'),
                "video_count": channel['statistics'].get('videoCount', 'N/A')
            }

        except Exception as e:
            return {"error": str(e)}

    def list_recent_shorts(self, max_results: int = 10) -> list:
        """
        List recently uploaded Shorts on the channel.

        Args:
            max_results: Number of Shorts to retrieve (default: 10)

        Returns:
            list: List of Short metadata dicts
        """
        try:
            # Get channel's uploads playlist
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()

            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # Get recent uploads
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()

            shorts = []

            for item in playlist_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']

                shorts.append({
                    "video_id": video_id,
                    "title": item['snippet']['title'],
                    "url": f"https://youtube.com/shorts/{video_id}",
                    "published_at": item['snippet']['publishedAt']
                })

            return shorts

        except Exception as e:
            print(f"[YouTubeUploader] Error listing Shorts: {e}")
            return []


if __name__ == "__main__":
    # Test the uploader
    uploader = YouTubeShortsUploader()

    # Get channel info
    channel = uploader.get_channel_info()
    print(f"\nChannel: {channel}")

    # List recent Shorts
    shorts = uploader.list_recent_shorts(max_results=5)
    print(f"\nRecent Shorts: {len(shorts)}")
    for short in shorts:
        print(f"  - {short['title']} ({short['url']})")
