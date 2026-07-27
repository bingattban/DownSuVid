"""
Package Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.package import Package, PackageStatus, PackageType


class PackageRepository(ABC):
    """Interface for package repository"""
    
    @abstractmethod
    async def get_available_packages(self, package_type: Optional[PackageType] = None) -> List[Package]:
        """
        Get available packages
        
        Args:
            package_type: Filter by package type
            
        Returns:
            List of packages
        """
        pass
    
    @abstractmethod
    async def get_installed_packages(self) -> List[Package]:
        """
        Get installed packages
        
        Returns:
            List of installed packages
        """
        pass
    
    @abstractmethod
    async def get_package(self, package_id: str) -> Optional[Package]:
        """
        Get package by ID
        
        Args:
            package_id: Package ID
            
        Returns:
            Package entity or None
        """
        pass
    
    @abstractmethod
    async def download_package(self, package_id: str) -> bool:
        """
        Download package
        
        Args:
            package_id: Package ID
            
        Returns:
            True if download started
        """
        pass
    
    @abstractmethod
    async def pause_download(self, package_id: str) -> bool:
        """
        Pause package download
        
        Args:
            package_id: Package ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def resume_download(self, package_id: str) -> bool:
        """
        Resume package download
        
        Args:
            package_id: Package ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def cancel_download(self, package_id: str) -> bool:
        """
        Cancel package download
        
        Args:
            package_id: Package ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete_package(self, package_id: str) -> bool:
        """
        Delete package
        
        Args:
            package_id: Package ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def update_package(self, package_id: str) -> bool:
        """
        Update package to latest version
        
        Args:
            package_id: Package ID
            
        Returns:
            True if update started
        """
        pass
    
    @abstractmethod
    async def verify_package(self, package_id: str) -> bool:
        """
        Verify package integrity
        
        Args:
            package_id: Package ID
            
        Returns:
            True if package is valid
        """
        pass
    
    @abstractmethod
    async def repair_package(self, package_id: str) -> bool:
        """
        Repair package
        
        Args:
            package_id: Package ID
            
        Returns:
            True if repair started
        """
        pass
    
    @abstractmethod
    async def get_package_disk_usage(self) -> int:
        """
        Get total disk usage by packages
        
        Returns:
            Size in bytes
        """
        pass
    
    @abstractmethod
    async def is_package_installed(self, source_lang: str, target_lang: str) -> bool:
        """
        Check if package is installed
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if installed
        """
        pass