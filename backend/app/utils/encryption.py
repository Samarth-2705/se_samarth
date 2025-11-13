"""
Encryption utilities for data security
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""

    def __init__(self, secret_key=None):
        """Initialize encryption service with a secret key"""
        if secret_key is None:
            secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

        # Derive a key from the secret
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'admission_system_salt',  # In production, use a random salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.cipher = Fernet(key)

    def encrypt(self, data):
        """Encrypt data"""
        if data is None:
            return None
        if isinstance(data, str):
            data = data.encode()
        encrypted = self.cipher.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data):
        """Decrypt data"""
        if encrypted_data is None:
            return None
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception:
            return None


# Global encryption service instance
encryption_service = EncryptionService()


def encrypt_field(data):
    """Encrypt a field"""
    return encryption_service.encrypt(data)


def decrypt_field(encrypted_data):
    """Decrypt a field"""
    return encryption_service.decrypt(encrypted_data)
