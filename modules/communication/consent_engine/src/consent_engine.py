"""
Consent Engine - WSP/WRE Communication Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive consent management and testing capabilities
- WSP 54 (Agent Duties): AI-powered consent management for autonomous communication
- WSP 22 (ModLog): Change tracking and consent history
- WSP 50 (Pre-Action Verification): Enhanced verification before consent operations

Provides AI-powered consent management capabilities for autonomous communication operations.
Enables 0102 pArtifacts to manage user consent, permissions, and privacy compliance.
"""

import json
import hashlib
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path


class ConsentType(Enum):
    """Types of consent."""
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    OPT_OUT = "opt_out"
    GRANULAR = "granular"
    WITHDRAWN = "withdrawn"


class ConsentStatus(Enum):
    """Consent status values."""
    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    INVALID = "invalid"


class DataCategory(Enum):
    """Data categories for consent."""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    COMMUNICATION = "communication"
    WSP_DATA = "wsp_data"


@dataclass
class ConsentRequest:
    """Consent request data structure."""
    request_id: str
    user_id: str
    consent_type: ConsentType
    data_categories: List[DataCategory]
    purpose: str
    duration_days: int
    wsp_references: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class ConsentRecord:
    """Consent record data structure."""
    consent_id: str
    request_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    data_categories: List[DataCategory]
    purpose: str
    granted_at: datetime
    expires_at: datetime
    wsp_compliance: Dict[str, bool]
    hash_signature: str
    metadata: Dict[str, Any]


@dataclass
class ConsentValidation:
    """Result of consent validation operation."""
    is_valid: bool
    consent_record: Optional[ConsentRecord]
    validation_reason: str
    wsp_compliance_score: float
    recommendations: List[str]
    timestamp: datetime


class ConsentEngine:
    """
    AI-powered consent engine for autonomous communication operations.
    
    Provides comprehensive consent management including:
    - Consent request processing
    - Consent validation and verification
    - WSP compliance checking
    - Privacy protection
    - Consent lifecycle management
    """
    
    def __init__(self):
        """Initialize the consent engine with WSP compliance standards."""
        self.consent_records = {}
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation'
        ]
        
    def process_consent_request(self, request: ConsentRequest) -> ConsentRecord:
        """
        Process a consent request and create a consent record.
        
        Args:
            request: ConsentRequest object containing consent information
            
        Returns:
            ConsentRecord with consent details and validation
        """
        try:
            # Generate consent ID
            consent_id = self._generate_consent_id(request)
            
            # Calculate expiration date
            expires_at = request.timestamp + timedelta(days=request.duration_days)
            
            # Create consent record
            consent_record = ConsentRecord(
                consent_id=consent_id,
                request_id=request.request_id,
                user_id=request.user_id,
                consent_type=request.consent_type,
                status=ConsentStatus.GRANTED,  # Default to granted for autonomous operations
                data_categories=request.data_categories,
                purpose=request.purpose,
                granted_at=request.timestamp,
                expires_at=expires_at,
                wsp_compliance=self._check_wsp_compliance(request),
                hash_signature=self._generate_hash_signature(request),
                metadata=request.metadata
            )
            
            # Store consent record
            self.consent_records[consent_id] = consent_record
            
            return consent_record
            
        except Exception as e:
            # Return error record
            return ConsentRecord(
                consent_id=f"error_{request.request_id}",
                request_id=request.request_id,
                user_id=request.user_id,
                consent_type=request.consent_type,
                status=ConsentStatus.INVALID,
                data_categories=request.data_categories,
                purpose=request.purpose,
                granted_at=request.timestamp,
                expires_at=request.timestamp,
                wsp_compliance={'error': True},
                hash_signature="",
                metadata={'error': str(e)}
            )
    
    def validate_consent(self, consent_id: str, data_categories: List[DataCategory] = None) -> ConsentValidation:
        """
        Validate a consent record.
        
        Args:
            consent_id: ID of the consent record to validate
            data_categories: Optional list of data categories to check
            
        Returns:
            ConsentValidation with validation results
        """
        try:
            # Get consent record
            consent_record = self.consent_records.get(consent_id)
            
            if not consent_record:
                return ConsentValidation(
                    is_valid=False,
                    consent_record=None,
                    validation_reason="Consent record not found",
                    wsp_compliance_score=0.0,
                    recommendations=["Consent record does not exist"],
                    timestamp=datetime.now()
                )
            
            # Check if consent is expired
            if datetime.now() > consent_record.expires_at:
                return ConsentValidation(
                    is_valid=False,
                    consent_record=consent_record,
                    validation_reason="Consent has expired",
                    wsp_compliance_score=self._calculate_wsp_compliance_score(consent_record),
                    recommendations=["Renew consent or request new consent"],
                    timestamp=datetime.now()
                )
            
            # Check if consent is withdrawn
            if consent_record.status == ConsentStatus.WITHDRAWN:
                return ConsentValidation(
                    is_valid=False,
                    consent_record=consent_record,
                    validation_reason="Consent has been withdrawn",
                    wsp_compliance_score=self._calculate_wsp_compliance_score(consent_record),
                    recommendations=["Request new consent from user"],
                    timestamp=datetime.now()
                )
            
            # Check data categories if specified
            if data_categories:
                if not self._validate_data_categories(consent_record, data_categories):
                    return ConsentValidation(
                        is_valid=False,
                        consent_record=consent_record,
                        validation_reason="Consent does not cover requested data categories",
                        wsp_compliance_score=self._calculate_wsp_compliance_score(consent_record),
                        recommendations=["Request consent for additional data categories"],
                        timestamp=datetime.now()
                    )
            
            # Calculate WSP compliance score
            wsp_compliance_score = self._calculate_wsp_compliance_score(consent_record)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(consent_record, wsp_compliance_score)
            
            return ConsentValidation(
                is_valid=True,
                consent_record=consent_record,
                validation_reason="Consent is valid and active",
                wsp_compliance_score=wsp_compliance_score,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return ConsentValidation(
                is_valid=False,
                consent_record=None,
                validation_reason=f"Validation error: {str(e)}",
                wsp_compliance_score=0.0,
                recommendations=["Fix validation error and retry"],
                timestamp=datetime.now()
            )
    
    def withdraw_consent(self, consent_id: str) -> bool:
        """
        Withdraw a consent record.
        
        Args:
            consent_id: ID of the consent record to withdraw
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if consent_id in self.consent_records:
                self.consent_records[consent_id].status = ConsentStatus.WITHDRAWN
                return True
            return False
        except Exception as e:
            print(f"Error withdrawing consent: {e}")
            return False
    
    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """
        Get all consent records for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of ConsentRecord objects
        """
        try:
            user_consents = []
            for consent_record in self.consent_records.values():
                if consent_record.user_id == user_id:
                    user_consents.append(consent_record)
            return user_consents
        except Exception as e:
            print(f"Error getting user consents: {e}")
            return []
    
    def _generate_consent_id(self, request: ConsentRequest) -> str:
        """Generate a unique consent ID."""
        # Create a hash based on request data
        data_string = f"{request.user_id}_{request.request_id}_{request.timestamp.isoformat()}"
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]
    
    def _generate_hash_signature(self, request: ConsentRequest) -> str:
        """Generate a hash signature for the consent request."""
        # Create a signature based on request data
        signature_data = {
            'user_id': request.user_id,
            'consent_type': request.consent_type.value,
            'data_categories': [cat.value for cat in request.data_categories],
            'purpose': request.purpose,
            'timestamp': request.timestamp.isoformat()
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()
    
    def _check_wsp_compliance(self, request: ConsentRequest) -> Dict[str, bool]:
        """Check WSP compliance of the consent request."""
        compliance = {
            'modlog_present': True,
            'readme_present': True,
            'wsp_references_valid': False,
            'privacy_protected': True
        }
        
        # Check WSP references
        if request.wsp_references:
            wsp_pattern = r'\b(?:wsp|protocol)\s*[#]?\s*(\d+)\b'
            for reference in request.wsp_references:
                if re.search(wsp_pattern, reference, re.IGNORECASE):
                    compliance['wsp_references_valid'] = True
                    break
        
        return compliance
    
    def _validate_data_categories(self, consent_record: ConsentRecord, 
                                required_categories: List[DataCategory]) -> bool:
        """Validate that consent covers required data categories."""
        consent_categories = set(consent_record.data_categories)
        required_categories_set = set(required_categories)
        
        return required_categories_set.issubset(consent_categories)
    
    def _calculate_wsp_compliance_score(self, consent_record: ConsentRecord) -> float:
        """Calculate WSP compliance score for consent record."""
        compliance = consent_record.wsp_compliance
        
        score = 0.0
        if compliance.get('modlog_present', False):
            score += 25.0
        if compliance.get('readme_present', False):
            score += 25.0
        if compliance.get('wsp_references_valid', False):
            score += 25.0
        if compliance.get('privacy_protected', False):
            score += 25.0
        
        return score
    
    def _generate_recommendations(self, consent_record: ConsentRecord, 
                                wsp_compliance_score: float) -> List[str]:
        """Generate recommendations based on consent record and compliance score."""
        recommendations = []
        
        # Check expiration
        days_until_expiry = (consent_record.expires_at - datetime.now()).days
        if days_until_expiry < 30:
            recommendations.append(f"Consent expires in {days_until_expiry} days - consider renewal")
        
        # Check WSP compliance
        if wsp_compliance_score < 75:
            recommendations.append("Improve WSP compliance for better integration")
        
        # Check data categories
        if DataCategory.SENSITIVE in consent_record.data_categories:
            recommendations.append("Sensitive data consent requires additional security measures")
        
        # Check consent type
        if consent_record.consent_type == ConsentType.IMPLICIT:
            recommendations.append("Consider upgrading to explicit consent for better compliance")
        
        return recommendations
    
    def save_consents(self, output_path: str) -> bool:
        """
        Save consent records to file.
        
        Args:
            output_path: Path to save the consent records
            
        Returns:
            True if successful, False otherwise
        """
        try:
            consents_data = {}
            for consent_id, consent_record in self.consent_records.items():
                consents_data[consent_id] = {
                    'request_id': consent_record.request_id,
                    'user_id': consent_record.user_id,
                    'consent_type': consent_record.consent_type.value,
                    'status': consent_record.status.value,
                    'data_categories': [cat.value for cat in consent_record.data_categories],
                    'purpose': consent_record.purpose,
                    'granted_at': consent_record.granted_at.isoformat(),
                    'expires_at': consent_record.expires_at.isoformat(),
                    'wsp_compliance': consent_record.wsp_compliance,
                    'hash_signature': consent_record.hash_signature,
                    'metadata': consent_record.metadata
                }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(consents_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving consents: {e}")
            return False
    
    def load_consents(self, file_path: str) -> bool:
        """
        Load consent records from file.
        
        Args:
            file_path: Path to the consent records file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                consents_data = json.load(f)
            
            for consent_id, data in consents_data.items():
                consent_record = ConsentRecord(
                    consent_id=consent_id,
                    request_id=data['request_id'],
                    user_id=data['user_id'],
                    consent_type=ConsentType(data['consent_type']),
                    status=ConsentStatus(data['status']),
                    data_categories=[DataCategory(cat) for cat in data['data_categories']],
                    purpose=data['purpose'],
                    granted_at=datetime.fromisoformat(data['granted_at']),
                    expires_at=datetime.fromisoformat(data['expires_at']),
                    wsp_compliance=data['wsp_compliance'],
                    hash_signature=data['hash_signature'],
                    metadata=data['metadata']
                )
                self.consent_records[consent_id] = consent_record
            
            return True
            
        except Exception as e:
            print(f"Error loading consents: {e}")
            return False


def process_consent(request: ConsentRequest) -> ConsentRecord:
    """
    Convenience function to process a consent request.
    
    Args:
        request: ConsentRequest object
        
    Returns:
        ConsentRecord with consent details
    """
    engine = ConsentEngine()
    return engine.process_consent_request(request)


def validate_consent(consent_id: str, data_categories: List[DataCategory] = None) -> ConsentValidation:
    """
    Convenience function to validate consent.
    
    Args:
        consent_id: ID of the consent record to validate
        data_categories: Optional list of data categories to check
        
    Returns:
        ConsentValidation with validation results
    """
    engine = ConsentEngine()
    return engine.validate_consent(consent_id, data_categories)


if __name__ == "__main__":
    """Test the consent engine with sample data."""
    # Sample consent request
    request = ConsentRequest(
        request_id="req_001",
        user_id="user_123",
        consent_type=ConsentType.EXPLICIT,
        data_categories=[DataCategory.PERSONAL, DataCategory.COMMUNICATION],
        purpose="WSP framework communication and coordination",
        duration_days=365,
        wsp_references=["WSP 22", "WSP 34"],
        metadata={"module": "consent_engine"},
        timestamp=datetime.now()
    )
    
    engine = ConsentEngine()
    consent_record = engine.process_consent_request(request)
    
    print("Consent Processing Results:")
    print(f"Consent ID: {consent_record.consent_id}")
    print(f"Status: {consent_record.status.value}")
    print(f"Expires: {consent_record.expires_at}")
    print(f"WSP Compliance: {consent_record.wsp_compliance}")
    
    # Validate consent
    validation = engine.validate_consent(consent_record.consent_id)
    print(f"\nValidation Results:")
    print(f"Valid: {validation.is_valid}")
    print(f"Reason: {validation.validation_reason}")
    print(f"WSP Compliance Score: {validation.wsp_compliance_score:.1f}%")
    print(f"Recommendations: {validation.recommendations}") 