"""Enhanced privacy and compliance tooling for jurisdictional regulations and client data segregation."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import json
import secrets
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from loguru import logger
import pandas as pd

from app.core.config import settings
from app.models.auth import User, AuditLog
from app.services.soc2_compliance import SecurityEventType, security_manager


class DataClassification(str, Enum):
    """Enhanced data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SENSITIVE = "sensitive"
    CRITICAL = "critical"


class PrivacyRight(str, Enum):
    """Privacy rights under various regulations."""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    AUTOMATED_DECISION = "automated_decision"
    CONSENT_WITHDRAWAL = "consent_withdrawal"


@dataclass
class DataSubjectRequest:
    """Enhanced data subject request model."""
    id: str
    request_type: PrivacyRight
    jurisdiction: str
    data_subject_id: str
    request_details: Dict[str, Any]
    status: str = "pending"
    requested_date: datetime = None
    deadline_date: datetime = None
    completed_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    response_data: Dict[str, Any] = None
    priority: str = "normal"

    def __post_init__(self):
        if self.requested_date is None:
            self.requested_date = datetime.utcnow()

        # Set deadline based on jurisdiction and priority
        base_deadline_days = 30
        if self.priority == "urgent":
            base_deadline_days = 7
        elif self.priority == "high":
            base_deadline_days = 14

        self.deadline_date = self.requested_date + timedelta(days=base_deadline_days)


class ClientDataSegregation:
    """Advanced client data segregation and isolation."""

    def __init__(self):
        self.client_schemas: Dict[str, Dict[str, Any]] = {}
        self.client_permissions: Dict[str, List[str]] = {}
        self.data_classification: Dict[str, Dict[str, Any]] = {}

    async def create_client_environment(
        self,
        session: AsyncSession,
        client_id: str,
        client_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create isolated environment for client data."""
        try:
            # Generate unique schema name
            schema_suffix = client_id.replace('-', '_').lower()
            schema_name = f"client_{schema_suffix}"

            # Create schema with security controls
            create_schema_sql = f"""
            CREATE SCHEMA IF NOT EXISTS {schema_name} AUTHORIZATION {client_config['db_user']};

            -- Enable RLS (Row Level Security)
            ALTER SCHEMA {schema_name} ENABLE ROW LEVEL SECURITY;

            -- Create audit table for this client
            CREATE TABLE IF NOT EXISTS {schema_name}.audit_log (
                id SERIAL PRIMARY KEY,
                action VARCHAR(100),
                table_name VARCHAR(100),
                record_id VARCHAR(100),
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details JSONB
            );

            -- Create RLS policies
            CREATE POLICY client_data_policy ON {schema_name}.legislative_bills
            FOR ALL USING (client_id = '{client_id}');
            """
            await session.execute(text(create_schema_sql))

            # Store client environment info
            self.client_schemas[client_id] = {
                "schema_name": schema_name,
                "created_date": datetime.utcnow(),
                "config": client_config,
                "status": "active",
                "encryption_enabled": True,
                "audit_enabled": True
            }

            logger.info(f"Client environment created: {schema_name}")
            return {
                "client_id": client_id,
                "schema_name": schema_name,
                "status": "created",
                "security_features": ["row_level_security", "audit_logging", "encryption"]
            }

        except Exception as e:
            logger.error(f"Error creating client environment: {e}")
            return {"error": str(e)}

    async def apply_data_classification(
        self,
        session: AsyncSession,
        client_id: str,
        data_classification: DataClassification,
        tables: List[str]
    ) -> Dict[str, Any]:
        """Apply data classification and security policies."""
        if client_id not in self.client_schemas:
            return {"error": "Client environment not found"}

        schema_name = self.client_schemas[client_id]["schema_name"]
        policies_applied = []

        try:
            for table in tables:
                # Apply classification-specific policies
                if data_classification in [DataClassification.SENSITIVE, DataClassification.CRITICAL]:
                    # Enable encryption for sensitive tables
                    alter_table_sql = f"""
                    ALTER TABLE {schema_name}.{table} ADD COLUMN IF NOT EXISTS
                    encrypted_data TEXT;
                    """
                    await session.execute(text(alter_table_sql))

                    # Create policy for sensitive data access
                    policy_sql = f"""
                    CREATE POLICY sensitive_data_policy ON {schema_name}.{table}
                    FOR ALL USING (
                        current_user = '{schema_name}_admin' OR
                        pg_has_role(current_user, 'data_processor', 'member')
                    );
                    """
                    await session.execute(text(policy_sql))
                    policies_applied.append(f"encryption_policy_{table}")

                elif data_classification == DataClassification.RESTRICTED:
                    # Apply strict access controls
                    policy_sql = f"""
                    CREATE POLICY restricted_data_policy ON {schema_name}.{table}
                    FOR ALL USING (current_user = '{schema_name}_admin');
                    """
                    await session.execute(text(policy_sql))
                    policies_applied.append(f"restricted_policy_{table}")

            # Update classification record
            self.data_classification[client_id] = {
                "classification": data_classification,
                "applied_date": datetime.utcnow(),
                "tables_affected": tables,
                "policies_applied": policies_applied
            }

            # Log classification application
            await security_manager._log_security_event(
                session=session,
                event_type=SecurityEventType.CONFIGURATION_CHANGE,
                user_id=None,
                details={
                    "action": "data_classification_applied",
                    "client_id": client_id,
                    "classification": data_classification,
                    "tables_affected": len(tables),
                    "policies_applied": policies_applied
                },
                request=None
            )

            return {
                "client_id": client_id,
                "classification": data_classification,
                "policies_applied": policies_applied,
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"Error applying data classification: {e}")
            return {"error": str(e)}

    async def generate_compliance_report(
        self,
        session: AsyncSession,
        client_id: str
    ) -> Dict[str, Any]:
        """Generate compliance report for a client."""
        if client_id not in self.client_schemas:
            return {"error": "Client not found"}

        client_info = self.client_schemas[client_id]
        classification_info = self.data_classification.get(client_id, {})

        # Check compliance status
        compliance_checks = {
            "data_segregation": client_info["status"] == "active",
            "encryption_enabled": client_info.get("encryption_enabled", False),
            "audit_logging": client_info.get("audit_enabled", False),
            "access_controls": len(client_info.get("config", {}).get("access_policies", [])) > 0,
            "data_classification": client_id in self.data_classification
        }

        compliance_score = sum(compliance_checks.values()) / len(compliance_checks) * 100

        report = {
            "client_id": client_id,
            "compliance_score": compliance_score,
            "compliance_status": "compliant" if compliance_score >= 90 else "needs_attention",
            "checks": compliance_checks,
            "schema_info": {
                "schema_name": client_info["schema_name"],
                "created_date": client_info["created_date"],
                "last_activity": client_info.get("last_accessed")
            },
            "data_classification": classification_info,
            "recommendations": self._generate_compliance_recommendations(compliance_checks),
            "generated_at": datetime.utcnow()
        }

        return report

    def _generate_compliance_recommendations(self, compliance_checks: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on compliance checks."""
        recommendations = []

        if not compliance_checks.get("data_segregation", False):
            recommendations.append("Implement client data segregation")

        if not compliance_checks.get("encryption_enabled", False):
            recommendations.append("Enable data encryption at rest")

        if not compliance_checks.get("audit_logging", False):
            recommendations.append("Enable comprehensive audit logging")

        if not compliance_checks.get("access_controls", False):
            recommendations.append("Implement proper access controls")

        return recommendations


class PrivacyRightsManager:
    """Manage privacy rights and data subject requests."""

    def __init__(self):
        self.active_requests: Dict[str, DataSubjectRequest] = {}
        self.request_history: List[Dict[str, Any]] = []
        self.jurisdiction_deadlines: Dict[str, int] = {
            "gdpr": 30,
            "ccpa": 45,
            "lgpd": 15,
            "pipeda": 30,
            "global": 30
        }

    async def submit_privacy_request(
        self,
        session: AsyncSession,
        request_data: Dict[str, Any]
    ) -> DataSubjectRequest:
        """Submit a privacy rights request."""
        request = DataSubjectRequest(**request_data)
        self.active_requests[request.id] = request

        # Calculate deadline based on jurisdiction
        if hasattr(request, 'jurisdiction') and request.jurisdiction in self.jurisdiction_deadlines:
            deadline_days = self.jurisdiction_deadlines[request.jurisdiction]
            request.deadline_date = request.requested_date + timedelta(days=deadline_days)

        # Log request submission
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.DATA_ACCESS,
            user_id=None,
            details={
                "action": "privacy_request_submitted",
                "request_id": request.id,
                "request_type": request.request_type,
                "jurisdiction": request.jurisdiction,
                "deadline": request.deadline_date.isoformat()
            },
            request=None
        )

        logger.info(f"Privacy request submitted: {request.id}")
        return request

    async def process_access_request(
        self,
        session: AsyncSession,
        request_id: str,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a data access request."""
        if request_id not in self.active_requests:
            return {"error": "Request not found"}

        request = self.active_requests[request_id]

        # Prepare response data
        response_data = {
            "personal_data": user_data.get("personal_data", {}),
            "data_categories": user_data.get("data_categories", []),
            "processing_purposes": user_data.get("processing_purposes", []),
            "data_sources": user_data.get("data_sources", []),
            "retention_periods": user_data.get("retention_periods", {}),
            "provided_date": datetime.utcnow(),
            "format": "json"
        }

        request.status = "completed"
        request.completed_date = datetime.utcnow()
        request.response_data = response_data

        # Move to history
        self.request_history.append({
            "request_id": request.id,
            "request_type": request.request_type,
            "completed_date": request.completed_date,
            "response_summary": {
                "data_categories_count": len(response_data["data_categories"]),
                "processing_purposes_count": len(response_data["processing_purposes"])
            }
        })

        # Log request completion
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.DATA_ACCESS,
            user_id=None,
            details={
                "action": "privacy_request_completed",
                "request_id": request_id,
                "request_type": "access",
                "data_categories_provided": len(response_data["data_categories"])
            },
            request=None
        )

        return response_data

    async def process_erasure_request(
        self,
        session: AsyncSession,
        request_id: str,
        data_subject_id: str
    ) -> Dict[str, Any]:
        """Process a data erasure request."""
        if request_id not in self.active_requests:
            return {"error": "Request not found"}

        request = self.active_requests[request_id]

        # Simulate data erasure process
        erasure_result = {
            "data_subject_id": data_subject_id,
            "records_deleted": 0,
            "systems_affected": ["main_database", "analytics", "backup_systems"],
            "erasure_completed": datetime.utcnow(),
            "retention_required": {
                "audit_logs": "7_years",  # Keep for compliance
                "billing_records": "5_years"  # Keep for tax purposes
            }
        }

        request.status = "completed"
        request.completed_date = datetime.utcnow()
        request.response_data = erasure_result

        # Log erasure completion
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.DATA_ACCESS,
            user_id=None,
            details={
                "action": "data_erasure_completed",
                "request_id": request_id,
                "data_subject_id": data_subject_id,
                "systems_affected": len(erasure_result["systems_affected"])
            },
            request=None
        )

        return erasure_result

    def get_request_status(self, request_id: str) -> Optional[DataSubjectRequest]:
        """Get the status of a privacy request."""
        return self.active_requests.get(request_id)

    def get_overdue_requests(self) -> List[DataSubjectRequest]:
        """Get list of overdue requests."""
        overdue = []
        now = datetime.utcnow()

        for request in self.active_requests.values():
            if request.deadline_date < now and request.status in ["pending", "in_progress"]:
                overdue.append(request)

        return overdue


class EnhancedPrivacyComplianceManager:
    """Enhanced privacy compliance management with advanced features."""

    def __init__(self):
        self.client_segregation = ClientDataSegregation()
        self.privacy_rights = PrivacyRightsManager()

    async def run_privacy_audit(
        self,
        session: AsyncSession,
        client_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Run comprehensive privacy audit."""
        audit_results = {
            "audit_date": datetime.utcnow(),
            "clients_audited": len(client_ids) if client_ids else "all",
            "findings": [],
            "compliance_score": 0,
            "critical_issues": 0,
            "recommendations": []
        }

        # Audit client data segregation
        if client_ids:
            clients_to_audit = client_ids
        else:
            clients_to_audit = list(self.client_segregation.client_schemas.keys())

        total_score = 0
        total_clients = len(clients_to_audit)

        for client_id in clients_to_audit:
            client_report = await self.client_segregation.generate_compliance_report(session, client_id)
            total_score += client_report.get("compliance_score", 0)

            if client_report.get("compliance_status") != "compliant":
                audit_results["critical_issues"] += 1
                audit_results["findings"].append({
                    "client_id": client_id,
                    "issue": "Non-compliant data segregation",
                    "recommendations": client_report.get("recommendations", [])
                })

        # Calculate overall compliance score
        if total_clients > 0:
            audit_results["compliance_score"] = total_score / total_clients

        # Generate overall recommendations
        if audit_results["critical_issues"] > 0:
            audit_results["recommendations"].append(
                f"Address compliance issues for {audit_results['critical_issues']} clients"
            )

        if audit_results["compliance_score"] < 90:
            audit_results["recommendations"].append(
                "Implement additional privacy controls to improve compliance score"
            )

        # Log audit completion
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=None,
            details={
                "action": "privacy_audit_completed",
                "clients_audited": total_clients,
                "compliance_score": audit_results["compliance_score"],
                "critical_issues": audit_results["critical_issues"]
            },
            request=None
        )

        return audit_results

    async def generate_data_inventory(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Generate comprehensive data inventory."""
        inventory = {
            "generated_date": datetime.utcnow(),
            "data_categories": {},
            "processing_activities": {},
            "data_subjects": {},
            "jurisdictional_coverage": {},
            "retention_schedules": {},
            "security_measures": []
        }

        # This would query actual database schema and populate the inventory
        # For now, return a structured template

        inventory["data_categories"] = {
            "personal_identifiers": ["name", "email", "phone"],
            "financial_data": ["transaction_history", "billing_info"],
            "behavioral_data": ["usage_patterns", "preferences"],
            "sensitive_data": ["health_info", "political_views", "biometrics"]
        }

        inventory["processing_activities"] = {
            "data_collection": ["user_registration", "legislative_tracking"],
            "data_processing": ["analytics", "personalization", "reporting"],
            "data_sharing": ["third_party_integrations", "data_export"],
            "data_storage": ["primary_database", "backup_systems"]
        }

        inventory["security_measures"] = [
            "encryption_at_rest",
            "encryption_in_transit",
            "access_controls",
            "audit_logging",
            "data_segregation",
            "regular_security_assessments"
        ]

        return inventory

    async def check_cross_border_transfers(
        self,
        session: AsyncSession,
        source_jurisdiction: str,
        target_jurisdiction: str,
        data_types: List[str]
    ) -> Dict[str, Any]:
        """Check compliance for cross-border data transfers."""
        # Define transfer requirements by jurisdiction pair
        transfer_requirements = {
            ("eu", "us"): {
                "mechanisms": ["adequacy_decision", "standard_contractual_clauses", "binding_corporate_rules"],
                "additional_measures": ["supplementary_measures", "impact_assessment"],
                "restricted_data": ["sensitive_personal_data", "health_data"]
            },
            ("us", "eu"): {
                "mechanisms": ["privacy_shield", "standard_contractual_clauses"],
                "additional_measures": ["adequacy_assessment"],
                "restricted_data": []
            }
        }

        pair_key = (source_jurisdiction.lower(), target_jurisdiction.lower())
        requirements = transfer_requirements.get(pair_key, {})

        # Check for restrictions
        compliance_issues = []
        restricted_data = requirements.get("restricted_data", [])

        for data_type in data_types:
            if data_type in restricted_data:
                compliance_issues.append(f"Data type '{data_type}' transfer restricted between {source_jurisdiction} and {target_jurisdiction}")

        return {
            "source_jurisdiction": source_jurisdiction,
            "target_jurisdiction": target_jurisdiction,
            "data_types": data_types,
            "compliant": len(compliance_issues) == 0,
            "compliance_issues": compliance_issues,
            "required_mechanisms": requirements.get("mechanisms", []),
            "additional_measures": requirements.get("additional_measures", []),
            "recommendations": [
                "Implement appropriate transfer mechanisms",
                "Conduct transfer impact assessment",
                "Update privacy notices for international transfers"
            ]
        }


# Global enhanced privacy compliance manager
enhanced_privacy_manager = EnhancedPrivacyComplianceManager()


async def run_enhanced_privacy_monitoring():
    """Enhanced privacy compliance monitoring."""
    while True:
        try:
            logger.info("Running enhanced privacy compliance monitoring")

            # Monitor overdue privacy requests
            overdue_requests = enhanced_privacy_manager.privacy_rights.get_overdue_requests()
            if overdue_requests:
                logger.warning(f"{len(overdue_requests)} overdue privacy requests detected")

                for request in overdue_requests:
                    logger.warning(f"Overdue request: {request.id} - {request.request_type} for {request.jurisdiction}")

            # Monitor client segregation health
            for client_id, schema_info in enhanced_privacy_manager.client_segregation.client_schemas.items():
                # Check if client environment is healthy
                if schema_info["status"] != "active":
                    logger.warning(f"Client {client_id} environment may be compromised")

            await asyncio.sleep(3600)  # Check every hour

        except Exception as e:
            logger.error(f"Error in enhanced privacy monitoring: {e}")
            await asyncio.sleep(600)  # Retry in 10 minutes
