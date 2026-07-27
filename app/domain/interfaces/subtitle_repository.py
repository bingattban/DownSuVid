"""
Subtitle Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.subtitle import Subtitle, SubtitleFormat, SubtitleSource


class SubtitleRepository(ABC):
    """Interface for subtitle repository"""
    
    @abstractmethod
    async def download_subtitle(self, url: str, language: str, 
                                output_path: str) -> Optional[Subtitle]:
        """
        Download subtitle
        
        Args:
            url: Video URL
            language: Subtitle language
            output_path: Output file path
            
        Returns:
            Subtitle entity or None
        """
        pass
    
    @abstractmethod
    async def extract_subtitle(self, video_path: str, 
                               output_path: str) -> Optional[Subtitle]:
        """
        Extract embedded subtitle
        
        Args:
            video_path: Video file path
            output_path: Output file path
            
        Returns:
            Subtitle entity or None
        """
        pass
    
    @abstractmethod
    async def generate_subtitle(self, audio_path: str, 
                                output_path: str) -> Optional[Subtitle]:
        """
        Generate subtitle from audio
        
        Args:
            audio_path: Audio file path
            output_path: Output file path
            
        Returns:
            Subtitle entity or None
        """
        pass
    
    @abstractmethod
    async def translate_subtitle(self, subtitle: Subtitle, 
                                 target_language: str = "ar") -> Optional[Subtitle]:
        """
        Translate subtitle
        
        Args:
            subtitle: Subtitle entity
            target_language: Target language code
            
        Returns:
            Translated subtitle or None
        """
        pass
    
    @abstractmethod
    async def detect_language(self, subtitle: Subtitle) -> Optional[str]:
        """
        Detect subtitle language
        
        Args:
            subtitle: Subtitle entity
            
        Returns:
            Language code or None
        """
        pass
    
    @abstractmethod
    async def process_subtitle_pipeline(self, url: str, 
                                        video_path: Optional[str] = None) -> List[Subtitle]:
        """
        Process subtitle pipeline following priority rules
        
        Args:
            url: Video URL
            video_path: Optional video file path
            
        Returns:
            List of processed subtitles
        """
        pass
    
    @abstractmethod
    async def get_available_subtitles(self, url: str) -> List[dict]:
        """
        Get available subtitles for video
        
        Args:
            url: Video URL
            
        Returns:
            List of subtitle info dictionaries
        """
        pass
    
    @abstractmethod
    async def validate_subtitle(self, file_path: str) -> bool:
        """
        Validate subtitle file
        
        Args:
            file_path: Subtitle file path
            
        Returns:
            True if valid
        """
        pass
    
    @abstractmethod
    async def convert_format(self, subtitle: Subtitle, 
                             target_format: SubtitleFormat) -> Optional[Subtitle]:
        """
        Convert subtitle format
        
        Args:
            subtitle: Subtitle entity
            target_format: Target format
            
        Returns:
            Converted subtitle or None
        """
        pass