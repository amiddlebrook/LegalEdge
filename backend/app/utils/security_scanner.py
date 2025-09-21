"""Vulnerability scanning and dependency governance."""
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import requests
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.config import settings


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""
    id: str
    severity: str
    title: str
    description: str
    package: str
    version: str
    fix_available: bool
    fix_version: Optional[str] = None
    cvss_score: Optional[float] = None
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class Dependency:
    """Represents a project dependency."""
    name: str
    version: str
    type: str  # 'python' or 'node'
    license: Optional[str] = None
    vulnerabilities: List[Vulnerability] = None

    def __post_init__(self):
        if self.vulnerabilities is None:
            self.vulnerabilities = []


class VulnerabilityScanner:
    """Scan dependencies for vulnerabilities."""

    def __init__(self):
        self.python_scanner = PythonVulnerabilityScanner()
        self.node_scanner = NodeVulnerabilityScanner()

    def scan_all(self) -> Dict[str, List[Dependency]]:
        """Scan all dependencies for vulnerabilities."""
        results = {}

        # Scan Python dependencies
        try:
            results['python'] = self.python_scanner.scan()
        except Exception as e:
            print(f"Python vulnerability scan failed: {e}")
            results['python'] = []

        # Scan Node.js dependencies
        try:
            results['node'] = self.node_scanner.scan()
        except Exception as e:
            print(f"Node.js vulnerability scan failed: {e}")
            results['node'] = []

        return results

    def get_critical_vulnerabilities(self) -> List[Vulnerability]:
        """Get all critical and high severity vulnerabilities."""
        all_deps = self.scan_all()
        critical_vulns = []

        for deps in all_deps.values():
            for dep in deps:
                for vuln in dep.vulnerabilities:
                    if vuln.severity in ['critical', 'high']:
                        critical_vulns.append(vuln)

        return critical_vulns

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive vulnerability report."""
        all_deps = self.scan_all()
        critical_vulns = self.get_critical_vulnerabilities()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_dependencies': sum(len(deps) for deps in all_deps.values()),
            'total_vulnerabilities': sum(
                len(dep.vulnerabilities) for deps in all_deps.values() for dep in deps
            ),
            'critical_vulnerabilities': len(critical_vulns),
            'scan_results': all_deps,
            'recommendations': self._generate_recommendations(critical_vulns)
        }

    def _generate_recommendations(self, critical_vulns: List[Vulnerability]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []

        if critical_vulns:
            recommendations.append(
                f"Found {len(critical_vulns)} critical vulnerabilities. "
                "Immediate action required."
            )

        # Check for outdated dependencies
        for vuln in critical_vulns:
            if vuln.fix_available and vuln.fix_version:
                recommendations.append(
                    f"Update {vuln.package} from {vuln.version} to {vuln.fix_version}"
                )

        recommendations.extend([
            "Regularly run security scans in CI/CD pipeline",
            "Keep dependencies updated to latest secure versions",
            "Use tools like Dependabot for automated dependency updates",
            "Implement security policies for dependency approval"
        ])

        return recommendations


class PythonVulnerabilityScanner:
    """Scan Python dependencies for vulnerabilities."""

    def scan(self) -> List[Dependency]:
        """Scan Python dependencies using safety and bandit."""
        dependencies = []

        try:
            # Use pip-audit for vulnerability scanning
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'audit', '--format', 'json'
            ], capture_output=True, text=True, check=False)

            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                dependencies = self._parse_pip_audit_results(vulnerabilities)

        except Exception as e:
            print(f"Python vulnerability scan error: {e}")

        return dependencies

    def _parse_pip_audit_results(self, audit_data: Dict[str, Any]) -> List[Dependency]:
        """Parse pip-audit results into Dependency objects."""
        dependencies = []

        for item in audit_data.get('vulnerabilities', []):
            dep = Dependency(
                name=item.get('name', 'unknown'),
                version=item.get('version', 'unknown'),
                type='python',
                license='Unknown'  # Would need to fetch from PyPI
            )

            vulnerability = Vulnerability(
                id=item.get('id', 'unknown'),
                severity=item.get('severity', 'unknown'),
                title=item.get('title', 'Unknown vulnerability'),
                description=item.get('description', ''),
                package=item.get('name', 'unknown'),
                version=item.get('version', 'unknown'),
                fix_available=item.get('fix_available', False),
                fix_version=item.get('fix_version'),
                cvss_score=item.get('cvss_score')
            )

            dep.vulnerabilities.append(vulnerability)
            dependencies.append(dep)

        return dependencies


class NodeVulnerabilityScanner:
    """Scan Node.js dependencies for vulnerabilities."""

    def scan(self) -> List[Dependency]:
        """Scan Node.js dependencies using npm audit."""
        dependencies = []

        try:
            frontend_dir = Path('frontend')
            if not frontend_dir.exists():
                return dependencies

            # Run npm audit
            result = subprocess.run([
                'npm', 'audit', '--json'
            ], cwd=frontend_dir, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                dependencies = self._parse_npm_audit_results(audit_data)

        except Exception as e:
            print(f"Node.js vulnerability scan error: {e}")

        return dependencies

    def _parse_npm_audit_results(self, audit_data: Dict[str, Any]) -> List[Dependency]:
        """Parse npm audit results into Dependency objects."""
        dependencies = []

        vulnerabilities = audit_data.get('vulnerabilities', {})

        for package_name, vuln_data in vulnerabilities.items():
            dep = Dependency(
                name=package_name,
                version=vuln_data.get('version', 'unknown'),
                type='node'
            )

            # npm audit doesn't provide license info in the JSON output
            # Would need to fetch from package.json or npm registry
            dep.license = 'Unknown'

            for vuln_id, vuln_info in vuln_data.get('vulnerabilities', {}).items():
                vulnerability = Vulnerability(
                    id=vuln_id,
                    severity=vuln_info.get('severity', 'unknown'),
                    title=vuln_info.get('title', 'Unknown vulnerability'),
                    description=vuln_info.get('overview', ''),
                    package=package_name,
                    version=vuln_info.get('affected_versions', 'unknown'),
                    fix_available=bool(vuln_info.get('recommendation')),
                    fix_version=vuln_info.get('recommendation', '').split(' ')[-1] if vuln_info.get('recommendation') else None,
                    cvss_score=vuln_info.get('cvss', {}).get('score')
                )

                dep.vulnerabilities.append(vulnerability)

            dependencies.append(dep)

        return dependencies


class DependencyGovernance:
    """Enforce dependency governance policies."""

    def __init__(self):
        self.allowed_licenses = {
            'MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause',
            'ISC', 'Unlicense', 'CC0-1.0', 'WTFPL'
        }

        self.blocked_packages = {
            'python': ['insecure-package', 'deprecated-module'],
            'node': ['insecure-npm-package', 'deprecated-component']
        }

    def check_license_compliance(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Check if all dependencies have compliant licenses."""
        non_compliant = []

        for dep in dependencies:
            if dep.license not in self.allowed_licenses:
                non_compliant.append({
                    'package': dep.name,
                    'license': dep.license,
                    'type': dep.type
                })

        return {
            'compliant': len(non_compliant) == 0,
            'non_compliant_packages': non_compliant
        }

    def check_blocked_packages(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Check for blocked packages."""
        blocked = []

        for dep in dependencies:
            if dep.name in self.blocked_packages.get(dep.type, []):
                blocked.append({
                    'package': dep.name,
                    'type': dep.type,
                    'reason': 'Blocked by security policy'
                })

        return {
            'has_blocked_packages': len(blocked) > 0,
            'blocked_packages': blocked
        }

    def run_governance_checks(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Run all governance checks."""
        license_check = self.check_license_compliance(dependencies)
        blocked_check = self.check_blocked_packages(dependencies)

        return {
            'license_compliance': license_check,
            'blocked_packages': blocked_check,
            'overall_compliance': (
                license_check['compliant'] and not blocked_check['has_blocked_packages']
            )
        }


# Global scanner instance
vulnerability_scanner = VulnerabilityScanner()
dependency_governance = DependencyGovernance()


def run_security_scan() -> Dict[str, Any]:
    """Run a comprehensive security scan."""
    scan_results = vulnerability_scanner.scan_all()

    # Flatten dependencies for governance checks
    all_dependencies = []
    for deps in scan_results.values():
        all_dependencies.extend(deps)

    governance_results = dependency_governance.run_governance_checks(all_dependencies)
    vulnerability_report = vulnerability_scanner.generate_report()

    return {
        'vulnerability_scan': vulnerability_report,
        'governance_check': governance_results,
        'scan_timestamp': datetime.utcnow().isoformat(),
        'security_score': _calculate_security_score(vulnerability_report, governance_results)
    }


def _calculate_security_score(vuln_report: Dict[str, Any], gov_results: Dict[str, Any]) -> float:
    """Calculate an overall security score (0-100)."""
    base_score = 100

    # Deduct points for vulnerabilities
    critical_vulns = vuln_report.get('critical_vulnerabilities', 0)
    base_score -= critical_vulns * 10  # 10 points per critical vulnerability

    # Deduct points for governance issues
    if not gov_results.get('overall_compliance', False):
        base_score -= 20

    return max(0, min(100, base_score))  # Clamp between 0 and 100
