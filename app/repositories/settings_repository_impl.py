"""
Settings Repository Implementation
"""

from typing import Any, Dict, Optional
import json

from app.utils.logger import LoggerMixin
from app.domain.interfaces.settings_repository import SettingsRepository
from app.services.settings.settings_service import SettingsService
from app.database.dao.settings_dao import SettingsDAO
from app.config.app_config import AppConfig


class SettingsRepositoryImpl(SettingsRepository, LoggerMixin):
    """Implementation of SettingsRepository"""
    
    def __init__(self):
        self.settings_service = SettingsService()
        self.settings_dao = SettingsDAO()
        self.app_config = AppConfig()
        self.logger.info("SettingsRepositoryImpl initialized")
    
    async def get_setting(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        try:
            # Try config first
            value = self.app_config.get(key)
            
            if value is not None:
                return value
            
            # Try database
            db_value = self.settings_dao.get(key)
            
            if db_value is not None:
                # Try to parse as original type
                return self._parse_value(db_value)
            
            return default
            
        except Exception as e:
            self.logger.error(f"Failed to get setting: {e}")
            return default
    
    async def set_setting(self, key: str, value: Any) -> bool:
        """Set setting value"""
        try:
            # Save to config
            self.app_config.set(key, value)
            
            # Save to database
            self.settings_dao.set(key, value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set setting: {e}")
            return False
    
    async def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        try:
            # Get from config
            config_settings = self.app_config.get_all()
            
            # Get from database (for any missing)
            db_settings = self.settings_dao.get_all()
            
            # Merge (config takes priority)
            for key, value in db_settings.items():
                if key not in config_settings:
                    config_settings[key] = self._parse_value(value)
            
            return config_settings
            
        except Exception as e:
            self.logger.error(f"Failed to get all settings: {e}")
            return {}
    
    async def delete_setting(self, key: str) -> bool:
        """Delete setting"""
        try:
            self.settings_dao.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete setting: {e}")
            return False
    
    async def reset_settings(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self.app_config.reset()
            self.settings_dao.delete_all()
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset settings: {e}")
            return False
    
    async def export_settings(self, file_path: str) -> bool:
        """Export settings to file"""
        try:
            settings = await self.get_all_settings()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Settings exported to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False
    
    async def import_settings(self, file_path: str) -> bool:
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            for key, value in settings.items():
                await self.set_setting(key, value)
            
            self.logger.info(f"Settings imported from: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False
    
    def _parse_value(self, value: str) -> Any:
        """Parse value to appropriate type"""
        if value is None:
            return None
        
        # Try boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value