"""
FFmpeg Service Module
"""

import os
import asyncio
import subprocess
from typing import Optional, Callable, List, Dict
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils
from app.config.constants import (
    AUDIO_FORMAT,
    AUDIO_SAMPLE_RATE,
)


class FFmpegService(LoggerMixin):
    """Service for FFmpeg operations"""
    
    def __init__(self):
        self._ffmpeg_path = "ffmpeg"
        self._ffprobe_path = "ffprobe"
        self._initialized = False
        self._available = False
        self.logger.info("FFmpegService initialized")
    
    async def initialize(self) -> bool:
        """Initialize FFmpeg service"""
        try:
            # Check if ffmpeg is available
            result = await self._run_command([self._ffmpeg_path, "-version"])
            self._available = result is not None
            self._initialized = True
            
            if self._available:
                self.logger.info("FFmpeg service ready")
            else:
                self.logger.warning("FFmpeg not available - some features will be disabled")
            
            return self._available
            
        except Exception as e:
            self.logger.error(f"FFmpeg initialization failed: {e}")
            self._available = False
            self._initialized = True
            return False
    
    async def is_available(self) -> bool:
        """Check if FFmpeg is available"""
        if not self._initialized:
            await self.initialize()
        return self._available
    
    async def _run_command(self, cmd: List[str], timeout: int = 300) -> Optional[str]:
        """Run a command and return stdout"""
        try:
            loop = asyncio.get_event_loop()
            
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            )
            
            if process.returncode == 0:
                return process.stdout
            
            if process.stderr:
                self.logger.debug(f"Command stderr: {process.stderr[:200]}")
            
            return None
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {' '.join(cmd[:3])}")
            return None
        except FileNotFoundError:
            self.logger.error(f"Command not found: {cmd[0]}")
            return None
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return None
    
    async def extract_audio(self, video_path: str,
                           output_path: Optional[str] = None,
                           audio_format: str = AUDIO_FORMAT,
                           sample_rate: int = AUDIO_SAMPLE_RATE,
                           channels: int = 1,
                           progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_path: Output directory path
            audio_format: Audio format (wav, mp3, etc.)
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            progress_callback: Progress callback
            
        Returns:
            Path to extracted audio file or None
        """
        try:
            if not await self.is_available():
                self.logger.error("FFmpeg not available")
                return None
            
            if not os.path.exists(video_path):
                self.logger.error(f"Video file not found: {video_path}")
                return None
            
            # Set output path
            if not output_path:
                output_path = str(FileUtils.get_audio_path())
            
            FileUtils.ensure_directory(output_path)
            
            # Generate output filename
            video_name = Path(video_path).stem
            output_file = os.path.join(output_path, f"{video_name}_audio.{audio_format}")
            
            self.logger.info(f"Extracting audio from: {video_name}")
            
            if progress_callback:
                await progress_callback(0.0, "starting")
            
            # Build FFmpeg command
            cmd = [
                self._ffmpeg_path,
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le" if audio_format == "wav" else audio_format,
                "-ar", str(sample_rate),
                "-ac", str(channels),
                "-y",  # Overwrite output file
                output_file
            ]
            
            # Run command
            result = await self._run_command(cmd, timeout=3600)
            
            if progress_callback:
                await progress_callback(100.0, "completed")
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                self.logger.info(f"Audio extracted successfully: {output_file}")
                return output_file
            
            self.logger.error("Audio extraction failed - no output file")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio: {e}")
            return None
    
    async def extract_audio_segment(self, video_path: str,
                                   start_time: float,
                                   duration: float,
                                   output_path: Optional[str] = None) -> Optional[str]:
        """
        Extract a segment of audio from video
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            duration: Duration in seconds
            output_path: Output directory
            
        Returns:
            Path to audio segment file
        """
        try:
            if not await self.is_available():
                return None
            
            if not output_path:
                output_path = str(FileUtils.get_audio_path())
            
            video_name = Path(video_path).stem
            output_file = os.path.join(
                output_path,
                f"{video_name}_segment_{int(start_time)}_{int(duration)}.{AUDIO_FORMAT}"
            )
            
            cmd = [
                self._ffmpeg_path,
                "-i", video_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", str(AUDIO_SAMPLE_RATE),
                "-ac", "1",
                "-y",
                output_file
            ]
            
            result = await self._run_command(cmd)
            
            if result is not None and os.path.exists(output_file):
                return output_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio segment: {e}")
            return None
    
    async def get_media_duration(self, file_path: str) -> Optional[float]:
        """
        Get media file duration in seconds
        
        Args:
            file_path: Path to media file
            
        Returns:
            Duration in seconds or None
        """
        try:
            if not await self.is_available():
                return None
            
            if not os.path.exists(file_path):
                return None
            
            cmd = [
                self._ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            
            output = await self._run_command(cmd, timeout=10)
            
            if output:
                return float(output.strip())
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get duration: {e}")
            return None
    
    async def get_media_info(self, file_path: str) -> Optional[Dict]:
        """
        Get detailed media information
        
        Args:
            file_path: Path to media file
            
        Returns:
            Media info dictionary
        """
        try:
            if not await self.is_available():
                return None
            
            if not os.path.exists(file_path):
                return None
            
            import json
            
            cmd = [
                self._ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            output = await self._run_command(cmd, timeout=10)
            
            if output:
                info = json.loads(output)
                
                format_info = info.get('format', {})
                streams = info.get('streams', [])
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'size': int(format_info.get('size', 0)),
                    'bitrate': int(format_info.get('bit_rate', 0)),
                    'format': format_info.get('format_name', ''),
                    'streams_count': len(streams),
                    'video_streams': len([s for s in streams if s.get('codec_type') == 'video']),
                    'audio_streams': len([s for s in streams if s.get('codec_type') == 'audio']),
                    'subtitle_streams': len([s for s in streams if s.get('codec_type') == 'subtitle']),
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get media info: {e}")
            return None
    
    async def create_thumbnail(self, video_path: str,
                              time_position: float = 5.0,
                              width: int = 320,
                              height: int = 180) -> Optional[str]:
        """
        Create thumbnail from video
        
        Args:
            video_path: Path to video file
            time_position: Time position in seconds
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            Path to thumbnail image
        """
        try:
            if not await self.is_available():
                return None
            
            if not os.path.exists(video_path):
                return None
            
            output_dir = FileUtils.get_cache_path()
            video_name = Path(video_path).stem
            output_file = str(output_dir / f"{video_name}_thumb.jpg")
            
            cmd = [
                self._ffmpeg_path,
                "-i", video_path,
                "-ss", str(time_position),
                "-vframes", "1",
                "-vf", f"scale={width}:{height}",
                "-y",
                output_file
            ]
            
            result = await self._run_command(cmd, timeout=30)
            
            if result is not None and os.path.exists(output_file):
                return output_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to create thumbnail: {e}")
            return None
    
    async def convert_video(self, input_path: str,
                           output_format: str = "mp4",
                           quality: str = "medium",
                           progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Convert video to different format
        
        Args:
            input_path: Path to input video
            output_format: Target format
            quality: Quality preset (low, medium, high)
            progress_callback: Progress callback
            
        Returns:
            Path to converted video
        """
        try:
            if not await self.is_available():
                return None
            
            if not os.path.exists(input_path):
                return None
            
            quality_presets = {
                'low': {'crf': '28', 'preset': 'fast'},
                'medium': {'crf': '23', 'preset': 'medium'},
                'high': {'crf': '18', 'preset': 'slow'},
            }
            
            preset = quality_presets.get(quality, quality_presets['medium'])
            
            output_dir = os.path.dirname(input_path)
            input_name = Path(input_path).stem
            output_file = os.path.join(output_dir, f"{input_name}_converted.{output_format}")
            
            if progress_callback:
                await progress_callback(0.0, "converting")
            
            cmd = [
                self._ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-crf", preset['crf'],
                "-preset", preset['preset'],
                "-c:a", "aac",
                "-b:a", "128k",
                "-y",
                output_file
            ]
            
            result = await self._run_command(cmd, timeout=3600)
            
            if progress_callback:
                await progress_callback(100.0, "completed")
            
            if result is not None and os.path.exists(output_file):
                return output_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to convert video: {e}")
            return None
    
    async def merge_audio_video(self, video_path: str,
                               audio_path: str,
                               output_path: Optional[str] = None) -> Optional[str]:
        """
        Merge audio with video
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Output directory
            
        Returns:
            Path to merged file
        """
        try:
            if not await self.is_available():
                return None
            
            if not os.path.exists(video_path) or not os.path.exists(audio_path):
                return None
            
            if not output_path:
                output_path = str(FileUtils.get_video_path())
            
            video_name = Path(video_path).stem
            output_file = os.path.join(output_path, f"{video_name}_merged.mp4")
            
            cmd = [
                self._ffmpeg_path,
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                "-y",
                output_file
            ]
            
            result = await self._run_command(cmd, timeout=300)
            
            if result is not None and os.path.exists(output_file):
                return output_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to merge audio/video: {e}")
            return None
    
    async def get_version(self) -> Optional[str]:
        """
        Get FFmpeg version string
        
        Returns:
            Version string or None
        """
        try:
            if not await self.is_available():
                return None
            
            output = await self._run_command([self._ffmpeg_path, "-version"], timeout=5)
            
            if output:
                # Extract version from first line
                first_line = output.split('\n')[0]
                parts = first_line.split()
                if len(parts) >= 3:
                    return parts[2]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get version: {e}")
            return None