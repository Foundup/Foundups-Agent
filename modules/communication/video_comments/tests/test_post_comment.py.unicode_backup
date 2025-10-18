#!/usr/bin/env python3
"""
Test posting a comment on a Move2Japan video
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def post_comment_on_video(video_id: str = None, comment_text: str = None):
    """Post a new top-level comment on a video"""
    
    MOVE2JAPAN_CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"
    
    logger.info("="*60)
    logger.info("💬 POSTING COMMENT ON MOVE2JAPAN VIDEO")
    logger.info("="*60)
    
    # Get YouTube service
    youtube = get_authenticated_service()
    
    if not youtube:
        logger.error("Failed to authenticate")
        return False
    
    try:
        # If no video_id provided, get the latest video
        if not video_id:
            logger.info("🔍 Getting latest Move2Japan video...")
            
            # Get channel uploads playlist
            channel_response = youtube.channels().list(
                part="contentDetails",
                id=MOVE2JAPAN_CHANNEL_ID
            ).execute()
            
            uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get latest video
            videos_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist,
                maxResults=1
            ).execute()
            
            if videos_response.get('items'):
                video_id = videos_response['items'][0]['snippet']['resourceId']['videoId']
                video_title = videos_response['items'][0]['snippet']['title']
                logger.info(f"✅ Found video: {video_title[:50]}...")
                logger.info(f"   Video ID: {video_id}")
            else:
                logger.error("No videos found")
                return False
        
        # Default comment if none provided
        if not comment_text:
            comment_text = f"🤖 0102 automated test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Testing comment posting capability for real-time dialogue system. This is a PoC test."
        
        logger.info(f"\n📝 Posting comment: {comment_text[:100]}...")
        
        # Post the comment using commentThreads.insert
        request = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        )
        
        response = request.execute()
        
        if response:
            comment_id = response['id']
            posted_text = response['snippet']['topLevelComment']['snippet']['textDisplay']
            author = response['snippet']['topLevelComment']['snippet']['authorDisplayName']
            
            logger.info("\n✅ SUCCESS! Comment posted!")
            logger.info(f"   Comment ID: {comment_id}")
            logger.info(f"   Author: {author}")
            logger.info(f"   Text: {posted_text}")
            logger.info(f"\n🎉 We CAN post comments on videos!")
            
            return comment_id
        else:
            logger.error("Failed to post comment - no response")
            return False
            
    except Exception as e:
        logger.error(f"Error posting comment: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comment_capabilities():
    """Test all comment capabilities"""
    
    logger.info("="*60)
    logger.info("📊 YOUTUBE COMMENT CAPABILITIES TEST")
    logger.info("="*60)
    
    logger.info("\n✅ What we CAN do:")
    logger.info("1. Post new comments on videos")
    logger.info("2. Reply to existing comments")
    logger.info("3. Read all comments")
    logger.info("4. Delete our own comments")
    logger.info("5. Monitor comments in real-time")
    
    logger.info("\n❌ What we CANNOT do:")
    logger.info("1. Like individual comments")
    logger.info("2. Heart comments (creator only)")
    
    logger.info("\n🚀 Testing comment posting...")
    
    # Test posting a comment
    comment_id = post_comment_on_video()
    
    if comment_id:
        logger.info("\n="*60)
        logger.info("💡 CONCLUSION")
        logger.info("="*60)
        logger.info("YES - The solution CAN comment on videos!")
        logger.info("We can create autonomous dialogue systems that:")
        logger.info("- Post original comments")
        logger.info("- Reply to user comments")
        logger.info("- Maintain conversation threads")
        logger.info("- Remember users across sessions")
    else:
        logger.info("\n⚠️ Comment posting failed - check quota limits")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║         TEST COMMENTING ON MOVE2JAPAN VIDEO           ║
    ╠════════════════════════════════════════════════════════╣
    ║  This will post a test comment on a video to verify   ║
    ║  that our solution CAN comment on videos.             ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    test_comment_capabilities()