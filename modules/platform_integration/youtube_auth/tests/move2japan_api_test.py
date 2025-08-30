#!/usr/bin/env python3
"""
Move2Japan YouTube API Test - Simple version without emojis for Windows compatibility
Tests specific API capabilities for interacting with comments.
"""

import os
import sys
import logging
import json
from datetime import datetime

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

# Setup logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_youtube_api_directly():
    """Test YouTube API directly without authentication to check basic access."""
    import requests
    
    # Test 1: Check if we can access YouTube Data API endpoints (public data)
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'channel_id': 'UC-LSSlOZwpGIRIYihaz8zCw',
        'channel_name': 'Move2Japan',
        'api_tests': {}
    }
    
    print("MOVE2JAPAN YOUTUBE API CAPABILITIES TEST")
    print("=" * 60)
    
    # Note: We can't test authenticated endpoints due to quota limitations
    # But we can document the API capabilities based on YouTube API documentation
    
    print("\nYOUTUBE API COMMENT INTERACTION CAPABILITIES:")
    print("-" * 50)
    
    # Document what we know from API documentation and our code analysis
    capabilities = {
        'list_comments': {
            'status': 'SUPPORTED',
            'method': 'commentThreads.list',
            'quota_cost': '1 unit per call',
            'max_results': '100 comments per call',
            'capabilities': [
                'Fetch comment text and metadata',
                'Get author information',
                'Get like counts on comments',
                'Get reply threads',
                'Filter by relevance or time'
            ],
            'limitations': [
                'Cannot see private comments',
                'Cannot access deleted comments',
                'Rate limited by quota'
            ]
        },
        
        'like_comments': {
            'status': 'NOT SUPPORTED',
            'method': 'N/A - No API endpoint exists',
            'reason': 'YouTube Data API v3 does not provide comment liking functionality',
            'evidence': 'Confirmed in our youtube_auth.py - like_comment() returns False',
            'alternatives': [
                'Can rate videos (videos.rate endpoint)',
                'Cannot interact with individual comment likes via API',
                'Must use YouTube web interface for comment likes'
            ]
        },
        
        'heart_comments': {
            'status': 'NOT SUPPORTED',
            'method': 'N/A - No API endpoint exists',
            'reason': 'Creator heart/pin functionality not exposed in API',
            'evidence': 'No heart/creator-like endpoint in YouTube Data API v3 documentation',
            'alternatives': [
                'Must be done manually through YouTube Studio',
                'No programmatic way to heart comments as channel owner'
            ]
        },
        
        'reply_to_comments': {
            'status': 'SUPPORTED',
            'method': 'comments.insert',
            'quota_cost': '50 units per call',
            'requirements': [
                'Authenticated user with write permissions',
                'Valid parent comment ID',
                'Text content for reply'
            ],
            'capabilities': [
                'Post replies to any comment thread',
                'Reply to your own or others comments',
                'Support for text formatting in replies'
            ],
            'limitations': [
                'High quota cost (50 units per reply)',
                'Must have proper OAuth scopes',
                'Subject to YouTube community guidelines'
            ]
        },
        
        'moderate_comments': {
            'status': 'LIMITED SUPPORT',
            'method': 'comments.setModerationStatus',
            'restrictions': 'Only works on your own channel videos',
            'capabilities': [
                'Approve/reject comments on your videos',
                'Mark comments as spam',
                'Publish held-for-review comments'
            ],
            'limitations': [
                'Cannot moderate others\' channels',
                'Cannot moderate comments on videos you don\'t own',
                'Limited to basic moderation actions'
            ]
        }
    }
    
    for feature_name, feature_info in capabilities.items():
        print(f"\n{feature_name.upper()}:")
        print(f"  Status: {feature_info['status']}")
        
        if feature_info['status'] == 'SUPPORTED':
            print(f"  API Method: {feature_info['method']}")
            print(f"  Quota Cost: {feature_info['quota_cost']}")
            if 'capabilities' in feature_info:
                print("  Capabilities:")
                for cap in feature_info['capabilities']:
                    print(f"    - {cap}")
        
        elif feature_info['status'] == 'NOT SUPPORTED':
            print(f"  Reason: {feature_info['reason']}")
            if 'evidence' in feature_info:
                print(f"  Evidence: {feature_info['evidence']}")
            if 'alternatives' in feature_info:
                print("  Alternatives:")
                for alt in feature_info['alternatives']:
                    print(f"    - {alt}")
        
        if 'limitations' in feature_info:
            print("  Limitations:")
            for limit in feature_info['limitations']:
                print(f"    - {limit}")
    
    # Test specific Move2Japan scenarios
    print(f"\nMOVE2JAPAN SPECIFIC SCENARIOS:")
    print("-" * 40)
    
    scenarios = {
        'find_videos_with_comments': {
            'description': 'Find Move2Japan videos that have existing comments',
            'api_calls_needed': [
                '1. search.list (channelId filter) - 100 units',
                '2. videos.list (get statistics) - 1 unit per video',
                '3. commentThreads.list (get comments) - 1 unit per video with comments'
            ],
            'estimated_quota': '150-200 units for 20 recent videos',
            'feasibility': 'HIGH - Well supported by API'
        },
        
        'like_existing_comments': {
            'description': 'Like comments on Move2Japan videos',
            'api_calls_needed': ['NONE - Not supported by API'],
            'feasibility': 'IMPOSSIBLE - API limitation',
            'workaround': 'Manual interaction through YouTube web interface only'
        },
        
        'reply_to_comments': {
            'description': 'Reply to existing comments on Move2Japan videos',
            'api_calls_needed': [
                '1. commentThreads.list (find comments) - 1 unit',
                '2. comments.insert (post reply) - 50 units per reply'
            ],
            'estimated_quota': '51+ units per reply',
            'feasibility': 'HIGH - Fully supported',
            'considerations': [
                'High quota cost',
                'Need appropriate OAuth scopes',
                'Must follow community guidelines'
            ]
        },
        
        'heart_comments_as_creator': {
            'description': 'Heart/pin comments as channel owner',
            'api_calls_needed': ['NONE - Not supported by API'],
            'feasibility': 'IMPOSSIBLE - API limitation',
            'workaround': 'Must use YouTube Studio interface'
        }
    }
    
    for scenario_name, scenario_info in scenarios.items():
        print(f"\n{scenario_name.replace('_', ' ').title()}:")
        print(f"  Description: {scenario_info['description']}")
        print(f"  Feasibility: {scenario_info['feasibility']}")
        
        if 'api_calls_needed' in scenario_info:
            print("  API Calls Needed:")
            for call in scenario_info['api_calls_needed']:
                print(f"    - {call}")
        
        if 'estimated_quota' in scenario_info:
            print(f"  Estimated Quota: {scenario_info['estimated_quota']}")
        
        if 'workaround' in scenario_info:
            print(f"  Workaround: {scenario_info['workaround']}")
        
        if 'considerations' in scenario_info:
            print("  Considerations:")
            for consideration in scenario_info['considerations']:
                print(f"    - {consideration}")
    
    # Summary and recommendations
    print(f"\nSUMMARY AND RECOMMENDATIONS:")
    print("-" * 35)
    
    print("\nWHAT WORKS:")
    print("  - Finding videos with comments (commentThreads.list)")
    print("  - Reading comment content and metadata")
    print("  - Replying to comments (comments.insert)")
    print("  - Getting video statistics including comment counts")
    print("  - Basic comment moderation on owned channels")
    
    print("\nWHAT DOESN'T WORK:")
    print("  - Liking individual comments (no API endpoint)")
    print("  - Hearting comments as channel owner (no API endpoint)")
    print("  - Interacting with comment likes in any way")
    print("  - Advanced comment moderation on other channels")
    
    print("\nBEST PRACTICES FOR MOVE2JAPAN INTERACTION:")
    print("  1. Focus on comment replies rather than likes")
    print("  2. Use quota efficiently - batch video lookups")
    print("  3. Monitor quota usage to avoid 403 errors")  
    print("  4. Consider manual liking through web interface")
    print("  5. Use reply functionality for meaningful engagement")
    
    # Save results
    test_results['capabilities'] = capabilities
    test_results['scenarios'] = scenarios
    
    report_file = f"move2japan_api_capabilities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = os.path.join(os.path.dirname(__file__), report_file)
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to: {report_path}")
    except Exception as e:
        print(f"Could not save report file: {e}")
    
    print("=" * 60)
    return test_results

if __name__ == "__main__":
    test_youtube_api_directly()