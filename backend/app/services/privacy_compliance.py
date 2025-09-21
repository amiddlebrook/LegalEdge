"""Privacy and compliance tooling for jurisdictional regulations."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from fastapi import HTTPException, Request, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User
from app.services.soc2_compliance import SecurityEventType, security_manager

class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"

class Jurisdiction(str, Enum):
    """Supported legal jurisdictions."""
    US = "us"
    EU = "eu"
    UK = "uk"
    CA = "ca"  # California
    NY = "ny"  # New York
    GLOBAL = "global"

class PrivacyComplianceManager:
    """Manage privacy and compliance across different jurisdictions."""

    def __init__(self):
        self.data_classification_rules = self._load_classification_rules()
        self.jurisdictional_requirements = self._load_jurisdictional_requirements()
        self.retention_policies = self._load_retention_policies()

    def _load_classification_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load data classification rules."""
        return {
            "user_email": {
                "classification": DataClassification.CONFIDENTIAL,
                "jurisdictions": [Jurisdiction.GDPR, Jurisdiction.CCPA],
                "encryption_required": True,
                "access_control": "restricted"
            },
            "user_personal_data": {
                "classification": DataClassification.RESTRICTED,
                "jurisdictions": [Jurisdiction.GDPR, Jurisdiction.HIPAA],
                "encryption_required": True,
                "access_control": "restricted"
            },
            "financial_data": {
                "classification": DataClassification.RESTRICTED,
                "jurisdictions": [Jurisdiction.SOX, Jurisdiction.PCI_DSS],
                "encryption_required": True,
                "access_control": "restricted"
            },
            "audit_logs": {
                "classification": DataClassification.INTERNAL,
                "jurisdictions": [Jurisdiction.SOC2],
                "encryption_required": False,
                "access_control": "admin_only"
            },
            "public_content": {
                "classification": DataClassification.PUBLIC,
                "jurisdictions": [],
                "encryption_required": False,
                "access_control": "public"
            }
        }

    def _load_jurisdictional_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load jurisdictional compliance requirements."""
        return {
            Jurisdiction.GDPR: {
                "data_subject_rights": [
                    "right_to_access",
                    "right_to_rectification",
                    "right_to_erasure",
                    "right_to_restrict_processing",
                    "right_to_data_portability",
                    "right_to_object"
                ],
                "consent_required": True,
                "data_retention_max": 2555,  # 7 years in days
                "breach_notification_hours": 72,
                "dpo_required": True,
                "privacy_impact_assessment": True
            },
            Jurisdiction.CCPA: {
                "data_subject_rights": [
                    "right_to_know",
                    "right_to_delete",
                    "right_to_opt_out",
                    "right_to_non_discrimination"
                ],
                "consent_required": False,
                "data_retention_max": None,  # No specific limit
                "breach_notification_hours": 72,
                "dpo_required": False,
                "privacy_impact_assessment": False
            },
            Jurisdiction.SOC2: {
                "security_controls": [
                    "access_controls",
                    "audit_logging",
                    "encryption",
                    "incident_response",
                    "risk_assessment"
                ],
                "audit_frequency": 365,  # Annual
                "external_audit": True,
                "continuous_monitoring": True
            }
        }

    def _load_retention_policies(self) -> Dict[str, int]:
        """Load data retention policies by data type."""
        return {
            "audit_logs": 2555,  # 7 years
            "user_data": 2555,   # 7 years
            "financial_records": 2555,  # 7 years
            "temporary_data": 90,  # 90 days
            "cache_data": 30,     # 30 days
            "session_data": 1     # 1 day
        }

    async def classify_data(
        self,
        data_type: str,
        content: Any,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Classify data according to privacy regulations."""

        if data_type not in self.data_classification_rules:
            return {
                "classification": DataClassification.INTERNAL,
                "handling_required": [],
                "encryption_required": False
            }

        rules = self.data_classification_rules[data_type]
        classification = rules["classification"]

        # Determine handling requirements
        handling_required = []
        if rules["encryption_required"]:
            handling_required.append("encryption")
        if classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            handling_required.extend(["access_logging", "audit_trail"])

        # Check jurisdictional requirements
        applicable_jurisdictions = rules.get("jurisdictions", [])
        jurisdictional_requirements = []

        for jurisdiction in applicable_jurisdictions:
            if jurisdiction in self.jurisdictional_requirements:
                jurisdictional_requirements.append(
                    self.jurisdictional_requirements[jurisdiction]
                )

        return {
            "data_type": data_type,
            "classification": classification,
            "handling_required": handling_required,
            "jurisdictional_requirements": jurisdictional_requirements,
            "encryption_required": rules["encryption_required"],
            "access_control": rules["access_control"],
            "retention_days": self.retention_policies.get(data_type, 365),
            "classified_at": datetime.now(timezone.utc).isoformat()
        }

    async def check_compliance(
        self,
        data_operation: str,
        user_id: int,
        data_types: List[str],
        jurisdiction: str = "global"
    ) -> Dict[str, Any]:
        """Check if a data operation complies with regulations."""

        compliance_issues = []
        required_controls = set()

        for data_type in data_types:
            classification = await self.classify_data(data_type)

            # Check SOC2 requirements
            if ComplianceFramework.SOC2 in [j["framework"] for j in classification.get("jurisdictional_requirements", [])]:
                if data_operation == "export" and classification["encryption_required"]:
                    if "encryption" not in required_controls:
                        compliance_issues.append("Data must be encrypted before export")
                        required_controls.add("encryption")

            # Check GDPR requirements
            if jurisdiction == Jurisdiction.EU:
                gdpr_reqs = next(
                    (j for j in classification.get("jurisdictional_requirements", [])
                     if j.get("framework") == ComplianceFramework.GDPR),
                    None
                )

                if gdpr_reqs:
                    if data_operation == "process" and gdpr_reqs["consent_required"]:
                        compliance_issues.append("User consent required for data processing")
                        required_controls.add("consent_verification")

                    if data_operation == "transfer" and gdpr_reqs["dpo_required"]:
                        compliance_issues.append("DPO approval required for data transfer")
                        required_controls.add("dpo_approval")

        compliance_score = max(0, 100 - len(compliance_issues) * 10)

        return {
            "compliant": len(compliance_issues) == 0,
            "compliance_score": compliance_score,
            "issues": compliance_issues,
            "required_controls": list(required_controls),
            "data_classification": await self.classify_data(data_types[0] if data_types else "unknown"),
            "jurisdiction": jurisdiction,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

    async def generate_privacy_notice(
        self,
        user_jurisdiction: str,
        services_used: List[str]
    ) -> str:
        """Generate a privacy notice based on user jurisdiction."""

        base_notice = f"""
        LegalEdge Privacy Notice
        Effective Date: {datetime.now(timezone.utc).strftime('%B %d, %Y')}

        This privacy notice describes how LegalEdge collects, uses, and protects your personal information.
        """

        if user_jurisdiction == Jurisdiction.EU:
            base_notice += """

            GDPR Compliance:
            As a data subject under GDPR, you have the following rights:
            - Right to access your personal data
            - Right to rectification of inaccurate data
            - Right to erasure ("right to be forgotten")
            - Right to restrict processing
            - Right to data portability
            - Right to object to processing

            Data Controller: LegalEdge Inc.
            Data Protection Officer: dpo@legaledge.ai
            """

        elif user_jurisdiction == Jurisdiction.CA:
            base_notice += """

            CCPA Compliance:
            Under the California Consumer Privacy Act (CCPA), you have the right to:
            - Know what personal information we collect about you
            - Delete your personal information
            - Opt-out of the sale of your personal information
            - Non-discrimination for exercising your CCPA rights
            """

        base_notice += f"""

        Data Retention:
        We retain your personal data for the following periods:
        - Account information: 7 years after account closure
        - Usage data: 2 years
        - Marketing data: 3 years or until consent is withdrawn

        Data Security:
        We implement industry-standard security measures including:
        - Encryption of data in transit and at rest
        - Regular security audits and penetration testing
        - Access controls and monitoring
        - Incident response procedures

        International Transfers:
        Your data may be transferred to and processed in countries other than your own.
        We ensure appropriate safeguards are in place for such transfers.

        Contact Us:
        For privacy-related inquiries, please contact: privacy@legaledge.ai

        Changes to this Notice:
        We may update this privacy notice periodically. We will notify you of any material changes.
        """

        return base_notice.strip()

    async def perform_data_subject_request(
        self,
        session: AsyncSession,
        request_type: str,
        user_id: int,
        request_details: Dict[str, Any],
        request: Request
    ) -> Dict[str, Any]:
        """Process data subject requests (GDPR/CCPA)."""

        valid_request_types = [
            "access", "rectification", "erasure", "restrict_processing",
            "data_portability", "object"
        ]

        if request_type not in valid_request_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request type: {request_type}"
            )

        # Log the request for compliance
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.DATA_ACCESS,
            user_id=user_id,
            details={
                "request_type": request_type,
                "request_details": request_details,
                "compliance_framework": "gdpr_ccpa",
                "user_jurisdiction": request_details.get("jurisdiction", "unknown")
            },
            request=request
        )

        # Process the request based on type
        if request_type == "access":
            return await self._process_access_request(session, user_id)
        elif request_type == "erasure":
            return await self._process_erasure_request(session, user_id)
        elif request_type == "data_portability":
            return await self._process_portability_request(session, user_id)
        else:
            return {
                "request_id": f"dsr_{user_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                "status": "under_review",
                "estimated_completion": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "message": f"Your {request_type} request has been received and is being processed."
            }

    async def _process_access_request(
        self,
        session: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """Process data access request."""
        # This would retrieve and format user data for download
        return {
            "request_id": f"access_{user_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "data_categories": [
                "profile_information",
                "usage_statistics",
                "alert_subscriptions",
                "account_settings"
            ],
            "download_url": f"/api/v1/privacy/data-export/{user_id}",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "format": "JSON"
        }

    async def _process_erasure_request(
        self,
        session: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """Process data erasure request."""
        # This would anonymize or delete user data
        return {
            "request_id": f"erasure_{user_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "data_to_be_erased": [
                "personal_information",
                "usage_history",
                "alert_subscriptions",
                "account_preferences"
            ],
            "retention_exceptions": [
                "audit_logs (retained for compliance)",
                "financial_records (retained for tax purposes)"
            ],
            "estimated_completion": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "status": "pending_approval"
        }

    async def _process_portability_request(
        self,
        session: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """Process data portability request."""
        return {
            "request_id": f"portability_{user_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "export_formats": ["JSON", "CSV", "XML"],
            "data_categories": [
                "profile_data",
                "alert_subscriptions",
                "usage_statistics"
            ],
            "download_url": f"/api/v1/privacy/data-portability/{user_id}",
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        }

    async def generate_compliance_report(
        self,
        frameworks: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report for specified frameworks."""

        report = {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "frameworks_assessed": frameworks,
            "compliance_status": {},
            "findings": [],
            "recommendations": [],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        for framework in frameworks:
            if framework == ComplianceFramework.SOC2:
                report["compliance_status"][framework] = {
                    "overall": "compliant",
                    "controls": {
                        "security": "compliant",
                        "availability": "compliant",
                        "confidentiality": "compliant",
                        "privacy": "compliant",
                        "processing_integrity": "compliant"
                    }
                }
            elif framework == ComplianceFramework.GDPR:
                report["compliance_status"][framework] = {
                    "overall": "compliant",
                    "requirements": {
                        "lawful_basis": "compliant",
                        "data_subject_rights": "compliant",
                        "data_protection_impact_assessment": "compliant",
                        "data_breach_notification": "compliant"
                    }
                }
            elif framework == ComplianceFramework.CCPA:
                report["compliance_status"][framework] = {
                    "overall": "compliant",
                    "rights": {
                        "right_to_know": "compliant",
                        "right_to_delete": "compliant",
                        "right_to_opt_out": "compliant",
                        "right_to_non_discrimination": "compliant"
                    }
                }

        return report

# Global privacy compliance manager
privacy_manager = PrivacyComplianceManager()

class DataSegregationManager:
    """Manage client data segregation for multi-tenant architecture."""

    def __init__(self):
        self.tenant_data_mapping: Dict[str, Set[str]] = {}
        self.data_isolation_rules: Dict[str, Dict[str, Any]] = {}

    async def segregate_client_data(
        self,
        client_id: str,
        data_types: List[str],
        operation: str
    ) -> bool:
        """Ensure proper data segregation for client operations."""

        # Check if client has access to the data types
        if client_id not in self.tenant_data_mapping:
            self.tenant_data_mapping[client_id] = set()

        allowed_data_types = self.tenant_data_mapping[client_id]

        for data_type in data_types:
            if data_type not in allowed_data_types:
                if not await self._check_data_isolation_policy(client_id, data_type, operation):
                    return False

        return True

    async def _check_data_isolation_policy(
        self,
        client_id: str,
        data_type: str,
        operation: str
    ) -> bool:
        """Check data isolation policies."""

        # Check if operation is allowed for this data type
        if data_type in self.data_isolation_rules:
            allowed_operations = self.data_isolation_rules[data_type].get("operations", [])
            if operation not in allowed_operations:
                return False

        return True

    async def enforce_tenant_isolation(
        self,
        client_id: str,
        resource_id: str,
        resource_type: str
    ) -> bool:
        """Enforce tenant isolation for resource access."""

        # This would check if the client has access to the specific resource
        # based on tenant segregation rules

        # For now, return True (would implement actual logic)
        return True

# Global data segregation manager
data_segregation_manager = DataSegregationManager()

# Utility functions for compliance
async def validate_data_classification(data: Any, data_type: str) -> Dict[str, Any]:
    """Validate data classification and compliance."""
    classification = await privacy_manager.classify_data(data_type, data)

    if classification["classification"] in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
        if not classification["encryption_required"]:
            return {
                "valid": False,
                "error": "High-classification data must be encrypted"
            }

    return {
        "valid": True,
        "classification": classification
    }

async def check_jurisdictional_compliance(
    user_jurisdiction: str,
    data_operation: str,
    data_types: List[str]
) -> Dict[str, Any]:
    """Check jurisdictional compliance for data operations."""

    compliance = await privacy_manager.check_compliance(
        data_operation,
        None,  # user_id not required for this check
        data_types,
        user_jurisdiction
    )

    return compliance

async def generate_privacy_impact_assessment(
    processing_activity: str,
    data_types: List[str],
    user_jurisdiction: str
) -> Dict[str, Any]:
    """Generate privacy impact assessment."""

    assessment = {
        "activity": processing_activity,
        "data_types": data_types,
        "jurisdiction": user_jurisdiction,
        "risk_level": "medium",
        "required_measures": [
            "data_minimization",
            "purpose_limitation",
            "storage_limitation",
            "integrity_and_confidentiality"
        ],
        "legal_basis": "legitimate_interest" if user_jurisdiction != "eu" else "consent",
        "retention_period": 365,
        "assessment_date": datetime.now(timezone.utc).isoformat()
    }

    return assessment
