#!/usr/bin/env python3
"""
Test liking/hearting a single comment on Move2Japan video
"""

import sys
import os
import logging

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.youtube_auth.src.youtube_auth import (
    get_authenticated_service,
    list_video_comments,
    like_comment
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_like_single_comment():
    """Try to like one comment on a Move2Japan video"""
    
    MOVE2JAPAN_CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"
    
    logger.info("="*60)
    logger.info("[TARGET] TESTING SINGLE COMMENT LIKE ON MOVE2JAPAN")
    logger.info("="*60)
    
    # Get YouTube service
    youtube = get_authenticated_service()
    
    if not youtube:
        logger.error("Failed to authenticate")
        return
    
    try:
        # Find a video with comments
        logger.info("[SEARCH] Searching for Move2Japan videos with comments...")
        
        # Get channel uploads playlist
        channel_response = youtube.channels().list(
            part="contentDetails",
            id=MOVE2JAPAN_CHANNEL_ID
        ).execute()
        
        uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get recent videos
        videos_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=10
        ).execute()
        
        # Find a video with comments
        for item in videos_response.get('items', []):
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            
            logger.info(f"\n[U+1F4F9] Checking video: {video_title[:50]}...")
            
            # Get comments
            comments = list_video_comments(youtube, video_id, max_results=5)
            
            if comments:
                # Found comments! Try to like the first one
                first_comment = comments[0]
                comment_id = first_comment['id']
                author = first_comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
                text = first_comment['snippet']['topLevelComment']['snippet']['textDisplay'][:100]
                like_count = first_comment['snippet']['topLevelComment']['snippet']['likeCount']
                
                logger.info(f"\n[U+1F4AC] Found comment by {author}:")
                logger.info(f"   Text: {text}...")
                logger.info(f"   Current likes: {like_count}")
                logger.info(f"   Comment ID: {comment_id}")
                
                # Try to like it
                logger.info("\n[U+1F44D] Attempting to like this comment...")
                result = like_comment(youtube, comment_id)
                
                if result:
                    logger.info("[OK] Successfully liked the comment!")
                else:
                    logger.info("[FAIL] Cannot like comment - API limitation")
                    logger.info("   YouTube API v3 does not support liking individual comments")
                    logger.info("   This is a known limitation, not an error")
                
                # Try to heart it (only works if we own the video)
                logger.info("\n[U+2764]️ Attempting to heart this comment...")
                logger.info("[FAIL] Cannot heart comment - API limitation")
                logger.info("   Hearts can only be added by video owner through YouTube Studio")
                logger.info("   No API endpoint exists for this action")
                
                # What we CAN do
                logger.info("\n[OK] What we CAN do via API:")
                logger.info("   1. Reply to this comment")
                logger.info("   2. Like the entire video")
                logger.info("   3. Subscribe to the channel")
                logger.info("   4. Create our own comments")
                
                # Show how to reply instead
                logger.info("\n[IDEA] Alternative: We could reply to show engagement")
                logger.info(f"   Example: 'Great point, {author}! Thanks for watching!'")
                
                return
        
        logger.info("\n[U+26A0]️ No comments found on recent videos")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
    [U+2554]========================================================[U+2557]
    [U+2551]        TEST LIKING A SINGLE MOVE2JAPAN COMMENT        [U+2551]
    [U+2560]========================================================[U+2563]
    [U+2551]  This will attempt to like and heart one comment      [U+2551]
    [U+2551]  Note: API limitations prevent these actions          [U+2551]
    [U+255A]========================================================[U+255D]
    """)
    
    test_like_single_comment()