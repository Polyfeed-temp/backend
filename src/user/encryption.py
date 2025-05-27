import os
import base64
from typing import Optional, Union
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class UserDataEncryption:
    """
    Handles encryption/decryption of sensitive user data using Fernet symmetric encryption.
    Supports key rotation and secure key derivation from environment variables.
    """
    
    def __init__(self):
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with key rotation support."""
        try:
            # Get encryption keys from environment
            primary_key = self._get_or_generate_key("USER_ENCRYPTION_KEY")
            rotation_key = os.getenv("USER_ENCRYPTION_KEY_ROTATION")
            
            if rotation_key:
                # Support key rotation - primary key for new data, rotation key for old data
                keys = [base64.urlsafe_b64decode(primary_key), base64.urlsafe_b64decode(rotation_key)]
                self._fernet = MultiFernet([Fernet(key) for key in keys])
                logger.info("Encryption initialized with key rotation support")
            else:
                # Single key mode
                self._fernet = Fernet(base64.urlsafe_b64decode(primary_key))
                logger.info("Encryption initialized with single key")
                
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise RuntimeError("Encryption initialization failed")
    
    def _get_or_generate_key(self, env_var: str) -> str:
        """Get encryption key from environment or generate a new one."""
        key = os.getenv(env_var)
        if not key:
            # Generate a new key and warn about it
            new_key = base64.urlsafe_b64encode(Fernet.generate_key()).decode()
            logger.warning(f"No {env_var} found in environment. Generated new key: {new_key}")
            logger.warning("Please add this key to your .env file for production use!")
            return new_key
        return key
    
    def encrypt_field(self, value: Optional[str]) -> Optional[str]:
        """
        Encrypt a string field. Returns None if input is None.
        
        Args:
            value: The string to encrypt
            
        Returns:
            Base64 encoded encrypted string or None
        """
        if value is None or value == "":
            return value
            
        try:
            encrypted_bytes = self._fernet.encrypt(value.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed for field: {e}")
            raise ValueError("Field encryption failed")
    
    def decrypt_field(self, encrypted_value: Optional[str]) -> Optional[str]:
        """
        Decrypt a string field. Returns None if input is None.
        
        Args:
            encrypted_value: Base64 encoded encrypted string
            
        Returns:
            Decrypted string or None
        """
        if encrypted_value is None or encrypted_value == "":
            return encrypted_value
            
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed for field: {e}")
            # Return the original value if decryption fails (might be unencrypted legacy data)
            logger.warning("Returning original value - might be legacy unencrypted data")
            return encrypted_value
    
    def encrypt_user_sensitive_fields(self, user_data: dict) -> dict:
        """
        Encrypt sensitive fields in user data dictionary.
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            Dictionary with sensitive fields encrypted
        """
        sensitive_fields = ['email', 'firstName', 'lastName', 'monashId', 'monashObjectId']
        encrypted_data = user_data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = self.encrypt_field(encrypted_data[field])
        
        return encrypted_data
    
    def decrypt_user_sensitive_fields(self, user_data: dict) -> dict:
        """
        Decrypt sensitive fields in user data dictionary.
        
        Args:
            user_data: Dictionary containing user data with encrypted fields
            
        Returns:
            Dictionary with sensitive fields decrypted
        """
        sensitive_fields = ['email', 'firstName', 'lastName', 'monashId', 'monashObjectId']
        decrypted_data = user_data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data:
                decrypted_data[field] = self.decrypt_field(decrypted_data[field])
        
        return decrypted_data
    
    def is_encrypted(self, value: str) -> bool:
        """
        Check if a value appears to be encrypted (basic heuristic).
        
        Args:
            value: String to check
            
        Returns:
            True if value appears encrypted
        """
        if not value:
            return False
        
        try:
            # Try to decode as base64 and check if it looks like Fernet token
            decoded = base64.urlsafe_b64decode(value.encode('utf-8'))
            # Fernet tokens are typically 60+ bytes
            return len(decoded) >= 60
        except:
            return False

# Global encryption instance
_encryption_instance = None

def get_encryption() -> UserDataEncryption:
    """Get the global encryption instance (singleton pattern)."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = UserDataEncryption()
    return _encryption_instance

# Convenience functions for direct use
def encrypt_sensitive_data(data: dict) -> dict:
    """Encrypt sensitive fields in a data dictionary."""
    return get_encryption().encrypt_user_sensitive_fields(data)

def decrypt_sensitive_data(data: dict) -> dict:
    """Decrypt sensitive fields in a data dictionary."""
    return get_encryption().decrypt_user_sensitive_fields(data)

def encrypt_field(value: Optional[str]) -> Optional[str]:
    """Encrypt a single field value."""
    return get_encryption().encrypt_field(value)

def decrypt_field(value: Optional[str]) -> Optional[str]:
    """Decrypt a single field value."""
    return get_encryption().decrypt_field(value) 