"""
FFmpeg Provider Module
"""

import os
import asyncio
import subprocess
from typing import Optional, List, Tuple
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils


class FFmpegProvider(LoggerMixin):
    """FFmpeg provider for audio/video processing"""
    
    def __init__(self):
        self._ffmpeg_path = "ffmpeg"
        self._ffprobe_path = "ffprobe"
        self._available = None
        self.logger.info("FFmpegProvider initialized")
    
    async def is_available(self) -> bool:
        """
        Check if FFmpeg is available
        
        Returns:
            True if FFmpeg is installed
        """
        if self._available is None:
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._check_ffmpeg
                )
                self._available = result
                self.logger.info(f"FFmpeg available: {self._available}")
            except Exception as e:
                self.logger.warning(f"FFmpeg check failed: {e}")
                self._available = False
        
        return self._available
    
    def _check_ffmpeg(self) -> bool:
        """Check FFmpeg availability"""
        try:
            subprocess.run(
                [self._ffmpeg_path, "-version"],
                capture_output=True,
                check=True,
                timeout=10
            )
            return True
        except Exception:
            return False
    
    async def extract_audio(self, video_path: str, output_path: str,
                           audio_format: str = "wav",
                           sample_rate: int = 16000,
                           channels: int = 1) -> Optional[str]:
        """
        Extract audio from video
        
        Args:
            video_path: Path to video file
            output_path: Output directory
            audio_format: Audio format
            sample_rate: Sample rate in Hz
            channels: Number of channels
            
        Returns:
            Path to audio file or None
        """
        try:
            if not await self.is_available():
                self.logger.error("FFmpeg is not available")
                return None
            
            # Ensure output directory exists
            FileUtils.ensure_directory(output_path)
            
            # Generate output filename
            video_name = Path(video_path).stem
            output_file = os.path.join(output_path, f"{video_name}_audio.{audio_format}")
            
            # Build FFmpeg command
            cmd = [
                self._ffmpeg_path,
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le" if audio_format == "wav" else audio_format,
                "-ar", str(sample_rate),
                "-ac", str(channels),
                "-y",  # Overwrite
                output_file
            ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._run_ffmpeg,
                cmd
            )
            
            if result and os.path.exists(output_file):
                self.logger.info(f"Audio extracted: {output_file}")
                return output_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio: {e}")
            return None
    
    async def convert_video(self, input_path: str, output_path: str,
                           video_codec: str = "libx264",
                           audio_codec: str = "aac") -> Optional[str]:
        """
        Convert video format
        
        Args:
            input_path: Input video path
            output_path: Output directory
            video_codec: Video codec
            audio_codec: Audio codec
            
        Returns:
            Path to converted video
        """
        try:
            if not await self.is_available():
                return None
            
            FileUtils.ensure_directory(output_path)
            
            input_name = Path(input_path).stem
            output_file = os.path.join(output_path, f"{input_name}_converted.mp4")
            
            cmd = [
                self._ffmpeg_path,
                "-i", input_path,
                "-c:v", video_codec,
                "-c:a", audio_codec,
                "-y",
                output_file
            ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_ffmpeg, cmd)
            
            return output_file if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to convert video: {e}")
            return None
    
    async def get_media_info(self, file_path: str) -> Optional[dict]:
        """
        Get media file information
        
        Args:
            file_path: Media file path
            
        Returns:
            Media info dictionary
        """
        try:
            if not await self.is_available():
                return None
            
            cmd = [
                self._ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._run_ffprobe,
                cmd
            )
            
            if result:
                import json
                return json.loads(result)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get media info: {e}")
            return None
    
    def _run_ffmpeg(self, cmd: List[str]) -> bool:
        """Run FFmpeg command"""
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if process.returncode == 0:
                return True
            else:
                self.logger.error(f"FFmpeg error: {process.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"FFmpeg execution failed: {e}")
            return False
    
    def _run_ffprobe(self, cmd: List[str]) -> Optional[str]:
        """Run FFprobe command"""
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                return process.stdout
            else:
                self.logger.error(f"FFprobe error: {process.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"FFprobe execution failed: {e}")
            return None
    
    async def concatenate_videos(self, input_files: List[str],
                                output_path: str) -> Optional[str]:
        """
        Concatenate multiple videos
        
        Args:
            input_files: List of video file paths
            output_path: Output file path
            
        Returns:
            Path to concatenated video
        """
        try:
            if not await self.is_available():
                return None
            
            # Create concat file
            concat_file = os.path.join(FileUtils.get_temp_path(), "concat_list.txt")
            with open(concat_file, 'w') as f:
                for video_path in input_files:
                    f.write(f"file '{video_path}'\n")
            
            cmd = [
                self._ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-y",
                output_path
            ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_ffmpeg, cmd)
            
            # Clean up concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            return output_path if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to concatenate videos: {e}")
            return None