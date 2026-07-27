"""
Model Repository Implementation
"""

from typing import Optional, List
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.domain.entities.model import Model, ModelStatus, ModelType, ModelProvider
from app.domain.interfaces.model_repository import ModelRepository
from app.services.models.model_service import ModelService
from app.database.dao.model_dao import ModelDAO


class ModelRepositoryImpl(ModelRepository, LoggerMixin):
    """Implementation of ModelRepository"""
    
    def __init__(self):
        self.model_service = ModelService()
        self.model_dao = ModelDAO()
        self.logger.info("ModelRepositoryImpl initialized")
    
    async def get_available_models(self, model_type: Optional[ModelType] = None) -> List[Model]:
        """Get available models"""
        try:
            models_data = await self.model_service.get_available_models(model_type)
            return [self._dict_to_entity(m) for m in models_data]
        except Exception as e:
            self.logger.error(f"Failed to get available models: {e}")
            return []
    
    async def get_installed_models(self) -> List[Model]:
        """Get installed models"""
        try:
            # Get from database
            db_models = self.model_dao.get_installed()
            return [self._db_to_entity(m) for m in db_models]
        except Exception as e:
            self.logger.error(f"Failed to get installed models: {e}")
            return []
    
    async def get_model(self, model_id: str) -> Optional[Model]:
        """Get model by ID"""
        try:
            # Check database
            db_model = self.model_dao.get_by_id(model_id)
            if db_model:
                return self._db_to_entity(db_model)
            
            # Check available models
            available = await self.get_available_models()
            for model in available:
                if model.id == model_id:
                    return model
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get model: {e}")
            return None
    
    async def download_model(self, model_id: str) -> bool:
        """Download model"""
        try:
            success = await self.model_service.download_model(model_id)
            
            if success:
                # Update database
                model = await self.get_model(model_id)
                if model:
                    model.status = ModelStatus.DOWNLOADING
                    await self._save_to_database(model)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to download model: {e}")
            return False
    
    async def pause_download(self, model_id: str) -> bool:
        """Pause model download"""
        try:
            return await self.model_service.cancel_download(model_id)
        except Exception as e:
            self.logger.error(f"Failed to pause download: {e}")
            return False
    
    async def resume_download(self, model_id: str) -> bool:
        """Resume model download"""
        return await self.download_model(model_id)
    
    async def cancel_download(self, model_id: str) -> bool:
        """Cancel model download"""
        return await self.model_service.cancel_download(model_id)
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete model"""
        try:
            success = await self.model_service.delete_model(model_id)
            
            if success:
                self.model_dao.delete(model_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete model: {e}")
            return False
    
    async def update_model(self, model_id: str) -> bool:
        """Update model"""
        # Delete old and download new
        await self.delete_model(model_id)
        return await self.download_model(model_id)
    
    async def verify_model(self, model_id: str) -> bool:
        """Verify model integrity"""
        try:
            is_installed = await self.model_service.is_model_installed(model_id)
            
            if is_installed:
                # Update status
                self.model_dao.update(model_id, {'status': 'installed'})
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify model: {e}")
            return False
    
    async def repair_model(self, model_id: str) -> bool:
        """Repair model"""
        # Delete and redownload
        return await self.update_model(model_id)
    
    async def get_model_disk_usage(self) -> int:
        """Get total model disk usage"""
        return await self.model_service.get_disk_usage()
    
    async def is_model_available(self, model_id: str) -> bool:
        """Check if model is available"""
        try:
            return await self.model_service.is_model_installed(model_id)
        except Exception:
            return False
    
    async def _save_to_database(self, model: Model):
        """Save model to database"""
        try:
            data = self._entity_to_db(model)
            
            existing = self.model_dao.get_by_id(model.id)
            if existing:
                self.model_dao.update(model.id, data)
            else:
                self.model_dao.insert(data)
                
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
    
    def _entity_to_db(self, model: Model) -> dict:
        """Convert Model entity to database dict"""
        return {
            'id': model.id,
            'name': model.name,
            'type': model.type.value,
            'language': model.language,
            'version': model.version,
            'file_path': model.file_path,
            'size_total': model.size_total,
            'size_downloaded': model.size_downloaded,
            'sha256': model.sha256,
            'status': model.status.value,
            'progress': model.progress,
            'is_active': 1 if model.is_active else 0,
            'created_at': model.created_at.isoformat(),
            'updated_at': model.updated_at.isoformat(),
        }
    
    def _db_to_entity(self, data: dict) -> Model:
        """Convert database dict to Model entity"""
        return Model(
            id=data.get('id', ''),
            name=data.get('name', ''),
            type=ModelType(data.get('type', 'speech_to_text')),
            provider=ModelProvider.CUSTOM,
            language=data.get('language'),
            version=data.get('version'),
            file_path=data.get('file_path'),
            size_total=data.get('size_total', 0),
            size_downloaded=data.get('size_downloaded', 0),
            sha256=data.get('sha256'),
            status=ModelStatus(data.get('status', 'not_installed')),
            progress=data.get('progress', 0.0),
            is_active=bool(data.get('is_active', 0)),
        )
    
    def _dict_to_entity(self, data: dict) -> Model:
        """Convert service dict to Model entity"""
        return Model(
            id=data.get('id', ''),
            name=data.get('name', ''),
            type=ModelType(data.get('type', 'speech_to_text')),
            provider=ModelProvider(data.get('provider', 'custom')),
            language=data.get('language'),
            size_total=data.get('size', 0),
            version=data.get('version'),
            status=ModelStatus.INSTALLED if data.get('installed') else ModelStatus.NOT_INSTALLED,
            description=data.get('description'),
            min_ram_mb=data.get('min_ram_mb', 512),
        )