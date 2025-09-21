"""Enhanced SOC2 controls: change management, access reviews, and incident response."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import json
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from loguru import logger
import pandas as pd

from app.core.config import settings
from app.models.auth import User, UserRole, AuditLog
from app.services.soc2_compliance import SecurityEventType, security_manager


class ChangeType(str, Enum):
    """Types of changes tracked for SOC2 compliance."""
    CODE_CHANGE = "code_change"
    CONFIGURATION_CHANGE = "configuration_change"
    INFRASTRUCTURE_CHANGE = "infrastructure_change"
    DATA_SCHEMA_CHANGE = "data_schema_change"
    SECURITY_POLICY_CHANGE = "security_policy_change"
    ACCESS_CONTROL_CHANGE = "access_control_change"


class RiskLevel(str, Enum):
    """Risk levels for change management."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeRequest(BaseModel):
    """Model for change requests."""
    id: str = Field(default_factory=lambda: secrets.token_hex(8))
    title: str
    description: str
    change_type: ChangeType
    risk_level: RiskLevel
    requester_id: int
    approver_ids: List[int]
    implementation_plan: str
    rollback_plan: str
    testing_requirements: str
    business_justification: str
    requested_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, approved, rejected, implemented, rolled_back
    approved_date: Optional[datetime] = None
    implemented_date: Optional[datetime] = None
    reviewed_date: Optional[datetime] = None


class ChangeManagement:
    """SOC2-compliant change management system."""

    def __init__(self):
        self.pending_changes: Dict[str, ChangeRequest] = {}
        self.change_history: List[Dict[str, Any]] = []

    async def submit_change_request(
        self,
        session: AsyncSession,
        change_data: Dict[str, Any]
    ) -> ChangeRequest:
        """Submit a change request for approval."""
        change_request = ChangeRequest(**change_data)

        # Validate risk level based on change type
        if change_request.change_type in [ChangeType.SECURITY_POLICY_CHANGE, ChangeType.ACCESS_CONTROL_CHANGE]:
            if change_request.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
                change_request.risk_level = RiskLevel.HIGH

        self.pending_changes[change_request.id] = change_request

        # Log change submission
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=change_request.requester_id,
            details={
                "action": "change_request_submitted",
                "change_id": change_request.id,
                "change_type": change_request.change_type,
                "risk_level": change_request.risk_level,
                "title": change_request.title
            },
            request=None
        )

        logger.info(f"Change request submitted: {change_request.id}")
        return change_request

    async def approve_change(
        self,
        session: AsyncSession,
        change_id: str,
        approver_id: int
    ) -> bool:
        """Approve a change request."""
        if change_id not in self.pending_changes:
            return False

        change = self.pending_changes[change_id]

        # Check if approver is authorized
        if approver_id not in change.approver_ids:
            await security_manager._log_security_event(
                session=session,
                event_type=SecurityEventType.AUTHORIZATION_FAILURE,
                user_id=approver_id,
                details={
                    "action": "unauthorized_change_approval_attempt",
                    "change_id": change_id,
                    "reason": "User not in approver list"
                },
                request=None
            )
            return False

        change.status = "approved"
        change.approved_date = datetime.utcnow()

        # Log approval
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=approver_id,
            details={
                "action": "change_approved",
                "change_id": change_id,
                "change_type": change.change_type,
                "risk_level": change.risk_level
            },
            request=None
        )

        logger.info(f"Change approved: {change_id}")
        return True

    async def implement_change(
        self,
        session: AsyncSession,
        change_id: str,
        implementer_id: int
    ) -> bool:
        """Implement an approved change."""
        if change_id not in self.pending_changes:
            return False

        change = self.pending_changes[change_id]

        if change.status != "approved":
            return False

        change.status = "implemented"
        change.implemented_date = datetime.utcnow()

        # Move to history
        change_dict = change.dict()
        self.change_history.append(change_dict)
        del self.pending_changes[change_id]

        # Log implementation
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=implementer_id,
            details={
                "action": "change_implemented",
                "change_id": change_id,
                "change_type": change.change_type,
                "risk_level": change.risk_level
            },
            request=None
        )

        logger.info(f"Change implemented: {change_id}")
        return True

    def get_change_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get change history for the specified period."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [
            change for change in self.change_history
            if change.get('implemented_date') and change['implemented_date'] >= cutoff_date
        ]

    def get_pending_changes(self) -> Dict[str, ChangeRequest]:
        """Get all pending changes."""
        return self.pending_changes.copy()


class AccessReviewManager:
    """SOC2-compliant access review management."""

    def __init__(self):
        self.review_cycles: Dict[str, Dict[str, Any]] = {}

    async def initiate_access_review(
        self,
        session: AsyncSession,
        reviewer_id: int,
        review_period_days: int = 90
    ) -> str:
        """Initiate an access review cycle."""
        review_id = secrets.token_hex(8)
        review_date = datetime.utcnow()

        self.review_cycles[review_id] = {
            "reviewer_id": reviewer_id,
            "initiated_date": review_date,
            "review_period_days": review_period_days,
            "status": "active",
            "findings": [],
            "recommendations": []
        }

        # Log access review initiation
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=reviewer_id,
            details={
                "action": "access_review_initiated",
                "review_id": review_id,
                "review_period_days": review_period_days
            },
            request=None
        )

        logger.info(f"Access review initiated: {review_id}")
        return review_id

    async def review_user_access(
        self,
        session: AsyncSession,
        review_id: str,
        user_id: int,
        reviewer_id: int,
        access_granted: bool,
        justification: str,
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> bool:
        """Review individual user access."""
        if review_id not in self.review_cycles:
            return False

        review = self.review_cycles[review_id]
        review["findings"].append({
            "user_id": user_id,
            "access_granted": access_granted,
            "justification": justification,
            "risk_level": risk_level,
            "reviewed_date": datetime.utcnow(),
            "reviewed_by": reviewer_id
        })

        # Log access review
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=reviewer_id,
            details={
                "action": "access_review_completed",
                "review_id": review_id,
                "reviewed_user_id": user_id,
                "access_granted": access_granted,
                "risk_level": risk_level
            },
            request=None
        )

        return True

    async def generate_access_review_report(
        self,
        session: AsyncSession,
        review_id: str
    ) -> Dict[str, Any]:
        """Generate access review report."""
        if review_id not in self.review_cycles:
            return {}

        review = self.review_cycles[review_id]

        # Calculate statistics
        total_reviews = len(review["findings"])
        granted_access = sum(1 for f in review["findings"] if f["access_granted"])
        denied_access = total_reviews - granted_access

        # Identify high-risk findings
        high_risk_findings = [
            f for f in review["findings"]
            if f["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]

        report = {
            "review_id": review_id,
            "initiated_date": review["initiated_date"],
            "reviewer_id": review["reviewer_id"],
            "status": review["status"],
            "statistics": {
                "total_reviews": total_reviews,
                "granted_access": granted_access,
                "denied_access": denied_access,
                "high_risk_findings": len(high_risk_findings)
            },
            "findings": review["findings"],
            "recommendations": self._generate_recommendations(review["findings"]),
            "generated_at": datetime.utcnow()
        }

        # Log report generation
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=review["reviewer_id"],
            details={
                "action": "access_review_report_generated",
                "review_id": review_id,
                "total_findings": total_reviews,
                "high_risk_count": len(high_risk_findings)
            },
            request=None
        )

        return report

    def _generate_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on access review findings."""
        recommendations = []

        high_risk_count = sum(1 for f in findings if f["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL])

        if high_risk_count > 0:
            recommendations.append(f"Review {high_risk_count} high-risk access grants")

        denied_count = sum(1 for f in findings if not f["access_granted"])
        if denied_count > 0:
            recommendations.append(f"Revoke access for {denied_count} users as recommended")

        if len(findings) > 50:
            recommendations.append("Consider implementing automated access review tools for large user bases")

        return recommendations


class IncidentResponseManager:
    """SOC2-compliant incident response management."""

    def __init__(self):
        self.active_incidents: Dict[str, Dict[str, Any]] = {}
        self.incident_history: List[Dict[str, Any]] = []

    async def report_incident(
        self,
        session: AsyncSession,
        reporter_id: int,
        incident_data: Dict[str, Any]
    ) -> str:
        """Report a security incident."""
        incident_id = secrets.token_hex(8)
        report_time = datetime.utcnow()

        incident = {
            "incident_id": incident_id,
            "reporter_id": reporter_id,
            "reported_date": report_time,
            "severity": incident_data.get("severity", IncidentSeverity.MEDIUM),
            "category": incident_data.get("category", "security"),
            "description": incident_data.get("description", ""),
            "affected_systems": incident_data.get("affected_systems", []),
            "potential_impact": incident_data.get("potential_impact", ""),
            "status": "reported",
            "assigned_to": None,
            "timeline": [
                {
                    "timestamp": report_time,
                    "action": "incident_reported",
                    "performed_by": reporter_id,
                    "details": "Incident initially reported"
                }
            ],
            "evidence": [],
            "remediation_steps": [],
            "lessons_learned": []
        }

        self.active_incidents[incident_id] = incident

        # Log incident report
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            user_id=reporter_id,
            details={
                "action": "incident_reported",
                "incident_id": incident_id,
                "severity": incident["severity"],
                "category": incident["category"]
            },
            request=None
        )

        logger.warning(f"Security incident reported: {incident_id}")
        return incident_id

    async def update_incident_status(
        self,
        session: AsyncSession,
        incident_id: str,
        user_id: int,
        status: str,
        details: str
    ) -> bool:
        """Update incident status."""
        if incident_id not in self.active_incidents:
            return False

        incident = self.active_incidents[incident_id]
        update_time = datetime.utcnow()

        incident["status"] = status
        incident["timeline"].append({
            "timestamp": update_time,
            "action": f"status_updated_to_{status}",
            "performed_by": user_id,
            "details": details
        })

        # Log status update
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=user_id,
            details={
                "action": "incident_status_updated",
                "incident_id": incident_id,
                "new_status": status,
                "details": details
            },
            request=None
        )

        logger.info(f"Incident {incident_id} status updated to {status}")
        return True

    async def add_incident_evidence(
        self,
        session: AsyncSession,
        incident_id: str,
        user_id: int,
        evidence: Dict[str, Any]
    ) -> bool:
        """Add evidence to an incident."""
        if incident_id not in self.active_incidents:
            return False

        incident = self.active_incidents[incident_id]

        evidence_entry = {
            "timestamp": datetime.utcnow(),
            "added_by": user_id,
            "type": evidence.get("type", "log"),
            "description": evidence.get("description", ""),
            "data": evidence.get("data", {}),
            "integrity_hash": self._calculate_hash(str(evidence))
        }

        incident["evidence"].append(evidence_entry)

        # Log evidence addition
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.DATA_ACCESS,
            user_id=user_id,
            details={
                "action": "evidence_added_to_incident",
                "incident_id": incident_id,
                "evidence_type": evidence_entry["type"]
            },
            request=None
        )

        logger.info(f"Evidence added to incident {incident_id}")
        return True

    async def generate_incident_report(
        self,
        session: AsyncSession,
        incident_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive incident report."""
        if incident_id not in self.active_incidents:
            return {}

        incident = self.active_incidents[incident_id]

        # Calculate incident duration
        start_time = incident["reported_date"]
        end_time = datetime.utcnow()
        duration_hours = (end_time - start_time).total_seconds() / 3600

        report = {
            "incident_id": incident_id,
            "summary": {
                "severity": incident["severity"],
                "category": incident["category"],
                "duration_hours": round(duration_hours, 2),
                "status": incident["status"],
                "reporter_id": incident["reporter_id"]
            },
            "timeline": incident["timeline"],
            "affected_systems": incident["affected_systems"],
            "evidence_count": len(incident["evidence"]),
            "evidence": incident["evidence"],
            "potential_impact": incident["potential_impact"],
            "remediation_steps": incident["remediation_steps"],
            "lessons_learned": incident["lessons_learned"],
            "recommendations": self._generate_incident_recommendations(incident),
            "generated_at": datetime.utcnow(),
            "report_version": "1.0"
        }

        # Log report generation
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=incident["reporter_id"],
            details={
                "action": "incident_report_generated",
                "incident_id": incident_id,
                "report_version": report["report_version"]
            },
            request=None
        )

        return report

    def _generate_incident_recommendations(self, incident: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on incident analysis."""
        recommendations = []

        if incident["severity"] in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            recommendations.append("Implement additional monitoring for affected systems")
            recommendations.append("Review access controls for privileged accounts")
            recommendations.append("Update incident response procedures")

        if len(incident["evidence"]) < 3:
            recommendations.append("Improve evidence collection procedures")

        if incident["status"] != "resolved":
            recommendations.append("Prioritize incident resolution")

        return recommendations

    def _calculate_hash(self, data: str) -> str:
        """Calculate integrity hash for evidence."""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()


class SOC2ComplianceManager:
    """Comprehensive SOC2 compliance management."""

    def __init__(self):
        self.change_management = ChangeManagement()
        self.access_review_manager = AccessReviewManager()
        self.incident_response_manager = IncidentResponseManager()

    async def run_compliance_audit(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Run comprehensive SOC2 compliance audit."""
        audit_results = {
            "audit_date": datetime.utcnow(),
            "compliance_overall": "compliant",
            "findings": [],
            "recommendations": [],
            "scores": {
                "security": 0,
                "availability": 0,
                "confidentiality": 0,
                "privacy": 0,
                "processing_integrity": 0
            }
        }

        # Check change management compliance
        change_history = self.change_management.get_change_history(30)
        if len(change_history) > 10:
            audit_results["scores"]["processing_integrity"] = 95
        else:
            audit_results["scores"]["processing_integrity"] = 85
            audit_results["findings"].append({
                "control": "Change Management",
                "finding": "Low change volume may indicate insufficient documentation",
                "severity": "medium"
            })

        # Check access review compliance
        active_reviews = len(self.access_review_manager.review_cycles)
        if active_reviews > 0:
            audit_results["scores"]["security"] = 95
        else:
            audit_results["scores"]["security"] = 75
            audit_results["findings"].append({
                "control": "Access Reviews",
                "finding": "No active access review cycles",
                "severity": "high"
            })

        # Check incident response readiness
        active_incidents = len(self.incident_response_manager.active_incidents)
        if active_incidents == 0:
            audit_results["scores"]["availability"] = 95
        else:
            audit_results["scores"]["availability"] = 80
            audit_results["findings"].append({
                "control": "Incident Response",
                "finding": f"{active_incidents} active incidents require attention",
                "severity": "high"
            })

        # Calculate overall compliance
        overall_score = sum(audit_results["scores"].values()) / len(audit_results["scores"])
        audit_results["overall_score"] = overall_score

        if overall_score < 85:
            audit_results["compliance_overall"] = "needs_improvement"
        elif overall_score < 95:
            audit_results["compliance_overall"] = "compliant_with_exceptions"
        else:
            audit_results["compliance_overall"] = "compliant"

        # Log audit completion
        await security_manager._log_security_event(
            session=session,
            event_type=SecurityEventType.CONFIGURATION_CHANGE,
            user_id=None,  # System audit
            details={
                "action": "compliance_audit_completed",
                "overall_score": overall_score,
                "findings_count": len(audit_results["findings"])
            },
            request=None
        )

        return audit_results

    async def get_compliance_dashboard(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get compliance dashboard data."""
        return {
            "last_audit": await self.run_compliance_audit(session),
            "active_changes": len(self.change_management.get_pending_changes()),
            "pending_reviews": len(self.access_review_manager.review_cycles),
            "active_incidents": len(self.incident_response_manager.active_incidents),
            "recent_changes": self.change_management.get_change_history(7),
            "security_health_score": 92,  # Would be calculated from actual metrics
            "last_updated": datetime.utcnow()
        }


# Global compliance manager
soc2_compliance_manager = SOC2ComplianceManager()


async def run_scheduled_compliance_checks():
    """Scheduled compliance monitoring."""
    while True:
        try:
            # This would run daily compliance checks
            logger.info("Running scheduled SOC2 compliance checks")

            # Check for changes requiring review
            pending_changes = soc2_compliance_manager.change_management.get_pending_changes()
            if pending_changes:
                logger.warning(f"{len(pending_changes)} changes pending review")

            # Check for overdue access reviews
            active_reviews = soc2_compliance_manager.access_review_manager.review_cycles
            for review_id, review in active_reviews.items():
                days_active = (datetime.utcnow() - review["initiated_date"]).days
                if days_active > review["review_period_days"]:
                    logger.warning(f"Access review {review_id} is overdue")

            await asyncio.sleep(86400)  # Daily

        except Exception as e:
            logger.error(f"Error in scheduled compliance checks: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour
