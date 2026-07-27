"""
File Utilities Module
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.config.constants import (
    STORAGE_ROOT,
    STORAGE_DOWNLOADS,
    STORAGE_VIDEOS,
    STORAGE_SUBTITLES,
    STORAGE_AUDIO,
    STORAGE_TEMP,
    STORAGE_CACHE,
    STORAGE_MODELS,
    STORAGE_PACKAGES,
    MAX_FILE_SIZE,
    MIN_FREE_SPACE
)


class FileUtils(LoggerMixin):
    """File utility functions"""
    
    @staticmethod
    def get_storage_path(*args) -> Path:
        """
        Get absolute storage path
        
        Args:
            *args: Path components
            
        Returns:
            Absolute path
        """
        base = Path.home() / STORAGE_ROOT
        path = base.joinpath(*args)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_download_path() -> Path:
        """Get downloads directory path"""
        return FileUtils.get_storage_path(STORAGE_DOWNLOADS)
    
    @staticmethod
    def get_video_path() -> Path:
        """Get videos directory path"""
        return FileUtils.get_storage_path(STORAGE_VIDEOS)
    
    @staticmethod
    def get_subtitle_path() -> Path:
        """Get subtitles directory path"""
        return FileUtils.get_storage_path(STORAGE_SUBTITLES)
    
    @staticmethod
    def get_audio_path() -> Path:
        """Get audio directory path"""
        return FileUtils.get_storage_path(STORAGE_AUDIO)
    
    @staticmethod
    def get_temp_path() -> Path:
        """Get temp directory path"""
        return FileUtils.get_storage_path(STORAGE_TEMP)
    
    @staticmethod
    def get_cache_path() -> Path:
        """Get cache directory path"""
        return FileUtils.get_storage_path(STORAGE_CACHE)
    
    @staticmethod
    def get_model_path(model_type: str = "") -> Path:
        """Get models directory path"""
        return FileUtils.get_storage_path(STORAGE_MODELS, model_type)
    
    @staticmethod
    def get_package_path(package_type: str = "") -> Path:
        """Get packages directory path"""
        return FileUtils.get_storage_path(STORAGE_PACKAGES, package_type)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe storage
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Limit length
        max_length = 200
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext
        
        return filename or 'unnamed'
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def get_directory_size(directory_path: str) -> int:
        """
        Get directory size
        
        Args:
            directory_path: Path to directory
            
        Returns:
            Total size in bytes
        """
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total += FileUtils.get_file_size(file_path)
        except OSError:
            pass
        return total
    
    @staticmethod
    def get_free_space(directory_path: str = None) -> int:
        """
        Get free disk space
        
        Args:
            directory_path: Directory to check
            
        Returns:
            Free space in bytes
        """
        try:
            if directory_path is None:
                directory_path = str(Path.home())
            
            if hasattr(shutil, 'disk_usage'):
                usage = shutil.disk_usage(directory_path)
                return usage.free
            else:
                import psutil
                usage = psutil.disk_usage(directory_path)
                return usage.free
        except Exception:
            return 0
    
    @staticmethod
    def verify_sha256(file_path: str, expected_hash: str) -> bool:
        """
        Verify file SHA256 hash
        
        Args:
            file_path: Path to file
            expected_hash: Expected SHA256 hash
            
        Returns:
            True if hash matches
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            
            actual_hash = sha256_hash.hexdigest()
            return actual_hash.lower() == expected_hash.lower()
            
        except Exception as e:
            FileUtils.logger.error(f"Hash verification failed: {e}")
            return False
    
    @staticmethod
    def calculate_sha256(file_path: str) -> Optional[str]:
        """
        Calculate SHA256 hash of file
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash string
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            FileUtils.logger.error(f"Hash calculation failed: {e}")
            return None
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """
        Ensure directory exists
        
        Args:
            path: Directory path
            
        Returns:
            True if directory exists
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            FileUtils.logger.error(f"Failed to create directory: {e}")
            return False
    
    @staticmethod
    def clean_temp_files(max_age_hours: int = 24) -> int:
        """
        Clean temporary files older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files removed
        """
        count = 0
        try:
            temp_path = FileUtils.get_temp_path()
            now = datetime.now()
            
            for file_path in temp_path.iterdir():
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    age_hours = (now - file_age).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        file_path.unlink()
                        count += 1
            
            return count
            
        except Exception as e:
            FileUtils.logger.error(f"Failed to clean temp files: {e}")
            return count
    
    @staticmethod
    def clean_cache(max_size_mb: int = 100) -> int:
        """
        Clean cache if exceeds maximum size
        
        Args:
            max_size_mb: Maximum cache size in MB
            
        Returns:
            Number of files removed
        """
        count = 0
        try:
            cache_path = FileUtils.get_cache_path()
            total_size = FileUtils.get_directory_size(str(cache_path))
            max_size = max_size_mb * 1024 * 1024
            
            if total_size > max_size:
                # Remove oldest files first
                files = [(f, f.stat().st_mtime) 
                        for f in cache_path.iterdir() if f.is_file()]
                files.sort(key=lambda x: x[1])
                
                for file_path, _ in files:
                    if total_size <= max_size:
                        break
                    
                    file_size = FileUtils.get_file_size(str(file_path))
                    file_path.unlink()
                    total_size -= file_size
                    count += 1
            
            return count
            
        except Exception as e:
            FileUtils.logger.error(f"Failed to clean cache: {e}")
            return count
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size to human readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"