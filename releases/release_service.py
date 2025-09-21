"""Release management system for iterative product development."""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class ReleaseStatus(Enum):
    """Release status."""
    PLANNING = "planning"
    IN_DEVELOPMENT = "in_development"
    TESTING = "testing"
    READY_FOR_RELEASE = "ready_for_release"
    RELEASED = "released"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class ReleaseType(Enum):
    """Type of release."""
    MAJOR = "major"  # Breaking changes, significant new features
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, security updates
    HOTFIX = "hotfix"  # Critical bug fixes in production


class FeatureStatus(Enum):
    """Feature development status."""
    BACKLOG = "backlog"
    IN_DESIGN = "in_design"
    IN_DEVELOPMENT = "in_development"
    IN_REVIEW = "in_review"
    TESTING = "testing"
    READY = "ready"
    RELEASED = "released"
    CANCELLED = "cancelled"


@dataclass
class ReleaseNote:
    """Release note data structure."""
    id: str
    version: str
    release_type: ReleaseType
    title: str
    description: str
    features: List[str]
    bug_fixes: List[str]
    breaking_changes: List[str]
    known_issues: List[str]
    upgrade_instructions: Optional[str]
    release_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert release note to dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "release_type": self.release_type.value,
            "title": self.title,
            "description": self.description,
            "features": self.features,
            "bug_fixes": self.bug_fixes,
            "breaking_changes": self.breaking_changes,
            "known_issues": self.known_issues,
            "upgrade_instructions": self.upgrade_instructions,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by
        }


@dataclass
class Feature:
    """Feature data structure."""
    id: str
    title: str
    description: str
    status: FeatureStatus
    priority: str  # high, medium, low
    estimated_effort: str  # small, medium, large
    business_value: str  # high, medium, low
    target_release: Optional[str]
    tags: List[str]
    acceptance_criteria: List[str]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    assigned_to: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert feature to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "estimated_effort": self.estimated_effort,
            "business_value": self.business_value,
            "target_release": self.target_release,
            "tags": self.tags,
            "acceptance_criteria": self.acceptance_criteria,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "assigned_to": self.assigned_to
        }


@dataclass
class Release:
    """Release data structure."""
    id: str
    version: str
    release_type: ReleaseType
    status: ReleaseStatus
    name: str
    description: str
    planned_date: Optional[datetime]
    actual_date: Optional[datetime]
    features: List[str]  # Feature IDs
    estimated_effort: str
    risk_level: str  # low, medium, high
    changelog: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert release to dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "release_type": self.release_type.value,
            "status": self.status.value,
            "name": self.name,
            "description": self.description,
            "planned_date": self.planned_date.isoformat() if self.planned_date else None,
            "actual_date": self.actual_date.isoformat() if self.actual_date else None,
            "features": self.features,
            "estimated_effort": self.estimated_effort,
            "risk_level": self.risk_level,
            "changelog": self.changelog,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by
        }


class ReleaseManager:
    """Manages product releases and roadmap."""

    def __init__(self):
        self.releases: Dict[str, Release] = {}
        self.features: Dict[str, Feature] = {}
        self.release_notes: Dict[str, ReleaseNote] = {}

    async def create_release(self, release_data: Dict[str, Any], created_by: str) -> Release:
        """Create a new release."""
        release_id = str(uuid.uuid4())

        # Generate version number
        version = await self._generate_next_version(release_data["release_type"])

        release = Release(
            id=release_id,
            version=version,
            release_type=ReleaseType(release_data["release_type"]),
            status=ReleaseStatus.PLANNING,
            name=release_data["name"],
            description=release_data["description"],
            planned_date=release_data.get("planned_date"),
            features=release_data.get("features", []),
            estimated_effort=release_data.get("estimated_effort", "medium"),
            risk_level=release_data.get("risk_level", "medium"),
            created_at=datetime.now(),
            created_by=created_by
        )

        self.releases[release_id] = release
        await self._save_release(release)
        return release

    async def update_release_status(self, release_id: str, status: ReleaseStatus, updated_by: str) -> bool:
        """Update release status."""
        if release_id in self.releases:
            self.releases[release_id].status = status
            self.releases[release_id].updated_at = datetime.now()

            # If releasing, set actual date
            if status == ReleaseStatus.RELEASED:
                self.releases[release_id].actual_date = datetime.now()
                await self._create_release_notes(release_id, updated_by)

            await self._update_release(self.releases[release_id])
            return True
        return False

    async def create_feature(self, feature_data: Dict[str, Any], created_by: str) -> Feature:
        """Create a new feature."""
        feature_id = str(uuid.uuid4())

        feature = Feature(
            id=feature_id,
            title=feature_data["title"],
            description=feature_data["description"],
            status=FeatureStatus(feature_data.get("status", "backlog")),
            priority=feature_data.get("priority", "medium"),
            estimated_effort=feature_data.get("estimated_effort", "medium"),
            business_value=feature_data.get("business_value", "medium"),
            target_release=feature_data.get("target_release"),
            tags=feature_data.get("tags", []),
            acceptance_criteria=feature_data.get("acceptance_criteria", []),
            dependencies=feature_data.get("dependencies", []),
            created_at=datetime.now(),
            created_by=created_by,
            assigned_to=feature_data.get("assigned_to")
        )

        self.features[feature_id] = feature
        await self._save_feature(feature)
        return feature

    async def generate_changelog(self, from_version: Optional[str] = None,
                               to_version: Optional[str] = None) -> str:
        """Generate changelog for releases."""
        releases = list(self.releases.values())

        if from_version:
            releases = [r for r in releases if self._compare_versions(r.version, from_version) > 0]

        if to_version:
            releases = [r for r in releases if self._compare_versions(r.version, to_version) <= 0]

        # Sort by version (newest first)
        releases.sort(key=lambda x: self._version_to_tuple(x.version), reverse=True)

        changelog_lines = []
        changelog_lines.append("# Changelog")
        changelog_lines.append("")

        for release in releases:
            if release.status == ReleaseStatus.RELEASED:
                release_date = release.actual_date or release.planned_date
                date_str = release_date.strftime("%Y-%m-%d") if release_date else "TBD"

                changelog_lines.append(f"## [{release.version}] - {date_str}")
                changelog_lines.append("")
                changelog_lines.append(release.description)
                changelog_lines.append("")

                # Add features
                if release.features:
                    changelog_lines.append("### Features")
                    for feature_id in release.features:
                        if feature_id in self.features:
                            feature = self.features[feature_id]
                            changelog_lines.append(f"- {feature.title}")
                    changelog_lines.append("")

                # Add notes if available
                if release.changelog:
                    changelog_lines.append(release.changelog)
                    changelog_lines.append("")

        return "\n".join(changelog_lines)

    async def get_roadmap(self) -> Dict[str, Any]:
        """Get product roadmap."""
        releases_by_status = {}
        for status in ReleaseStatus:
            releases_by_status[status.value] = [
                r.to_dict() for r in self.releases.values()
                if r.status == status
            ]

        upcoming_features = [
            f.to_dict() for f in self.features.values()
            if f.status in [FeatureStatus.BACKLOG, FeatureStatus.IN_DESIGN, FeatureStatus.IN_DEVELOPMENT]
        ]

        return {
            "releases_by_status": releases_by_status,
            "upcoming_features": upcoming_features,
            "total_features": len(self.features),
            "features_by_status": await self._get_features_by_status()
        }

    async def _generate_next_version(self, release_type: str) -> str:
        """Generate next version number based on release type."""
        # Get latest version
        latest_version = "0.0.0"
        for release in self.releases.values():
            if self._compare_versions(release.version, latest_version) > 0:
                latest_version = release.version

        major, minor, patch = [int(x) for x in latest_version.split(".")]

        if release_type == ReleaseType.MAJOR.value:
            return f"{major + 1}.0.0"
        elif release_type == ReleaseType.MINOR.value:
            return f"{major}.{minor + 1}.0"
        else:  # PATCH or HOTFIX
            return f"{major}.{minor}.{patch + 1}"

    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings."""
        v1_parts = [int(x) for x in v1.split(".")]
        v2_parts = [int(x) for x in v2.split(".")]

        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0

            if v1_part > v2_part:
                return 1
            elif v1_part < v2_part:
                return -1

        return 0

    def _version_to_tuple(self, version: str) -> tuple:
        """Convert version string to comparable tuple."""
        return tuple(int(x) for x in version.split("."))

    async def _create_release_notes(self, release_id: str, created_by: str):
        """Create release notes for a release."""
        if release_id not in self.releases:
            return

        release = self.releases[release_id]
        features = [self.features.get(f_id, Feature(id=f_id, title="Unknown", description="", status=FeatureStatus.RELEASED, priority="medium", estimated_effort="medium", business_value="medium", target_release=None, tags=[], acceptance_criteria=[], dependencies=[], created_at=datetime.now(), created_by="", assigned_to=None)) for f_id in release.features]

        # Extract features and bug fixes from features
        release_features = []
        bug_fixes = []
        breaking_changes = []

        for feature in features:
            if "bug" in feature.title.lower() or "fix" in feature.title.lower():
                bug_fixes.append(feature.title)
            elif "breaking" in feature.title.lower() or "break" in feature.title.lower():
                breaking_changes.append(feature.title)
            else:
                release_features.append(feature.title)

        release_note = ReleaseNote(
            id=str(uuid.uuid4()),
            version=release.version,
            release_type=release.release_type,
            title=release.name,
            description=release.description,
            features=release_features,
            bug_fixes=bug_fixes,
            breaking_changes=breaking_changes,
            known_issues=[],  # Would be populated manually
            upgrade_instructions=None,  # Would be populated manually
            release_date=release.actual_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=created_by
        )

        self.release_notes[release_note.id] = release_note
        await self._save_release_note(release_note)

    async def _get_features_by_status(self) -> Dict[str, int]:
        """Get count of features by status."""
        status_counts = {}
        for status in FeatureStatus:
            status_counts[status.value] = sum(1 for f in self.features.values() if f.status == status)
        return status_counts

    async def _save_release(self, release: Release):
        """Save release to storage."""
        filepath = Path("releases") / f"{release.id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(release.to_dict(), f, indent=2)

    async def _update_release(self, release: Release):
        """Update release in storage."""
        await self._save_release(release)

    async def _save_feature(self, feature: Feature):
        """Save feature to storage."""
        filepath = Path("releases") / "features" / f"{feature.id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(feature.to_dict(), f, indent=2)

    async def _save_release_note(self, release_note: ReleaseNote):
        """Save release note to storage."""
        filepath = Path("releases") / "notes" / f"{release_note.id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(release_note.to_dict(), f, indent=2)


# Global release manager instance
release_manager = ReleaseManager()


class ReleaseService:
    """Service for managing releases and product roadmap."""

    @staticmethod
    async def create_feature_request(feature_data: Dict[str, Any], created_by: str) -> Feature:
        """Create a feature request from user feedback."""
        return await release_manager.create_feature(feature_data, created_by)

    @staticmethod
    async def plan_release(release_data: Dict[str, Any], planned_by: str) -> Release:
        """Plan a new release."""
        return await release_manager.create_release(release_data, planned_by)

    @staticmethod
    async def release_version(release_id: str, released_by: str) -> bool:
        """Mark a release as released."""
        return await release_manager.update_release_status(
            release_id, ReleaseStatus.RELEASED, released_by
        )

    @staticmethod
    async def get_roadmap() -> Dict[str, Any]:
        """Get the product roadmap."""
        return await release_manager.get_roadmap()

    @staticmethod
    async def generate_changelog(from_version: Optional[str] = None,
                               to_version: Optional[str] = None) -> str:
        """Generate changelog."""
        return await release_manager.generate_changelog(from_version, to_version)

    @staticmethod
    async def get_release_notes(version: str) -> Optional[ReleaseNote]:
        """Get release notes for a specific version."""
        for note in release_manager.release_notes.values():
            if note.version == version:
                return note
        return None

    @staticmethod
    async def create_sample_roadmap(created_by: str):
        """Create a sample roadmap for demonstration."""
        # Create sample features
        features = [
            {
                "title": "Real-time Alerts",
                "description": "Instant notifications for legislative changes",
                "status": "in_development",
                "priority": "high",
                "estimated_effort": "medium",
                "business_value": "high",
                "tags": ["alerts", "real-time"],
                "acceptance_criteria": ["Push notifications", "Email alerts", "SMS alerts"],
                "created_by": created_by
            },
            {
                "title": "Portfolio Rebalancing",
                "description": "Automated portfolio rebalancing based on legislative changes",
                "status": "backlog",
                "priority": "medium",
                "estimated_effort": "large",
                "business_value": "high",
                "tags": ["portfolio", "automation"],
                "acceptance_criteria": ["Risk-based rebalancing", "Tax optimization", "Performance tracking"],
                "created_by": created_by
            },
            {
                "title": "Advanced Analytics Dashboard",
                "description": "Enhanced analytics with custom charts and reports",
                "status": "in_design",
                "priority": "medium",
                "estimated_effort": "medium",
                "business_value": "medium",
                "tags": ["analytics", "dashboard"],
                "acceptance_criteria": ["Custom widgets", "Export capabilities", "Real-time updates"],
                "created_by": created_by
            }
        ]

        created_features = []
        for feature_data in features:
            feature = await release_manager.create_feature(feature_data, created_by)
            created_features.append(feature)

        # Create sample releases
        releases = [
            {
                "name": "Real-time Notifications",
                "description": "Introducing real-time alerts and enhanced notification system",
                "release_type": "minor",
                "planned_date": datetime.now() + timedelta(days=30),
                "features": [f.id for f in created_features[:1]],
                "estimated_effort": "medium",
                "risk_level": "low"
            },
            {
                "name": "Portfolio Intelligence",
                "description": "Advanced portfolio analysis and automated rebalancing features",
                "release_type": "minor",
                "planned_date": datetime.now() + timedelta(days=90),
                "features": [f.id for f in created_features[1:2]],
                "estimated_effort": "large",
                "risk_level": "medium"
            }
        ]

        for release_data in releases:
            await release_manager.create_release(release_data, created_by)

    @staticmethod
    async def get_feature_analytics() -> Dict[str, Any]:
        """Get feature development analytics."""
        features = list(release_manager.features.values())

        analytics = {
            "total_features": len(features),
            "status_breakdown": {},
            "priority_breakdown": {},
            "effort_breakdown": {},
            "features_by_month": {},
            "completion_rate": 0
        }

        for status in FeatureStatus:
            analytics["status_breakdown"][status.value] = sum(1 for f in features if f.status == status)

        for priority in ["high", "medium", "low"]:
            analytics["priority_breakdown"][priority] = sum(1 for f in features if f.priority == priority)

        for effort in ["small", "medium", "large"]:
            analytics["effort_breakdown"][effort] = sum(1 for f in features if f.estimated_effort == effort)

        # Calculate completion rate (features that reached ready or released)
        completed_features = sum(1 for f in features if f.status in [FeatureStatus.READY, FeatureStatus.RELEASED])
        analytics["completion_rate"] = completed_features / max(1, len(features))

        return analytics
