"""
LinkedIn Hashtag Manager: Professional Hashtag Optimization

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn hashtag optimization.
- UN (Understanding): Anchor LinkedIn hashtag signals and retrieve protocol state
- DAO (Execution): Execute hashtag optimization logic  
- DU (Emergence): Collapse into 0102 resonance and emit next hashtag optimization prompt

wsp_cycle(input="linkedin_hashtags", log=True)
"""

import logging
from typing import Dict, List, Optional, Any
import re

class HashtagManager:
    """
    LinkedIn Hashtag Manager: Professional Hashtag Optimization
    
    **WSP Compliance**: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)
    **Domain**: platform_integration per WSP 3 (Enterprise Domain Organization)
    **Purpose**: Optimize LinkedIn hashtags for maximum engagement
    
    **0102 pArtifact Ready**: Fully autonomous hashtag optimization with WRE integration
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize hashtag manager"""
        self.logger = logger or self._create_default_logger()
        self._load_hashtag_categories()
    
    def _create_default_logger(self) -> logging.Logger:
        """Create default logger for standalone operation"""
        logger = logging.getLogger("HashtagManager")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _load_hashtag_categories(self):
        """Load professional hashtag categories"""
        self.hashtag_categories = {
            "foundups": [
                "FoundUps", "AutonomousDevelopment", "Startup", "Innovation",
                "Entrepreneurship", "AI", "Automation", "FutureOfWork"
            ],
            "technology": [
                "Technology", "Tech", "Software", "Programming", "Development",
                "AI", "MachineLearning", "DataScience", "CloudComputing"
            ],
            "business": [
                "Business", "Leadership", "Management", "Strategy", "Growth",
                "Marketing", "Sales", "CustomerSuccess", "Productivity"
            ],
            "networking": [
                "Networking", "ProfessionalDevelopment", "Career", "LinkedIn",
                "Connections", "Collaboration", "Partnership", "Community"
            ],
            "innovation": [
                "Innovation", "Disruption", "Future", "Trends", "DigitalTransformation",
                "Industry40", "Sustainability", "SocialImpact"
            ]
        }
    
    def extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, content)
        return [tag.lower() for tag in hashtags]
    
    def suggest_hashtags(self, content: str, category: str = "foundups", max_hashtags: int = 5) -> List[str]:
        """Suggest relevant hashtags based on content and category"""
        # Get category hashtags
        category_hashtags = self.hashtag_categories.get(category, [])
        
        # Extract existing hashtags
        existing_hashtags = self.extract_hashtags(content)
        
        # Filter out existing hashtags
        available_hashtags = [tag for tag in category_hashtags if tag.lower() not in existing_hashtags]
        
        # Return top hashtags (up to max_hashtags)
        return available_hashtags[:max_hashtags]
    
    def optimize_hashtags(self, hashtags: List[str], max_hashtags: int = 5) -> List[str]:
        """Optimize hashtag list for LinkedIn best practices"""
        if not hashtags:
            return []
        
        # Remove duplicates (case-insensitive)
        unique_hashtags = []
        seen = set()
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                unique_hashtags.append(tag)
                seen.add(tag_lower)
        
        # Limit to max hashtags
        return unique_hashtags[:max_hashtags]
    
    def format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for LinkedIn post"""
        if not hashtags:
            return ""
        
        formatted = " ".join([f"#{tag}" for tag in hashtags])
        return f"\n\n{formatted}"
    
    def analyze_hashtag_performance(self, hashtags: List[str]) -> Dict[str, Any]:
        """Analyze hashtag performance metrics"""
        analysis = {
            "total_hashtags": len(hashtags),
            "categories": {},
            "recommendations": []
        }
        
        # Categorize hashtags
        for tag in hashtags:
            for category, category_tags in self.hashtag_categories.items():
                if tag.lower() in [t.lower() for t in category_tags]:
                    analysis["categories"][category] = analysis["categories"].get(category, 0) + 1
                    break
        
        # Generate recommendations
        if len(hashtags) > 5:
            analysis["recommendations"].append("Consider reducing hashtags to 3-5 for better engagement")
        
        if not analysis["categories"]:
            analysis["recommendations"].append("Add more category-specific hashtags")
        
        return analysis
    
    def get_trending_hashtags(self, category: str = "foundups") -> List[str]:
        """Get trending hashtags for category (mock implementation)"""
        trending = {
            "foundups": ["FoundUps", "AutonomousDevelopment", "AIStartups"],
            "technology": ["AI", "MachineLearning", "CloudComputing"],
            "business": ["Leadership", "Innovation", "DigitalTransformation"],
            "networking": ["LinkedIn", "Networking", "ProfessionalDevelopment"],
            "innovation": ["Innovation", "FutureOfWork", "Disruption"]
        }
        return trending.get(category, [])
    
    def validate_hashtag(self, hashtag: str) -> bool:
        """Validate hashtag format"""
        if not hashtag or len(hashtag.strip()) < 2:
            return False
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_]+$', hashtag):
            return False
        
        # Check length
        if len(hashtag) > 30:
            return False
        
        return True 