"""
History Service Module
"""

import asyncio
from typing import Optional, List, Dict
from datetime import datetime
import uuid

from app.utils.logger import LoggerMixin
from app.database.database_manager import DatabaseManager


class HistoryService(LoggerMixin):
    """Service for managing download history"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.logger.info("HistoryService initialized")
    
    async def add_entry(self, url: str, title: Optional[str] = None,
                       action: str = "download", status: str = "completed",
                       file_path: Optional[str] = None,
                       file_size: Optional[int] = None) -> bool:
        """
        Add history entry
        
        Args:
            url: Video URL
            title: Video title
            action: Action type
            status: Action status
            file_path: Downloaded file path
            file_size: File size in bytes
            
        Returns:
            True if successful
        """
        try:
            query = """
            INSERT INTO history (url, title, action, status, file_path, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute(query, (
                url,
                title or "Unknown",
                action,
                status,
                file_path,
                file_size or 0,
                datetime.now().isoformat()
            ))
            
            self.logger.debug(f"History entry added: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add history entry: {e}")
            return False
    
    async def get_entries(self, limit: int = 50, 
                         offset: int = 0) -> List[Dict]:
        """
        Get history entries
        
        Args:
            limit: Maximum entries
            offset: Offset for pagination
            
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
    
    async def search_entries(self, query_text: str) -> List[Dict]:
        """
        Search history entries
        
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
    
    async def get_entry_by_url(self, url: str) -> Optional[Dict]:
        """
        Get history entry by URL
        
        Args:
            url: Video URL
            
        Returns:
            History entry or None
        """
        try:
            query = "SELECT * FROM history WHERE url = ? ORDER BY created_at DESC LIMIT 1"
            row = self.db.fetch_one(query, (url,))
            return dict(row) if row else None
            
        except Exception as e:
            self.logger.error(f"Failed to get entry: {e}")
            return None
    
    async def delete_entry(self, entry_id: int) -> bool:
        """
        Delete history entry
        
        Args:
            entry_id: Entry ID
            
        Returns:
            True if successful
        """
        try:
            self.db.execute("DELETE FROM history WHERE id = ?", (entry_id,))
            self.logger.debug(f"History entry deleted: {entry_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete entry: {e}")
            return False
    
    async def clear_history(self) -> bool:
        """
        Clear all history
        
        Returns:
            True if successful
        """
        try:
            self.db.execute("DELETE FROM history")
            self.logger.info("History cleared")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear history: {e}")
            return False
    
    async def get_stats(self) -> Dict:
        """
        Get history statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            stats = {}
            
            # Total downloads
            row = self.db.fetch_one("SELECT COUNT(*) as count FROM history WHERE action = 'download'")
            stats['total_downloads'] = row['count'] if row else 0
            
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
            
            # Total downloaded size
            row = self.db.fetch_one(
                "SELECT SUM(file_size) as total FROM history WHERE action = 'download' AND status = 'completed'"
            )
            stats['total_size'] = row['total'] if row and row['total'] else 0
            
            # Downloads today
            row = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM history WHERE date(created_at) = date('now')"
            )
            stats['today_downloads'] = row['count'] if row else 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {
                'total_downloads': 0,
                'successful_downloads': 0,
                'failed_downloads': 0,
                'total_size': 0,
                'today_downloads': 0,
            }
    
    async def get_recent_urls(self, limit: int = 10) -> List[str]:
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