"""
Settings Service Module
"""

import json
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.config.app_config import AppConfig
from app.config.constants import (
    APP_VERSION,
    SUPPORTED_VIDEO_QUALITIES,
    SUBTITLE_FORMATS,
    MAX_PARALLEL_DOWNLOADS
)


class SettingsService(LoggerMixin):
    """Service for managing application settings"""
    
    def __init__(self):
        self.config = AppConfig()
        self.logger.info("SettingsService initialized")
    
    async def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all settings
        
        Returns:
            Dictionary of all settings
        """
        return {
            'language': await self.get_language(),
            'theme': await self.get_theme(),
            'video_quality': await self.get_video_quality(),
            'subtitle_format': await self.get_subtitle_format(),
            'download_folder': await self.get_download_folder(),
            'max_parallel_downloads': await self.get_max_parallel_downloads(),
            'auto_resume': await self.get_auto_resume(),
            'auto_clean_cache': await self.get_auto_clean_cache(),
            'auto_check_updates': await self.get_auto_check_updates(),
            'speech_engine': await self.get_speech_engine(),
            'translation_engine': await self.get_translation_engine(),
            'notification_enabled': await self.get_notification_enabled(),
            'app_version': APP_VERSION,
        }
    
    async def get_language(self) -> str:
        """Get interface language"""
        return self.config.get('language', 'ar')
    
    async def set_language(self, language: str) -> bool:
        """Set interface language"""
        if language in ['ar', 'en']:
            return self.config.set('language', language)
        return False
    
    async def get_theme(self) -> str:
        """Get theme setting"""
        return self.config.get('theme', 'dark')
    
    async def set_theme(self, theme: str) -> bool:
        """Set theme"""
        if theme in ['dark', 'light', 'system']:
            return self.config.set('theme', theme)
        return False
    
    async def get_video_quality(self) -> str:
        """Get preferred video quality"""
        return self.config.get('video_quality', '720p')
    
    async def set_video_quality(self, quality: str) -> bool:
        """Set preferred video quality"""
        if quality in SUPPORTED_VIDEO_QUALITIES:
            return self.config.set('video_quality', quality)
        return False
    
    async def get_subtitle_format(self) -> str:
        """Get preferred subtitle format"""
        return self.config.get('subtitle_format', 'srt')
    
    async def set_subtitle_format(self, fmt: str) -> bool:
        """Set preferred subtitle format"""
        if fmt in SUBTITLE_FORMATS:
            return self.config.set('subtitle_format', fmt)
        return False
    
    async def get_download_folder(self) -> str:
        """Get download folder path"""
        return self.config.get('download_folder', 'Downloads')
    
    async def set_download_folder(self, folder: str) -> bool:
        """Set download folder path"""
        return self.config.set('download_folder', folder)
    
    async def get_max_parallel_downloads(self) -> int:
        """Get maximum parallel downloads"""
        return self.config.get('max_parallel_downloads', 3)
    
    async def set_max_parallel_downloads(self, count: int) -> bool:
        """Set maximum parallel downloads"""
        if 1 <= count <= 10:
            return self.config.set('max_parallel_downloads', count)
        return False
    
    async def get_auto_resume(self) -> bool:
        """Get auto-resume setting"""
        return self.config.get('auto_resume', True)
    
    async def set_auto_resume(self, enabled: bool) -> bool:
        """Set auto-resume"""
        return self.config.set('auto_resume', enabled)
    
    async def get_auto_clean_cache(self) -> bool:
        """Get auto-clean cache setting"""
        return self.config.get('auto_clean_cache', False)
    
    async def set_auto_clean_cache(self, enabled: bool) -> bool:
        """Set auto-clean cache"""
        return self.config.set('auto_clean_cache', enabled)
    
    async def get_auto_check_updates(self) -> bool:
        """Get auto-check updates setting"""
        return self.config.get('auto_check_updates', True)
    
    async def set_auto_check_updates(self, enabled: bool) -> bool:
        """Set auto-check updates"""
        return self.config.set('auto_check_updates', enabled)
    
    async def get_speech_engine(self) -> str:
        """Get speech recognition engine"""
        return self.config.get('speech_engine', 'whisper')
    
    async def set_speech_engine(self, engine: str) -> bool:
        """Set speech recognition engine"""
        return self.config.set('speech_engine', engine)
    
    async def get_translation_engine(self) -> str:
        """Get translation engine"""
        return self.config.get('translation_engine', 'argos')
    
    async def set_translation_engine(self, engine: str) -> bool:
        """Set translation engine"""
        return self.config.set('translation_engine', engine)
    
    async def get_notification_enabled(self) -> bool:
        """Get notification setting"""
        return self.config.get('notification_enabled', True)
    
    async def set_notification_enabled(self, enabled: bool) -> bool:
        """Set notification"""
        return self.config.set('notification_enabled', enabled)
    
    async def export_settings(self) -> Optional[str]:
        """Export settings to JSON string"""
        try:
            settings = await self.get_all_settings()
            return json.dumps(settings, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return None
    
    async def import_settings(self, settings_json: str) -> bool:
        """Import settings from JSON string"""
        try:
            settings = json.loads(settings_json)
            
            for key, value in settings.items():
                if hasattr(self, f'set_{key}'):
                    setter = getattr(self, f'set_{key}')
                    await setter(value)
            
            self.logger.info("Settings imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False
    
    async def reset_settings(self) -> bool:
        """Reset all settings to defaults"""
        return self.config.reset()
    
    async def get_setting(self, key: str, default: Any = None) -> Any:
        """Get specific setting"""
        return self.config.get(key, default)
    
    async def set_setting(self, key: str, value: Any) -> bool:
        """Set specific setting"""
        return self.config.set(key, value)