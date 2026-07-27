"""
Package DAO Module
"""

from typing import Optional, List, Dict
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.database.database_manager import DatabaseManager


class PackageDAO(LoggerMixin):
    """Data Access Object for packages"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def insert(self, package_data: Dict) -> bool:
        """Insert a package"""
        try:
            query = """
            INSERT INTO packages (
                id, name, type, source_lang, target_lang, version,
                file_path, size_total, size_downloaded, sha256,
                status, progress, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute(query, (
                package_data.get('id'),
                package_data.get('name'),
                package_data.get('type'),
                package_data.get('source_lang'),
                package_data.get('target_lang'),
                package_data.get('version'),
                package_data.get('file_path'),
                package_data.get('size_total', 0),
                package_data.get('size_downloaded', 0),
                package_data.get('sha256'),
                package_data.get('status', 'not_installed'),
                package_data.get('progress', 0.0),
                package_data.get('is_active', 0),
                package_data.get('created_at', datetime.now().isoformat()),
                package_data.get('updated_at', datetime.now().isoformat()),
            ))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to insert package: {e}")
            return False
    
    def get_all(self) -> List[Dict]:
        """Get all packages"""
        try:
            rows = self.db.fetch_all("SELECT * FROM packages ORDER BY name")
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get packages: {e}")
            return []
    
    def get_by_id(self, package_id: str) -> Optional[Dict]:
        """Get package by ID"""
        try:
            row = self.db.fetch_one("SELECT * FROM packages WHERE id = ?", (package_id,))
            return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get package: {e}")
            return None
    
    def update(self, package_id: str, data: Dict) -> bool:
        """Update package"""
        try:
            set_clauses = []
            values = []
            
            for key, value in data.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(datetime.now().isoformat())
            values.append(package_id)
            
            query = f"UPDATE packages SET {', '.join(set_clauses)}, updated_at = ? WHERE id = ?"
            self.db.execute(query, tuple(values))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update package: {e}")
            return False
    
    def delete(self, package_id: str) -> bool:
        """Delete package"""
        try:
            self.db.execute("DELETE FROM packages WHERE id = ?", (package_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete package: {e}")
            return False
    
    def get_installed(self) -> List[Dict]:
        """Get installed packages"""
        try:
            rows = self.db.fetch_all(
                "SELECT * FROM packages WHERE status = 'installed'"
            )
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get installed packages: {e}")
            return []
    
    def get_by_language_pair(self, source_lang: str, target_lang: str) -> Optional[Dict]:
        """Get package by language pair"""
        try:
            row = self.db.fetch_one(
                "SELECT * FROM packages WHERE source_lang = ? AND target_lang = ?",
                (source_lang, target_lang)
            )
            return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get package by language: {e}")
            return None