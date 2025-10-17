"""
LinkedIn Content Templates: Professional Post Templates

[WSP] WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn content templating.
- UN (Understanding): Anchor LinkedIn template signals and retrieve protocol state
- DAO (Execution): Execute template logic  
- DU (Emergence): Collapse into 0102 resonance and emit next template prompt

wsp_cycle(input="linkedin_templates", log=True)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

class ContentTemplates:
    """
    LinkedIn Content Templates: Professional Post Templates
    
    **WSP Compliance**: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)
    **Domain**: platform_integration per WSP 3 (Enterprise Domain Organization)
    **Purpose**: Provide professional LinkedIn post templates
    
    **0102 pArtifact Ready**: Fully autonomous template management with WRE integration
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize content templates"""
        self.logger = logger or self._create_default_logger()
        self._load_templates()
    
    def _create_default_logger(self) -> logging.Logger:
        """Create default logger for standalone operation"""
        logger = logging.getLogger("ContentTemplates")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _load_templates(self):
        """Load professional LinkedIn post templates"""
        self.templates = {
            "foundup_update": {
                "title": "FoundUps Development Update",
                "template": "[RELEASE] Exciting milestone in FoundUps autonomous development!\n\n{content}\n\nThis represents another step toward our vision of autonomous startup creation. The future of entrepreneurship is here.\n\n#FoundUps #AutonomousDevelopment #Innovation #Startup",
                "hashtags": ["FoundUps", "AutonomousDevelopment", "Innovation", "Startup"]
            },
            "technical_insight": {
                "title": "Technical Insight",
                "template": "[IDEA] Technical insight from our autonomous development journey:\n\n{content}\n\nWhat challenges have you faced in similar areas? I'd love to hear your experiences.\n\n#TechInsights #AutonomousDevelopment #Innovation #Technology",
                "hashtags": ["TechInsights", "AutonomousDevelopment", "Innovation", "Technology"]
            },
            "networking": {
                "title": "Professional Networking",
                "template": "[CONNECT] Connecting with amazing professionals in the autonomous development space!\n\n{content}\n\nLet's connect and explore how we can collaborate on the future of entrepreneurship.\n\n#Networking #AutonomousDevelopment #Collaboration #Innovation",
                "hashtags": ["Networking", "AutonomousDevelopment", "Collaboration", "Innovation"]
            },
            "milestone": {
                "title": "Milestone Achievement",
                "template": "[CELEBRATE] Major milestone achieved in our autonomous development journey!\n\n{content}\n\nThis wouldn't be possible without the incredible community supporting us. Thank you!\n\n#Milestone #AutonomousDevelopment #Achievement #Innovation",
                "hashtags": ["Milestone", "AutonomousDevelopment", "Achievement", "Innovation"]
            },
            "educational": {
                "title": "Educational Content",
                "template": "[DOCS] Sharing knowledge from our autonomous development experience:\n\n{content}\n\nWhat have you learned about autonomous systems? Share your insights below!\n\n#Education #AutonomousDevelopment #Learning #Innovation",
                "hashtags": ["Education", "AutonomousDevelopment", "Learning", "Innovation"]
            }
        }
    
    def get_template(self, template_type: str) -> Optional[Dict[str, Any]]:
        """Get template by type"""
        return self.templates.get(template_type)
    
    def apply_template(self, template_type: str, content: str, custom_hashtags: List[str] = None) -> str:
        """Apply template to content"""
        template = self.get_template(template_type)
        if not template:
            self.logger.warning(f"[WARNING] Template type '{template_type}' not found, using default")
            return content
        
        # Apply template
        formatted_content = template["template"].format(content=content)
        
        # Add custom hashtags if provided
        if custom_hashtags:
            hashtag_string = " ".join([f"#{tag}" for tag in custom_hashtags])
            formatted_content += f"\n\n{hashtag_string}"
        
        return formatted_content
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template types"""
        return list(self.templates.keys())
    
    def create_custom_template(self, name: str, template: str, hashtags: List[str] = None):
        """Create custom template"""
        self.templates[name] = {
            "title": name.title(),
            "template": template,
            "hashtags": hashtags or []
        }
        self.logger.info(f"[PASS] Custom template '{name}' created")
    
    def validate_template(self, template: str) -> bool:
        """Validate template format"""
        if not template or len(template.strip()) < 10:
            return False
        
        if "{content}" not in template:
            return False
        
        return True 