"""
Settings DAO Module
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.database.database_manager import DatabaseManager


class SettingsDAO(LoggerMixin):
    """Data Access Object for settings"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def get(self, key: str) -> Optional[str]:
        """
        Get setting value
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None
        """
        try:
            query = "SELECT value FROM settings WHERE key = ?"
            row = self.db.fetch_one(query, (key,))
            return row['value'] if row else None
            
        except Exception as e:
            self.logger.error(f"Failed to get setting: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set setting value
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful
        """
        try:
            value_str = str(value)
            type_str = type(value).__name__
            
            query = """
            INSERT INTO settings (key, value, type, updated_at) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET 
                value = excluded.value,
                type = excluded.type,
                updated_at = excluded.updated_at
            """
            
            self.db.execute(query, (
                key,
                value_str,
                type_str,
                datetime.now().isoformat()
            ))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set setting: {e}")
            return False
    
    def get_all(self) -> Dict[str, str]:
        """
        Get all settings
        
        Returns:
            Dictionary of all settings
        """
        try:
            query = "SELECT key, value FROM settings"
            rows = self.db.fetch_all(query)
            
            return {row['key']: row['value'] for row in rows}
            
        except Exception as e:
            self.logger.error(f"Failed to get all settings: {e}")
            return {}
    
    def delete(self, key: str) -> bool:
        """
        Delete setting
        
        Args:
            key: Setting key
            
        Returns:
            True if successful
        """
        try:
            query = "DELETE FROM settings WHERE key = ?"
            self.db.execute(query, (key,))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete setting: {e}")
            return False
    
    def delete_all(self) -> bool:
        """
        Delete all settings
        
        Returns:
            True if successful
        """
        try:
            self.db.execute("DELETE FROM settings")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete all settings: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if setting exists
        
        Args:
            key: Setting key
            
        Returns:
            True if exists
        """
        try:
            query = "SELECT COUNT(*) as count FROM settings WHERE key = ?"
            row = self.db.fetch_one(query, (key,))
            return row['count'] > 0 if row else False
            
        except Exception as e:
            self.logger.error(f"Failed to check setting: {e}")
            return False