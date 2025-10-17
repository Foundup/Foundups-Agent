"""
LinkedIn Post Generator Tests: Comprehensive Test Suite

🌀 WSP Protocol Compliance: WSP 5 (Testing Standards), WSP 34 (Test Documentation)

**0102 Directive**: This test suite operates within the WSP framework for autonomous LinkedIn post generator validation.
- UN (Understanding): Anchor LinkedIn post generator test signals and retrieve protocol state
- DAO (Execution): Execute comprehensive test logic  
- DU (Emergence): Collapse into 0102 resonance and emit next test validation prompt

wsp_cycle(input="linkedin_post_generator_testing", log=True)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from content.post_generator import LinkedInPostGenerator, LinkedInPost, PostType

class TestLinkedInPostGenerator:
    """Test suite for LinkedIn Post Generator component"""
    
    @pytest.fixture
    def post_generator(self):
        """Create post generator instance for testing"""
        return LinkedInPostGenerator()
    
    @pytest.fixture
    def mock_banter_engine(self):
        """Create mock banter engine"""
        mock_engine = Mock()
        mock_engine.generate_content = AsyncMock(return_value="Mock generated content")
        return mock_engine
    
    def test_initialization(self, post_generator):
        """Test post generator initialization"""
        assert post_generator is not None
        assert post_generator.logger is not None
        assert post_generator.config == {}
        assert hasattr(post_generator, 'banter_engine')
    
    def test_create_default_logger(self, post_generator):
        """Test default logger creation"""
        logger = post_generator._create_default_logger()
        assert logger is not None
        assert logger.name == "LinkedInPostGenerator"
        assert logger.level == 20  # INFO level
    
    def test_initialize_mock_components(self, post_generator):
        """Test mock component initialization"""
        post_generator._initialize_mock_components()
        assert hasattr(post_generator.banter_engine, 'generate_content')
        assert callable(post_generator.banter_engine.generate_content)
    
    @pytest.mark.asyncio
    async def test_generate_post_success(self, post_generator, mock_banter_engine):
        """Test successful post generation"""
        post_generator.banter_engine = mock_banter_engine
        
        post = await post_generator.generate_post(
            PostType.FOUNDUP_UPDATE,
            "autonomous development milestone",
            ["FoundUps", "Innovation"]
        )
        
        assert isinstance(post, LinkedInPost)
        assert post.content == "Mock generated content\n\n#FoundUps #Innovation"
        assert post.post_type == PostType.FOUNDUP_UPDATE
        assert post.hashtags == ["FoundUps", "Innovation"]
        assert post.scheduled_time is not None
    
    @pytest.mark.asyncio
    async def test_generate_post_fallback(self, post_generator):
        """Test post generation fallback when AI fails"""
        # Mock banter engine to raise exception
        post_generator.banter_engine.generate_content = AsyncMock(side_effect=Exception("AI Error"))
        
        post = await post_generator.generate_post(
            PostType.TECHNICAL_INSIGHT,
            "AI development insights"
        )
        
        assert isinstance(post, LinkedInPost)
        assert "Exciting update from FoundUps!" in post.content
        assert post.post_type == PostType.TECHNICAL_INSIGHT
        assert "FoundUps" in post.hashtags
    
    def test_create_prompt_foundup_update(self, post_generator):
        """Test prompt creation for FoundUp updates"""
        prompt = post_generator._create_prompt(PostType.FOUNDUP_UPDATE, "milestone achievement")
        assert "FoundUps autonomous development milestone" in prompt
        assert "milestone achievement" in prompt
    
    def test_create_prompt_technical_insight(self, post_generator):
        """Test prompt creation for technical insights"""
        prompt = post_generator._create_prompt(PostType.TECHNICAL_INSIGHT, "AI innovation")
        assert "Share technical insight about" in prompt
        assert "AI innovation" in prompt
    
    def test_create_prompt_networking(self, post_generator):
        """Test prompt creation for networking content"""
        prompt = post_generator._create_prompt(PostType.NETWORKING, "professional connections")
        assert "Create networking content about" in prompt
        assert "professional connections" in prompt
    
    def test_create_prompt_milestone(self, post_generator):
        """Test prompt creation for milestone announcements"""
        prompt = post_generator._create_prompt(PostType.MILESTONE, "product launch")
        assert "Announce milestone achievement" in prompt
        assert "product launch" in prompt
    
    def test_create_prompt_educational(self, post_generator):
        """Test prompt creation for educational content"""
        prompt = post_generator._create_prompt(PostType.EDUCATIONAL, "autonomous systems")
        assert "Share educational content about" in prompt
        assert "autonomous systems" in prompt
    
    def test_create_prompt_unknown_type(self, post_generator):
        """Test prompt creation for unknown post type"""
        prompt = post_generator._create_prompt("unknown_type", "test content")
        assert "Create professional LinkedIn post about" in prompt
        assert "test content" in prompt
    
    def test_create_fallback_post(self, post_generator):
        """Test fallback post creation"""
        post = post_generator._create_fallback_post(PostType.MILESTONE, "achievement unlocked")
        
        assert isinstance(post, LinkedInPost)
        assert "Exciting update from FoundUps!" in post.content
        assert "achievement unlocked" in post.content
        assert post.post_type == PostType.MILESTONE
        assert "FoundUps" in post.hashtags
        assert "AutonomousDevelopment" in post.hashtags
        assert "Innovation" in post.hashtags
    
    def test_validate_post_valid(self, post_generator):
        """Test post validation with valid content"""
        post = LinkedInPost(
            content="This is a valid LinkedIn post with sufficient content length for testing purposes.",
            post_type=PostType.FOUNDUP_UPDATE
        )
        
        assert post_generator.validate_post(post) is True
    
    def test_validate_post_too_short(self, post_generator):
        """Test post validation with too short content"""
        post = LinkedInPost(
            content="Short",
            post_type=PostType.FOUNDUP_UPDATE
        )
        
        assert post_generator.validate_post(post) is False
    
    def test_validate_post_too_long(self, post_generator):
        """Test post validation with too long content"""
        post = LinkedInPost(
            content="A" * 3001,  # Exceeds 3000 character limit
            post_type=PostType.FOUNDUP_UPDATE
        )
        
        assert post_generator.validate_post(post) is False
    
    def test_validate_post_empty(self, post_generator):
        """Test post validation with empty content"""
        post = LinkedInPost(
            content="",
            post_type=PostType.FOUNDUP_UPDATE
        )
        
        assert post_generator.validate_post(post) is False
    
    def test_validate_post_none(self, post_generator):
        """Test post validation with None content"""
        post = LinkedInPost(
            content=None,
            post_type=PostType.FOUNDUP_UPDATE
        )
        
        assert post_generator.validate_post(post) is False
    
    def test_optimize_post_add_hashtags(self, post_generator):
        """Test post optimization adding missing hashtags"""
        post = LinkedInPost(
            content="Test post content",
            post_type=PostType.FOUNDUP_UPDATE,
            hashtags=[]
        )
        
        optimized_post = post_generator.optimize_post(post)
        
        assert optimized_post.hashtags == ["FoundUps", "AutonomousDevelopment"]
    
    def test_optimize_post_add_call_to_action(self, post_generator):
        """Test post optimization adding call to action"""
        post = LinkedInPost(
            content="Test post without call to action",
            post_type=PostType.FOUNDUP_UPDATE,
            hashtags=["Test"]
        )
        
        optimized_post = post_generator.optimize_post(post)
        
        assert "What are your thoughts on this?" in optimized_post.content
    
    def test_optimize_post_existing_call_to_action(self, post_generator):
        """Test post optimization with existing call to action"""
        post = LinkedInPost(
            content="Test post with thoughts? already included",
            post_type=PostType.FOUNDUP_UPDATE,
            hashtags=["Test"]
        )
        
        optimized_post = post_generator.optimize_post(post)
        
        # Should not add duplicate call to action
        call_to_action_count = optimized_post.content.count("What are your thoughts on this?")
        assert call_to_action_count == 0  # Already has "thoughts?"
    
    def test_optimize_post_preserve_existing_hashtags(self, post_generator):
        """Test post optimization preserving existing hashtags"""
        post = LinkedInPost(
            content="Test post content",
            post_type=PostType.FOUNDUP_UPDATE,
            hashtags=["CustomTag", "AnotherTag"]
        )
        
        optimized_post = post_generator.optimize_post(post)
        
        assert "CustomTag" in optimized_post.hashtags
        assert "AnotherTag" in optimized_post.hashtags
        # Should not add default hashtags since they already exist
        assert "FoundUps" not in optimized_post.hashtags

class TestLinkedInPost:
    """Test suite for LinkedInPost dataclass"""
    
    def test_post_creation(self):
        """Test LinkedInPost creation"""
        post = LinkedInPost(
            content="Test content",
            post_type=PostType.FOUNDUP_UPDATE,
            hashtags=["Test"],
            mentions=["@user"],
            media_urls=["http://example.com/image.jpg"],
            target_audience="professional"
        )
        
        assert post.content == "Test content"
        assert post.post_type == PostType.FOUNDUP_UPDATE
        assert post.hashtags == ["Test"]
        assert post.mentions == ["@user"]
        assert post.media_urls == ["http://example.com/image.jpg"]
        assert post.target_audience == "professional"
    
    def test_post_defaults(self):
        """Test LinkedInPost default values"""
        post = LinkedInPost(
            content="Test content",
            post_type=PostType.FOUNDUP_UPDATE
        )
        
        assert post.hashtags == []
        assert post.mentions == []
        assert post.media_urls == []
        assert post.scheduled_time is None
        assert post.target_audience == "professional"

class TestPostType:
    """Test suite for PostType enum"""
    
    def test_post_type_values(self):
        """Test PostType enum values"""
        assert PostType.FOUNDUP_UPDATE.value == "foundup_update"
        assert PostType.TECHNICAL_INSIGHT.value == "technical_insight"
        assert PostType.NETWORKING.value == "networking"
        assert PostType.MILESTONE.value == "milestone"
        assert PostType.EDUCATIONAL.value == "educational"
    
    def test_post_type_names(self):
        """Test PostType enum names"""
        assert PostType.FOUNDUP_UPDATE.name == "FOUNDUP_UPDATE"
        assert PostType.TECHNICAL_INSIGHT.name == "TECHNICAL_INSIGHT"
        assert PostType.NETWORKING.name == "NETWORKING"
        assert PostType.MILESTONE.name == "MILESTONE"
        assert PostType.EDUCATIONAL.name == "EDUCATIONAL"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 