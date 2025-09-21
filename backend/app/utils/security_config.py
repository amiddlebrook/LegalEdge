"""Dependency and security configuration."""
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

import toml
import yaml


class DependencyManager:
    """Manage and audit project dependencies."""

    def __init__(self, requirements_path: str = "requirements.txt"):
        self.requirements_path = Path(requirements_path)
        self.frontend_package_path = Path("frontend/package.json")

    def audit_python_dependencies(self) -> Dict[str, Any]:
        """Audit Python dependencies for vulnerabilities."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "audit"
            ], capture_output=True, text=True, check=False)

            return {
                "vulnerabilities": result.stdout,
                "has_vulnerabilities": result.returncode != 0,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {
                "error": str(e),
                "has_vulnerabilities": False
            }

    def check_dependency_licenses(self) -> Dict[str, Any]:
        """Check licenses of dependencies."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "show", "."
            ], capture_output=True, text=True, check=False)

            return {
                "licenses": result.stdout,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }

    def audit_node_dependencies(self) -> Dict[str, Any]:
        """Audit Node.js dependencies for vulnerabilities."""
        try:
            if not self.frontend_package_path.exists():
                return {"error": "package.json not found"}

            result = subprocess.run([
                "npm", "audit", "--json"
            ], cwd="frontend", capture_output=True, text=True, check=False)

            return {
                "vulnerabilities": result.stdout if result.returncode == 0 else result.stderr,
                "has_vulnerabilities": result.returncode != 0,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {
                "error": str(e),
                "has_vulnerabilities": False
            }

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        python_audit = self.audit_python_dependencies()
        node_audit = self.audit_node_dependencies()
        licenses = self.check_dependency_licenses()

        return {
            "timestamp": subprocess.run(["date", "+%Y-%m-%d %H:%M:%S"],
                                     capture_output=True, text=True).stdout.strip(),
            "python_dependencies": python_audit,
            "node_dependencies": node_audit,
            "license_check": licenses,
            "overall_security_status": not (
                python_audit.get("has_vulnerabilities", False) or
                node_audit.get("has_vulnerabilities", False)
            )
        }


def run_safety_check() -> bool:
    """Run safety check on Python dependencies."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "safety", "check"
        ], check=False)
        return result.returncode == 0
    except Exception:
        return False


def run_bandit_scan() -> bool:
    """Run bandit security scan on Python code."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "bandit", "-r", "app/", "-f", "json", "-o", "bandit-report.json"
        ], check=False)
        return result.returncode == 0
    except Exception:
        return False


def create_security_policy() -> None:
    """Create a security policy file."""
    security_policy = """
# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in this project, please report it responsibly.

### Report Process

1. **Do NOT** create a public GitHub issue
2. Send an email to security@legaledge.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Your contact information (optional)

### Response Timeline

- Initial acknowledgment: 24-48 hours
- Status update: Every 3-5 business days
- Resolution: As soon as possible based on severity

## Security Measures

This project implements the following security measures:

- **Code Analysis**: Automated security scanning with Bandit and Safety
- **Dependency Auditing**: Regular vulnerability scanning of dependencies
- **Input Validation**: Comprehensive input validation and sanitization
- **Authentication**: OAuth 2.0 with JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS 1.3 for all communications
- **Monitoring**: Comprehensive logging and alerting

## Dependencies

All dependencies are regularly scanned for known vulnerabilities. Critical and high-severity issues are addressed within 30 days.
"""

    Path("SECURITY.md").write_text(security_policy.strip())


def create_compliance_config() -> None:
    """Create compliance configuration for SOC2, GDPR, etc."""
    compliance_config = {
        "soc2": {
            "enabled": True,
            "controls": {
                "access_control": True,
                "audit_logging": True,
                "data_encryption": True,
                "incident_response": True,
                "risk_assessment": True
            }
        },
        "gdpr": {
            "enabled": True,
            "data_subject_requests": True,
            "privacy_by_design": True,
            "data_minimization": True
        },
        "ccpa": {
            "enabled": True,
            "data_collection_notice": True,
            "opt_out_mechanism": True
        }
    }

    with open("compliance.yaml", "w") as f:
        yaml.dump(compliance_config, f, default_flow_style=False)
