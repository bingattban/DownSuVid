"""
History DAO Module
"""

from typing import Optional, List, Dict
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.database.database_manager import DatabaseManager


class HistoryDAO(LoggerMixin):
    """Data Access Object for download history"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def insert(self, history_data: Dict) -> bool:
        """
        Insert history entry
        
        Args:
            history_data: History data
            
        Returns:
            True if successful
        """
        try:
            query = """
            INSERT INTO history (url, title, action, status, file_path, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute(query, (
                history_data.get('url'),
                history_data.get('title'),
                history_data.get('action', 'download'),
                history_data.get('status', 'completed'),
                history_data.get('file_path'),
                history_data.get('file_size', 0),
                history_data.get('created_at', datetime.now().isoformat()),
            ))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to insert history: {e}")
            return False
    
    def get_all(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Get history entries
        
        Args:
            limit: Maximum entries
            offset: Pagination offset
            
        Returns:
            List of history entries
        """
        try:
            query = """
            SELECT * FROM history 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
            """
            rows = self.db.fetch_all(query, (limit, offset))
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get history: {e}")
            return []
    
    def get_by_url(self, url: str) -> Optional[Dict]:
        """
        Get history entry by URL
        
        Args:
            url: Video URL
            
        Returns:
            History entry or None
        """
        try:
            query = """
            SELECT * FROM history 
            WHERE url = ? 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            row = self.db.fetch_one(query, (url,))
            return dict(row) if row else None
            
        except Exception as e:
            self.logger.error(f"Failed to get history by URL: {e}")
            return None
    
    def search(self, query_text: str) -> List[Dict]:
        """
        Search history
        
        Args:
            query_text: Search query
            
        Returns:
            List of matching entries
        """
        try:
            query = """
            SELECT * FROM history 
            WHERE title LIKE ? OR url LIKE ?
            ORDER BY created_at DESC
            LIMIT 50
            """
            
            search_param = f"%{query_text}%"
            rows = self.db.fetch_all(query, (search_param, search_param))
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to search history: {e}")
            return []
    
    def delete(self, entry_id: int) -> bool:
        """
        Delete history entry
        
        Args:
            entry_id: Entry ID
            
        Returns:
            True if successful
        """
        try:
            self.db.execute("DELETE FROM history WHERE id = ?", (entry_id,))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete history: {e}")
            return False
    
    def delete_all(self) -> bool:
        """
        Delete all history
        
        Returns:
            True if successful
        """
        try:
            self.db.execute("DELETE FROM history")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete all history: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get history statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            stats = {}
            
            # Total entries
            row = self.db.fetch_one("SELECT COUNT(*) as count FROM history")
            stats['total_entries'] = row['count'] if row else 0
            
            # Successful downloads
            row = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM history WHERE action = 'download' AND status = 'completed'"
            )
            stats['successful_downloads'] = row['count'] if row else 0
            
            # Failed downloads
            row = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM history WHERE action = 'download' AND status = 'failed'"
            )
            stats['failed_downloads'] = row['count'] if row else 0
            
            # Today's entries
            row = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM history WHERE date(created_at) = date('now')"
            )
            stats['today_entries'] = row['count'] if row else 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get history stats: {e}")
            return {}
    
    def get_recent_urls(self, limit: int = 10) -> List[str]:
        """
        Get recently downloaded URLs
        
        Args:
            limit: Maximum URLs
            
        Returns:
            List of URLs
        """
        try:
            query = """
            SELECT DISTINCT url FROM history
            WHERE action = 'download'
            ORDER BY created_at DESC
            LIMIT ?
            """
            
            rows = self.db.fetch_all(query, (limit,))
            return [row['url'] for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent URLs: {e}")
            return []