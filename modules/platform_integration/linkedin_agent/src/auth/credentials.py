"""
LinkedIn Credentials Manager

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn credentials management.
- UN (Understanding): Anchor LinkedIn credentials signals and retrieve protocol state
- DAO (Execution): Execute credentials management logic  
- DU (Emergence): Collapse into 0102 resonance and emit next credentials prompt

wsp_cycle(input="linkedin_credentials", log=True)
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class LinkedInCredentials:
    """LinkedIn credentials data"""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list
    api_version: str = "v2"
    base_url: str = "https://api.linkedin.com"

class LinkedInCredentialsManager:
    """
    LinkedIn Credentials Manager
    
    **WSP Compliance**: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)
    **Purpose**: Manages LinkedIn API credentials and configuration
    **Size**: ≤300 lines per WSP 40 requirements
    """
    
    def __init__(self, credentials_file: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """Initialize credentials manager"""
        self.logger = logger or logging.getLogger(__name__)
        self.credentials_file = credentials_file or "linkedin_credentials.json"
        self.credentials: Optional[LinkedInCredentials] = None
    
    def load_from_environment(self) -> LinkedInCredentials:
        """
        Load credentials from environment variables
        
        Returns:
            LinkedInCredentials: Loaded credentials
        """
        credentials = LinkedInCredentials(
            client_id=os.getenv('LINKEDIN_CLIENT_ID', ''),
            client_secret=os.getenv('LINKEDIN_CLIENT_SECRET', ''),
            redirect_uri=os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:3000/callback'),
            scopes=os.getenv('LINKEDIN_SCOPES', 'w_member_social,r_liteprofile,r_emailaddress').split(',')
        )
        
        self.credentials = credentials
        self.logger.info("Loaded LinkedIn credentials from environment")
        return credentials
    
    def load_from_file(self, file_path: Optional[str] = None) -> Optional[LinkedInCredentials]:
        """
        Load credentials from JSON file
        
        Args:
            file_path: Path to credentials file
            
        Returns:
            LinkedInCredentials: Loaded credentials or None if failed
        """
        file_path = file_path or self.credentials_file
        
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                data = json.load(f)
            
            credentials = LinkedInCredentials(
                client_id=data.get('client_id', ''),
                client_secret=data.get('client_secret', ''),
                redirect_uri=data.get('redirect_uri', 'http://localhost:3000/callback'),
                scopes=data.get('scopes', ['w_member_social', 'r_liteprofile', 'r_emailaddress']),
                api_version=data.get('api_version', 'v2'),
                base_url=data.get('base_url', 'https://api.linkedin.com')
            )
            
            self.credentials = credentials
            self.logger.info(f"Loaded LinkedIn credentials from file: {file_path}")
            return credentials
            
        except FileNotFoundError:
            self.logger.warning(f"Credentials file not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in credentials file: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading credentials from file: {e}")
            return None
    
    def save_to_file(self, credentials: LinkedInCredentials, file_path: Optional[str] = None) -> bool:
        """
        Save credentials to JSON file
        
        Args:
            credentials: Credentials to save
            file_path: Path to save credentials
            
        Returns:
            bool: True if save successful
        """
        file_path = file_path or self.credentials_file
        
        try:
            data = {
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'redirect_uri': credentials.redirect_uri,
                'scopes': credentials.scopes,
                'api_version': credentials.api_version,
                'base_url': credentials.base_url
            }
            
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved LinkedIn credentials to file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving credentials to file: {e}")
            return False
    
    def get_credentials(self) -> Optional[LinkedInCredentials]:
        """
        Get current credentials
        
        Returns:
            LinkedInCredentials: Current credentials or None
        """
        return self.credentials
    
    def validate_credentials(self, credentials: Optional[LinkedInCredentials] = None) -> bool:
        """
        Validate credentials
        
        Args:
            credentials: Credentials to validate (uses current if None)
            
        Returns:
            bool: True if credentials are valid
        """
        creds = credentials or self.credentials
        if not creds:
            return False
        
        # Check required fields
        if not creds.client_id or not creds.client_secret:
            self.logger.warning("Missing required credentials: client_id or client_secret")
            return False
        
        if not creds.redirect_uri:
            self.logger.warning("Missing required credentials: redirect_uri")
            return False
        
        if not creds.scopes:
            self.logger.warning("Missing required credentials: scopes")
            return False
        
        self.logger.info("LinkedIn credentials validation successful")
        return True
    
    def get_auth_url(self, state: Optional[str] = None) -> Optional[str]:
        """
        Generate LinkedIn authorization URL
        
        Args:
            state: Optional state parameter for security
            
        Returns:
            str: Authorization URL or None if credentials invalid
        """
        if not self.validate_credentials():
            return None
        
        params = {
            'response_type': 'code',
            'client_id': self.credentials.client_id,
            'redirect_uri': self.credentials.redirect_uri,
            'scope': ' '.join(self.credentials.scopes)
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{query_string}"
        
        return auth_url
    
    def clear_credentials(self):
        """Clear stored credentials"""
        self.credentials = None
        self.logger.info("Cleared LinkedIn credentials") 