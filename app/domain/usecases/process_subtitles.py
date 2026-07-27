"""
Process Subtitles Use Case
"""

from typing import List, Optional
from app.utils.logger import LoggerMixin
from app.domain.entities.subtitle import Subtitle, SubtitlePriority
from app.domain.interfaces.subtitle_repository import SubtitleRepository


class ProcessSubtitlesUseCase(LoggerMixin):
    """Use case for processing subtitles with smart pipeline"""
    
    def __init__(self, subtitle_repository: SubtitleRepository):
        self.subtitle_repository = subtitle_repository
        self.logger.info("ProcessSubtitlesUseCase initialized")
    
    async def execute(self, url: str, 
                     video_path: Optional[str] = None) -> List[Subtitle]:
        """
        Execute subtitle processing
        
        Priority:
        1. Arabic subtitles
        2. Best available subtitle → translate
        3. Generate from audio → translate
        
        Args:
            url: Video URL
            video_path: Optional video file path
            
        Returns:
            List of processed subtitles
        """
        try:
            # Get available subtitles
            available_subs = await self.subtitle_repository.get_available_subtitles(url)
            
            # Priority 1: Check for Arabic subtitles
            arabic_sub = await self._get_arabic_subtitle(url, available_subs)
            if arabic_sub:
                self.logger.info("Arabic subtitle found")
                return [arabic_sub]
            
            # Priority 2: Find best subtitle
            best_sub = await self._get_best_subtitle(url, available_subs)
            if best_sub:
                self.logger.info(f"Best subtitle found: {best_sub.language}")
                
                # Detect language if not Arabic
                detected_lang = await self.subtitle_repository.detect_language(best_sub)
                
                if detected_lang and detected_lang.lower() in ['ar', 'ara', 'arabic']:
                    return [best_sub]
                
                # Translate to Arabic
                translated = await self.subtitle_repository.translate_subtitle(
                    best_sub, "ar"
                )
                
                if translated:
                    return [best_sub, translated]
                
                return [best_sub]
            
            # Priority 3: Generate from audio
            if video_path:
                self.logger.info("Generating subtitle from audio")
                generated = await self.subtitle_repository.generate_subtitle(
                    video_path, ""
                )
                
                if generated:
                    # Detect language
                    detected_lang = await self.subtitle_repository.detect_language(generated)
                    
                    if detected_lang and detected_lang.lower() in ['ar', 'ara', 'arabic']:
                        return [generated]
                    
                    # Translate
                    translated = await self.subtitle_repository.translate_subtitle(
                        generated, "ar"
                    )
                    
                    if translated:
                        return [generated, translated]
                    
                    return [generated]
            
            self.logger.warning("No subtitles could be obtained")
            return []
            
        except Exception as e:
            self.logger.error(f"Subtitle processing failed: {e}")
            return []
    
    async def _get_arabic_subtitle(self, url: str, 
                                   available_subs: List[dict]) -> Optional[Subtitle]:
        """Get Arabic subtitle if available"""
        # Check for Arabic in available subtitles
        for sub_info in available_subs:
            lang = sub_info.get('language', '').lower()
            if lang in ['ar', 'ara', 'arabic']:
                return await self.subtitle_repository.download_subtitle(
                    url, lang, ""
                )
        
        return None
    
    async def _get_best_subtitle(self, url: str,
                                 available_subs: List[dict]) -> Optional[Subtitle]:
        """Get the best available subtitle"""
        if not available_subs:
            return None
        
        # Priority order: English manual > other manual > English auto > other auto
        manual_subs = [s for s in available_subs if s.get('type') == 'manual']
        auto_subs = [s for s in available_subs if s.get('type') == 'auto']
        
        # Try English manual first
        en_manual = [s for s in manual_subs 
                    if s.get('language', '').lower() in ['en', 'eng', 'english']]
        
        target = None
        if en_manual:
            target = en_manual[0]
        elif manual_subs:
            target = manual_subs[0]
        elif auto_subs:
            en_auto = [s for s in auto_subs 
                      if s.get('language', '').lower() in ['en', 'eng', 'english']]
            target = en_auto[0] if en_auto else auto_subs[0]
        
        if target:
            return await self.subtitle_repository.download_subtitle(
                url, target['language'], ""
            )
        
        return None
    
    async def download_subtitle_only(self, url: str, language: str) -> Optional[Subtitle]:
        """
        Download subtitle in specific language
        
        Args:
            url: Video URL
            language: Language code
            
        Returns:
            Subtitle entity or None
        """
        return await self.subtitle_repository.download_subtitle(url, language, "")
    
    async def translate_subtitle_file(self, file_path: str, 
                                     source_lang: str,
                                     target_lang: str = "ar") -> Optional[Subtitle]:
        """
        Translate an existing subtitle file
        
        Args:
            file_path: Path to subtitle file
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            Translated subtitle or None
        """
        # Read subtitle file
        subtitle = Subtitle(
            language=source_lang,
            file_path=file_path,
        )
        
        # Read content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                subtitle.content = f.read()
        except Exception as e:
            self.logger.error(f"Failed to read subtitle file: {e}")
            return None
        
        # Translate
        return await self.subtitle_repository.translate_subtitle(
            subtitle, target_lang
        )
    
    async def generate_subtitle_from_video(self, video_path: str) -> Optional[Subtitle]:
        """
        Generate subtitle from video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Generated subtitle or None
        """
        return await self.subtitle_repository.generate_subtitle(video_path, "")