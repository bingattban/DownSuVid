"""
Download Controller Module
"""

import asyncio
from typing import Optional, Callable, List
from kivy.clock import Clock

from app.utils.logger import LoggerMixin
from app.services.download.download_service import DownloadService
from app.services.subtitle.subtitle_service import SubtitleService
from app.domain.entities.download import Download, DownloadStatus, VideoInfo


class DownloadController(LoggerMixin):
    """Controller for download operations"""
    
    def __init__(self):
        self.download_service = DownloadService()
        self.subtitle_service = SubtitleService()
        self._progress_callbacks: dict = {}
        self.logger.info("DownloadController initialized")
    
    async def analyze_url(self, url: str) -> Optional[VideoInfo]:
        """
        Analyze URL and get video info
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo entity
        """
        return await self.download_service.analyze_url(url)
    
    async def start_download(self, url: str, quality: str = "720p",
                           progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Start a new download
        
        Args:
            url: Video URL
            quality: Video quality
            progress_callback: Progress callback function
            
        Returns:
            Download ID
        """
        try:
            # Create download
            download = await self.download_service.create_download(url)
            
            if not download:
                return None
            
            # Register progress callback
            if progress_callback:
                self._progress_callbacks[download.id] = progress_callback
            
            # Start download
            success = await self.download_service.start_download(
                download.id, quality
            )
            
            if success:
                # Start progress monitoring
                asyncio.create_task(self._monitor_progress(download.id))
                return download.id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to start download: {e}")
            return None
    
    async def _monitor_progress(self, download_id: str):
        """Monitor download progress"""
        while True:
            download = await self.download_service.get_download(download_id)
            
            if not download:
                break
            
            # Call progress callback
            if download_id in self._progress_callbacks:
                callback = self._progress_callbacks[download_id]
                
                Clock.schedule_once(lambda dt: callback(
                    download_id=download.id,
                    progress=download.progress.percentage,
                    speed=download.progress.get_formatted_speed(),
                    eta=download.progress.get_formatted_eta(),
                    status=download.status.value,
                    subtitle_status=download.subtitle_status.value,
                ))
            
            # Check if completed
            if download.status in [DownloadStatus.COMPLETED, 
                                  DownloadStatus.FAILED,
                                  DownloadStatus.CANCELLED]:
                break
            
            await asyncio.sleep(0.5)
    
    async def pause_download(self, download_id: str) -> bool:
        """Pause download"""
        return await self.download_service.pause_download(download_id)
    
    async def resume_download(self, download_id: str) -> bool:
        """Resume download"""
        return await self.download_service.resume_download(download_id)
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel download"""
        return await self.download_service.cancel_download(download_id)
    
    async def retry_download(self, download_id: str) -> bool:
        """Retry failed download"""
        return await self.download_service.retry_download(download_id)
    
    async def delete_download(self, download_id: str) -> bool:
        """Delete download"""
        return await self.download_service.delete_download(download_id)
    
    async def get_downloads(self) -> List[Download]:
        """Get all downloads"""
        return await self.download_service.get_downloads()
    
    async def get_download(self, download_id: str) -> Optional[Download]:
        """Get download by ID"""
        return await self.download_service.get_download(download_id)
    
    async def process_subtitles(self, url: str, 
                               video_path: Optional[str] = None) -> bool:
        """
        Process subtitles for download
        
        Args:
            url: Video URL
            video_path: Optional video path
            
        Returns:
            True if successful
        """
        subtitles = await self.subtitle_service.process_subtitles(url, video_path)
        return len(subtitles) > 0
    
    async def clear_completed(self):
        """Clear completed downloads"""
        await self.download_service.clear_completed()
    
    def remove_progress_callback(self, download_id: str):
        """Remove progress callback"""
        if download_id in self._progress_callbacks:
            del self._progress_callbacks[download_id]