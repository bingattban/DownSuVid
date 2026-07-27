"""
Model DAO Module
"""

from typing import Optional, List, Dict
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.database.database_manager import DatabaseManager


class ModelDAO(LoggerMixin):
    """Data Access Object for models"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def insert(self, model_data: Dict) -> bool:
        """Insert a model"""
        try:
            query = """
            INSERT INTO models (
                id, name, type, language, version, file_path,
                size_total, size_downloaded, sha256, status, progress,
                is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute(query, (
                model_data.get('id'),
                model_data.get('name'),
                model_data.get('type'),
                model_data.get('language'),
                model_data.get('version'),
                model_data.get('file_path'),
                model_data.get('size_total', 0),
                model_data.get('size_downloaded', 0),
                model_data.get('sha256'),
                model_data.get('status', 'not_installed'),
                model_data.get('progress', 0.0),
                model_data.get('is_active', 0),
                model_data.get('created_at', datetime.now().isoformat()),
                model_data.get('updated_at', datetime.now().isoformat()),
            ))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to insert model: {e}")
            return False
    
    def get_all(self) -> List[Dict]:
        """Get all models"""
        try:
            rows = self.db.fetch_all("SELECT * FROM models ORDER BY name")
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get models: {e}")
            return []
    
    def get_by_id(self, model_id: str) -> Optional[Dict]:
        """Get model by ID"""
        try:
            row = self.db.fetch_one("SELECT * FROM models WHERE id = ?", (model_id,))
            return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"Failed to get model: {e}")
            return None
    
    def update(self, model_id: str, data: Dict) -> bool:
        """Update model"""
        try:
            set_clauses = []
            values = []
            
            for key, value in data.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(datetime.now().isoformat())
            values.append(model_id)
            
            query = f"UPDATE models SET {', '.join(set_clauses)}, updated_at = ? WHERE id = ?"
            self.db.execute(query, tuple(values))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update model: {e}")
            return False
    
    def delete(self, model_id: str) -> bool:
        """Delete model"""
        try:
            self.db.execute("DELETE FROM models WHERE id = ?", (model_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete model: {e}")
            return False
    
    def get_installed(self) -> List[Dict]:
        """Get installed models"""
        try:
            rows = self.db.fetch_all(
                "SELECT * FROM models WHERE status = 'installed'"
            )
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get installed models: {e}")
            return []