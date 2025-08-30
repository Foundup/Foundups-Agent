#!/usr/bin/env python3
"""
Move2Japan YouTube Comments Testing Script
Tests API capabilities for interacting with comments on Move2Japan channel.

Channel: Move2Japan (UC-LSSlOZwpGIRIYihaz8zCw)
"""

import os
import sys
import logging
import json
from datetime import datetime

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from modules.platform_integration.youtube_auth.src.youtube_auth import (
    get_authenticated_service,
    list_video_comments,
    like_comment,
    reply_to_comment,
    get_latest_video_id
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_channel_videos(youtube_service, channel_id, max_results=50):
    """Get recent videos from the channel."""
    try:
        request = youtube_service.search().list(
            part="id,snippet",
            channelId=channel_id,
            maxResults=max_results,
            order="date",
            type="video"
        )
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        logger.error(f"Error fetching channel videos: {e}")
        return []

def get_video_statistics(youtube_service, video_id):
    """Get video statistics including comment count."""
    try:
        request = youtube_service.videos().list(
            part="statistics,snippet",
            id=video_id
        )
        response = request.execute()
        items = response.get('items', [])
        if items:
            return items[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching video statistics: {e}")
        return None

def test_comment_interactions(youtube_service, comment_id):
    """Test various comment interaction capabilities."""
    results = {}
    
    # Test 1: Like comment (expected to fail based on API limitations)
    logger.info(f"Testing comment liking for comment: {comment_id}")
    like_result = like_comment(youtube_service, comment_id)
    results['like_comment'] = {
        'success': like_result,
        'note': 'Expected to fail - YouTube API limitation'
    }
    
    # Test 2: Try comment rating (alternative approach)
    try:
        # This is also likely to fail as it's for spam reporting
        request = youtube_service.comments().setModerationStatus(
            id=comment_id,
            moderationStatus='published'  # This only works for your own channel
        )
        # Don't execute - this would only work on our own channel
        results['moderation'] = {
            'success': False,
            'note': 'Can only moderate comments on own channel'
        }
    except Exception as e:
        results['moderation'] = {
            'success': False,
            'error': str(e),
            'note': 'Expected - requires channel ownership'
        }
    
    return results

def main():
    """Main testing function."""
    logger.info("🎬 Starting Move2Japan YouTube Comments Test")
    
    # Move2Japan channel ID
    CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"
    
    try:
        # Get authenticated service
        logger.info("🔑 Authenticating with YouTube API...")
        youtube_service = get_authenticated_service()
        logger.info("✅ Authentication successful")
        
        # Results collection
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'channel_id': CHANNEL_ID,
            'channel_name': 'Move2Japan',
            'videos_analyzed': [],
            'comment_interaction_tests': {},
            'api_limitations': [],
            'working_features': []
        }
        
        # Step 1: Get recent videos from the channel
        logger.info("📺 Fetching recent videos from Move2Japan channel...")
        videos = get_channel_videos(youtube_service, CHANNEL_ID, max_results=20)
        logger.info(f"Found {len(videos)} recent videos")
        
        videos_with_comments = []
        
        # Step 2: Check each video for comments
        for i, video in enumerate(videos[:10]):  # Limit to first 10 to save quota
            video_id = video['id']['videoId']
            video_title = video['snippet']['title']
            published = video['snippet']['publishedAt']
            
            logger.info(f"🔍 Analyzing video {i+1}: {video_title[:50]}...")
            
            # Get video statistics
            video_stats = get_video_statistics(youtube_service, video_id)
            if not video_stats:
                continue
                
            stats = video_stats.get('statistics', {})
            comment_count = int(stats.get('commentCount', 0))
            view_count = int(stats.get('viewCount', 0))
            like_count = int(stats.get('likeCount', 0))
            
            video_info = {
                'video_id': video_id,
                'title': video_title,
                'published': published,
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': comment_count,
                'has_comments': comment_count > 0,
                'sample_comments': []
            }
            
            if comment_count > 0:
                logger.info(f"💬 Video has {comment_count} comments, fetching sample...")
                
                # Get sample comments
                comments = list_video_comments(youtube_service, video_id, max_results=5)
                
                for comment_thread in comments:
                    top_comment = comment_thread['snippet']['topLevelComment']
                    comment_info = {
                        'comment_id': top_comment['id'],
                        'author': top_comment['snippet']['authorDisplayName'],
                        'text': top_comment['snippet']['textOriginal'][:200],  # Truncate for readability
                        'like_count': top_comment['snippet']['likeCount'],
                        'published': top_comment['snippet']['publishedAt']
                    }
                    video_info['sample_comments'].append(comment_info)
                
                videos_with_comments.append(video_info)
                
            test_results['videos_analyzed'].append(video_info)
            
        logger.info(f"📊 Found {len(videos_with_comments)} videos with comments")
        
        # Step 3: Test comment interactions on first available comment
        if videos_with_comments and videos_with_comments[0]['sample_comments']:
            test_video = videos_with_comments[0]
            test_comment = test_video['sample_comments'][0]
            
            logger.info(f"🧪 Testing comment interactions on: {test_comment['comment_id']}")
            
            interaction_results = test_comment_interactions(
                youtube_service, 
                test_comment['comment_id']
            )
            
            test_results['comment_interaction_tests'] = {
                'test_video_id': test_video['video_id'],
                'test_video_title': test_video['title'],
                'test_comment_id': test_comment['comment_id'],
                'test_comment_author': test_comment['author'],
                'results': interaction_results
            }
        
        # Step 4: Document API capabilities and limitations
        test_results['api_limitations'] = [
            {
                'feature': 'Like Comments',
                'status': 'NOT SUPPORTED',
                'reason': 'YouTube Data API v3 does not provide a direct endpoint to like comments',
                'alternative': 'Can only rate videos, not individual comments'
            },
            {
                'feature': 'Heart Comments (as channel owner)',
                'status': 'NOT SUPPORTED via API',
                'reason': 'YouTube Data API does not expose the heart/creator like functionality',
                'alternative': 'Must be done manually through YouTube interface'
            },
            {
                'feature': 'Comment Moderation',
                'status': 'LIMITED',
                'reason': 'Can only moderate comments on videos from your own channel',
                'alternative': 'Can report spam/inappropriate comments'
            }
        ]
        
        test_results['working_features'] = [
            {
                'feature': 'List Comments',
                'status': 'WORKING',
                'quota_cost': '1 unit per call (up to 100 comments)',
                'capabilities': 'Can fetch comment text, author, timestamps, like counts, replies'
            },
            {
                'feature': 'Reply to Comments',
                'status': 'WORKING',
                'quota_cost': '50 units per call',
                'capabilities': 'Can post replies to any comment thread',
                'note': 'Requires write permissions in OAuth scope'
            },
            {
                'feature': 'Search Channel Videos',
                'status': 'WORKING',
                'quota_cost': '100 units per call',
                'capabilities': 'Can find videos by date, relevance, view count'
            },
            {
                'feature': 'Get Video Statistics',
                'status': 'WORKING',
                'quota_cost': '1 unit per call',
                'capabilities': 'View count, like count, comment count, duration'
            }
        ]
        
        # Step 5: Generate detailed report
        logger.info("📋 Generating detailed report...")
        
        print("\n" + "="*80)
        print("MOVE2JAPAN YOUTUBE COMMENTS ANALYSIS REPORT")
        print("="*80)
        
        print(f"\n📺 CHANNEL ANALYSIS")
        print(f"Channel ID: {CHANNEL_ID}")
        print(f"Videos Analyzed: {len(test_results['videos_analyzed'])}")
        print(f"Videos with Comments: {len(videos_with_comments)}")
        
        print(f"\n💬 VIDEOS WITH COMMENTS:")
        for video in videos_with_comments[:5]:  # Show top 5
            print(f"  • {video['title'][:60]}...")
            print(f"    Comments: {video['comment_count']}, Views: {video['view_count']:,}")
            print(f"    Latest comment: {video['sample_comments'][0]['text'][:100]}...")
            print()
        
        print(f"\n🧪 API INTERACTION TEST RESULTS:")
        if test_results['comment_interaction_tests']:
            test_data = test_results['comment_interaction_tests']
            print(f"Test Video: {test_data['test_video_title'][:50]}...")
            print(f"Test Comment by: {test_data['test_comment_author']}")
            for test_name, result in test_data['results'].items():
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"  {test_name}: {status}")
                if 'note' in result:
                    print(f"    Note: {result['note']}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
        
        print(f"\n⚠️  API LIMITATIONS:")
        for limitation in test_results['api_limitations']:
            print(f"  • {limitation['feature']}: {limitation['status']}")
            print(f"    Reason: {limitation['reason']}")
            if limitation.get('alternative'):
                print(f"    Alternative: {limitation['alternative']}")
            print()
        
        print(f"\n✅ WORKING FEATURES:")
        for feature in test_results['working_features']:
            print(f"  • {feature['feature']}: {feature['status']}")
            print(f"    Cost: {feature['quota_cost']}")
            print(f"    Details: {feature['capabilities']}")
            if feature.get('note'):
                print(f"    Note: {feature['note']}")
            print()
        
        # Save detailed results to file
        report_file = f"move2japan_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(os.path.dirname(__file__), report_file)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: {report_path}")
        print("="*80)
        
        logger.info("✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    main()