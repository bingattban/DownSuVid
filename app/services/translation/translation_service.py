"""
Translation Service Module
"""

import asyncio
from typing import Optional, List, Dict
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils
from app.domain.entities.subtitle import Subtitle, SubtitleFormat
from app.providers.translation.translation_provider import (
    TranslationProvider,
    TranslationProviderFactory
)
from app.config.app_config import AppConfig


class TranslationService(LoggerMixin):
    """Service for translation operations"""
    
    def __init__(self):
        self.config = AppConfig()
        self.provider: Optional[TranslationProvider] = None
        self._initialized = False
        self.logger.info("TranslationService initialized")
    
    async def initialize(self) -> bool:
        """Initialize translation service"""
        if self._initialized:
            return True
        
        try:
            # Get configured provider name
            provider_name = self.config.get('translation_engine', 'argos')
            
            # Create provider
            self.provider = TranslationProviderFactory.create_provider(provider_name)
            
            if self.provider:
                available = await self.provider.initialize()
                self._initialized = available
                
                if available:
                    self.logger.info(f"Translation provider ready: {provider_name}")
                else:
                    self.logger.warning(f"Translation provider not available: {provider_name}")
            else:
                self.logger.warning(f"No translation provider found: {provider_name}")
                self._initialized = False
            
            return self._initialized
            
        except Exception as e:
            self.logger.error(f"Failed to initialize translation: {e}")
            self._initialized = False
            return False
    
    async def is_available(self) -> bool:
        """Check if translation service is available"""
        if not self._initialized:
            await self.initialize()
        
        if not self.provider:
            return False
        
        return await self.provider.is_available()
    
    async def translate_text(self, text: str, source_lang: str,
                            target_lang: str = "ar") -> Optional[str]:
        """
        Translate text
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        try:
            if not await self.is_available():
                self.logger.error("Translation service not available")
                return None
            
            return await self.provider.translate(text, source_lang, target_lang)
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return None
    
    async def translate_batch(self, texts: List[str], source_lang: str,
                             target_lang: str = "ar") -> List[Optional[str]]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            List of translated texts
        """
        try:
            if not await self.is_available():
                return [None] * len(texts)
            
            return await self.provider.translate_batch(texts, source_lang, target_lang)
            
        except Exception as e:
            self.logger.error(f"Batch translation failed: {e}")
            return [None] * len(texts)
    
    async def translate_subtitle(self, subtitle: Subtitle,
                                target_lang: str = "ar") -> Optional[Subtitle]:
        """
        Translate subtitle to target language
        
        Args:
            subtitle: Subtitle entity
            target_lang: Target language code
            
        Returns:
            Translated subtitle or None
        """
        try:
            if not subtitle.content:
                self.logger.error("No subtitle content to translate")
                return None
            
            # Parse subtitle entries
            entries = subtitle.parse_content()
            if not entries:
                self.logger.error("Failed to parse subtitle")
                return None
            
            # Extract texts
            texts = [entry['text'] for entry in entries]
            
            # Detect source language if not set
            source_lang = subtitle.language
            if not source_lang and self.provider:
                source_lang = await self.provider.detect_language(' '.join(texts))
            
            if not source_lang:
                source_lang = 'en'  # Default
            
            # Translate texts
            translated_texts = await self.translate_batch(texts, source_lang, target_lang)
            
            # Create new subtitle with translations
            translated_entries = []
            for entry, translated_text in zip(entries, translated_texts):
                if translated_text:
                    entry['text'] = translated_text
                    translated_entries.append(entry)
            
            if not translated_entries:
                return None
            
            # Build SRT content
            srt_content = self._build_srt(translated_entries)
            
            # Save translated subtitle
            output_path = FileUtils.get_subtitle_path()
            original_name = Path(subtitle.file_path).stem if subtitle.file_path else "subtitle"
            translated_file = str(output_path / f"{original_name}_ar.srt")
            
            with open(translated_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            # Create translated subtitle entity
            translated_subtitle = Subtitle(
                language=target_lang,
                language_name='العربية',
                format=SubtitleFormat.SRT,
                source=subtitle.source,
                priority=subtitle.priority,
                file_path=translated_file,
                content=srt_content,
                original_content=subtitle.content,
                original_language=source_lang,
                translated_from=source_lang,
                translation_engine=self.config.get('translation_engine'),
            )
            
            self.logger.info(f"Subtitle translated to {target_lang}")
            return translated_subtitle
            
        except Exception as e:
            self.logger.error(f"Subtitle translation failed: {e}")
            return None
    
    def _build_srt(self, entries: List[Dict]) -> str:
        """Build SRT content from entries"""
        srt_lines = []
        
        for i, entry in enumerate(entries, 1):
            start = self._seconds_to_srt_time(entry['start_time'])
            end = self._seconds_to_srt_time(entry['end_time'])
            text = entry['text']
            
            srt_lines.append(str(i))
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return '\n'.join(srt_lines)
    
    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs - int(secs)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"
    
    async def detect_language(self, text: str) -> Optional[str]:
        """Detect text language"""
        try:
            if not await self.is_available():
                return None
            
            return await self.provider.detect_language(text)
            
        except Exception as e:
            self.logger.error(f"Language detection failed: {e}")
            return None
    
    async def get_available_packages(self) -> List[Dict]:
        """Get available translation packages"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.get_available_packages()
        return []
    
    async def get_installed_packages(self) -> List[Dict]:
        """Get installed translation packages"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.get_installed_packages()
        return []
    
    async def download_package(self, source_lang: str, target_lang: str) -> bool:
        """Download translation package"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.download_package(source_lang, target_lang)
        return False
    
    async def delete_package(self, source_lang: str, target_lang: str) -> bool:
        """Delete translation package"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.delete_package(source_lang, target_lang)
        return False