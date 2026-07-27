"""
Package Repository Implementation
"""

from typing import Optional, List
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.domain.entities.package import Package, PackageStatus, PackageType, PackageProvider
from app.domain.interfaces.package_repository import PackageRepository
from app.services.packages.package_service import PackageService
from app.database.dao.package_dao import PackageDAO


class PackageRepositoryImpl(PackageRepository, LoggerMixin):
    """Implementation of PackageRepository"""
    
    def __init__(self):
        self.package_service = PackageService()
        self.package_dao = PackageDAO()
        self.logger.info("PackageRepositoryImpl initialized")
    
    async def get_available_packages(self, package_type: Optional[PackageType] = None) -> List[Package]:
        """Get available packages"""
        try:
            packages_data = await self.package_service.get_available_packages(package_type)
            return [self._dict_to_entity(p) for p in packages_data]
        except Exception as e:
            self.logger.error(f"Failed to get available packages: {e}")
            return []
    
    async def get_installed_packages(self) -> List[Package]:
        """Get installed packages"""
        try:
            db_packages = self.package_dao.get_installed()
            return [self._db_to_entity(p) for p in db_packages]
        except Exception as e:
            self.logger.error(f"Failed to get installed packages: {e}")
            return []
    
    async def get_package(self, package_id: str) -> Optional[Package]:
        """Get package by ID"""
        try:
            db_package = self.package_dao.get_by_id(package_id)
            if db_package:
                return self._db_to_entity(db_package)
            
            available = await self.get_available_packages()
            for package in available:
                if package.id == package_id:
                    return package
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get package: {e}")
            return None
    
    async def download_package(self, package_id: str) -> bool:
        """Download package"""
        try:
            success = await self.package_service.download_package(package_id)
            
            if success:
                package = await self.get_package(package_id)
                if package:
                    package.status = PackageStatus.DOWNLOADING
                    await self._save_to_database(package)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to download package: {e}")
            return False
    
    async def pause_download(self, package_id: str) -> bool:
        """Pause package download"""
        try:
            return await self.package_service.cancel_download(package_id)
        except Exception as e:
            self.logger.error(f"Failed to pause download: {e}")
            return False
    
    async def resume_download(self, package_id: str) -> bool:
        """Resume package download"""
        return await self.download_package(package_id)
    
    async def cancel_download(self, package_id: str) -> bool:
        """Cancel package download"""
        return await self.package_service.cancel_download(package_id)
    
    async def delete_package(self, package_id: str) -> bool:
        """Delete package"""
        try:
            success = await self.package_service.delete_package(package_id)
            
            if success:
                self.package_dao.delete(package_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete package: {e}")
            return False
    
    async def update_package(self, package_id: str) -> bool:
        """Update package"""
        await self.delete_package(package_id)
        return await self.download_package(package_id)
    
    async def verify_package(self, package_id: str) -> bool:
        """Verify package integrity"""
        try:
            package = await self.get_package(package_id)
            
            if package:
                is_installed = await self.package_service.is_package_installed(package_id)
                
                if is_installed:
                    self.package_dao.update(package_id, {'status': 'installed'})
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify package: {e}")
            return False
    
    async def repair_package(self, package_id: str) -> bool:
        """Repair package"""
        return await self.update_package(package_id)
    
    async def get_package_disk_usage(self) -> int:
        """Get total package disk usage"""
        return await self.package_service.get_disk_usage()
    
    async def is_package_installed(self, source_lang: str, target_lang: str) -> bool:
        """Check if package is installed"""
        try:
            db_package = self.package_dao.get_by_language_pair(source_lang, target_lang)
            return db_package is not None and db_package.get('status') == 'installed'
        except Exception:
            return False
    
    async def _save_to_database(self, package: Package):
        """Save package to database"""
        try:
            data = self._entity_to_db(package)
            
            existing = self.package_dao.get_by_id(package.id)
            if existing:
                self.package_dao.update(package.id, data)
            else:
                self.package_dao.insert(data)
                
        except Exception as e:
            self.logger.error(f"Failed to save package: {e}")
    
    def _entity_to_db(self, package: Package) -> dict:
        """Convert Package entity to database dict"""
        return {
            'id': package.id,
            'name': package.name,
            'type': package.type.value,
            'source_lang': package.source_language,
            'target_lang': package.target_language,
            'version': package.version,
            'file_path': package.file_path,
            'size_total': package.size_total,
            'size_downloaded': package.size_downloaded,
            'sha256': package.sha256,
            'status': package.status.value,
            'progress': package.progress,
            'is_active': 1 if package.is_active else 0,
            'created_at': package.created_at.isoformat(),
            'updated_at': package.updated_at.isoformat(),
        }
    
    def _db_to_entity(self, data: dict) -> Package:
        """Convert database dict to Package entity"""
        return Package(
            id=data.get('id', ''),
            name=data.get('name', ''),
            type=PackageType(data.get('type', 'translation')),
            provider=PackageProvider.CUSTOM,
            source_language=data.get('source_lang', ''),
            target_language=data.get('target_lang', ''),
            version=data.get('version'),
            file_path=data.get('file_path'),
            size_total=data.get('size_total', 0),
            size_downloaded=data.get('size_downloaded', 0),
            sha256=data.get('sha256'),
            status=PackageStatus(data.get('status', 'not_installed')),
            progress=data.get('progress', 0.0),
            is_active=bool(data.get('is_active', 0)),
        )
    
    def _dict_to_entity(self, data: dict) -> Package:
        """Convert service dict to Package entity"""
        return Package(
            id=data.get('id', ''),
            name=data.get('name', ''),
            type=PackageType(data.get('type', 'translation')),
            provider=PackageProvider(data.get('provider', 'custom')),
            source_language=data.get('source_lang', ''),
            target_language=data.get('target_lang', ''),
            source_language_name=data.get('source_lang_name'),
            target_language_name=data.get('target_lang_name'),
            size_total=data.get('size', 0),
            version=data.get('version'),
            status=PackageStatus.INSTALLED if data.get('installed') else PackageStatus.NOT_INSTALLED,
            description=data.get('description'),
        )