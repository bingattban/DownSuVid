"""
Download Video Use Case
"""

from typing import Optional, List
import asyncio

from app.utils.logger import LoggerMixin
from app.domain.entities.download import Download, DownloadStatus, VideoInfo
from app.domain.interfaces.download_repository import DownloadRepository
from app.domain.interfaces.subtitle_repository import SubtitleRepository


class DownloadVideoUseCase(LoggerMixin):
    """Use case for downloading videos"""
    
    def __init__(self, download_repository: DownloadRepository,
                 subtitle_repository: Optional[SubtitleRepository] = None):
        self.download_repository = download_repository
        self.subtitle_repository = subtitle_repository
        self.logger.info("DownloadVideoUseCase initialized")
    
    async def execute(self, url: str, quality: str = "720p",
                     download_subtitle: bool = True,
                     generate_subtitle: bool = False) -> Optional[Download]:
        """
        Execute download use case
        
        Args:
            url: Video URL
            quality: Video quality
            download_subtitle: Whether to download subtitles
            generate_subtitle: Whether to generate subtitles if not available
            
        Returns:
            Download entity or None
        """
        try:
            # Step 1: Analyze URL
            self.logger.info(f"Analyzing URL: {url}")
            video_info = await self.download_repository.analyze_url(url)
            
            if not video_info:
                self.logger.error(f"Failed to analyze URL: {url}")
                return None
            
            # Step 2: Create download
            download = await self.download_repository.create_download(url)
            
            if not download:
                self.logger.error("Failed to create download")
                return None
            
            download.video_info = video_info
            download.quality = quality
            
            # Step 3: Start download
            self.logger.info(f"Starting download: {download.id}")
            
            success = await self._download_video(download, quality)
            
            if not success:
                download.status = DownloadStatus.FAILED
                download.error_message = "Video download failed"
                return download
            
            download.status = DownloadStatus.COMPLETED
            
            # Step 4: Handle subtitles
            if download_subtitle and self.subtitle_repository:
                await self._handle_subtitles(download, url)
            
            self.logger.info(f"Download completed successfully: {download.id}")
            return download
            
        except Exception as e:
            self.logger.error(f"Download use case failed: {e}")
            return None
    
    async def _download_video(self, download: Download, quality: str) -> bool:
        """Download video file"""
        try:
            # Update status
            download.status = DownloadStatus.DOWNLOADING
            
            # Start download
            success = await self.download_repository.start_download(
                download.id, quality
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Video download failed: {e}")
            return False
    
    async def _handle_subtitles(self, download: Download, url: str):
        """Handle subtitle processing"""
        try:
            # Process subtitles using subtitle repository
            subtitles = await self.subtitle_repository.process_subtitle_pipeline(url)
            
            if subtitles:
                download.subtitles = subtitles
                download.subtitle_path = subtitles[0].file_path
                self.logger.info(f"Subtitles processed: {len(subtitles)} files")
            else:
                self.logger.warning("No subtitles were processed")
                
        except Exception as e:
            self.logger.error(f"Subtitle processing failed: {e}")
    
    async def pause(self, download_id: str) -> bool:
        """Pause download"""
        return await self.download_repository.pause_download(download_id)
    
    async def resume(self, download_id: str) -> bool:
        """Resume download"""
        return await self.download_repository.resume_download(download_id)
    
    async def cancel(self, download_id: str) -> bool:
        """Cancel download"""
        return await self.download_repository.cancel_download(download_id)
    
    async def retry(self, download_id: str) -> bool:
        """Retry failed download"""
        download = await self.download_repository.get_download(download_id)
        
        if download and download.can_retry():
            download.retry_count += 1
            return await self._download_video(download, download.quality or "720p")
        
        return False
    
    async def get_progress(self, download_id: str) -> Optional[float]:
        """Get download progress"""
        download = await self.download_repository.get_download(download_id)
        
        if download:
            return download.progress.percentage
        
        return None
    
    async def get_active_downloads(self) -> List[Download]:
        """Get all active downloads"""
        return await self.download_repository.get_downloads_by_status(
            DownloadStatus.DOWNLOADING
        )