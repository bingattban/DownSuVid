"""
yt-dlp Provider Module
"""

import os
import asyncio
import json
from typing import Optional, Dict, Any, Callable, List
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.config.constants import (
    STORAGE_DOWNLOADS,
    STORAGE_VIDEOS,
    STORAGE_SUBTITLES,
    STORAGE_AUDIO,
    DEFAULT_VIDEO_QUALITY,
    SUPPORTED_VIDEO_QUALITIES
)


class YTDLPProvider(LoggerMixin):
    """yt-dlp download provider"""
    
    def __init__(self):
        self._ytdlp = None
        self.logger.info("YTDLPProvider initialized")
    
    async def _ensure_ytdlp(self):
        """Lazy load yt-dlp"""
        if self._ytdlp is None:
            try:
                import yt_dlp
                self._ytdlp = yt_dlp
                self.logger.debug("yt-dlp loaded successfully")
            except ImportError as e:
                self.logger.error(f"Failed to import yt-dlp: {e}")
                raise ImportError("yt-dlp is not installed")
        return self._ytdlp
    
    async def extract_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract video information
        
        Args:
            url: Video URL
            
        Returns:
            Video info dictionary
        """
        try:
            yt_dlp = await self._ensure_ytdlp()
            
            options = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
                'writesubtitles': False,
                'writeautomaticsub': False,
            }
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                self._sync_extract_info,
                yt_dlp,
                options,
                url
            )
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to extract info: {e}")
            return None
    
    def _sync_extract_info(self, yt_dlp, options: dict, url: str) -> Optional[dict]:
        """Synchronous extract info"""
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            self.logger.error(f"Sync extract info failed: {e}")
            return None
    
    async def download_video(self, url: str, output_path: str, 
                            quality: str = DEFAULT_VIDEO_QUALITY,
                            progress_callback: Optional[Callable] = None) -> bool:
        """
        Download video
        
        Args:
            url: Video URL
            output_path: Output directory
            quality: Video quality
            progress_callback: Progress callback function
            
        Returns:
            True if successful
        """
        try:
            yt_dlp = await self._ensure_ytdlp()
            
            # Extract quality value
            quality_value = quality.rstrip('p')
            format_string = f'bestvideo[height<={quality_value}]+bestaudio/best[height<={quality_value}]'
            
            options = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'format': format_string,
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [],
                'noplaylist': True,
            }
            
            if progress_callback:
                options['progress_hooks'].append(progress_callback)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._sync_download,
                yt_dlp,
                options,
                url
            )
            
            return result == 0
            
        except Exception as e:
            self.logger.error(f"Failed to download video: {e}")
            return False
    
    def _sync_download(self, yt_dlp, options: dict, url: str) -> int:
        """Synchronous download"""
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.download([url])
        except Exception as e:
            self.logger.error(f"Sync download failed: {e}")
            return 1
    
    async def download_audio(self, url: str, output_path: str,
                            progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Download audio only
        
        Args:
            url: Video URL
            output_path: Output directory
            progress_callback: Progress callback
            
        Returns:
            Path to audio file or None
        """
        try:
            yt_dlp = await self._ensure_ytdlp()
            
            options = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            
            if progress_callback:
                options['progress_hooks'] = [progress_callback]
            
            loop = asyncio.get_event_loop()
            
            # Extract info first to get filename
            info = await self.extract_info(url)
            if not info:
                return None
            
            result = await loop.run_in_executor(
                None,
                self._sync_download,
                yt_dlp,
                options,
                url
            )
            
            if result == 0:
                title = info.get('title', 'audio')
                audio_file = os.path.join(output_path, f"{title}.wav")
                if os.path.exists(audio_file):
                    return audio_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to download audio: {e}")
            return None
    
    async def download_subtitle(self, url: str, language: str,
                                output_path: str) -> Optional[str]:
        """
        Download subtitle
        
        Args:
            url: Video URL
            language: Subtitle language code
            output_path: Output directory
            
        Returns:
            Path to subtitle file or None
        """
        try:
            yt_dlp = await self._ensure_ytdlp()
            
            options = {
                'outtmpl': os.path.join(output_path, '%(title)s'),
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [language],
                'subtitlesformat': 'srt/vtt/ass/best',
                'quiet': True,
                'no_warnings': True,
            }
            
            loop = asyncio.get_event_loop()
            
            # Extract info to get filename
            info = await self.extract_info(url)
            if not info:
                return None
            
            result = await loop.run_in_executor(
                None,
                self._sync_download,
                yt_dlp,
                options,
                url
            )
            
            if result == 0:
                title = info.get('title', 'subtitle')
                # Find subtitle file
                for ext in ['srt', 'vtt', 'ass']:
                    sub_path = os.path.join(output_path, f"{title}.{language}.{ext}")
                    if os.path.exists(sub_path):
                        return sub_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to download subtitle: {e}")
            return None
    
    async def get_available_subtitles(self, url: str) -> List[Dict[str, str]]:
        """
        Get available subtitle languages
        
        Args:
            url: Video URL
            
        Returns:
            List of subtitle info
        """
        try:
            info = await self.extract_info(url)
            if not info:
                return []
            
            subtitles = []
            
            # Manual subtitles
            subs = info.get('subtitles', {})
            for lang, formats in subs.items():
                subtitles.append({
                    'language': lang,
                    'type': 'manual',
                    'formats': [f.get('ext', '') for f in formats]
                })
            
            # Auto-generated subtitles
            auto_subs = info.get('automatic_captions', {})
            for lang, formats in auto_subs.items():
                subtitles.append({
                    'language': lang,
                    'type': 'auto',
                    'formats': [f.get('ext', '') for f in formats]
                })
            
            return subtitles
            
        except Exception as e:
            self.logger.error(f"Failed to get subtitles: {e}")
            return []
    
    async def get_video_formats(self, url: str) -> List[Dict[str, Any]]:
        """
        Get available video formats
        
        Args:
            url: Video URL
            
        Returns:
            List of format info
        """
        try:
            info = await self.extract_info(url)
            if not info:
                return []
            
            formats = []
            seen_qualities = set()
            
            for fmt in info.get('formats', []):
                height = fmt.get('height')
                if height and height not in seen_qualities:
                    seen_qualities.add(height)
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'quality': f"{height}p",
                        'ext': fmt.get('ext'),
                        'filesize': fmt.get('filesize'),
                        'format_note': fmt.get('format_note'),
                    })
            
            # Sort by quality
            formats.sort(key=lambda x: int(x['quality'].rstrip('p')), reverse=True)
            
            return formats
            
        except Exception as e:
            self.logger.error(f"Failed to get formats: {e}")
            return []