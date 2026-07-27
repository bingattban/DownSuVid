"""
Manage Models Use Case
"""

from typing import List, Optional, Dict
from app.utils.logger import LoggerMixin
from app.domain.entities.model import Model, ModelStatus, ModelType
from app.domain.interfaces.model_repository import ModelRepository


class ManageModelsUseCase(LoggerMixin):
    """Use case for managing AI models"""
    
    def __init__(self, model_repository: ModelRepository):
        self.model_repository = model_repository
        self.logger.info("ManageModelsUseCase initialized")
    
    async def get_available_models(self, model_type: Optional[ModelType] = None) -> List[Model]:
        """
        Get available models
        
        Args:
            model_type: Filter by type
            
        Returns:
            List of models
        """
        return await self.model_repository.get_available_models(model_type)
    
    async def get_installed_models(self) -> List[Model]:
        """Get installed models"""
        return await self.model_repository.get_installed_models()
    
    async def download_model(self, model_id: str) -> bool:
        """
        Download a model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if download started
        """
        # Check if model exists
        model = await self.model_repository.get_model(model_id)
        
        if not model:
            self.logger.error(f"Model not found: {model_id}")
            return False
        
        # Check disk space
        disk_usage = await self.model_repository.get_model_disk_usage()
        # Implementation would check available space
        
        # Start download
        success = await self.model_repository.download_model(model_id)
        
        if success:
            self.logger.info(f"Model download started: {model_id}")
        else:
            self.logger.error(f"Failed to start model download: {model_id}")
        
        return success
    
    async def delete_model(self, model_id: str) -> bool:
        """
        Delete a model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if deleted
        """
        model = await self.model_repository.get_model(model_id)
        
        if not model:
            self.logger.error(f"Model not found: {model_id}")
            return False
        
        if model.is_downloading():
            self.logger.warning(f"Cannot delete downloading model: {model_id}")
            return False
        
        success = await self.model_repository.delete_model(model_id)
        
        if success:
            self.logger.info(f"Model deleted: {model_id}")
        
        return success
    
    async def update_model(self, model_id: str) -> bool:
        """
        Update a model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if update started
        """
        model = await self.model_repository.get_model(model_id)
        
        if not model:
            self.logger.error(f"Model not found: {model_id}")
            return False
        
        if not model.can_update():
            self.logger.warning(f"Model cannot be updated: {model_id}")
            return False
        
        return await self.model_repository.update_model(model_id)
    
    async def verify_model(self, model_id: str) -> bool:
        """
        Verify model integrity
        
        Args:
            model_id: Model ID
            
        Returns:
            True if model is valid
        """
        return await self.model_repository.verify_model(model_id)
    
    async def repair_model(self, model_id: str) -> bool:
        """
        Repair a model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if repair started
        """
        model = await self.model_repository.get_model(model_id)
        
        if not model:
            self.logger.error(f"Model not found: {model_id}")
            return False
        
        if not model.needs_repair():
            self.logger.info(f"Model doesn't need repair: {model_id}")
            return True
        
        return await self.model_repository.repair_model(model_id)
    
    async def get_disk_usage(self) -> int:
        """Get total model disk usage"""
        return await self.model_repository.get_model_disk_usage()
    
    async def is_model_available(self, model_id: str) -> bool:
        """
        Check if model is available for use
        
        Args:
            model_id: Model ID
            
        Returns:
            True if model is installed and ready
        """
        return await self.model_repository.is_model_available(model_id)
    
    async def get_model_stats(self) -> Dict:
        """
        Get model statistics
        
        Returns:
            Statistics dictionary
        """
        installed = await self.get_installed_models()
        available = await self.get_available_models()
        
        return {
            'total_installed': len(installed),
            'total_available': len(available),
            'disk_usage': await self.get_disk_usage(),
            'installed_models': [
                {
                    'id': m.id,
                    'name': m.name,
                    'version': m.version,
                    'size': m.size_total,
                }
                for m in installed
            ],
        }