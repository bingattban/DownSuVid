"""
Model Controller Module
"""

import asyncio
from typing import Optional, Callable, List, Dict

from app.utils.logger import LoggerMixin
from app.services.models.model_service import ModelService
from app.services.packages.package_service import PackageService


class ModelController(LoggerMixin):
    """Controller for model and package management"""
    
    def __init__(self):
        self.model_service = ModelService()
        self.package_service = PackageService()
        self._progress_callbacks: dict = {}
        self.logger.info("ModelController initialized")
    
    # Model operations
    
    async def get_available_models(self) -> List[Dict]:
        """Get available speech models"""
        return await self.model_service.get_available_models()
    
    async def get_installed_models(self) -> List[Dict]:
        """Get installed speech models"""
        return await self.model_service.get_installed_models()
    
    async def download_model(self, model_id: str,
                           progress_callback: Optional[Callable] = None) -> bool:
        """
        Download a model
        
        Args:
            model_id: Model ID
            progress_callback: Progress callback
            
        Returns:
            True if started
        """
        if progress_callback:
            self._progress_callbacks[model_id] = progress_callback
        
        return await self.model_service.download_model(model_id, progress_callback)
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete a model"""
        return await self.model_service.delete_model(model_id)
    
    async def cancel_model_download(self, model_id: str) -> bool:
        """Cancel model download"""
        return await self.model_service.cancel_download(model_id)
    
    async def get_model_progress(self, model_id: str) -> Optional[Dict]:
        """Get model download progress"""
        return await self.model_service.get_download_progress(model_id)
    
    async def get_model_disk_usage(self) -> int:
        """Get total model disk usage"""
        return await self.model_service.get_disk_usage()
    
    # Package operations
    
    async def get_available_packages(self) -> List[Dict]:
        """Get available translation packages"""
        return await self.package_service.get_available_packages()
    
    async def get_installed_packages(self) -> List[Dict]:
        """Get installed translation packages"""
        return await self.package_service.get_installed_packages()
    
    async def download_package(self, package_id: str,
                              progress_callback: Optional[Callable] = None) -> bool:
        """
        Download a package
        
        Args:
            package_id: Package ID
            progress_callback: Progress callback
            
        Returns:
            True if started
        """
        if progress_callback:
            self._progress_callbacks[package_id] = progress_callback
        
        return await self.package_service.download_package(package_id, progress_callback)
    
    async def delete_package(self, package_id: str) -> bool:
        """Delete a package"""
        return await self.package_service.delete_package(package_id)
    
    async def cancel_package_download(self, package_id: str) -> bool:
        """Cancel package download"""
        return await self.package_service.cancel_download(package_id)
    
    async def get_package_progress(self, package_id: str) -> Optional[Dict]:
        """Get package download progress"""
        return await self.package_service.get_download_progress(package_id)
    
    async def get_package_disk_usage(self) -> int:
        """Get total package disk usage"""
        return await self.package_service.get_disk_usage()
    
    def remove_progress_callback(self, item_id: str):
        """Remove progress callback"""
        if item_id in self._progress_callbacks:
            del self._progress_callbacks[item_id]