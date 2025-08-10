"""
LinkedIn Media Handler: Professional Media Attachment Management

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn media handling.
- UN (Understanding): Anchor LinkedIn media signals and retrieve protocol state
- DAO (Execution): Execute media handling logic  
- DU (Emergence): Collapse into 0102 resonance and emit next media handling prompt

wsp_cycle(input="linkedin_media", log=True)
"""

import logging
import os
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import mimetypes

class MediaHandler:
    """
    LinkedIn Media Handler: Professional Media Attachment Management
    
    **WSP Compliance**: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)
    **Domain**: platform_integration per WSP 3 (Enterprise Domain Organization)
    **Purpose**: Handle LinkedIn media attachments and optimization
    
    **0102 pArtifact Ready**: Fully autonomous media handling with WRE integration
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize media handler"""
        self.logger = logger or self._create_default_logger()
        self._load_supported_formats()
    
    def _create_default_logger(self) -> logging.Logger:
        """Create default logger for standalone operation"""
        logger = logging.getLogger("MediaHandler")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _load_supported_formats(self):
        """Load supported media formats for LinkedIn"""
        self.supported_formats = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
            "videos": [".mp4", ".mov", ".avi", ".wmv"],
            "documents": [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
        }
        
        self.max_file_sizes = {
            "images": 5 * 1024 * 1024,  # 5MB
            "videos": 200 * 1024 * 1024,  # 200MB
            "documents": 100 * 1024 * 1024  # 100MB
        }
    
    def validate_media_url(self, url: str) -> bool:
        """Validate media URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def get_media_type(self, file_path: str) -> Optional[str]:
        """Get media type from file path"""
        if not file_path:
            return None
        
        # Get file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Check supported formats
        for media_type, extensions in self.supported_formats.items():
            if ext in extensions:
                return media_type
        
        return None
    
    def validate_media_file(self, file_path: str) -> Dict[str, Any]:
        """Validate media file for LinkedIn upload"""
        validation = {
            "valid": False,
            "errors": [],
            "media_type": None,
            "file_size": 0
        }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                validation["errors"].append("File does not exist")
                return validation
            
            # Get file size
            file_size = os.path.getsize(file_path)
            validation["file_size"] = file_size
            
            # Get media type
            media_type = self.get_media_type(file_path)
            validation["media_type"] = media_type
            
            if not media_type:
                validation["errors"].append("Unsupported file format")
                return validation
            
            # Check file size
            max_size = self.max_file_sizes.get(media_type, 0)
            if file_size > max_size:
                validation["errors"].append(f"File size exceeds {max_size / (1024*1024):.1f}MB limit")
                return validation
            
            validation["valid"] = True
            
        except Exception as e:
            validation["errors"].append(f"Validation error: {str(e)}")
        
        return validation
    
    def optimize_media_for_linkedin(self, file_path: str, output_path: str = None) -> Optional[str]:
        """Optimize media for LinkedIn upload (mock implementation)"""
        try:
            validation = self.validate_media_file(file_path)
            if not validation["valid"]:
                self.logger.error(f"❌ Media validation failed: {validation['errors']}")
                return None
            
            # For now, just copy the file (in real implementation, would optimize)
            if output_path:
                import shutil
                shutil.copy2(file_path, output_path)
                self.logger.info(f"✅ Media optimized and saved to {output_path}")
                return output_path
            else:
                self.logger.info(f"✅ Media validated for LinkedIn upload")
                return file_path
                
        except Exception as e:
            self.logger.error(f"❌ Media optimization failed: {e}")
            return None
    
    def create_media_attachment(self, file_path: str, description: str = "") -> Dict[str, Any]:
        """Create media attachment object for LinkedIn post"""
        validation = self.validate_media_file(file_path)
        
        if not validation["valid"]:
            return {
                "valid": False,
                "errors": validation["errors"]
            }
        
        return {
            "valid": True,
            "file_path": file_path,
            "media_type": validation["media_type"],
            "file_size": validation["file_size"],
            "description": description,
            "url": None  # Would be set after upload
        }
    
    def get_media_upload_url(self, media_type: str) -> Optional[str]:
        """Get LinkedIn media upload URL (mock implementation)"""
        upload_urls = {
            "images": "https://api.linkedin.com/v2/assets?action=registerUpload",
            "videos": "https://api.linkedin.com/v2/assets?action=registerUpload",
            "documents": "https://api.linkedin.com/v2/assets?action=registerUpload"
        }
        return upload_urls.get(media_type)
    
    def format_media_description(self, description: str, hashtags: List[str] = None) -> str:
        """Format media description for LinkedIn"""
        formatted = description
        
        if hashtags:
            hashtag_string = " ".join([f"#{tag}" for tag in hashtags])
            formatted += f"\n\n{hashtag_string}"
        
        return formatted
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported media formats"""
        return self.supported_formats.copy()
    
    def get_max_file_sizes(self) -> Dict[str, int]:
        """Get maximum file sizes for each media type"""
        return self.max_file_sizes.copy() 