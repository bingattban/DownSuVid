"""
Download DAO Module
"""

from typing import Optional, List, Dict
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.database.database_manager import DatabaseManager


class DownloadDAO(LoggerMixin):
    """Data Access Object for downloads"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def insert(self, download_data: Dict) -> bool:
        """
        Insert a new download
        
        Args:
            download_data: Download data dictionary
            
        Returns:
            True if successful
        """
        try:
            query = """
            INSERT INTO downloads (
                id, url, title, thumbnail_url, file_path, subtitle_path,
                status, progress, speed, size_total, size_downloaded,
                format_id, quality, website, uploader, duration,
                error_message, retry_count, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute(query, (
                download_data.get('id'),
                download_data.get('url'),
                download_data.get('title'),
                download_data.get('thumbnail_url'),
                download_data.get('file_path'),
                download_data.get('subtitle_path'),
                download_data.get('status', 'pending'),
                download_data.get('progress', 0.0),
                download_data.get('speed'),
                download_data.get('size_total', 0),
                download_data.get('size_downloaded', 0),
                download_data.get('format_id'),
                download_data.get('quality'),
                download_data.get('website'),
                download_data.get('uploader'),
                download_data.get('duration'),
                download_data.get('error_message'),
                download_data.get('retry_count', 0),
                download_data.get('created_at', datetime.now().isoformat()),
                download_data.get('updated_at', datetime.now().isoformat()),
            ))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to insert download: {e}")
            return False
    
    def get_by_id(self, download_id: str) -> Optional[Dict]:
        """
        Get download by ID
        
        Args:
            download_id: Download ID
            
        Returns:
            Download data or None
        """
        try:
            query = "SELECT * FROM downloads WHERE id = ?"
            row = self.db.fetch_one(query, (download_id,))
            return dict(row) if row else None
            
        except Exception as e:
            self.logger.error(f"Failed to get download: {e}")
            return None
    
    def get_all(self) -> List[Dict]:
        """
        Get all downloads
        
        Returns:
            List of download data
        """
        try:
            query = "SELECT * FROM downloads ORDER BY created_at DESC"
            rows = self.db.fetch_all(query)
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get downloads: {e}")
            return []
    
    def get_by_status(self, status: str) -> List[Dict]:
        """
        Get downloads by status
        
        Args:
            status: Download status
            
        Returns:
            List of downloads
        """
        try:
            query = "SELECT * FROM downloads WHERE status = ? ORDER BY created_at DESC"
            rows = self.db.fetch_all(query, (status,))
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get downloads by status: {e}")
            return []
    
    def get_active_downloads(self) -> List[Dict]:
        """
        Get active downloads
        
        Returns:
            List of active downloads
        """
        try:
            query = """
            SELECT * FROM downloads 
            WHERE status IN ('pending', 'downloading', 'processing')
            ORDER BY created_at ASC
            """
            rows = self.db.fetch_all(query)
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get active downloads: {e}")
            return []
    
    def update(self, download_id: str, update_data: Dict) -> bool:
        """
        Update download
        
        Args:
            download_id: Download ID
            update_data: Data to update
            
        Returns:
            True if successful
        """
        try:
            # Build SET clause
            set_clauses = []
            values = []
            
            allowed_fields = [
                'title', 'thumbnail_url', 'file_path', 'subtitle_path',
                'status', 'progress', 'speed', 'size_total', 'size_downloaded',
                'format_id', 'quality', 'error_message', 'retry_count',
                'updated_at', 'completed_at'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    set_clauses.append(f"{field} = ?")
                    values.append(update_data[field])
            
            if not set_clauses:
                return False
            
            # Always update timestamp
            set_clauses.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            
            values.append(download_id)
            
            query = f"UPDATE downloads SET {', '.join(set_clauses)} WHERE id = ?"
            
            self.db.execute(query, tuple(values))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update download: {e}")
            return False
    
    def delete(self, download_id: str) -> bool:
        """
        Delete download
        
        Args:
            download_id: Download ID
            
        Returns:
            True if successful
        """
        try:
            query = "DELETE FROM downloads WHERE id = ?"
            self.db.execute(query, (download_id,))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete download: {e}")
            return False
    
    def delete_completed(self) -> int:
        """
        Delete completed downloads
        
        Returns:
            Number of deleted records
        """
        try:
            query = """
            DELETE FROM downloads 
            WHERE status IN ('completed', 'cancelled', 'failed')
            """
            self.db.execute(query)
            
            # Get count from changes
            cursor = self.db._connection.cursor()
            count = cursor.rowcount
            cursor.close()
            
            return count if count else 0
            
        except Exception as e:
            self.logger.error(f"Failed to delete completed downloads: {e}")
            return 0
    
    def get_count_by_status(self) -> Dict[str, int]:
        """
        Get download count by status
        
        Returns:
            Dictionary of status counts
        """
        try:
            query = """
            SELECT status, COUNT(*) as count 
            FROM downloads 
            GROUP BY status
            """
            rows = self.db.fetch_all(query)
            
            return {row['status']: row['count'] for row in rows}
            
        except Exception as e:
            self.logger.error(f"Failed to get download counts: {e}")
            return {}
    
    def get_total_downloaded_size(self) -> int:
        """
        Get total downloaded size
        
        Returns:
            Total size in bytes
        """
        try:
            query = """
            SELECT SUM(size_total) as total 
            FROM downloads 
            WHERE status = 'completed'
            """
            row = self.db.fetch_one(query)
            return row['total'] if row and row['total'] else 0
            
        except Exception as e:
            self.logger.error(f"Failed to get total size: {e}")
            return 0
    
    def search(self, query_text: str) -> List[Dict]:
        """
        Search downloads
        
        Args:
            query_text: Search query
            
        Returns:
            List of matching downloads
        """
        try:
            query = """
            SELECT * FROM downloads 
            WHERE title LIKE ? OR url LIKE ? OR website LIKE ?
            ORDER BY created_at DESC
            LIMIT 50
            """
            
            search_param = f"%{query_text}%"
            rows = self.db.fetch_all(query, (search_param, search_param, search_param))
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to search downloads: {e}")
            return []