"""
Infrastructure Consent Engine

AI-powered consent management for autonomous infrastructure operations.
Provides system-level consent validation, tracking, and compliance management.

WSP Compliance: WSP 34, WSP 54, WSP 22, WSP 50
"""

import json
import logging
import threading
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path


class ConsentType(Enum):
    """Types of system consent for infrastructure operations."""
    SYSTEM_ACCESS = "system_access"
    DATA_PROCESSING = "data_processing"
    AGENT_ACTIVATION = "agent_activation"
    API_INTEGRATION = "api_integration"
    MONITORING = "monitoring"
    AUTOMATION = "automation"
    DEBUGGING = "debugging"
    MAINTENANCE = "maintenance"


class ConsentStatus(Enum):
    """Status of consent for infrastructure operations."""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"


class DataCategory(Enum):
    """Categories of data that may require consent."""
    SYSTEM_LOGS = "system_logs"
    PERFORMANCE_METRICS = "performance_metrics"
    USER_ACTIVITY = "user_activity"
    CONFIGURATION_DATA = "configuration_data"
    AUDIT_TRAILS = "audit_trails"
    ERROR_REPORTS = "error_reports"
    SECURITY_EVENTS = "security_events"
    OPERATIONAL_DATA = "operational_data"


@dataclass
class ConsentRequest:
    """Request for system consent."""
    request_id: str
    consent_type: ConsentType
    data_categories: List[DataCategory]
    purpose: str
    duration: timedelta
    scope: str
    requester: str
    timestamp: datetime
    metadata: Dict[str, Any]
    wsp_references: List[str] = None


@dataclass
class ConsentRecord:
    """Record of granted consent."""
    consent_id: str
    request_id: str
    consent_type: ConsentType
    data_categories: List[DataCategory]
    purpose: str
    granted_at: datetime
    expires_at: datetime
    status: ConsentStatus
    user_id: str
    scope: str
    signature: str
    wsp_compliance: bool
    metadata: Dict[str, Any]
    wsp_references: List[str] = None


@dataclass
class ConsentValidation:
    """Validation result for consent check."""
    is_valid: bool
    consent_id: str
    consent_type: ConsentType
    data_categories: List[DataCategory]
    granted_at: datetime
    expires_at: datetime
    status: ConsentStatus
    validation_message: str
    wsp_compliance: bool
    recommendations: List[str] = None


class InfrastructureConsentEngine:
    """
    AI-powered consent engine for autonomous infrastructure operations.
    
    Provides comprehensive consent management including:
    - System-level consent request processing
    - Infrastructure operation validation
    - WSP compliance checking
    - Consent lifecycle management
    - Audit trail maintenance
    """
    
    def __init__(self, storage_path: str = "consent_records.json"):
        """Initialize the infrastructure consent engine with WSP compliance standards."""
        self.storage_path = Path(storage_path)
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.pending_requests: Dict[str, ConsentRequest] = {}
        self.lock = threading.Lock()
        
        # WSP compliance keywords for infrastructure operations
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation',
            'infrastructure', 'system', 'consent', 'validation'
        ]
        
        # Load existing consent records
        self._load_consent_records()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def process_consent_request(self, request: ConsentRequest) -> ConsentRecord:
        """
        Process a consent request for infrastructure operations.
        
        Args:
            request: The consent request to process
            
        Returns:
            ConsentRecord: The processed consent record
        """
        with self.lock:
            # Validate request
            if not self._validate_consent_request(request):
                raise ValueError("Invalid consent request")
            
            # Check for existing consent
            existing_consent = self._find_existing_consent(request)
            if existing_consent and existing_consent.status == ConsentStatus.GRANTED:
                return existing_consent
            
            # Generate consent record
            consent_id = self._generate_consent_id()
            signature = self._generate_consent_signature(request)
            
            consent_record = ConsentRecord(
                consent_id=consent_id,
                request_id=request.request_id,
                consent_type=request.consent_type,
                data_categories=request.data_categories,
                purpose=request.purpose,
                granted_at=datetime.now(),
                expires_at=datetime.now() + request.duration,
                status=ConsentStatus.GRANTED,
                user_id=request.requester,
                scope=request.scope,
                signature=signature,
                wsp_compliance=self._check_wsp_compliance(request),
                metadata=request.metadata,
                wsp_references=request.wsp_references or []
            )
            
            # Store consent record
            self.consent_records[consent_id] = consent_record
            self._save_consent_records()
            
            # Log consent grant
            self.logger.info(f"Consent granted: {consent_id} for {request.consent_type.value}")
            
            return consent_record
    
    def validate_consent(self, consent_id: str, 
                        data_categories: List[DataCategory] = None,
                        consent_type: ConsentType = None) -> ConsentValidation:
        """
        Validate existing consent for infrastructure operations.
        
        Args:
            consent_id: The consent ID to validate
            data_categories: Optional data categories to check
            consent_type: Optional consent type to check
            
        Returns:
            ConsentValidation: Validation result
        """
        with self.lock:
            if consent_id not in self.consent_records:
                return ConsentValidation(
                    is_valid=False,
                    consent_id=consent_id,
                    consent_type=consent_type or ConsentType.SYSTEM_ACCESS,
                    data_categories=data_categories or [],
                    granted_at=datetime.now(),
                    expires_at=datetime.now(),
                    status=ConsentStatus.DENIED,
                    validation_message="Consent not found",
                    wsp_compliance=False,
                    recommendations=["Request new consent"]
                )
            
            record = self.consent_records[consent_id]
            
            # Check if consent is expired
            if datetime.now() > record.expires_at:
                record.status = ConsentStatus.EXPIRED
                self._save_consent_records()
                return ConsentValidation(
                    is_valid=False,
                    consent_id=consent_id,
                    consent_type=record.consent_type,
                    data_categories=record.data_categories,
                    granted_at=record.granted_at,
                    expires_at=record.expires_at,
                    status=ConsentStatus.EXPIRED,
                    validation_message="Consent has expired",
                    wsp_compliance=record.wsp_compliance,
                    recommendations=["Request consent renewal"]
                )
            
            # Check status
            if record.status != ConsentStatus.GRANTED:
                return ConsentValidation(
                    is_valid=False,
                    consent_id=consent_id,
                    consent_type=record.consent_type,
                    data_categories=record.data_categories,
                    granted_at=record.granted_at,
                    expires_at=record.expires_at,
                    status=record.status,
                    validation_message=f"Consent status: {record.status.value}",
                    wsp_compliance=record.wsp_compliance,
                    recommendations=["Check consent status"]
                )
            
            # Validate data categories if specified
            if data_categories and not all(cat in record.data_categories for cat in data_categories):
                return ConsentValidation(
                    is_valid=False,
                    consent_id=consent_id,
                    consent_type=record.consent_type,
                    data_categories=record.data_categories,
                    granted_at=record.granted_at,
                    expires_at=record.expires_at,
                    status=record.status,
                    validation_message="Insufficient data category permissions",
                    wsp_compliance=record.wsp_compliance,
                    recommendations=["Request additional data category permissions"]
                )
            
            # Validate consent type if specified
            if consent_type and record.consent_type != consent_type:
                return ConsentValidation(
                    is_valid=False,
                    consent_id=consent_id,
                    consent_type=record.consent_type,
                    data_categories=record.data_categories,
                    granted_at=record.granted_at,
                    expires_at=record.expires_at,
                    status=record.status,
                    validation_message="Insufficient consent type permissions",
                    wsp_compliance=record.wsp_compliance,
                    recommendations=["Request appropriate consent type"]
                )
            
            # Consent is valid
            return ConsentValidation(
                is_valid=True,
                consent_id=consent_id,
                consent_type=record.consent_type,
                data_categories=record.data_categories,
                granted_at=record.granted_at,
                expires_at=record.expires_at,
                status=record.status,
                validation_message="Consent is valid",
                wsp_compliance=record.wsp_compliance,
                recommendations=[]
            )
    
    def withdraw_consent(self, consent_id: str) -> bool:
        """
        Withdraw consent for infrastructure operations.
        
        Args:
            consent_id: The consent ID to withdraw
            
        Returns:
            bool: True if consent was successfully withdrawn
        """
        with self.lock:
            if consent_id not in self.consent_records:
                return False
            
            record = self.consent_records[consent_id]
            record.status = ConsentStatus.WITHDRAWN
            self._save_consent_records()
            
            self.logger.info(f"Consent withdrawn: {consent_id}")
            return True
    
    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """
        Get all consents for a specific user.
        
        Args:
            user_id: The user ID to get consents for
            
        Returns:
            List[ConsentRecord]: List of consent records for the user
        """
        with self.lock:
            return [record for record in self.consent_records.values() 
                   if record.user_id == user_id]
    
    def get_active_consents(self, consent_type: ConsentType = None) -> List[ConsentRecord]:
        """
        Get all active consents, optionally filtered by type.
        
        Args:
            consent_type: Optional consent type filter
            
        Returns:
            List[ConsentRecord]: List of active consent records
        """
        with self.lock:
            active_consents = [
                record for record in self.consent_records.values()
                if record.status == ConsentStatus.GRANTED and 
                datetime.now() <= record.expires_at
            ]
            
            if consent_type:
                active_consents = [
                    record for record in active_consents
                    if record.consent_type == consent_type
                ]
            
            return active_consents
    
    def cleanup_expired_consents(self) -> int:
        """
        Clean up expired consents.
        
        Returns:
            int: Number of expired consents cleaned up
        """
        with self.lock:
            expired_count = 0
            current_time = datetime.now()
            
            for consent_id, record in list(self.consent_records.items()):
                if current_time > record.expires_at and record.status == ConsentStatus.GRANTED:
                    record.status = ConsentStatus.EXPIRED
                    expired_count += 1
            
            if expired_count > 0:
                self._save_consent_records()
                self.logger.info(f"Cleaned up {expired_count} expired consents")
            
            return expired_count
    
    def export_consent_data(self, output_file: str) -> bool:
        """
        Export consent data to JSON file.
        
        Args:
            output_file: Output file path
            
        Returns:
            bool: True if export was successful
        """
        try:
            with self.lock:
                data = {
                    'consent_records': [asdict(record) for record in self.consent_records.values()],
                    'export_timestamp': datetime.now().isoformat(),
                    'total_records': len(self.consent_records)
                }
                
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                self.logger.info(f"Consent data exported to {output_file}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to export consent data: {e}")
            return False
    
    def _validate_consent_request(self, request: ConsentRequest) -> bool:
        """Validate consent request parameters."""
        if not request.request_id or not request.purpose:
            return False
        
        if not request.data_categories or len(request.data_categories) == 0:
            return False
        
        if request.duration <= timedelta(0):
            return False
        
        return True
    
    def _find_existing_consent(self, request: ConsentRequest) -> Optional[ConsentRecord]:
        """Find existing consent for the same request."""
        for record in self.consent_records.values():
            if (record.user_id == request.requester and
                record.consent_type == request.consent_type and
                record.scope == request.scope and
                record.status == ConsentStatus.GRANTED and
                datetime.now() <= record.expires_at):
                return record
        return None
    
    def _generate_consent_id(self) -> str:
        """Generate unique consent ID."""
        return f"consent_{uuid.uuid4().hex[:8]}"
    
    def _generate_consent_signature(self, request: ConsentRequest) -> str:
        """Generate consent signature for validation."""
        signature_data = f"{request.request_id}:{request.consent_type.value}:{request.requester}:{datetime.now().isoformat()}"
        return f"sig_{uuid.uuid5(uuid.NAMESPACE_DNS, signature_data).hex[:16]}"
    
    def _check_wsp_compliance(self, request: ConsentRequest) -> bool:
        """Check WSP compliance for consent request."""
        # Check for WSP keywords in purpose and metadata
        purpose_lower = request.purpose.lower()
        metadata_str = str(request.metadata).lower()
        
        wsp_keywords_found = [
            keyword for keyword in self.wsp_keywords
            if keyword in purpose_lower or keyword in metadata_str
        ]
        
        # Check for WSP references
        has_wsp_references = bool(request.wsp_references and len(request.wsp_references) > 0)
        
        return len(wsp_keywords_found) > 0 or has_wsp_references
    
    def _validate_data_categories(self, categories: List[DataCategory]) -> bool:
        """Validate data categories."""
        valid_categories = set(DataCategory)
        return all(cat in valid_categories for cat in categories)
    
    def _get_consent_recommendations(self, validation: ConsentValidation) -> List[str]:
        """Generate recommendations based on validation result."""
        recommendations = []
        
        if not validation.is_valid:
            if validation.status == ConsentStatus.EXPIRED:
                recommendations.append("Request consent renewal")
            elif validation.status == ConsentStatus.DENIED:
                recommendations.append("Submit new consent request")
            elif validation.status == ConsentStatus.WITHDRAWN:
                recommendations.append("Contact system administrator")
        
        if not validation.wsp_compliance:
            recommendations.append("Ensure WSP compliance in consent request")
        
        return recommendations
    
    def _load_consent_records(self):
        """Load consent records from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for record_data in data.get('consent_records', []):
                        # Convert string dates back to datetime objects
                        record_data['granted_at'] = datetime.fromisoformat(record_data['granted_at'])
                        record_data['expires_at'] = datetime.fromisoformat(record_data['expires_at'])
                        
                        # Convert enums
                        record_data['consent_type'] = ConsentType(record_data['consent_type'])
                        record_data['status'] = ConsentStatus(record_data['status'])
                        record_data['data_categories'] = [DataCategory(cat) for cat in record_data['data_categories']]
                        
                        record = ConsentRecord(**record_data)
                        self.consent_records[record.consent_id] = record
            except Exception as e:
                self.logger.error(f"Failed to load consent records: {e}")
    
    def _save_consent_records(self):
        """Save consent records to storage."""
        try:
            data = {
                'consent_records': [asdict(record) for record in self.consent_records.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save consent records: {e}")


# Convenience functions for common operations
def create_system_access_consent(user_id: str, scope: str, duration_days: int = 30) -> ConsentRequest:
    """Create a system access consent request."""
    return ConsentRequest(
        request_id=f"sys_access_{uuid.uuid4().hex[:8]}",
        consent_type=ConsentType.SYSTEM_ACCESS,
        data_categories=[DataCategory.SYSTEM_LOGS, DataCategory.CONFIGURATION_DATA],
        purpose="System access for infrastructure operations",
        duration=timedelta(days=duration_days),
        scope=scope,
        requester=user_id,
        timestamp=datetime.now(),
        metadata={"operation_type": "system_access"},
        wsp_references=["WSP 54", "WSP 50"]
    )


def create_monitoring_consent(user_id: str, scope: str, duration_days: int = 90) -> ConsentRequest:
    """Create a monitoring consent request."""
    return ConsentRequest(
        request_id=f"monitoring_{uuid.uuid4().hex[:8]}",
        consent_type=ConsentType.MONITORING,
        data_categories=[
            DataCategory.PERFORMANCE_METRICS,
            DataCategory.SYSTEM_LOGS,
            DataCategory.SECURITY_EVENTS
        ],
        purpose="System monitoring for performance and security",
        duration=timedelta(days=duration_days),
        scope=scope,
        requester=user_id,
        timestamp=datetime.now(),
        metadata={"operation_type": "monitoring"},
        wsp_references=["WSP 34", "WSP 47"]
    )


def validate_infrastructure_operation(consent_engine: InfrastructureConsentEngine,
                                    consent_id: str,
                                    operation_type: str,
                                    data_categories: List[DataCategory]) -> bool:
    """Validate consent for infrastructure operation."""
    validation = consent_engine.validate_consent(
        consent_id=consent_id,
        data_categories=data_categories
    )
    
    if not validation.is_valid:
        consent_engine.logger.warning(
            f"Consent validation failed for operation {operation_type}: {validation.validation_message}"
        )
        return False
    
    consent_engine.logger.info(
        f"Consent validation successful for operation {operation_type}"
    )
    return True 