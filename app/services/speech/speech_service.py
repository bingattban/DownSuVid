"""
Speech Service Module
"""

import os
import asyncio
from typing import Optional, List, Dict
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.utils.file_utils import FileUtils
from app.providers.speech.speech_provider import (
    SpeechToTextProvider,
    SpeechProviderFactory
)
from app.config.app_config import AppConfig


class SpeechService(LoggerMixin):
    """Service for speech-to-text operations"""
    
    def __init__(self):
        self.config = AppConfig()
        self.provider: Optional[SpeechToTextProvider] = None
        self._initialized = False
        self.logger.info("SpeechService initialized")
    
    async def initialize(self) -> bool:
        """Initialize speech service"""
        if self._initialized:
            return True
        
        try:
            # Get configured provider
            provider_name = self.config.get('speech_engine', 'whisper')
            
            # Create provider
            self.provider = SpeechProviderFactory.create_provider(provider_name)
            
            if self.provider:
                available = await self.provider.initialize()
                self._initialized = available
                
                if available:
                    self.logger.info(f"Speech provider ready: {provider_name}")
                else:
                    self.logger.warning(f"Speech provider not available: {provider_name}")
            else:
                self.logger.warning(f"No speech provider found: {provider_name}")
                self._initialized = False
            
            return self._initialized
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech: {e}")
            self._initialized = False
            return False
    
    async def is_available(self) -> bool:
        """Check if speech service is available"""
        if not self._initialized:
            await self.initialize()
        
        if not self.provider:
            return False
        
        return await self.provider.is_available()
    
    async def transcribe_audio(self, audio_path: str,
                              language: Optional[str] = None) -> Optional[Dict]:
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional)
            
        Returns:
            Dictionary with text, segments, language, confidence
        """
        try:
            if not await self.is_available():
                self.logger.error("Speech service not available")
                return None
            
            if not os.path.exists(audio_path):
                self.logger.error(f"Audio file not found: {audio_path}")
                return None
            
            # Check file size
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                self.logger.error("Audio file is empty")
                return None
            
            self.logger.info(f"Transcribing audio: {audio_path} ({file_size} bytes)")
            
            # Transcribe with timestamps
            segments = await self.provider.transcribe_with_timestamps(
                audio_path, language
            )
            
            if not segments:
                # Fallback to plain transcription
                text = await self.provider.transcribe(audio_path, language)
                if text:
                    segments = [{'text': text, 'start': 0, 'end': 0}]
                else:
                    return None
            
            # Calculate confidence
            confidence = sum(s.get('confidence', 0) for s in segments) / len(segments) if segments else 0
            
            # Detect language if not provided
            detected_lang = language
            if not detected_lang and segments:
                # Simple language detection based on text
                full_text = ' '.join(s.get('text', '') for s in segments)
                detected_lang = await self._detect_language_simple(full_text)
            
            result = {
                'text': ' '.join(s.get('text', '') for s in segments),
                'segments': segments,
                'language': detected_lang or 'en',
                'confidence': confidence,
                'duration': segments[-1].get('end', 0) if segments else 0,
            }
            
            self.logger.info(f"Transcription completed: {len(segments)} segments")
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None
    
    async def _detect_language_simple(self, text: str) -> Optional[str]:
        """Simple language detection"""
        if not text:
            return None
        
        # Arabic characters check
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06ff')
        if arabic_chars > len(text) * 0.3:
            return 'ar'
        
        # Default to English
        return 'en'
    
    async def get_available_models(self) -> List[Dict]:
        """Get available speech recognition models"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.get_available_models()
        return []
    
    async def download_model(self, model_id: str) -> bool:
        """Download speech model"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.download_model(model_id)
        return False
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete speech model"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.delete_model(model_id)
        return False
    
    async def verify_model(self, model_id: str) -> bool:
        """Verify model integrity"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.verify_model(model_id)
        return False
    
    async def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get model information"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.get_model_info(model_id)
        return None
    
    async def get_disk_usage(self) -> int:
        """Get disk usage by models"""
        if not self._initialized:
            await self.initialize()
        
        if self.provider:
            return await self.provider.get_disk_usage()
        return 0