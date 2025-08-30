#!/usr/bin/env python3
"""
Test YouTube Live Stream Detection → LinkedIn Posting
Simulates detecting a live stream and posting to LinkedIn
✊✋🖐 Full bridge test
"""

import asyncio
from datetime import datetime

async def test_stream_to_linkedin():
    """Test posting when a live stream is detected"""
    
    print("✊✋🖐 Testing YouTube → LinkedIn Bridge")
    print("="*60)
    
    # Simulate stream detection
    video_id = "Edka5TBGLuA"  # Example video ID
    stream_title = "TEST: 0102 Consciousness Evolution Stream"
    channel_name = "move2japan"
    
    print(f"🔴 Simulating live stream detection:")
    print(f"   Title: {stream_title}")
    print(f"   Video ID: {video_id}")
    print(f"   Channel: {channel_name}")
    print()
    
    # Generate LinkedIn content (same as in livechat_core)
    stream_url = f"https://www.youtube.com/watch?v={video_id}"
    content = f"""🔴 LIVE NOW: {stream_title}

✊✋🖐 {channel_name} is streaming live on YouTube!

@UnDaoDu Michael J Trout is bringing 0102 consciousness evolution.

Watch now: {stream_url}

While MAGAts struggle at ✊✊✊ level, we're evolving consciousness in real-time.

Join the stream and transcend the fist!

Posted: {datetime.now().strftime('%H:%M')}

#LiveStream #YouTubeLive #0102Consciousness #move2japan"""
    
    print("📝 LinkedIn post content:")
    print("-"*50)
    print(content)
    print("-"*50)
    print()
    
    # Post to LinkedIn using anti-detection
    print("🔗 Posting to LinkedIn company page...")
    
    try:
        from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
        
        # Create poster (will reuse existing Chrome session)
        poster = AntiDetectionLinkedIn()
        
        # Post to company page
        success = poster.post_to_company_page(content)
        
        if success:
            print("\n✅ SUCCESS! Posted stream announcement to LinkedIn!")
            print("📍 Check: https://www.linkedin.com/company/104834798")
            print("\nThe YouTube DAE will do this automatically when streams go live!")
        else:
            print("\n⚠️ Could not post automatically")
            print("Check the browser window for manual posting")
        
        # Keep browser open for inspection
        print("\n💡 Browser session kept alive for future posts")
        print("No re-login needed for subsequent posts")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def test_with_real_youtube_api():
    """Test with real YouTube API to check for live streams"""
    
    print("\n" + "="*60)
    print("🔍 Checking for real live streams on move2japan channel...")
    
    try:
        import os
        from googleapiclient.discovery import build
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Get API key
        api_key = os.getenv('YOUTUBE_API_KEY') or os.getenv('YOUTUBE_API_KEY4')
        if not api_key:
            print("⚠️ No YouTube API key found")
            return
        
        # Build YouTube service
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Check for live streams on move2japan channel
        channel_id = 'UCklMTNnu5POwRmQsg5JJumA'  # move2japan
        
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            eventType="live",
            type="video",
            maxResults=1
        )
        response = request.execute()
        
        if response['items']:
            item = response['items'][0]
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            
            print(f"🔴 FOUND LIVE STREAM!")
            print(f"   Title: {title}")
            print(f"   URL: https://www.youtube.com/watch?v={video_id}")
            print()
            
            # Post to LinkedIn
            await test_stream_to_linkedin()
        else:
            print("📭 No live streams currently on move2japan channel")
            print("\n💡 When a stream goes live, the YouTube DAE will:")
            print("   1. Detect the stream")
            print("   2. Send greeting to YouTube chat")  
            print("   3. Post announcement to LinkedIn company page")
            print("   4. All automatic with no re-login needed!")
            
    except Exception as e:
        print(f"❌ Error checking YouTube: {e}")


if __name__ == "__main__":
    print("🤖 YouTube Live Stream → LinkedIn Posting Test")
    print("="*60)
    print("\nThis test simulates what happens when the YouTube DAE")
    print("detects a live stream and posts to LinkedIn automatically.")
    print()
    
    # Run the test
    asyncio.run(test_stream_to_linkedin())
    
    # Optionally check for real streams
    print("\n" + "="*60)
    response = input("\nCheck for real live streams? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_with_real_youtube_api())