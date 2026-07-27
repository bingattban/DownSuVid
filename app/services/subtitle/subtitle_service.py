"""
Subtitle Service Module
"""

import os
import asyncio
from typing import Optional, List, Dict
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils
from app.domain.entities.subtitle import (
    Subtitle, SubtitleFormat, SubtitleSource, SubtitlePriority
)
from app.providers.downloader.ytdlp_provider import YTDLPProvider
from app.providers.ffmpeg.ffmpeg_provider import FFmpegProvider
from app.services.speech.speech_service import SpeechService
from app.services.translation.translation_service import TranslationService


class SubtitleService(LoggerMixin):
    """Service for subtitle processing with smart pipeline"""
    
    def __init__(self):
        self.ytdlp_provider = YTDLPProvider()
        self.ffmpeg_provider = FFmpegProvider()
        self.speech_service = SpeechService()
        self.translation_service = TranslationService()
        self.logger.info("SubtitleService initialized")
    
    async def process_subtitles(self, url: str, 
                               video_path: Optional[str] = None) -> List[Subtitle]:
        """
        Process subtitles using smart pipeline
        
        Priority:
        1. Arabic subtitles if available
        2. Best available subtitle → translate to Arabic
        3. Generate from audio → translate to Arabic
        
        Args:
            url: Video URL
            video_path: Optional video file path
            
        Returns:
            List of processed subtitles
        """
        try:
            self.logger.info(f"Starting subtitle pipeline for {url}")
            
            # Step 1: Check for Arabic subtitles
            arabic_sub = await self._get_arabic_subtitle(url)
            if arabic_sub:
                self.logger.info("Arabic subtitle found and downloaded")
                return [arabic_sub]
            
            # Step 2: Find best available subtitle
            best_sub = await self._get_best_subtitle(url)
            if best_sub:
                self.logger.info(f"Best subtitle found: {best_sub.language}")
                
                # Check if already Arabic
                if best_sub.is_arabic():
                    return [best_sub]
                
                # Translate to Arabic
                translated = await self.translation_service.translate_subtitle(
                    best_sub, "ar"
                )
                
                if translated:
                    self.logger.info("Subtitle translated to Arabic")
                    return [best_sub, translated]
                else:
                    self.logger.warning("Translation failed, returning original")
                    return [best_sub]
            
            # Step 3: Generate from audio
            self.logger.info("No subtitles found, generating from audio")
            
            # Need video path for audio extraction
            if not video_path:
                self.logger.error("Video path required for audio extraction")
                return []
            
            generated_sub = await self._generate_subtitle_from_audio(video_path)
            
            if generated_sub:
                if generated_sub.is_arabic():
                    return [generated_sub]
                
                # Translate generated subtitle
                translated = await self.translation_service.translate_subtitle(
                    generated_sub, "ar"
                )
                
                if translated:
                    return [generated_sub, translated]
                else:
                    return [generated_sub]
            
            self.logger.error("Failed to generate subtitle")
            return []
            
        except Exception as e:
            self.logger.error(f"Subtitle pipeline failed: {e}")
            return []
    
    async def _get_arabic_subtitle(self, url: str) -> Optional[Subtitle]:
        """Try to get Arabic subtitle"""
        try:
            # Check available subtitles
            subtitles = await self.ytdlp_provider.get_available_subtitles(url)
            
            arabic_subs = [
                s for s in subtitles 
                if s['language'].lower() in ['ar', 'ara', 'arabic']
            ]
            
            if not arabic_subs:
                return None
            
            self.logger.info(f"Found {len(arabic_subs)} Arabic subtitle(s)")
            
            # Download Arabic subtitle
            output_path = str(FileUtils.get_subtitle_path())
            sub_path = await self.ytdlp_provider.download_subtitle(
                url, 'ar', output_path
            )
            
            if sub_path and os.path.exists(sub_path):
                # Read subtitle content
                with open(sub_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine format
                ext = Path(sub_path).suffix.lower().lstrip('.')
                format_map = {
                    'srt': SubtitleFormat.SRT,
                    'vtt': SubtitleFormat.VTT,
                    'ass': SubtitleFormat.ASS,
                }
                
                subtitle = Subtitle(
                    language='ar',
                    language_name='العربية',
                    format=format_map.get(ext, SubtitleFormat.SRT),
                    source=SubtitleSource.DOWNLOADED,
                    priority=SubtitlePriority.ARABIC_ORIGINAL,
                    file_path=sub_path,
                    content=content,
                    is_auto_generated=False,
                )
                
                return subtitle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get Arabic subtitle: {e}")
            return None
    
    async def _get_best_subtitle(self, url: str) -> Optional[Subtitle]:
        """Get the best available subtitle"""
        try:
            subtitles = await self.ytdlp_provider.get_available_subtitles(url)
            
            if not subtitles:
                return None
            
            # Priority: manual > auto-generated
            # Priority: English > other languages
            manual_subs = [s for s in subtitles if s['type'] == 'manual']
            auto_subs = [s for s in subtitles if s['type'] == 'auto']
            
            # Prefer English manuals
            en_manual = [s for s in manual_subs 
                        if s['language'].lower() in ['en', 'eng', 'english']]
            
            target_sub = None
            if en_manual:
                target_sub = en_manual[0]
            elif manual_subs:
                target_sub = manual_subs[0]
            elif auto_subs:
                # Prefer English auto
                en_auto = [s for s in auto_subs 
                          if s['language'].lower() in ['en', 'eng', 'english']]
                target_sub = en_auto[0] if en_auto else auto_subs[0]
            
            if not target_sub:
                return None
            
            # Download the subtitle
            output_path = str(FileUtils.get_subtitle_path())
            sub_path = await self.ytdlp_provider.download_subtitle(
                url,
                target_sub['language'],
                output_path
            )
            
            if sub_path and os.path.exists(sub_path):
                with open(sub_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ext = Path(sub_path).suffix.lower().lstrip('.')
                format_map = {
                    'srt': SubtitleFormat.SRT,
                    'vtt': SubtitleFormat.VTT,
                    'ass': SubtitleFormat.ASS,
                }
                
                subtitle = Subtitle(
                    language=target_sub['language'],
                    language_name=target_sub['language'],
                    format=format_map.get(ext, SubtitleFormat.SRT),
                    source=SubtitleSource.DOWNLOADED,
                    priority=SubtitlePriority.OTHER_TRANSLATED,
                    file_path=sub_path,
                    content=content,
                    is_auto_generated=(target_sub['type'] == 'auto'),
                )
                
                return subtitle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get best subtitle: {e}")
            return None
    
    async def _generate_subtitle_from_audio(self, video_path: str) -> Optional[Subtitle]:
        """Generate subtitle from video audio"""
        try:
            # Check if speech service is available
            if not await self.speech_service.is_available():
                self.logger.warning("Speech service not available")
                return None
            
            # Extract audio from video
            audio_path = await self.ffmpeg_provider.extract_audio(
                video_path,
                str(FileUtils.get_audio_path()),
                sample_rate=16000
            )
            
            if not audio_path:
                self.logger.error("Failed to extract audio")
                return None
            
            # Transcribe audio
            result = await self.speech_service.transcribe_audio(audio_path)
            
            if not result or not result.get('text'):
                self.logger.error("Transcription failed")
                return None
            
            # Create subtitle from transcription
            segments = result.get('segments', [])
            
            srt_content = self._create_srt_from_segments(segments)
            
            # Save subtitle file
            output_path = FileUtils.get_subtitle_path()
            video_name = Path(video_path).stem
            subtitle_file = os.path.join(str(output_path), f"{video_name}_generated.srt")
            
            with open(subtitle_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            subtitle = Subtitle(
                language=result.get('language', 'en'),
                language_name=result.get('language', 'English'),
                format=SubtitleFormat.SRT,
                source=SubtitleSource.GENERATED,
                priority=SubtitlePriority.GENERATED,
                file_path=subtitle_file,
                content=srt_content,
                is_auto_generated=True,
                confidence_score=result.get('confidence', 0.0),
            )
            
            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return subtitle
            
        except Exception as e:
            self.logger.error(f"Failed to generate subtitle: {e}")
            return None
    
    def _create_srt_from_segments(self, segments: List[Dict]) -> str:
        """Create SRT content from segments"""
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            text = segment.get('text', '').strip()
            
            if not text:
                continue
            
            # Format times
            start_str = self._format_timestamp(start_time)
            end_str = self._format_timestamp(end_time)
            
            srt_lines.append(str(i))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return '\n'.join(srt_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs - int(secs)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"