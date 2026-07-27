"""
Download Repository Implementation
"""

from typing import Optional, List
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.domain.entities.download import Download, DownloadStatus, VideoInfo, DownloadProgress
from app.domain.interfaces.download_repository import DownloadRepository
from app.services.download.download_service import DownloadService
from app.database.dao.download_dao import DownloadDAO


class DownloadRepositoryImpl(DownloadRepository, LoggerMixin):
    """Implementation of DownloadRepository"""
    
    def __init__(self):
        self.download_service = DownloadService()
        self.download_dao = DownloadDAO()
        self.logger.info("DownloadRepositoryImpl initialized")
    
    async def create_download(self, url: str) -> Optional[Download]:
        """Create a new download"""
        try:
            download = await self.download_service.create_download(url)
            
            if download:
                # Save to database
                self._save_to_database(download)
            
            return download
            
        except Exception as e:
            self.logger.error(f"Failed to create download: {e}")
            return None
    
    async def get_download(self, download_id: str) -> Optional[Download]:
        """Get download by ID"""
        try:
            # Try memory first
            download = await self.download_service.get_download(download_id)
            
            if download:
                return download
            
            # Try database
            db_data = self.download_dao.get_by_id(download_id)
            if db_data:
                return self._db_to_entity(db_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get download: {e}")
            return None
    
    async def get_all_downloads(self) -> List[Download]:
        """Get all downloads"""
        try:
            # Get from service (in-memory)
            downloads = await self.download_service.get_downloads()
            
            if downloads:
                return downloads
            
            # Get from database
            db_downloads = self.download_dao.get_all()
            return [self._db_to_entity(d) for d in db_downloads]
            
        except Exception as e:
            self.logger.error(f"Failed to get all downloads: {e}")
            return []
    
    async def get_downloads_by_status(self, status: DownloadStatus) -> List[Download]:
        """Get downloads by status"""
        try:
            all_downloads = await self.get_all_downloads()
            return [d for d in all_downloads if d.status == status]
            
        except Exception as e:
            self.logger.error(f"Failed to get downloads by status: {e}")
            return []
    
    async def update_download(self, download: Download) -> bool:
        """Update download"""
        try:
            # Update in database
            self.download_dao.update(download.id, self._entity_to_db(download))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update download: {e}")
            return False
    
    async def delete_download(self, download_id: str) -> bool:
        """Delete download"""
        try:
            # Delete from service
            await self.download_service.delete_download(download_id)
            
            # Delete from database
            self.download_dao.delete(download_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete download: {e}")
            return False
    
    async def pause_download(self, download_id: str) -> bool:
        """Pause download"""
        return await self.download_service.pause_download(download_id)
    
    async def resume_download(self, download_id: str) -> bool:
        """Resume download"""
        return await self.download_service.resume_download(download_id)
    
    async def retry_download(self, download_id: str) -> bool:
        """Retry failed download"""
        return await self.download_service.retry_download(download_id)
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel download"""
        return await self.download_service.cancel_download(download_id)
    
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get video information"""
        return await self.download_service.analyze_url(url)
    
    async def analyze_url(self, url: str) -> Optional[VideoInfo]:
        """Analyze URL and extract video information"""
        return await self.download_service.analyze_url(url)
    
    async def start_download(self, download_id: str, quality: str = "720p") -> bool:
        """Start download with specified quality"""
        return await self.download_service.start_download(download_id, quality)
    
    async def get_download_progress(self, download_id: str) -> Optional[DownloadProgress]:
        """Get download progress"""
        download = await self.get_download(download_id)
        if download:
            return download.progress
        return None
    
    async def get_queue_position(self, download_id: str) -> int:
        """Get download queue position"""
        try:
            all_downloads = await self.get_all_downloads()
            pending = [d for d in all_downloads if d.status == DownloadStatus.PENDING]
            
            for i, d in enumerate(pending):
                if d.id == download_id:
                    return i + 1
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to get queue position: {e}")
            return 0
    
    async def get_download_count(self) -> int:
        """Get total download count"""
        try:
            downloads = await self.get_all_downloads()
            return len(downloads)
        except Exception:
            return 0
    
    async def get_active_download_count(self) -> int:
        """Get active download count"""
        try:
            downloads = await self.get_all_downloads()
            return len([d for d in downloads if d.is_active()])
        except Exception:
            return 0
    
    async def get_completed_download_count(self) -> int:
        """Get completed download count"""
        try:
            downloads = await self.get_all_downloads()
            return len([d for d in downloads if d.is_completed()])
        except Exception:
            return 0
    
    async def clear_completed_downloads(self) -> int:
        """Clear completed downloads"""
        try:
            await self.download_service.clear_completed()
            
            # Also clear from database
            deleted_count = self.download_dao.delete_completed()
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to clear completed: {e}")
            return 0
    
    async def is_url_already_downloaded(self, url: str) -> bool:
        """Check if URL was already downloaded"""
        try:
            downloads = await self.get_all_downloads()
            return any(
                d.url == url and d.status == DownloadStatus.COMPLETED
                for d in downloads
            )
        except Exception:
            return False
    
    async def get_download_by_url(self, url: str) -> Optional[Download]:
        """Get download by URL"""
        try:
            downloads = await self.get_all_downloads()
            
            for download in downloads:
                if download.url == url:
                    return download
            
            # Check database
            db_downloads = self.download_dao.search(url)
            if db_downloads:
                return self._db_to_entity(db_downloads[0])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get download by URL: {e}")
            return None
    
    def _save_to_database(self, download: Download):
        """Save download to database"""
        try:
            db_data = self._entity_to_db(download)
            
            # Check if exists
            existing = self.download_dao.get_by_id(download.id)
            if existing:
                self.download_dao.update(download.id, db_data)
            else:
                self.download_dao.insert(db_data)
                
        except Exception as e:
            self.logger.error(f"Failed to save to database: {e}")
    
    def _entity_to_db(self, download: Download) -> dict:
        """Convert Download entity to database dict"""
        data = {
            'id': download.id,
            'url': download.url,
            'title': download.title,
            'thumbnail_url': download.thumbnail_url,
            'file_path': download.file_path,
            'subtitle_path': download.subtitle_path,
            'status': download.status.value if download.status else 'pending',
            'progress': download.progress.percentage if download.progress else 0.0,
            'speed': download.progress.speed if download.progress else None,
            'size_total': download.progress.total_bytes if download.progress else 0,
            'size_downloaded': download.progress.downloaded_bytes if download.progress else 0,
            'format_id': download.format_id,
            'quality': download.quality,
            'error_message': download.error_message,
            'retry_count': download.retry_count,
        }
        
        # Add video info if available
        if download.video_info:
            data['website'] = download.video_info.website
            data['uploader'] = download.video_info.uploader
            data['duration'] = download.video_info.duration
        
        # Add timestamps
        if download.created_at:
            data['created_at'] = download.created_at.isoformat()
        else:
            data['created_at'] = datetime.now().isoformat()
        
        if download.updated_at:
            data['updated_at'] = download.updated_at.isoformat()
        else:
            data['updated_at'] = datetime.now().isoformat()
        
        if download.completed_at:
            data['completed_at'] = download.completed_at.isoformat()
        
        return data
    
    def _db_to_entity(self, data: dict) -> Download:
        """Convert database dict to Download entity"""
        from datetime import datetime as dt
        
        # Create download with required fields
        download = Download(
            id=data.get('id', ''),
            url=data.get('url', ''),
            title=data.get('title'),
            thumbnail_url=data.get('thumbnail_url'),
            file_path=data.get('file_path'),
            subtitle_path=data.get('subtitle_path'),
            format_id=data.get('format_id'),
            quality=data.get('quality'),
            error_message=data.get('error_message'),
            retry_count=data.get('retry_count', 0),
        )
        
        # Set status
        status_str = data.get('status', 'pending')
        try:
            download.status = DownloadStatus(status_str)
        except ValueError:
            download.status = DownloadStatus.PENDING
        
        # Set progress
        download.progress.percentage = data.get('progress', 0.0)
        download.progress.speed = data.get('speed')
        download.progress.total_bytes = data.get('size_total', 0)
        download.progress.downloaded_bytes = data.get('size_downloaded', 0)
        
        # Set video info
        if data.get('website') or data.get('uploader') or data.get('duration'):
            download.video_info = VideoInfo(
                url=data.get('url', ''),
                title=data.get('title'),
                thumbnail_url=data.get('thumbnail_url'),
                uploader=data.get('uploader'),
                duration=data.get('duration'),
                website=data.get('website'),
            )
        
        # Set timestamps
        if data.get('created_at'):
            try:
                download.created_at = dt.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                download.created_at = dt.now()
        
        if data.get('updated_at'):
            try:
                download.updated_at = dt.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                download.updated_at = dt.now()
        
        if data.get('completed_at'):
            try:
                download.completed_at = dt.fromisoformat(data['completed_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        return download