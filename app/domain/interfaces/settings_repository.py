"""
Settings Repository Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class SettingsRepository(ABC):
    """Interface for settings repository"""
    
    @abstractmethod
    async def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get setting value
        
        Args:
            key: Setting key
            default: Default value
            
        Returns:
            Setting value
        """
        pass
    
    @abstractmethod
    async def set_setting(self, key: str, value: Any) -> bool:
        """
        Set setting value
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all settings
        
        Returns:
            Dictionary of all settings
        """
        pass
    
    @abstractmethod
    async def delete_setting(self, key: str) -> bool:
        """
        Delete setting
        
        Args:
            key: Setting key
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def reset_settings(self) -> bool:
        """
        Reset all settings to defaults
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def export_settings(self, file_path: str) -> bool:
        """
        Export settings to file
        
        Args:
            file_path: Export file path
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def import_settings(self, file_path: str) -> bool:
        """
        Import settings from file
        
        Args:
            file_path: Import file path
            
        Returns:
            True if successful
        """
        pass