"""
Manage Packages Use Case
"""

from typing import List, Optional, Dict
from app.utils.logger import LoggerMixin
from app.domain.entities.package import Package, PackageStatus, PackageType
from app.domain.interfaces.package_repository import PackageRepository


class ManagePackagesUseCase(LoggerMixin):
    """Use case for managing translation packages"""
    
    def __init__(self, package_repository: PackageRepository):
        self.package_repository = package_repository
        self.logger.info("ManagePackagesUseCase initialized")
    
    async def get_available_packages(self, 
                                     package_type: Optional[PackageType] = None) -> List[Package]:
        """
        Get available packages
        
        Args:
            package_type: Filter by type
            
        Returns:
            List of packages
        """
        return await self.package_repository.get_available_packages(package_type)
    
    async def get_installed_packages(self) -> List[Package]:
        """Get installed packages"""
        return await self.package_repository.get_installed_packages()
    
    async def download_package(self, package_id: str) -> bool:
        """
        Download a package
        
        Args:
            package_id: Package ID
            
        Returns:
            True if download started
        """
        package = await self.package_repository.get_package(package_id)
        
        if not package:
            self.logger.error(f"Package not found: {package_id}")
            return False
        
        if package.is_downloading():
            self.logger.warning(f"Package already downloading: {package_id}")
            return False
        
        success = await self.package_repository.download_package(package_id)
        
        if success:
            self.logger.info(f"Package download started: {package_id}")
        
        return success
    
    async def delete_package(self, package_id: str) -> bool:
        """
        Delete a package
        
        Args:
            package_id: Package ID
            
        Returns:
            True if deleted
        """
        package = await self.package_repository.get_package(package_id)
        
        if not package:
            self.logger.error(f"Package not found: {package_id}")
            return False
        
        if package.is_downloading():
            self.logger.warning(f"Cannot delete downloading package: {package_id}")
            return False
        
        return await self.package_repository.delete_package(package_id)
    
    async def update_package(self, package_id: str) -> bool:
        """
        Update a package
        
        Args:
            package_id: Package ID
            
        Returns:
            True if update started
        """
        package = await self.package_repository.get_package(package_id)
        
        if not package:
            self.logger.error(f"Package not found: {package_id}")
            return False
        
        return await self.package_repository.update_package(package_id)
    
    async def verify_package(self, package_id: str) -> bool:
        """
        Verify package integrity
        
        Args:
            package_id: Package ID
            
        Returns:
            True if package is valid
        """
        return await self.package_repository.verify_package(package_id)
    
    async def repair_package(self, package_id: str) -> bool:
        """
        Repair a package
        
        Args:
            package_id: Package ID
            
        Returns:
            True if repair started
        """
        return await self.package_repository.repair_package(package_id)
    
    async def get_disk_usage(self) -> int:
        """Get total package disk usage"""
        return await self.package_repository.get_package_disk_usage()
    
    async def is_package_installed(self, source_lang: str, 
                                   target_lang: str) -> bool:
        """
        Check if translation package is installed
        
        Args:
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            True if installed
        """
        return await self.package_repository.is_package_installed(
            source_lang, target_lang
        )
    
    async def get_package_stats(self) -> Dict:
        """
        Get package statistics
        
        Returns:
            Statistics dictionary
        """
        installed = await self.get_installed_packages()
        available = await self.get_available_packages()
        
        return {
            'total_installed': len(installed),
            'total_available': len(available),
            'disk_usage': await self.get_disk_usage(),
            'installed_packages': [
                {
                    'id': p.id,
                    'name': p.name,
                    'language_pair': p.get_language_pair(),
                    'version': p.version,
                    'size': p.size_total,
                }
                for p in installed
            ],
            'supported_languages': list(set(
                p.target_language for p in installed
            )),
        }