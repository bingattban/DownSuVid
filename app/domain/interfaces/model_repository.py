"""
Model Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.model import Model, ModelStatus, ModelType, ModelProvider


class ModelRepository(ABC):
    """Interface for model repository"""
    
    @abstractmethod
    async def get_available_models(self, model_type: Optional[ModelType] = None) -> List[Model]:
        """
        Get available models
        
        Args:
            model_type: Filter by model type
            
        Returns:
            List of models
        """
        pass
    
    @abstractmethod
    async def get_installed_models(self) -> List[Model]:
        """
        Get installed models
        
        Returns:
            List of installed models
        """
        pass
    
    @abstractmethod
    async def get_model(self, model_id: str) -> Optional[Model]:
        """
        Get model by ID
        
        Args:
            model_id: Model ID
            
        Returns:
            Model entity or None
        """
        pass
    
    @abstractmethod
    async def download_model(self, model_id: str) -> bool:
        """
        Download model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if download started
        """
        pass
    
    @abstractmethod
    async def pause_download(self, model_id: str) -> bool:
        """
        Pause model download
        
        Args:
            model_id: Model ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def resume_download(self, model_id: str) -> bool:
        """
        Resume model download
        
        Args:
            model_id: Model ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def cancel_download(self, model_id: str) -> bool:
        """
        Cancel model download
        
        Args:
            model_id: Model ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete_model(self, model_id: str) -> bool:
        """
        Delete model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def update_model(self, model_id: str) -> bool:
        """
        Update model to latest version
        
        Args:
            model_id: Model ID
            
        Returns:
            True if update started
        """
        pass
    
    @abstractmethod
    async def verify_model(self, model_id: str) -> bool:
        """
        Verify model integrity
        
        Args:
            model_id: Model ID
            
        Returns:
            True if model is valid
        """
        pass
    
    @abstractmethod
    async def repair_model(self, model_id: str) -> bool:
        """
        Repair model
        
        Args:
            model_id: Model ID
            
        Returns:
            True if repair started
        """
        pass
    
    @abstractmethod
    async def get_model_disk_usage(self) -> int:
        """
        Get total disk usage by models
        
        Returns:
            Size in bytes
        """
        pass
    
    @abstractmethod
    async def is_model_available(self, model_id: str) -> bool:
        """
        Check if model is available and installed
        
        Args:
            model_id: Model ID
            
        Returns:
            True if model is ready
        """
        pass