#!/usr/bin/env python3
"""
Community Quota Sharing Setup
WSP-Compliant: Enable community members to contribute their 10K daily YouTube API quota

This script helps community members:
1. Set up their Google Cloud project
2. Enable YouTube Data API v3
3. Create OAuth credentials
4. Authorize access for quota sharing
5. Add their credentials to the rotation system

Usage:
    python community_quota_setup.py --setup  # Interactive setup guide
    python community_quota_setup.py --add-contributor "username"  # Add new contributor
    python community_quota_setup.py --status  # Show all contributors
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
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.quota_monitor import QuotaMonitor
from src.quota_intelligence import QuotaIntelligence


class CommunityQuotaManager:
    """Manages community quota contributors and their credentials."""
    
    def __init__(self):
        self.contributors_file = Path("memory/community_contributors.json")
        self.contributors_file.parent.mkdir(exist_ok=True)
        self.contributors = self._load_contributors()
        
    def _load_contributors(self) -> dict:
        """Load community contributors data."""
        if self.contributors_file.exists():
            try:
                with open(self.contributors_file, 'r', encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading contributors: {e}")
        
        return {
            'contributors': {},
            'next_set_number': 11,  # Start after our core sets (1, 10)
            'total_quota_contributed': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_contributors(self):
        """Save contributors data."""
        self.contributors['last_updated'] = datetime.now().isoformat()
        try:
            with open(self.contributors_file, 'w', encoding="utf-8") as f:
                json.dump(self.contributors, f, indent=2)
        except Exception as e:
            print(f"Error saving contributors: {e}")
    
    def show_setup_guide(self):
        """Display interactive setup guide for new contributors."""
        print("\\n" + "="*80)
        print("[ROCKET] COMMUNITY QUOTA SHARING SETUP GUIDE")
        print("="*80)
        print()
        print("Help expand our YouTube API quota by contributing your free 10,000 daily units!")
        print()
        
        print("[CLIPBOARD] STEP 1: Google Cloud Setup")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Create a new project (or use existing)")
        print("   3. Enable 'YouTube Data API v3' in APIs & Services")
        print()
        
        print("[U+1F511] STEP 2: Create OAuth Credentials")
        print("   1. Go to 'APIs & Services' > 'Credentials'")
        print("   2. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("   3. Choose 'Desktop Application'")
        print("   4. Download the JSON file")
        print()
        
        print("[U+1F4E7] STEP 3: Contact Us")
        print("   1. Send the downloaded JSON file (safely)")
        print("   2. Include your preferred username for recognition")
        print("   3. We'll add you to the rotation system")
        print()
        
        print("[U+1F4B0] YOUR CONTRIBUTION:")
        print(f"   • 10,000 API units per day (resets at midnight PT)")
        print(f"   • Current total: {self.get_total_daily_quota():,} units from {len(self.contributors['contributors'])} contributors")
        print(f"   • Each unit enables ~50 chat messages or stream monitoring")
        print()
        
        print("[U+1F3C6] RECOGNITION:")
        print("   • Listed as quota contributor in our dashboard")
        print("   • Special recognition during streams")
        print("   • Helping enable MAGAdoom gaming for everyone!")
        print()
        
        print("[U+26A0]️ IMPORTANT:")
        print("   • Your credentials only access YouTube API (read/write chat)")
        print("   • No access to your personal data or accounts")
        print("   • You can revoke access anytime in Google Cloud Console")
        print("="*80)
    
    def add_contributor(self, username: str, credentials_path: str = None):
        """Add a new community contributor."""
        if username in self.contributors['contributors']:
            print(f"[FAIL] Contributor '{username}' already exists!")
            return False
        
        # Get next available set number
        set_number = self.contributors['next_set_number']
        
        contributor_data = {
            'username': username,
            'credential_set': set_number,
            'added_date': datetime.now().isoformat(),
            'daily_quota': 10000,
            'total_contributed': 0,
            'status': 'pending_setup',  # pending_setup -> active -> inactive
            'credentials_file': f"oauth_token{set_number}.json"
        }
        
        # Add to contributors
        self.contributors['contributors'][username] = contributor_data
        self.contributors['next_set_number'] = set_number + 1
        self.contributors['total_quota_contributed'] += 10000
        
        # Update quota monitor to include this set
        self._update_quota_monitor_config(set_number)
        
        self._save_contributors()
        
        print(f"[OK] Added contributor '{username}' as credential set {set_number}")
        print(f"[DATA] Total daily quota now: {self.get_total_daily_quota():,} units")
        
        # Create authorization script for this contributor
        self._create_auth_script(username, set_number)
        
        return True
    
    def _update_quota_monitor_config(self, set_number: int):
        """Update quota monitor to include new credential set."""
        # This would update the quota monitor configuration
        # For now, we'll document the manual steps needed
        print(f"\\n[NOTE] MANUAL STEPS NEEDED:")
        print(f"   1. Add set {set_number} to quota_monitor.py daily_limits")
        print(f"   2. Update quota_intelligence.py if needed")
        print(f"   3. Test authorization with authorize_set{set_number}.py")
    
    def _create_auth_script(self, username: str, set_number: int):
        """Create authorization script for new contributor."""
        script_content = f'''#!/usr/bin/env python3
"""
Authorization Script for Community Contributor: {username}
Credential Set: {set_number}
Generated: {datetime.now().isoformat()}

This script authorizes YouTube API access for community quota sharing.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube_auth import authorize_specific_set

def main():
    print("Authorizing Community Contributor: {username}")
    print("Credential Set: {set_number}")
    print()
    
    try:
        success = authorize_specific_set({set_number})
        if success:
            print("[OK] Authorization successful!")
            print("Your quota is now available for community use.")
        else:
            print("[FAIL] Authorization failed. Please check your credentials.")
    except Exception as e:
        print(f"Error: {{e}}")

if __name__ == "__main__":
    main()
'''
        
        script_path = Path(f"scripts/authorize_set{set_number}.py")
        with open(script_path, 'w', encoding="utf-8") as f:
            f.write(script_content)
        
        print(f"[U+1F4DC] Created authorization script: {script_path}")
    
    def get_total_daily_quota(self) -> int:
        """Get total daily quota from all contributors."""
        base_quota = 20000  # Our Sets 1 and 10
        community_quota = len(self.contributors['contributors']) * 10000
        return base_quota + community_quota
    
    def show_status(self):
        """Show community contributors status."""
        print("\\n" + "="*80)
        print("[U+1F3C6] COMMUNITY QUOTA CONTRIBUTORS")
        print("="*80)
        
        total_quota = self.get_total_daily_quota()
        print(f"[DATA] Total Daily Quota: {total_quota:,} units")
        print(f"[U+1F465] Contributors: {len(self.contributors['contributors'])}")
        print(f"[U+1F4B0] Community Contribution: {len(self.contributors['contributors']) * 10000:,} units")
        print()
        
        if not self.contributors['contributors']:
            print("No community contributors yet. Be the first!")
            print("Run: python community_quota_setup.py --setup")
            return
        
        print("CONTRIBUTORS:")
        for username, data in self.contributors['contributors'].items():
            status_emoji = {
                'pending_setup': '⏳',
                'active': '[OK]',
                'inactive': '[FAIL]'
            }.get(data['status'], '[U+2753]')
            
            print(f"  {status_emoji} {username} (Set {data['credential_set']}) - {data['daily_quota']:,} units/day")
            print(f"     Added: {data['added_date'][:10]} | Status: {data['status']}")
        
        print("="*80)
    
    def remove_contributor(self, username: str):
        """Remove a community contributor."""
        if username not in self.contributors['contributors']:
            print(f"[FAIL] Contributor '{username}' not found!")
            return False
        
        contributor = self.contributors['contributors'][username]
        set_number = contributor['credential_set']
        
        # Remove from contributors
        del self.contributors['contributors'][username]
        self.contributors['total_quota_contributed'] -= 10000
        
        self._save_contributors()
        
        print(f"[OK] Removed contributor '{username}' (Set {set_number})")
        print(f"[DATA] Total daily quota now: {self.get_total_daily_quota():,} units")
        print(f"\\n[NOTE] MANUAL CLEANUP NEEDED:")
        print(f"   1. Remove oauth_token{set_number}.json")
        print(f"   2. Update quota_monitor.py daily_limits")
        print(f"   3. Remove authorize_set{set_number}.py")
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Community Quota Sharing Management")
    parser.add_argument('--setup', action='store_true', help='Show setup guide')
    parser.add_argument('--add-contributor', metavar='USERNAME', help='Add new contributor')
    parser.add_argument('--remove-contributor', metavar='USERNAME', help='Remove contributor')
    parser.add_argument('--status', action='store_true', help='Show contributors status')
    
    args = parser.parse_args()
    
    manager = CommunityQuotaManager()
    
    if args.setup:
        manager.show_setup_guide()
    elif args.add_contributor:
        manager.add_contributor(args.add_contributor)
    elif args.remove_contributor:
        manager.remove_contributor(args.remove_contributor)
    elif args.status:
        manager.show_status()
    else:
        print("Use --help to see available options")
        manager.show_status()


if __name__ == "__main__":
    main()