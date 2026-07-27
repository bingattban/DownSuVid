"""
Subtitle Repository Implementation
"""

from typing import Optional, List
import os

from app.utils.logger import LoggerMixin
from app.domain.entities.subtitle import Subtitle, SubtitleFormat, SubtitleSource
from app.domain.interfaces.subtitle_repository import SubtitleRepository
from app.services.subtitle.subtitle_service import SubtitleService
from app.services.translation.translation_service import TranslationService
from app.services.speech.speech_service import SpeechService
from app.providers.downloader.ytdlp_provider import YTDLPProvider
from app.utils.file_utils import FileUtils


class SubtitleRepositoryImpl(SubtitleRepository, LoggerMixin):
    """Implementation of SubtitleRepository"""
    
    def __init__(self):
        self.subtitle_service = SubtitleService()
        self.translation_service = TranslationService()
        self.speech_service = SpeechService()
        self.ytdlp_provider = YTDLPProvider()
        self.logger.info("SubtitleRepositoryImpl initialized")
    
    async def download_subtitle(self, url: str, language: str,
                                output_path: str) -> Optional[Subtitle]:
        """Download subtitle"""
        try:
            if not output_path:
                output_path = str(FileUtils.get_subtitle_path())
            
            # Download using yt-dlp
            sub_path = await self.ytdlp_provider.download_subtitle(url, language, output_path)
            
            if sub_path and os.path.exists(sub_path):
                # Read content
                with open(sub_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine format
                ext = os.path.splitext(sub_path)[1].lower().lstrip('.')
                format_map = {
                    'srt': SubtitleFormat.SRT,
                    'vtt': SubtitleFormat.VTT,
                    'ass': SubtitleFormat.ASS,
                }
                
                subtitle = Subtitle(
                    language=language,
                    language_name=language,
                    format=format_map.get(ext, SubtitleFormat.SRT),
                    source=SubtitleSource.DOWNLOADED,
                    file_path=sub_path,
                    content=content,
                    video_url=url,
                )
                
                # Count words
                subtitle.word_count = len(content.split())
                subtitle.character_count = len(content)
                
                return subtitle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to download subtitle: {e}")
            return None
    
    async def extract_subtitle(self, video_path: str,
                               output_path: str) -> Optional[Subtitle]:
        """Extract embedded subtitle"""
        try:
            # Use FFmpeg to extract embedded subtitles
            from app.providers.ffmpeg.ffmpeg_provider import FFmpegProvider
            
            ffmpeg = FFmpegProvider()
            
            if not await ffmpeg.is_available():
                self.logger.error("FFmpeg not available")
                return None
            
            if not output_path:
                output_path = str(FileUtils.get_subtitle_path())
            
            # Extract subtitle stream
            media_info = await ffmpeg.get_media_info(video_path)
            
            if not media_info:
                return None
            
            # Find subtitle streams
            subtitle_streams = [
                s for s in media_info.get('streams', [])
                if s.get('codec_type') == 'subtitle'
            ]
            
            if not subtitle_streams:
                self.logger.info("No embedded subtitles found")
                return None
            
            # Extract first subtitle stream
            output_file = os.path.join(output_path, 'extracted_subtitle.srt')
            
            # Build extraction command
            import subprocess
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-map', f"0:{subtitle_streams[0].get('index', 2)}",
                '-c:s', 'srt',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lang = subtitle_streams[0].get('tags', {}).get('language', 'unknown')
                
                subtitle = Subtitle(
                    language=lang,
                    language_name=lang,
                    format=SubtitleFormat.SRT,
                    source=SubtitleSource.EXTRACTED,
                    file_path=output_file,
                    content=content,
                )
                
                return subtitle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract subtitle: {e}")
            return None
    
    async def generate_subtitle(self, audio_path: str,
                                output_path: str) -> Optional[Subtitle]:
        """Generate subtitle from audio"""
        try:
            if not output_path:
                output_path = str(FileUtils.get_subtitle_path())
            
            # Use speech service
            result = await self.speech_service.transcribe_audio(audio_path)
            
            if not result or not result.get('text'):
                return None
            
            # Build SRT from segments
            segments = result.get('segments', [])
            srt_content = self._build_srt(segments)
            
            # Save subtitle file
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            subtitle_file = os.path.join(output_path, f"{audio_name}_generated.srt")
            
            with open(subtitle_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            subtitle = Subtitle(
                language=result.get('language', 'en'),
                language_name=result.get('language', 'English'),
                format=SubtitleFormat.SRT,
                source=SubtitleSource.GENERATED,
                file_path=subtitle_file,
                content=srt_content,
                is_auto_generated=True,
                confidence_score=result.get('confidence', 0.0),
            )
            
            return subtitle
            
        except Exception as e:
            self.logger.error(f"Failed to generate subtitle: {e}")
            return None
    
    async def translate_subtitle(self, subtitle: Subtitle,
                                 target_language: str = "ar") -> Optional[Subtitle]:
        """Translate subtitle"""
        try:
            return await self.translation_service.translate_subtitle(subtitle, target_language)
        except Exception as e:
            self.logger.error(f"Failed to translate subtitle: {e}")
            return None
    
    async def detect_language(self, subtitle: Subtitle) -> Optional[str]:
        """Detect subtitle language"""
        try:
            if not subtitle.content:
                return None
            
            return await self.translation_service.detect_language(subtitle.content)
            
        except Exception as e:
            self.logger.error(f"Failed to detect language: {e}")
            return None
    
    async def process_subtitle_pipeline(self, url: str,
                                        video_path: Optional[str] = None) -> List[Subtitle]:
        """Process subtitle pipeline"""
        try:
            return await self.subtitle_service.process_subtitles(url, video_path)
        except Exception as e:
            self.logger.error(f"Failed to process subtitle pipeline: {e}")
            return []
    
    async def get_available_subtitles(self, url: str) -> List[dict]:
        """Get available subtitles for video"""
        try:
            return await self.ytdlp_provider.get_available_subtitles(url)
        except Exception as e:
            self.logger.error(f"Failed to get available subtitles: {e}")
            return []
    
    async def validate_subtitle(self, file_path: str) -> bool:
        """Validate subtitle file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check file size
            if os.path.getsize(file_path) == 0:
                return False
            
            # Try to parse content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return False
            
            # Check for basic SRT structure
            if '-->' in content:
                return True
            
            return True
            
        except Exception:
            return False
    
    async def convert_format(self, subtitle: Subtitle,
                             target_format: SubtitleFormat) -> Optional[Subtitle]:
        """Convert subtitle format"""
        try:
            if subtitle.format == target_format:
                return subtitle
            
            # Convert to SRT first if needed
            srt_content = subtitle.to_srt_format()
            
            # Save converted file
            original_path = subtitle.file_path or "subtitle"
            base_name = os.path.splitext(original_path)[0]
            new_path = f"{base_name}.{target_format.value}"
            
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            converted_subtitle = Subtitle(
                language=subtitle.language,
                language_name=subtitle.language_name,
                format=target_format,
                source=subtitle.source,
                file_path=new_path,
                content=srt_content,
                original_content=subtitle.original_content,
            )
            
            return converted_subtitle
            
        except Exception as e:
            self.logger.error(f"Failed to convert format: {e}")
            return None
    
    def _build_srt(self, segments: List[dict]) -> str:
        """Build SRT content from segments"""
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start = self._format_time(segment.get('start', 0))
            end = self._format_time(segment.get('end', 0))
            text = segment.get('text', '').strip()
            
            if text:
                srt_lines.append(str(i))
                srt_lines.append(f"{start} --> {end}")
                srt_lines.append(text)
                srt_lines.append("")
        
        return '\n'.join(srt_lines)
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to SRT time"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs - int(secs)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"