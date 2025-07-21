"""
Encryption Manager for Intelligence OS
Handles encryption/decryption of sensitive data
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self):
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with key from environment"""
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if not encryption_key:
            # Generate a key if none exists (for development only)
            logger.warning("No ENCRYPTION_KEY found in environment. Generating temporary key.")
            encryption_key = Fernet.generate_key().decode()
            logger.warning(f"Generated encryption key: {encryption_key}")
            logger.warning("Please set ENCRYPTION_KEY in your environment variables for production!")
        
        try:
            # If the key is a string, encode it
            if isinstance(encryption_key, str):
                # Derive a proper key from the string
                key_bytes = self._derive_key_from_string(encryption_key)
            else:
                key_bytes = encryption_key
            
            self._fernet = Fernet(key_bytes)
            logger.info("Encryption manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {str(e)}")
            raise
    
    def _derive_key_from_string(self, key_string: str) -> bytes:
        """Derive a proper Fernet key from a string"""
        # Use a fixed salt for consistency (in production, use a proper salt)
        salt = os.getenv('HASH_SALT', 'intelligence_os_salt').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(key_string.encode()))
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """Encrypt data and return base64 encoded string"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self._fernet.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def encrypt_dict(self, data: dict) -> dict:
        """Encrypt sensitive fields in a dictionary"""
        sensitive_fields = [
            'password', 'api_key', 'secret', 'token', 'credential',
            'private_key', 'access_token', 'refresh_token'
        ]
        
        encrypted_data = data.copy()
        
        for key, value in data.items():
            if any(sensitive_field in key.lower() for sensitive_field in sensitive_fields):
                if isinstance(value, str) and value:
                    encrypted_data[key] = self.encrypt(value)
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict) -> dict:
        """Decrypt sensitive fields in a dictionary"""
        sensitive_fields = [
            'password', 'api_key', 'secret', 'token', 'credential',
            'private_key', 'access_token', 'refresh_token'
        ]
        
        decrypted_data = data.copy()
        
        for key, value in data.items():
            if any(sensitive_field in key.lower() for sensitive_field in sensitive_fields):
                if isinstance(value, str) and value:
                    try:
                        decrypted_data[key] = self.decrypt(value)
                    except Exception:
                        # If decryption fails, assume it's not encrypted
                        pass
        
        return decrypted_data
    
    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """Create a hash of data (one-way, for verification)"""
        if salt is None:
            salt = os.getenv('HASH_SALT', 'intelligence_os_salt')
        
        combined = f"{data}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str, salt: Optional[str] = None) -> bool:
        """Verify data against its hash"""
        return self.hash_data(data, salt) == hash_value
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Encrypt a file"""
        if output_path is None:
            output_path = f"{file_path}.encrypted"
        
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            encrypted_data = self._fernet.encrypt(file_data)
            
            with open(output_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            logger.info(f"File encrypted successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file"""
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        try:
            with open(encrypted_file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            decrypted_data = self._fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as file:
                file.write(decrypted_data)
            
            logger.info(f"File decrypted successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File decryption failed: {str(e)}")
            raise

# Global encryption manager instance
encryption_manager = EncryptionManager()