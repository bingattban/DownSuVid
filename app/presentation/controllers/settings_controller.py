"""
Settings Controller Module
"""

from typing import Any, Dict
from app.utils.logger import LoggerMixin
from app.services.settings.settings_service import SettingsService
from app.services.storage.storage_service import StorageService


class SettingsController(LoggerMixin):
    """Controller for settings operations"""
    
    def __init__(self):
        self.settings_service = SettingsService()
        self.storage_service = StorageService()
        self.logger.info("SettingsController initialized")
    
    async def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return await self.settings_service.get_all_settings()
    
    async def get_theme(self) -> str:
        """Get theme setting"""
        return await self.settings_service.get_theme()
    
    async def set_theme(self, theme: str) -> bool:
        """Set theme"""
        return await self.settings_service.set_theme(theme)
    
    async def get_language(self) -> str:
        """Get language setting"""
        return await self.settings_service.get_language()
    
    async def set_language(self, language: str) -> bool:
        """Set language"""
        return await self.settings_service.set_language(language)
    
    async def get_video_quality(self) -> str:
        """Get video quality setting"""
        return await self.settings_service.get_video_quality()
    
    async def set_video_quality(self, quality: str) -> bool:
        """Set video quality"""
        return await self.settings_service.set_video_quality(quality)
    
    async def get_max_parallel_downloads(self) -> int:
        """Get max parallel downloads"""
        return await self.settings_service.get_max_parallel_downloads()
    
    async def set_max_parallel_downloads(self, count: int) -> bool:
        """Set max parallel downloads"""
        return await self.settings_service.set_max_parallel_downloads(count)
    
    async def get_auto_resume(self) -> bool:
        """Get auto resume setting"""
        return await self.settings_service.get_auto_resume()
    
    async def set_auto_resume(self, enabled: bool) -> bool:
        """Set auto resume"""
        return await self.settings_service.set_auto_resume(enabled)
    
    async def get_auto_clean_cache(self) -> bool:
        """Get auto clean cache setting"""
        return await self.settings_service.get_auto_clean_cache()
    
    async def set_auto_clean_cache(self, enabled: bool) -> bool:
        """Set auto clean cache"""
        return await self.settings_service.set_auto_clean_cache(enabled)
    
    async def get_auto_check_updates(self) -> bool:
        """Get auto check updates setting"""
        return await self.settings_service.get_auto_check_updates()
    
    async def set_auto_check_updates(self, enabled: bool) -> bool:
        """Set auto check updates"""
        return await self.settings_service.set_auto_check_updates(enabled)
    
    async def get_notification_enabled(self) -> bool:
        """Get notification setting"""
        return await self.settings_service.get_notification_enabled()
    
    async def set_notification_enabled(self, enabled: bool) -> bool:
        """Set notification"""
        return await self.settings_service.set_notification_enabled(enabled)
    
    async def get_speech_engine(self) -> str:
        """Get speech engine setting"""
        return await self.settings_service.get_speech_engine()
    
    async def set_speech_engine(self, engine: str) -> bool:
        """Set speech engine"""
        return await self.settings_service.set_speech_engine(engine)
    
    async def get_translation_engine(self) -> str:
        """Get translation engine setting"""
        return await self.settings_service.get_translation_engine()
    
    async def set_translation_engine(self, engine: str) -> bool:
        """Set translation engine"""
        return await self.settings_service.set_translation_engine(engine)
    
    async def reset_settings(self) -> bool:
        """Reset all settings"""
        return await self.settings_service.reset_settings()
    
    async def export_settings(self) -> str:
        """Export settings"""
        return await self.settings_service.export_settings()
    
    async def import_settings(self, settings_json: str) -> bool:
        """Import settings"""
        return await self.settings_service.import_settings(settings_json)
    
    # Storage operations
    
    async def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        return await self.storage_service.get_storage_stats()
    
    async def clean_temp_files(self) -> Dict:
        """Clean temporary files"""
        return await self.storage_service.clean_all_temp()
    
    async def get_disk_usage(self) -> Dict:
        """Get disk usage"""
        return await self.storage_service.get_disk_usage()