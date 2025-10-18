#!/usr/bin/env python
"""
Test YouTube Comment APIs - Read and interact with Move2Japan comments
Per WSP 84: Using existing youtube_auth module, no vibecoding
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from modules.platform_integration.youtube_auth.src.youtube_auth import (
    get_authenticated_service,
    list_video_comments,
    reply_to_comment,
    get_latest_video_id,
    like_comment
)
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Move2Japan channel ID
MOVE2JAPAN_CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"

def test_comment_reading():
    """Test reading comments from latest Move2Japan video"""
    try:
        # Get authenticated YouTube service
        logger.info("[U+1F510] Authenticating with YouTube...")
        youtube = get_authenticated_service()
        
        # Get channel info to confirm we're authenticated
        channel_response = youtube.channels().list(
            part='snippet',
            mine=True
        ).execute()
        
        if channel_response.get('items'):
            auth_channel = channel_response['items'][0]['snippet']['title']
            logger.info(f"[OK] Authenticated as: {auth_channel}")
        
        # Get latest video from Move2Japan
        logger.info(f"[CAMERA] Getting latest video from Move2Japan...")
        latest_video_id = get_latest_video_id(youtube, MOVE2JAPAN_CHANNEL_ID)
        
        if not latest_video_id:
            logger.error("[FAIL] Could not find latest video")
            return
        
        logger.info(f"[U+1F4F9] Latest video ID: {latest_video_id}")
        logger.info(f"[LINK] Video URL: https://youtube.com/watch?v={latest_video_id}")
        
        # List comments on the video
        logger.info("[U+1F4AC] Fetching comments...")
        comments = list_video_comments(youtube, latest_video_id, max_results=10)
        
        if not comments:
            logger.warning("No comments found on this video")
            return
        
        logger.info(f"Found {len(comments)} comment threads")
        logger.info("-" * 60)
        
        # Display comments
        for i, comment_thread in enumerate(comments, 1):
            snippet = comment_thread['snippet']['topLevelComment']['snippet']
            author = snippet['authorDisplayName']
            text = snippet['textDisplay']
            likes = snippet.get('likeCount', 0)
            comment_id = comment_thread['id']
            
            logger.info(f"\n#{i} Comment by {author} ({likes} likes)")
            logger.info(f"   ID: {comment_id}")
            logger.info(f"   Text: {text[:200]}...")
            
            # Check if comment can be replied to
            can_reply = comment_thread['snippet'].get('canReply', False)
            logger.info(f"   Can reply: {can_reply}")
            
            # Show replies if any
            reply_count = comment_thread['snippet'].get('totalReplyCount', 0)
            if reply_count > 0:
                logger.info(f"   Has {reply_count} replies")
                
                # Show first reply if available
                if 'replies' in comment_thread:
                    first_reply = comment_thread['replies']['comments'][0]['snippet']
                    logger.info(f"     Reply by {first_reply['authorDisplayName']}: {first_reply['textDisplay'][:100]}...")
        
        logger.info("-" * 60)
        
        # Test liking a comment (Note: API doesn't support this)
        logger.info("\n[U+1F90D] Testing comment liking...")
        result = like_comment(youtube, comments[0]['id'])
        if not result:
            logger.info("ℹ️ YouTube API doesn't support liking comments directly")
            logger.info("   Comments can only be liked through the YouTube UI")
        
        # Offer to post a test reply
        logger.info("\n[U+1F4AC] Ready to test replying to comments")
        logger.info("To test replying, uncomment the reply code below")
        
        # UNCOMMENT TO TEST REPLYING (costs 50 quota units!)
        # if comments and comments[0]['snippet'].get('canReply', False):
        #     test_reply = "Great video! [U+1F38C] (This is a test from 0102 UnDaoDu bot)"
        #     logger.info(f"Posting test reply: {test_reply}")
        #     response = reply_to_comment(youtube, comments[0]['id'], test_reply)
        #     if response:
        #         logger.info("[OK] Successfully posted reply!")
        #     else:
        #         logger.error("[FAIL] Failed to post reply")
        
        return comments
        
    except Exception as e:
        logger.error(f"[FAIL] Error in comment test: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_video_rating():
    """Test rating/liking a video (this is what YouTube supports instead of comment likes)"""
    try:
        youtube = get_authenticated_service()
        
        # Get latest video
        latest_video_id = get_latest_video_id(youtube, MOVE2JAPAN_CHANNEL_ID)
        
        if latest_video_id:
            logger.info(f"\n[U+1F44D] Testing video rating/liking...")
            logger.info(f"Video ID: {latest_video_id}")
            
            # Rate the video as 'like'
            try:
                request = youtube.videos().rate(
                    id=latest_video_id,
                    rating='like'  # Options: 'like', 'dislike', 'none'
                )
                request.execute()
                logger.info("[OK] Successfully liked the video!")
            except Exception as e:
                logger.error(f"[FAIL] Error liking video: {e}")
                
    except Exception as e:
        logger.error(f"Error in video rating test: {e}")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("YouTube Comment API Test - Move2Japan Channel")
    logger.info("=" * 60)
    
    # Test reading comments
    comments = test_comment_reading()
    
    # Test liking a video (since we can't like comments)
    test_video_rating()
    
    logger.info("\n[OK] Test complete!")
    logger.info("Note: YouTube API limitations:")
    logger.info("  - Cannot like individual comments via API")
    logger.info("  - Can like videos via API")
    logger.info("  - Can reply to comments (costs 50 units)")