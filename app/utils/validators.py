"""
Validation Utilities Module
"""

import re
from typing import Optional, Tuple
from pathlib import Path
import os


class Validators:
    """Utility class for validation functions"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
        """
        if not url:
            return False
        
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        
        return bool(url_pattern.match(url))
    
    @staticmethod
    def validate_quality(quality: str) -> bool:
        """
        Validate video quality
        
        Args:
            quality: Quality string (e.g., '720p')
            
        Returns:
            True if valid
        """
        if not quality:
            return False
        
        # Must end with 'p'
        if not quality.endswith('p'):
            return False
        
        # Extract number
        try:
            height = int(quality.rstrip('p'))
            return height > 0 and height <= 4320  # Max 8K
        except ValueError:
            return False
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """
        Validate file path
        
        Args:
            path: File path to validate
            
        Returns:
            True if path is safe
        """
        if not path:
            return False
        
        # Check for dangerous paths
        dangerous_patterns = ['..', '~', '$', '`', '|', ';', '&']
        for pattern in dangerous_patterns:
            if pattern in path:
                return False
        
        # Check path length
        if len(path) > 4096:
            return False
        
        try:
            # Try to resolve path
            Path(path).resolve()
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate filename
        
        Args:
            filename: Filename to validate
            
        Returns:
            True if valid
        """
        if not filename:
            return False
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in filename:
                return False
        
        # Check length
        if len(filename) > 255:
            return False
        
        # Check for reserved names (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
        ]
        
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    @staticmethod
    def validate_language_code(code: str) -> bool:
        """
        Validate language code (ISO 639-1 or 639-2)
        
        Args:
            code: Language code
            
        Returns:
            True if valid
        """
        if not code:
            return False
        
        # ISO 639-1: 2 letters
        if len(code) == 2 and code.isalpha():
            return True
        
        # ISO 639-2: 3 letters
        if len(code) == 3 and code.isalpha():
            return True
        
        return False
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text for safe display
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def validate_sha256(hash_string: str) -> bool:
        """
        Validate SHA256 hash format
        
        Args:
            hash_string: Hash string
            
        Returns:
            True if valid SHA256
        """
        if not hash_string:
            return False
        
        sha256_pattern = re.compile(r'^[a-fA-F0-9]{64}$')
        return bool(sha256_pattern.match(hash_string))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address
            
        Returns:
            True if valid
        """
        if not email:
            return False
        
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        return bool(email_pattern.match(email))
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get file extension
        
        Args:
            filename: Filename
            
        Returns:
            File extension (lowercase)
        """
        return os.path.splitext(filename)[1].lower()