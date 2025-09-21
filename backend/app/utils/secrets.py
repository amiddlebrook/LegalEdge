"""Secrets rotation and encryption utilities."""
import asyncio
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from app.core.config import settings


class EncryptionManager:
    """Manage encryption and decryption of sensitive data."""

    def __init__(self, key: Optional[str] = None):
        self.key = key or settings.encryption_key or self._generate_key()
        self.cipher = self._setup_cipher()

    def _generate_key(self) -> str:
        """Generate a new encryption key."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

    def _setup_cipher(self) -> Fernet:
        """Setup the Fernet cipher."""
        if isinstance(self.key, str):
            key_bytes = self.key.encode()
        else:
            key_bytes = self.key
        return Fernet(key_bytes)

    def encrypt(self, data: str) -> str:
        """Encrypt data."""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


class SecretsManager:
    """Manage application secrets with rotation."""

    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.secrets: Dict[str, Dict[str, Any]] = {}
        self.rotation_schedule: Dict[str, datetime] = {}

    def store_secret(self, name: str, value: str, rotation_days: int = 90) -> None:
        """Store an encrypted secret."""
        encrypted_value = self.encryption_manager.encrypt(value)
        self.secrets[name] = {
            'value': encrypted_value,
            'created_at': datetime.utcnow(),
            'rotation_due': datetime.utcnow() + timedelta(days=rotation_days)
        }
        self.rotation_schedule[name] = datetime.utcnow() + timedelta(days=rotation_days)

    def get_secret(self, name: str) -> Optional[str]:
        """Retrieve and decrypt a secret."""
        if name not in self.secrets:
            return None

        secret_data = self.secrets[name]
        if datetime.utcnow() > secret_data['rotation_due']:
            # Secret has expired, should be rotated
            return None

        return self.encryption_manager.decrypt(secret_data['value'])

    def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret with a new value."""
        if name not in self.secrets:
            return False

        self.store_secret(name, new_value)
        return True

    def list_secrets(self) -> Dict[str, Dict[str, Any]]:
        """List all secrets (without exposing values)."""
        return {
            name: {
                'created_at': data['created_at'],
                'rotation_due': data['rotation_due'],
                'needs_rotation': datetime.utcnow() > data['rotation_due']
            }
            for name, data in self.secrets.items()
        }

    async def check_rotation_schedule(self) -> Dict[str, bool]:
        """Check which secrets need rotation."""
        now = datetime.utcnow()
        needs_rotation = {}

        for name, due_date in self.rotation_schedule.items():
            needs_rotation[name] = now > due_date

        return needs_rotation


class KeyRotationManager:
    """Manage encryption key rotation."""

    def __init__(self):
        self.current_key = settings.encryption_key
        self.previous_keys: list[str] = []
        self.key_history: Dict[str, datetime] = {}

    def rotate_key(self) -> str:
        """Generate and set a new encryption key."""
        new_key = EncryptionManager()._generate_key()

        # Store current key as previous
        if self.current_key:
            self.previous_keys.append(self.current_key)
            self.key_history[self.current_key] = datetime.utcnow()

        self.current_key = new_key
        return new_key

    def decrypt_with_fallback(self, encrypted_data: str) -> str:
        """Try to decrypt with current key, fallback to previous keys."""
        current_manager = EncryptionManager(self.current_key)

        try:
            return current_manager.decrypt(encrypted_data)
        except Exception:
            # Try previous keys
            for prev_key in self.previous_keys:
                try:
                    prev_manager = EncryptionManager(prev_key)
                    return prev_manager.decrypt(encrypted_data)
                except Exception:
                    continue

            raise Exception("Unable to decrypt data with any available key")


# Global instances
secrets_manager = SecretsManager()
key_rotation_manager = KeyRotationManager()


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data for storage."""
    return secrets_manager.encryption_manager.encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    return key_rotation_manager.decrypt_with_fallback(encrypted_data)


async def rotate_database_password() -> bool:
    """Rotate the database password."""
    try:
        # Generate new password
        new_password = secrets.token_urlsafe(32)

        # This would typically involve updating the database and secrets manager
        # For now, just log the rotation
        print(f"Database password rotation initiated at {datetime.utcnow()}")
        return True
    except Exception as e:
        print(f"Database password rotation failed: {e}")
        return False


async def run_secrets_rotation_check() -> None:
    """Periodic check for secrets that need rotation."""
    while True:
        try:
            needs_rotation = await secrets_manager.check_rotation_schedule()

            for secret_name, needs_rotating in needs_rotation.items():
                if needs_rotating:
                    print(f"Secret {secret_name} needs rotation")
                    # Trigger rotation logic here

        except Exception as e:
            print(f"Error during secrets rotation check: {e}")

        # Wait for next check (daily)
        await asyncio.sleep(86400)  # 24 hours
