"""
Download Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.download import Download, DownloadStatus, VideoInfo


class DownloadRepository(ABC):
    """Interface for download repository"""
    
    @abstractmethod
    async def create_download(self, url: str) -> Download:
        """
        Create a new download
        
        Args:
            url: Video URL
            
        Returns:
            Download entity
        """
        pass
    
    @abstractmethod
    async def get_download(self, download_id: str) -> Optional[Download]:
        """
        Get download by ID
        
        Args:
            download_id: Download ID
            
        Returns:
            Download entity or None
        """
        pass
    
    @abstractmethod
    async def get_all_downloads(self) -> List[Download]:
        """
        Get all downloads
        
        Returns:
            List of downloads
        """
        pass
    
    @abstractmethod
    async def get_downloads_by_status(self, status: DownloadStatus) -> List[Download]:
        """
        Get downloads by status
        
        Args:
            status: Download status
            
        Returns:
            List of downloads
        """
        pass
    
    @abstractmethod
    async def update_download(self, download: Download) -> bool:
        """
        Update download
        
        Args:
            download: Download entity
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete_download(self, download_id: str) -> bool:
        """
        Delete download
        
        Args:
            download_id: Download ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def pause_download(self, download_id: str) -> bool:
        """
        Pause download
        
        Args:
            download_id: Download ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def resume_download(self, download_id: str) -> bool:
        """
        Resume download
        
        Args:
            download_id: Download ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def retry_download(self, download_id: str) -> bool:
        """
        Retry failed download
        
        Args:
            download_id: Download ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def cancel_download(self, download_id: str) -> bool:
        """
        Cancel download
        
        Args:
            download_id: Download ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """
        Get video information
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo entity or None
        """
        pass
    
    @abstractmethod
    async def analyze_url(self, url: str) -> Optional[VideoInfo]:
        """
        Analyze URL and extract video information
        
        Args:
            url: Video URL
            
        Returns:
            VideoInfo entity or None
        """
        pass