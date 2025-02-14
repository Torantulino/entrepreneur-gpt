import json
from typing import Optional

from cryptography.fernet import Fernet

from backend.util.settings import Settings

ENCRYPTION_KEY = Settings().secrets.encryption_key


class JSONCryptor:
    def __init__(self, key: Optional[str] = None):
        # Use provided key or get from environment
        self.key = key or ENCRYPTION_KEY
        if not self.key:
            raise ValueError(
                "Encryption key must be provided or set in ENCRYPTION_KEY environment variable"
            )
        self.fernet = Fernet(
            self.key.encode() if isinstance(self.key, str) else self.key
        )

    def encrypt(self, data: dict) -> str:
        """Encrypt dictionary data to string"""
        json_str = json.dumps(data)
        encrypted = self.fernet.encrypt(json_str.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_str: str) -> dict:
        """Decrypt string to dictionary"""
        if not encrypted_str:
            return {}
        try:
            decrypted = self.fernet.decrypt(encrypted_str.encode())
            return json.loads(decrypted.decode())
        except Exception:
            return {}
