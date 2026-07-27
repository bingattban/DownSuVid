"""
Download Service Module
"""

import os
import asyncio
import uuid
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils
from app.domain.entities.download import (
    Download, DownloadStatus, VideoInfo, 
    SubtitleInfo, SubtitleStatus, DownloadProgress
)
from app.providers.downloader.ytdlp_provider import YTDLPProvider
from app.providers.ffmpeg.ffmpeg_provider import FFmpegProvider


class DownloadService(LoggerMixin):
    """Service for managing downloads"""
    
    def __init__(self):
        self.ytdlp_provider = YTDLPProvider()
        self.ffmpeg_provider = FFmpegProvider()
        self.active_downloads: Dict[str, Download] = {}
        self.download_queue: List[str] = []
        self.max_parallel = 3
        self._processing = False
        self.logger.info("DownloadService initialized")
    
    async def create_download(self, url: str) -> Optional[Download]:
        """
        Create a new download from URL
        
        Args:
            url: Video URL
            
        Returns:
            Download entity or None
        """
        try:
            # Create download entity
            download_id = str(uuid.uuid4())
            download = Download(
                id=download_id,
                url=url,
                status=DownloadStatus.PENDING
            )
            
            # Store download
            self.active_downloads[download_id] = download
            
            # Add to queue
            self.download_queue.append(download_id)
            
            # Start processing if not already
            if not self._processing:
                asyncio.create_task(self._process_queue())
            
            self.logger.info(f"Download created: {download_id}")
            return download
            
        except Exception as e:
            self.logger.error(f"Failed to create download: {e}")
            return None
    
    async def analyze_url(self, url: str) -> Optional[VideoInfo]:
        """
        Analyze URL and get video information
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo entity or None
        """
        try:
            info = await self.ytdlp_provider.extract_info(url)
            if not info:
                return None
            
            # Build VideoInfo
            video_info = VideoInfo(
                url=url,
                title=info.get('title'),
                thumbnail_url=info.get('thumbnail'),
                uploader=info.get('uploader'),
                duration=info.get('duration'),
                website=info.get('extractor'),
                description=info.get('description'),
            )
            
            # Get formats
            formats = await self.ytdlp_provider.get_video_formats(url)
            video_info.formats = formats
            video_info.qualities = [f['quality'] for f in formats]
            
            # Get subtitles
            subtitles = await self.ytdlp_provider.get_available_subtitles(url)
            video_info.subtitle_languages = [s['language'] for s in subtitles]
            
            return video_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze URL: {e}")
            return None
    
    async def start_download(self, download_id: str, 
                           quality: str = "720p",
                           download_subtitle: bool = True) -> bool:
        """
        Start downloading video
        
        Args:
            download_id: Download ID
            quality: Video quality
            download_subtitle: Whether to download subtitles
            
        Returns:
            True if download started
        """
        try:
            download = self.active_downloads.get(download_id)
            if not download:
                self.logger.error(f"Download not found: {download_id}")
                return False
            
            download.status = DownloadStatus.DOWNLOADING
            download.quality = quality
            
            # Start download in background
            asyncio.create_task(
                self._download_video(download, quality, download_subtitle)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start download: {e}")
            return False
    
    async def _download_video(self, download: Download, quality: str,
                            download_subtitle: bool):
        """Internal video download method"""
        try:
            # Get output path
            output_path = str(FileUtils.get_video_path())
            FileUtils.ensure_directory(output_path)
            
            # Progress callback
            def progress_hook(progress_data: dict):
                self._update_progress(download, progress_data)
            
            # Download video
            success = await self.ytdlp_provider.download_video(
                download.url,
                output_path,
                quality,
                progress_hook
            )
            
            if success:
                download.status = DownloadStatus.COMPLETED
                download.completed_at = datetime.now()
                
                # Download subtitle if requested
                if download_subtitle:
                    download.subtitle_status = SubtitleStatus.DOWNLOADING
                    asyncio.create_task(self._download_subtitles(download))
                
                self.logger.info(f"Download completed: {download.id}")
            else:
                download.status = DownloadStatus.FAILED
                download.error_message = "Download failed"
                
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            download.status = DownloadStatus.FAILED
            download.error_message = str(e)
    
    def _update_progress(self, download: Download, progress_data: dict):
        """Update download progress"""
        if progress_data.get('status') == 'downloading':
            downloaded = progress_data.get('downloaded_bytes', 0)
            total = progress_data.get('total_bytes', 0) or progress_data.get('total_bytes_estimate', 0)
            speed = progress_data.get('speed', 0)
            
            download.progress.downloaded_bytes = downloaded
            download.progress.total_bytes = total
            download.progress.speed_bytes = speed
            
            if total:
                download.progress.percentage = (downloaded / total) * 100
            
            if speed:
                from app.utils.file_utils import FileUtils
                download.progress.speed = f"{FileUtils.format_file_size(int(speed))}/s"
            
            eta = progress_data.get('eta')
            if eta:
                download.progress.eta = eta
    
    async def _download_subtitles(self, download: Download):
        """Download subtitles for video"""
        try:
            # Get available subtitles
            subtitles = await self.ytdlp_provider.get_available_subtitles(download.url)
            
            # Priority: Arabic first
            arabic_subs = [s for s in subtitles 
                          if s['language'].lower() in ['ar', 'ara', 'arabic']]
            
            if arabic_subs:
                # Download Arabic subtitle
                sub_path = await self.ytdlp_provider.download_subtitle(
                    download.url,
                    'ar',
                    str(FileUtils.get_subtitle_path())
                )
                
                if sub_path:
                    download.subtitle_status = SubtitleStatus.COMPLETED
                    download.subtitle_path = sub_path
                    self.logger.info(f"Arabic subtitle downloaded for {download.id}")
                else:
                    download.subtitle_status = SubtitleStatus.FAILED
            else:
                # Will be handled by subtitle service
                download.subtitle_status = SubtitleStatus.NONE
                
        except Exception as e:
            self.logger.error(f"Subtitle download error: {e}")
            download.subtitle_status = SubtitleStatus.FAILED
    
    async def pause_download(self, download_id: str) -> bool:
        """Pause download"""
        download = self.active_downloads.get(download_id)
        if download and download.status == DownloadStatus.DOWNLOADING:
            download.status = DownloadStatus.PAUSED
            return True
        return False
    
    async def resume_download(self, download_id: str) -> bool:
        """Resume download"""
        download = self.active_downloads.get(download_id)
        if download and download.status == DownloadStatus.PAUSED:
            return await self.start_download(download_id, download.quality)
        return False
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel download"""
        download = self.active_downloads.get(download_id)
        if download:
            download.status = DownloadStatus.CANCELLED
            # Remove from queue
            if download_id in self.download_queue:
                self.download_queue.remove(download_id)
            return True
        return False
    
    async def retry_download(self, download_id: str) -> bool:
        """Retry failed download"""
        download = self.active_downloads.get(download_id)
        if download and download.can_retry():
            download.retry_count += 1
            return await self.start_download(download_id, download.quality)
        return False
    
    async def delete_download(self, download_id: str) -> bool:
        """Delete download and files"""
        download = self.active_downloads.get(download_id)
        if download:
            # Delete files if exist
            if download.file_path and os.path.exists(download.file_path):
                os.remove(download.file_path)
            if download.subtitle_path and os.path.exists(download.subtitle_path):
                os.remove(download.subtitle_path)
            
            # Remove from memory
            del self.active_downloads[download_id]
            if download_id in self.download_queue:
                self.download_queue.remove(download_id)
            
            return True
        return False
    
    async def _process_queue(self):
        """Process download queue"""
        self._processing = True
        
        while self.download_queue:
            # Count active downloads
            active_count = sum(1 for d in self.active_downloads.values() 
                             if d.status == DownloadStatus.DOWNLOADING)
            
            if active_count >= self.max_parallel:
                await asyncio.sleep(1)
                continue
            
            # Get next pending download
            download_id = self.download_queue.pop(0)
            download = self.active_downloads.get(download_id)
            
            if download and download.status == DownloadStatus.PENDING:
                await self.start_download(download_id)
            
            await asyncio.sleep(0.5)
        
        self._processing = False
    
    async def get_downloads(self) -> List[Download]:
        """Get all downloads"""
        return list(self.active_downloads.values())
    
    async def get_download(self, download_id: str) -> Optional[Download]:
        """Get download by ID"""
        return self.active_downloads.get(download_id)
    
    async def get_queue_size(self) -> int:
        """Get queue size"""
        return len(self.download_queue)
    
    async def clear_completed(self):
        """Clear completed downloads"""
        completed_ids = [
            d_id for d_id, d in self.active_downloads.items()
            if d.status in [DownloadStatus.COMPLETED, DownloadStatus.CANCELLED]
        ]
        for d_id in completed_ids:
            del self.active_downloads[d_id]
    
    async def set_max_parallel(self, count: int):
        """Set maximum parallel downloads"""
        self.max_parallel = max(1, min(count, 10))