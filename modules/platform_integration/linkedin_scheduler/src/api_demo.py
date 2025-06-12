"""
LinkedIn Scheduler API Integration Demo
Demonstrates real LinkedIn API v2 integration capabilities
"""

import logging
from datetime import datetime, timedelta
from linkedin_scheduler import LinkedInScheduler, PostQueue, LinkedInAPIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_oauth_flow():
    """Demonstrate LinkedIn OAuth 2.0 flow setup"""
    logger.info("=== LinkedIn OAuth 2.0 Flow Demo ===")
    
    # Initialize scheduler with demo credentials
    scheduler = LinkedInScheduler(
        client_id="your_client_id_here",
        client_secret="your_client_secret_here"
    )
    
    # Generate OAuth URL
    redirect_uri = "https://your-app.com/auth/linkedin/callback"
    oauth_url = scheduler.get_oauth_url(redirect_uri, state="demo_state_123")
    
    logger.info(f"📱 OAuth URL Generated:")
    logger.info(f"   {oauth_url}")
    logger.info(f"📋 Steps to authenticate:")
    logger.info(f"   1. Visit the OAuth URL above")
    logger.info(f"   2. Login to LinkedIn and authorize your app")
    logger.info(f"   3. LinkedIn will redirect to your callback URL with 'code' parameter")
    logger.info(f"   4. Use exchange_code_for_token() to get access token")
    
    return scheduler


def demo_api_capabilities():
    """Demonstrate LinkedIn API posting capabilities"""
    logger.info("\n=== LinkedIn API Capabilities Demo ===")
    
    scheduler = LinkedInScheduler(
        client_id="demo_client_id",
        client_secret="demo_client_secret"
    )
    
    # Demo profile and token (these would be real in production)
    demo_profile = "urn:li:person:demo123"
    demo_token = "demo_access_token"
    
    logger.info(f"📝 Supported Post Types:")
    logger.info(f"   ✅ Text Posts: Simple text-only LinkedIn posts")
    logger.info(f"   ✅ Article Posts: Posts with URL attachments and metadata")
    logger.info(f"   🔄 Image Posts: (Implementation ready for asset upload flow)")
    logger.info(f"   🔄 Video Posts: (Implementation ready for asset upload flow)")
    
    logger.info(f"\n📊 Rate Limits (per LinkedIn documentation):")
    logger.info(f"   • Member Daily: {scheduler.RATE_LIMITS['member_daily']} requests")
    logger.info(f"   • Application Daily: {scheduler.RATE_LIMITS['app_daily']} requests")
    logger.info(f"   • Recommended: {scheduler.RATE_LIMITS['posts_per_hour']} posts/hour")
    
    logger.info(f"\n🔐 Authentication Requirements:")
    logger.info(f"   • OAuth 2.0 scope: 'w_member_social'")
    logger.info(f"   • Required headers: X-Restli-Protocol-Version: 2.0.0")
    logger.info(f"   • API endpoint: {scheduler.UGC_POSTS_ENDPOINT}")
    
    return scheduler


def demo_text_post_structure():
    """Demonstrate text post API structure"""
    logger.info("\n=== Text Post API Structure Demo ===")
    
    sample_post = {
        "author": "urn:li:person:8675309",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Hello World! This is my first automated LinkedIn post! 🚀"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    logger.info(f"📋 Sample Text Post JSON Structure:")
    import json
    logger.info(json.dumps(sample_post, indent=2))
    
    return sample_post


def demo_article_post_structure():
    """Demonstrate article post API structure"""
    logger.info("\n=== Article Post API Structure Demo ===")
    
    sample_article = {
        "author": "urn:li:person:8675309",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Great insights on professional networking! 💼"
                },
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Learn about building meaningful professional relationships"
                        },
                        "originalUrl": "https://blog.linkedin.com/professional-networking",
                        "title": {
                            "text": "The Art of Professional Networking"
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    logger.info(f"📋 Sample Article Post JSON Structure:")
    import json
    logger.info(json.dumps(sample_article, indent=2))
    
    return sample_article


def demo_queue_management():
    """Demonstrate advanced queue management capabilities"""
    logger.info("\n=== Advanced Queue Management Demo ===")
    
    scheduler = LinkedInScheduler()
    queue = PostQueue(scheduler)
    
    # Simulate adding posts to queue
    future_time = datetime.now() + timedelta(hours=1)
    
    logger.info(f"📅 Adding sample posts to queue:")
    
    # Add text post
    text_post_id = queue.add_post(
        profile_id="urn:li:person:demo123",
        content="Excited to share my latest project insights! #innovation",
        schedule_time=future_time,
        post_type="text",
        visibility="PUBLIC"
    )
    logger.info(f"   ✅ Added text post: {text_post_id}")
    
    # Add article post
    article_post_id = queue.add_post(
        profile_id="urn:li:person:demo123",
        content="Great article on emerging tech trends!",
        schedule_time=future_time + timedelta(minutes=30),
        post_type="article",
        article_url="https://example.com/tech-trends",
        title="Tech Trends 2025",
        description="Analysis of upcoming technology developments",
        visibility="PUBLIC"
    )
    logger.info(f"   ✅ Added article post: {article_post_id}")
    
    # Show queue status
    status = queue.get_queue_status()
    logger.info(f"\n📊 Queue Status:")
    logger.info(f"   • Queued: {status['queued']}")
    logger.info(f"   • Processed: {status['processed']}")
    logger.info(f"   • Failed: {status['failed']}")
    logger.info(f"   • Total: {status['total']}")
    logger.info(f"   • Next Scheduled: {status['next_scheduled']}")
    
    logger.info(f"\n🔄 Queue Features:")
    logger.info(f"   ✅ Automatic retry logic with exponential backoff")
    logger.info(f"   ✅ Rate limit awareness and spacing")
    logger.info(f"   ✅ Comprehensive error handling and logging")
    logger.info(f"   ✅ Support for multiple post types and profiles")
    
    return queue


def demo_integration_workflow():
    """Demonstrate complete integration workflow"""
    logger.info("\n=== Complete Integration Workflow Demo ===")
    
    logger.info(f"🔄 Typical 012 Observer → 0102 Executor Workflow:")
    logger.info(f"   1. 012 Observer identifies content to share")
    logger.info(f"   2. Content is analyzed and formatted for LinkedIn")
    logger.info(f"   3. Optimal posting time is calculated")
    logger.info(f"   4. Post is added to scheduler queue")
    logger.info(f"   5. 0102 Executor processes queue at scheduled time")
    logger.info(f"   6. LinkedIn API call is made with proper authentication")
    logger.info(f"   7. Result is logged and any failures are retried")
    logger.info(f"   8. Success metrics are tracked for optimization")
    
    logger.info(f"\n💡 Key Benefits:")
    logger.info(f"   🎯 Automated content distribution")
    logger.info(f"   📈 Consistent professional presence")
    logger.info(f"   ⏰ Optimal timing for maximum engagement")
    logger.info(f"   🔒 Secure OAuth 2.0 authentication")
    logger.info(f"   📊 Built-in rate limiting and error handling")
    logger.info(f"   🔄 Automatic retry logic for resilience")


def run_complete_demo():
    """Run the complete LinkedIn API integration demo"""
    logger.info("🚀 LinkedIn Scheduler API Integration Demo")
    logger.info("=" * 60)
    
    try:
        # Demo OAuth flow setup
        scheduler = demo_oauth_flow()
        
        # Demo API capabilities
        demo_api_capabilities()
        
        # Demo post structures
        demo_text_post_structure()
        demo_article_post_structure()
        
        # Demo queue management
        demo_queue_management()
        
        # Demo integration workflow
        demo_integration_workflow()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Demo completed successfully!")
        logger.info("📚 Ready for production LinkedIn API integration")
        logger.info("🔧 Configure with real LinkedIn app credentials to go live")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    run_complete_demo() 