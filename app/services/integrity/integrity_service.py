"""
Integrity Service Module
"""

import os
import asyncio
import hashlib
from typing import Optional, Dict, List
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils


class IntegrityService(LoggerMixin):
    """Service for verifying file integrity"""
    
    def __init__(self):
        self.verification_cache: Dict[str, str] = {}
        self.logger.info("IntegrityService initialized")
    
    async def verify_file(self, file_path: str, 
                         expected_hash: Optional[str] = None,
                         algorithm: str = 'sha256') -> bool:
        """
        Verify file integrity
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm (sha256, md5)
            
        Returns:
            True if file is valid
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False
            
            # Check cache first
            if file_path in self.verification_cache and not expected_hash:
                return True
            
            # Calculate hash
            actual_hash = await self._calculate_hash(file_path, algorithm)
            
            if not actual_hash:
                return False
            
            # If expected hash provided, compare
            if expected_hash:
                is_valid = actual_hash.lower() == expected_hash.lower()
                
                if is_valid:
                    self.verification_cache[file_path] = actual_hash
                    self.logger.info(f"File verified: {file_path}")
                else:
                    self.logger.warning(f"Hash mismatch for: {file_path}")
                
                return is_valid
            
            # No expected hash, just cache and return True
            self.verification_cache[file_path] = actual_hash
            return True
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False
    
    async def _calculate_hash(self, file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """Calculate file hash"""
        try:
            if algorithm == 'sha256':
                hasher = hashlib.sha256()
            elif algorithm == 'md5':
                hasher = hashlib.md5()
            else:
                self.logger.error(f"Unsupported algorithm: {algorithm}")
                return None
            
            loop = asyncio.get_event_loop()
            
            def _hash_file():
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        hasher.update(chunk)
                return hasher.hexdigest()
            
            return await loop.run_in_executor(None, _hash_file)
            
        except Exception as e:
            self.logger.error(f"Hash calculation failed: {e}")
            return None
    
    async def verify_directory(self, directory_path: str,
                              expected_hashes: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
        """
        Verify all files in directory
        
        Args:
            directory_path: Directory path
            expected_hashes: Dictionary of filename to expected hash
            
        Returns:
            Dictionary of file path to verification result
        """
        results = {}
        
        try:
            if not os.path.exists(directory_path):
                return results
            
            for root, dirs, files in os.walk(directory_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    expected = None
                    if expected_hashes:
                        expected = expected_hashes.get(filename)
                    
                    results[file_path] = await self.verify_file(file_path, expected)
            
        except Exception as e:
            self.logger.error(f"Directory verification failed: {e}")
        
        return results
    
    async def generate_checksum_file(self, directory_path: str, 
                                    output_file: str = 'checksums.sha256') -> bool:
        """
        Generate checksum file for directory
        
        Args:
            directory_path: Directory path
            output_file: Output filename
            
        Returns:
            True if successful
        """
        try:
            checksums = []
            
            for root, dirs, files in os.walk(directory_path):
                for filename in sorted(files):
                    file_path = os.path.join(root, filename)
                    hash_value = await self._calculate_hash(file_path)
                    
                    if hash_value:
                        relative_path = os.path.relpath(file_path, directory_path)
                        checksums.append(f"{hash_value}  {relative_path}")
            
            output_path = os.path.join(directory_path, output_file)
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(checksums))
            
            self.logger.info(f"Checksum file generated: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate checksum: {e}")
            return False
    
    async def verify_checksum_file(self, checksum_file: str, 
                                  base_directory: Optional[str] = None) -> bool:
        """
        Verify files against checksum file
        
        Args:
            checksum_file: Path to checksum file
            base_directory: Base directory for relative paths
            
        Returns:
            True if all files verified
        """
        try:
            if not os.path.exists(checksum_file):
                return False
            
            if base_directory is None:
                base_directory = os.path.dirname(checksum_file)
            
            with open(checksum_file, 'r') as f:
                lines = f.readlines()
            
            all_valid = True
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('  ', 1)
                if len(parts) != 2:
                    continue
                
                expected_hash, relative_path = parts
                file_path = os.path.join(base_directory, relative_path)
                
                if not await self.verify_file(file_path, expected_hash):
                    all_valid = False
                    self.logger.warning(f"Verification failed: {relative_path}")
            
            return all_valid
            
        except Exception as e:
            self.logger.error(f"Checksum verification failed: {e}")
            return False
    
    async def clear_cache(self):
        """Clear verification cache"""
        self.verification_cache.clear()
        self.logger.debug("Verification cache cleared")
    
    async def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            File info dictionary
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                'path': file_path,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'hash_sha256': await self._calculate_hash(file_path, 'sha256'),
                'hash_md5': await self._calculate_hash(file_path, 'md5'),
                'is_valid': await self.verify_file(file_path),
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            return None