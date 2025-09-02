#!/usr/bin/env python3
"""
Grok-powered Log Analyzer for YouTube Live Chat Bot
Uses AI to analyze logs and recommend fixes
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

class GrokLogAnalyzer:
    """
    AI-powered log analyzer that identifies patterns and recommends fixes
    """
    
    def __init__(self, log_path: Optional[str] = None):
        # Fix path construction
        if log_path:
            self.log_path = log_path
        else:
            self.log_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'memory', 'chat_logs', 'live_chat_debug.log'
            )
        self.issues_found = []
        self.recommendations = []
        self.stats = {}
        
    def analyze_log(self) -> Dict:
        """
        Comprehensive log analysis with AI-powered insights
        """
        if not os.path.exists(self.log_path):
            return {"error": f"Log file not found: {self.log_path}"}
        
        with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Collect patterns
        errors = []
        warnings = []
        user_messages = []
        bot_responses = []
        timeouts_issued = []
        skipped_users = []
        maga_detections = []
        emoji_detections = []
        auto_captures = []
        
        for line in lines:
            # ERROR patterns
            if 'ERROR' in line:
                errors.append(line.strip())
                
            # WARNING patterns  
            elif 'WARNING' in line:
                warnings.append(line.strip())
                
            # User activity patterns
            elif 'AUTO-CAPTURED' in line:
                auto_captures.append(line)
                
            elif 'Skipping non-moderator' in line:
                match = re.search(r'Skipping non-moderator: (\w+)', line)
                if match:
                    skipped_users.append(match.group(1))
                    
            elif 'MAGA DETECTED' in line:
                maga_detections.append(line)
                
            elif 'FOUND SEQUENCE' in line:
                emoji_detections.append(line)
                
            elif 'AUTO-TIMEOUT' in line or 'MAGA TIMEOUT' in line:
                timeouts_issued.append(line)
                
            elif 'SENT:' in line:
                bot_responses.append(line)
        
        # Analyze patterns
        analysis = {
            "summary": {
                "total_lines": len(lines),
                "errors": len(errors),
                "warnings": len(warnings),
                "users_captured": len(auto_captures),
                "regular_users_skipped": len(set(skipped_users)),
                "maga_detected": len(maga_detections),
                "emoji_sequences": len(emoji_detections),
                "timeouts_issued": len(timeouts_issued),
                "bot_responses": len(bot_responses)
            },
            "issues": [],
            "recommendations": []
        }
        
        # ISSUE DETECTION with AI-like intelligence
        
        # 1. Check for connection issues
        if analysis["summary"]["errors"] > 0:
            for error in errors[-5:]:  # Last 5 errors
                if 'Authentication failed' in error:
                    analysis["issues"].append("❌ Authentication failure detected")
                    analysis["recommendations"].append(
                        "🔧 FIX: Check OAuth credentials in oauth_management module"
                    )
                elif 'textMessageDetails' in error:
                    analysis["issues"].append("❌ Error parsing message structure")
                    analysis["recommendations"].append(
                        "🔧 FIX: Some messages (like Super Chats) have different structure - add error handling"
                    )
                elif 'quota' in error.lower():
                    analysis["issues"].append("❌ YouTube API quota exceeded")
                    analysis["recommendations"].append(
                        "🔧 FIX: Rotate to backup credentials or wait for quota reset"
                    )
        
        # 2. Check if bot is not responding
        if len(lines) > 0:
            last_line_time = self._extract_timestamp(lines[-1])
            if last_line_time:
                time_since_last = datetime.now() - last_line_time
                if time_since_last > timedelta(minutes=10):
                    analysis["issues"].append(f"⚠️ Log hasn't updated in {time_since_last.total_seconds()/60:.0f} minutes")
                    analysis["recommendations"].append(
                        "🔧 FIX: Bot may be stuck or not finding livestream. Restart with: python main.py"
                    )
        
        # 3. Check for MAGA detection issues
        if len(maga_detections) == 0 and len(lines) > 100:
            analysis["issues"].append("⚠️ No MAGA detections in logs")
            analysis["recommendations"].append(
                "🔧 FIX: Either no MAGA supporters in chat, or detection not working. Test with 'love maga'"
            )
        
        # 4. Check for regular users being skipped
        if len(set(skipped_users)) > 10:
            analysis["issues"].append(f"ℹ️ {len(set(skipped_users))} regular users ignored (working as intended)")
            analysis["recommendations"].append(
                "✅ Bot correctly ignoring non-mod/member users for commands"
            )
        
        # 5. Check for response patterns
        if len(bot_responses) == 0 and len(maga_detections) > 0:
            analysis["issues"].append("❌ MAGA detected but no responses sent")
            analysis["recommendations"].append(
                "🔧 FIX: Check send_message() function or API permissions"
            )
        
        # 6. Check for emoji sequence issues
        if len(emoji_detections) > 0 and len(bot_responses) < len(emoji_detections) / 2:
            analysis["issues"].append("⚠️ Emoji sequences detected but low response rate")
            analysis["recommendations"].append(
                "🔧 FIX: Check cooldown settings or moderator-only restrictions"
            )
        
        # 7. Smart pattern recognition
        if 'love maga' in ' '.join(lines).lower() and len(timeouts_issued) == 0:
            analysis["issues"].append("❌ 'love maga' detected but no timeout issued")
            analysis["recommendations"].append(
                "🔧 FIX: MAGA trigger list may need updating. Check greeting_generator.py"
            )
        
        # 8. Check for livestream issues
        if 'No active livestream found' in ' '.join(lines):
            analysis["issues"].append("❌ Bot cannot find livestream")
            analysis["recommendations"].append(
                "🔧 FIX: Ensure you're live on YouTube, check channel ID matches"
            )
            
        # 9. Database capture analysis
        mod_captures = [c for c in auto_captures if 'MOD' in c or 'OWNER' in c]
        if len(mod_captures) > 0:
            analysis["issues"].append(f"✅ Successfully captured {len(mod_captures)} mods/owners")
        
        # Generate final AI recommendation
        if len(analysis["issues"]) == 0:
            analysis["recommendations"].append("✅ No issues detected! Bot appears to be working correctly.")
        else:
            analysis["recommendations"].insert(0, 
                f"🤖 GROK AI ANALYSIS: Found {len(analysis['issues'])} potential issues. "
                f"Priority: {self._get_priority_fix(analysis['issues'])}"
            )
        
        return analysis
    
    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """Extract timestamp from log line"""
        try:
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if match:
                return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
        except:
            pass
        return None
    
    def _get_priority_fix(self, issues: List[str]) -> str:
        """Determine priority fix based on issues"""
        if any('Authentication' in i for i in issues):
            return "Fix authentication first!"
        elif any('cannot find livestream' in i for i in issues):
            return "Check if stream is live!"
        elif any("hasn't updated" in i for i in issues):
            return "Restart the bot!"
        elif any('No MAGA detections' in i for i in issues):
            return "Test MAGA detection!"
        else:
            return "Review recommendations below"
    
    def print_analysis(self, analysis: Dict):
        """Pretty print the analysis"""
        print("\n" + "="*60)
        print("🤖 GROK LOG ANALYZER - AI-POWERED DIAGNOSTICS")
        print("="*60)
        
        if "error" in analysis:
            print(f"\n❌ ERROR: {analysis['error']}")
            return
            
        print("\n📊 SUMMARY:")
        for key, value in analysis.get("summary", {}).items():
            print(f"  {key}: {value}")
        
        if analysis.get("issues"):
            print("\n🔍 ISSUES DETECTED:")
            for issue in analysis["issues"]:
                print(f"  {issue}")
        
        if analysis.get("recommendations"):
            print("\n💡 AI RECOMMENDATIONS:")
            for rec in analysis["recommendations"]:
                print(f"  {rec}")
        
        print("\n" + "="*60)
    
    def get_recent_errors(self, minutes: int = 5) -> List[str]:
        """Get errors from last N minutes"""
        recent_errors = []
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'ERROR' in line:
                    timestamp = self._extract_timestamp(line)
                    if timestamp and timestamp > cutoff_time:
                        recent_errors.append(line.strip())
        
        return recent_errors
    
    def suggest_fix_for_error(self, error: str) -> str:
        """AI-like fix suggestions for specific errors"""
        error_lower = error.lower()
        
        if 'authentication' in error_lower:
            return "Run: python -m modules.infrastructure.oauth_management.tools.validate_credentials"
        elif 'quota' in error_lower:
            return "Switch credentials or wait for quota reset (daily at midnight PT)"
        elif 'textmessagedetails' in error_lower:
            return "Update message parsing to handle Super Chats/memberships"
        elif 'timeout' in error_lower or 'connection' in error_lower:
            return "Check internet connection and restart bot"
        elif 'no active livestream' in error_lower:
            return "Start streaming on YouTube first, then restart bot"
        else:
            return "Check full error context and search for similar issues"


def main():
    """Run the analyzer"""
    print("🚀 Starting Grok Log Analyzer...")
    
    analyzer = GrokLogAnalyzer()
    analysis = analyzer.analyze_log()
    analyzer.print_analysis(analysis)
    
    # Check for recent errors
    recent_errors = analyzer.get_recent_errors(minutes=10)
    if recent_errors:
        print("\n⚠️ RECENT ERRORS (Last 10 minutes):")
        for error in recent_errors[-3:]:  # Show last 3
            print(f"  {error}")
            fix = analyzer.suggest_fix_for_error(error)
            print(f"  → FIX: {fix}")
    
    # Quick tips based on common issues
    print("\n🎯 QUICK FIXES:")
    if "hasn't updated" in str(analysis.get("issues", [])):
        print("  ⚡ Bot not running! Start with: python main.py")
    if "No MAGA detections" in str(analysis.get("issues", [])):
        print("  ⚡ Test MAGA detection with: 'love maga' or 'trump 2024'")
    if "Emoji sequences detected but" in str(analysis.get("issues", [])):
        print("  ⚡ Only mods/members can trigger emoji responses")
    
    print("\n💡 Run this analyzer anytime to diagnose bot issues!")


if __name__ == "__main__":
    main()